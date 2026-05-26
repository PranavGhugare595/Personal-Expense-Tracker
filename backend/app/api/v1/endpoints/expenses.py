from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List, Optional
from datetime import datetime

from app.core.database import db_manager
from app.api.deps import get_current_user
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse

router = APIRouter()

@router.get("", response_model=List[ExpenseResponse])
def get_expenses(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """Fetches all logged transactions for the authenticated user, supporting optional category filters."""
    query = {"userId": current_user["_id"]}
    if category:
        query["category"] = category
        
    expenses = db_manager.find_many("expenses", query)
    
    # Standardize output model matching for ObjectID casting
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
        
    return expenses

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_in: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """Logs a new transaction under the active user account."""
    expense_dict = expense_in.model_dump()
    expense_dict["userId"] = current_user["_id"]
    expense_dict["created_at"] = datetime.utcnow()
    
    inserted_id = db_manager.insert_one("expenses", expense_dict)
    expense_dict["_id"] = inserted_id
    
    return expense_dict

@router.put("/{id}", response_model=ExpenseResponse)
def update_expense(
    id: str,
    expense_in: ExpenseUpdate,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """Updates the details of a specific transaction."""
    query = {"_id": id, "userId": current_user["_id"]}
    existing_expense = db_manager.find_one("expenses", query)
    if not existing_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction entry not found or unauthorized access"
        )
    
    update_data = expense_in.model_dump(exclude_unset=True)
    db_manager.update_one("expenses", query, update_data)
    
    # Fetch updated state
    updated_expense = db_manager.find_one("expenses", query)
    updated_expense["_id"] = str(updated_expense["_id"])
    
    return updated_expense

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_expense(
    id: str,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """Removes a transactional log from the user's registry."""
    query = {"_id": id, "userId": current_user["_id"]}
    existing_expense = db_manager.find_one("expenses", query)
    if not existing_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction entry not found or unauthorized access"
        )
    
    db_manager.delete_one("expenses", query)
    return {"message": "Transaction record successfully deleted.", "id": id}
