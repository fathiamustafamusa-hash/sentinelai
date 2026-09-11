"""
Alert model for SOC detections.
Note: severity and status are stored as String (not Enum) to avoid
PostgreSQL ENUM migration complexities. Validation happens at the
Pydantic schema level.
"""

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # String instead of Enum (validation at Pydantic layer)
    severity = Column(String(20), nullable=False, default="medium", index=True)
    status = Column(String(20), nullable=False, default="new", index=True)

    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(100), nullable=True, index=True)

    raw_data = Column(JSON, nullable=True)
    mitre_techniques = Column(JSON, nullable=True)
    iocs = Column(JSON, nullable=True)

    assigned_to = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Alert(id={self.id}, title={self.title}, severity={self.severity})>"
