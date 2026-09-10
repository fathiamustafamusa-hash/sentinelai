"""
Unit tests for alert_service business logic.
"""

import pytest

from app.services import alert_service
from app.schemas import AlertCreate, AlertUpdate, AlertSeverity, AlertStatus
from app.models import Alert, User, UserRole


@pytest.fixture
def sample_alert(db_session):
    alert = Alert(
        title="Test Alert",
        description="Test description",
        severity="medium",
        status="new",
        source="TestSource",
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert


class TestCreateAlert:
    def test_create(self, db_session):
        data = AlertCreate(
            title="New Alert",
            description="Desc",
            severity=AlertSeverity.HIGH,
            source="Wazuh",
        )
        alert = alert_service.create_alert(db_session, data)
        assert alert.id is not None
        assert alert.title == "New Alert"
        assert alert.severity == "high"
        assert alert.status == "new"


class TestGetAlert:
    def test_get_existing(self, db_session, sample_alert):
        found = alert_service.get_alert(db_session, sample_alert.id)
        assert found is not None
        assert found.id == sample_alert.id

    def test_get_nonexistent(self, db_session):
        assert alert_service.get_alert(db_session, 99999) is None


class TestListAlerts:
    def test_list(self, db_session, sample_alert):
        alerts = alert_service.list_alerts(db_session)
        assert len(alerts) >= 1

    def test_filter_by_severity(self, db_session, sample_alert):
        result = alert_service.list_alerts(db_session, severity="medium")
        assert len(result) == 1
        result = alert_service.list_alerts(db_session, severity="critical")
        assert len(result) == 0


class TestUpdateAlert:
    def test_update_title(self, db_session, sample_alert):
        updated = alert_service.update_alert(
            db_session, sample_alert.id, AlertUpdate(title="Updated Title")
        )
        assert updated.title == "Updated Title"

    def test_update_status_to_resolved_sets_timestamp(self, db_session, sample_alert):
        updated = alert_service.update_alert(
            db_session, sample_alert.id, AlertUpdate(status=AlertStatus.RESOLVED)
        )
        assert updated.status == "resolved"
        assert updated.resolved_at is not None

    def test_update_nonexistent(self, db_session):
        result = alert_service.update_alert(db_session, 99999, AlertUpdate(title="XXX"))
        assert result is None


class TestDeleteAlert:
    def test_delete(self, db_session, sample_alert):
        assert alert_service.delete_alert(db_session, sample_alert.id) is True
        assert alert_service.get_alert(db_session, sample_alert.id) is None

    def test_delete_nonexistent(self, db_session):
        assert alert_service.delete_alert(db_session, 99999) is False


class TestAssignAlert:
    def test_assign(self, db_session, sample_alert):
        user = User(
            username="assignee",
            email="assignee@example.com",
            hashed_password="x",
            role=UserRole.ANALYST.value,
        )
        db_session.add(user)
        db_session.commit()

        result = alert_service.assign_alert(db_session, sample_alert.id, user.id)
        assert result.assigned_to == user.id
        assert result.status == "investigating"

    def test_assign_nonexistent_alert(self, db_session):
        result = alert_service.assign_alert(db_session, 99999, 1)
        assert result is None


class TestStats:
    def test_stats(self, db_session, sample_alert):
        stats = alert_service.get_stats(db_session)
        assert stats["total"] == 1
        assert stats["by_severity"].get("medium") == 1
        assert stats["by_status"].get("new") == 1
        assert stats["by_source"].get("TestSource") == 1
