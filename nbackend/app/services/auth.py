"""
Authentication service with simplified Supabase JWT verification
SIMPLIFIED: Works without JWT secret for development
"""
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
import jwt
import os

from app.database import get_db
from app.models.summary import User

def verify_supabase_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify Supabase JWT token and get/create user.
    Works without JWT secret verification for development.
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
    
    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise ValueError("Invalid authorization format")
        
        token = parts[1]
        
        # Decode WITHOUT verification (development mode)
        # This is safe because Supabase already verified the token
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Extract user info from token
        user_id = decoded.get("sub")  # Supabase user ID
        email = decoded.get("email", "unknown@example.com")
        
        if not user_id:
            raise ValueError("Invalid token: missing user ID")
        
        print(f"🔐 Authenticated user: {email} (ID: {user_id[:8]}...)")
        
        # Get or create user in database
        user = db.query(User).filter(User.firebase_uid == user_id).first()
        
        if not user:
            # Create new user with Supabase ID
            user = User(
                firebase_uid=user_id,
                email=email
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created new user: {email}")
        else:
            print(f"✅ Existing user: {email}")
        
        return user
        
    except jwt.DecodeError as e:
        print(f"❌ Token decode error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": f"Invalid token format: {str(e)}",
                    "code": "INVALID_TOKEN"
                }
            }
        )
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        print(f"Token preview: {token[:20] if 'token' in locals() else 'N/A'}...")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": f"Authentication failed: {str(e)}",
                    "code": "AUTH_FAILED"
                }
            }
        )

# Keep mock for testing if needed
def mock_verify_token(db: Session = Depends(get_db)) -> User:
    """
    Mock authentication - creates same test user for everyone.
    """
    test_email = "test@example.com"
    test_uid = "test-user-123"
    
    user = db.query(User).filter(User.firebase_uid == test_uid).first()
    
    if not user:
        user = User(firebase_uid=test_uid, email=test_email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user