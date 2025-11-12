"""Tests for type definitions in plangen.types module."""

import pytest

from plangen.types import (AlgorithmResult, PlanResult, SolveResult,
                           VerificationResult)


class TestVerificationResult:
    """Tests for VerificationResult TypedDict."""

    def test_verification_result_creation(self):
        """Test creating a VerificationResult."""
        result = VerificationResult(
            is_valid=True,
            score=85.5,
            reason="Solution meets all constraints",
            feedback="Good work on addressing the requirements",
        )

        assert result["is_valid"] is True
        assert result["score"] == 85.5
        assert result["reason"] == "Solution meets all constraints"
        assert result["feedback"] == "Good work on addressing the requirements"

    def test_verification_result_with_none_feedback(self):
        """Test creating a VerificationResult with None feedback."""
        result = VerificationResult(
            is_valid=False,
            score=30.0,
            reason="Missing critical steps",
            feedback=None,
        )

        assert result["is_valid"] is False
        assert result["score"] == 30.0
        assert result["feedback"] is None

    def test_verification_result_invalid(self):
        """Test VerificationResult for invalid solution."""
        result = VerificationResult(
            is_valid=False,
            score=0.0,
            reason="Solution does not address the problem",
            feedback=None,
        )

        assert result["is_valid"] is False
        assert result["score"] == 0.0


class TestSolveResult:
    """Tests for SolveResult TypedDict."""

    def test_solve_result_success(self):
        """Test creating a successful SolveResult."""
        result = SolveResult(
            problem="Test problem",
            constraints="Test constraints",
            solutions=["Solution 1", "Solution 2"],
            verification_results=["Result 1", "Result 2"],
            selected_solution={"solution": "Solution 1", "score": 90.0},
            score=90.0,
            metadata={"iterations": 3},
            error=None,
        )

        assert result["problem"] == "Test problem"
        assert result["constraints"] == "Test constraints"
        assert len(result["solutions"]) == 2
        assert result["score"] == 90.0
        assert result["error"] is None

    def test_solve_result_with_error(self):
        """Test creating a SolveResult with error."""
        result = SolveResult(
            problem="Test problem",
            constraints=None,
            solutions=None,
            verification_results=None,
            selected_solution=None,
            score=None,
            metadata={},
            error="Failed to extract constraints",
        )

        assert result["problem"] == "Test problem"
        assert result["error"] == "Failed to extract constraints"
        assert result["solutions"] is None
        assert result["score"] is None

    def test_solve_result_partial(self):
        """Test creating a partial SolveResult."""
        result = SolveResult(
            problem="Test problem",
            constraints="Some constraints",
            solutions=["Solution 1"],
            verification_results=None,
            selected_solution=None,
            score=None,
            metadata={},
            error="Error during verification",
        )

        assert result["problem"] == "Test problem"
        assert result["constraints"] == "Some constraints"
        assert result["solutions"] is not None
        assert result["verification_results"] is None
        assert result["error"] is not None


class TestAlgorithmResult:
    """Tests for AlgorithmResult TypedDict."""

    def test_algorithm_result_creation(self):
        """Test creating an AlgorithmResult."""
        result = AlgorithmResult(
            best_plan="Detailed plan here",
            score=95.0,
            metadata={
                "algorithm": "best_of_n",
                "n_plans": 5,
                "iterations": 1,
            },
        )

        assert result["best_plan"] == "Detailed plan here"
        assert result["score"] == 95.0
        assert result["metadata"]["algorithm"] == "best_of_n"
        assert result["metadata"]["n_plans"] == 5

    def test_algorithm_result_with_empty_metadata(self):
        """Test AlgorithmResult with empty metadata."""
        result = AlgorithmResult(
            best_plan="Simple plan",
            score=70.0,
            metadata={},
        )

        assert result["best_plan"] == "Simple plan"
        assert result["score"] == 70.0
        assert result["metadata"] == {}


class TestPlanResult:
    """Tests for PlanResult TypedDict."""

    def test_plan_result_creation(self):
        """Test creating a PlanResult."""
        result = PlanResult(
            problem="Find the kth largest element",
            selected_solution="Use quickselect algorithm",
            score=88.5,
            metadata={
                "algorithm": "tree_of_thought",
                "depth": 3,
            },
        )

        assert result["problem"] == "Find the kth largest element"
        assert result["selected_solution"] == "Use quickselect algorithm"
        assert result["score"] == 88.5
        assert result["metadata"]["algorithm"] == "tree_of_thought"

    def test_plan_result_with_minimal_metadata(self):
        """Test PlanResult with minimal metadata."""
        result = PlanResult(
            problem="Simple problem",
            selected_solution="Simple solution",
            score=60.0,
            metadata={},
        )

        assert result["problem"] == "Simple problem"
        assert result["selected_solution"] == "Simple solution"
        assert result["score"] == 60.0


class TestTypeImports:
    """Tests for importing types from plangen package."""

    def test_import_from_plangen(self):
        """Test that types can be imported from main package."""
        from plangen import (AlgorithmResult, PlanResult, SolveResult,
                             VerificationResult)

        # Verify all types are available
        assert AlgorithmResult is not None
        assert PlanResult is not None
        assert SolveResult is not None
        assert VerificationResult is not None

    def test_types_in_all(self):
        """Test that types are exported in __all__."""
        import plangen

        assert "AlgorithmResult" in plangen.__all__
        assert "PlanResult" in plangen.__all__
        assert "SolveResult" in plangen.__all__
        assert "VerificationResult" in plangen.__all__
