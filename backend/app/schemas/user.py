from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    currency: str = Field(default="INR")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    monthly_income: float = Field(default=0.0, ge=0, description="User's monthly income")
    safety_allocation: float = Field(default=20.0, ge=0, le=100, description="Savings allocation percentage")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    """Schema for updating non-sensitive profile fields."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    currency: Optional[str] = None
    monthly_income: Optional[float] = Field(None, ge=0)
    safety_allocation: Optional[float] = Field(None, ge=0, le=100)

class UserChangePassword(BaseModel):
    """Schema for secure password change."""
    current_password: str
    new_password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: str = Field(..., alias="_id")
    monthly_income: float = Field(default=0.0)
    safety_allocation: float = Field(default=20.0)
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "_id": "645a2b8e9c0b1123456789ab",
                "name": "Shreyas Gurav",
                "email": "shreyas6170@gmail.com",
                "currency": "INR",
                "monthly_income": 50000.0,
                "safety_allocation": 20.0,
                "created_at": "2026-05-26T10:00:00Z",
                "updated_at": "2026-05-26T10:00:00Z"
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
