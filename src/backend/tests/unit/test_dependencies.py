import pytest

"""
Unit tests for auth dependencies (get_current_user, require_role).
"""
from app.dependencies.auth import require_role
from app.models import User, UserRole


def _make_user(role: str) -> User:
    u = User()
    u.id = 1
    u.username = "u"
    u.email = "u@example.com"
    u.role = role
    u.is_active = True
    return u


class TestRequireRole:
    def test_admin_allowed_for_admin_role(self):
        checker = require_role(UserRole.ADMIN.value)
        user = _make_user(UserRole.ADMIN.value)
        # Call the inner function directly (async)
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(checker(current_user=user))
        assert result is user

    def test_analyst_forbidden_for_admin_role(self):
        from fastapi import HTTPException
        import asyncio
        checker = require_role(UserRole.ADMIN.value)
        user = _make_user(UserRole.ANALYST.value)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(checker(current_user=user))
        assert exc_info.value.status_code == 403

    def test_analyst_allowed_for_analyst_role(self):
        import asyncio
        checker = require_role(UserRole.ANALYST.value, UserRole.ADMIN.value)
        user = _make_user(UserRole.ANALYST.value)
        result = asyncio.get_event_loop().run_until_complete(checker(current_user=user))
        assert result is user
