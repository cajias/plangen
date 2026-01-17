# Visualization API Reference

This page documents the visualization classes and interfaces in PlanGEN.

## GraphRenderer

The main visualization class for rendering algorithm execution.

### Constructor

```python
def __init__(
    self,
    output_dir: str = "./visualizations",
    format: str = "png",
    dpi: int = 100,
    figsize: tuple = (10, 8)
)
```

**Parameters:**

- `output_dir`: Directory to save visualizations
- `format`: Output format ('png', 'svg', 'pdf')
- `dpi`: Resolution for raster formats
- `figsize`: Figure size as (width, height) in inches

**Example:**

```python
from plangen.visualization import GraphRenderer

renderer = GraphRenderer(
    output_dir="./my_visualizations",
    format="png",
    dpi=300,
    figsize=(12, 8)
)
```

### Methods

#### `notify`

```python
def notify(self, event: str, data: Dict[str, Any]) -> None
```

Receive notifications from algorithms during execution.

**Parameters:**

- `event`: Event type (e.g., "plan_generated", "plan_verified")
- `data`: Event data dictionary

**Example:**

```python
# Typically called automatically by algorithms
algorithm.add_observer(renderer)
```

#### `render_tree`

```python
def render_tree(
    self,
    tree_data: Dict[str, Any],
    filename: str = "tree_structure.png"
) -> None
```

Render a tree structure visualization.

**Parameters:**

- `tree_data`: Tree structure data
- `filename`: Output filename

#### `render_scores`

```python
def render_scores(
    self,
    scores: List[float],
    filename: str = "scores.png"
) -> None
```

Render score progression plot.

**Parameters:**

- `scores`: List of scores over time
- `filename`: Output filename

## ObserverProtocol

Protocol for implementing custom observers.

```python
from typing import Protocol, Dict, Any

class ObserverProtocol(Protocol):
    """Protocol for algorithm observers."""
    
    def notify(self, event: str, data: Dict[str, Any]) -> None:
        """Receive notifications from algorithms."""
        ...
```

## Custom Observer Example

```python
from typing import Dict, Any
import json

class JsonLogger:
    """Observer that logs events to JSON."""
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.events = []
    
    def notify(self, event: str, data: Dict[str, Any]) -> None:
        """Log event to list."""
        self.events.append({
            'event': event,
            'timestamp': time.time(),
            'data': data
        })
    
    def save(self) -> None:
        """Save events to file."""
        with open(self.output_file, 'w') as f:
            json.dump(self.events, f, indent=2)

# Usage
logger = JsonLogger("events.json")
algorithm.add_observer(logger)
solution, score, metadata = algorithm.run(problem)
logger.save()
```

## Visualization Types

### Tree Visualizations

Used with TreeOfThought algorithm to show exploration paths.

### Score Plots

Used with REBASE to show iterative improvement.

### Comparison Charts

Used with BestOfN to compare generated plans.

## See Also

- [Visualization Guide](../user_guide/visualization.md)
- [Algorithm API](algorithm.md)
- [Examples](../examples/visualization_example.md)
