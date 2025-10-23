from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.summary import User, Summary
from app.routes.auth import verify_token
from app.services.export_service import ExportService
import uuid
import io

router = APIRouter()


@router.get("/download")
async def download_summary(
        summary_id: str = Query(..., description="Summary ID to download"),
        type: str = Query(..., regex="^(txt|pdf|docx)$", description="Export format"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Download summary in specified format (txt, pdf, docx)
    """
    try:
        # Get summary
        summary = db.query(Summary).filter(
            Summary.id == uuid.UUID(summary_id)
        ).first()

        if not summary:
            raise HTTPException(
                status_code=404,
                detail="Summary not found"
            )

        # Verify ownership
        user = db.query(User).filter(User.email == current_user['email']).first()
        if not user or summary.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to download this summary"
            )

        # Prepare summary data
        summary_data = {
            "summary_id": str(summary.id),
            "file_names": summary.file_names,
            "context_type": summary.context_type,
            "summary": summary.summary,
            "created_at": summary.created_at
        }

        export_service = ExportService()

        # Generate file based on type
        if type == "txt":
            content = export_service.export_to_txt(summary_data)
            media_type = "text/plain"
            filename = f"summary_{summary_id[:8]}.txt"

        elif type == "pdf":
            content = export_service.export_to_pdf(summary_data)
            media_type = "application/pdf"
            filename = f"summary_{summary_id[:8]}.pdf"

        elif type == "docx":
            content = export_service.export_to_docx(summary_data)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"summary_{summary_id[:8]}.docx"

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating download: {str(e)}"
        )