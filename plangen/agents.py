"""
Agent implementations for PlanGEN
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from .models import BaseModelInterface
from .prompts import PromptManager

class ConstraintAgent:
    """Agent for extracting constraints from problem statements."""
    
    def __init__(
        self, 
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ):
        """Initialize the constraint agent.
        
        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager
    
    def extract_constraints(self, problem: str) -> str:
        """Extract constraints from a problem statement.
        
        Args:
            problem: Problem statement
            
        Returns:
            Extracted constraints
        """
        system_message = self.prompt_manager.get_system_message("constraint")
        prompt = self.prompt_manager.get_prompt("constraint_extraction", problem=problem)
        
        return self.model.generate(prompt, system_message=system_message)


class SolutionAgent:
    """Agent for generating solutions based on constraints."""
    
    def __init__(
        self, 
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ):
        """Initialize the solution agent.
        
        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager
    
    def generate_solutions(
        self, 
        problem: str, 
        constraints: str, 
        num_solutions: int = 3
    ) -> List[str]:
        """Generate multiple solutions for a problem.
        
        Args:
            problem: Problem statement
            constraints: Extracted constraints
            num_solutions: Number of solutions to generate
            
        Returns:
            List of generated solutions
        """
        prompt = self.prompt_manager.get_prompt(
            "solution_generation", 
            problem=problem, 
            constraints=constraints
        )
        
        # Generate multiple solutions with different temperatures
        solutions = []
        temperatures = [0.7, 0.8, 0.9]  # Different temperatures for diversity
        
        for i in range(num_solutions):
            temp = temperatures[i % len(temperatures)]
            solution = self.model.generate(prompt, temperature=temp)
            solutions.append(solution)
        
        return solutions


class VerificationAgent:
    """Agent for verifying solutions against constraints."""
    
    def __init__(
        self, 
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ):
        """Initialize the verification agent.
        
        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager
    
    def verify_solutions(
        self, 
        solutions: List[str], 
        constraints: str
    ) -> List[str]:
        """Verify multiple solutions against constraints.
        
        Args:
            solutions: List of solutions to verify
            constraints: Extracted constraints
            
        Returns:
            List of verification results
        """
        system_message = self.prompt_manager.get_system_message("verification")
        
        verification_results = []
        for solution in solutions:
            prompt = self.prompt_manager.get_prompt(
                "solution_verification", 
                solution=solution, 
                constraints=constraints
            )
            
            result = self.model.generate(prompt, system_message=system_message)
            verification_results.append(result)
        
        return verification_results


class Solution(BaseModel):
    """Model for a solution and its verification."""
    
    text: str = Field(..., description="The solution text")
    verification: str = Field(..., description="Verification results for the solution")


class SelectionAgent:
    """Agent for selecting the best solution based on verification results."""
    
    def __init__(
        self, 
        model: BaseModelInterface,
        prompt_manager: PromptManager,
    ):
        """Initialize the selection agent.
        
        Args:
            model: Model interface for generating responses
            prompt_manager: Manager for prompt templates
        """
        self.model = model
        self.prompt_manager = prompt_manager
    
    def select_best_solution(
        self, 
        solutions: List[str], 
        verification_results: List[str]
    ) -> Dict[str, Any]:
        """Select the best solution based on verification results.
        
        Args:
            solutions: List of solutions
            verification_results: List of verification results
            
        Returns:
            Dictionary with the best solution and selection reasoning
        """
        system_message = self.prompt_manager.get_system_message("selection")
        
        # Prepare solution objects for the prompt
        solution_objects = [
            Solution(text=solution, verification=verification)
            for solution, verification in zip(solutions, verification_results)
        ]
        
        prompt = self.prompt_manager.get_prompt(
            "solution_selection", 
            solutions=solution_objects
        )
        
        selection_reasoning = self.model.generate(prompt, system_message=system_message)
        
        # Extract the selected solution index (assuming it's mentioned in the reasoning)
        # This is a simple heuristic; in practice, you might want a more robust approach
        selected_index = 0
        for i, solution in enumerate(solutions):
            if f"Solution {i+1}" in selection_reasoning and "best" in selection_reasoning.lower():
                selected_index = i
                break
        
        return {
            "selected_solution": solutions[selected_index],
            "selection_reasoning": selection_reasoning,
            "selected_index": selected_index,
        }