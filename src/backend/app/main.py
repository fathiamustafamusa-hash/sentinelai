"""
SentinelAI SOC API - Main FastAPI application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from redis import asyncio as aioredis

from app.config import settings
from app.database import async_engine


# ============ Redis client (module-level, initialized in lifespan) ============
redis_client: aioredis.Redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: initialize connections on startup, cleanup on shutdown.
    """
    global redis_client

    # ---- Startup ----
    print("🚀 Starting SentinelAI SOC API...")

    # 1. Connect to Redis
    try:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        raise

    # 2. Verify PostgreSQL
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connected successfully")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        raise

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


# ============ Health Check Endpoint ============
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Health check that verifies connectivity to PostgreSQL and Redis.
    Returns 200 if all services are up, 503 otherwise.
    """
    # Check PostgreSQL
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "up"
    except Exception as e:
        db_status = f"down: {type(e).__name__}"

    # Check Redis
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


# ============ Root Endpoint ============
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
