"""
Unit tests for authentication endpoints.
"""


class TestRegister:
    def test_register_success(self, client, test_user_data):
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == "analyst"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        # Password MUST NOT be in response
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, test_user_data):
        client.post("/api/auth/register", json=test_user_data)
        # Try again with same username but different email
        dup = {**test_user_data, "email": "other@example.com"}
        response = client.post("/api/auth/register", json=dup)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, test_user_data):
        client.post("/api/auth/register", json=test_user_data)
        dup = {**test_user_data, "username": "otheruser"}
        response = client.post("/api/auth/register", json=dup)
        assert response.status_code == 400

    def test_register_invalid_email(self, client, test_user_data):
        bad = {**test_user_data, "email": "not-an-email"}
        response = client.post("/api/auth/register", json=bad)
        assert response.status_code == 422

    def test_register_short_password(self, client, test_user_data):
        bad = {**test_user_data, "password": "short"}
        response = client.post("/api/auth/register", json=bad)
        assert response.status_code == 422

    def test_register_short_username(self, client, test_user_data):
        bad = {**test_user_data, "username": "ab"}
        response = client.post("/api/auth/register", json=bad)
        assert response.status_code == 422

    def test_register_invalid_username_chars(self, client, test_user_data):
        bad = {**test_user_data, "username": "bad user name!"}
        response = client.post("/api/auth/register", json=bad)
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user, test_user_data):
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20

    def test_login_wrong_password(self, client, registered_user, test_user_data):
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": "WrongPassword!",
            },
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "ghost", "password": "Whatever123!"},
        )
        assert response.status_code == 401


class TestMe:
    def test_get_me_with_valid_token(self, client, auth_headers, registered_user):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == registered_user["username"]
        assert data["email"] == registered_user["email"]

    def test_get_me_without_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self, client):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
