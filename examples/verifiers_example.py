"""
Examples of using different verifiers with the PlanGEN public API.

This file demonstrates how to use different verifiers and create custom verifiers
for the PlanGEN framework through the new API.
"""

from typing import List, Tuple

from plangen import PlanGen, Verifiers


def calendar_verifier_example():
    """Example of using the calendar scheduling verifier."""
    print("=== Calendar Verifier Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a calendar scheduling problem
    problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Create a calendar verifier
    calendar_verifier = Verifiers.calendar()

    # Extract constraints from the problem
    constraints = plangen.extract_constraints(problem)
    print("Extracted constraints:")
    for i, constraint in enumerate(constraints):
        print(f"{i+1}. {constraint}")

    # Generate a plan
    plan = plangen.generate_plan(problem, constraints)
    print("\nGenerated plan:")
    print(plan)

    # Verify the plan with the calendar verifier
    feedback, score = plangen.verify_plan(
        problem, plan, constraints, verifier=calendar_verifier
    )

    print(f"\nVerification score: {score}")
    print(f"Feedback: {feedback}")

    return {"problem": problem, "plan": plan, "score": score, "feedback": feedback}


def math_verifier_example():
    """Example of using the math problem verifier."""
    print("=== Math Verifier Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a math problem
    problem = "Solve the equation: 3x + 7 = 22"

    # Create a math verifier
    math_verifier = Verifiers.math()

    # Extract constraints from the problem
    constraints = plangen.extract_constraints(problem)
    print("Extracted constraints:")
    for i, constraint in enumerate(constraints):
        print(f"{i+1}. {constraint}")

    # Generate a plan
    plan = plangen.generate_plan(problem, constraints)
    print("\nGenerated plan:")
    print(plan)

    # Verify the plan with the math verifier
    feedback, score = plangen.verify_plan(
        problem, plan, constraints, verifier=math_verifier
    )

    print(f"\nVerification score: {score}")
    print(f"Feedback: {feedback}")

    return {"problem": problem, "plan": plan, "score": score, "feedback": feedback}


def custom_verifier_example():
    """Example of using a custom verifier."""
    print("=== Custom Verifier Example ===")

    # Define a custom verification function
    def verify_recipe(
        problem: str, constraints: List[str], plan: str
    ) -> Tuple[str, float]:
        """Custom verifier for a recipe plan."""
        # Check if the plan includes all required sections
        required_sections = ["ingredients", "steps", "time"]
        score = 0.0
        feedback = []

        for section in required_sections:
            if section.lower() in plan.lower():
                score += 0.3
                feedback.append(f"✓ Plan includes {section} section")
            else:
                feedback.append(f"✗ Plan is missing {section} section")

        # Check for specific constraints
        if "vegetarian" in " ".join(constraints).lower():
            meat_ingredients = ["meat", "beef", "chicken", "pork", "fish"]
            has_meat = any(meat in plan.lower() for meat in meat_ingredients)

            if has_meat:
                feedback.append("✗ Recipe contains meat but should be vegetarian")
            else:
                score += 0.1
                feedback.append("✓ Recipe is vegetarian as required")

        # Cap the score at 1.0
        score = min(score, 1.0)

        return "\n".join(feedback), score

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a recipe problem
    problem = (
        "Create a vegetarian pasta recipe that can be prepared in under 30 minutes."
    )

    # Create a custom verifier
    recipe_verifier = Verifiers.custom(verify_recipe)

    # Extract constraints from the problem
    constraints = plangen.extract_constraints(problem)
    print("Extracted constraints:")
    for i, constraint in enumerate(constraints):
        print(f"{i+1}. {constraint}")

    # Generate a plan
    plan = plangen.generate_plan(problem, constraints)
    print("\nGenerated plan:")
    print(plan)

    # Verify the plan with the custom verifier
    feedback, score = plangen.verify_plan(
        problem, plan, constraints, verifier=recipe_verifier
    )

    print(f"\nVerification score: {score}")
    print(f"Feedback: {feedback}")

    return {"problem": problem, "plan": plan, "score": score, "feedback": feedback}


def solve_with_verifier_example():
    """Example of using a verifier with the solve method."""
    print("=== Solve with Verifier Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a recipe problem
    problem = (
        "Create a vegetarian pasta recipe that can be prepared in under 30 minutes."
    )

    # Define a custom verification function
    def verify_recipe(
        problem: str, constraints: List[str], plan: str
    ) -> Tuple[str, float]:
        """Custom verifier for a recipe plan."""
        # Check if the plan includes all required sections
        required_sections = ["ingredients", "steps", "time"]
        score = 0.0
        feedback = []

        for section in required_sections:
            if section.lower() in plan.lower():
                score += 0.3
                feedback.append(f"✓ Plan includes {section} section")
            else:
                feedback.append(f"✗ Plan is missing {section} section")

        # Check for specific constraints
        if "vegetarian" in " ".join(constraints).lower():
            meat_ingredients = ["meat", "beef", "chicken", "pork", "fish"]
            has_meat = any(meat in plan.lower() for meat in meat_ingredients)

            if has_meat:
                feedback.append("✗ Recipe contains meat but should be vegetarian")
            else:
                score += 0.1
                feedback.append("✓ Recipe is vegetarian as required")

        # Cap the score at 1.0
        score = min(score, 1.0)

        return "\n".join(feedback), score

    # Create a custom verifier
    recipe_verifier = Verifiers.custom(verify_recipe)

    # Solve the problem with the Best of N algorithm and the custom verifier
    result = plangen.solve(
        problem,
        algorithm="best_of_n",
        verifier=recipe_verifier,
        n_plans=3,
    )

    # Print the results
    print("Problem:", problem)
    print("\nBest solution:", result["selected_solution"])
    print("\nScore:", result["score"])

    return result


def main():
    """Run all verifier examples."""
    calendar_verifier_example()
    print("\n" + "-" * 80 + "\n")

    math_verifier_example()
    print("\n" + "-" * 80 + "\n")

    custom_verifier_example()
    print("\n" + "-" * 80 + "\n")

    solve_with_verifier_example()


if __name__ == "__main__":
    main()
