from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class AuthResponse(Token):
    user: User

# Analysis schemas
class SentimentResult(BaseModel):
    label: str  # 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    confidence: float
    text: str

    class Config:
        from_attributes = True

class AnalysisJobBase(BaseModel):
    type: str  # 'text', 'link', 'file'

class AnalysisJobCreate(AnalysisJobBase):
    pass

class AnalysisJob(AnalysisJobBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    results: Optional[List[SentimentResult]] = Field(validation_alias="sentiment_results")
    metadata: Optional[Dict[str, Any]] = Field(validation_alias="job_metadata")

    class Config:
        from_attributes = True

# Request schemas
class AnalyzeTextRequest(BaseModel):
    text: str

class AnalyzeLinkRequest(BaseModel):
    url: str
    type: str  # 'youtube', 'shopee', 'tiki'

class AnalyzeFileRequest(BaseModel):
    pass  # File will be handled via multipart

# Comment schemas
class Comment(BaseModel):
    id: str
    job_id: str
    text: str
    sentiment: SentimentResult
    source_url: Optional[str]
    source_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics schemas
class SentimentDistribution(BaseModel):
    positive: int
    neutral: int
    negative: int

class TrendData(BaseModel):
    date: str
    positive: int
    neutral: int
    negative: int

class TopKeyword(BaseModel):
    word: str
    count: int

class AnalyticsSummary(BaseModel):
    total_analyses: int
    text_analyses: int
    file_analyses: int
    link_analyses: int
    sentiment_distribution: SentimentDistribution
    trend_data: List[TrendData]
    top_keywords: List[TopKeyword]
    top_positive_comments: List[Comment]
    top_negative_comments: List[Comment]

class DailyAnalysisCount(BaseModel):
    date: str
    count: int

class UserAnalyticsSummary(BaseModel):
    total_analyses: int
    text_analyses: int
    file_analyses: int
    link_analyses: int
    sentiment_distribution: SentimentDistribution
    daily_analysis_counts: List[DailyAnalysisCount]
    top_keywords: List[TopKeyword]