"""
Alert Pydantic schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class AlertCreate(BaseModel):
    """Schema for creating a new alert."""

    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    source: str = Field(..., max_length=50)
    source_id: str | None = Field(None, max_length=100)
    raw_data: dict[str, Any] | None = None
    mitre_techniques: list[str] | None = None
    iocs: list[dict[str, Any]] | None = None


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""

    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = None
    severity: AlertSeverity | None = None
    status: AlertStatus | None = None
    assigned_to: int | None = None


class AlertResponse(BaseModel):
    """Schema for alert data returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    severity: str
    status: str
    source: str
    source_id: str | None
    raw_data: dict[str, Any] | None
    mitre_techniques: list[str] | None
    iocs: list[dict[str, Any]] | None
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime | None
    resolved_at: datetime | None
