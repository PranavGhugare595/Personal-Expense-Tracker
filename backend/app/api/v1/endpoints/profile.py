from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import verify_password, hash_password
from app.models.user import ProfileUpdate, PasswordChange, UserResponse
from app.models.sql_models import User

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=UserResponse, summary="Get user profile")
async def get_profile(user: User = Depends(get_current_user)):
    """Return the authenticated user's profile data."""
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        currency=user.currency,
        monthly_income=user.monthly_income,
        savings_target=user.savings_target,
        created_at=user.created_at,
    )


@router.put("/", response_model=UserResponse, summary="Update profile & financial settings")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user's name, currency, monthly income, and/or savings target."""
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.currency is not None:
        user.currency = data.currency
    if data.monthly_income is not None:
        user.monthly_income = data.monthly_income
    if data.savings_target is not None:
        user.savings_target = data.savings_target

    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    # Update localStorage user data on frontend side
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        currency=user.currency,
        monthly_income=user.monthly_income,
        savings_target=user.savings_target,
        created_at=user.created_at,
    )


@router.put("/password", summary="Change password")
async def change_password(
    data: PasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the authenticated user's password."""
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match.")

    user.password_hash = hash_password(data.new_password)
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Password updated successfully.", "success": True}
