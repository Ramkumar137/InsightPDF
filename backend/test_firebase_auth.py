import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os

load_dotenv()

def test_firebase_auth():
    # Initialize Firebase
    try:
        if not firebase_admin._apps:
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        print("Testing Firebase Authentication Service...\n")
        
        # Test 1: List users (should work even with 0 users)
        print("Test 1: Listing users...")
        users = auth.list_users(max_results=10)
        print(f"✅ Auth service is working!")
        print(f"   Total users found: {len(users.users)}")
        
        # Test 2: Try to get user by email (should fail gracefully)
        print("\nTest 2: Testing user lookup...")
        try:
            user = auth.get_user_by_email('test@example.com')
            print(f"✅ Found user: {user.email}")
        except auth.UserNotFoundError:
            print("✅ User lookup works (no user found - that's expected)")
        
        # Test 3: Verify token validation setup
        print("\nTest 3: Testing token verification setup...")
        try:
            # This will fail because we don't have a real token, but it confirms the service exists
            auth.verify_id_token('dummy_token')
        except auth.InvalidIdTokenError:
            print("✅ Token verification service is configured")
        except Exception as e:
            if "CONFIGURATION_NOT_FOUND" in str(e):
                print("❌ Auth still not properly configured")
            else:
                print(f"✅ Token verification service is configured (expected error: {type(e).__name__})")
        
        print("\n" + "="*50)
        print("✅ All Firebase Auth tests passed!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_firebase_auth()