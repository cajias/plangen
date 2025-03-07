"""
Best of N algorithm for PlanGEN
"""

from typing import Dict, List, Optional, Tuple, Any

from .base_algorithm import BaseAlgorithm
from ..utils.llm_interface import LLMInterface

class BestOfN(BaseAlgorithm):
    """Implementation of the Best of N algorithm.
    
    This algorithm generates N independent plans and selects the best one based on
    verification scores.
    """
    
    def __init__(
        self,
        n_plans: int = 3,
        **kwargs,
    ):
        """Initialize the Best of N algorithm.
        
        Args:
            n_plans: Number of plans to generate
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        self.n_plans = n_plans
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Best of N algorithm on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        
        # Generate and evaluate N plans
        plans = []
        scores = []
        feedbacks = []
        
        for i in range(self.n_plans):
            # Generate plan with slightly different temperature for diversity
            temperature = self.temperature + (i * 0.1)
            plan = self._generate_plan(
                problem_statement, 
                constraints,
                temperature=temperature,
            )
            
            # Verify plan
            feedback, score = self._verify_plan(problem_statement, constraints, plan)
            
            plans.append(plan)
            scores.append(score)
            feedbacks.append(feedback)
        
        # Find the best plan
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
        best_plan = plans[best_idx]
        best_score = scores[best_idx]
        
        # Prepare metadata
        metadata = {
            "algorithm": "Best of N",
            "n_plans": self.n_plans,
            "all_scores": scores,
            "all_feedbacks": feedbacks,
            "constraints": constraints,
        }
        
        return best_plan, best_score, metadata