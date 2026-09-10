"""
Unit tests for Celery task logic (pure functions).
"""

import pytest

from app.tasks.alert_tasks import _analyze_with_ai, _compute_risk_score
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
    alert.source_id = "wazuh-999"
    alert.raw_data = {"src_ip": "10.0.0.5", "dst_port": 22}
    alert.mitre_techniques = None
    alert.iocs = None
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
        # New enrichment fields
        assert "iocs" in result
        assert "iocs_flat" in result
        assert "mitre_techniques_detailed" in result

    def test_summary_includes_title(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert mock_alert.title in result["summary"]

    def test_recommended_actions_is_list(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["recommended_actions"], list)
        assert len(result["recommended_actions"]) > 0

    def test_mitre_techniques_is_list(self, mock_alert):
        """MITRE techniques should be a list (may contain detected ones)."""
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["mitre_techniques"], list)
        # Wazuh source always adds T1078, T1059, T1110 per SOURCE_HINTS
        assert "T1078" in result["mitre_techniques"]

    def test_detects_brute_force_from_description(self, mock_alert):
        """'failed logins' keyword should map to T1110."""
        result = _analyze_with_ai(mock_alert)
        assert "T1110" in result["mitre_techniques"]

    def test_extracts_private_ip_by_default(self, mock_alert):
        """IOC extraction includes private IPs by default."""
        result = _analyze_with_ai(mock_alert)
        ips = result["iocs"]["ips"]
        assert "10.0.0.5" in ips

    def test_iocs_flat_format(self, mock_alert):
        """iocs_flat should be a list of {type, value} dicts."""
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["iocs_flat"], list)
        for item in result["iocs_flat"]:
            assert "type" in item
            assert "value" in item

    def test_mitre_techniques_detailed_has_info(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["mitre_techniques_detailed"], list)
        for tech in result["mitre_techniques_detailed"]:
            assert "id" in tech
            assert "name" in tech

    def test_risk_score_is_numeric(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert isinstance(result["risk_score"], (int, float))
        assert 0 <= result["risk_score"] <= 100

    def test_model_is_v1_with_enrichment(self, mock_alert):
        result = _analyze_with_ai(mock_alert)
        assert result["model"] == "stub-v1-with-enrichment"


class TestComputeRiskScore:
    def test_critical_higher_than_low(self):
        critical = Alert()
        critical.severity = "critical"
        low = Alert()
        low.severity = "low"
        assert _compute_risk_score(critical, [], []) > _compute_risk_score(low, [], [])

    def test_iocs_increase_score(self):
        alert = Alert()
        alert.severity = "medium"
        base = _compute_risk_score(alert, [], [])
        with_iocs = _compute_risk_score(alert, [{"type": "ip", "value": "1.1.1.1"}], [])
        assert with_iocs >= base

    def test_techniques_increase_score(self):
        alert = Alert()
        alert.severity = "medium"
        base = _compute_risk_score(alert, [], [])
        with_tech = _compute_risk_score(alert, [], ["T1110"])
        assert with_tech >= base

    def test_max_score_capped_at_100(self):
        alert = Alert()
        alert.severity = "critical"
        many_iocs = [{"type": "ip", "value": f"1.1.1.{i}"} for i in range(50)]
        many_tech = [f"T1{i:03d}" for i in range(20)]
        score = _compute_risk_score(alert, many_iocs, many_tech)
        assert score <= 100
