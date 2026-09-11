"""
Models package: export all models for easy import.
"""

from app.models.alert import Alert
from app.models.user import User, UserRole

__all__ = ["User", "UserRole", "Alert"]
