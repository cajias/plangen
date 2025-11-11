"""LLM Interface for PlanGEN."""
from __future__ import annotations

import os
from typing import Self


class LLMInterface:
    """Interface for interacting with LLMs."""

    def __init__(
        self: Self,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        api_key: str | None = None,
    ) -> None:
        """Initialize the LLM interface.

        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            api_key: API key for the LLM provider
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set up the client based on the model name
        if "gpt" in model_name.lower():
            self._setup_openai(api_key)
        elif "claude" in model_name.lower():
            self._setup_anthropic(api_key)
        elif "gemini" in model_name.lower():
            self._setup_google(api_key)
        else:
            msg = f"Unsupported model: {model_name}"
            raise ValueError(msg)

    def _setup_openai(self: Self, api_key: str | None = None) -> None:
        """Set up the OpenAI client.

        Args:
            api_key: OpenAI API key
        """
        try:
            import openai

            self.client = openai.OpenAI(
                api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            )
            self.provider = "openai"
        except ImportError:
            msg = "OpenAI package not installed. Install it with 'pip install openai'."
            raise ImportError(msg) from None

    def _setup_anthropic(self: Self, api_key: str | None = None) -> None:
        """Set up the Anthropic client.

        Args:
            api_key: Anthropic API key
        """
        try:
            import anthropic

            self.client = anthropic.Anthropic(
                api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
            )
            self.provider = "anthropic"
        except ImportError:
            msg = "Anthropic package not installed. Install it with 'pip install anthropic'."
            raise ImportError(msg) from None

    def _setup_google(self: Self, api_key: str | None = None) -> None:
        """Set up the Google client.

        Args:
            api_key: Google API key
        """
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
            self.client = genai
            self.provider = "google"
        except ImportError:
            msg = "Google Generative AI package not installed. Install it with 'pip install google-generativeai'."
            raise ImportError(msg) from None

    def generate(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using the LLM.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        if self.provider == "openai":
            return self._generate_openai(prompt, system_message, temp, tokens)
        if self.provider == "anthropic":
            return self._generate_anthropic(prompt, system_message, temp, tokens)
        if self.provider == "google":
            return self._generate_google(prompt, system_message, temp, tokens)
        msg = f"Unsupported provider: {self.provider}"
        raise ValueError(msg) from None

    def _generate_openai(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def _generate_anthropic(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using Anthropic.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        response = self.client.messages.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.content[0].text

    def _generate_google(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using Google.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if system_message:
            prompt = f"{system_message}\n\n{prompt}"

        model = self.client.GenerativeModel(self.model_name)
        response = model.generate_content(prompt, generation_config=generation_config)

        return response.text

    def batch_generate(
        self: Self,
        prompts: list[str],
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> list[str]:
        """Generate text for multiple prompts.

        Args:
            prompts: List of input prompts
            system_message: Optional system message
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            List of generated texts
        """
        return [
            self.generate(prompt, system_message, temperature, max_tokens)
            for prompt in prompts
        ]
