"""
Unit tests for security utilities (password hashing + JWT).
"""
import pytest
from datetime import timedelta

from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = get_password_hash("MyPassword123!")
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_correct_password(self):
        password = "MyPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_empty_password(self):
        hashed = get_password_hash("SomePassword")
        assert verify_password("", hashed) is False

    def test_same_password_produces_different_hashes(self):
        """bcrypt salts → different hashes each time."""
        password = "SamePassword123!"
        h1 = get_password_hash(password)
        h2 = get_password_hash(password)
        assert h1 != h2
        # Both must verify
        assert verify_password(password, h1)
        assert verify_password(password, h2)

    def test_long_password_truncated_to_72_bytes(self):
        """bcrypt limit: passwords > 72 bytes must not raise."""
        long_pwd = "A" * 200
        hashed = get_password_hash(long_pwd)  # must not raise
        assert verify_password(long_pwd, hashed) is True

    def test_unicode_password(self):
        """Unicode chars should work."""
        password = "كلمةالمرور123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True


class TestJWT:
    def test_create_token_returns_string(self):
        token = create_access_token({"sub": "testuser"})
        assert isinstance(token, str)
        assert len(token) > 20
        assert token.count(".") == 2  # JWT has 3 parts

    def test_decode_valid_token(self):
        token = create_access_token({"sub": "testuser", "role": "analyst"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "analyst"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_invalid_token(self):
        assert decode_access_token("not.a.valid.token") is None
        assert decode_access_token("") is None
        assert decode_access_token("a.b") is None

    def test_decode_token_with_wrong_secret(self):
        """Tokens signed with different keys must fail."""
        from jose import jwt
        bad_token = jwt.encode({"sub": "x"}, "wrong-secret", algorithm="HS256")
        assert decode_access_token(bad_token) is None

    def test_expired_token_returns_none(self):
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(seconds=-1),
        )
        assert decode_access_token(token) is None
