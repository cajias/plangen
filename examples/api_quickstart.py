"""
Quick start example for PlanGEN using the new public API
"""

import json
from dotenv import load_dotenv

from plangen import PlanGen

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a quick start example of PlanGEN with the new public API."""
    # Create a PlanGen instance
    # This will automatically use OpenAI if OPENAI_API_KEY is set,
    # or try to fall back to AWS Bedrock if AWS credentials are available
    plangen = PlanGen.create()

    # Define a problem
    problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    print(f"Problem: {problem.strip()}")
    print("\nSolving problem...")

    # Solve the problem
    result = plangen.solve(problem)

    # Print the extracted constraints
    print("\n=== Extracted Constraints ===")
    constraints = result.get("constraints", [])
    for i, constraint in enumerate(constraints, 1):
        print(f"{i}. {constraint}")

    # Print the selected solution
    print("\n=== Selected Solution ===")
    selected_solution = result.get("selected_solution", {})
    if isinstance(selected_solution, dict):
        print(selected_solution.get("selected_solution", "No solution found"))
    else:
        print(selected_solution)

    # Save the results to a file
    with open("api_quickstart_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\nResults saved to api_quickstart_results.json")


if __name__ == "__main__":
    main()