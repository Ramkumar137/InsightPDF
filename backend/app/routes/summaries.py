"""
Routes for retrieving summary history and individual summaries
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.summary import User, Summary
from app.services.auth import verify_firebase_token

router = APIRouter()

@router.get("/summaries")
async def get_summaries(
    user: User = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get summary history for authenticated user.
    
    Query Parameters:
        - limit: Maximum number of summaries to return (1-100, default 50)
        - offset: Number of summaries to skip (default 0)
        
    Response:
        - summaries: Array of summary objects with metadata
        - total: Total count of user's summaries
    """
    try:
        # Get total count
        total = db.query(Summary).filter(Summary.user_id == user.id).count()
        
        # Get summaries with pagination, ordered by most recent first
        summaries = db.query(Summary).filter(
            Summary.user_id == user.id
        ).order_by(
            Summary.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Convert to response format
        summary_list = [s.to_history_dict() for s in summaries]
        
        return {
            "summaries": summary_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Failed to retrieve summaries: {str(e)}",
                    "code": "RETRIEVAL_FAILED"
                }
            }
        )

@router.get("/summaries/{summary_id}")
async def get_summary(
    summary_id: str,
    user: User = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """
    Get a specific summary by ID.
    
    Path Parameters:
        - summary_id: UUID of the summary
        
    Response:
        - Full summary object with all content sections
    """
    try:
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
        
        # Return full summary data
        return {
            "summaryId": str(summary.id),
            "content": {
                "overview": summary.overview,
                "keyInsights": summary.key_insights,
                "risks": summary.risks or "",
                "recommendations": summary.recommendations or ""
            },
            "metadata": {
                "fileName": summary.file_names[0] if summary.file_names else "Unknown",
                "fileNames": summary.file_names,
                "contextType": summary.context_type,
                "createdAt": summary.created_at.isoformat(),
                "updatedAt": summary.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Failed to retrieve summary: {str(e)}",
                    "code": "RETRIEVAL_FAILED"
                }
            }
        )

@router.delete("/summaries/{summary_id}")
async def delete_summary(
    summary_id: str,
    user: User = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """
    Delete a specific summary.
    
    Path Parameters:
        - summary_id: UUID of the summary to delete
        
    Response:
        - success: Boolean indicating deletion success
        - message: Confirmation message
    """
    try:
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
        
        # Delete the summary
        db.delete(summary)
        db.commit()
        
        return {
            "success": True,
            "message": "Summary deleted successfully",
            "summaryId": summary_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Failed to delete summary: {str(e)}",
                    "code": "DELETION_FAILED"
                }
            }
        )