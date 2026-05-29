from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status, Response
from sqlalchemy.orm import Session, joinedload
from ..models import database, models
from ..schemas import (
    AnalysisJob, AnalyzeTextRequest, AnalyzeLinkRequest,
    SentimentResult, Comment
)
from ..utils.sentiment import sentiment_analyzer
from ..routes.auth import get_current_user
from core.crawlers.youtube_crawler import YouTubeCrawler
from core.crawlers.tiki_crawler import TikiCrawler
import uuid
import os
import re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_analysis_job(db: Session, user_id: str, job_type: str, source_url: Optional[str] = None ) -> models.AnalysisJob:
    """Create a new analysis job"""
    job_id = str(uuid.uuid4())
    job = models.AnalysisJob(
        id=job_id,
        user_id=user_id,
        type=job_type,
        status="processing",
        source_url=source_url
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def save_sentiment_results(
    db: Session,
    job_id: str,
    results: List[Dict],
    texts: List[str] = None,
    comment_dates: List[Optional[datetime]] = None,
):
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
                text=texts[i],
                source_date=comment_dates[i] if comment_dates and i < len(comment_dates) else None
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


def parse_source_dates_from_dataframe(df: pd.DataFrame) -> List[Optional[datetime]]:
    date_columns = [
        col for col in df.columns
        if any(keyword in col.lower() for keyword in ["date", "time", "timestamp", "ngày", "thời", "publish"])
    ]
    if not date_columns:
        return [None] * len(df)

    date_column = date_columns[0]
    parsed = pd.to_datetime(df[date_column], errors="coerce")
    return [dt.to_pydatetime() if not pd.isna(dt) else None for dt in parsed]


def get_text_column(df: pd.DataFrame) -> str:
    exclude_keywords = {"date", "time", "timestamp", "ngày", "thời", "publish"}
    text_columns = [
        col for col in df.columns
        if not any(keyword in col.lower() for keyword in exclude_keywords)
    ]
    if text_columns:
        return text_columns[0]
    return df.columns[0]

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
    response: Response,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Analyze sentiment from a URL (YouTube, Shopee, Tiki)"""
     # 1. CHECK TRÙNG: Tìm theo cột source_url 
    existing_job = db.query(models.AnalysisJob)\
        .options(joinedload(models.AnalysisJob.sentiment_results))\
        .filter(
            models.AnalysisJob.status == "completed",
            models.AnalysisJob.source_url == request.url
        ).first()

    if existing_job:
        response.status_code = status.HTTP_200_OK
        # Thên from cache flag
        job_schema = AnalysisJob.from_orm(existing_job)
        job_schema.from_cache = True 
        return job_schema

    # Create NEW job
    job = create_analysis_job(db, current_user.id, "link", source_url=request.url)

    try:
        comment_dates = None
        if request.type == 'youtube':
            crawler = YouTubeCrawler()
            comments = crawler.get_comments(request.url, max_comments=50)
            if not comments:
                raise HTTPException(status_code=404, detail="No comments found for the provided YouTube video")
            texts = [comment['text'] for comment in comments]
            comment_dates = []
            for comment in comments:
                timestamp = comment.get('timestamp')
                try:
                    if timestamp:
                        comment_dates.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
                    else:
                        comment_dates.append(None)
                except Exception:
                    comment_dates.append(None)
        elif request.type == 'tiki':
            crawler = TikiCrawler()
            reviews = crawler.get_reviews(request.url, max_reviews=50)
            if not reviews:
                raise HTTPException(status_code=404, detail="No reviews found for the provided Tiki product")
            texts = [review['text'] for review in reviews]
            comment_dates = []
            for review in reviews:
                timestamp = review.get('timestamp')
                try:
                    if timestamp:
                        comment_dates.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
                    else:
                        comment_dates.append(None)
                except Exception:
                    comment_dates.append(None)
        else:
            # Fallback for other platforms until implemented
            texts = [
                "Sản phẩm rất tốt, chất lượng tuyệt vời!",
                "Giao hàng nhanh, đóng gói cẩn thận",
                "Giá cả hợp lý, sẽ mua lại",
                "Không hài lòng với chất lượng",
                "Sản phẩm bị hỏng khi nhận"
            ]

        results = sentiment_analyzer.analyze_batch(texts)
        save_sentiment_results(db, job.id, results, texts, comment_dates=comment_dates)

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

    response.status_code = status.HTTP_201_CREATED
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
        comment_dates = None
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            text_column = get_text_column(df)
            texts = df[text_column].astype(str).tolist()
            comment_dates = parse_source_dates_from_dataframe(df)
        elif file.filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")
            text_column = get_text_column(df)
            texts = df[text_column].astype(str).tolist()
            comment_dates = parse_source_dates_from_dataframe(df)
        elif file.filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                texts = []
                comment_dates = []
                for line in lines:
                    parts = re.split(r'[\t,;|]', line, maxsplit=1)
                    if len(parts) == 2:
                        maybe_date, maybe_text = parts
                        parsed_date = pd.to_datetime(maybe_date, errors='coerce')
                        if not pd.isna(parsed_date):
                            texts.append(maybe_text.strip())
                            comment_dates.append(parsed_date.to_pydatetime())
                            continue
                    texts.append(line)
                    comment_dates.append(None)

        if not texts:
            raise HTTPException(status_code=400, detail="No text found in file")

        # Analyze sentiments
        results = sentiment_analyzer.analyze_batch(texts)
        save_sentiment_results(db, job.id, results, texts, comment_dates=comment_dates)

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

@router.get("/check-existing/{job_id}")
async def check_existing_analysis(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Check if an analysis job exists and has sentiment results"""
    job = db.query(models.AnalysisJob).filter(
        models.AnalysisJob.id == job_id,
        models.AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        return {
            "exists": False,
            "has_results": False
        }
    
    result_count = db.query(models.SentimentResult).filter(
        models.SentimentResult.job_id == job_id
    ).count()
    
    return {
        "exists": True,
        "has_results": result_count > 0,
        "job_type": job.type,
        "status": job.status,
        "created_at": job.created_at,
        "result_count": result_count,
        "metadata": job.job_metadata
    }


@router.post("/refresh/{job_id}", response_model=AnalysisJob)
async def refresh_analysis(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Refresh sentiment analysis for an existing link"""
    original_job = db.query(models.AnalysisJob).filter(
        models.AnalysisJob.id == job_id,
        models.AnalysisJob.user_id == current_user.id
    ).first()
    
    if not original_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if original_job.type == 'text' or original_job.type == 'file':
        raise HTTPException(status_code=400, detail="Cannot refresh text/file analysis")
    
    # take URL
    source_url = original_job.source_url
    metadata = original_job.job_metadata or {}
    platform = metadata.get('platform', 'youtube')

    if not source_url:
        raise HTTPException(status_code=400, detail="Original URL not found in job record")

    new_job = create_analysis_job(db, current_user.id, original_job.type, source_url=source_url)
    
    try:
        if original_job.type == 'link': 
            texts = []
            comment_dates = None
            
            if platform == 'youtube':
                crawler = YouTubeCrawler()
                comments = crawler.get_comments(source_url, max_comments=50)
                if not comments:
                    raise HTTPException(status_code=404, detail="No comments found")
                texts = [comment['text'] for comment in comments]
                comment_dates = []
                for comment in comments:
                    timestamp = comment.get('timestamp')
                    try:
                        if timestamp:
                            comment_dates.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
                        else:
                            comment_dates.append(None)
                    except:
                        comment_dates.append(None)
            else:
                # For other platforms, we would implement similar crawling logic
                raise HTTPException(status_code=400, detail=f"Refresh not supported for platform: {platform}")
            
            results = sentiment_analyzer.analyze_batch(texts)
            save_sentiment_results(db, new_job.id, results, texts, comment_dates=comment_dates)
            
            positive_count = sum(1 for r in results if r['label'] == 'POSITIVE')
            neutral_count = sum(1 for r in results if r['label'] == 'NEUTRAL')
            negative_count = sum(1 for r in results if r['label'] == 'NEGATIVE')
            total = len(results)
            
            new_metadata = {
                "total_comments": total,
                "positive_ratio": positive_count / total if total > 0 else 0,
                "neutral_ratio": neutral_count / total if total > 0 else 0,
                "negative_ratio": negative_count / total if total > 0 else 0,
                "source_url": source_url,
                "platform": platform,
                "refreshed_from": job_id
            }
            update_job_status(db, new_job.id, "completed", new_metadata)

            db.delete(original_job)
            db.commit()
    
    except HTTPException:
        update_job_status(db, new_job.id, "failed")
        raise
    except Exception as e:
        update_job_status(db, new_job.id, "failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    new_job = db.query(models.AnalysisJob).options(
        joinedload(models.AnalysisJob.sentiment_results)
    ).filter(models.AnalysisJob.id == new_job.id).first()
    
    return AnalysisJob.from_orm(new_job)

