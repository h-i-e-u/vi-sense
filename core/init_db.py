#!/usr/bin/env python3

from app.models.database import engine
from app.models.models import Base

def init_database():
    """Initialize the database by creating all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()