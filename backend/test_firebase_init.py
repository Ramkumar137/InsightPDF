import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os
import json

load_dotenv()

def initialize_firebase():
    try:
        # Try file path first
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully using file path!")
            
        # Try JSON string
        elif os.getenv('FIREBASE_CREDENTIALS_JSON'):
            cred_dict = json.loads(os.getenv('FIREBASE_CREDENTIALS_JSON'))
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully using JSON string!")
        
        else:
            print("❌ No Firebase credentials found!")
            return False
        
        # Test authentication
        print("\nTesting Firebase Auth...")
        # This will fail if credentials are invalid
        users = auth.list_users(max_results=1)
        print(f"✅ Firebase Auth working! Found {users.users.__len__()} users")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_firebase()