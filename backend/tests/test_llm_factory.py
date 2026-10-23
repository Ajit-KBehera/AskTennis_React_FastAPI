"""
Unit tests for LLMFactory and Config provider switching.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from app.core.config.config import Config
from app.infrastructure.llm.llm_setup import LLMFactory


class TestLLMFactoryAndConfig:
    def test_config_ollama_provider(self, monkeypatch):
        """Test Config initialization and validation for Ollama provider."""
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("DEFAULT_MODEL", "qwen2.5-coder:7b")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GCP_PROJECT_ID", raising=False)

        config = Config()
        assert config.llm_provider == "ollama"
        assert config.model_name == "qwen2.5-coder:7b"
        assert config.api_key == ""
        assert config.validate_config() is True

    def test_create_llm_ollama(self):
        """Test LLMFactory creates ChatOllama for ollama provider."""
        llm = LLMFactory.create_llm(
            provider="ollama",
            model="qwen2.5-coder:7b",
            base_url="http://localhost:11434",
            temperature=0.0,
        )
        assert llm is not None
        assert getattr(llm, "model", None) == "qwen2.5-coder:7b"
        assert hasattr(llm, "bind_tools")

    def test_create_llm_gemini(self):
        """Test LLMFactory creates ChatGoogleGenerativeAI for gemini provider."""
        llm = LLMFactory.create_llm(
            provider="gemini",
            api_key="fake-test-key",
            model="gemini-1.5-flash",
            temperature=0.0,
        )
        assert llm is not None
        assert getattr(llm, "model", None) == "gemini-1.5-flash"
