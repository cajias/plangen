"""
Intent test for PlanGEN using both Bedrock and Claude 3.5 models
"""

import json
import os

from dotenv import load_dotenv

from plangen import PlanGEN
from plangen.models import BedrockModelInterface, OpenAIModelInterface
from plangen.prompts import PromptManager

# Load environment variables from .env file
load_dotenv()


def run_test_with_model(model, problem_statement, model_name):
    """Run a test with a specific model."""
    print(f"\n=== Testing with {model_name} ===")

    # Initialize prompt manager
    prompt_manager = PromptManager()

    # Initialize PlanGEN
    plangen = PlanGEN(
        model=model,
        prompt_manager=prompt_manager,
        num_solutions=3,
    )

    print(f"Problem: {problem_statement}")
    print("\nSolving problem...")

    try:
        # Solve the problem
        result = plangen.solve(problem_statement)

        # Print the results
        print("\n=== Extracted Constraints ===")
        if "constraints" in result:
            print(result["constraints"])
        else:
            print("No constraints found in result")
            print(f"Result keys: {list(result.keys())}")

        print("\n=== Selected Solution ===")
        if "selected_solution" in result and isinstance(
            result["selected_solution"], dict
        ):
            if "selected_solution" in result["selected_solution"]:
                print(result["selected_solution"]["selected_solution"])
            else:
                print(
                    f"Selected solution keys: {list(result['selected_solution'].keys())}"
                )
        else:
            print("No selected solution found in result")

        print("\n=== Selection Reasoning ===")
        if "selected_solution" in result and isinstance(
            result["selected_solution"], dict
        ):
            if "selection_reasoning" in result["selected_solution"]:
                print(result["selected_solution"]["selection_reasoning"])
            else:
                print("No selection reasoning found")
        else:
            print("No selected solution found in result")

        # Save the results to a file
        output_file = f"plangen_results_{model_name.lower().replace(' ', '_')}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

        print(f"\nResults saved to {output_file}")

        return result
    except Exception as e:
        print(f"\nError running test with {model_name}: {str(e)}")
        return None


def main():
    """Run intent tests with different models on a complex planning problem."""

    # Example from the paper: Calendar scheduling problem
    calendar_problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Test with OpenAI model (Claude 3.5 Sonnet)
    if os.environ.get("OPENAI_API_KEY"):
        openai_model = OpenAIModelInterface(
            model_name="claude-3-5-sonnet-20240620",
            temperature=0.7,
            max_tokens=1024,
        )
        run_test_with_model(openai_model, calendar_problem, "Claude 3.5 Sonnet")
    else:
        print("Skipping Claude 3.5 test - OPENAI_API_KEY not set")

    # Test with AWS Bedrock model
    if os.environ.get("AWS_PROFILE") or os.environ.get("AWS_ACCESS_KEY_ID"):
        bedrock_model = BedrockModelInterface(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            temperature=0.7,
            max_tokens=1024,
        )
        run_test_with_model(bedrock_model, calendar_problem, "AWS Bedrock Claude")
    else:
        print("Skipping AWS Bedrock test - AWS credentials not set")


if __name__ == "__main__":
    main()
