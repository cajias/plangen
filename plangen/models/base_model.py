"""Base model interface for PlanGEN."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


class BaseModelInterface(ABC):
    """Base class for all model interfaces."""

    @abstractmethod
    def generate(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text from the model.

        Args:
            prompt: The prompt to send to the model
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated text from the model
        """

    @abstractmethod
    def batch_generate(
        self: Self,
        prompts: list[str],
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> list[str]:
        """Generate multiple responses from the model.

        Args:
            prompts: List of prompts to send to the model
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            List of generated texts from the model
        """
