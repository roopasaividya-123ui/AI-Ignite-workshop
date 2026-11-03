"""
app/database.py — SQLAlchemy database setup and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

DATABASE_URL = settings.database_url

_connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding a clean database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_tables():
    """Create all database tables and run initial seed if empty."""
    import app.models.db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    # Run data seeder
    from app.services.seed_data import seed_database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
