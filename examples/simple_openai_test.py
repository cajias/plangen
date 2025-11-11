"""
Simple example using PlanGEN with OpenAI model (using modern public API).

This example demonstrates the recommended way to use PlanGEN with the new public API.
"""

import json
import os

from dotenv import load_dotenv

from plangen import PlanGen

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a simple example with the calendar scheduling problem."""

    # Calendar scheduling problem from the paper
    calendar_problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Initialize PlanGen with OpenAI using modern public API
    # Can also use PlanGen.create() to auto-detect, or PlanGen.with_bedrock() for AWS
    plangen = PlanGen.with_openai(
        model_name="gpt-4o",
        temperature=0.7,
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving problem...")

    try:
        # Solve the problem using the full workflow
        result = plangen.solve(calendar_problem)

        # Print the results
        print("\n=== Extracted Constraints ===")
        print(result.get("constraints", "No constraints found"))

        # Print solutions if available
        if "solutions" in result:
            print(f"\n=== Generated {len(result['solutions'])} Solutions ===")
            for i, solution in enumerate(result["solutions"]):
                print(f"\nSolution {i+1}:")
                print(solution[:200] + "..." if len(solution) > 200 else solution)

        # Print verification results if available
        if "verification_results" in result:
            print(f"\n=== Verification Results ===")
            for i, vr in enumerate(result["verification_results"]):
                print(f"\nVerification {i+1}:")
                print(vr[:200] + "..." if len(vr) > 200 else vr)

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

            print("\n=== Selection Reasoning ===")
            print(
                result["selected_solution"].get(
                    "selection_reasoning", "No selection reasoning found"
                )
            )

        # Print any errors
        if "error" in result:
            print("\n=== Error ===")
            print(result["error"])

        # Save the results to a file
        with open("calendar_scheduling_openai_result.json", "w") as f:
            json.dump(result, f, indent=2)

        print("\nResults saved to calendar_scheduling_openai_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")


if __name__ == "__main__":
    main()
