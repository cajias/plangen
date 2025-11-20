# Visualization Guide

PlanGEN provides visualization capabilities to help you understand and debug the planning process. This guide explains how to use the visualization tools.

## Overview

Visualization in PlanGEN:

- Shows algorithm execution flow
- Displays score progression
- Illustrates reasoning paths
- Helps debug issues
- Enables analysis

## GraphRenderer

The `GraphRenderer` class is the main visualization tool:

```python
from plangen.visualization import GraphRenderer
from plangen.algorithms import TreeOfThought
from plangen.models import OpenAIModelInterface

# Create model
model = OpenAIModelInterface(model_name="gpt-4o")

# Create renderer
renderer = GraphRenderer(output_dir="./visualizations")

# Create algorithm with visualization
algorithm = TreeOfThought(
    branching_factor=3,
    max_depth=5,
    llm_interface=model
)

# Add observer
algorithm.add_observer(renderer)

# Run algorithm (visualizations will be generated)
problem = "Your problem here"
solution, score, metadata = algorithm.run(problem)

# Check ./visualizations directory for output
```

## Visualization Types

### Tree of Thought Visualization

Shows the exploration tree with nodes and branches:

```python
from plangen.visualization import GraphRenderer
from plangen.algorithms import TreeOfThought

renderer = GraphRenderer(output_dir="./tot_viz")
tot = TreeOfThought(branching_factor=3, max_depth=5, llm_interface=model)
tot.add_observer(renderer)

solution, score, metadata = tot.run(problem)
# Generates: tree_structure.png, path_scores.png
```

### BestOfN Visualization

Shows comparison of generated plans:

```python
from plangen.visualization import GraphRenderer
from plangen.algorithms import BestOfN

renderer = GraphRenderer(output_dir="./bon_viz")
bon = BestOfN(n_plans=5, llm_interface=model)
bon.add_observer(renderer)

solution, score, metadata = bon.run(problem)
# Generates: plan_comparison.png, score_distribution.png
```

### REBASE Visualization

Shows iterative refinement progress:

```python
from plangen.visualization import GraphRenderer
from plangen.algorithms import REBASE

renderer = GraphRenderer(output_dir="./rebase_viz")
rebase = REBASE(max_iterations=5, llm_interface=model)
rebase.add_observer(renderer)

solution, score, metadata = rebase.run(problem)
# Generates: iteration_scores.png, convergence_plot.png
```

## Configuration

### Output Directory

```python
# Specify where visualizations are saved
renderer = GraphRenderer(output_dir="./my_visualizations")
```

### Format Options

```python
# Configure visualization format
renderer = GraphRenderer(
    output_dir="./viz",
    format="png",  # or "svg", "pdf"
    dpi=300,       # resolution
    figsize=(12, 8)  # figure size
)
```

## Using with PlanGen API

```python
from plangen import PlanGen
from plangen.visualization import GraphRenderer

# Create PlanGen
plangen = PlanGen.create()

# For direct algorithm use, you need to access the internal algorithm
# This is more advanced usage - typically used for debugging
```

## Best Practices

### 1. Use Descriptive Output Directories

```python
# Good: Descriptive names
renderer = GraphRenderer(output_dir="./problem_type_visualization")

# Bad: Generic names
renderer = GraphRenderer(output_dir="./viz")
```

### 2. Clear Old Visualizations

```python
import shutil
import os

# Clear previous runs
if os.path.exists("./visualizations"):
    shutil.rmtree("./visualizations")

renderer = GraphRenderer(output_dir="./visualizations")
```

### 3. Save Metadata

```python
import json

solution, score, metadata = algorithm.run(problem)

# Save metadata with visualizations
with open("./visualizations/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

## Example Output

### Tree Structure

The tree structure visualization shows:
- Nodes representing reasoning steps
- Edges showing branching decisions
- Colors indicating scores
- Pruned branches marked differently

### Score Progression

Score progression plots show:
- X-axis: Iteration or step number
- Y-axis: Score (0.0 to 1.0)
- Line showing improvement over time
- Markers for significant events

### Comparison Charts

For BestOfN, comparison charts show:
- Bar chart of all plan scores
- Selected plan highlighted
- Distribution of scores
- Statistical summaries

## Advanced Features

### Custom Observers

Create custom observers for specialized visualization:

```python
from typing import Dict, Any

class CustomVisualizer:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.events = []
    
    def notify(self, event: str, data: Dict[str, Any]) -> None:
        """Receive notifications from algorithms."""
        self.events.append({'event': event, 'data': data})
        
        if event == "plan_generated":
            self._visualize_plan(data)
        elif event == "plan_verified":
            self._visualize_verification(data)
    
    def _visualize_plan(self, data):
        # Custom visualization logic
        pass
    
    def _visualize_verification(self, data):
        # Custom visualization logic
        pass

# Use custom visualizer
visualizer = CustomVisualizer(output_dir="./custom_viz")
algorithm.add_observer(visualizer)
```

## Troubleshooting

### No Visualizations Generated

- Check that output directory is writable
- Ensure algorithm has the observer added
- Verify the algorithm ran successfully

### Poor Quality Visualizations

```python
# Increase resolution
renderer = GraphRenderer(
    output_dir="./viz",
    dpi=300,  # Higher resolution
    figsize=(16, 12)  # Larger figure
)
```

## Integration with Notebooks

Visualizations work great in Jupyter notebooks:

```python
from IPython.display import Image, display

# Run algorithm with visualization
solution, score, metadata = algorithm.run(problem)

# Display in notebook
display(Image(filename="./visualizations/tree_structure.png"))
display(Image(filename="./visualizations/scores.png"))
```

## Next Steps

- See [Examples](../examples/visualization_example.md) for complete examples
- Read [Algorithm Reference](../algorithm_reference/index.md) for algorithm-specific visualization
- Check [Configuration](configuration.md) for advanced settings
