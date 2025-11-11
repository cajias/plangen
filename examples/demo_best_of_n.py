"""
Test script for the Best of N algorithm
"""

import json
import os

from dotenv import load_dotenv

from plangen.agents.constraint_agent import ConstraintAgent
from plangen.agents.verification_agent import VerificationAgent
from plangen.algorithms.best_of_n import BestOfN
from plangen.examples.calendar import CalendarVerifier
from plangen.utils.llm_interface import LLMInterface

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a test of the Best of N algorithm on a calendar scheduling problem."""

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

    # Initialize the Best of N algorithm
    best_of_n = BestOfN(
        llm_interface=llm_interface,
        constraint_agent=constraint_agent,
        verification_agent=verification_agent,
        n_plans=5,
        sampling_strategy="diverse",
        parallel=False,
        temperature=0.7,
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving problem with Best of N algorithm...")

    try:
        # Run the algorithm
        best_plan, best_score, metadata = best_of_n.run(calendar_problem)

        # Print the results
        print("\n=== Best Plan ===")
        print(best_plan)

        print(f"\n=== Best Score: {best_score} ===")

        # Print the constraints
        print("\n=== Extracted Constraints ===")
        print("\n".join([f"- {constraint}" for constraint in metadata["constraints"]]))

        # Print algorithm statistics
        print("\n=== Algorithm Statistics ===")
        print(f"N Plans: {metadata['n_plans']}")
        print(f"Sampling Strategy: {metadata['sampling_strategy']}")
        print(f"Mean Score: {metadata['mean_score']:.2f}")
        print(f"Standard Deviation: {metadata['std_score']:.2f}")

        # Print all plans and scores
        print("\n=== All Plans ===")
        for i, (score, feedback) in enumerate(
            zip(metadata["all_scores"], metadata["all_feedbacks"])
        ):
            is_best = i == metadata["best_index"]
            print(f"\nPlan {i+1}{' (BEST)' if is_best else ''}:")
            print(f"Score: {score}")
            print(f"Feedback: {feedback}")

        # Save the results to a file
        with open("best_of_n_result.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_metadata = {
                "algorithm": metadata["algorithm"],
                "n_plans": metadata["n_plans"],
                "sampling_strategy": metadata["sampling_strategy"],
                "parallel": metadata["parallel"],
                "constraints": metadata["constraints"],
                "all_scores": list(metadata["all_scores"]),
                "all_feedbacks": list(metadata["all_feedbacks"]),
                "best_index": metadata["best_index"],
                "mean_score": float(metadata["mean_score"]),
                "std_score": float(metadata["std_score"]),
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

        print("\nResults saved to best_of_n_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
