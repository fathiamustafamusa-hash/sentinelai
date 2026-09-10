"""
Unit tests for Celery task logic (pure functions).
"""
import pytest

from app.tasks.alert_tasks import _analyze_with_ai
from app.models import Alert


@pytest.fixture
def mock_alert():
    """Alert object with mock data for testing pure logic."""
    alert = Alert()
    alert.id = 42
    alert.title = "Suspicious Login"
    alert.description = "Multiple failed logins"
    alert.severity = "high"
    alert.status = "new"
    alert.source = "Wazuh"
    alert.mitre_techniques = ["T1110", "T1078"]
    return alert


class TestAnalyzeWithAI:
    def test_returns_dict(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result, dict)

    def test_contains_required_keys(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert "summary" in result
        assert "recommended_actions" in result
        assert "mitre_techniques" in result
        assert "risk_score" in result
        assert "model" in result
        assert "analyzed_at" in result

    def test_summary_includes_title(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert mock_alert.title in result["summary"]

    def test_recommended_actions_is_list(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["recommended_actions"], list)
        assert len(result["recommended_actions"]) > 0

    def test_mitre_techniques_preserved(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert result["mitre_techniques"] == ["T1110", "T1078"]

    def test_mitre_techniques_empty_when_none(self, mock_alert):
        mock_alert.mitre_techniques = None
        result = _analyze_with_ai(mock_alert)
        assert result["mitre_techniques"] == []

    def test_risk_score_is_numeric(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["risk_score"], (int, float))
        assert 0 <= result["risk_score"] <= 100

    def test_model_is_stub(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert result["model"] == "stub-v0"
