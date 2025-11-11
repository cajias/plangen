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

    def test_extract_constraints_method_exists(self):
        """Regression test for issue #25: Verify extract_constraints method exists."""
        # Verify that the extract_constraints method exists
        self.assertTrue(
            hasattr(self.agent, 'extract_constraints'),
            "ConstraintAgent must have extract_constraints method"
        )
        self.assertTrue(
            callable(getattr(self.agent, 'extract_constraints')),
            "extract_constraints must be callable"
        )

    def test_extract_constraints_delegates_to_run(self):
        """Regression test for issue #25: Verify extract_constraints and run produce same results."""
        # Mock the llm_interface used by ConstraintAgent
        mock_llm_interface = MagicMock()
        mock_llm_interface.generate.return_value = """
        1. Constraint one
        2. Constraint two
        3. Constraint three
        """

        agent = ConstraintAgent(llm_interface=mock_llm_interface)
        problem_statement = "Test problem statement"

        # Call both methods
        result_from_run = agent.run(problem_statement)
        result_from_extract = agent.extract_constraints(problem_statement)

        # Verify both methods produce the same results
        self.assertEqual(
            result_from_run,
            result_from_extract,
            "extract_constraints should delegate to run and produce identical results"
        )

        # Verify both contain expected constraints
        self.assertIn("Constraint one", result_from_run)
        self.assertIn("Constraint two", result_from_run)
        self.assertIn("Constraint three", result_from_run)


if __name__ == "__main__":
    unittest.main()
