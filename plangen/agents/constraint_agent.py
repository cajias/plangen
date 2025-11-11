"""Constraint agent for PlanGEN."""
from __future__ import annotations

from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from plangen.models import BaseModelInterface
    from plangen.prompts import PromptManager


class ConstraintAgent:
    """Agent for extracting constraints from problem statements."""

    def __init__(
        self: Self,
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ) -> None:
        """Initialize the constraint agent.

        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager

    def extract_constraints(self: Self, problem: str) -> str:
        """Extract constraints from a problem statement.

        Args:
            problem: Problem statement

        Returns:
            Extracted constraints as a string
        """
        # Get the system message and prompt template
        system_message = self.prompt_manager.get_system_message("constraint")
        prompt = self.prompt_manager.get_prompt(
            "constraint_extraction", problem=problem,
        )

        # Generate constraints using the model
        return self.model.generate(prompt, system_message=system_message)

