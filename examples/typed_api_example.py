"""Example demonstrating the use of typed API results.

This example shows how to use the new TypedDict types for better type safety
and IDE autocompletion when working with PlanGEN results.
"""

from plangen import PlanGen, PlanResult, SolveResult, VerificationResult


def example_with_typed_results() -> None:
    """Example showing typed result usage."""
    # Create a PlanGen instance (mock for example)
    # plangen = PlanGen.create(model="gpt-4o")

    # The solve method now returns a typed result
    # result: SolveResult = plangen.solve("Design a sorting algorithm")

    # With TypedDict, IDEs can provide autocompletion for available keys
    # print(f"Problem: {result['problem']}")
    # print(f"Selected Solution: {result['selected_solution']}")
    # print(f"Score: {result['score']}")

    # You can also destructure the result
    # problem = result["problem"]
    # solution = result["selected_solution"]
    # score = result["score"]

    # For algorithm-specific usage, you get PlanResult
    # result: PlanResult = plangen.solve("Problem", algorithm="best_of_n", n_plans=5)
    # print(f"Algorithm metadata: {result['metadata']}")

    print("Example demonstrating typed API usage")
    print("See the docstring for usage patterns")


def example_with_verification() -> None:
    """Example showing typed verification results."""
    # With typed verification results, you get better type hints
    # plangen = PlanGen.create()
    # feedback, score = plangen.verify_plan(
    #     problem="Test problem",
    #     plan="Test plan"
    # )

    # When using a custom verifier that returns VerificationResult
    # result: VerificationResult = {
    #     "is_valid": True,
    #     "score": 85.5,
    #     "reason": "Solution meets requirements",
    #     "feedback": "Good work"
    # }

    print("Example demonstrating typed verification usage")
    print("See the docstring for usage patterns")


if __name__ == "__main__":
    example_with_typed_results()
    example_with_verification()
