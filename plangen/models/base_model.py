"""
Base model interface for PlanGEN
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseModelInterface(ABC):
    """Base class for all model interfaces."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
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
        pass

    @abstractmethod
    def batch_generate(
        self,
        prompts: List[str],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> List[str]:
        """Generate multiple responses from the model.

        Args:
            prompts: List of prompts to send to the model
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            List of generated texts from the model
        """
        pass
