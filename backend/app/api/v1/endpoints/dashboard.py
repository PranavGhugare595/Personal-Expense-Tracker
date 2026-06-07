from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import DashboardStats
from app.models.sql_models import User, Expense

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats, summary="Get dashboard statistics")
async def get_dashboard_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate and return dashboard stats:
    - Gross expenditure (sum of all expenses this month)
    - Monthly income & savings target from profile
    - Budget used percentage
    - Category distribution
    """
    # Current month boundaries
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Gross expenditure this month
    result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
            Expense.user_id == user.id,
            Expense.date >= month_start,
        )
    )
    gross_expenditure = float(result.scalar() or 0.0)

    # Category distribution this month
    cat_result = await db.execute(
        select(Expense.category, func.sum(Expense.amount))
        .where(Expense.user_id == user.id, Expense.date >= month_start)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )
    category_distribution = {row[0]: round(float(row[1]), 2) for row in cat_result.all()}

    # Budget calculations
    income = user.monthly_income or 0
    savings_pct = user.savings_target or 20
    savings_amount = (income * savings_pct) / 100
    budget_limit = income - savings_amount  # available budget after savings

    budget_used_pct = 0.0
    if budget_limit > 0:
        budget_used_pct = round((gross_expenditure / budget_limit) * 100, 1)

    return DashboardStats(
        gross_expenditure=round(gross_expenditure, 2),
        monthly_income=income,
        savings_target_pct=savings_pct,
        savings_target_amount=round(savings_amount, 2),
        budget_used_pct=budget_used_pct,
        category_distribution=category_distribution,
    )
