"""
Alert service: business logic for CRUD, filtering, and statistics.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import Alert, User
from app.schemas import AlertCreate, AlertUpdate


def create_alert(db: Session, alert_data: AlertCreate) -> Alert:
    """Create a new alert."""
    db_alert = Alert(
        title=alert_data.title,
        description=alert_data.description,
        severity=alert_data.severity.value,
        status="new",
        source=alert_data.source,
        source_id=alert_data.source_id,
        raw_data=alert_data.raw_data,
        mitre_techniques=alert_data.mitre_techniques,
        iocs=alert_data.iocs,
        assigned_to=None,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """Get a single alert by ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def list_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    assigned_to: Optional[int] = None,
) -> List[Alert]:
    """
    List alerts with optional filters and pagination.
    Results ordered by created_at DESC (newest first).
    """
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if source:
        query = query.filter(Alert.source == source)
    if assigned_to is not None:
        query = query.filter(Alert.assigned_to == assigned_to)

    return query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()


def count_alerts(
    db: Session,
    severity: Optional[str] = None,
    status: Optional[str] = None,
) -> int:
    """Count alerts with optional filters."""
    query = db.query(func.count(Alert.id))
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    return query.scalar() or 0


def update_alert(
    db: Session, alert_id: int, alert_data: AlertUpdate
) -> Optional[Alert]:
    """Update an alert. Only modifies fields that are explicitly provided."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None

    update_data = alert_data.model_dump(exclude_unset=True)

    # Convert enum values to their string representation
    if "severity" in update_data and update_data["severity"] is not None:
        update_data["severity"] = update_data["severity"].value
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value

    for field, value in update_data.items():
        setattr(db_alert, field, value)

    # Auto-set resolved_at when status becomes resolved
    if update_data.get("status") == "resolved":
        from datetime import datetime, timezone

        db_alert.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_alert)
    return db_alert


def delete_alert(db: Session, alert_id: int) -> bool:
    """Delete an alert. Returns True if deleted, False if not found."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return False
    db.delete(db_alert)
    db.commit()
    return True


def assign_alert(db: Session, alert_id: int, user_id: int) -> Optional[Alert]:
    """Assign an alert to a user."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    db_alert.assigned_to = user_id
    if db_alert.status == "new":
        db_alert.status = "investigating"

    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_stats(db: Session) -> dict:
    """
    Get overview statistics for alerts.
    Returns counts by severity, status, and source.
    """
    # Total
    total = db.query(func.count(Alert.id)).scalar() or 0

    # By severity
    severity_rows = (
        db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    )
    by_severity = {row[0]: row[1] for row in severity_rows}

    # By status
    status_rows = (
        db.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all()
    )
    by_status = {row[0]: row[1] for row in status_rows}

    # By source (top sources)
    source_rows = (
        db.query(Alert.source, func.count(Alert.id))
        .group_by(Alert.source)
        .order_by(desc(func.count(Alert.id)))
        .limit(10)
        .all()
    )
    by_source = {row[0]: row[1] for row in source_rows}

    # Unassigned count
    unassigned = (
        db.query(func.count(Alert.id)).filter(Alert.assigned_to.is_(None)).scalar() or 0
    )

    return {
        "total": total,
        "unassigned": unassigned,
        "by_severity": by_severity,
        "by_status": by_status,
        "by_source": by_source,
    }
