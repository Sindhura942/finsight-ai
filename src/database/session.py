"""Database session and connection management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import get_settings

# Get settings
settings = get_settings()

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.database_echo,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for ORM models
Base = declarative_base()


def get_db():
    """Dependency for database session
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
