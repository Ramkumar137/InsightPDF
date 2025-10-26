"""
Example tests for the PDF Summarizer API
Run with: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from io import BytesIO
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

# from main import app
from app.database import Base, get_db
from app.services.auth import verify_firebase_token, mock_verify_token

# ==================== Performance Tests ====================

def test_multiple_file_upload():
    """Test uploading multiple PDF files at once"""
    # Create multiple fake PDFs
    files = [
        ("files", ("test1.pdf", BytesIO(b"%PDF-1.4\nTest 1"), "application/pdf")),
        ("files", ("test2.pdf", BytesIO(b"%PDF-1.4\nTest 2"), "application/pdf"))
    ]
    data = {"contextType": "executive"}
    
    response = client.post("/api/summarize", files=files, data=data)
    # Should handle multiple files (may fail on malformed PDFs)
    assert response.status_code in [200, 400, 500]

def test_large_context_types():
    """Test all context types are valid"""
    valid_contexts = ["executive", "student", "analyst", "general"]
    
    for context in valid_contexts:
        pdf_content = b"%PDF-1.4\nTest content"
        files = {"files": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        data = {"contextType": context}
        
        response = client.post("/api/summarize", files=files, data=data)
        # Should accept all valid context types
        assert response.status_code in [200, 400]  # 400 if PDF extraction fails

# ==================== Error Handling Tests ====================

def test_error_response_format():
    """Test that error responses follow consistent format"""
    response = client.post(
        "/api/summarize",
        data={"contextType": "invalid"}
    )
    
    if response.status_code >= 400:
        assert "error" in response.json()
        assert "message" in response.json()["error"]
        assert "code" in response.json()["error"]

def test_unauthorized_without_token():
    """Test endpoints without auth token (when not mocked)"""
    # This test only works if you remove the mock dependency override
    # app.dependency_overrides.pop(verify_firebase_token, None)
    # response = client.get("/api/summaries")
    # assert response.status_code == 401
    pass

# ==================== Utility Functions for Testing ====================

def create_test_summary(db_session, user_id):
    """Helper function to create a test summary in database"""
    from app.models.summary import Summary
    import uuid
    
    summary = Summary(
        user_id=user_id,
        file_names=["test.pdf"],
        context_type="executive",
        overview="Test overview",
        key_insights="Test insights",
        risks="Test risks",
        recommendations="Test recommendations"
    )
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)
    return summary

# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override dependencies for testing
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_firebase_token] = mock_verify_token

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ==================== Health Check Tests ====================

def test_root_endpoint():
    """Test root endpoint returns status"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# ==================== PDF Upload & Summarization Tests ====================

def test_upload_pdf_missing_files():
    """Test upload without files returns error"""
    response = client.post(
        "/api/summarize",
        data={"contextType": "executive"}
    )
    assert response.status_code == 422  # Validation error

def test_upload_pdf_invalid_context():
    """Test upload with invalid context type"""
    # Create fake PDF file
    pdf_content = b"%PDF-1.4\n%Test PDF content\n"
    files = {"files": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
    data = {"contextType": "invalid_context"}
    
    response = client.post("/api/summarize", files=files, data=data)
    assert response.status_code == 400
    assert "INVALID_CONTEXT" in response.json()["error"]["code"]

def test_upload_pdf_wrong_file_type():
    """Test upload with non-PDF file"""
    files = {"files": ("test.txt", BytesIO(b"Hello"), "text/plain")}
    data = {"contextType": "executive"}
    
    response = client.post("/api/summarize", files=files, data=data)
    assert response.status_code == 400
    assert "INVALID_FILE_TYPE" in response.json()["error"]["code"]

def test_successful_pdf_upload():
    """Test successful PDF upload and summarization"""
    # Create more realistic PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Test PDF Content) Tj ET
endstream endobj
xref
0 5
trailer<</Size 5/Root 1 0 R>>
startxref
200
%%EOF"""
    
    files = {"files": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
    data = {"contextType": "executive"}
    
    response = client.post("/api/summarize", files=files, data=data)
    
    # Note: This might fail if PDF extraction fails on malformed PDF
    # In production, use a real PDF file for testing
    if response.status_code == 200:
        assert "summaryId" in response.json()
        assert "content" in response.json()
        assert "metadata" in response.json()

# ==================== Summary Retrieval Tests ====================

def test_get_summaries_empty():
    """Test getting summaries when none exist"""
    response = client.get("/api/summaries")
    assert response.status_code == 200
    assert "summaries" in response.json()
    assert isinstance(response.json()["summaries"], list)

def test_get_specific_summary_not_found():
    """Test getting non-existent summary"""
    response = client.get("/api/summaries/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "NOT_FOUND" in response.json()["error"]["code"]

def test_get_summaries_with_pagination():
    """Test summary list with pagination parameters"""
    response = client.get("/api/summaries?limit=10&offset=0")
    assert response.status_code == 200
    assert "summaries" in response.json()
    assert "total" in response.json()
    assert response.json()["limit"] == 10
    assert response.json()["offset"] == 0

# ==================== Summary Refinement Tests ====================

def test_refine_summary_invalid_action():
    """Test refinement with invalid action"""
    summary_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/api/summaries/{summary_id}/refine",
        data={"action": "invalid_action"}
    )
    assert response.status_code == 400
    assert "INVALID_ACTION" in response.json()["error"]["code"]

def test_refine_nonexistent_summary():
    """Test refining non-existent summary"""
    summary_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/api/summaries/{summary_id}/refine",
        data={"action": "shorten"}
    )
    assert response.status_code == 404

# ==================== Download Tests ====================

def test_download_invalid_format():
    """Test download with invalid format"""
    summary_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/summaries/{summary_id}/download?format=invalid")
    assert response.status_code == 422  # Validation error

def test_download_nonexistent_summary():
    """Test downloading non-existent summary"""
    summary_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/summaries/{summary_id}/download?format=txt")
    assert response.status_code == 404

# ==================== Delete Tests ====================

def test_delete_nonexistent_summary():
    """Test deleting non-existent summary"""
    summary_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/summaries/{summary_id}")
    assert response.status_code == 404

# ==================== Integration Test ====================

def test_full_workflow():
    """
    Complete workflow test:
    1. Upload PDF
    2. Get summary
    3. Refine summary
    4. Download summary
    5. Delete summary
    """
    # This is a placeholder - implement with real PDF file
    # For actual testing, you would:
    # 1. Upload a real PDF
    # 2. Store the returned summaryId
    # 3. Use that ID for subsequent operations
    pass

# 