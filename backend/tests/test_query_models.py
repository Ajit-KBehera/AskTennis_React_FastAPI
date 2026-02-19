"""
Unit tests for API models (Pydantic validation).
"""
import pytest
from pydantic import ValidationError
from app.api.routers.query import QueryRequest

class TestQueryModels:
    def test_query_request_valid(self):
        """Test valid QueryRequest."""
        req = QueryRequest(query="Who won Wimbledon?", session_id="abc")
        assert req.query == "Who won Wimbledon?"
        assert req.session_id == "abc"

    def test_query_request_minimal(self):
        """Test QueryRequest with only required fields."""
        req = QueryRequest(query="Test query")
        assert req.query == "Test query"
        assert req.session_id is None

    def test_query_request_empty_query(self):
        """Test that empty query strings are rejected."""
        with pytest.raises(ValidationError):
            QueryRequest(query="")
        
        with pytest.raises(ValidationError):
            QueryRequest(query="   ")

    def test_query_request_too_long(self):
        """Test that extremely long queries are rejected."""
        long_query = "a" * 2001
        with pytest.raises(ValidationError):
            QueryRequest(query=long_query)

    def test_query_request_normalize_session_id(self):
        """Test that session_id is normalized (empty-ish strings become None)."""
        req1 = QueryRequest(query="test", session_id="  ")
        assert req1.session_id is None
        
        req2 = QueryRequest(query="test", session_id=None)
        assert req2.session_id is None
