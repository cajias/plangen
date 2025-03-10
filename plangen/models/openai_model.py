"""
OpenAI model interface for PlanGEN
"""

import os
from typing import Any, Dict, List, Optional

import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base_model import BaseModelInterface


class OpenAIModelInterface(BaseModelInterface):
    """Interface for interacting with OpenAI models."""

    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """Initialize the OpenAI model interface.

        Args:
            model_name: Name of the model to use
            api_key: API key for OpenAI
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set as OPENAI_API_KEY environment variable"
            )

        self.client = OpenAI(api_key=self.api_key)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text from the OpenAI model.

        Args:
            prompt: The prompt to send to the model
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated text from the model
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        return response.choices[0].message.content

    def batch_generate(
        self,
        prompts: List[str],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> List[str]:
        """Generate multiple responses from the OpenAI model.

        Args:
            prompts: List of prompts to send to the model
            system_message: Optional system message to set context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            List of generated texts from the model
        """
        return [
            self.generate(
                prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for prompt in prompts
        ]
