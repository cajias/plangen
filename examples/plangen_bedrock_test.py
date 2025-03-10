"""
Full PlanGEN test using AWS Bedrock
"""

import json
import os

from dotenv import load_dotenv

from plangen import PlanGEN
from plangen.models import BedrockModelInterface
from plangen.prompts import PromptManager

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a full PlanGEN test with the calendar scheduling problem."""

    # Calendar scheduling problem from the paper
    calendar_problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Initialize Bedrock model
    model = BedrockModelInterface(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        temperature=0.7,
        max_tokens=1024,
    )

    # Initialize prompt manager with custom prompts
    prompt_manager = PromptManager()

    # Update prompts for better performance with Claude
    prompt_manager.update_prompt(
        "constraint_extraction",
        """
        You are an expert scheduler. Please analyze the following problem and identify all constraints:
        
        {problem}
        
        List all constraints in the problem, including:
        - Meeting duration
        - Time window
        - Participant availability/unavailability
        - Any other requirements
        
        Format your response as a clear, numbered list of constraints.
        """,
    )

    prompt_manager.update_prompt(
        "solution_generation",
        """
        You are an expert scheduler. Please solve the following problem:
        
        {problem}
        
        Consider these constraints:
        {constraints}
        
        Generate a detailed solution that:
        1. Analyzes each person's availability
        2. Finds common available time slots
        3. Identifies the earliest slot that works for everyone
        4. Verifies the solution meets all constraints
        
        Format your solution as a step-by-step plan with a clear final answer.
        """,
    )

    prompt_manager.update_prompt(
        "solution_verification",
        """
        You are an expert scheduler. Please verify the following solution against the constraints:
        
        Problem:
        {problem}
        
        Constraints:
        {constraints}
        
        Proposed Solution:
        {solution}
        
        Verify if the solution satisfies all constraints. Check for:
        - Meeting duration is correct
        - Time slot is within the allowed window
        - No conflicts with any participant's busy schedule
        - The slot is indeed the earliest possible
        
        Format your verification as a clear analysis with a final verdict (Valid/Invalid).
        """,
    )

    prompt_manager.update_prompt(
        "solution_selection",
        """
        You are an expert scheduler. Please select the best solution from the following candidates:
        
        Problem:
        {problem}
        
        Constraints:
        {constraints}
        
        Solutions:
        {solutions}
        
        Verification Results:
        {verification_results}
        
        Select the best solution based on:
        - Correctness (meets all constraints)
        - Optimality (finds the earliest possible slot)
        - Clarity (clear explanation and reasoning)
        
        Format your response with:
        1. The selected solution
        2. Your reasoning for selecting this solution
        """,
    )

    # Initialize PlanGEN
    plangen = PlanGEN(
        model=model,
        prompt_manager=prompt_manager,
        num_solutions=2,  # Generate 2 solutions to save time
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving problem with PlanGEN using AWS Bedrock Claude 3...")

    try:
        # Solve the problem
        result = plangen.solve(calendar_problem)

        # Print the results
        print("\n=== Extracted Constraints ===")
        print(result.get("constraints", "No constraints found"))

        # Print solutions if available
        if "solutions" in result:
            print(f"\n=== Generated {len(result['solutions'])} Solutions ===")
            for i, solution in enumerate(result["solutions"]):
                print(f"\nSolution {i+1}:")
                print(solution[:300] + "..." if len(solution) > 300 else solution)

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
        with open("plangen_bedrock_result.json", "w") as f:
            json.dump(result, f, indent=2)

        print("\nResults saved to plangen_bedrock_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")


if __name__ == "__main__":
    main()
