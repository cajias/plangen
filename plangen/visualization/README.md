# Plan Visualization

This module provides visualization tools for monitoring and analyzing plan exploration algorithms in the PlanGEN library.

## Overview

The visualization module offers:

1. **Observer Pattern**: A generic observer pattern implementation for monitoring algorithm execution
2. **Graph Rendering**: Real-time visualization of plan exploration as graph/tree structures
3. **Algorithm-Specific Visualizations**: Tailored visualizations for different algorithm types

## Usage

### Basic Usage

```python
from plangen.algorithms import TreeOfThought
from plangen.visualization import GraphRenderer

# Create visualization renderer
graph_renderer = GraphRenderer(
    output_dir="./visualizations",
    auto_render=True
)

# Create algorithm
algorithm = TreeOfThought()

# Add observer to algorithm
algorithm.add_observer(graph_renderer)

# Run algorithm (visualization happens automatically)
best_plan, best_score, metadata = algorithm.run(problem_statement)

# Save final graph
graph_renderer.save_graph_data("final_graph.json")
```

### Visualization Options

The `GraphRenderer` supports various options:

- **Output Directory**: Where to save visualizations
- **Render Format**: PNG, SVG, or PDF format (default: PNG)
- **Auto-Render**: Automatically render on each update (default: True)
- **Display Mode**: Save to file or display interactively

## Supported Algorithms

### Tree of Thought

Visualizes the exploration tree with:
- Nodes for each plan state
- Color coding by score
- Visual indication of complete vs. incomplete plans
- Tree structure showing the exploration path

### REBASE

Visualizes the refinement process with:
- Linear sequence of plan iterations
- Feedback and score at each refinement step

### Best of N

Visualizes multiple plans with:
- Star pattern with central root
- Individual plans as separate nodes
- Score-based coloring

## Extending

To add visualization for new algorithms:

1. Ensure your algorithm inherits from `BaseAlgorithm` 
2. Call `self.notify_observers(data)` at key points in the algorithm
3. Add algorithm-specific rendering in `GraphRenderer._update_[algorithm]_graph()`

## Dependencies

- NetworkX: Graph data structure
- Matplotlib: Rendering visualizations
- (Optional) PyGraphviz: For improved tree layouts

## Examples

See the `examples/plan_visualization_example.py` for a complete usage example.