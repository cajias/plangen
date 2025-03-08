"""
Mixture of Algorithms for PlanGEN.

This module implements the Mixture of Algorithms approach, which dynamically selects
the best inference algorithm based on the problem's complexity and characteristics.
The approach supports domain-specific templates and verification.

Example:
    ```python
    from plangen.algorithms import MixtureOfAlgorithms
    from plangen.examples.calendar import CalendarVerifier
    
    # Initialize with domain-specific verifier
    algorithm = MixtureOfAlgorithms(
        max_algorithm_switches=2,
        domain="calendar",
        verifier=CalendarVerifier()
    )
    
    # Run the algorithm
    best_plan, score, metadata = algorithm.run(problem_statement)
    ```
"""

from typing import Dict, List, Optional, Tuple, Any

from .base_algorithm import BaseAlgorithm
from .best_of_n import BestOfN
from .tree_of_thought import TreeOfThought
from .rebase import REBASE
from ..agents.selection_agent import SelectionAgent
from ..utils.llm_interface import LLMInterface
from ..utils.template_loader import TemplateLoader

class MixtureOfAlgorithms(BaseAlgorithm):
    """Implementation of the Mixture of Algorithms approach.
    
    This algorithm dynamically selects the best inference algorithm based on
    the problem's complexity and characteristics.
    
    Attributes:
        selection_agent: Agent for selecting algorithms
        algorithms: Dictionary of available algorithms
        max_algorithm_switches: Maximum number of algorithm switches allowed
        domain: Optional domain name for domain-specific templates
    """
    
    def __init__(
        self,
        selection_agent: Optional[SelectionAgent] = None,
        max_algorithm_switches: int = 2,
        domain: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the Mixture of Algorithms approach.
        
        Args:
            selection_agent: Optional selection agent to use
            max_algorithm_switches: Maximum number of algorithm switches allowed
            domain: Optional domain name for domain-specific templates
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        
        # Initialize the algorithms
        self.algorithms = {
            "Best of N": BestOfN(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
                domain=domain,
                **kwargs
            ),
            "Tree of Thought": TreeOfThought(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
                domain=domain,
                **kwargs
            ),
            "REBASE": REBASE(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
                domain=domain,
                **kwargs
            )
        }
        
        self.selection_agent = selection_agent or SelectionAgent(
            llm_interface=self.llm_interface
        )
        self.max_algorithm_switches = max_algorithm_switches
        self.domain = domain
        
        # Initialize template loader
        self.template_loader = TemplateLoader()
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Mixture of Algorithms approach on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        formatted_constraints = "\n".join([f"- {constraint}" for constraint in constraints])
        
        # Select initial algorithm
        current_algorithm_name = self._select_algorithm(problem_statement, constraints)
        current_algorithm = self.algorithms[current_algorithm_name]
        
        # Track algorithm switches
        algorithm_history = [current_algorithm_name]
        
        # Run initial algorithm
        current_plan, current_score, current_metadata = current_algorithm.run(problem_statement)
        
        # Track all iterations for metadata
        iterations = [{
            "algorithm": current_algorithm_name,
            "plan": current_plan,
            "score": current_score,
            "metadata": current_metadata
        }]
        
        # Iteratively switch algorithms if needed
        for _ in range(self.max_algorithm_switches):
            # Select next algorithm based on current results
            next_algorithm_name = self._select_next_algorithm(
                problem_statement,
                constraints,
                current_plan,
                current_score,
                current_algorithm_name
            )
            
            # If same algorithm selected, we're done
            if next_algorithm_name == current_algorithm_name:
                break
                
            # Switch to next algorithm
            current_algorithm_name = next_algorithm_name
            current_algorithm = self.algorithms[current_algorithm_name]
            algorithm_history.append(current_algorithm_name)
            
            # Run next algorithm
            next_plan, next_score, next_metadata = current_algorithm.run(problem_statement)
            
            # Track iteration
            iterations.append({
                "algorithm": current_algorithm_name,
                "plan": next_plan,
                "score": next_score,
                "metadata": next_metadata
            })
            
            # Keep the better plan
            if next_score > current_score:
                current_plan = next_plan
                current_score = next_score
                current_metadata = next_metadata
        
        # Prepare metadata
        metadata = {
            "algorithm": "Mixture of Algorithms",
            "max_algorithm_switches": self.max_algorithm_switches,
            "algorithm_history": algorithm_history,
            "iterations": iterations,
            "constraints": constraints
        }
        
        return current_plan, current_score, metadata
    
    def _select_algorithm(
        self,
        problem_statement: str,
        constraints: List[str]
    ) -> str:
        """Select an algorithm based on the problem statement and constraints.
        
        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints
            
        Returns:
            Name of the selected algorithm
        """
        # Get the template path
        template_path = self.template_loader.get_algorithm_template(
            algorithm="mixture_of_algorithms",
            template_type="algorithm_selection",
            domain=self.domain
        )
        
        # Format constraints as a string
        formatted_constraints = "\n".join([f"- {constraint}" for constraint in constraints])
        
        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "constraints": formatted_constraints,
                "available_algorithms": list(self.algorithms.keys())
            }
        )
        
        # Generate the algorithm selection
        response = self.llm_interface.generate(prompt=prompt)
        
        # Extract the algorithm name from the response
        for algorithm_name in self.algorithms.keys():
            if algorithm_name in response:
                return algorithm_name
        
        # Default to Best of N if no algorithm is found
        return "Best of N"
    
    def _select_next_algorithm(
        self,
        problem_statement: str,
        constraints: List[str],
        current_plan: str,
        current_score: float,
        current_algorithm: str
    ) -> str:
        """Select the next algorithm based on current results.
        
        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints
            current_plan: Current plan
            current_score: Current score
            current_algorithm: Current algorithm name
            
        Returns:
            Name of the next algorithm to try
        """
        # Get the template path
        template_path = self.template_loader.get_algorithm_template(
            algorithm="mixture_of_algorithms",
            template_type="algorithm_selection",
            domain=self.domain
        )
        
        # Format constraints as a string
        formatted_constraints = "\n".join([f"- {constraint}" for constraint in constraints])
        
        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "constraints": formatted_constraints,
                "available_algorithms": list(self.algorithms.keys()),
                "current_algorithm": current_algorithm,
                "current_plan": current_plan,
                "current_score": current_score
            }
        )
        
        # Generate the algorithm selection
        response = self.llm_interface.generate(prompt=prompt)
        
        # Extract the algorithm name from the response
        for algorithm_name in self.algorithms.keys():
            if algorithm_name in response and algorithm_name != current_algorithm:
                return algorithm_name
        
        # Default to current algorithm if no new algorithm is found
        return current_algorithm