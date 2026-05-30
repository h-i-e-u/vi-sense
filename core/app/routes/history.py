from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..models import database, models
from ..schemas import AnalysisJob, Comment
from ..routes.auth import get_current_user
from typing import List

router = APIRouter()

@router.get("/", response_model=List[AnalysisJob])
async def get_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get user's analysis history"""
    jobs = db.query(models.AnalysisJob).options(
        joinedload(models.AnalysisJob.sentiment_results)
    ).filter(
        models.AnalysisJob.user_id == current_user.id
    ).order_by(models.AnalysisJob.created_at.desc()).offset(skip).limit(limit).all()

    return [AnalysisJob.from_orm(job) for job in jobs]

@router.get("/{job_id}", response_model=AnalysisJob)
async def get_job_by_id(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get detailed information about a specific analysis job"""
    job = db.query(models.AnalysisJob).options(
        joinedload(models.AnalysisJob.sentiment_results)
    ).filter(
        models.AnalysisJob.id == job_id,
        models.AnalysisJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return AnalysisJob.from_orm(job)

@router.delete("/")
async def delete_all_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Delete all analysis history for the current user"""
    # Get all jobs for the user
    jobs = db.query(models.AnalysisJob).filter(
        models.AnalysisJob.user_id == current_user.id
    ).all()
    
    # Delete all jobs (cascade will delete related records)
    for job in jobs:
        db.delete(job)
    
    db.commit()
    return {"message": "All history deleted successfully"}