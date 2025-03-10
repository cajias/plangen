"""
Simple example of using PlanGEN
"""

import json
import os

from dotenv import load_dotenv

from plangen import PlanGEN
from plangen.models import BedrockModelInterface, OpenAIModelInterface
from plangen.prompts import PromptManager

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a simple example of PlanGEN."""
    # Choose model interface based on available credentials
    if os.environ.get("OPENAI_API_KEY"):
        model = OpenAIModelInterface(
            model_name="gpt-4o",
            temperature=0.7,
            max_tokens=1024,
        )
        print("Using OpenAI model")
    elif os.environ.get("AWS_PROFILE") or os.environ.get("AWS_ACCESS_KEY_ID"):
        model = BedrockModelInterface(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            temperature=0.7,
            max_tokens=1024,
        )
        print("Using AWS Bedrock model")
    else:
        raise ValueError(
            "No API credentials found. Please set OPENAI_API_KEY or AWS credentials."
        )

    # Initialize prompt manager
    prompt_manager = PromptManager()

    # Initialize PlanGEN
    plangen = PlanGEN(
        model=model,
        prompt_manager=prompt_manager,
        num_solutions=3,
    )

    # Define a problem
    problem = """
    Design an algorithm to find the kth largest element in an unsorted array.
    For example, given [3, 2, 1, 5, 6, 4] and k = 2, the output should be 5.
    """

    print(f"Problem: {problem}")
    print("\nSolving problem...")

    # Solve the problem
    result = plangen.solve(problem)

    # Print the results
    print("\n=== Extracted Constraints ===")
    print(result["constraints"])

    print("\n=== Selected Solution ===")
    print(result["selected_solution"]["selected_solution"])

    print("\n=== Selection Reasoning ===")
    print(result["selected_solution"]["selection_reasoning"])

    # Save the results to a file
    with open("plangen_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\nResults saved to plangen_results.json")


if __name__ == "__main__":
    main()
