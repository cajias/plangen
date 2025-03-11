# PlanGEN Agents

## Current Implementation Status

Currently, the PlanGEN framework has two parallel agent implementations:

1. **Main Implementation** (in `plangen/agents.py`):
   - Used by `plangen.py` and the core workflow
   - Has a prompt-manager and model-based interface
   - Used when importing directly from plangen: `from plangen import ConstraintAgent`

2. **Package Implementation** (in `plangen/agents/*.py`):
   - Newer implementation with different interfaces
   - Has LLM-interface based design
   - Currently not used by core parts of the framework

For consistency, the `plangen/agents/__init__.py` file currently re-exports the main implementation classes from `plangen/agents.py`.

## Future Direction

These implementations will be unified in the future to provide a single, consistent interface. Until then, use whichever interface is most appropriate for your use case.

## Usage

```python
# These are identical:
from plangen import ConstraintAgent
from plangen.agents import ConstraintAgent
```