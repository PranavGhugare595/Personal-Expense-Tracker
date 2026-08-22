from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_verification_token,
    decode_verification_token,
)
from app.core.email_service import send_verification_email
from app.models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.models.sql_models import User
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ──── Helper schema for resend endpoint ────

class ResendVerificationRequest(BaseModel):
    email: EmailStr


# ──── Register ────

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user account and send a verification email."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    # Generate verification token
    verification_token = create_verification_token(user_data.email.lower().strip())

    # Create user (unverified)
    new_user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email.lower().strip(),
        password_hash=hash_password(user_data.password),
        is_verified=True,  # Bypassing email verification for Render deployment
        verification_token=verification_token,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send verification email in the background
    # Bypassed because Render Free Tier blocks SMTP Port 587
    # background_tasks.add_task(
    #     send_verification_email,
    #     to_email=new_user.email,
    #     full_name=new_user.full_name,
    #     token=verification_token,
    # )

    return {
        "message": "Account created successfully! You can now log in.",
        "success": True,
        "user_id": new_user.id,
    }


# ──── Login ────

@router.post("/login", response_model=TokenResponse, summary="Login and get JWT token")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT access token. Requires verified email."""
    result = await db.execute(select(User).where(User.email == credentials.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Block login if email is not verified
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in. Check your inbox for the verification link.",
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            currency=user.currency,
            monthly_income=user.monthly_income,
            savings_target=user.savings_target,
            created_at=user.created_at,
        ),
    )


# ──── Verify Email ────

@router.get("/verify-email", summary="Verify user email address")
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Verify the user's email using the token from the verification link."""
    email = decode_verification_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link.")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.is_verified:
        return {"message": "Email is already verified. You can log in.", "already_verified": True}

    # Mark as verified
    user.is_verified = True
    user.verification_token = None
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Email verified successfully! You can now log in.", "success": True}


# ──── Resend Verification Email ────

@router.post("/resend-verification", summary="Resend verification email")
async def resend_verification(
    body: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Resend the verification email to an unverified user."""
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if email exists — just return a generic success
        return {"message": "If that email is registered, a new verification link has been sent."}

    if user.is_verified:
        return {"message": "This email is already verified. You can log in."}

    # Generate a new token
    new_token = create_verification_token(user.email)
    user.verification_token = new_token
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    # Send email in background
    background_tasks.add_task(
        send_verification_email,
        to_email=user.email,
        full_name=user.full_name,
        token=new_token,
    )

    return {"message": "If that email is registered, a new verification link has been sent."}
