"""
Routes for downloading summaries in multiple formats
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.summary import User, Summary
from app.services.auth import verify_firebase_token
from app.services.export_service import export_service

router = APIRouter()

@router.get("/summaries/{summary_id}/download")
async def download_summary(
    summary_id: str,
    format: str = Query(..., regex="^(txt|pdf|docx)$"),
    user: User = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """
    Download summary in specified format.
    
    Path Parameters:
        - summary_id: UUID of the summary
        
    Query Parameters:
        - format: File format (txt|pdf|docx)
        
    Response:
        - Binary file download with appropriate content type
    """
    # Get summary from database
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == user.id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "message": "Summary not found",
                    "code": "NOT_FOUND"
                }
            }
        )
    
    try:
        # Generate file based on format
        if format == "txt":
            file_content = export_service.export_to_txt(summary)
            media_type = "text/plain"
            file_extension = "txt"
            
        elif format == "pdf":
            file_content = export_service.export_to_pdf(summary)
            media_type = "application/pdf"
            file_extension = "pdf"
            
        elif format == "docx":
            file_content = export_service.export_to_docx(summary)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            file_extension = "docx"
        
        # Generate filename
        base_filename = summary.file_names[0].replace('.pdf', '') if summary.file_names else 'summary'
        filename = f"{base_filename}_summary.{file_extension}"
        
        # Return file as download
        return Response(
            content=file_content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Failed to generate {format.upper()} file: {str(e)}",
                    "code": "EXPORT_FAILED"
                }
            }
        )