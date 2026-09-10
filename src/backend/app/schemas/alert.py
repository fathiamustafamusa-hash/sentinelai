"""
Alert Pydantic schemas.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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
    description: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    source: str = Field(..., max_length=50)
    source_id: Optional[str] = Field(None, max_length=100)
    raw_data: Optional[Dict[str, Any]] = None
    mitre_techniques: Optional[List[str]] = None
    iocs: Optional[List[Dict[str, Any]]] = None


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    assigned_to: Optional[int] = None


class AlertResponse(BaseModel):
    """Schema for alert data returned to clients."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    severity: str
    status: str
    source: str
    source_id: Optional[str]
    raw_data: Optional[Dict[str, Any]]
    mitre_techniques: Optional[List[str]]
    iocs: Optional[List[Dict[str, Any]]]
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
