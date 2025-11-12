# TreeOfThought Algorithm Example

Example using TreeOfThought algorithm.

```python
from plangen import PlanGen

plangen = PlanGen.create()

result = plangen.solve(
    problem="Your problem",
    algorithm="tree_of_thought",
    branching_factor=3,
    max_depth=5
)
```
