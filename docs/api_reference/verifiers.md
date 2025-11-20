# Verifiers API Reference

This page documents the verifier classes and interfaces in PlanGEN.

## Verifiers Factory

### `Verifiers` Class

Factory class for creating common verifiers.

```python
from plangen import Verifiers
```

#### `calendar()`

```python
@staticmethod
def calendar() -> BaseVerifier
```

Create a calendar scheduling verifier.

**Returns:**
- Verifier specialized for calendar scheduling problems

**Example:**
```python
verifier = Verifiers.calendar()
plangen.solve(problem, verifier=verifier)
```

#### `math()`

```python
@staticmethod
def math() -> BaseVerifier
```

Create a mathematical problem verifier.

**Returns:**
- Verifier specialized for math problems

**Example:**
```python
verifier = Verifiers.math()
plangen.solve(problem, verifier=verifier)
```

#### `algorithm()`

```python
@staticmethod
def algorithm() -> BaseVerifier
```

Create an algorithm design verifier.

**Returns:**
- Verifier specialized for algorithm design problems

**Example:**
```python
verifier = Verifiers.algorithm()
plangen.solve(problem, verifier=verifier)
```

## BaseVerifier

Base class for all verifiers.

### Methods

#### `verify_solution`

```python
def verify_solution(
    self,
    problem: str,
    solution: str,
    constraints: List[str]
) -> Tuple[str, float]
```

Verify a solution against constraints.

**Parameters:**
- `problem`: Problem statement
- `solution`: Proposed solution
- `constraints`: List of constraints

**Returns:**
- Tuple of (feedback: str, score: float)

**Example:**
```python
feedback, score = verifier.verify_solution(
    problem="Schedule a meeting...",
    solution="Monday 10:00-10:30",
    constraints=["30 minutes", "3 participants"]
)
```

#### `is_applicable`

```python
def is_applicable(self, problem: str) -> bool
```

Check if verifier applies to the problem.

**Parameters:**
- `problem`: Problem statement

**Returns:**
- True if verifier is applicable, False otherwise

**Example:**
```python
if verifier.is_applicable(problem):
    feedback, score = verifier.verify_solution(problem, solution, constraints)
```

#### `extract_domain_constraints`

```python
def extract_domain_constraints(self, problem: str) -> List[str]
```

Extract domain-specific constraints from problem.

**Parameters:**
- `problem`: Problem statement

**Returns:**
- List of domain-specific constraints

**Example:**
```python
constraints = verifier.extract_domain_constraints(problem)
```

## Custom Verifier

Create custom verifiers by subclassing BaseVerifier:

```python
from typing import List, Tuple
from plangen.verification.base_verifier import BaseVerifier

class CustomVerifier(BaseVerifier):
    """Custom domain-specific verifier."""
    
    def verify_solution(
        self,
        problem: str,
        solution: str,
        constraints: List[str]
    ) -> Tuple[str, float]:
        """Verify solution with custom logic."""
        feedback = []
        score = 1.0
        
        # Custom verification logic
        for constraint in constraints:
            if not self._check_constraint(solution, constraint):
                feedback.append(f"Failed: {constraint}")
                score -= 0.2
        
        return "\n".join(feedback) or "Valid", max(0.0, score)
    
    def _check_constraint(self, solution: str, constraint: str) -> bool:
        """Check specific constraint."""
        # Implementation
        return True
    
    def is_applicable(self, problem: str) -> bool:
        """Check if verifier applies."""
        return "your_domain_keyword" in problem.lower()
    
    def extract_domain_constraints(self, problem: str) -> List[str]:
        """Extract domain constraints."""
        # Implementation
        return []

# Usage
custom_verifier = CustomVerifier()
result = plangen.solve(problem, verifier=custom_verifier)
```

## VerifierFactory

Factory for registering and retrieving verifiers.

### `register`

```python
@classmethod
def register(cls, name: str, verifier_class: Type[BaseVerifier]) -> None
```

Register a custom verifier.

**Parameters:**
- `name`: Name for the verifier
- `verifier_class`: Verifier class

**Example:**
```python
from plangen.verification import VerifierFactory

VerifierFactory.register("custom", CustomVerifier)
```

### `get`

```python
@classmethod
def get(cls, name: str) -> BaseVerifier
```

Get a registered verifier by name.

**Parameters:**
- `name`: Verifier name

**Returns:**
- Verifier instance

**Example:**
```python
verifier = VerifierFactory.get("custom")
```

### `get_applicable`

```python
@classmethod
def get_applicable(cls, problem: str) -> Optional[BaseVerifier]
```

Get the first applicable verifier for a problem.

**Parameters:**
- `problem`: Problem statement

**Returns:**
- Applicable verifier or None

**Example:**
```python
verifier = VerifierFactory.get_applicable(problem)
if verifier:
    feedback, score = verifier.verify_solution(problem, solution, constraints)
```

## Complete Example

```python
from plangen import PlanGen, Verifiers
from plangen.verification.base_verifier import BaseVerifier
from typing import List, Tuple

# Use built-in verifier
plangen = PlanGen.create()
calendar_verifier = Verifiers.calendar()

result = plangen.solve(
    "Schedule a meeting...",
    verifier=calendar_verifier
)

# Create custom verifier
class EmailVerifier(BaseVerifier):
    def verify_solution(
        self, 
        problem: str,
        solution: str,
        constraints: List[str]
    ) -> Tuple[str, float]:
        # Custom logic for email validation
        score = 1.0
        feedback = []
        
        if "@" not in solution:
            feedback.append("Missing @ symbol")
            score -= 0.5
        
        if "." not in solution.split("@")[-1]:
            feedback.append("Invalid domain")
            score -= 0.3
        
        return "\n".join(feedback) or "Valid email", max(0.0, score)
    
    def is_applicable(self, problem: str) -> bool:
        return "email" in problem.lower()

# Use custom verifier
email_verifier = EmailVerifier()
result = plangen.solve(
    "Validate this email address...",
    verifier=email_verifier
)
```

## See Also

- [Verification Guide](../user_guide/verification.md)
- [Custom Verification Example](../examples/custom_verification.md)
- [Algorithm API](algorithm.md)
