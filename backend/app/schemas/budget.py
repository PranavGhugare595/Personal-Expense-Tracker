from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict

class MLRecommended(BaseModel):
    was_recommended: bool = False
    recommended_savings_rate: Optional[float] = None

class BudgetBase(BaseModel):
    month: str = Field(..., description="Target budget month in YYYY-MM format")
    total_limit: float = Field(..., gt=0, description="Total absolute spending limit for the month")
    category_limits: Dict[str, float] = Field(default_factory=dict, description="Custom category-wise caps")
    ml_recommended: Optional[MLRecommended] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    total_limit: Optional[float] = Field(None, gt=0)
    category_limits: Optional[Dict[str, float]] = None
    ml_recommended: Optional[MLRecommended] = None

class BudgetResponse(BudgetBase):
    id: str = Field(..., alias="_id")
    userId: str
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "_id": "645a2b8e9c0b1123456789ef",
                "userId": "645a2b8e9c0b1123456789ab",
                "month": "2026-05",
                "total_limit": 3000.00,
                "category_limits": {
                    "Food & Dining": 600.00,
                    "Transport": 300.00,
                    "Entertainment": 200.00,
                    "Utilities": 400.00
                },
                "ml_recommended": {
                    "was_recommended": True,
                    "recommended_savings_rate": 0.20
                },
                "created_at": "2026-05-01T00:00:00Z"
            }
        }
