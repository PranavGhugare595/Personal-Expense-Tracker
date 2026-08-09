from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.core.database import get_db
from app.models.sql_models import Expense, CategoryBudget
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/insights")
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    insights = []
    
    # 1. Check Top Spending Category
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    exp_result = await db.execute(
        select(Expense.category, func.sum(Expense.amount).label("total"))
        .where(Expense.user_id == current_user.id)
        .where(Expense.date >= first_day_of_month)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )
    categories = exp_result.all()
    
    if categories:
        top_cat = categories[0]
        insights.append({
            "type": "info",
            "message": f"'{top_cat.category}' is your highest expense category this month at ₹{top_cat.total:.2f}."
        })
        
    # 2. Check budgets
    budgets_result = await db.execute(
        select(CategoryBudget).where(CategoryBudget.user_id == current_user.id)
    )
    budgets = budgets_result.scalars().all()
    
    spent_by_cat = {row.category: row.total for row in categories}
    
    over_budget_cats = []
    good_budget_cats = []
    
    for b in budgets:
        spent = spent_by_cat.get(b.category, 0)
        if spent > b.amount:
            over_budget_cats.append(b.category)
            insights.append({
                "type": "warning",
                "message": f"You have exceeded your budget for {b.category} by ₹{(spent - b.amount):.2f}."
            })
        elif spent > 0 and spent <= b.amount * 0.5:
            good_budget_cats.append(b.category)
            
    if not over_budget_cats and budgets:
        insights.append({
            "type": "success",
            "message": "Great job! You are maintaining all your budgets this month."
        })
        
    if good_budget_cats:
        insights.append({
            "type": "success",
            "message": f"You are doing excellent in managing expenses for: {', '.join(good_budget_cats)}."
        })

    # 3. Income vs Savings
    total_spent = sum(spent_by_cat.values())
    if current_user.monthly_income > 0:
        savings = current_user.monthly_income - total_spent
        if savings > 0:
            insights.append({
                "type": "success",
                "message": f"You are on track to save ₹{savings:.2f} this month."
            })
        else:
            insights.append({
                "type": "danger",
                "message": f"Warning: You have spent ₹{abs(savings):.2f} more than your monthly income."
            })
            
    if not insights:
        insights.append({
            "type": "info",
            "message": "Start logging more expenses and set budgets to get personalized financial insights!"
        })

    return insights
