"""
Unit tests for the AuthService (Hashing and JWT logic).
"""
import pytest
from datetime import timedelta
from services.auth_service import AuthService
from jose import jwt
from constants import JWT_SECRET_KEY, JWT_ALGORITHM

class TestAuthService:
    def test_password_hashing(self):
        """Test that passwords are hashed and can be verified."""
        password = "secure_password_123"
        hashed = AuthService.get_password_hash(password)
        
        assert hashed != password
        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrong_password", hashed) is False

    def test_create_access_token(self):
        """Test JWT token creation and content."""
        data = {"sub": "testuser", "role": "admin"}
        token = AuthService.create_access_token(data)
        
        assert isinstance(token, str)
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_create_access_token_expiry(self):
        """Test JWT token creation with custom expiry."""
        data = {"sub": "testuser"}
        expires = timedelta(minutes=60)
        token = AuthService.create_access_token(data, expires_delta=expires)
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert "exp" in payload

    def test_decode_token_success(self):
        """Test successful token decoding."""
        data = {"sub": "testuser"}
        token = AuthService.create_access_token(data)
        
        decoded = AuthService.decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "testuser"

    def test_decode_token_invalid(self):
        """Test decoding an invalid token returns None."""
        assert AuthService.decode_token("invalid.token.here") is None
        assert AuthService.decode_token("") is None
