# BestOfN Algorithm Example

Example using the BestOfN algorithm.

```python
from plangen import PlanGen

plangen = PlanGen.create()

result = plangen.solve(
    problem="Your problem",
    algorithm="best_of_n",
    n_plans=5,
    parallel=True
)
```
