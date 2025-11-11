"""Factory for creating domain-specific verifiers."""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

from .strategies.math_verifier import MathVerifier


if TYPE_CHECKING:
    from .base_verifier import BaseVerifier


class VerifierFactory:
    """Factory for creating and managing domain-specific verifiers.

    This factory maintains a registry of verifiers and selects the appropriate
    verifier for a given problem based on domain detection.
    """

    def __init__(self: Self) -> None:
        """Initialize the verifier factory."""
        # Register available verifiers
        self._verifiers: list[BaseVerifier] = [
            MathVerifier(),
            # Add more verifiers here as they are implemented
        ]

    def get_verifier(self: Self, problem_statement: str) -> BaseVerifier:
        """Get the appropriate verifier for a given problem.

        Args:
            problem_statement: The problem to analyze

        Returns:
            The most appropriate verifier for the problem

        Raises:
            ValueError: If no suitable verifier is found
        """
        # Try each registered verifier
        for verifier in self._verifiers:
            if verifier.is_applicable(problem_statement):
                return verifier

        msg = (
            "No suitable verifier found for the given problem. "
            "The problem domain may not be supported yet."
        )
        raise ValueError(
            msg,
        )

    def register_verifier(self: Self, verifier: BaseVerifier) -> None:
        """Register a new verifier.

        Args:
            verifier: The verifier to register
        """
        self._verifiers.append(verifier)

    def get_supported_domains(self: Self) -> list[str]:
        """Get a list of supported problem domains.

        Returns:
            List of domain names that can be verified
        """
        return [type(v).__name__.replace("Verifier", "") for v in self._verifiers]
