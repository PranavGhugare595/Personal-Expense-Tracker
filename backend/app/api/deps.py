from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import requests
from datetime import datetime
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import db_manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

FIREBASE_KEYS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_firebase_public_keys = {}

def get_firebase_public_keys():
    global _firebase_public_keys
    try:
        response = requests.get(FIREBASE_KEYS_URL, timeout=10)
        if response.status_code == 200:
            _firebase_public_keys = response.json()
    except Exception as e:
        print(f"[ERROR] Error fetching Firebase public keys: {e}")
    return _firebase_public_keys

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodes the Firebase ID token, validates the signature,
    and returns/auto-provisions the authenticated user context.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    project_id = settings.FIREBASE_PROJECT_ID
    bypass_verification = not project_id or project_id == "YOUR_FIREBASE_PROJECT_ID_HERE" or project_id == ""
    
    payload = None
    if bypass_verification:
        try:
            # Decode without verification for development fallback
            payload = jwt.decode(token, options={"verify_signature": False})
            print("[INFO] Dev Bypass: Firebase ID token decoded without verification.")
        except Exception as e:
            print(f"[WARNING] Dev Bypass token decode failed: {e}")
            raise credentials_exception
    else:
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if not kid:
                raise credentials_exception
                
            public_keys = get_firebase_public_keys()
            cert = public_keys.get(kid)
            if not cert:
                # Retry once by refreshing keys
                public_keys = get_firebase_public_keys()
                cert = public_keys.get(kid)
                if not cert:
                    raise credentials_exception
            
            from cryptography.x509 import load_pem_x509_certificate
            from cryptography.hazmat.backends import default_backend
            
            cert_bytes = cert.encode("utf-8")
            x509_cert = load_pem_x509_certificate(cert_bytes, default_backend())
            public_key = x509_cert.public_key()
            
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=project_id,
                issuer=f"https://securetoken.google.com/{project_id}"
            )
        except Exception as e:
            print(f"[ERROR] Strict Firebase ID token verification failed: {e}")
            raise credentials_exception

    if not payload:
        raise credentials_exception
        
    uid = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name") or (email.split("@")[0] if email else "User")
    
    if not uid:
        raise credentials_exception
        
    # Query database for current user
    user = db_manager.find_one("users", {"_id": uid})
    
    # Auto-provision new user on first registration/login
    if user is None:
        user = {
            "_id": uid,
            "email": email,
            "name": name,
            "currency": "USD",
            "monthly_income": 0.0,
            "safety_allocation": 20.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db_manager.insert_one("users", user)
        print(f"[INFO] Auto-provisioned new database user profile: {email} (uid: {uid})")
        
        # Send welcome email (non-blocking)
        try:
            from app.core.email_service import send_welcome_email
            send_welcome_email(to_email=email, user_name=name)
        except Exception as e:
            print(f"[WARNING] Welcome email failed (non-critical): {e}")
            
    # Standardize string representation
    user["_id"] = str(user["_id"])
    return user

