"""
Example using the BestOfN algorithm with the new public API
"""

import json
from dotenv import load_dotenv

from plangen import PlanGen

# Load environment variables from .env file
load_dotenv()


def main():
    """Run an example using the BestOfN algorithm with the new public API."""
    # Create a PlanGen instance
    plangen = PlanGen.create()

    # Define a problem
    problem = """
    Design an algorithm to find the kth largest element in an unsorted array.
    For example, given [3, 2, 1, 5, 6, 4] and k = 2, the output should be 5.
    """

    print(f"Problem: {problem.strip()}")
    print("\nSolving problem using BestOfN algorithm...")

    # Solve the problem using the BestOfN algorithm
    result = plangen.solve(
        problem,
        algorithm="best_of_n",
        n_plans=3,  # Generate 3 different solutions
        sampling_strategy="diverse",  # Use diverse sampling strategy
        parallel=True  # Generate solutions in parallel
    )

    # Print the extracted constraints
    print("\n=== Extracted Constraints ===")
    constraints = result.get("constraints", [])
    for i, constraint in enumerate(constraints, 1):
        print(f"{i}. {constraint}")

    # Print the selected solution
    print("\n=== Selected Solution ===")
    print(result.get("selected_solution", "No solution found"))

    # Print metadata if available
    if "metadata" in result:
        print("\n=== Metadata ===")
        print(f"Number of plans generated: {len(result['metadata'].get('plans', []))}")
        print(f"Best score: {result.get('score', 'N/A')}")

    # Save the results to a file
    with open("best_of_n_results.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\nResults saved to best_of_n_results.json")


if __name__ == "__main__":
    main()