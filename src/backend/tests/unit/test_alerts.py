import pytest

"""
Unit tests for alerts endpoints and RBAC.
"""


@pytest.fixture
def sample_alert_data():
    return {
        "title": "Suspicious SSH Login",
        "description": "Multiple failed SSH attempts from 10.0.0.5",
        "severity": "high",
        "source": "Wazuh",
        "source_id": "wazuh-999",
        "raw_data": {"src_ip": "10.0.0.5", "dst_port": 22},
        "mitre_techniques": ["T1110"],
        "iocs": [{"type": "ip", "value": "10.0.0.5"}],
    }


class TestCreateAlert:
    def test_create_alert_as_analyst(self, client, auth_headers, sample_alert_data):
        response = client.post(
            "/api/alerts/", json=sample_alert_data, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_alert_data["title"]
        assert data["severity"] == "high"
        assert data["status"] == "new"
        assert data["source"] == "Wazuh"
        assert data["assigned_to"] is None
        assert data["id"] > 0

    def test_create_alert_without_token(self, client, sample_alert_data):
        response = client.post("/api/alerts/", json=sample_alert_data)
        assert response.status_code == 401

    def test_create_alert_invalid_severity(
        self, client, auth_headers, sample_alert_data
    ):
        bad = {**sample_alert_data, "severity": "super-critical"}
        response = client.post("/api/alerts/", json=bad, headers=auth_headers)
        assert response.status_code == 422

    def test_create_alert_missing_title(self, client, auth_headers):
        response = client.post(
            "/api/alerts/",
            json={"severity": "high", "source": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestListAlerts:
    def test_list_empty(self, client, auth_headers):
        response = client.get("/api/alerts/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_multiple(self, client, auth_headers, sample_alert_data):
        # Create 3 alerts
        for i in range(3):
            data = {**sample_alert_data, "title": f"Alert {i}"}
            client.post("/api/alerts/", json=data, headers=auth_headers)

        response = client.get("/api/alerts/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_filter_by_severity(self, client, auth_headers, sample_alert_data):
        client.post(
            "/api/alerts/",
            json={**sample_alert_data, "severity": "high"},
            headers=auth_headers,
        )
        client.post(
            "/api/alerts/",
            json={**sample_alert_data, "severity": "low"},
            headers=auth_headers,
        )

        response = client.get("/api/alerts/?severity=high", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["severity"] == "high"

    def test_pagination(self, client, auth_headers, sample_alert_data):
        for i in range(5):
            data = {**sample_alert_data, "title": f"Alert {i}"}
            client.post("/api/alerts/", json=data, headers=auth_headers)

        response = client.get("/api/alerts/?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetAlert:
    def test_get_existing(self, client, auth_headers, sample_alert_data):
        created = client.post(
            "/api/alerts/", json=sample_alert_data, headers=auth_headers
        ).json()
        response = client.get(f"/api/alerts/{created['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_nonexistent(self, client, auth_headers):
        response = client.get("/api/alerts/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateAlert:
    def test_update_status(self, client, auth_headers, sample_alert_data):
        created = client.post(
            "/api/alerts/", json=sample_alert_data, headers=auth_headers
        ).json()
        response = client.patch(
            f"/api/alerts/{created['id']}",
            json={"status": "investigating"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "investigating"

    def test_update_to_resolved_sets_resolved_at(
        self, client, auth_headers, sample_alert_data
    ):
        created = client.post(
            "/api/alerts/", json=sample_alert_data, headers=auth_headers
        ).json()
        response = client.patch(
            f"/api/alerts/{created['id']}",
            json={"status": "resolved"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolved_at"] is not None


class TestDeleteAlert:
    def test_delete_as_admin(
        self, client, admin_headers, auth_headers, sample_alert_data
    ):
        # Analyst creates alert
        created = client.post(
            "/api/alerts/", json=sample_alert_data, headers=auth_headers
        ).json()
        # Admin deletes
        response = client.delete(f"/api/alerts/{created['id']}", headers=admin_headers)
        assert response.status_code == 204

    def test_delete_as_analyst_forbidden(self, client, auth_headers, sample_alert_data):
        created = client.post(
            "/api/alerts/", json=sample_alert_data, headers=auth_headers
        ).json()
        response = client.delete(f"/api/alerts/{created['id']}", headers=auth_headers)
        assert response.status_code == 403


class TestStats:
    def test_stats_empty(self, client, auth_headers):
        response = client.get("/api/alerts/stats/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["unassigned"] == 0

    def test_stats_with_alerts(self, client, auth_headers, sample_alert_data):
        client.post(
            "/api/alerts/",
            json={**sample_alert_data, "severity": "high"},
            headers=auth_headers,
        )
        client.post(
            "/api/alerts/",
            json={**sample_alert_data, "severity": "critical"},
            headers=auth_headers,
        )
        response = client.get("/api/alerts/stats/overview", headers=auth_headers)
        data = response.json()
        assert data["total"] == 2
        assert data["by_severity"].get("high") == 1
        assert data["by_severity"].get("critical") == 1
