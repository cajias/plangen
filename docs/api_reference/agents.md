# Agents

Internal agents for the PlanGEN workflow pipeline.

## Overview

PlanGEN uses specialized agents for each step of the planning process. These are internal components—use the high-level [PlanGen](plangen.md) API instead.

## Classes

### ConstraintAgent

Extracts constraints from problem statements.

```python
from plangen.agents import ConstraintAgent

agent = ConstraintAgent(model_name="gpt-4o")
constraints = agent.run(problem="Schedule a meeting...")
```

### SolutionAgent

Generates candidate solutions that satisfy constraints.

```python
from plangen.agents import SolutionAgent

agent = SolutionAgent(model_name="gpt-4o")
solution = agent.run(problem="...", constraints=["..."])
```

### VerificationAgent

Validates solutions against constraints and provides feedback.

```python
from plangen.agents import VerificationAgent

agent = VerificationAgent(model_name="gpt-4o")
result = agent.run(problem="...", solution="...", constraints=["..."])
```

### SelectionAgent

Selects the best solution from candidates based on verification scores.

```python
from plangen.agents import SelectionAgent

agent = SelectionAgent()
best = agent.run(solutions=[...], scores=[...])
```

## Base Class

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    def __init__(
        self,
        llm_interface: LLMInterface | None = None,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        system_message: str | None = None,
    ) -> None: ...

    @abstractmethod
    def run(self, *args, **kwargs) -> object: ...
```

## See Also

- [PlanGen](plangen.md) - High-level API (recommended)
- [Models](models.md) - LLM interfaces used by agents
