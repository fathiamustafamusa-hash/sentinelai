"""
Celery application for SentinelAI.
Run with:
    celery -A celery_app worker --loglevel=info
"""
from celery import Celery

from app.config import settings


# Broker and backend use Redis (DB 0 for broker, DB 1 for results)
def _redis_url(db: int) -> str:
    if settings.REDIS_PASSWORD:
        return (
            f"redis://:{settings.REDIS_PASSWORD}@"
            f"{settings.REDIS_HOST}:{settings.REDIS_PORT}/{db}"
        )
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{db}"


celery_app = Celery(
    "sentinelai",
    broker=_redis_url(0),
    backend=_redis_url(1),
    include=["app.tasks.alert_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=15 * 60,        # 15 minutes hard limit
    task_soft_time_limit=12 * 60,   # 12 minutes soft limit
    worker_prefetch_multiplier=1,
    result_expires=3600,            # Results expire after 1 hour
    broker_connection_retry_on_startup=True,
)


if __name__ == "__main__":
    celery_app.start()
