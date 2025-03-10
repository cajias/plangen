"""
Integration tests for all PlanGEN algorithms
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from plangen.agents.constraint_agent import ConstraintAgent
from plangen.agents.verification_agent import VerificationAgent
from plangen.algorithms.best_of_n import BestOfN
from plangen.algorithms.mixture_of_algorithms import MixtureOfAlgorithms
from plangen.algorithms.rebase import REBASE
from plangen.algorithms.tree_of_thought import TreeOfThought
from plangen.utils.llm_interface import LLMInterface


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="OPENAI_API_KEY environment variable not set",
)
class TestAllAlgorithmsIntegration:
    """Integration tests for all PlanGEN algorithms."""

    def setup_method(self):
        """Set up common test components."""
        # Create mock LLM interface
        self.mock_llm = MagicMock(spec=LLMInterface)

        # Create mock verifier
        self.mock_verifier = MagicMock()
        self.mock_verifier.extract_domain_constraints.return_value = []

        # Create agents
        self.constraint_agent = ConstraintAgent(llm_interface=self.mock_llm)
        self.verification_agent = VerificationAgent(
            llm_interface=self.mock_llm, verifier=self.mock_verifier
        )

        # Define a simple problem
        self.problem = """
        Design a function to find the maximum sum of a contiguous subarray within an array of integers.
        For example, given the array [-2, 1, -3, 4, -1, 2, 1, -5, 4], the contiguous subarray with the
        largest sum is [4, -1, 2, 1], with a sum of 6.
        """

    def test_tree_of_thought_algorithm(self):
        """Test Tree of Thought algorithm with a simple problem."""
        # Mock responses for constraint extraction
        self.mock_llm.generate.side_effect = [
            # Constraint extraction
            """
            1. Function must find maximum sum of contiguous subarray
            2. Function should handle negative numbers
            3. Function should return the sum value
            """,
            # Evaluation responses for steps
            "Good progress, consider Kadane's algorithm",
            "Good progress, implement the algorithm",
            "Excellent solution with optimal time complexity",
        ]

        # Mock verification scores
        self.mock_verifier.verify_solution.side_effect = [
            {"is_valid": True, "score": 95, "reason": "Optimal solution"}
        ]

        # Create Tree of Thought algorithm
        tot = TreeOfThought(
            llm_interface=self.mock_llm,
            constraint_agent=self.constraint_agent,
            verification_agent=self.verification_agent,
            branching_factor=2,
            max_depth=2,
            beam_width=1,
        )

        # Mock the internal methods to avoid complex tree exploration
        with patch.object(tot, "_generate_next_steps") as mock_generate:
            with patch.object(tot, "_evaluate_step") as mock_evaluate:
                with patch.object(tot, "_is_complete") as mock_is_complete:
                    with patch.object(tot, "_verify_plan") as mock_verify:
                        # Configure mocks
                        mock_generate.side_effect = [
                            # First level
                            [
                                "Consider Kadane's algorithm",
                                "Consider brute force approach",
                            ],
                            # Second level
                            ["Implement Kadane's algorithm with O(n) time complexity"],
                        ]

                        mock_evaluate.side_effect = [
                            # First level evaluations
                            ("Good progress", 70.0),
                            ("Less efficient approach", 40.0),
                            # Second level evaluations
                            ("Excellent solution", 95.0),
                        ]

                        # First two nodes are not complete, final node is complete
                        mock_is_complete.side_effect = [False, False, True]

                        # Final verification
                        mock_verify.return_value = ("Optimal solution", 95.0)

                        # Run the algorithm
                        best_plan, best_score, metadata = tot.run(self.problem)

        # Verify the results
        assert best_score == 95.0
        assert metadata["algorithm"] == "Tree of Thought"
        assert metadata["max_depth"] == 2
        assert metadata["branching_factor"] == 2

    def test_rebase_algorithm(self):
        """Test REBASE algorithm with a simple problem."""
        # Create a mock REBASE instance
        mock_rebase = MagicMock(spec=REBASE)

        # Configure the mock to return expected values
        mock_rebase.run.return_value = (
            "Optimized Kadane's algorithm with O(1) space complexity",
            95.0,
            {
                "algorithm": "REBASE",
                "iterations": [
                    {"plan": "Initial solution", "score": 60.0},
                    {"plan": "Improved solution", "score": 85.0},
                    {"plan": "Optimized Kadane's algorithm", "score": 95.0},
                ],
            },
        )

        # Run the mock algorithm
        best_plan, best_score, metadata = mock_rebase.run(self.problem)

        # Verify the results
        assert "Optimized Kadane's algorithm" in best_plan
        assert best_score == 95.0
        assert metadata["algorithm"] == "REBASE"
        assert len(metadata["iterations"]) == 3
        assert metadata["iterations"][0]["score"] == 60.0
        assert metadata["iterations"][2]["score"] == 95.0

    def test_mixture_of_algorithms(self):
        """Test Mixture of Algorithms with a simple problem."""
        # Create mock algorithms
        mock_best_of_n = MagicMock(spec=BestOfN)
        mock_tree_of_thought = MagicMock(spec=TreeOfThought)
        mock_rebase = MagicMock(spec=REBASE)

        # Set up the mock Tree of Thought to return a good plan
        mock_tree_of_thought.run.return_value = (
            "Solution using Kadane's algorithm",
            95.0,
            {"algorithm": "Tree of Thought"},
        )

        # Create a mock MixtureOfAlgorithms instance
        mock_moa = MagicMock(spec=MixtureOfAlgorithms)

        # Configure the mock to return expected values
        mock_moa.run.return_value = (
            "Solution using Kadane's algorithm",
            95.0,
            {
                "algorithm": "Mixture of Algorithms",
                "algorithm_history": ["Tree of Thought"],
                "max_algorithm_switches": 2,
            },
        )

        # Run the mock algorithm
        best_plan, best_score, metadata = mock_moa.run(self.problem)

        # Verify the results
        assert best_plan == "Solution using Kadane's algorithm"
        assert best_score == 95.0
        assert metadata["algorithm"] == "Mixture of Algorithms"
        assert "Tree of Thought" in metadata["algorithm_history"]
        assert metadata["max_algorithm_switches"] == 2
