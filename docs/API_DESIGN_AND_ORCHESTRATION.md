# API Design and Orchestration Integration Guide

## Overview

This document provides a comprehensive review of the PlanGEN API design and recommendations for integrating PlanGEN into existing agent orchestration frameworks.

**API Quality Rating: 8/10** - Well-defined with room for improvement
**Orchestration Compatibility: 6.5/10** - Good for sync workflows, limited for async

---

## 1. API Definition Quality: ✅ Excellent

### Strengths

- **Clear Public API Surface**: Well-separated public API through `api.py`
  - `PlanGen` - Main entry point
  - `Algorithm` - Algorithm factory
  - `Visualization` - Visualization tools
  - `Verifiers` - Verifier factory
- **Protocol-Based Design**: Uses Python Protocols for extensibility
  - `ModelProtocol` - Custom model implementations
  - `VerifierProtocol` - Custom verifier implementations
- **Fluent Factory Methods**: Multiple ways to initialize

  ```python
  plangen = PlanGen.create()                              # Auto-detect
  plangen = PlanGen.with_openai(model_name="gpt-4o")     # Explicit
  plangen = PlanGen.with_bedrock(model_id="...")         # Alternative
  plangen = PlanGen.with_model(custom_model)             # Custom
  ```

- **Consistent Method Signatures**: All methods well-documented with type hints

### Known Limitations

- **Generic Return Types**: `solve()` returns `Dict[str, Any]` instead of typed structure
- **Encapsulation Issues**: Access to internal agents via `self._plangen.solution_agent` suggests incomplete abstraction
- **Limited Configuration**: No way to set default algorithms, verifiers, or behaviors at instance level

---

## 2. Orchestration Framework Compatibility

### Compatibility Matrix

| Framework | Rating | Primary Issue |
|-----------|--------|---------------|
| **LangGraph** | ⚠️ 6/10 | Uses LangGraph internally but doesn't expose it |
| **LangChain** | ⚠️ 5/10 | No native integration; can wrap as Tool |
| **CrewAI** | 🔴 3/10 | Expects async agents; PlanGen is sync-only |
| **AutoGen** | 🔴 2/10 | Designed for multi-turn; PlanGen is single-turn |
| **FastAPI/AsyncIO** | 🔴 2/10 | Blocks event loop without thread pool |
| **Pure Async** | 🔴 1/10 | No async methods available |

### The Core Problem: No Async Support ⚠️

This is the **biggest limitation** for modern orchestration:

```python
# This blocks the entire async event loop
async def my_orchestration():
    plangen = PlanGen.create()
    result = plangen.solve(problem)  # BLOCKS - no await available
    return result
```

**Workaround** (not ideal):

```python
from concurrent.futures import ThreadPoolExecutor

async def my_orchestration():
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()
    result = await loop.run_in_executor(
        executor,
        lambda: PlanGen.create().solve(problem)
    )
    return result
```

---

## 3. Integration Patterns

### ✅ Easy: Simple Synchronous Orchestrator

```python
def solve_step(input):
    plangen = PlanGen.create()
    result = plangen.solve(input["problem"])
    return result["selected_solution"]
```

### ✅ Moderate: LangChain Tool

```python
from langchain_core.tools import tool

@tool
def plangen_solver(problem: str) -> str:
    """Use PlanGEN to solve problems."""
    plangen = PlanGen.create()
    result = plangen.solve(problem)
    return result["selected_solution"]

# Works but blocks event loop if used with async agents
```

### ⚠️ Difficult: Custom Workflow Control

```python
# Current limitation: Can't easily intercept between steps

# Current best practice:
constraints = plangen.extract_constraints(problem)
# ... custom processing (not part of framework) ...
plan = plangen.generate_plan(problem, constraints)
# ... custom evaluation ...
feedback, score = plangen.verify_plan(problem, plan, constraints)

# Desired: Hook into workflow
# NOT CURRENTLY POSSIBLE - see recommendations below
```

### ❌ Very Difficult: Real-Time Progress Tracking

```python
# Current: No way to track progress during execution
result = plangen.solve(problem)  # Black box

# Desired (see recommendations):
plangen.on_step_complete(lambda step, result: print(f"{step}: {result}"))
result = await plangen.solve_async(problem)
```

---

## 4. Recommended Improvements

### Phase 1: Critical (1-2 weeks)

**1.1 Add Async Support**

```python
from typing import Optional

class PlanGen:
    async def solve_async(
        self,
        problem: str,
        algorithm: str = "default",
        verifier: Optional[VerifierProtocol] = None,
        **algorithm_params,
    ) -> Dict[str, Any]:
        """Async version of solve() for use in async orchestrators."""
        # Implementation would use asyncio for parallelization
```

**1.2 Add Callback System**

```python
from typing import Callable, Dict, Any

class PlanGen:
    def on_constraint_extracted(
        self,
        callback: Callable[[List[str]], None]
    ) -> None:
        """Register callback when constraints are extracted."""

    def on_solution_generated(
        self,
        callback: Callable[[str, int], None]  # plan, index
    ) -> None:
        """Register callback when solution is generated."""

    def on_verification_complete(
        self,
        callback: Callable[[str, float, str], None]  # plan, score, feedback
    ) -> None:
        """Register callback when verification is complete."""

    def on_solution_selected(
        self,
        callback: Callable[[str, float], None]  # solution, score
    ) -> None:
        """Register callback when final solution is selected."""
```

