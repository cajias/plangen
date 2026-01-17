"""AWS Bedrock model interface."""
from __future__ import annotations

import json
from typing import Iterator
from typing_extensions import Self

import boto3

from .base_model import BaseModelInterface


class BedrockModelInterface(BaseModelInterface):
    """Interface for AWS Bedrock models."""

    def __init__(
        self: Self,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        region: str | None = None,
    ) -> None:
        """Initialize the Bedrock model interface.

        Args:
            model_id: Bedrock model ID
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            region: AWS region (optional)
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize Bedrock client
        self.client = boto3.client("bedrock-runtime", region_name=region or "us-east-1")

    def generate(self: Self, prompt: str, system_message: str | None = None) -> str:
        """Generate text using the Bedrock model.

        Args:
            prompt: Input prompt
            system_message: Optional system message

        Returns:
            Generated text
        """
        # Format the prompt based on model type
        if "anthropic" in self.model_id:
            return self._generate_anthropic(prompt, system_message)
        if "amazon" in self.model_id:
            return self._generate_amazon(prompt, system_message)
        msg = f"Unsupported model ID: {self.model_id}"
        raise ValueError(msg)

    def batch_generate(
        self: Self, prompts: list[str], system_message: str | None = None,
    ) -> list[str]:
        """Generate text for multiple prompts.

        Args:
            prompts: List of input prompts
            system_message: Optional system message

        Returns:
            List of generated texts
        """
        return [self.generate(prompt, system_message) for prompt in prompts]

    def generate_stream(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Generate text using the Bedrock model with streaming.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            Chunks of generated text from the model
        """
        # Format the prompt based on model type
        if "anthropic" in self.model_id:
            yield from self._generate_anthropic_stream(
                prompt, system_message, temperature, max_tokens
            )
        elif "amazon" in self.model_id:
            yield from self._generate_amazon_stream(
                prompt, system_message, temperature, max_tokens
            )
        else:
            msg = f"Unsupported model ID: {self.model_id}"
            raise ValueError(msg)

    def _generate_anthropic(
        self: Self, prompt: str, system_message: str | None = None,
    ) -> str:
        """Generate text using Anthropic Claude models.

        Args:
            prompt: Input prompt
            system_message: Optional system message

        Returns:
            Generated text
        """
        # For Claude 3 in Bedrock, we need to format the prompt differently
        # If system message is provided, include it in the user message
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"

        # Format messages for Claude 3
        messages = [{"role": "user", "content": full_prompt}]

        # Prepare the request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "messages": messages,
            "temperature": self.temperature,
        }

        # Make the API call
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Parse the response
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]

    def _generate_amazon(
        self: Self, prompt: str, system_message: str | None = None,
    ) -> str:
        """Generate text using Amazon Titan models.

        Args:
            prompt: Input prompt
            system_message: Optional system message

        Returns:
            Generated text
        """
        # Combine system message and prompt for Titan models
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"

        # Prepare the request body for Titan models
        body = {
            "inputText": full_prompt,
            "textGenerationConfig": {
                "maxTokenCount": self.max_tokens,
                "temperature": self.temperature,
                "topP": 0.9,
            },
        }

        # Make the API call
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Parse the response
        response_body = json.loads(response["body"].read())
        return response_body["results"][0]["outputText"]

    def _generate_anthropic_stream(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Generate text using Anthropic Claude models with streaming.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            Chunks of generated text
        """
        # For Claude 3 in Bedrock, we need to format the prompt differently
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"

        # Format messages for Claude 3
        messages = [{"role": "user", "content": full_prompt}]

        # Prepare the request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
            "temperature": temperature or self.temperature,
        }

        # Make the streaming API call
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Process the stream
        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                if "delta" in chunk and "text" in chunk["delta"]:
                    yield chunk["delta"]["text"]

    def _generate_amazon_stream(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Generate text using Amazon Titan models with streaming.

        Args:
            prompt: Input prompt
            system_message: Optional system message
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            Chunks of generated text
        """
        # Combine system message and prompt for Titan models
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"

        # Prepare the request body for Titan models
        body = {
            "inputText": full_prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "topP": 0.9,
            },
        }

        # Make the streaming API call
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Process the stream
        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "outputText" in chunk:
                yield chunk["outputText"]
