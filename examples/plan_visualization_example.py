"""
Example demonstrating plan visualization for Tree of Thought algorithm.
"""

import json
import os

from plangen.algorithms.tree_of_thought import TreeOfThought
from plangen.visualization.graph_renderer import GraphRenderer


def main():
    """Run a simple Tree of Thought example with visualization."""

    # Create output directory for visualizations
    output_dir = os.path.join(os.path.dirname(__file__), "visualizations")
    os.makedirs(output_dir, exist_ok=True)

    # Problem statement for the algorithm
    problem_statement = """
    You need to organize a small conference with the following requirements:
    1. Schedule 3 speakers during a one-day event
    2. Include breaks for networking
    3. Plan lunch arrangements
    4. Arrange for basic AV equipment
    5. Set up a registration process
    """

    # Create a visualization observer
    graph_renderer = GraphRenderer(
        output_dir=output_dir, auto_render=True, render_format="png"
    )

    # Create the algorithm with appropriate parameters
    algorithm = TreeOfThought(
        branching_factor=2,  # Generate 2 options at each step
        max_depth=4,  # Allow up to 4 steps
        beam_width=2,  # Keep the 2 best plans at each level
        temperature=0.7,  # Use moderate randomness
    )

    # Add the observer to the algorithm
    algorithm.add_observer(graph_renderer)

    # Run the algorithm
    print("Running Tree of Thought algorithm...")
    best_plan, best_score, metadata = algorithm.run(problem_statement)

    # Display algorithm results
    print("\n" + "=" * 50)
    print("BEST PLAN:")
    print("-" * 50)
    print(best_plan)
    print("\nScore:", best_score)
    print("=" * 50)

    # Save visualization data
    graph_renderer.save_graph_data(filename="tree_of_thought_graph_data.json")

    # Save final visualization
    graph_renderer.render(
        save=True, display=False, filename="tree_of_thought_final.png"
    )

    print(f"\nVisualizations saved to: {output_dir}")

    # Save metadata
    with open(os.path.join(output_dir, "tree_of_thought_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()
