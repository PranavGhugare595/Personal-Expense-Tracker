from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MLMetadata(BaseModel):
    is_suggested: bool = False
    confidence_score: Optional[float] = None
    original_description: Optional[str] = None

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount must be greater than zero")
    description: str = Field(..., min_length=2, description="Short transaction description")
    category: str = Field(..., min_length=2, description="Category name")
    date: datetime = Field(default_factory=datetime.utcnow)
    payment_method: str = Field(default="Cash")
    ml_metadata: Optional[MLMetadata] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=2)
    category: Optional[str] = Field(None, min_length=2)
    date: Optional[datetime] = None
    payment_method: Optional[str] = None
    ml_metadata: Optional[MLMetadata] = None

class ExpenseResponse(ExpenseBase):
    id: str = Field(..., alias="_id")
    userId: str

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "_id": "645a2b8e9c0b1123456789cd",
                "userId": "645a2b8e9c0b1123456789ab",
                "amount": 42.50,
                "description": "Weekly grocery shopping",
                "category": "Food & Dining",
                "date": "2026-05-26T10:00:00Z",
                "payment_method": "Credit Card",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.94,
                    "original_description": "Weekly grocery shopping at Whole Foods"
                }
            }
        }

