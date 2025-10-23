from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
import json
from app.config import settings
import os


# Initialize Firebase Admin SDK
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # Try to load from JSON string (for env variables)
            if settings.FIREBASE_CREDENTIALS_JSON:
                cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
                cred = credentials.Certificate(cred_dict)
            # Try to load from file path
            elif settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            else:
                # For development without Firebase
                print("Warning: Firebase credentials not found. Running without authentication.")
                return None

            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            return None
    return True


# Initialize on import
initialize_firebase()

# Security scheme
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Firebase JWT token and extract user information
    """
    token = credentials.credentials

    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token.get('uid')
        email = decoded_token.get('email')

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return {
            "user_id": user_id,
            "email": email
        }
    except firebase_admin.auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except firebase_admin.auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


# Optional: For development without Firebase
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Optional authentication for development
    """
    if not firebase_admin._apps:
        # Return mock user for development
        return {
            "user_id": "dev-user-123",
            "email": "dev@example.com"
        }

    return await verify_token(credentials)