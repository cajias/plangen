"""Solution agent for PlanGEN."""


from typing_extensions import Self

from plangen.models import BaseModelInterface
from plangen.prompts import PromptManager


class SolutionAgent:
    """Agent for generating solutions based on constraints."""

    def __init__(
        self: Self,
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ) -> None:
        """Initialize the solution agent.

        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager

    def generate_solutions(
        self: Self, problem: str, constraints: str, num_solutions: int = 3,
    ) -> list[str]:
        """Generate multiple solutions for a problem.

        Args:
            problem: Problem statement
            constraints: Extracted constraints
            num_solutions: Number of solutions to generate

        Returns:
            List of generated solutions
        """
        # Get the system message and prompt template
        # Use constraint system message as fallback if solution system message doesn't exist
        try:
            system_message = self.prompt_manager.get_system_message("solution")
        except KeyError:
            # Fallback to constraint system message if solution message doesn't exist
            system_message = self.prompt_manager.get_system_message("constraint")

        prompt_template = self.prompt_manager.get_prompt(
            "solution_generation", problem=problem, constraints=constraints,
        )

        # Generate multiple solutions
        solutions = []
        for _i in range(num_solutions):
            solution = self.model.generate(
                prompt_template, system_message=system_message,
            )
            solutions.append(solution)

        return solutions
