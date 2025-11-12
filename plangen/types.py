"""Type definitions for the PlanGEN framework.

This module defines TypedDict classes for structured return values and data structures
used throughout the framework. These types improve type safety and IDE support.
"""

from __future__ import annotations

from typing import Any, TypedDict


class VerificationResult(TypedDict):
    """Result from verifying a solution.

    Attributes:
        is_valid: Whether the solution is valid
        score: Numerical score (0-100) indicating solution quality
        reason: Explanation of the verification result
        feedback: Optional detailed feedback
    """

    is_valid: bool
    score: float
    reason: str
    feedback: str | None


class SolveResult(TypedDict):
    """Result from solving a problem with PlanGEN.

    Attributes:
        problem: The original problem statement
        constraints: Extracted constraints (if any)
        solutions: Generated candidate solutions (if any)
        verification_results: Verification results for each solution (if any)
        selected_solution: The selected best solution (if any)
        score: Score of the selected solution (if available)
        metadata: Additional metadata from the solving process
        error: Error message if the solving process failed (if any)
    """

    problem: str
    constraints: str | None
    solutions: list[str] | None
    verification_results: list[str] | None
    selected_solution: dict[str, Any] | None
    score: float | None
    metadata: dict[str, Any]
    error: str | None


class AlgorithmResult(TypedDict):
    """Result from running an algorithm.

    Attributes:
        best_plan: The best plan/solution found
        score: Score of the best plan
        metadata: Additional metadata from the algorithm execution
    """

    best_plan: str
    score: float
    metadata: dict[str, Any]


class PlanResult(TypedDict):
    """Result from the simplified solve API.

    Attributes:
        problem: The original problem statement
        selected_solution: The selected best solution
        score: Score of the selected solution
        metadata: Additional metadata from the solving process
    """

    problem: str
    selected_solution: str
    score: float
    metadata: dict[str, Any]
