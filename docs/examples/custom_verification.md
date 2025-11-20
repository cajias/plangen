# Custom Verification Example

Example creating custom verifiers.

```python
from plangen import PlanGen
from plangen.verification.base_verifier import BaseVerifier

class CustomVerifier(BaseVerifier):
    def verify_solution(self, problem, solution, constraints):
        # Custom logic
        return "Feedback", 0.9

plangen = PlanGen.create()
verifier = CustomVerifier()
result = plangen.solve(problem, verifier=verifier)
```
