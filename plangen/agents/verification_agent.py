"""
Verification agent for PlanGEN.
"""

from typing import Dict, List, Optional, Tuple, Any

from ..utils.llm_interface import LLMInterface
from ..verification import BaseVerifier, VerifierFactory


class VerificationAgent:
    """Agent for verifying plans and solutions."""
    
    def __init__(
        self, 
        llm_interface: LLMInterface,
        verifier: Optional[BaseVerifier] = None
    ):
        """Initialize the verification agent.
        
        Args:
            llm_interface: LLM interface for generating responses
            verifier: Optional specific verifier to use. If None, will auto-detect.
        """
        self.llm_interface = llm_interface
        self.verifier = verifier
        self.verifier_factory = VerifierFactory()
    
    def run(
        self, 
        problem_statement: str,
        constraints: List[str],
        plan: str,
    ) -> Tuple[str, float]:
        """Verify a plan against constraints.
        
        Args:
            problem_statement: Original problem statement
            constraints: List of constraints
            plan: Plan to verify
            
        Returns:
            Tuple of (feedback, score)
        """
        # Get appropriate verifier
        verifier = self.verifier or self.verifier_factory.get_verifier(problem_statement)
        
        # Extract domain-specific constraints
        domain_constraints = verifier.extract_domain_constraints(problem_statement, constraints)
        all_constraints = constraints + domain_constraints
        
        # Verify the solution
        results = verifier.verify_solution(problem_statement, plan, all_constraints)
        
        # Format feedback
        feedback = f"Verification: {'PASS' if results['is_valid'] else 'FAIL'}\n"
        feedback += f"Reason: {results['reason']}\n"
        feedback += f"Score: {results['score']}"
        
        return feedback, float(results['score'])