"""
SentinelAI SOC API - Main FastAPI application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from redis import asyncio as aioredis

from app.config import settings
from app.database import async_engine, sync_engine, Base

# Import models so they are registered with Base.metadata
from app import models  # noqa: F401

# Import routers
from app.routers import auth


# ============ Redis client (module-level, initialized in lifespan) ============
redis_client: aioredis.Redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init connections, create tables, cleanup."""
    global redis_client

    # ---- Startup ----
    print("🚀 Starting SentinelAI SOC API...")

    # 1. Connect to Redis
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await redis_client.ping()
    print("✅ Redis connected successfully")

    # 2. Verify PostgreSQL
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("✅ PostgreSQL connected successfully")

    # 3. Create tables (idempotent)
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Database tables created/verified")

    print("✅ Application startup complete")

    yield

    # ---- Shutdown ----
    print("🛑 Shutting down...")
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
        await redis_client.ping()
        redis_status = "up"
    except Exception as e:
        redis_status = f"down: {type(e).__name__}"

    all_up = (db_status == "up" and redis_status == "up")
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
