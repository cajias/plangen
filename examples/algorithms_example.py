"""
Examples of using different algorithms with the PlanGEN public API.

This file demonstrates how to use each of the planning algorithms
available in the PlanGEN framework through the new API.
"""

from plangen import Algorithm, PlanGen, Visualization


def best_of_n_example():
    """Example of using the Best of N algorithm."""
    print("=== Best of N Algorithm Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a problem
    problem = "Design a sorting algorithm that works well for nearly sorted arrays."

    # Solve using the Best of N algorithm
    result = plangen.solve(
        problem,
        algorithm="best_of_n",
        n_plans=3,
        sampling_strategy="diverse",
    )

    # Print the results
    print("Problem:", problem)
    print("\nBest solution:", result["selected_solution"])
    print("\nScore:", result["score"])

    return result


def tree_of_thought_example():
    """Example of using the Tree of Thought algorithm."""
    print("=== Tree of Thought Algorithm Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a problem
    problem = "Create a marketing strategy for a new eco-friendly product targeting millennials."

    # Solve using the Tree of Thought algorithm
    result = plangen.solve(
        problem,
        algorithm="tree_of_thought",
        max_depth=3,
        branching_factor=2,
        beam_width=2,
    )

    # Print the results
    print("Problem:", problem)
    print("\nBest solution:", result["selected_solution"])
    print("\nScore:", result["score"])

    # Visualize the Tree of Thought
    vis_path = Visualization.create_graph(
        result,
        output_format="png",
        output_path="tree_of_thought_visualization.png",
    )
    print(f"\nTree visualization saved to: {vis_path}")

    return result


def rebase_example():
    """Example of using the REBASE algorithm."""
    print("=== REBASE Algorithm Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a problem
    problem = "Develop a fitness app that helps users track their progress and stay motivated."

    # Solve using the REBASE algorithm
    result = plangen.solve(
        problem,
        algorithm="rebase",
        max_iterations=3,
        improvement_threshold=0.1,
    )

    # Print the results
    print("Problem:", problem)
    print("\nBest solution:", result["selected_solution"])
    print("\nScore:", result["score"])

    # If the result includes iteration history, print it
    if "metadata" in result and "iterations" in result["metadata"]:
        print("\nREBASE iterations:")
        for i, iteration in enumerate(result["metadata"]["iterations"]):
            print(f"Iteration {i+1} score: {iteration.get('score', 'N/A')}")

    return result


def mixture_of_algorithms_example():
    """Example of using the Mixture of Algorithms approach."""
    print("=== Mixture of Algorithms Example ===")

    # Create a plangen instance
    plangen = PlanGen.create()

    # Define a complex problem
    problem = """
    Design a system to optimize delivery routes for a fleet of 20 trucks serving 100 locations in a city.
    Constraints:
    - Each truck has a maximum capacity of 1000 kg
    - Deliveries must be made within specific time windows
    - Some locations require special handling
    - The system must minimize total distance traveled
    - The system must balance workload across all trucks
    """

    # Solve using the Mixture of Algorithms approach
    result = plangen.solve(
        problem,
        algorithm="mixture",
        max_algorithm_switches=2,
    )

    # Print the results
    print("Problem:", problem)
    print("\nBest solution:", result["selected_solution"])
    print("\nScore:", result["score"])

    # If the result includes algorithm selection history, print it
    if "metadata" in result and "selected_algorithms" in result["metadata"]:
        print("\nAlgorithm selection history:")
        for i, algo in enumerate(result["metadata"]["selected_algorithms"]):
            print(f"Step {i+1}: {algo}")

    return result


def algorithm_direct_usage_example():
    """Example of using algorithm instances directly."""
    print("=== Direct Algorithm Usage Example ===")

    # Create algorithm instances directly
    best_of_n = Algorithm.create("best_of_n", n_plans=3)
    tree_of_thought = Algorithm.create("tree_of_thought", max_depth=3)
    rebase = Algorithm.create("rebase", max_iterations=2)

    # Define a simple problem
    problem = "Create a plan for a weekend trip to a nearby city."

    # Run each algorithm on the problem
    print("Running BestOfN algorithm...")
    bon_plan, bon_score, bon_metadata = best_of_n.run(problem)

    print("Running TreeOfThought algorithm...")
    tot_plan, tot_score, tot_metadata = tree_of_thought.run(problem)

    print("Running REBASE algorithm...")
    rebase_plan, rebase_score, rebase_metadata = rebase.run(problem)

    # Compare results
    print("\nAlgorithm comparison results:")
    print(f"BestOfN score: {bon_score}")
    print(f"TreeOfThought score: {tot_score}")
    print(f"REBASE score: {rebase_score}")

    # Determine the best algorithm for this problem
    best_score = max(bon_score, tot_score, rebase_score)
    if best_score == bon_score:
        print("\nBest algorithm for this problem: BestOfN")
        best_plan = bon_plan
    elif best_score == tot_score:
        print("\nBest algorithm for this problem: TreeOfThought")
        best_plan = tot_plan
    else:
        print("\nBest algorithm for this problem: REBASE")
        best_plan = rebase_plan

    print("\nBest plan:", best_plan)

    return {
        "problem": problem,
        "best_of_n": {"plan": bon_plan, "score": bon_score},
        "tree_of_thought": {"plan": tot_plan, "score": tot_score},
        "rebase": {"plan": rebase_plan, "score": rebase_score},
    }


def main():
    """Run all algorithm examples."""
    best_of_n_example()
    print("\n" + "-" * 80 + "\n")

    tree_of_thought_example()
    print("\n" + "-" * 80 + "\n")

    rebase_example()
    print("\n" + "-" * 80 + "\n")

    mixture_of_algorithms_example()
    print("\n" + "-" * 80 + "\n")

    algorithm_direct_usage_example()


if __name__ == "__main__":
    main()
