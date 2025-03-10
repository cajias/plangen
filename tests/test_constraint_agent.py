"""
Tests for the ConstraintAgent class
"""

import unittest
from unittest.mock import MagicMock, patch

from plangen.agents.constraint_agent import ConstraintAgent
from plangen.models import BaseModelInterface
from plangen.prompts import PromptManager


class TestConstraintAgent(unittest.TestCase):
    """Test cases for the ConstraintAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock(spec=BaseModelInterface)
        self.mock_prompt_manager = MagicMock(spec=PromptManager)
        self.agent = ConstraintAgent(
            model=self.mock_model, prompt_manager=self.mock_prompt_manager
        )

    def test_run_extracts_constraints(self):
        """Test that run method extracts constraints correctly."""
        # Mock prompt manager responses
        self.mock_prompt_manager.get_system_message.return_value = (
            "You are a constraint extraction agent"
        )
        self.mock_prompt_manager.get_prompt.return_value = (
            "Extract constraints from: {problem}"
        )

        # Mock model response
        self.mock_model.generate.return_value = """
        1. Meeting duration must be 30 minutes
        2. Meeting must be on Monday
        3. Meeting must be between 9:00 and 17:00
        4. All participants must be available
        """

        problem_statement = """
        Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
        """

        constraints = self.agent.extract_constraints(problem_statement)

        # Check that the model was called with the correct prompt
        self.mock_prompt_manager.get_system_message.assert_called_once_with(
            "constraint"
        )
        self.mock_prompt_manager.get_prompt.assert_called_once()
        self.mock_model.generate.assert_called_once()

        # Check that constraints were extracted correctly
        self.assertIn("Meeting duration must be 30 minutes", constraints)
        self.assertIn("Meeting must be on Monday", constraints)
        self.assertIn("Meeting must be between 9:00 and 17:00", constraints)
        self.assertIn("All participants must be available", constraints)

    def test_run_handles_different_formats(self):
        """Test that extract_constraints method handles different constraint formats."""
        # Mock prompt manager responses
        self.mock_prompt_manager.get_system_message.return_value = (
            "You are a constraint extraction agent"
        )
        self.mock_prompt_manager.get_prompt.return_value = (
            "Extract constraints from: {problem}"
        )

        # Mock model response with different formats
        self.mock_model.generate.return_value = """
        1) Meeting duration must be 30 minutes
        - Meeting must be on Monday
        * Meeting must be between 9:00 and 17:00
        """

        problem_statement = """
        Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
        """

        constraints = self.agent.extract_constraints(problem_statement)

        # Check that constraints were extracted correctly despite different formats
        self.assertIn("Meeting duration must be 30 minutes", constraints)
        self.assertIn("Meeting must be on Monday", constraints)
        self.assertIn("Meeting must be between 9:00 and 17:00", constraints)


if __name__ == "__main__":
    unittest.main()
