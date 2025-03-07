"""
Constraint agent for PlanGEN
"""

from typing import Dict, List, Any, Optional

class ConstraintAgent:
    """Agent for extracting constraints from problem statements."""
    
    def __init__(
        self, 
        llm_interface=None,
    ):
        """Initialize the constraint agent.
        
        Args:
            llm_interface: LLM interface for generating responses
        """
        self.llm_interface = llm_interface
        
        self.constraint_prompt_template = (
            "You are an expert in understanding an input problem and generating set of constraints. "
            "Analyze the input problem and extract all relevant instance-specific constraints and "
            "contextual details necessary for accurate and feasible planning.\n\n"
            "These constraints may include:\n"
            "- Time constraints (deadlines, durations, etc.)\n"
            "- Resource constraints (availability, capacity, etc.)\n"
            "- Dependency constraints (prerequisites, etc.)\n"
            "- Logical constraints (rules, conditions, etc.)\n"
            "- Physical constraints (distances, locations, etc.)\n\n"
            "Input Problem: {problem_statement}\n\n"
            "Output ONLY a numbered list of specific constraints, one per line. Be comprehensive but concise."
        )
    
    def run(self, problem_statement: str) -> List[str]:
        """Extract constraints from a problem statement.
        
        Args:
            problem_statement: Problem statement
            
        Returns:
            List of extracted constraints
        """
        prompt = self.constraint_prompt_template.format(
            problem_statement=problem_statement
        )
        
        response = self.llm_interface.generate(prompt=prompt)
        
        # Parse the response to extract the constraints
        constraints = []
        for line in response.split("\n"):
            line = line.strip()
            
            # Check if this line starts with a number (like "1." or "1)")
            if line and (
                (line[0].isdigit() and len(line) > 1 and line[1] in [".", ")", ":"]) or
                (line.startswith("- "))
            ):
                # Remove the numbering/bullet and any leading/trailing whitespace
                constraint = line
                if line[0].isdigit():
                    constraint = line[2:].strip()
                elif line.startswith("- "):
                    constraint = line[2:].strip()
                
                constraints.append(constraint)
        
        return constraints