"""
Mixture of Algorithms for PlanGEN
"""

from typing import Dict, List, Optional, Tuple, Any

from .base_algorithm import BaseAlgorithm
from .best_of_n import BestOfN
from .tree_of_thought import TreeOfThought
from .rebase import REBASE
from ..agents.selection_agent import SelectionAgent
from ..utils.llm_interface import LLMInterface

class MixtureOfAlgorithms(BaseAlgorithm):
    """Implementation of the Mixture of Algorithms approach.
    
    This algorithm dynamically selects the best inference algorithm based on
    the problem's complexity and characteristics.
    """
    
    def __init__(
        self,
        selection_agent: Optional[SelectionAgent] = None,
        max_algorithm_switches: int = 2,
        **kwargs,
    ):
        """Initialize the Mixture of Algorithms approach.
        
        Args:
            selection_agent: Optional selection agent to use
            max_algorithm_switches: Maximum number of algorithm switches allowed
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        
        # Initialize the algorithms
        self.algorithms = {
            "Best of N": BestOfN(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
            ),
            "Tree of Thought": TreeOfThought(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
            ),
            "REBASE": REBASE(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
            ),
        }
        
        # Initialize the selection agent
        self.selection_agent = selection_agent or SelectionAgent(
            algorithm_names=list(self.algorithms.keys()),
            llm_interface=self.llm_interface,
        )
        
        self.max_algorithm_switches = max_algorithm_switches
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Mixture of Algorithms approach on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        
        # Track the best plan and score
        best_plan = None
        best_score = float('-inf')
        
        # Track algorithm usage and performance
        algorithm_history = []
        
        # Try different algorithms up to max_algorithm_switches + 1 times
        for i in range(self.max_algorithm_switches + 1):
            # Select the next algorithm to try
            algorithm_name = self.selection_agent.run(problem_statement)
            
            # Run the selected algorithm
            algorithm = self.algorithms[algorithm_name]
            plan, score, algo_metadata = algorithm.run(problem_statement)
            
            # Update the selection agent with the reward
            self.selection_agent.update_ucb(algorithm_name, score)
            
            # Track this algorithm's performance
            algorithm_history.append({
                "iteration": i,
                "algorithm": algorithm_name,
                "score": score,
                "plan": plan,
            })
            
            # Update the best plan if needed
            if score > best_score:
                best_plan = plan
                best_score = score
            
            # If we've found a good enough plan, stop early
            if score >= 80:  # Threshold for a good plan
                break
        
        # Prepare metadata
        metadata = {
            "algorithm": "Mixture of Algorithms",
            "max_algorithm_switches": self.max_algorithm_switches,
            "algorithm_history": algorithm_history,
            "constraints": constraints,
            "ucb_scores": self.selection_agent.ucb.get_ucb_scores() if hasattr(self.selection_agent, "ucb") else None,
        }
        
        return best_plan, best_score, metadata