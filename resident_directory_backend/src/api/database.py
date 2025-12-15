import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Database URL is read from environment variables.
# Instructions: Set DATABASE_URL in the backend container .env file.
# Example (based on resident_directory_database startup):
# DATABASE_URL=postgresql://appuser:dbuser123@localhost:5000/myapp
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Provide a clear error for missing DB URL to help setup.
    raise RuntimeError(
        "DATABASE_URL is not set. Please configure the backend .env with DATABASE_URL. "
        "Refer to resident_directory_database/db_connection.txt for connection info."
    )

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and ensures proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
