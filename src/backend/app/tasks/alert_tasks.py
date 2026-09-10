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
from app.services.ioc_extractor import extract_flat_iocs, extract_iocs
from app.services.mitre_mapper import map_to_mitre, get_technique_info


logger = logging.getLogger(__name__)

# Sync session factory for Celery workers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def _build_alert_text(alert: Alert) -> str:
    """
    Build a searchable text blob from alert fields.

    We include title, description, source_id, and stringified raw_data so
    that IOC regexes and MITRE keyword matching can scan everything.
    """
    parts = [
        alert.title or "",
        alert.description or "",
        alert.source_id or "",
    ]
    if alert.raw_data:
        try:
            import json

            parts.append(json.dumps(alert.raw_data, ensure_ascii=False))
        except Exception:
            parts.append(str(alert.raw_data))
    return " ".join(parts)


def _analyze_with_ai(alert: Alert) -> dict:
    """
    AI analysis stub + enrichment.

    Currently performs deterministic enrichment:
      1. IOC extraction from alert text (IPs, domains, hashes, etc.)
      2. MITRE ATT&CK mapping based on keywords + source hints

    In a future iteration, this will additionally call OpenAI or Ollama to
    produce a natural-language summary and recommended actions.
    """
    # ---- 1. IOC extraction ----
    text = _build_alert_text(alert)
    iocs_by_type = extract_iocs(text)
    iocs_flat = extract_flat_iocs(text)

    # ---- 2. MITRE ATT&CK mapping ----
    detected_techniques = map_to_mitre(
        title=alert.title or "",
        description=alert.description or "",
        source=alert.source or "",
        raw_data=text,
    )
    techniques_with_info = [get_technique_info(t) for t in detected_techniques]

    # ---- 3. Compose result ----
    return {
        "summary": f"Automated analysis of: {alert.title}",
        "recommended_actions": [
            "Correlate with recent logs from the same source",
            "Check threat intelligence for the extracted IOCs",
            "Verify affected assets in the CMDB",
        ],
        "iocs": iocs_by_type,
        "iocs_flat": iocs_flat,
        "mitre_techniques": detected_techniques,
        "mitre_techniques_detailed": techniques_with_info,
        "risk_score": _compute_risk_score(alert, iocs_flat, detected_techniques),
        "model": "stub-v1-with-enrichment",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


def _compute_risk_score(alert: Alert, iocs: list, techniques: list) -> int:
    """
    Simple risk-scoring heuristic on a 0-100 scale.

    Base score depends on severity; then bonus from IOCs and techniques.
    """
    base = {
        "critical": 90,
        "high": 70,
        "medium": 50,
        "low": 30,
        "info": 10,
    }.get((alert.severity or "medium").lower(), 50)

    ioc_bonus = min(len(iocs) * 2, 10)
    technique_bonus = min(len(techniques) * 2, 10)

    return min(base + ioc_bonus + technique_bonus, 100)


@celery_app.task(
    name="analyze_alert_ai",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def analyze_alert_ai(self, alert_id: int) -> dict:
    """
    Analyze a given alert: extract IOCs, map to MITRE, compute risk score.
    """
    logger.info(f"[analyze_alert_ai] Starting analysis for alert {alert_id}")

    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            logger.warning(f"[analyze_alert_ai] Alert {alert_id} not found")
            return {"status": "not_found", "alert_id": alert_id}

        analysis = _analyze_with_ai(alert)

        # Persist extracted IOCs and MITRE techniques back onto the alert
        # (does not overwrite user-provided values if already present)
        if not alert.mitre_techniques and analysis["mitre_techniques"]:
            alert.mitre_techniques = analysis["mitre_techniques"]
        if not alert.iocs and analysis["iocs_flat"]:
            alert.iocs = analysis["iocs_flat"]
        db.commit()

        logger.info(
            f"[analyze_alert_ai] Finished analysis for alert {alert_id}: "
            f"{len(analysis['iocs_flat'])} IOCs, "
            f"{len(analysis['mitre_techniques'])} techniques, "
            f"risk_score={analysis['risk_score']}"
        )
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
