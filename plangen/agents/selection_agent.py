"""Selection agent for PlanGEN."""

from typing import Any, Self

from pydantic import BaseModel, Field

from plangen.models import BaseModelInterface
from plangen.prompts import PromptManager


class Solution(BaseModel):
    """Model for a solution and its verification."""

    text: str = Field(..., description="The solution text")
    verification: str = Field(..., description="Verification results for the solution")


class SelectionAgent:
    """Agent for selecting the best solution based on verification results."""

    def __init__(
        self: Self,
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ) -> None:
        """Initialize the selection agent.

        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager

    def select_best_solution(
        self: Self, solutions: list[str], verification_results: list[str],
    ) -> dict[str, Any]:
        """Select the best solution based on verification results.

        Args:
            solutions: List of solutions
            verification_results: List of verification results

        Returns:
            Dictionary with the best solution and selection reasoning
        """
        system_message = self.prompt_manager.get_system_message("selection")

        # Prepare solution objects for the prompt
        solution_objects = [
            Solution(text=solution, verification=verification)
            for solution, verification in zip(solutions, verification_results)
        ]

        prompt = self.prompt_manager.get_prompt(
            "solution_selection", solutions=solution_objects,
        )

        selection_reasoning = self.model.generate(prompt, system_message=system_message)

        # Extract the selected solution index (assuming it's mentioned in the reasoning)
        # This is a simple heuristic; in practice, you might want a more robust approach
        selected_index = 0
        for i, _solution in enumerate(solutions):
            if (
                f"Solution {i+1}" in selection_reasoning
                and "best" in selection_reasoning.lower()
            ):
                selected_index = i
                break

        return {
            "selected_solution": solutions[selected_index],
            "selection_reasoning": selection_reasoning,
            "selected_index": selected_index,
        }
