"""
Integration tests for PlanGEN
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from plangen import PlanGEN
from plangen.models import OpenAIModelInterface
from plangen.prompts import PromptManager


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="OPENAI_API_KEY environment variable not set",
)
class TestPlanGENIntegration:
    """Integration tests for PlanGEN."""

    def test_simple_problem(self):
        """Test PlanGEN with a simple problem."""
        # Create PlanGEN
        model = OpenAIModelInterface(model_name="gpt-3.5-turbo")
        prompt_manager = PromptManager()
        plangen = PlanGEN(model=model, prompt_manager=prompt_manager, num_solutions=2)

        # Define a simple problem
        problem = """
        Design a function to find the maximum sum of a contiguous subarray within an array of integers.
        For example, given the array [-2, 1, -3, 4, -1, 2, 1, -5, 4], the contiguous subarray with the
        largest sum is [4, -1, 2, 1], with a sum of 6.
        """

        # Solve the problem
        result = plangen.solve(problem)

        # Verify the result structure
        assert "problem" in result
        assert "constraints" in result
        assert "solutions" in result
        assert "verification_results" in result
        assert "selected_solution" in result

        # Verify the solutions
        assert len(result["solutions"]) == 2
        assert isinstance(result["solutions"][0], str)
        assert isinstance(result["solutions"][1], str)

        # Verify the selected solution
        assert "selected_solution" in result["selected_solution"]
        assert "selection_reasoning" in result["selected_solution"]
        assert "selected_index" in result["selected_solution"]

    @pytest.mark.parametrize(
        "problem",
        [
            """
            Design a function to check if a string is a palindrome, considering only alphanumeric characters
            and ignoring case. For example, "A man, a plan, a canal: Panama" should return true.
            """,
            """
            Implement a stack data structure with O(1) time complexity for push, pop, and finding the minimum element.
            """,
        ],
    )
    def test_multiple_problems(self, problem):
        """Test PlanGEN with multiple problems."""
        # Create PlanGEN with mocked model to speed up tests
        mock_model = MagicMock()
        mock_model.generate.side_effect = [
            "1. Input must be an array\n2. Function should return a number",  # constraints
            "Solution using Kadane's algorithm",  # solution 1
            "Solution using divide and conquer",  # solution 2
            "Verification of solution 1",  # verification 1
            "Verification of solution 2",  # verification 2
            "Solution 1 is better because...",  # selection
        ]

        prompt_manager = PromptManager()
        plangen = PlanGEN(
            model=mock_model, prompt_manager=prompt_manager, num_solutions=2
        )

        # Solve the problem
        result = plangen.solve(problem)

        # Verify the result structure
        assert "problem" in result
        assert "constraints" in result
        assert "solutions" in result
        assert "verification_results" in result
        assert "selected_solution" in result

        # Verify the mock calls
        assert mock_model.generate.call_count == 6
