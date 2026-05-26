from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from datetime import datetime

from app.core.database import db_manager
from app.api.deps import get_current_user
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse

router = APIRouter()

@router.get("/active", response_model=BudgetResponse)
def get_active_budget(current_user: dict = Depends(get_current_user)) -> Any:
    """Fetches the active budget configurations for the current calendar month."""
    current_month_str = datetime.utcnow().strftime("%Y-%m")
    query = {"userId": current_user["_id"], "month": current_month_str}
    
    budget = db_manager.find_one("budgets", query)
    if not budget:
        # Auto-initialize an empty baseline budget for the current month
        default_budget = {
            "userId": current_user["_id"],
            "month": current_month_str,
            "total_limit": 2000.0,
            "category_limits": {
                "Food & Dining": 500.0,
                "Transport": 200.0,
                "Utilities": 300.0
            },
            "ml_recommended": {
                "was_recommended": False,
                "recommended_savings_rate": 0.20
            },
            "created_at": datetime.utcnow()
        }
        inserted_id = db_manager.insert_one("budgets", default_budget)
        default_budget["_id"] = inserted_id
        return default_budget

    budget["_id"] = str(budget["_id"])
    return budget

@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    budget_in: BudgetCreate,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """Creates a new budget or overrides an existing limit config for the target month."""
    query = {"userId": current_user["_id"], "month": budget_in.month}
    existing_budget = db_manager.find_one("budgets", query)
    
    budget_dict = budget_in.model_dump()
    budget_dict["userId"] = current_user["_id"]
    budget_dict["created_at"] = datetime.utcnow()
    
    if existing_budget:
        # Update existing
        db_manager.update_one("budgets", query, budget_dict)
        budget_dict["_id"] = str(existing_budget["_id"])
    else:
        # Create new
        inserted_id = db_manager.insert_one("budgets", budget_dict)
        budget_dict["_id"] = inserted_id
        
    return budget_dict
