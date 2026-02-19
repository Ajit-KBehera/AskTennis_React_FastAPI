"""
Unit tests for helper utility functions.
"""
import pytest
from utils.string_utils import safe_parse

class TestStringUtils:
    def test_safe_parse_list(self):
        """Test safe_parse returns list as is."""
        data = [{"a": 1}]
        assert safe_parse(data) == data

    def test_safe_parse_dict(self):
        """Test safe_parse wraps dict in list."""
        data = {"a": 1}
        assert safe_parse(data) == [data]

    def test_safe_parse_json_string(self):
        """Test safe_parse handles JSON strings."""
        data = '[{"a": 1}]'
        assert safe_parse(data) == [{"a": 1}]

    def test_safe_parse_literal_string(self):
        """Test safe_parse handles Python literal strings."""
        data = "[{'a': 1}]"
        assert safe_parse(data) == [{"a": 1}]

    def test_safe_parse_recursive(self):
        """Test safe_parse handles strings-within-lists (LLM pattern)."""
        data = ['[{"a": 1}]']
        assert safe_parse(data) == [{"a": 1}]

    def test_safe_parse_invalid(self):
        """Test safe_parse handles invalid content gracefully."""
        assert safe_parse(None) == []
        assert safe_parse("") == []
        assert safe_parse("just a string") == ["just a string"]
