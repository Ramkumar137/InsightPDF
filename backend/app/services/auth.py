"""
Firebase authentication service for JWT token validation
"""
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
import os

from app.config import settings
from app.database import get_db
from app.models.summary import User

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials"""
    try:
        if not firebase_admin._apps:
            # Check if credentials file exists
            if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            else:
                # Try to use environment variable with JSON credentials
                cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_JSON"))
            
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"⚠️ Firebase initialization warning: {e}")
        # In development, we can proceed without Firebase
        pass

# Initialize on module load
initialize_firebase()

async def verify_firebase_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to verify Firebase JWT token and get/create user.
    
    Args:
        authorization: Bearer token from request header
        db: Database session
    
    Returns:
        User object from database
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Authorization header missing",
                    "code": "UNAUTHORIZED"
                }
            }
        )
    
    # Extract token from "Bearer <token>"
    try:
        token = authorization.split("Bearer ")[-1]
    except:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid authorization format",
                    "code": "UNAUTHORIZED"
                }
            }
        )
    
    try:
        # Verify the Firebase token
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email", "")
        
        # Get or create user in database
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            # Create new user
            user = User(
                firebase_uid=firebase_uid,
                email=email
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid authentication token",
                    "code": "INVALID_TOKEN"
                }
            }
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Authentication token has expired",
                    "code": "TOKEN_EXPIRED"
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": f"Authentication failed: {str(e)}",
                    "code": "AUTH_FAILED"
                }
            }
        )

# Optional: Mock authentication for development/testing
async def mock_verify_token(db: Session = Depends(get_db)) -> User:
    """
    Mock authentication for development without Firebase.
    Replace verify_firebase_token with this in development mode.
    """
    # Create or get a test user
    test_email = "test@example.com"
    test_uid = "test-user-123"
    
    user = db.query(User).filter(User.firebase_uid == test_uid).first()
    
    if not user:
        user = User(firebase_uid=test_uid, email=test_email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user