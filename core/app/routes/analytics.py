from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from ..models import database, models
from ..schemas import AnalyticsSummary, SentimentDistribution, TrendData, TopKeyword, Comment, SentimentResult
from ..routes.auth import get_current_user
from ..utils.sentiment import sentiment_analyzer
from typing import List, Dict
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
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

    # Get all sentiment results
    results = db.query(models.SentimentResult).join(models.AnalysisJob).filter(
        models.AnalysisJob.user_id == current_user.id,
        models.AnalysisJob.status == "completed"
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

    # Generate trend data (last 7 days)
    trend_data = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        day_results = [r for r in results if r.created_at.date() == date.date()]

        positive = sum(1 for r in day_results if r.label == 'POSITIVE')
        neutral = sum(1 for r in day_results if r.label == 'NEUTRAL')
        negative = sum(1 for r in day_results if r.label == 'NEGATIVE')

        trend_data.append(TrendData(
            date=date_str,
            positive=positive,
            neutral=neutral,
            negative=negative
        ))

    trend_data.reverse()  # Oldest first

    # Extract top keywords
    all_texts = [r.text for r in results]
    top_keywords = sentiment_analyzer.extract_keywords(all_texts, 10) if all_texts else []

    # Get top positive and negative comments
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

    # Convert to Comment schema
    top_positive_comments = []
    top_negative_comments = []

    for result in positive_comments:
        comment = Comment(
            id=result.id,
            job_id=result.job_id,
            text=result.text,
            sentiment=SentimentResult(
                label=result.label,
                confidence=result.confidence,
                text=result.text
            ),
            source_url=None,
            created_at=result.created_at
        )
        top_positive_comments.append(comment)

    for result in negative_comments:
        comment = Comment(
            id=result.id,
            job_id=result.job_id,
            text=result.text,
            sentiment=SentimentResult(
                label=result.label,
                confidence=result.confidence,
                text=result.text
            ),
            source_url=None,
            created_at=result.created_at
        )
        top_negative_comments.append(comment)

    return AnalyticsSummary(
        total_analyses=total_analyses,
        text_analyses=text_analyses,
        file_analyses=file_analyses,
        link_analyses=link_analyses,
        sentiment_distribution=sentiment_distribution,
        trend_data=trend_data,
        top_keywords=top_keywords,
        top_positive_comments=top_positive_comments,
        top_negative_comments=top_negative_comments
    )