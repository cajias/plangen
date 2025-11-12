"""Base verifier interface for domain-agnostic verification."""

from abc import ABC, abstractmethod
from typing import Any, Self

from plangen.types import VerificationResult


class BaseVerifier(ABC):
    """Abstract base class for solution verifiers.

    This interface defines the contract that all domain-specific verifiers must implement.
    It allows the core algorithm to remain domain-agnostic while enabling specialized
    verification for different problem domains.
    """

    @abstractmethod
    def verify_solution(
        self: Self,
        problem_statement: str,
        solution: str,
        constraints: list[str],
    ) -> dict[str, Any] | VerificationResult:
        """Verify if a solution satisfies the constraints for a given problem.

        Args:
            problem_statement: The original problem statement
            solution: The proposed solution
            constraints: List of constraints the solution must satisfy

        Returns:
            VerificationResult or dict containing verification results with at least:
            - 'is_valid': Boolean indicating if solution is valid
            - 'score': Numerical score (0-100) indicating solution quality
            - 'reason': Explanation of verification result
            - 'feedback': Optional detailed feedback
        """

    @abstractmethod
    def is_applicable(self: Self, problem_statement: str) -> bool:
        """Check if this verifier is applicable to the given problem.

        Args:
            problem_statement: The problem statement to check

        Returns:
            True if this verifier can handle the problem, False otherwise
        """

    @abstractmethod
    def extract_domain_constraints(
        self: Self,
        problem_statement: str,
        general_constraints: list[str],
    ) -> list[str]:
        """Extract domain-specific constraints from the problem statement.

        Args:
            problem_statement: The problem statement
            general_constraints: General constraints already extracted

        Returns:
            List of domain-specific constraints
        """
