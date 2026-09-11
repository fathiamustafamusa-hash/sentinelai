"""
SentinelAI SOC API - Main FastAPI application.
"""

from contextlib import asynccontextmanager

# ============ Redis client ============
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from redis import asyncio as aioredis
from sqlalchemy import text

# Register models with Base.metadata
from app import models  # noqa: F401
from app.config import settings
from app.database import Base, async_engine, sync_engine

# Import routers
from app.routers import alerts, auth, tasks

redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init connections, create tables, cleanup."""
    global redis_client

    # ---- Startup ----
    print("🚀 Starting SentinelAI SOC API...")

    # 1. Redis
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await redis_client.ping()
    print("✅ Redis connected successfully")

    # 2. PostgreSQL
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("✅ PostgreSQL connected successfully")

    # 3. Create tables
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Database tables created/verified")

    print("✅ Application startup complete")

    yield

    # ---- Shutdown ----
    print("🛑 Shutting down...")
    if redis_client is not None:
        await redis_client.close()
    await async_engine.dispose()
    print("🛑 Connections closed")


# ============ FastAPI App ============
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for SentinelAI - AI-Powered SOC Platform",
    lifespan=lifespan,
)

# ============ Include Routers ============
app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(tasks.router)


# ============ Health Check ============
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Health check verifying PostgreSQL and Redis connectivity."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "up"
    except Exception as e:
        db_status = f"down: {type(e).__name__}"

    try:
        if redis_client is None:
            redis_status = "down: not_initialized"
        else:
            await redis_client.ping()
            redis_status = "up"
    except Exception as e:
        redis_status = f"down: {type(e).__name__}"

    all_up = db_status == "up" and redis_status == "up"
    status_code = status.HTTP_200_OK if all_up else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_up else "unhealthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "dependencies": {
                "postgres": db_status,
                "redis": redis_status,
            },
        },
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
