"""
Agent implementations for PlanGEN

IMPORTANT: This module is deprecated and will be removed in a future version.
For backward compatibility, it re-exports the legacy agent classes from agents_legacy.py.

The recommended way to use agents is through the package structure in plangen/agents/*.
"""

import warnings

# Show deprecation warning
warnings.warn(
    "The agents.py module is deprecated and will be removed in a future version. "
    "Please use the package structure in plangen/agents/* instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export the legacy agent classes for backward compatibility
from .agents_legacy import (
    ConstraintAgent,
    SelectionAgent,
    SolutionAgent,
    VerificationAgent,
    Solution
)

__all__ = [
    "ConstraintAgent",
    "SolutionAgent",
    "VerificationAgent",
    "SelectionAgent",
    "Solution"
]
