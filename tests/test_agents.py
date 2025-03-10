"""
Tests for agents
"""

from unittest.mock import MagicMock, patch

import pytest

from plangen.agents import (
    ConstraintAgent,
    SelectionAgent,
    Solution,
    SolutionAgent,
    VerificationAgent,
)


class TestConstraintAgent:
    """Tests for ConstraintAgent."""

    def test_extract_constraints(self):
        """Test constraint extraction."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()

        mock_model.generate.return_value = "Extracted constraints"
        mock_prompt_manager.get_system_message.return_value = "System message"
        mock_prompt_manager.get_prompt.return_value = "Prompt"

        # Create agent and test
        agent = ConstraintAgent(mock_model, mock_prompt_manager)
        result = agent.extract_constraints("Test problem")

        # Verify
        assert result == "Extracted constraints"
        mock_prompt_manager.get_system_message.assert_called_with("constraint")
        mock_prompt_manager.get_prompt.assert_called_with(
            "constraint_extraction", problem="Test problem"
        )
        mock_model.generate.assert_called_with(
            "Prompt", system_message="System message"
        )


class TestSolutionAgent:
    """Tests for SolutionAgent."""

    def test_generate_solutions(self):
        """Test solution generation."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()

        mock_model.generate.return_value = "Generated solution"
        mock_prompt_manager.get_prompt.return_value = "Prompt"

        # Create agent and test
        agent = SolutionAgent(mock_model, mock_prompt_manager)
        results = agent.generate_solutions(
            "Test problem", "Test constraints", num_solutions=2
        )

        # Verify
        assert results == ["Generated solution", "Generated solution"]
        assert mock_model.generate.call_count == 2
        mock_prompt_manager.get_prompt.assert_called_with(
            "solution_generation",
            problem="Test problem",
            constraints="Test constraints",
        )


class TestVerificationAgent:
    """Tests for VerificationAgent."""

    def test_verify_solutions(self):
        """Test solution verification."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()

        mock_model.generate.return_value = "Verification result"
        mock_prompt_manager.get_system_message.return_value = "System message"
        mock_prompt_manager.get_prompt.return_value = "Prompt"

        # Create agent and test
        agent = VerificationAgent(mock_model, mock_prompt_manager)
        results = agent.verify_solutions(
            ["Solution 1", "Solution 2"], "Test constraints"
        )

        # Verify
        assert results == ["Verification result", "Verification result"]
        assert mock_model.generate.call_count == 2
        mock_prompt_manager.get_system_message.assert_called_with("verification")
        assert mock_prompt_manager.get_prompt.call_count == 2


class TestSelectionAgent:
    """Tests for SelectionAgent."""

    def test_select_best_solution(self):
        """Test solution selection."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()

        mock_model.generate.return_value = "Solution 1 is the best..."
        mock_prompt_manager.get_system_message.return_value = "System message"
        mock_prompt_manager.get_prompt.return_value = "Prompt"

        # Create agent and test
        agent = SelectionAgent(mock_model, mock_prompt_manager)
        result = agent.select_best_solution(
            ["Solution 1", "Solution 2"],
            ["Verification 1", "Verification 2"],
        )

        # Verify
        assert result["selected_solution"] == "Solution 1"
        assert result["selection_reasoning"] == "Solution 1 is the best..."
        assert result["selected_index"] == 0
        mock_prompt_manager.get_system_message.assert_called_with("selection")
        mock_prompt_manager.get_prompt.assert_called_once()
        mock_model.generate.assert_called_with(
            "Prompt", system_message="System message"
        )
