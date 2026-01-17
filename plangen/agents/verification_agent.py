"""Verification agent for PlanGEN."""


from typing_extensions import Self

from plangen.models import BaseModelInterface
from plangen.prompts import PromptManager


class VerificationAgent:
    """Agent for verifying plans and solutions."""

    def __init__(
        self: Self,
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ) -> None:
        """Initialize the verification agent.

        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager

    def verify_solutions(
        self: Self, solutions: list[str], constraints: str,
    ) -> list[str]:
        """Verify multiple solutions against constraints.

        Args:
            solutions: List of solutions to verify
            constraints: Extracted constraints

        Returns:
            List of verification results
        """
        # Get the system message for verification
        system_message = self.prompt_manager.get_system_message("verification")

        # Verify each solution
        verification_results = []
        for solution in solutions:
            prompt = self.prompt_manager.get_prompt(
                "solution_verification",
                solution=solution,
                constraints=constraints,
            )
            verification = self.model.generate(prompt, system_message=system_message)
            verification_results.append(verification)

        return verification_results
