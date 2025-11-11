"""
Verification agent for PlanGEN.
"""

from typing import Any, Dict, List, Optional, Tuple

from ..models import BaseModelInterface
from ..prompts import PromptManager


class VerificationAgent:
    """Agent for verifying plans and solutions."""

    def __init__(
        self,
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ):
        """Initialize the verification agent.

        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager

    def verify_solutions(
        self, solutions: List[str], constraints: str
    ) -> List[str]:
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
