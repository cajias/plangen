"""
PlanGEN: A multi-agent framework for generating planning and reasoning trajectories

This framework implements the PlanGEN workflow described in the paper
"PlanGEN: Generative Planning with Large Language Models".
"""

__version__ = "0.1.0"

# Import public API classes - the recommended interface for users
from .api import Algorithm, PlanGen, Verifiers, Visualization
from .plangen import PlanGEN
from .visualization import (
    GraphRenderer,
    Observable,
    PlanObserver,
)

# Import agent classes
from .agents import (
    ConstraintAgent,
    SelectionAgent,
    SolutionAgent,
    VerificationAgent,
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
