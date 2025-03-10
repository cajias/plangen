"""
AWS Bedrock model interface
"""

import json
from typing import Any, Dict, List, Optional

import boto3

from .base_model import BaseModelInterface


class BedrockModelInterface(BaseModelInterface):
    """Interface for AWS Bedrock models."""

    def __init__(
        self,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        region: Optional[str] = None,
    ):
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

    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
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
        elif "amazon" in self.model_id:
            return self._generate_amazon(prompt, system_message)
        else:
            raise ValueError(f"Unsupported model ID: {self.model_id}")

    def batch_generate(
        self, prompts: List[str], system_message: Optional[str] = None
    ) -> List[str]:
        """Generate text for multiple prompts.

        Args:
            prompts: List of input prompts
            system_message: Optional system message

        Returns:
            List of generated texts
        """
        return [self.generate(prompt, system_message) for prompt in prompts]

    def _generate_anthropic(
        self, prompt: str, system_message: Optional[str] = None
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
        self, prompt: str, system_message: Optional[str] = None
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
