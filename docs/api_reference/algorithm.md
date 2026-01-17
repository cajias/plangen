# Algorithm API Reference

This page documents the Algorithm classes and interfaces in PlanGEN.

## Algorithm Factory

### `Algorithm.create`

```python
@classmethod
def create(
    cls,
    algorithm_type: str,
    model: ModelProtocol,
    **kwargs
) -> BaseAlgorithm
```

Factory method to create algorithm instances.

**Parameters:**

- `algorithm_type`: Type of algorithm ('best_of_n', 'tree_of_thought', 'rebase', 'mixture')
- `model`: Language model interface
- `**kwargs`: Algorithm-specific parameters

**Returns:**

- Configured algorithm instance

**Example:**

```python
from plangen import Algorithm, PlanGen

plangen = PlanGen.create()
algorithm = Algorithm.create(
    algorithm_type="best_of_n",
    model=plangen._plangen.model,
    n_plans=5,
    parallel=True
)
```

## BaseAlgorithm

Base class for all planning algorithms.

### Methods

#### `run`

```python
def run(
    self,
    problem: str,
    constraints: Optional[List[str]] = None,
    **kwargs
) -> Tuple[str, float, Dict[str, Any]]
```

Execute the planning algorithm.

**Parameters:**

- `problem`: Problem statement
- `constraints`: Optional list of constraints (extracted automatically if not provided)
- `**kwargs`: Additional algorithm-specific parameters

**Returns:**

- Tuple of (best_plan, score, metadata)

**Example:**

```python
best_plan, score, metadata = algorithm.run(
    problem="Schedule a meeting...",
    constraints=["30 minutes", "Monday only"]
)
```

#### `add_observer`

```python
def add_observer(self, observer: ObserverProtocol) -> None
```

Add an observer for visualization or logging.

**Parameters:**

- `observer`: Observer implementing ObserverProtocol

**Example:**

```python
from plangen.visualization import GraphRenderer

renderer = GraphRenderer(output_dir="./viz")
algorithm.add_observer(renderer)
```

## BestOfN

Generates multiple plans and selects the best one.

### Constructor

```python
def __init__(
    self,
    n_plans: int = 5,
    sampling_strategy: str = "diverse",
    parallel: bool = True,
    llm_interface: ModelProtocol = None,
    **kwargs
)
```

**Parameters:**

- `n_plans`: Number of plans to generate
- `sampling_strategy`: Strategy for generation ('diverse' or 'adaptive')
- `parallel`: Whether to generate in parallel
- `llm_interface`: Language model interface

**Example:**

```python
from plangen.algorithms import BestOfN
from plangen.models import OpenAIModelInterface

model = OpenAIModelInterface(model_name="gpt-4o")
algorithm = BestOfN(
    n_plans=10,
    sampling_strategy="diverse",
    parallel=True,
    llm_interface=model
)
```

## TreeOfThought

Explores multiple reasoning paths in a tree structure.

### Constructor

```python
def __init__(
    self,
    branching_factor: int = 3,
    max_depth: int = 5,
    beam_width: int = 2,
    llm_interface: ModelProtocol = None,
    **kwargs
)
```

**Parameters:**

- `branching_factor`: Number of branches per node
- `max_depth`: Maximum tree depth
- `beam_width`: Number of best branches to keep at each level
- `llm_interface`: Language model interface

**Example:**

```python
from plangen.algorithms import TreeOfThought

algorithm = TreeOfThought(
    branching_factor=4,
    max_depth=6,
    beam_width=3,
    llm_interface=model
)
```

## REBASE

Iteratively refines solutions based on feedback.

### Constructor

```python
def __init__(
    self,
    max_iterations: int = 5,
    improvement_threshold: float = 0.1,
    llm_interface: ModelProtocol = None,
    **kwargs
)
```

**Parameters:**

- `max_iterations`: Maximum number of refinement iterations
- `improvement_threshold`: Minimum improvement to continue
- `llm_interface`: Language model interface

**Example:**

```python
from plangen.algorithms import REBASE

algorithm = REBASE(
    max_iterations=10,
    improvement_threshold=0.05,
    llm_interface=model
)
```

## MixtureOfAlgorithms

Dynamically selects the best algorithm for the problem.

### Constructor

```python
def __init__(
    self,
    max_algorithm_switches: int = 2,
    llm_interface: ModelProtocol = None,
    **kwargs
)
```

**Parameters:**

- `max_algorithm_switches`: Maximum number of algorithm switches allowed
- `llm_interface`: Language model interface

**Example:**

```python
from plangen.algorithms import MixtureOfAlgorithms

algorithm = MixtureOfAlgorithms(
    max_algorithm_switches=3,
    llm_interface=model
)
```

## Common Metadata

All algorithms return metadata with run information:

```python
metadata = {
    'algorithm': 'best_of_n',
    'num_plans_generated': 5,
    'generation_time': 12.5,
    'verification_time': 8.3,
    'total_time': 20.8,
    'all_scores': [0.9, 0.85, 0.95, 0.8, 0.88],
    'selected_index': 2,
    # Algorithm-specific metadata
}
```

## Observer Protocol

For custom observers:

```python
from typing import Protocol

class ObserverProtocol(Protocol):
    def notify(self, event: str, data: Dict[str, Any]) -> None:
        """Receive notifications from algorithms."""
        pass
```

## Complete Example

```python
from plangen import PlanGen
from plangen.algorithms import BestOfN, TreeOfThought, REBASE
from plangen.visualization import GraphRenderer

# Create model
plangen = PlanGen.create()
model = plangen._plangen.model

# Create visualizer
renderer = GraphRenderer(output_dir="./visualizations")

# Try different algorithms
problem = "Your problem statement here"

# BestOfN
best_of_n = BestOfN(n_plans=5, llm_interface=model)
best_of_n.add_observer(renderer)
plan1, score1, meta1 = best_of_n.run(problem)

# TreeOfThought
tot = TreeOfThought(branching_factor=3, max_depth=5, llm_interface=model)
tot.add_observer(renderer)
plan2, score2, meta2 = tot.run(problem)

# REBASE
rebase = REBASE(max_iterations=5, llm_interface=model)
rebase.add_observer(renderer)
plan3, score3, meta3 = rebase.run(problem)

# Compare results
print(f"BestOfN: {score1}")
print(f"TreeOfThought: {score2}")
print(f"REBASE: {score3}")
```

## See Also

- [Algorithm Selection Guide](../algorithm_reference/algorithm_selection_guide.md)
- [Algorithm References](../algorithm_reference/index.md)
- [Visualization](visualization.md)
