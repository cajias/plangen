"""
Test script for the REBASE algorithm
"""

import json
import os
import sys

from dotenv import load_dotenv

# Add examples directory to path to allow importing calendar_domain
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calendar_domain import CalendarVerifier
from plangen.agents.constraint_agent import ConstraintAgent
from plangen.agents.verification_agent import VerificationAgent
from plangen.algorithms.rebase import REBASE
from plangen.utils.llm_interface import LLMInterface

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a test of the REBASE algorithm on a calendar scheduling problem."""

    # Calendar scheduling problem
    calendar_problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Initialize the LLM interface
    # You can change the model to "gpt-4o" or "anthropic.claude-3-sonnet-20240229-v1:0" or "gemini-1.5-pro"
    llm_interface = LLMInterface(
        model_name="gpt-4o",
        temperature=0.7,
        max_tokens=1024,
    )

    # Initialize the constraint agent
    constraint_agent = ConstraintAgent(llm_interface=llm_interface)

    # Initialize the verification agent with calendar verifier
    verification_agent = VerificationAgent(
        llm_interface=llm_interface, verifier=CalendarVerifier()
    )

    # Initialize the REBASE algorithm
    rebase = REBASE(
        llm_interface=llm_interface,
        constraint_agent=constraint_agent,
        verification_agent=verification_agent,
        max_iterations=5,  # Maximum number of refinement iterations
        improvement_threshold=10.0,  # Minimum score improvement to continue refining
        temperature=0.7,  # Temperature for generation
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving problem with REBASE algorithm...")

    try:
        # Run the algorithm
        best_plan, best_score, metadata = rebase.run(calendar_problem)

        # Print the results
        print("\n=== Best Plan ===")
        print(best_plan)

        print(f"\n=== Best Score: {best_score} ===")

        # Print the constraints
        print("\n=== Extracted Constraints ===")
        print("\n".join([f"- {constraint}" for constraint in metadata["constraints"]]))

        # Print algorithm statistics
        print("\n=== Algorithm Statistics ===")
        print(f"Max Iterations: {metadata['max_iterations']}")
        print(f"Improvement Threshold: {metadata['improvement_threshold']}")
        print(f"Total Iterations Completed: {len(metadata['iterations']) - 1}")

        # Print iteration history
        print("\n=== Iteration History ===")
        for i, iteration in enumerate(metadata["iterations"]):
            print(f"\nIteration {i}:")
            print(f"  Score: {iteration['score']:.1f}")
            if i > 0:
                improvement = iteration["score"] - metadata["iterations"][i-1]["score"]
                print(f"  Improvement: {improvement:+.1f}")
            print(f"  Plan: {iteration['plan'][:100]}...")  # First 100 chars
            if iteration["feedback"]:
                print(f"  Feedback: {iteration['feedback'][:100]}...")  # First 100 chars

        # Save the results to a file
        with open("rebase_result.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_metadata = {
                "algorithm": metadata["algorithm"],
                "max_iterations": metadata["max_iterations"],
                "improvement_threshold": metadata["improvement_threshold"],
                "constraints": metadata["constraints"],
                "iterations": [
                    {
                        "plan": iteration["plan"],
                        "score": iteration["score"],
                        "feedback": str(iteration.get("feedback", "")),
                    }
                    for iteration in metadata["iterations"]
                ],
            }

            json.dump(
                {
                    "problem": calendar_problem,
                    "best_plan": best_plan,
                    "best_score": best_score,
                    "metadata": serializable_metadata,
                },
                f,
                indent=2,
            )

        print("\nResults saved to rebase_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
