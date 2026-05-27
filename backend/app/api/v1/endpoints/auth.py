from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Any

from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.database import db_manager
from app.api.deps import get_current_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserProfileUpdate, UserChangePassword

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate) -> Any:
    """Registers a new user account, encrypting their password, and sends a welcome email."""
    # Check for duplicate email accounts
    existing_user = db_manager.find_one("users", {"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email user is already registered in the system."
        )

    user_dict = user_in.model_dump()
    # Encrypt password
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()

    # Save document
    inserted_id = db_manager.insert_one("users", user_dict)
    user_dict["_id"] = inserted_id

    # Send welcome email (non-blocking — failure won't break registration)
    try:
        from app.core.email_service import send_welcome_email
        send_welcome_email(to_email=user_dict["email"], user_name=user_dict["name"])
    except Exception as e:
        print(f"[WARNING] Welcome email failed (non-critical): {e}")

    return user_dict


@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin) -> Any:
    """Authenticates credentials and returns a signed access token (JSON Body support)"""
    user = db_manager.find_one("users", {"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password combination"
        )

    access_token = create_access_token(subject=str(user["_id"]))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/form", response_model=Token, include_in_schema=False)
def login_user_form(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Authenticates credentials and returns an access token (Form-Data support for Swagger UI compatibility)"""
    user = db_manager.find_one("users", {"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password combination"
        )

    access_token = create_access_token(subject=str(user["_id"]))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: dict = Depends(get_current_user)) -> Any:
    """Fetches full account information for the active user context."""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Updates the authenticated user's profile settings.
    Accepts any combination of: name, currency, monthly_income, safety_allocation.
    """
    update_data = profile_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update."
        )

    update_data["updated_at"] = datetime.utcnow()
    db_manager.update_one("users", {"_id": current_user["_id"]}, update_data)

    # Return updated user
    updated_user = db_manager.find_one("users", {"_id": current_user["_id"]})
    updated_user["_id"] = str(updated_user["_id"])
    return updated_user


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    pwd_in: UserChangePassword,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Securely changes the user's password.
    Requires the current password for verification before updating.
    """
    if not verify_password(pwd_in.current_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )

    new_hash = get_password_hash(pwd_in.new_password)
    db_manager.update_one(
        "users",
        {"_id": current_user["_id"]},
        {"password_hash": new_hash, "updated_at": datetime.utcnow()}
    )
    return {"message": "✅ Password changed successfully. Please log in again with your new password."}
