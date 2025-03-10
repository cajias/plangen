"""
Calendar scheduling example using AWS Bedrock
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
    """Run a calendar scheduling example with AWS Bedrock."""

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

    # Define custom prompts for the calendar scheduling problem
    constraint_prompt = """
    You are an expert scheduler. Please analyze the following scheduling problem and identify all constraints:
    
    Problem: Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    
    Extract and list all constraints in the problem, including:
    1. Meeting duration requirements
    2. Time window restrictions
    3. Each participant's busy/unavailable times
    4. Any other scheduling requirements
    
    Format your response as a clear, numbered list of constraints.
    """

    solution_prompt = """
    You are an expert scheduler. Please solve the following scheduling problem:
    
    Problem: Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    
    Generate a detailed solution by:
    1. Creating a timeline of each person's availability
    2. Identifying all time slots when everyone is available
    3. Finding the earliest time slot that works for all participants
    4. Verifying this slot meets all constraints
    
    Your solution should be clear, precise, and include the exact time slot (start and end time) for the meeting.
    """

    verification_prompt = """
    You are an expert scheduler. Please verify if the following solution correctly solves the scheduling problem:
    
    Problem: Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    
    Proposed Solution:
    {solution}
    
    Verify if the solution:
    1. Respects the meeting duration requirement (30 minutes)
    2. Falls within the allowed time window (9:00-17:00)
    3. Avoids all conflicts with participants' busy schedules
    4. Is indeed the earliest possible time slot that works for everyone
    
    Provide a detailed verification with a clear VALID or INVALID conclusion.
    """

    selection_prompt = """
    You are an expert scheduler. Please select the best solution for the following scheduling problem:
    
    Problem: Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    
    Candidate Solutions:
    {solutions}
    
    Verification Results:
    {verification_results}
    
    Select the best solution based on:
    1. Correctness - Does it satisfy all constraints?
    2. Optimality - Is it the earliest possible time slot?
    3. Clarity - Is the solution clearly explained?
    
    Provide your selected solution and detailed reasoning for your choice.
    """

    # Update the prompts
    prompt_manager.update_prompt("constraint_extraction", constraint_prompt)
    prompt_manager.update_prompt("solution_generation", solution_prompt)
    prompt_manager.update_prompt("solution_verification", verification_prompt)
    prompt_manager.update_prompt("solution_selection", selection_prompt)

    # Initialize PlanGEN
    plangen = PlanGEN(
        model=model,
        prompt_manager=prompt_manager,
        num_solutions=2,  # Generate 2 solutions to save time
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving calendar scheduling problem with AWS Bedrock Claude 3...")

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
                print(solution)

        # Print verification results if available
        if "verification_results" in result:
            print(f"\n=== Verification Results ===")
            for i, vr in enumerate(result["verification_results"]):
                print(f"\nVerification {i+1}:")
                print(vr)

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
        with open("calendar_scheduling_bedrock_result.json", "w") as f:
            json.dump(result, f, indent=2)

        print("\nResults saved to calendar_scheduling_bedrock_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")


if __name__ == "__main__":
    main()
