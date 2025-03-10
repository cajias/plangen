"""
Tests for prompt manager
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from plangen.prompts import PromptManager


class TestPromptManager:
    """Tests for PromptManager."""

    def test_initialization_default_dir(self):
        """Test initialization with default templates directory."""
        manager = PromptManager()
        assert os.path.exists(manager.templates_dir)
        assert manager.env is not None

    def test_initialization_custom_dir(self, tmp_path):
        """Test initialization with custom templates directory."""
        templates_dir = str(tmp_path)
        manager = PromptManager(templates_dir=templates_dir)
        assert manager.templates_dir == templates_dir
        assert manager.env is not None

    @patch("jinja2.Environment")
    def test_render(self, mock_env):
        """Test render method."""
        # Setup mock
        mock_template = MagicMock()
        mock_env.return_value.get_template.return_value = mock_template
        mock_template.render.return_value = "Rendered template"

        # Create manager and test
        manager = PromptManager()
        result = manager.render("test_template", var1="value1", var2="value2")

        # Verify
        assert result == "Rendered template"
        mock_env.return_value.get_template.assert_called_with("test_template.j2")
        mock_template.render.assert_called_with(var1="value1", var2="value2")

    @patch("plangen.prompts.prompt_manager.PromptManager.render")
    def test_get_system_message(self, mock_render):
        """Test get_system_message method."""
        # Setup mock
        mock_render.return_value = "System message"

        # Create manager and test
        manager = PromptManager()
        result = manager.get_system_message("constraint")

        # Verify
        assert result == "System message"
        mock_render.assert_called_with("system_constraint")

    @patch("plangen.prompts.prompt_manager.PromptManager.render")
    def test_get_prompt(self, mock_render):
        """Test get_prompt method."""
        # Setup mock
        mock_render.return_value = "Rendered prompt"

        # Create manager and test
        manager = PromptManager()
        result = manager.get_prompt("constraint_extraction", problem="Test problem")

        # Verify
        assert result == "Rendered prompt"
        mock_render.assert_called_with("constraint_extraction", problem="Test problem")
