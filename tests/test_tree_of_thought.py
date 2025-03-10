"""
Tests for TreeOfThought algorithm
"""

from unittest.mock import MagicMock, patch

import pytest

from plangen.algorithms.tree_of_thought import TreeOfThought
from plangen.utils.llm_interface import LLMInterface


class TestTreeOfThought:
    """Tests for TreeOfThought algorithm."""

    def test_initialization(self):
        """Test initialization."""
        # Setup mocks
        mock_llm = MagicMock(spec=LLMInterface)
        mock_constraint_agent = MagicMock()
        mock_verification_agent = MagicMock()

        # Create algorithm
        algorithm = TreeOfThought(
            llm_interface=mock_llm,
            constraint_agent=mock_constraint_agent,
            verification_agent=mock_verification_agent,
            branching_factor=3,
            max_depth=5,
            beam_width=2,
        )

        # Verify
        assert algorithm.llm_interface == mock_llm
        assert algorithm.constraint_agent == mock_constraint_agent
        assert algorithm.verification_agent == mock_verification_agent
        assert algorithm.branching_factor == 3
        assert algorithm.max_depth == 5
        assert algorithm.beam_width == 2

    def test_run_method(self):
        """Test run method."""
        # Setup mocks
        mock_llm = MagicMock(spec=LLMInterface)
        mock_constraint_agent = MagicMock()
        mock_verification_agent = MagicMock()

        # Mock responses
        mock_constraint_agent.run.return_value = ["Constraint 1", "Constraint 2"]

        # Mock LLM responses for tree exploration
        mock_llm.generate.side_effect = [
            # First level branches (generate_next_steps)
            "Step 1A",
            "Step 1B",
            # Second level branches (generate_next_steps)
            "Step 2A from 1A",
            "Step 2B from 1A",
            # Evaluation of steps
            "Good intermediate step",
            "Not as good step",
            "Good next step",
            "Better next step",
            # Verification for complete paths
            "Good complete solution",
            "Best complete solution",
        ]

        # Mock verification scores
        mock_verification_agent.run.side_effect = [
            ("Good path", 70.0),  # For 1A + 2A
            ("Best path", 90.0),  # For 1A + 2B
        ]

        # Create algorithm with minimal branching for test
        algorithm = TreeOfThought(
            llm_interface=mock_llm,
            constraint_agent=mock_constraint_agent,
            verification_agent=mock_verification_agent,
            branching_factor=2,  # Only generate 2 branches at each step
            max_depth=2,  # Only go 2 levels deep
            beam_width=1,  # Only keep the best path at each level
        )

        # Patch the methods we need to control
        with patch.object(algorithm, "_generate_next_steps") as mock_generate:
            with patch.object(algorithm, "_evaluate_step") as mock_evaluate:
                with patch.object(algorithm, "_is_complete") as mock_is_complete:
                    with patch.object(algorithm, "_verify_plan") as mock_verify:
                        # Set up the mocks
                        mock_generate.side_effect = [
                            # First level branches
                            ["Step 1A", "Step 1B"],
                            # Second level branches from 1A
                            ["Step 2A from 1A", "Step 2B from 1A"],
                        ]

                        mock_evaluate.side_effect = [
                            ("Good intermediate step", 50.0),  # For 1A
                            ("Not as good step", 30.0),  # For 1B
                            ("Good next step", 70.0),  # For 1A + 2A
                            ("Better next step", 90.0),  # For 1A + 2B
                        ]

                        # First check is not complete, second depth is complete
                        mock_is_complete.side_effect = [False, False, True, True]

                        # Verification scores for complete paths
                        mock_verify.side_effect = [
                            ("Good complete solution", 70.0),  # For 1A + 2A
                            ("Best complete solution", 90.0),  # For 1A + 2B
                        ]

                        # Run algorithm
                        best_plan, best_score, metadata = algorithm.run("Test problem")

        # Verify
        assert "Step 2B from 1A" in best_plan
        assert best_score == 90.0
        assert metadata["algorithm"] == "Tree of Thought"
        assert metadata["max_depth"] == 2
        assert metadata["branching_factor"] == 2
        assert metadata["beam_width"] == 1
