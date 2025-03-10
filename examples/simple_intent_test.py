"""
Simplified intent test for PlanGEN using OpenAI model
"""

import json
import os

from dotenv import load_dotenv

from plangen import PlanGEN
from plangen.models import OpenAIModelInterface
from plangen.prompts import PromptManager

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a simple intent test with the calendar scheduling problem."""

    # Calendar scheduling problem from the paper
    calendar_problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Initialize OpenAI model with gpt-4o
    model = OpenAIModelInterface(
        model_name="gpt-4o",
        temperature=0.7,
        max_tokens=1024,
    )

    # Initialize prompt manager
    prompt_manager = PromptManager()

    # Initialize PlanGEN
    plangen = PlanGEN(
        model=model,
        prompt_manager=prompt_manager,
        num_solutions=3,
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving problem...")

    try:
        # Solve the problem
        result = plangen.solve(calendar_problem)

        # Print the results
        print("\n=== Extracted Constraints ===")
        print(result.get("constraints", "No constraints found"))

        # Print the selected solution if available
        if "selected_solution" in result and isinstance(
            result["selected_solution"], dict
        ):
            print("\n=== Selected Solution ===")
            print(
                result["selected_solution"].get(
                    "selected_solution", "No solution details found"
                )
            )
        else:
            print("\nNo selected solution found in result")
            print(f"Result keys: {list(result.keys())}")

        # Save the results to a file
        with open("calendar_scheduling_result.json", "w") as f:
            json.dump(result, f, indent=2)

        print("\nResults saved to calendar_scheduling_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")


if __name__ == "__main__":
    main()
