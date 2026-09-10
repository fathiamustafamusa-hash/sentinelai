"""
Alert routes: CRUD operations with RBAC.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import (
    get_db,
    get_current_active_user,
    require_role,
)
from app.models import User, UserRole
from app.schemas import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertSeverity,
    AlertStatus,
)
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


# ============================================================
# Statistics (must be before /{alert_id} to avoid route conflict)
# ============================================================
@router.get(
    "/stats/overview",
    summary="Get alerts statistics",
)
def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get overview statistics for alerts.
    Accessible to all authenticated users.
    """
    return alert_service.get_stats(db)


# ============================================================
# Create
# ============================================================
@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alert",
)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN.value, UserRole.ANALYST.value)
    ),
):
    """
    Create a new alert.
    Requires role: **admin** or **analyst**.
    """
    return alert_service.create_alert(db, alert_data)


# ============================================================
# List with filters
# ============================================================
@router.get(
    "/",
    response_model=List[AlertResponse],
    summary="List alerts with filters",
)
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    severity: Optional[AlertSeverity] = Query(None),
    status_filter: Optional[AlertStatus] = Query(None, alias="status"),
    source: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List alerts with pagination and optional filters.
    Accessible to all authenticated users.
    """
    return alert_service.list_alerts(
        db,
        skip=skip,
        limit=limit,
        severity=severity.value if severity else None,
        status=status_filter.value if status_filter else None,
        source=source,
        assigned_to=assigned_to,
    )


# ============================================================
# Get by ID
# ============================================================
@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get a single alert",
)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single alert by ID."""
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    return alert


# ============================================================
# Update
# ============================================================
@router.patch(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Update an alert",
)
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN.value, UserRole.ANALYST.value)
    ),
):
    """
    Update an alert (partial update).
    Requires role: **admin** or **analyst**.
    """
    alert = alert_service.update_alert(db, alert_id, alert_data)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    return alert


# ============================================================
# Assign
# ============================================================
@router.post(
    "/{alert_id}/assign",
    response_model=AlertResponse,
    summary="Assign an alert to a user",
)
def assign_alert(
    alert_id: int,
    user_id: int = Query(..., description="ID of the user to assign the alert to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN.value, UserRole.ANALYST.value)
    ),
):
    """
    Assign an alert to a user.
    Requires role: **admin** or **analyst**.
    """
    alert = alert_service.assign_alert(db, alert_id, user_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} or user {user_id} not found",
        )
    return alert


# ============================================================
# Delete (admin only)
# ============================================================
@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an alert",
)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    """
    Delete an alert.
    Requires role: **admin**.
    """
    deleted = alert_service.delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    return None


# ============================================================
# AI Analysis (async task via Celery)
# ============================================================
@router.post(
    "/{alert_id}/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue AI analysis for an alert",
)
def analyze_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN.value, UserRole.ANALYST.value)
    ),
):
    """
    Queue an AI analysis task for the given alert.

    Returns 202 Accepted with the Celery task ID so the client can poll
    for the result via GET /api/tasks/{task_id}.
    """
    # Verify alert exists before queuing
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    # Import here to avoid circular imports
    from app.tasks.alert_tasks import analyze_alert_ai

    task = analyze_alert_ai.delay(alert_id)

    return {
        "task_id": task.id,
        "status": "queued",
        "alert_id": alert_id,
    }
