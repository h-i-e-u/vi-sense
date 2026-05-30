from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    analysis_jobs = relationship("AnalysisJob", back_populates="user")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'text', 'link', 'file'
    status = Column(String, default="pending")  # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    job_metadata = Column(JSON, nullable=True)  # Store analysis metadata
    source_url = Column(String, nullable=True, index=True) 

    # Relationships
    user = relationship("User", back_populates="analysis_jobs")
    comments = relationship("Comment", back_populates="job", cascade="all, delete-orphan")
    sentiment_results = relationship("SentimentResult", back_populates="job", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("analysis_jobs.id"), nullable=False)
    text = Column(Text, nullable=False)
    source_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("AnalysisJob", back_populates="comments")
    sentiment_result = relationship("SentimentResult", back_populates="comment", uselist=False, cascade="all, delete-orphan")

class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("analysis_jobs.id"), nullable=False)
    comment_id = Column(String, ForeignKey("comments.id"), nullable=True)
    label = Column(String, nullable=False)  # 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    confidence = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("AnalysisJob", back_populates="sentiment_results")
    comment = relationship("Comment", back_populates="sentiment_result")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("analysis_jobs.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("AnalysisJob", back_populates="uploaded_file")

# Add back reference to AnalysisJob
AnalysisJob.uploaded_file = relationship("UploadedFile", back_populates="job", uselist=False, cascade="all, delete-orphan")