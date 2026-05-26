from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.security import ALGORITHM
from app.core.database import db_manager
from app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodes the JWT bearer token, validates the signature,
    and returns the authenticated user dictionary context.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception
    
    # Query Database for current active user
    user = db_manager.find_one("users", {"_id": token_data.user_id})
    if user is None:
        raise credentials_exception
    
    # Convert _id field to string representation if needed
    if "_id" in user:
        user["_id"] = str(user["_id"])
        
    return user
