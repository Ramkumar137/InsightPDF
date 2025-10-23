import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_firebase_credentials():
    print("Testing Firebase Credentials...\n")
    
    # Check Method 1: File Path
    file_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if file_path and os.path.exists(file_path):
        print(f"✅ Found credentials file: {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"   Project ID: {data.get('project_id')}")
            print(f"   Client Email: {data.get('client_email')}")
    else:
        print("❌ Credentials file not found")
    
    # Check Method 2: JSON String
    json_string = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if json_string:
        print("\n✅ Found credentials JSON string")
        data = json.loads(json_string)
        print(f"   Project ID: {data.get('project_id')}")
        print(f"   Client Email: {data.get('client_email')}")
    else:
        print("\n❌ Credentials JSON string not found")

if __name__ == "__main__":
    test_firebase_credentials()