"""
Example usage of the new PlanGEN public API.

This file demonstrates how to use the new simplified API to solve planning problems.
"""

from plangen import Algorithm, PlanGen, Verifiers, Visualization


def basic_usage_example():
    """Basic usage example with default settings."""
    # Create a plangen instance with default settings (uses GPT-4o)
    plangen = PlanGen.create()

    # Define a simple problem
    problem = (
        "Design an algorithm to find the kth largest element in an unsorted array."
    )

    # Solve the problem using the default workflow
    result = plangen.solve(problem)

    # Print the results
    print("Problem:", problem)
    print("\nExtracted Constraints:", result["constraints"])
    print("\nSelected Solution:", result["selected_solution"]["selected_solution"])
    print("\nVerification Score:", result["selected_solution"]["score"])

    return result


def algorithm_selection_example():
    """Example of using a specific algorithm."""
    # Create a plangen instance with OpenAI
    plangen = PlanGen.with_openai(model_name="gpt-4")

    # Define a problem
    problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Create a calendar verifier
    calendar_verifier = Verifiers.calendar()

    # Solve using the Best of N algorithm with the calendar verifier
    result = plangen.solve(
        problem,
        algorithm="best_of_n",
        verifier=calendar_verifier,
        n_plans=3,
        sampling_strategy="diverse",
    )

    # Print the results
    print("Problem:", problem)
    print("\nBest solution:", result["selected_solution"])
    print("\nScore:", result["score"])

    return result


def direct_api_example():
    """Example of using the API components directly."""
    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a problem
    problem = (
        "Create a plan for organizing a conference with 100 attendees over 2 days."
    )

    # Extract constraints
    constraints = plangen.extract_constraints(problem)
    print("Extracted constraints:")
    for i, constraint in enumerate(constraints):
        print(f"{i+1}. {constraint}")

    # Generate a plan based on these constraints
    plan = plangen.generate_plan(problem, constraints)
    print("\nGenerated plan:")
    print(plan)

    # Verify the plan
    feedback, score = plangen.verify_plan(problem, plan, constraints)
    print(f"\nVerification score: {score}")
    print(f"Feedback: {feedback}")

    return {
        "problem": problem,
        "constraints": constraints,
        "plan": plan,
        "score": score,
    }


def visualization_example(result):
    """Example of using the visualization tools."""
    # Generate a visualization of the result
    vis_path = Visualization.create_graph(
        result,
        output_format="png",
        output_path="plan_visualization.png",
    )

    print(f"\nVisualization saved to: {vis_path}")


def main():
    """Run all examples."""
    print("=== Basic Usage Example ===")
    basic_result = basic_usage_example()
    print("\n\n=== Algorithm Selection Example ===")
    algorithm_result = algorithm_selection_example()
    print("\n\n=== Direct API Example ===")
    direct_result = direct_api_example()
    print("\n\n=== Visualization Example ===")
    visualization_example(algorithm_result)


if __name__ == "__main__":
    main()
