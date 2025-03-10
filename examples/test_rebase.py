"""
Test script for the REBASE algorithm
"""

import json
import os

from dotenv import load_dotenv

from plangen.agents.constraint_agent import ConstraintAgent
from plangen.agents.verification_agent import VerificationAgent
from plangen.algorithms.rebase import REBASE
from plangen.examples.calendar import CalendarVerifier
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
        max_depth=5,  # Maximum depth of the tree
        max_width=3,  # Maximum children per node
        pruning_threshold=0.3,  # Prune paths with relative score < 0.3
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
        print(f"Max Depth: {metadata['max_depth']}")
        print(f"Max Width: {metadata['max_width']}")
        print(f"Pruning Threshold: {metadata['pruning_threshold']}")
        print(f"Total Nodes Explored: {metadata['nodes_explored']}")

        # Print exploration tree statistics
        complete_nodes = sum(1 for node in metadata["all_nodes"] if node["complete"])
        pruned_nodes = metadata["nodes_explored"] - len(
            [
                node
                for node in metadata["all_nodes"]
                if node["score"] / 100 >= metadata["pruning_threshold"]
            ]
        )

        print(f"\n=== Tree Statistics ===")
        print(f"Complete Solutions Found: {complete_nodes}")
        print(f"Nodes Pruned: {pruned_nodes}")

        # Print the node history, grouped by depth
        print("\n=== Node Exploration History ===")
        max_depth_found = max(node["depth"] for node in metadata["all_nodes"])

        for depth in range(max_depth_found + 1):
            depth_nodes = [
                node for node in metadata["all_nodes"] if node["depth"] == depth
            ]
            depth_nodes.sort(key=lambda x: x["score"], reverse=True)

            print(f"\nDepth {depth} (Total nodes: {len(depth_nodes)}):")
            for i, node in enumerate(depth_nodes):
                status = "✓" if node["complete"] else " "
                pruned = (
                    "🗑" if node["score"] / 100 < metadata["pruning_threshold"] else " "
                )
                steps_text = " → ".join(node["steps"])
                print(f"{status}{pruned} [{node['score']:>3.0f}] {steps_text}")

        # Save the results to a file
        with open("rebase_result.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_metadata = {
                "algorithm": metadata["algorithm"],
                "max_depth": metadata["max_depth"],
                "max_width": metadata["max_width"],
                "pruning_threshold": metadata["pruning_threshold"],
                "nodes_explored": metadata["nodes_explored"],
                "constraints": metadata["constraints"],
                "all_nodes": [
                    {
                        "steps": node["steps"],
                        "score": node["score"],
                        "depth": node["depth"],
                        "complete": node.get("complete", False),
                        "feedback": str(node.get("feedback", "")),
                    }
                    for node in metadata["all_nodes"]
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
