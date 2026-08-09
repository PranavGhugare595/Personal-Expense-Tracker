from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.models.sql_models import CategoryBudget, Expense
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class BudgetSetRequest(BaseModel):
    category: str
    amount: float

class BudgetResponse(BaseModel):
    category: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    usage_percentage: float

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Get all budgets for the user
    result = await db.execute(
        select(CategoryBudget).where(CategoryBudget.user_id == current_user.id)
    )
    budgets = result.scalars().all()
    
    # Get spending for current month for each category
    now = datetime.now()
    first_day_of_month = datetime(now.year, now.month, 1)
    
    expenses_result = await db.execute(
        select(Expense.category, func.sum(Expense.amount).label("total_spent"))
        .where(Expense.user_id == current_user.id)
        .where(Expense.date >= first_day_of_month)
        .group_by(Expense.category)
    )
    
    spent_by_category = {row.category: row.total_spent for row in expenses_result.all()}
    
    response = []
    for budget in budgets:
        spent = spent_by_category.get(budget.category, 0.0)
        remaining = budget.amount - spent
        usage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        response.append({
            "category": budget.category,
            "budget_amount": budget.amount,
            "spent_amount": spent,
            "remaining_amount": remaining,
            "usage_percentage": usage
        })
        
    return response

@router.post("/")
async def set_budget(
    request: BudgetSetRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if request.amount < 0:
        raise HTTPException(status_code=400, detail="Budget amount cannot be negative")
        
    # Check if budget exists
    result = await db.execute(
        select(CategoryBudget)
        .where(CategoryBudget.user_id == current_user.id)
        .where(CategoryBudget.category == request.category)
    )
    existing_budget = result.scalar_one_or_none()
    
    if existing_budget:
        existing_budget.amount = request.amount
    else:
        new_budget = CategoryBudget(
            user_id=current_user.id,
            category=request.category,
            amount=request.amount
        )
        db.add(new_budget)
        
    await db.commit()
    return {"status": "success", "message": "Budget updated successfully"}
