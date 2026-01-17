"""Example demonstrating streaming support in PlanGEN.

This example shows how to use the solve_stream() method to get real-time updates
as PlanGEN processes a problem through its workflow stages.
"""

import os
import sys
from typing import Any

# Add parent directory to path for local development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from plangen.api import PlanGen


def print_streaming_update(update: dict[str, Any]) -> None:
    """Print a streaming update in a formatted way.

    Args:
        update: Streaming update dictionary
    """
    step = update["step"]
    status = update["status"]

    if status == "in_progress":
        print(f"\n⏳ {step}: Starting...")
    elif status == "complete":
        print(f"✓ {step}: Complete")
        # Print relevant data based on step
        if step == "extract_constraints" and "constraints" in update.get("data", {}):
            constraints = update["data"]["constraints"]
            print(f"   Constraints extracted ({len(constraints)} chars)")
            print(f"   Preview: {constraints[:100]}...")
        elif step == "generate_solutions" and "solutions" in update.get("data", {}):
            solutions = update["data"]["solutions"]
            print(f"   Generated {len(solutions)} solutions")
        elif step == "verify_solutions" and "verification_results" in update.get(
            "data", {}
        ):
            results = update["data"]["verification_results"]
            print(f"   Verified {len(results)} solutions")
        elif step == "select_solution" and "selected_solution" in update.get(
            "data", {}
        ):
            selected = update["data"]["selected_solution"]
            score = update["data"].get("score", "N/A")
            print(f"   Selected best solution (score: {score})")
    elif status == "error":
        print(f"✗ {step}: Error occurred")
        print(f"   Error: {update.get('error', 'Unknown error')}")


def main() -> None:
    """Run the streaming example."""
    # Define a scheduling problem
    problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    print("=" * 80)
    print("PlanGEN Streaming Example")
    print("=" * 80)
    print("\nProblem:")
    print(problem)
    print("\n" + "=" * 80)
    print("Processing with streaming updates:")
    print("=" * 80)

    # Note: This example requires an OpenAI API key to run
    # Set OPENAI_API_KEY environment variable or pass api_key parameter
    try:
        # Create PlanGen instance
        plangen = PlanGen.create(model="gpt-4o")

        # Process with streaming
        final_data = None
        for update in plangen.solve_stream(problem):
            print_streaming_update(update)
            if update["status"] == "complete" and update["step"] == "select_solution":
                final_data = update["data"]

        # Print final result
        if final_data:
            print("\n" + "=" * 80)
            print("Final Result:")
            print("=" * 80)
            selected = final_data["selected_solution"]
            if selected:
                print(f"\nSelected Solution:")
                print(selected.get("selected_solution", "N/A"))
                print(f"\nScore: {final_data.get('score', 'N/A')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(
            "\nNote: This example requires an OpenAI API key."
            " Set the OPENAI_API_KEY environment variable."
        )


def example_with_progress_tracking() -> None:
    """Example showing how to track progress with a progress bar or similar."""
    print("\n" + "=" * 80)
    print("Example: Progress Tracking")
    print("=" * 80)

    problem = "Example problem for progress tracking"

    # Define expected steps
    steps = [
        "extract_constraints",
        "generate_solutions",
        "verify_solutions",
        "select_solution",
    ]
    step_progress = {step: "pending" for step in steps}

    try:
        plangen = PlanGen.create(model="gpt-4o")

        for update in plangen.solve_stream(problem):
            step = update["step"]
            status = update["status"]

            if step in step_progress:
                step_progress[step] = status

                # Print progress
                completed = sum(1 for s in step_progress.values() if s == "complete")
                total = len(steps)
                percentage = (completed / total) * 100

                print(f"\rProgress: {percentage:.0f}% [{completed}/{total}]", end="")

                if status == "error":
                    print(f"\n✗ Error in {step}: {update.get('error')}")
                    break

        print()  # New line after progress

    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_collecting_intermediate_results() -> None:
    """Example showing how to collect intermediate results for analysis."""
    print("\n" + "=" * 80)
    print("Example: Collecting Intermediate Results")
    print("=" * 80)

    problem = "Example problem"

    try:
        plangen = PlanGen.create(model="gpt-4o")

        # Collect all intermediate results
        results = {
            "constraints": None,
            "solutions": [],
            "verification_results": [],
            "selected_solution": None,
        }

        for update in plangen.solve_stream(problem):
            if update["status"] == "complete":
                data = update.get("data", {})

                if "constraints" in data:
                    results["constraints"] = data["constraints"]
                if "solutions" in data:
                    results["solutions"] = data["solutions"]
                if "verification_results" in data:
                    results["verification_results"] = data["verification_results"]
                if "selected_solution" in data:
                    results["selected_solution"] = data["selected_solution"]

        # Now you can analyze all intermediate results
        print(f"Collected constraints: {results['constraints'] is not None}")
        print(f"Collected {len(results['solutions'])} solutions")
        print(
            f"Collected {len(results['verification_results'])} verification results"
        )
        print(f"Final solution selected: {results['selected_solution'] is not None}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Run the main example
    main()

    # Uncomment to run additional examples:
    # example_with_progress_tracking()
    # example_collecting_intermediate_results()
