from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta, date

from app.core.database import get_db
from app.models.sql_models import Expense, User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/")
async def get_analytics(
    filter: str = "this_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    now = datetime.now()
    
    if filter == "today":
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif filter == "last_7_days":
        start_dt = now - timedelta(days=7)
        end_dt = now
    elif filter == "this_month":
        start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif filter == "this_year":
        start_dt = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif filter == "custom" and start_date and end_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    else:
        # Default to this month
        start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_dt = now

    # Get expenses within range
    result = await db.execute(
        select(Expense)
        .where(Expense.user_id == current_user.id)
        .where(Expense.date >= start_dt)
        .where(Expense.date <= end_dt)
    )
    expenses = result.scalars().all()

    # Calculate summary stats
    total_expenses = sum(exp.amount for exp in expenses)
    days_in_range = max((end_dt - start_dt).days, 1)
    avg_daily = total_expenses / days_in_range
    
    # Calculate category distribution
    category_totals = {}
    for exp in expenses:
        category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount
        
    highest_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else "None"
    
    # Calculate daily trend
    daily_totals = {}
    for exp in expenses:
        date_str = exp.date.strftime("%b %d")
        daily_totals[date_str] = daily_totals.get(date_str, 0) + exp.amount
        
    trend_data = [{"date": k, "amount": v} for k, v in sorted(daily_totals.items())]
    
    # Pie chart data
    pie_data = [{"name": k, "value": v} for k, v in category_totals.items()]
    
    return {
        "summary": {
            "total_expenses": total_expenses,
            "avg_daily": avg_daily,
            "highest_category": highest_category,
        },
        "pie_data": pie_data,
        "trend_data": trend_data
    }
