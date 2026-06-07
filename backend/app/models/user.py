from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ──── Auth Schemas ────

class UserCreate(BaseModel):
    """Schema for user registration request."""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


# ──── Token Schemas ────

class UserResponse(BaseModel):
    """User data returned in responses (no password)."""
    id: str
    full_name: str
    email: str
    currency: str = "INR"
    monthly_income: float = 0.0
    savings_target: int = 20
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response after login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ──── Profile Schemas ────

class ProfileUpdate(BaseModel):
    """Schema for updating profile & financial settings."""
    full_name: Optional[str] = None
    currency: Optional[str] = None
    monthly_income: Optional[float] = None
    savings_target: Optional[int] = None


class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str


# ──── Expense Schemas ────

class ExpenseCreate(BaseModel):
    """Schema for creating an expense."""
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=0)
    category: str = Field(default="Other", max_length=50)
    payment_route: Optional[str] = Field(default="Cash", max_length=50)


class ExpenseResponse(BaseModel):
    """Expense data returned in responses."""
    id: str
    description: str
    amount: float
    category: str
    payment_route: Optional[str]
    date: datetime


class ExpenseListResponse(BaseModel):
    """Paginated list of expenses."""
    expenses: list[ExpenseResponse]
    total: int


# ──── Dashboard Schemas ────

class DashboardStats(BaseModel):
    """Dashboard statistics."""
    gross_expenditure: float = 0.0
    monthly_income: float = 0.0
    savings_target_pct: int = 20
    savings_target_amount: float = 0.0
    budget_used_pct: float = 0.0
    category_distribution: dict = {}
