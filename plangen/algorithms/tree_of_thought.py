"""
Tree of Thought algorithm for PlanGEN

This implementation follows the specifications in the PlanGEN paper.
"""

from typing import Dict, List, Optional, Tuple, Any
import heapq
import copy

from .base_algorithm import BaseAlgorithm
from ..utils.llm_interface import LLMInterface

class TreeOfThought(BaseAlgorithm):
    """Implementation of the Tree of Thought algorithm as specified in the PlanGEN paper.
    
    This algorithm explores multiple reasoning paths in a tree structure, allowing for
    backtracking and exploration of alternatives.
    """
    
    def __init__(
        self,
        branching_factor: int = 3,
        max_depth: int = 5,
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
        
        # Define the step prompt template as specified in the paper
        self.step_prompt_template = (
            "You are an expert assistant for generating step-by-step plan to solve a given question using "
            "specified tools. Given the problem and any intermediate steps, output only the next step in "
            "the plan. Ensure that the next action helps in moving toward the correct plan to solve the "
            "given question. Do not provide the full plan. Keep responses concise, focusing solely on the "
            "immediate next step that is most effective in progressing toward the correct plan.\n\n"
            "<problem>\n{problem_statement}\n</problem>\n"
            "<intermediate_step>\n{intermediate_steps}\n</intermediate_step>"
        )
        
        # Define the step reward prompt template as specified in the paper
        self.step_reward_prompt_template = (
            "Provide a reward score between -100 and 100 for the quality of the provided plan steps, using "
            "strict evaluation standards. Ensure the reward reflects how effectively the plan contributes to "
            "progressing toward the correct solution.\n\n"
            "Problem Statement:\n{problem_statement}\n\n"
            "Plan:\n{plan}\n\n"
            "Consider the following constraints while evaluating:\n{constraints}\n\n"
            "Provide feedback in the following format:\n"
            "[Step-by-step reasoning for the reward score]\n"
            "Score: [Strictly provide an integer reward score between -100 and 100]"
        )
        
        # Define the completion prompt template as specified in the paper
        self.completion_prompt_template = (
            "You are an assistant tasked with verifying if the final, complete plan to solve the given question "
            "has been achieved within the intermediate steps. Output only '1' if the intermediate steps "
            "contain the full solution needed to solve the question. If the full plan has not yet been reached, "
            "output only '0'. Provide no additional commentary—return exclusively '1' or '0'.\n\n"
            "<problem>\n{problem_statement}\n</problem>\n"
            "<intermediate_step>\n{intermediate_steps}\n</intermediate_step>"
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
        formatted_constraints = "\n".join([f"- {constraint}" for constraint in constraints])
        
        # Initialize the tree with a root node
        root = {
            "steps": [],
            "score": 0,
            "depth": 0,
            "complete": False
        }
        
        # Initialize beam with the root node
        beam = [root]
        
        # Track the best plan and score
        best_plan = None
        best_score = float('-inf')
        
        # Track all explored paths for metadata
        all_paths = []
        
        # Explore the tree up to max_depth
        for depth in range(self.max_depth):
            next_beam = []
            
            for node in beam:
                # Check if the current plan is complete
                if self._is_complete(problem_statement, node["steps"]):
                    node["complete"] = True
                    
                    # Evaluate the complete plan
                    plan_text = "\n".join(node["steps"])
                    feedback, score = self._verify_plan(problem_statement, constraints, plan_text)
                    
                    # Update the best plan if needed
                    if score > best_score:
                        best_plan = plan_text
                        best_score = score
                    
                    # Add to all paths
                    all_paths.append({
                        "steps": node["steps"],
                        "score": score,
                        "feedback": feedback,
                        "depth": depth,
                        "complete": True
                    })
                    
                    # Add to next beam to keep this complete solution
                    next_beam.append(node)
                    continue
                
                # Generate branching_factor next steps
                next_steps = self._generate_next_steps(
                    problem_statement, 
                    node["steps"],
                    self.branching_factor
                )
                
                # Evaluate each next step
                for next_step in next_steps:
                    new_steps = node["steps"] + [next_step]
                    new_plan_text = "\n".join(new_steps)
                    
                    # Evaluate the new plan
                    step_feedback, step_score = self._evaluate_step(
                        problem_statement, 
                        constraints,
                        formatted_constraints,
                        new_plan_text
                    )
                    
                    # Create a new node
                    new_node = {
                        "steps": new_steps,
                        "score": step_score,
                        "depth": depth + 1,
                        "complete": False,
                        "feedback": step_feedback
                    }
                    
                    # Add to next beam
                    next_beam.append(new_node)
                    
                    # Add to all paths
                    all_paths.append({
                        "steps": new_steps,
                        "score": step_score,
                        "feedback": step_feedback,
                        "depth": depth + 1,
                        "complete": False
                    })
            
            # If we have any complete solutions, prioritize them
            complete_solutions = [node for node in next_beam if node["complete"]]
            if complete_solutions:
                # Sort complete solutions by score
                complete_solutions.sort(key=lambda x: x["score"], reverse=True)
                
                # Take the best complete solution
                best_complete = complete_solutions[0]
                best_plan = "\n".join(best_complete["steps"])
                best_score = best_complete["score"]
                
                # We can stop here as we found a complete solution
                break
            
            # Keep only the beam_width best plans based on score
            next_beam.sort(key=lambda x: x["score"], reverse=True)
            beam = next_beam[:self.beam_width]
            
            # If all paths in the beam are complete, we can stop
            if all(node["complete"] for node in beam):
                break
        
        # If we didn't find a complete solution, use the best scoring path
        if best_plan is None and beam:
            best_node = max(beam, key=lambda x: x["score"])
            best_plan = "\n".join(best_node["steps"])
            best_score = best_node["score"]
        
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
        intermediate_steps: List[str],
        num_steps: int
    ) -> List[str]:
        """Generate next steps for the current plan using the step prompt.
        
        Args:
            problem_statement: The problem statement to solve
            intermediate_steps: List of steps generated so far
            num_steps: Number of next steps to generate
            
        Returns:
            List of next steps
        """
        next_steps = []
        
        # Format intermediate steps as a string
        intermediate_steps_text = "\n".join(intermediate_steps)
        
        # Generate num_steps different next steps
        for i in range(num_steps):
            # Use slightly different temperature for diversity
            temperature = self.temperature + (i * 0.1)
            
            # Format the step prompt
            prompt = self.step_prompt_template.format(
                problem_statement=problem_statement,
                intermediate_steps=intermediate_steps_text
            )
            
            # Generate the next step
            next_step = self.llm_interface.generate(
                prompt=prompt,
                temperature=temperature
            )
            
            next_steps.append(next_step.strip())
        
        return next_steps
    
    def _evaluate_step(
        self, 
        problem_statement: str, 
        constraints: List[str],
        formatted_constraints: str,
        plan: str
    ) -> Tuple[str, float]:
        """Evaluate a plan step using the step reward prompt.
        
        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints
            formatted_constraints: Formatted constraints string
            plan: The plan to evaluate
            
        Returns:
            Tuple of (feedback, score)
        """
        # Format the step reward prompt
        prompt = self.step_reward_prompt_template.format(
            problem_statement=problem_statement,
            plan=plan,
            constraints=formatted_constraints
        )
        
        # Generate the evaluation
        response = self.llm_interface.generate(prompt=prompt)
        
        # Extract the score from the response
        score = -100  # Default to lowest score
        feedback = response
        
        # Look for "Score: X" pattern
        for line in response.split("\n"):
            if line.startswith("Score:"):
                try:
                    score_str = line.replace("Score:", "").strip()
                    score = float(score_str)
                except ValueError:
                    pass
        
        return feedback, score
    
    def _is_complete(self, problem_statement: str, steps: List[str]) -> bool:
        """Check if the current plan is complete using the completion prompt.
        
        Args:
            problem_statement: The problem statement to solve
            steps: List of steps generated so far
            
        Returns:
            True if the plan is complete, False otherwise
        """
        # If no steps, not complete
        if not steps:
            return False
        
        # Format intermediate steps as a string
        intermediate_steps_text = "\n".join(steps)
        
        # Format the completion prompt
        prompt = self.completion_prompt_template.format(
            problem_statement=problem_statement,
            intermediate_steps=intermediate_steps_text
        )
        
        # Generate the completion check
        response = self.llm_interface.generate(prompt=prompt)
        
        # Check if the response indicates completion
        return response.strip() == "1"