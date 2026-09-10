"""
Models package: export all models for easy import.
"""

from app.models.user import User, UserRole
from app.models.alert import Alert

__all__ = ["User", "UserRole", "Alert"]
