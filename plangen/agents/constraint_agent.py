"""
Constraint agent for PlanGEN
"""

from typing import Dict, List, Any, Optional

from ..models import BaseModelInterface
from ..prompts import PromptManager

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