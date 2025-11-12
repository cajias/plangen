"""PlanGEN: A multi-agent framework for generating planning and reasoning trajectories.

This framework implements the PlanGEN workflow described in the paper
"PlanGEN: Generative Planning with Large Language Models".
"""

__version__ = "0.1.0"

# Import public API classes - the recommended interface for users
# Import agent classes
from .agents import (ConstraintAgent, SelectionAgent, SolutionAgent,
                     VerificationAgent)
from .api import Algorithm, PlanGen, Verifiers, Visualization
from .plangen import PlanGEN
from .types import AlgorithmResult, PlanResult, SolveResult, VerificationResult
from .visualization import GraphRenderer, Observable, PlanObserver

__all__ = [
    "Algorithm",
    "AlgorithmResult",
    "ConstraintAgent",
    "GraphRenderer",
    "Observable",
    # Legacy classes (for backward compatibility)
    "PlanGEN",
    # Public API (recommended)
    "PlanGen",
    "PlanObserver",
    "PlanResult",
    "SelectionAgent",
    "SolutionAgent",
    "SolveResult",
    "VerificationAgent",
    "VerificationResult",
    "Verifiers",
    "Visualization",
]
