from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.summary import User, Summary
from app.routes.auth import verify_token
from app.services.pdf_reader import PDFReader
from app.services.summarizer import get_summarizer
from app.config import settings
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/summarize")
async def create_summary(
        files: List[UploadFile] = File(...),
        context_type: str = Form(...),
        action: Optional[str] = Query(None, regex="^(shorten|refine|regenerate)$"),
        summary_id: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Generate or refine PDF summary

    Actions:
    - None (default): Create new summary
    - shorten: Make existing summary shorter
    - refine: Improve clarity and remove redundancy
    - regenerate: Regenerate summary with same parameters
    """

    # Validate context type
    valid_contexts = ["executive", "student", "analyst", "general"]
    if context_type.lower() not in valid_contexts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid context type. Must be one of: {', '.join(valid_contexts)}"
        )

    # Handle refinement actions
    if action and action in ["shorten", "refine", "regenerate"]:
        if not summary_id:
            raise HTTPException(
                status_code=400,
                detail="summary_id is required for refinement actions"
            )

        return await refine_summary(summary_id, action, context_type, db, current_user)

    # Validate number of files
    if len(files) > settings.MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_FILES} files allowed"
        )

    # Validate file types and sizes
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Only PDF files are allowed."
            )

        # Read file content
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size of {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        await file.seek(0)  # Reset file pointer

    try:
        # Get or create user
        user = db.query(User).filter(User.email == current_user['email']).first()
        if not user:
            user = User(
                id=uuid.UUID(current_user['user_id']),
                email=current_user['email']
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Extract text from PDFs
        pdf_reader = PDFReader()
        files_content = []

        for file in files:
            content = await file.read()
            files_content.append((file.filename, content))

        combined_text, file_names = pdf_reader.extract_text_from_multiple_pdfs(files_content)

        if not combined_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF files"
            )

        # Split into chunks if necessary
        chunks = pdf_reader.chunk_text(combined_text, settings.MAX_INPUT_LENGTH)

        # Generate summary
        summarizer = get_summarizer()

        if len(chunks) > 1:
            summary_text = summarizer.summarize_chunks(chunks, context_type.lower())
        else:
            summary_text = summarizer.generate_summary(chunks[0], context_type.lower())

        # Save to database
        new_summary = Summary(
            id=uuid.uuid4(),
            user_id=user.id,
            file_names=file_names,
            context_type=context_type.lower(),
            summary=summary_text,
            original_text=combined_text[:10000],  # Store first 10k chars for refinement
            created_at=datetime.utcnow()
        )

        db.add(new_summary)
        db.commit()
        db.refresh(new_summary)

        return {
            "summary_id": str(new_summary.id),
            "summary": new_summary.summary,
            "context_type": new_summary.context_type,
            "file_names": new_summary.file_names,
            "created_at": new_summary.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDFs: {str(e)}"
        )


async def refine_summary(
        summary_id: str,
        action: str,
        context_type: str,
        db: Session,
        current_user: dict
):
    """
    Refine existing summary with specified action
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
                detail="Not authorized to modify this summary"
            )

        summarizer = get_summarizer()

        # Perform action
        if action == "shorten":
            updated_summary = summarizer.shorten_summary(
                summary.summary,
                context_type.lower()
            )
        elif action == "refine":
            updated_summary = summarizer.refine_summary(
                summary.summary,
                context_type.lower()
            )
        elif action == "regenerate":
            # Regenerate from original text if available
            if summary.original_text:
                pdf_reader = PDFReader()
                chunks = pdf_reader.chunk_text(summary.original_text, settings.MAX_INPUT_LENGTH)
                if len(chunks) > 1:
                    updated_summary = summarizer.summarize_chunks(chunks, context_type.lower())
                else:
                    updated_summary = summarizer.generate_summary(chunks[0], context_type.lower())
            else:
                # If no original text, just refine existing
                updated_summary = summarizer.generate_summary(
                    summary.summary,
                    context_type.lower()
                )

        # Update summary in database
        summary.summary = updated_summary
        summary.context_type = context_type.lower()
        summary.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(summary)

        return {
            "summary_id": str(summary.id),
            "updated_summary": summary.summary,
            "context_type": summary.context_type,
            "action": action,
            "updated_at": summary.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refining summary: {str(e)}"
        )


@router.get("/summaries")
async def get_user_summaries(
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Get all summaries for the current user
    """
    try:
        # Get user
        user = db.query(User).filter(User.email == current_user['email']).first()

        if not user:
            return []

        # Get all user summaries
        summaries = db.query(Summary).filter(
            Summary.user_id == user.id
        ).order_by(Summary.created_at.desc()).all()

        return [
            {
                "summary_id": str(s.id),
                "file_names": s.file_names,
                "context_type": s.context_type,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat() if s.updated_at else None
            }
            for s in summaries
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching summaries: {str(e)}"
        )


@router.get("/summaries/{summary_id}")
async def get_summary(
        summary_id: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Get a specific summary by ID
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
                detail="Not authorized to access this summary"
            )

        return {
            "summary_id": str(summary.id),
            "file_names": summary.file_names,
            "context_type": summary.context_type,
            "summary": summary.summary,
            "created_at": summary.created_at.isoformat(),
            "updated_at": summary.updated_at.isoformat() if summary.updated_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching summary: {str(e)}"
        )


@router.delete("/summaries/{summary_id}")
async def delete_summary(
        summary_id: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Delete a summary
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
                detail="Not authorized to delete this summary"
            )

        db.delete(summary)
        db.commit()

        return {
            "message": "Summary deleted successfully",
            "summary_id": summary_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting summary: {str(e)}"
        )