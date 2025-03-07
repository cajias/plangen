"""
Verification package for PlanGEN.

This package provides domain-agnostic verification interfaces and domain-specific
verification strategies for validating solutions to different types of problems.
"""

from .base_verifier import BaseVerifier
from .verifier_factory import VerifierFactory
from .strategies.math_verifier import MathVerifier

__all__ = [
    'BaseVerifier',
    'VerifierFactory',
    'MathVerifier',
]