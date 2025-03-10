"""
Test script for the Tree of Thought algorithm
"""

import json
import os

from dotenv import load_dotenv

from plangen.agents.constraint_agent import ConstraintAgent
from plangen.agents.verification_agent import VerificationAgent
from plangen.algorithms.tree_of_thought import TreeOfThought
from plangen.utils.llm_interface import LLMInterface

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a test of the Tree of Thought algorithm on a calendar scheduling problem."""

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

    # Initialize the verification agent
    verification_agent = VerificationAgent(llm_interface=llm_interface)

    # Initialize the Tree of Thought algorithm
    tot = TreeOfThought(
        llm_interface=llm_interface,
        constraint_agent=constraint_agent,
        verification_agent=verification_agent,
        branching_factor=3,  # Generate 3 next steps at each node
        max_depth=3,  # Maximum depth of the tree
        beam_width=2,  # Keep the 2 best paths at each level
        max_iterations=5,  # Maximum number of iterations
        temperature=0.7,  # Temperature for generation
    )

    print(f"Problem: {calendar_problem}")
    print("\nSolving problem with Tree of Thought algorithm...")

    try:
        # Run the algorithm
        best_plan, best_score, metadata = tot.run(calendar_problem)

        # Print the results
        print("\n=== Best Plan ===")
        print(best_plan)

        print(f"\n=== Best Score: {best_score} ===")

        # Print the constraints
        print("\n=== Extracted Constraints ===")
        print("\n".join([f"- {constraint}" for constraint in metadata["constraints"]]))

        # Print some statistics
        print("\n=== Algorithm Statistics ===")
        print(f"Branching Factor: {metadata['branching_factor']}")
        print(f"Max Depth: {metadata['max_depth']}")
        print(f"Beam Width: {metadata['beam_width']}")
        print(f"Total Paths Explored: {len(metadata['all_paths'])}")

        # Print the path history
        print("\n=== Path History ===")
        for i, path in enumerate(metadata["all_paths"]):
            print(
                f"\nPath {i+1} (Depth: {path['depth']}, Score: {path['score']}, Complete: {path.get('complete', False)}):"
            )
            print("\n".join(path["steps"]))
            print("-" * 50)

        # Save the results to a file
        with open("tree_of_thought_result.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_metadata = {
                "algorithm": metadata["algorithm"],
                "branching_factor": metadata["branching_factor"],
                "max_depth": metadata["max_depth"],
                "beam_width": metadata["beam_width"],
                "constraints": metadata["constraints"],
                "all_paths": [
                    {
                        "steps": path["steps"],
                        "score": path["score"],
                        "depth": path["depth"],
                        "complete": path.get("complete", False),
                        "feedback": str(path.get("feedback", "")),
                    }
                    for path in metadata["all_paths"]
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

        print("\nResults saved to tree_of_thought_result.json")

    except Exception as e:
        print(f"\nError running test: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
