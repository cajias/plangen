# PlanGEN Agents

This directory contains the agent implementations for the PlanGEN framework. These are the modern implementations that should be used for new code.

## Overview

The agents directory contains the following files:

- `__init__.py`: Re-exports the agent classes from the individual modules
- `base_agent.py`: Contains the `BaseAgent` class that all agents inherit from
- `constraint_agent.py`: Contains the `ConstraintAgent` class for extracting constraints from problem statements
- `selection_agent.py`: Contains the `SelectionAgent` class for selecting the best solution
- `solution_agent.py`: Contains the `SolutionAgent` class for generating solutions
- `verification_agent.py`: Contains the `VerificationAgent` class for verifying solutions

## Usage

```python
from plangen.agents import ConstraintAgent, SelectionAgent, SolutionAgent, VerificationAgent
```

## Legacy APIs

For backward compatibility, you can still use the legacy agent classes from the `agents.py` module:

```python
from plangen import ConstraintAgent, SelectionAgent, SolutionAgent, VerificationAgent
```

However, this approach is deprecated and will be removed in a future version. The legacy implementation can be found in the `plangen/agents_legacy.py` file.