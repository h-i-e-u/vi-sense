from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from ..models import database, models
from ..schemas import DailyAnalysisCount, UserAnalyticsSummary, AnalyticsSummary, SentimentDistribution, TrendData, TopKeyword, Comment, SentimentResult
from ..routes.auth import get_current_user
from ..utils.sentiment import sentiment_analyzer
from typing import List, Dict
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary", response_model=UserAnalyticsSummary)
async def get_analytics_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get comprehensive analytics summary for the user"""

    # Get all user's jobs
    jobs = db.query(models.AnalysisJob).filter(
        models.AnalysisJob.user_id == current_user.id,
        models.AnalysisJob.status == "completed"
    ).all()

    total_analyses = len(jobs)
    
    # Count analyses by type
    text_analyses = sum(1 for job in jobs if job.type == 'text')
    file_analyses = sum(1 for job in jobs if job.type == 'file')
    link_analyses = sum(1 for job in jobs if job.type == 'link')

    # Get all sentiment results for user's completed jobs
    # Note: some DBs may not have `comments.source_date` column (older schema).
    # Avoid referencing that column in SQL to prevent OperationalError; handle
    # date fallbacks in Python instead.
    results = db.query(models.SentimentResult).join(models.Comment).join(models.AnalysisJob).filter(
        models.AnalysisJob.user_id == current_user.id,
        models.AnalysisJob.status == "completed"
    ).all()

    # Separate results by job type: only link and file have dates for trending
    file_and_link_results = [
        r for r in results 
        if r.comment and r.comment.job and r.comment.job.type in ('link', 'file')
    ]

    # Calculate sentiment distribution (from all results)
    positive_count = sum(1 for r in results if r.label == 'POSITIVE')
    neutral_count = sum(1 for r in results if r.label == 'NEUTRAL')
    negative_count = sum(1 for r in results if r.label == 'NEGATIVE')

    sentiment_distribution = SentimentDistribution(
        positive=positive_count,
        neutral=neutral_count,
        negative=negative_count
    )

    daily_analysis_counts = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        count = sum(
            1
            for job in jobs
            if job.created_at and job.created_at.date() == date.date()
        )
        daily_analysis_counts.append(
            DailyAnalysisCount(date=date_str, count=count)
        )
    daily_analysis_counts.reverse()

    # Extract top keywords
    all_texts = [r.text for r in results]
    top_keywords = sentiment_analyzer.extract_keywords(all_texts, 10) if all_texts else []

 

    return UserAnalyticsSummary(
        total_analyses=total_analyses,
        text_analyses=text_analyses,
        file_analyses=file_analyses,
        link_analyses=link_analyses,
        sentiment_distribution=sentiment_distribution,
        daily_analysis_counts=daily_analysis_counts,
        top_keywords=top_keywords,
    )


@router.get("/job/{job_id}", response_model=AnalyticsSummary)
async def get_job_analytics(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get detailed analytics for a specific job (link or file)"""
    
    job = db.query(models.AnalysisJob).filter(
        models.AnalysisJob.id == job_id,
        models.AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get sentiment results for this job only
    results = db.query(models.SentimentResult).join(models.Comment).filter(
        models.SentimentResult.job_id == job_id
    ).all()
    
    # Calculate sentiment distribution
    positive_count = sum(1 for r in results if r.label == 'POSITIVE')
    neutral_count = sum(1 for r in results if r.label == 'NEUTRAL')
    negative_count = sum(1 for r in results if r.label == 'NEGATIVE')
    
    sentiment_distribution = SentimentDistribution(
        positive=positive_count,
        neutral=neutral_count,
        negative=negative_count
    )
    
    # For file/link: generate trend data; for text: just show summary
    trend_data = []
    if job.type in ('link', 'file'):
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            day_results = []
            for r in results:
                if not r.comment:
                    continue
                dt = None
                if getattr(r.comment, 'source_date', None):
                    dt = r.comment.source_date
                elif getattr(r.comment, 'created_at', None):
                    dt = r.comment.created_at
                if dt and dt.date() == date.date():
                    day_results.append(r)
            
            positive = sum(1 for r in day_results if r.label == 'POSITIVE')
            neutral = sum(1 for r in day_results if r.label == 'NEUTRAL')
            negative = sum(1 for r in day_results if r.label == 'NEGATIVE')
            
            trend_data.append(TrendData(
                date=date_str,
                positive=positive,
                neutral=neutral,
                negative=negative
            ))
        trend_data.reverse()
    
    # Extract keywords
    all_texts = [r.text for r in results]
    top_keywords = sentiment_analyzer.extract_keywords(all_texts, 10) if all_texts else []
    
    # Get top comments
    positive_comments = sorted(
        [r for r in results if r.label == 'POSITIVE'],
        key=lambda x: x.confidence,
        reverse=True
    )[:5]
    
    negative_comments = sorted(
        [r for r in results if r.label == 'NEGATIVE'],
        key=lambda x: x.confidence,
        reverse=True
    )[:5]
    
    top_positive_comments = []
    top_negative_comments = []
    
    for result in positive_comments:
        source_comment = result.comment
        comment = Comment(
            id=result.id,
            job_id=result.job_id,
            text=result.text,
            sentiment=SentimentResult(
                label=result.label,
                confidence=result.confidence,
                text=result.text
            ),
            source_url=source_comment.source_url if source_comment else None,
            source_date=source_comment.source_date if source_comment else None,
            created_at=(source_comment.source_date if source_comment and getattr(source_comment, 'source_date', None)
                    else (source_comment.created_at if source_comment and getattr(source_comment, 'created_at', None)
                        else result.created_at))
        )
        top_positive_comments.append(comment)
    
    for result in negative_comments:
        source_comment = result.comment
        comment = Comment(
            id=result.id,
            job_id=result.job_id,
            text=result.text,
            sentiment=SentimentResult(
                label=result.label,
                confidence=result.confidence,
                text=result.text
            ),
            source_url=source_comment.source_url if source_comment else None,
            source_date=source_comment.source_date if source_comment else None,
            created_at=(source_comment.source_date if source_comment and getattr(source_comment, 'source_date', None)
                    else (source_comment.created_at if source_comment and getattr(source_comment, 'created_at', None)
                        else result.created_at))
        )
        top_negative_comments.append(comment)
    
    return AnalyticsSummary(
        total_analyses=1,
        text_analyses=1 if job.type == 'text' else 0,
        file_analyses=1 if job.type == 'file' else 0,
        link_analyses=1 if job.type == 'link' else 0,
        sentiment_distribution=sentiment_distribution,
        trend_data=trend_data,
        top_keywords=top_keywords,
        top_positive_comments=top_positive_comments,
        top_negative_comments=top_negative_comments
    )