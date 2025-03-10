"""
Tests for PlanGEN workflow
"""

from unittest.mock import MagicMock, patch

import pytest

from plangen import PlanGEN
from plangen.plangen import PlanGENState


class TestPlanGEN:
    """Tests for PlanGEN."""

    def test_initialization(self):
        """Test initialization."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()

        # Create PlanGEN and test
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
            num_solutions=3,
        )

        # Verify
        assert plangen.model == mock_model
        assert plangen.prompt_manager == mock_prompt_manager
        assert plangen.num_solutions == 3
        assert plangen.constraint_agent is not None
        assert plangen.solution_agent is not None
        assert plangen.verification_agent is not None
        assert plangen.selection_agent is not None
        assert plangen.workflow is not None

    def test_extract_constraints(self):
        """Test _extract_constraints method."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()

        # Create PlanGEN
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.constraint_agent = mock_constraint_agent
        mock_constraint_agent.extract_constraints.return_value = "Extracted constraints"

        # Test
        state = {"problem": "Test problem"}
        result = plangen._extract_constraints(state)

        # Verify
        assert result == {"constraints": "Extracted constraints"}
        mock_constraint_agent.extract_constraints.assert_called_with("Test problem")

    def test_extract_constraints_error(self):
        """Test _extract_constraints method with error."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_constraint_agent = MagicMock()

        # Create PlanGEN
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.constraint_agent = mock_constraint_agent
        mock_constraint_agent.extract_constraints.side_effect = Exception("Test error")

        # Test
        state = {"problem": "Test problem"}
        result = plangen._extract_constraints(state)

        # Verify
        assert "error" in result
        assert "Test error" in result["error"]

    def test_generate_solutions(self):
        """Test _generate_solutions method."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_solution_agent = MagicMock()

        # Create PlanGEN
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
            num_solutions=2,
        )
        plangen.solution_agent = mock_solution_agent
        mock_solution_agent.generate_solutions.return_value = [
            "Solution 1",
            "Solution 2",
        ]

        # Test
        state = {"problem": "Test problem", "constraints": "Test constraints"}
        result = plangen._generate_solutions(state)

        # Verify
        assert result == {"solutions": ["Solution 1", "Solution 2"]}
        mock_solution_agent.generate_solutions.assert_called_with(
            "Test problem", "Test constraints", num_solutions=2
        )

    def test_verify_solutions(self):
        """Test _verify_solutions method."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_verification_agent = MagicMock()

        # Create PlanGEN
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.verification_agent = mock_verification_agent
        mock_verification_agent.verify_solutions.return_value = [
            "Verification 1",
            "Verification 2",
        ]

        # Test
        state = {
            "solutions": ["Solution 1", "Solution 2"],
            "constraints": "Test constraints",
        }
        result = plangen._verify_solutions(state)

        # Verify
        assert result == {"verification_results": ["Verification 1", "Verification 2"]}
        mock_verification_agent.verify_solutions.assert_called_with(
            ["Solution 1", "Solution 2"], "Test constraints"
        )

    def test_select_solution(self):
        """Test _select_solution method."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_selection_agent = MagicMock()

        # Create PlanGEN
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        plangen.selection_agent = mock_selection_agent
        mock_selection_agent.select_best_solution.return_value = {
            "selected_solution": "Solution 1",
            "selection_reasoning": "Reasoning",
            "selected_index": 0,
        }

        # Test
        state = {
            "solutions": ["Solution 1", "Solution 2"],
            "verification_results": ["Verification 1", "Verification 2"],
        }
        result = plangen._select_solution(state)

        # Verify
        assert result == {
            "selected_solution": {
                "selected_solution": "Solution 1",
                "selection_reasoning": "Reasoning",
                "selected_index": 0,
            }
        }
        mock_selection_agent.select_best_solution.assert_called_with(
            ["Solution 1", "Solution 2"], ["Verification 1", "Verification 2"]
        )

    @patch("plangen.plangen.PlanGEN._build_workflow")
    def test_solve(self, mock_build_workflow):
        """Test solve method."""
        # Setup mocks
        mock_model = MagicMock()
        mock_prompt_manager = MagicMock()
        mock_workflow = MagicMock()
        mock_build_workflow.return_value = mock_workflow

        # Expected result
        expected_result = {
            "problem": "Test problem",
            "constraints": "Extracted constraints",
            "solutions": ["Solution 1", "Solution 2"],
            "verification_results": ["Verification 1", "Verification 2"],
            "selected_solution": {
                "selected_solution": "Solution 1",
                "selection_reasoning": "Reasoning",
                "selected_index": 0,
            },
        }
        mock_workflow.invoke.return_value = expected_result

        # Create PlanGEN and test
        plangen = PlanGEN(
            model=mock_model,
            prompt_manager=mock_prompt_manager,
        )
        result = plangen.solve("Test problem")

        # Verify
        assert result == expected_result
        mock_workflow.invoke.assert_called_with({"problem": "Test problem"})
