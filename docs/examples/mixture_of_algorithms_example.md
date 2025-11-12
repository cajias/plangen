# Mixture of Algorithms Example

Example using automatic algorithm selection.

```python
from plangen import PlanGen

plangen = PlanGen.create()

result = plangen.solve(
    problem="Your problem",
    algorithm="mixture"
)

print(f"Used: {result['metadata']['algorithm_used']}")
```
