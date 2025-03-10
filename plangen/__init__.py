"""
PlanGEN: A multi-agent framework for generating planning and reasoning trajectories

This framework implements the PlanGEN workflow described in the paper
"PlanGEN: Generative Planning with Large Language Models".
"""

__version__ = "0.1.0"

# Import public API classes - the recommended interface for users
from .api import PlanGen, Algorithm, Visualization, Verifiers

# Import original classes for backward compatibility
from .agents import (
    ConstraintAgent,
    SelectionAgent,
    SolutionAgent,
    VerificationAgent,
)
from .plangen import PlanGEN
from .visualization import (
    GraphRenderer,
    Observable,
    PlanObserver,
)

__all__ = [
    # Public API (recommended)
    "PlanGen",
    "Algorithm",
    "Visualization",
    "Verifiers",
    # Legacy classes (for backward compatibility)
    "PlanGEN",
    "ConstraintAgent",
    "SolutionAgent",
    "VerificationAgent",
    "SelectionAgent",
    "GraphRenderer",
    "PlanObserver",
    "Observable",
]
