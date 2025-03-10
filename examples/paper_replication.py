"""
Replication of experiments from the PlanGEN paper
"""

import json
import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv

from plangen import PlanGEN
from plangen.models import BedrockModelInterface, OpenAIModelInterface
from plangen.prompts import PromptManager

# Load environment variables from .env file
load_dotenv()

# Test problems from the paper (or similar ones)
TEST_PROBLEMS = [
    {
        "name": "Maximum Subarray",
        "description": """
        Design a function to find the maximum sum of a contiguous subarray within an array of integers.
        For example, given the array [-2, 1, -3, 4, -1, 2, 1, -5, 4], the contiguous subarray with the
        largest sum is [4, -1, 2, 1], with a sum of 6.
        """,
    },
    {
        "name": "Binary Search Tree Validation",
        "description": """
        Write a function to determine if a given binary tree is a valid binary search tree (BST).
        A valid BST is defined as follows:
        - The left subtree of a node contains only nodes with keys less than the node's key.
        - The right subtree of a node contains only nodes with keys greater than the node's key.
        - Both the left and right subtrees must also be binary search trees.
        """,
    },
    {
        "name": "LRU Cache",
        "description": """
        Design and implement a data structure for Least Recently Used (LRU) cache.
        It should support the following operations: get and put.
        - get(key): Get the value of the key if the key exists in the cache, otherwise return -1.
        - put(key, value): Set or insert the value if the key is not already present. When the cache reaches its capacity,
          it should invalidate the least recently used item before inserting a new item.
        The cache should be initialized with a positive capacity.
        """,
    },
]


def run_experiment(
    problems: List[Dict[str, str]], model_type: str = "openai"
) -> Dict[str, Any]:
    """Run the experiment on the given problems.

    Args:
        problems: List of problem dictionaries with name and description
        model_type: Type of model to use ("openai" or "bedrock")

    Returns:
        Dictionary with experiment results
    """
    # Choose model interface based on model_type
    if model_type == "openai" and os.environ.get("OPENAI_API_KEY"):
        model = OpenAIModelInterface(
            model_name="gpt-4o",
            temperature=0.7,
            max_tokens=1024,
        )
        print(f"Using OpenAI model: gpt-4o")
    elif model_type == "bedrock" and (
        os.environ.get("AWS_PROFILE") or os.environ.get("AWS_ACCESS_KEY_ID")
    ):
        model = BedrockModelInterface(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            temperature=0.7,
            max_tokens=1024,
        )
        print(f"Using AWS Bedrock model: claude-3-sonnet")
    else:
        raise ValueError(
            f"Cannot use {model_type} model. Please set appropriate API credentials."
        )

    # Initialize prompt manager
    prompt_manager = PromptManager()

    # Initialize PlanGEN
    plangen = PlanGEN(
        model=model,
        prompt_manager=prompt_manager,
        num_solutions=3,
    )

    # Run experiments
    results = {
        "model_type": model_type,
        "problems": [],
    }

    for problem in problems:
        print(f"\n\n=== Solving: {problem['name']} ===")
        print(f"Problem: {problem['description']}")

        start_time = time.time()
        result = plangen.solve(problem["description"])
        end_time = time.time()

        problem_result = {
            "name": problem["name"],
            "description": problem["description"],
            "constraints": result["constraints"],
            "solutions": result["solutions"],
            "verification_results": result["verification_results"],
            "selected_solution": result["selected_solution"],
            "time_taken": end_time - start_time,
        }

        results["problems"].append(problem_result)

        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(
            f"Selected solution index: {result['selected_solution']['selected_index']}"
        )

    return results


def main():
    """Run the paper replication experiment."""
    # Run experiment with OpenAI model
    try:
        openai_results = run_experiment(TEST_PROBLEMS, model_type="openai")
        with open("plangen_openai_results.json", "w") as f:
            json.dump(openai_results, f, indent=2)
        print("\nOpenAI results saved to plangen_openai_results.json")
    except ValueError as e:
        print(f"Skipping OpenAI experiment: {e}")

    # Run experiment with Bedrock model
    try:
        bedrock_results = run_experiment(TEST_PROBLEMS, model_type="bedrock")
        with open("plangen_bedrock_results.json", "w") as f:
            json.dump(bedrock_results, f, indent=2)
        print("\nBedrock results saved to plangen_bedrock_results.json")
    except ValueError as e:
        print(f"Skipping Bedrock experiment: {e}")


if __name__ == "__main__":
    main()
