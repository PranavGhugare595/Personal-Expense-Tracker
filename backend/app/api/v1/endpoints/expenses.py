from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import ExpenseCreate, ExpenseResponse, ExpenseListResponse
from app.models.sql_models import User, Expense

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=201, summary="Log a new expense")
async def create_expense(
    data: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new expense entry for the authenticated user."""
    expense = Expense(
        user_id=user.id,
        description=data.description.strip(),
        amount=data.amount,
        category=data.category,
        payment_route=data.payment_route or "Cash",
        date=datetime.now(timezone.utc),
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)

    return ExpenseResponse(
        id=expense.id,
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
        payment_route=expense.payment_route,
        date=expense.date,
    )


@router.get("/", response_model=ExpenseListResponse, summary="List user's expenses")
async def list_expenses(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of expenses for the authenticated user, newest first."""
    # Count total
    count_result = await db.execute(
        select(func.count(Expense.id)).where(Expense.user_id == user.id)
    )
    total = count_result.scalar() or 0

    # Fetch expenses
    result = await db.execute(
        select(Expense)
        .where(Expense.user_id == user.id)
        .order_by(Expense.date.desc())
        .limit(limit)
        .offset(offset)
    )
    expenses = result.scalars().all()

    return ExpenseListResponse(
        expenses=[
            ExpenseResponse(
                id=e.id,
                description=e.description,
                amount=e.amount,
                category=e.category,
                payment_route=e.payment_route,
                date=e.date,
            )
            for e in expenses
        ],
        total=total,
    )


@router.delete("/{expense_id}", summary="Delete an expense")
async def delete_expense(
    expense_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an expense by ID (must belong to the authenticated user)."""
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found.")

    await db.delete(expense)
    await db.commit()

    return {"message": "Expense deleted successfully.", "success": True}
