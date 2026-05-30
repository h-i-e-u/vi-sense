from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import math

from ..models.database import get_db # Hoặc hàm lấy db session của bạn
from ..models import models
from ..schemas import PaginatedSentencesResponse
from ..routes.auth import get_current_user # Dependency check token user

router = APIRouter()

@router.get("/", response_model=PaginatedSentencesResponse)
def get_processed_sentences(
    page: int = Query(1, ge=1, description="Curent page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search text in sentences"),
    job_type: Optional[str] = Query(None, description="Sort: 'text', 'link', 'file'"),
    label: Optional[str] = Query(None, description="Sort: 'POSITIVE', 'NEGATIVE', 'NEUTRAL'"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Khởi tạo Query kết hợp Join với AnalysisJob để lọc theo user_id
    query = db.query(models.SentimentResult).\
        join(models.AnalysisJob, models.SentimentResult.job_id == models.AnalysisJob.id).\
        filter(models.AnalysisJob.user_id == current_user.id)

    # 2. Áp dụng các bộ lọc (Filters) nếu có
    if search:
        query = query.filter(models.SentimentResult.text.ilike(f"%{search}%"))
        
    if job_type:
        query = query.filter(models.AnalysisJob.type == job_type)
        
    if label:
        query = query.filter(models.SentimentResult.label == label.upper())

    # 3. calculate total items for pagination before applying offset/limit
    total_items = query.count()
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0

    # 4. apply pagination: calculate offset and limit results
    offset = (page - 1) * limit
    sentences = query.order_by(models.SentimentResult.created_at.desc()).\
        offset(offset).\
        limit(limit).\
        all()

    # 5. return response with pagination metadata and items
    return {
        "total": total_items,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": sentences
    }
