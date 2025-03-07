"""
Tree of Thought algorithm for PlanGEN
"""

from typing import Dict, List, Optional, Tuple, Any
import heapq

from .base_algorithm import BaseAlgorithm
from ..utils.llm_interface import LLMInterface

class TreeOfThought(BaseAlgorithm):
    """Implementation of the Tree of Thought algorithm.
    
    This algorithm explores multiple reasoning paths in a tree structure, allowing for
    backtracking and exploration of alternatives.
    """
    
    def __init__(
        self,
        branching_factor: int = 3,
        max_depth: int = 3,
        beam_width: int = 2,
        **kwargs,
    ):
        """Initialize the Tree of Thought algorithm.
        
        Args:
            branching_factor: Number of branches to explore at each node
            max_depth: Maximum depth of the tree
            beam_width: Number of paths to keep at each level
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        self.branching_factor = branching_factor
        self.max_depth = max_depth
        self.beam_width = beam_width
        
        self.step_generation_prompt_template = (
            "I'm solving this problem step by step:\n\n"
            "Problem statement:\n{problem_statement}\n\n"
            "Constraints to consider:\n{constraints}\n\n"
            "Current plan so far:\n{current_plan}\n\n"
            "Generate {branching_factor} different possible next steps to continue this plan. "
            "Each step should be a logical continuation of the current plan and help address "
            "the problem. Make the steps diverse and explore different approaches.\n\n"
            "Next steps (provide exactly {branching_factor} numbered options):"
        )
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Tree of Thought algorithm on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        
        # Start with an empty plan
        initial_plan = "I'll solve this problem step by step:"
        
        # Initialize beam with the initial plan
        beam = [(0, initial_plan)]  # (score, plan)
        
        # Track the best plan and score
        best_plan = initial_plan
        best_score = float('-inf')
        
        # Track all explored paths for metadata
        all_paths = []
        
        # Explore the tree up to max_depth
        for depth in range(self.max_depth):
            next_beam = []
            
            for _, current_plan in beam:
                # Generate branching_factor next steps
                next_steps = self._generate_next_steps(
                    problem_statement, 
                    constraints, 
                    current_plan,
                )
                
                # Evaluate each next step
                for next_step in next_steps:
                    new_plan = f"{current_plan}\n\n{next_step}"
                    
                    # Verify the new plan
                    feedback, score = self._verify_plan(
                        problem_statement, 
                        constraints, 
                        new_plan,
                    )
                    
                    # Update the best plan if needed
                    if score > best_score:
                        best_plan = new_plan
                        best_score = score
                    
                    # Add to next beam
                    next_beam.append((score, new_plan))
                    
                    # Track this path
                    all_paths.append({
                        "plan": new_plan,
                        "score": score,
                        "feedback": feedback,
                        "depth": depth + 1,
                    })
            
            # Keep only the beam_width best plans
            beam = heapq.nlargest(self.beam_width, next_beam, key=lambda x: x[0])
        
        # Prepare metadata
        metadata = {
            "algorithm": "Tree of Thought",
            "branching_factor": self.branching_factor,
            "max_depth": self.max_depth,
            "beam_width": self.beam_width,
            "all_paths": all_paths,
            "constraints": constraints,
        }
        
        return best_plan, best_score, metadata
    
    def _generate_next_steps(
        self, 
        problem_statement: str, 
        constraints: List[str], 
        current_plan: str,
    ) -> List[str]:
        """Generate next steps for the current plan.
        
        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints to consider
            current_plan: The current plan
            
        Returns:
            List of next steps
        """
        # Format constraints as a numbered list
        formatted_constraints = "\n".join(
            f"{i+1}. {constraint}" for i, constraint in enumerate(constraints)
        )
        
        prompt = self.step_generation_prompt_template.format(
            problem_statement=problem_statement,
            constraints=formatted_constraints,
            current_plan=current_plan,
            branching_factor=self.branching_factor,
        )
        
        response = self.llm_interface.generate(prompt=prompt)
        
        # Parse the response to extract the next steps
        next_steps = []
        current_step = ""
        
        for line in response.split("\n"):
            line = line.strip()
            
            # Check if this line starts a new step
            if line and line[0].isdigit() and "." in line[:3]:
                if current_step:
                    next_steps.append(current_step.strip())
                current_step = line
            else:
                current_step += "\n" + line
        
        # Add the last step
        if current_step:
            next_steps.append(current_step.strip())
        
        # Ensure we have exactly branching_factor steps
        if len(next_steps) > self.branching_factor:
            next_steps = next_steps[:self.branching_factor]
        
        # If we have fewer steps than expected, generate some more
        while len(next_steps) < self.branching_factor:
            next_steps.append(f"{len(next_steps) + 1}. Continue by analyzing the problem further...")
        
        return next_steps