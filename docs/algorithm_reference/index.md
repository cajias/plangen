# Algorithm Reference

This section provides detailed information about the planning algorithms available in PlanGEN.

## Available Algorithms

- [BestOfN](best_of_n.md) - Generates multiple plans and selects the best one based on verification scores
- [TreeOfThought](tree_of_thought.md) - Explores multiple reasoning paths in a tree structure, allowing for backtracking
- [REBASE](rebase.md) - Uses recursive refinement to improve plans through iterative feedback
- [MixtureOfAlgorithms](mixture_of_algorithms.md) - Dynamically selects the best algorithm for the problem

## Algorithm Comparison

| Algorithm | When to Use | Pros | Cons |
|-----------|-------------|------|------|
| BestOfN | Quick solutions, diverse options | Simple, parallelizable | Limited exploration |
| TreeOfThought | Complex reasoning, step-by-step planning | Structured exploration, backtracking | Higher computational cost |
| REBASE | When refinement is needed | Iterative improvement | More API calls, higher cost |
| MixtureOfAlgorithms | When uncertain which algorithm is best | Adaptability | Overhead from algorithm switching |