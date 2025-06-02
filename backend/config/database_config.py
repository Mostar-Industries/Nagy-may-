import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

# Synchronous database connection
def get_db_engine():
    """Get SQLAlchemy engine for Neon PostgreSQL."""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Create engine with connection pooling
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False
    )
    
    return engine

# Asynchronous database connection
def get_async_db_engine():
    """Get async SQLAlchemy engine for Neon PostgreSQL."""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Convert to async URL if needed
    if not database_url.startswith('postgresql+asyncpg://'):
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        else:
            database_url = f'postgresql+asyncpg://{database_url}'
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10
    )
    
    return engine

# Session factories
def get_db_session():
    """Get synchronous database session."""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

async def get_async_db_session():
    """Get asynchronous database session."""
    engine = get_async_db_engine()
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        yield session

# Test database connection
def test_db_connection():
    """Test database connection."""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").scalar()
            if result == 1:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False
