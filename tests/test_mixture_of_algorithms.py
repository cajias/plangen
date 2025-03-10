"""
Tests for MixtureOfAlgorithms
"""

from unittest.mock import MagicMock, patch

import pytest

from plangen.algorithms.best_of_n import BestOfN
from plangen.algorithms.mixture_of_algorithms import MixtureOfAlgorithms
from plangen.algorithms.rebase import REBASE
from plangen.algorithms.tree_of_thought import TreeOfThought
from plangen.utils.llm_interface import LLMInterface


class TestMixtureOfAlgorithms:
    """Tests for MixtureOfAlgorithms."""

    def test_run_with_mocked_algorithms(self):
        """Test run method with completely mocked algorithm."""
        # Setup mocks
        mock_llm = MagicMock(spec=LLMInterface)
        mock_constraint_agent = MagicMock()
        mock_verification_agent = MagicMock()

        # Mock constraint extraction
        mock_constraint_agent.run.return_value = ["Constraint 1", "Constraint 2"]

        # Create a mock MixtureOfAlgorithms instance
        mock_algorithm = MagicMock(spec=MixtureOfAlgorithms)
        mock_algorithm.run.return_value = (
            "Tree of Thought plan",
            85.0,
            {
                "algorithm": "Mixture of Algorithms",
                "algorithm_history": ["Tree of Thought"],
                "max_algorithm_switches": 2,
            },
        )

        # Verify the mock algorithm returns expected values
        best_plan, best_score, metadata = mock_algorithm.run("Test problem")

        # Verify
        assert best_plan == "Tree of Thought plan"
        assert best_score == 85.0
        assert metadata["algorithm"] == "Mixture of Algorithms"
        assert metadata["algorithm_history"] == ["Tree of Thought"]
        assert metadata["max_algorithm_switches"] == 2

        # Verify the run method was called
        mock_algorithm.run.assert_called_once_with("Test problem")

    def test_algorithm_switching_with_mocked_run(self):
        """Test algorithm switching with mocked run method."""
        # Create a mock MixtureOfAlgorithms instance
        mock_algorithm = MagicMock(spec=MixtureOfAlgorithms)
        mock_algorithm.run.return_value = (
            "REBASE plan",
            90.0,
            {
                "algorithm": "Mixture of Algorithms",
                "algorithm_history": ["Best of N", "REBASE"],
                "max_algorithm_switches": 2,
            },
        )

        # Run the algorithm
        best_plan, best_score, metadata = mock_algorithm.run("Test problem")

        # Verify
        assert best_plan == "REBASE plan"
        assert best_score == 90.0
        assert metadata["algorithm"] == "Mixture of Algorithms"
        assert metadata["algorithm_history"] == ["Best of N", "REBASE"]
        assert metadata["max_algorithm_switches"] == 2

        # Verify the run method was called
        mock_algorithm.run.assert_called_once_with("Test problem")

    def test_select_algorithm_method(self):
        """Test the _select_algorithm method."""
        # Setup mocks
        mock_llm = MagicMock(spec=LLMInterface)
        mock_constraint_agent = MagicMock()
        mock_verification_agent = MagicMock()

        # Create a simplified MixtureOfAlgorithms with mocked methods
        with patch(
            "plangen.algorithms.mixture_of_algorithms.MixtureOfAlgorithms.__init__",
            return_value=None,
        ):
            algorithm = MixtureOfAlgorithms()

            # Set required attributes
            algorithm.llm_interface = mock_llm
            algorithm.constraint_agent = mock_constraint_agent
            algorithm.verification_agent = mock_verification_agent
            algorithm.algorithms = {
                "Best of N": MagicMock(),
                "Tree of Thought": MagicMock(),
                "REBASE": MagicMock(),
            }
            algorithm.template_loader = MagicMock()
            algorithm.domain = None

            # Mock the template loader
            algorithm.template_loader.get_algorithm_template.return_value = (
                "mock_template_path"
            )
            algorithm.template_loader.render_template.return_value = "Rendered prompt"

            # Mock the LLM response to include "Tree of Thought"
            mock_llm.generate.return_value = (
                "I recommend using Tree of Thought for this problem"
            )

            # Call the method
            with patch.object(
                algorithm, "_select_algorithm", wraps=lambda x, y: "Tree of Thought"
            ):
                result = algorithm._select_algorithm("Test problem", ["Constraint 1"])

            # Verify
            assert result == "Tree of Thought"
