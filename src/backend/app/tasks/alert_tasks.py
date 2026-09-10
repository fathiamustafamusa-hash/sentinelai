"""
Celery tasks for alert processing and AI analysis.
Tasks are explicitly bound to `celery_app` (configured with Redis broker).
"""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import sessionmaker

from celery_app import celery_app
from app.database import sync_engine
from app.models import Alert


logger = logging.getLogger(__name__)

# Sync session factory for Celery workers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def _analyze_with_ai(alert: Alert) -> dict:
    """
    AI analysis stub.

    In a future iteration, this will call OpenAI or Ollama with the alert's
    raw data and context to produce:
      - Summary
      - Recommended actions
      - Related MITRE techniques
      - Severity adjustment proposal

    For now, we return a deterministic stub to keep the pipeline testable.
    """
    return {
        "summary": f"Automated analysis of: {alert.title}",
        "recommended_actions": [
            "Correlate with recent logs from the same source",
            "Check threat intelligence for the extracted IOCs",
            "Verify affected assets in the CMDB",
        ],
        "mitre_techniques": alert.mitre_techniques or [],
        "risk_score": 75,
        "model": "stub-v0",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


@celery_app.task(
    name="analyze_alert_ai",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def analyze_alert_ai(self, alert_id: int) -> dict:
    """
    Analyze a given alert using AI (currently a stub).
    """
    logger.info(f"[analyze_alert_ai] Starting analysis for alert {alert_id}")

    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            logger.warning(f"[analyze_alert_ai] Alert {alert_id} not found")
            return {"status": "not_found", "alert_id": alert_id}

        analysis = _analyze_with_ai(alert)

        logger.info(f"[analyze_alert_ai] Finished analysis for alert {alert_id}")
        return {
            "status": "completed",
            "alert_id": alert_id,
            "analysis": analysis,
        }
    except Exception as exc:
        logger.exception(f"[analyze_alert_ai] Failed for alert {alert_id}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(name="ping")
def ping() -> str:
    """Simple health-check task."""
    return "pong"
