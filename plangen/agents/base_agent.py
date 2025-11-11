"""
Base Agent class for PlanGEN
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from plangen.utils.llm_interface import LLMInterface


class BaseAgent(ABC):
    """Base class for all PlanGEN agents."""

    def __init__(
        self,
        llm_interface: LLMInterface | None = None,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        system_message: str | None = None,
    ) -> None:
        """Initialize the base agent.

        Args:
            llm_interface: Optional LLM interface to use
            model_name: Name of the model to use if llm_interface is not provided
            temperature: Temperature for LLM generation
            system_message: System message to set context for the agent
        """
        self.llm_interface = llm_interface or LLMInterface(
            model_name=model_name,
            temperature=temperature,
        )
        self.system_message = system_message

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Run the agent.

        This method should be implemented by all subclasses.
        """

    def _generate_prompt(self, template: str, **kwargs) -> str:
        """Generate a prompt from a template.

        Args:
            template: Prompt template with placeholders
            **kwargs: Values to fill in the template

        Returns:
            Formatted prompt
        """
        return template.format(**kwargs)

    def _call_llm(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Call the LLM with the given prompt.

        Args:
            prompt: Prompt to send to the LLM
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated text from the LLM
        """
        return self.llm_interface.generate(
            prompt=prompt,
            system_message=self.system_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )
