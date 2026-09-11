"""
SQLAlchemy setup: async engine for FastAPI + sync engine for migrations/create_all.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# ============ Base for all models ============
Base = declarative_base()

# ============ Async Engine (for FastAPI endpoints) ============
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ============ Sync Engine (for create_all and scripts) ============
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


# ============ FastAPI Dependency ============
async def get_async_db():
    """Yield an async database session for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        yield session
