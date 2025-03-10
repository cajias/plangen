"""
Tests for model interfaces
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from plangen.models import BedrockModelInterface, OpenAIModelInterface


class TestOpenAIModelInterface:
    """Tests for OpenAIModelInterface."""

    @patch("openai.OpenAI")
    def test_initialization(self, mock_openai):
        """Test initialization with API key."""
        # Test with explicit API key
        model = OpenAIModelInterface(api_key="test_key")
        assert model.api_key == "test_key"
        assert model.model_name == "gpt-4o"
        assert model.temperature == 0.7
        assert model.max_tokens == 1024

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"})
    @patch("openai.OpenAI")
    def test_initialization_from_env(self, mock_openai):
        """Test initialization with API key from environment."""
        model = OpenAIModelInterface()
        assert model.api_key == "env_key"

    @patch("openai.OpenAI")
    def test_initialization_no_key(self, mock_openai):
        """Test initialization with no API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                OpenAIModelInterface()

    @patch("openai.OpenAI")
    def test_generate(self, mock_openai):
        """Test generate method."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Generated text"

        # Create model and test
        with patch.object(
            OpenAIModelInterface, "generate", return_value="Generated text"
        ):
            model = OpenAIModelInterface(api_key="test_key")
            result = model.generate("Test prompt")

        # Verify
        assert result == "Generated text"

    @patch("openai.OpenAI")
    def test_batch_generate(self, mock_openai):
        """Test batch_generate method."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Generated text"

        # Create model and test
        with patch.object(
            OpenAIModelInterface, "generate", return_value="Generated text"
        ):
            model = OpenAIModelInterface(api_key="test_key")
            results = model.batch_generate(["Prompt 1", "Prompt 2"])

        # Verify
        assert results == ["Generated text", "Generated text"]


class TestBedrockModelInterface:
    """Tests for BedrockModelInterface."""

    @patch("boto3.Session")
    def test_initialization(self, mock_session):
        """Test initialization."""
        # Setup mock
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client

        # Create model and test
        model = BedrockModelInterface(model_id="anthropic.claude-v2")

        # Verify
        assert model.model_id == "anthropic.claude-v2"
        assert model.temperature == 0.7
        assert model.max_tokens == 1024
        mock_session.return_value.client.assert_called_with(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            config=mock_session.return_value.client.call_args[1][
                "config"
            ],  # Just use the actual config
        )

    @patch("boto3.Session")
    def test_format_prompt_claude(self, mock_session):
        """Test prompt formatting for Claude."""
        # Setup mock
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client

        # Create model and test
        model = BedrockModelInterface(model_id="anthropic.claude-v2")

        # Test without system message
        prompt = model._format_prompt("Test prompt")
        assert prompt == "Human: Test prompt\n\nAssistant:"

        # Test with system message
        prompt = model._format_prompt("Test prompt", "System message")
        assert prompt == "System: System message\n\nHuman: Test prompt\n\nAssistant:"

    @patch("boto3.Session")
    def test_format_prompt_titan(self, mock_session):
        """Test prompt formatting for Titan."""
        # Setup mock
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client

        # Create model and test
        model = BedrockModelInterface(model_id="amazon.titan-text-express-v1")

        # Test without system message
        prompt = model._format_prompt("Test prompt")
        assert prompt == "User: Test prompt\nAssistant:"

        # Test with system message
        prompt = model._format_prompt("Test prompt", "System message")
        assert prompt == "System: System message\nUser: Test prompt\nAssistant:"

    @patch("boto3.Session")
    @patch("json.loads")
    def test_parse_response_claude(self, mock_loads, mock_session):
        """Test response parsing for Claude."""
        # Setup mocks
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_response = MagicMock()
        mock_response_body = MagicMock()
        mock_response["body"] = mock_response_body
        mock_response_body.read.return_value = "{}"
        mock_loads.return_value = {"completion": "Generated text"}

        # Create model and test
        model = BedrockModelInterface(model_id="anthropic.claude-v2")
        result = model._parse_response(mock_response)

        # Verify
        assert result == "Generated text"

    @patch("boto3.Session")
    @patch("json.loads")
    def test_parse_response_titan(self, mock_loads, mock_session):
        """Test response parsing for Titan."""
        # Setup mocks
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_response = MagicMock()
        mock_response_body = MagicMock()
        mock_response["body"] = mock_response_body
        mock_response_body.read.return_value = "{}"
        mock_loads.return_value = {"outputText": "Generated text"}

        # Create model and test
        model = BedrockModelInterface(model_id="amazon.titan-text-express-v1")
        result = model._parse_response(mock_response)

        # Verify
        assert result == "Generated text"
