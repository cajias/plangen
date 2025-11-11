"""
Regression tests for issue #26: VerificationAgent missing verify_solutions method.

Issue: https://github.com/cajias/plangen/issues/26

The VerificationAgent class was missing the verify_solutions method, which caused
the simple_example.py to fail. This test ensures the bug doesn't reoccur.
"""

from unittest.mock import MagicMock

import pytest

from plangen import PlanGEN
from plangen.agents import VerificationAgent
from plangen.models import BaseModelInterface
from plangen.prompts import PromptManager


class TestIssue26Regression:
    """Regression tests for issue #26."""

    def test_verification_agent_has_verify_solutions_method(self):
        """Test that VerificationAgent has verify_solutions method with correct signature."""
        # Create mock dependencies
        mock_model = MagicMock(spec=BaseModelInterface)
        mock_prompt_manager = MagicMock(spec=PromptManager)

        # Create agent
        agent = VerificationAgent(mock_model, mock_prompt_manager)

        # Verify method exists
        assert hasattr(
            agent, "verify_solutions"
        ), "VerificationAgent must have verify_solutions method"
        assert callable(agent.verify_solutions), "verify_solutions must be callable"

    def test_verification_agent_signature_matches_expected(self):
        """Test that verify_solutions accepts expected parameters."""
        mock_model = MagicMock(spec=BaseModelInterface)
        mock_prompt_manager = MagicMock(spec=PromptManager)

        # Configure mocks
        mock_model.generate.return_value = "Verification passed"
        mock_prompt_manager.get_system_message.return_value = "System message"
        mock_prompt_manager.get_prompt.return_value = "Prompt"

        agent = VerificationAgent(mock_model, mock_prompt_manager)

        # Call with the expected signature from PlanGEN._verify_solutions
        solutions = ["Solution 1", "Solution 2", "Solution 3"]
        constraints = "Test constraints"

        result = agent.verify_solutions(solutions, constraints)

        # Verify return type and content
        assert isinstance(result, list), "verify_solutions must return a list"
        assert len(result) == 3, "Should return one result per solution"
        assert all(
            r == "Verification passed" for r in result
        ), "All results should be verification strings"

    def test_plangen_can_call_verification_agent_verify_solutions(self):
        """Test that PlanGEN workflow can successfully call verify_solutions."""
        # Create mocks
        mock_model = MagicMock(spec=BaseModelInterface)
        mock_prompt_manager = MagicMock(spec=PromptManager)

        # Configure mocks to return proper values
        mock_model.generate.side_effect = [
            "Constraint 1\nConstraint 2",  # constraint extraction
            "Solution 1",
            "Solution 2",
            "Solution 3",  # solution generation
            "Verification 1",
            "Verification 2",
            "Verification 3",  # verification
            "Solution 1 is best",  # selection
        ]
        mock_prompt_manager.get_system_message.return_value = "System message"
        mock_prompt_manager.get_prompt.return_value = "Prompt"

        # Create PlanGEN instance
        plangen = PlanGEN(
            model=mock_model, prompt_manager=mock_prompt_manager, num_solutions=3
        )

        # Create a state that triggers verification
        state = {
            "problem": "Test problem",
            "constraints": "Test constraints",
            "solutions": ["Solution 1", "Solution 2", "Solution 3"],
        }

        # Call _verify_solutions directly (this is what failed in issue #26)
        result = plangen._verify_solutions(state)

        # Verify result
        assert "verification_results" in result, "Should return verification_results"
        assert isinstance(
            result["verification_results"], list
        ), "verification_results must be a list"
        assert len(result["verification_results"]) == 3, "Should have 3 results"

    def test_agent_initialization_matches_plangen_expectations(self):
        """Test that VerificationAgent can be initialized as PlanGEN expects."""
        # This tests the exact initialization pattern used in PlanGEN.__init__
        mock_model = MagicMock(spec=BaseModelInterface)
        mock_prompt_manager = MagicMock(spec=PromptManager)

        # This should not raise any errors
        agent = VerificationAgent(mock_model, mock_prompt_manager)

        # Verify the agent has the expected attributes
        assert hasattr(agent, "model"), "Agent should have model attribute"
        assert hasattr(
            agent, "prompt_manager"
        ), "Agent should have prompt_manager attribute"
        assert agent.model is mock_model
        assert agent.prompt_manager is mock_prompt_manager
