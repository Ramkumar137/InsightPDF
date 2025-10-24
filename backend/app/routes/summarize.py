"""
Routes for PDF upload and summarization
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.summary import User, Summary
from app.services.auth import verify_firebase_token
from app.services.pdf_reader import PDFReader
from app.services.summarizer import summarization_service
from app.config import settings

router = APIRouter()

@router.post("/summarize")
async def create_summary(
    files: List[UploadFile] = File(...),
    contextType: str = Form(...),
    user: User = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """
    Upload PDF files and generate context-aware summary.
    
    Request:
        - files: List of PDF files (multipart/form-data)
        - contextType: executive|student|analyst|general
        
    Response:
        - summaryId: UUID of created summary
        - content: Structured summary with sections
        - metadata: File names, context, timestamp
    """
    # Validate context type
    valid_contexts = ["executive", "student", "analyst", "general"]
    if contextType not in valid_contexts:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": f"Invalid context type. Must be one of: {', '.join(valid_contexts)}",
                    "code": "INVALID_CONTEXT"
                }
            }
        )
    
    # Validate files
    if not files:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "No files uploaded",
                    "code": "NO_FILES"
                }
            }
        )
    
    # Validate file types and size
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "message": f"Invalid file type: {file.filename}. Only PDF files are allowed.",
                        "code": "INVALID_FILE_TYPE"
                    }
                }
            )
        
        # Check file size (read content to get size)
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "message": f"File {file.filename} exceeds maximum size of {settings.MAX_FILE_SIZE / (1024*1024)}MB",
                        "code": "FILE_TOO_LARGE"
                    }
                }
            )
        # Reset file pointer after reading
        await file.seek(0)
    
    try:
        # Extract text from PDFs
        pdf_data = await PDFReader.extract_text_from_multiple_pdfs(files)
        combined_text = pdf_data["combined_text"]
        file_names = pdf_data["file_names"]
        
        # Generate structured summary
        summary_content = summarization_service.generate_structured_summary(
            combined_text,
            contextType
        )
        
        # Create summary record in database
        new_summary = Summary(
            user_id=user.id,
            file_names=file_names,
            context_type=contextType,
            overview=summary_content["overview"],
            key_insights=summary_content["keyInsights"],
            risks=summary_content["risks"],
            recommendations=summary_content["recommendations"]
        )
        
        db.add(new_summary)
        db.commit()
        db.refresh(new_summary)
        
        # Return response matching frontend expectations
        return {
            "summaryId": str(new_summary.id),
            "content": {
                "overview": new_summary.overview,
                "keyInsights": new_summary.key_insights,
                "risks": new_summary.risks,
                "recommendations": new_summary.recommendations
            },
            "metadata": {
                "fileName": file_names[0] if file_names else "Unknown",
                "fileNames": file_names,
                "contextType": contextType,
                "createdAt": new_summary.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Failed to process PDFs: {str(e)}",
                    "code": "PROCESSING_FAILED"
                }
            }
        )

@router.post("/summarize/{summary_id}/refine")
async def refine_summary(
    summary_id: str,
    action: str = Form(...),
    user: User = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """
    Refine an existing summary with different actions.
    
    Actions:
        - shorten: Generate shorter version
        - refine: Improve clarity and remove redundancy
        - regenerate: Regenerate with same parameters
        
    Response:
        - summaryId: UUID of summary
        - content: Updated summary content
    """
    # Validate action
    valid_actions = ["shorten", "refine", "regenerate"]
    if action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": f"Invalid action. Must be one of: {', '.join(valid_actions)}",
                    "code": "INVALID_ACTION"
                }
            }
        )
    
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
        # Combine existing content for context
        full_content = f"{summary.overview}\n\n{summary.key_insights}"
        if summary.risks:
            full_content += f"\n\n{summary.risks}"
        if summary.recommendations:
            full_content += f"\n\n{summary.recommendations}"
        
        # Apply action
        if action == "shorten":
            # Shorten each section
            summary.overview = summarization_service.shorten_summary(
                summary.overview,
                summary.context_type
            )
            summary.key_insights = summarization_service.shorten_summary(
                summary.key_insights,
                summary.context_type
            )
            
        elif action == "refine":
            # Refine for clarity
            summary.overview = summarization_service.refine_summary(
                summary.overview,
                summary.context_type
            )
            summary.key_insights = summarization_service.refine_summary(
                summary.key_insights,
                summary.context_type
            )
            
        elif action == "regenerate":
            # Note: Ideally we'd re-process the original PDFs
            # For now, we regenerate from existing content
            new_content = summarization_service.generate_structured_summary(
                full_content,
                summary.context_type
            )
            summary.overview = new_content["overview"]
            summary.key_insights = new_content["keyInsights"]
            summary.risks = new_content["risks"]
            summary.recommendations = new_content["recommendations"]
        
        # Update timestamp
        summary.updated_at = datetime.utcnow()
        
        # Save to database
        db.commit()
        db.refresh(summary)
        
        return {
            "summaryId": str(summary.id),
            "content": {
                "overview": summary.overview,
                "keyInsights": summary.key_insights,
                "risks": summary.risks,
                "recommendations": summary.recommendations
            },
            "updatedAt": summary.updated_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Failed to refine summary: {str(e)}",
                    "code": "REFINEMENT_FAILED"
                }
            }
        )