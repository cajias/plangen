# Verification

Verification strategies and mechanisms for PlanGEN.

## Overview

PlanGEN uses a pluggable verification system. Domain-specific verifiers can validate solutions using specialized logic.

## Classes

### BaseVerifier

Abstract base class for all verifiers.

```python
class BaseVerifier(ABC):
    @abstractmethod
    def verify_solution(
        self,
        problem_statement: str,
        solution: str,
        constraints: list[str],
    ) -> VerificationResult | dict: ...

    @abstractmethod
    def is_applicable(self, problem_statement: str) -> bool: ...

    @abstractmethod
    def extract_domain_constraints(
        self,
        problem_statement: str,
        general_constraints: list[str],
    ) -> list[str]: ...
```

### MathVerifier

Specialized verifier for mathematical problems.

```python
from plangen.verification import MathVerifier

verifier = MathVerifier()
if verifier.is_applicable(problem):
    result = verifier.verify_solution(problem, solution, constraints)
```

### VerifierFactory

Creates verifiers based on problem domain.

```python
from plangen.verification import VerifierFactory

verifier = VerifierFactory.create("math")
# or
verifier = VerifierFactory.auto_detect(problem_statement)
```

## Verification Result

```python
class VerificationResult(TypedDict):
    is_valid: bool      # Whether solution satisfies constraints
    score: float        # Quality score (0-100)
    reason: str         # Explanation of result
    feedback: str       # Detailed feedback for improvement
```

## Custom Verifiers

Implement `BaseVerifier` for domain-specific validation:

```python
from plangen.verification import BaseVerifier

class SchedulingVerifier(BaseVerifier):
    def verify_solution(self, problem, solution, constraints):
        # Check time conflicts, capacity limits, etc.
        return {"is_valid": True, "score": 85, "reason": "...", "feedback": "..."}

    def is_applicable(self, problem):
        return "schedule" in problem.lower() or "meeting" in problem.lower()

    def extract_domain_constraints(self, problem, general_constraints):
        # Extract time windows, resource limits, etc.
        return general_constraints + ["No double-booking"]
```

## See Also

- [Verifiers](verifiers.md) - High-level verifier factory API
- [PlanGen](plangen.md) - Using verifiers with the main API
