"""Unit tests for browser utilities."""

import os
from unittest.mock import patch

import pytest

from familiar.utils.browser import create_llm


class TestCreateLLM:
    """Tests for LLM client creation."""

    def test_create_llm_anthropic(self):
        """Test creating Anthropic LLM client."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "anthropic",
                    "ANTHROPIC_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatAnthropic") as mock_chat,
        ):
            llm = create_llm(temperature=0.7)
            mock_chat.assert_called_once_with(
                model="claude-sonnet-4-0",
                temperature=0.7,
            )

    def test_create_llm_openai(self):
        """Test creating OpenAI LLM client."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "openai",
                    "OPENAI_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatOpenAI") as mock_chat,
        ):
            llm = create_llm(temperature=0.5)
            mock_chat.assert_called_once_with(
                model="gpt-4o",
                temperature=0.5,
            )

    def test_create_llm_google(self):
        """Test creating Google LLM client."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "google",
                    "GOOGLE_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatGoogle") as mock_chat,
        ):
            llm = create_llm(temperature=0.5)
            mock_chat.assert_called_once_with(
                model="gemini-flash-latest",
                temperature=0.5,
            )

    def test_create_llm_gemini_alias(self):
        """Test creating Gemini LLM client using gemini alias."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "gemini",
                    "GOOGLE_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatGoogle") as mock_chat,
        ):
            llm = create_llm(temperature=0.5)
            mock_chat.assert_called_once_with(
                model="gemini-flash-latest",
                temperature=0.5,
            )

    def test_create_llm_ollama(self):
        """Test creating Ollama LLM client (no API key required)."""
        with patch.dict(os.environ, {"FAMILIAR_MODEL_PROVIDER": "ollama"}, clear=True):
            with patch("browser_use.ChatOllama") as mock_chat:
                llm = create_llm(temperature=0.5)
                mock_chat.assert_called_once_with(
                    model="llama3.1:8b",
                    temperature=0.5,
                )

    def test_create_llm_browser_use(self):
        """Test creating Browser Use LLM client."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "browser-use",
                    "BROWSER_USE_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatBrowserUse") as mock_chat,
        ):
            llm = create_llm(temperature=0.5)
            mock_chat.assert_called_once_with(
                temperature=0.5,
            )

    def test_create_llm_groq(self):
        """Test creating Groq LLM client."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "groq",
                    "GROQ_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatGroq") as mock_chat,
        ):
            llm = create_llm(temperature=0.5)
            mock_chat.assert_called_once_with(
                model="llama-4-maverick-17b-128e-instruct",
                temperature=0.5,
            )

    def test_create_llm_azure(self):
        """Test creating Azure OpenAI LLM client."""
        with (
            patch.dict(
                os.environ,
                {
                    "FAMILIAR_MODEL_PROVIDER": "azure",
                    "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
                    "AZURE_OPENAI_API_KEY": "test-key-123",
                },
            ),
            patch("browser_use.ChatAzureOpenAI") as mock_chat,
        ):
            llm = create_llm(temperature=0.5)
            mock_chat.assert_called_once_with(
                model="gpt-4o",
                temperature=0.5,
            )

    def test_create_llm_invalid_provider(self):
        """Test error handling for invalid provider."""
        with patch.dict(os.environ, {"FAMILIAR_MODEL_PROVIDER": "invalid-provider"}, clear=True):
            with pytest.raises(ValueError, match="Unsupported model provider"):
                create_llm()

    def test_create_llm_missing_anthropic_api_key(self):
        """Test error handling for missing Anthropic API key."""
        with patch.dict(os.environ, {"FAMILIAR_MODEL_PROVIDER": "anthropic"}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                create_llm()

    def test_create_llm_missing_openai_api_key(self):
        """Test error handling for missing OpenAI API key."""
        with patch.dict(os.environ, {"FAMILIAR_MODEL_PROVIDER": "openai"}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                create_llm()