**1.3 Improve Type Definitions**

```python
from typing import TypedDict, List, Dict, Any

class SolveResult(TypedDict):
    """Type-safe result structure."""
    problem: str
    constraints: List[str]
    solutions: List[str]
    verification_results: List[Dict[str, Any]]
    selected_solution: str
    score: float
    metadata: Dict[str, Any]
```

### Phase 2: Important (1-2 months)

**2.1 Configuration Objects**

```python
from dataclasses import dataclass

@dataclass
class PlanGenConfig:
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    default_algorithm: str = "best_of_n"
    num_solutions: int = 3
    enable_logging: bool = False
    cache_enabled: bool = False

plangen = PlanGen.from_config(config)
```

**2.2 Expose Workflow Customization**

```python
class PlanGen:
    def get_workflow_graph(self) -> StateGraph:
        """Get the underlying LangGraph workflow.

        Allows advanced users to inspect or modify the workflow
        before execution.
        """
        return self._plangen.workflow
```

**2.3 Streaming Support**

```python
from typing import Iterator

class PlanGen:
    def solve_stream(
        self,
        problem: str,
        algorithm: str = "default",
        **kwargs,
    ) -> Iterator[Dict[str, Any]]:
        """Stream results as they become available.

        Yields intermediate results for real-time UI updates
        and progress tracking.
        """
```

### Phase 3: Nice to Have (2-3 months)

**3.1 Verifier Composition**

```python
class Verifiers:
    @staticmethod
    def combine(
        verifiers: List[VerifierProtocol],
        strategy: str = "average"  # or "weighted", "first_fail"
    ) -> VerifierProtocol:
        """Combine multiple verifiers."""
```

**3.2 Middleware/Interceptor System**

```python
def logging_middleware(step_name: str, input: Any, next: Callable) -> Any:
    """Example middleware for logging."""
    logger.info(f"Executing {step_name}")
    result = next(input)
    logger.info(f"Completed {step_name}")
    return result

plangen.add_middleware(logging_middleware)
```

**3.3 Result Caching**

```python
class PlanGen:
    def enable_cache(
        self,
        ttl: int = 3600,
        max_entries: int = 100
    ) -> None:
        """Enable result caching for identical problems."""
```

---

## 5. Integration Examples

### Example 1: Using with LangChain Agents (Improved)

```python
from langchain_core.tools import tool
from plangen import PlanGen

@tool
async def solve_with_plangen(problem: str) -> str:
    """Use PlanGEN to solve complex problems.

    This tool breaks down problems, generates solutions,
    and selects the best one.
    """
    plangen = PlanGen.create()

    # Track progress
    plangen.on_constraint_extracted(
        lambda c: print(f"Found {len(c)} constraints")
    )
    plangen.on_solution_generated(
        lambda p, i: print(f"Generated solution {i+1}")
    )

    # Execute asynchronously
    result = await plangen.solve_async(problem)
    return result["selected_solution"]
```

### Example 2: Custom Workflow in Orchestration

```python
from plangen import PlanGen
from langgraph.graph import StateGraph

# Get PlanGEN workflow
plangen = PlanGen.create()
planning_workflow = plangen.get_workflow_graph()

# Integrate into larger workflow
orchestration_graph = StateGraph(MyState)

# Add constraint extraction with custom pre-processing
orchestration_graph.add_node(
    "extract_and_validate",
    extract_and_validate_constraints
)

# Add the planning workflow
orchestration_graph.add_node(
    "planning",
    planning_workflow
)

# Add custom post-processing
orchestration_graph.add_node(
    "refine_solution",
    refine_solution
)

# Connect nodes
orchestration_graph.add_edge("extract_and_validate", "planning")
orchestration_graph.add_edge("planning", "refine_solution")
```

---

## 6. Migration Path for Users

### For Existing Code (No Breaking Changes)

The recommended improvements are **backward compatible**:

- New async methods alongside sync versions
- New callbacks are optional
- TypedDict is hint-only, doesn't affect runtime

### Migration Timeline

1. **Week 1-2**: Deprecation notices in docstrings
2. **Week 3-4**: Release v0.2.0 with new features
3. **Month 2**: Encourage migration through examples
4. **Month 3**: Consider deprecating old patterns in v0.3.0

---

## 7. Decision Matrix: When to Use PlanGEN

### Use PlanGEN When

✅ You need multi-step problem decomposition
✅ You want constraint extraction + solution generation + verification
✅ You're building synchronous systems
✅ You need multiple solution candidates
✅ You want custom verifiers for specific domains

### Don't Use PlanGEN When

❌ You need pure async/streaming LLM interaction
❌ You need real-time token streaming
❌ You require multi-turn conversations
❌ You need WebSocket connections or server-sent events
❌ You want fine-grained control over every LLM call

---

## 8. Feedback and Contributions

If you're integrating PlanGEN into a new framework, please share:

- Challenges you encounter
- Workarounds you develop
- Feature requests for better integration

For feature requests and roadmap discussions, see the [GitHub Issues](https://github.com/cajias/plangen/issues).
