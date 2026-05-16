from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from ..models import database, models
from ..schemas import (
    AnalysisJob, AnalyzeTextRequest, AnalyzeLinkRequest,
    SentimentResult, Comment
)
from ..utils.sentiment import sentiment_analyzer
from ..routes.auth import get_current_user
import uuid
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_analysis_job(db: Session, user_id: str, job_type: str) -> models.AnalysisJob:
    """Create a new analysis job"""
    job_id = str(uuid.uuid4())
    job = models.AnalysisJob(
        id=job_id,
        user_id=user_id,
        type=job_type,
        status="processing"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def save_sentiment_results(db: Session, job_id: str, results: List[Dict], texts: List[str] = None):
    """Save sentiment analysis results to database"""
    for i, result in enumerate(results):
        sentiment_result = models.SentimentResult(
            id=str(uuid.uuid4()),
            job_id=job_id,
            label=result['label'],
            confidence=result['confidence'],
            text=result['text']
        )
        db.add(sentiment_result)

        # Create comment if we have source texts
        if texts and i < len(texts):
            comment = models.Comment(
                id=str(uuid.uuid4()),
                job_id=job_id,
                text=texts[i]
            )
            db.add(comment)
            db.commit()
            sentiment_result.comment_id = comment.id
            db.commit()

    db.commit()

def update_job_status(db: Session, job_id: str, status: str, metadata: Dict = None):
    """Update job status and metadata"""
    job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == job_id).first()
    if job:
        job.status = status
        if metadata:
            job.job_metadata = metadata
        if status == "completed":
            job.completed_at = datetime.utcnow()
        db.commit()

@router.post("/text", response_model=AnalysisJob)
async def analyze_text(
    request: AnalyzeTextRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Analyze sentiment of a single text"""
    job = create_analysis_job(db, current_user.id, "text")

    # Perform analysis
    try:
        result = sentiment_analyzer.analyze_text(request.text)
        save_sentiment_results(db, job.id, [result], [request.text])

        # Update job metadata
        metadata = {
            "total_comments": 1,
            "positive_ratio": 1.0 if result['label'] == 'POSITIVE' else 0.0,
            "neutral_ratio": 1.0 if result['label'] == 'NEUTRAL' else 0.0,
            "negative_ratio": 1.0 if result['label'] == 'NEGATIVE' else 0.0
        }
        update_job_status(db, job.id, "completed", metadata)

    except Exception as e:
        update_job_status(db, job.id, "failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Reload job with relationships for response
    job = db.query(models.AnalysisJob).options(
        joinedload(models.AnalysisJob.sentiment_results)
    ).filter(models.AnalysisJob.id == job.id).first()

    # Return updated job
    return AnalysisJob.from_orm(job)

@router.post("/link", response_model=AnalysisJob)
async def analyze_link(
    request: AnalyzeLinkRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Analyze sentiment from a URL (YouTube, Shopee, Tiki)"""
    job = create_analysis_job(db, current_user.id, "link")

    # TODO: Implement crawler for different platforms
    # For now, return mock data
    try:
        # Mock comments for demonstration
        mock_comments = [
            "Sản phẩm rất tốt, chất lượng tuyệt vời!",
            "Giao hàng nhanh, đóng gói cẩn thận",
            "Giá cả hợp lý, sẽ mua lại",
            "Không hài lòng với chất lượng",
            "Sản phẩm bị hỏng khi nhận"
        ]

        results = sentiment_analyzer.analyze_batch(mock_comments)
        save_sentiment_results(db, job.id, results, mock_comments)

        # Calculate ratios
        positive_count = sum(1 for r in results if r['label'] == 'POSITIVE')
        neutral_count = sum(1 for r in results if r['label'] == 'NEUTRAL')
        negative_count = sum(1 for r in results if r['label'] == 'NEGATIVE')
        total = len(results)

        metadata = {
            "total_comments": total,
            "positive_ratio": positive_count / total,
            "neutral_ratio": neutral_count / total,
            "negative_ratio": negative_count / total,
            "source_url": request.url,
            "platform": request.type
        }
        update_job_status(db, job.id, "completed", metadata)

    except Exception as e:
        update_job_status(db, job.id, "failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Reload job with relationships for response
    job = db.query(models.AnalysisJob).options(
        joinedload(models.AnalysisJob.sentiment_results)
    ).filter(models.AnalysisJob.id == job.id).first()

    return AnalysisJob.from_orm(job)

@router.post("/file", response_model=AnalysisJob)
async def analyze_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Analyze sentiment from uploaded file (CSV, XLSX, TXT)"""
    job = create_analysis_job(db, current_user.id, "file")

    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{job.id}_{file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Save file record
        uploaded_file = models.UploadedFile(
            id=str(uuid.uuid4()),
            job_id=job.id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type
        )
        db.add(uploaded_file)
        db.commit()

        # Process file based on type
        texts = []
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            # Assume first column contains text
            texts = df.iloc[:, 0].astype(str).tolist()
        elif file.filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")
            texts = df.iloc[:, 0].astype(str).tolist()
        elif file.filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                texts = [line.strip() for line in content.split('\n') if line.strip()]

        if not texts:
            raise HTTPException(status_code=400, detail="No text found in file")

        # Analyze sentiments
        results = sentiment_analyzer.analyze_batch(texts)
        save_sentiment_results(db, job.id, results, texts)

        # Calculate ratios
        positive_count = sum(1 for r in results if r['label'] == 'POSITIVE')
        neutral_count = sum(1 for r in results if r['label'] == 'NEUTRAL')
        negative_count = sum(1 for r in results if r['label'] == 'NEGATIVE')
        total = len(results)

        metadata = {
            "total_comments": total,
            "positive_ratio": positive_count / total,
            "neutral_ratio": neutral_count / total,
            "negative_ratio": negative_count / total,
            "file_name": file.filename,
            "file_size": len(content)
        }
        update_job_status(db, job.id, "completed", metadata)

    except Exception as e:
        update_job_status(db, job.id, "failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Reload job with relationships for response
    job = db.query(models.AnalysisJob).options(
        joinedload(models.AnalysisJob.sentiment_results)
    ).filter(models.AnalysisJob.id == job.id).first()

    return AnalysisJob.from_orm(job)