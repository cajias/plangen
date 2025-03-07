"""
REBASE algorithm for PlanGEN

REBASE: REward-BAlanced SEarch
This implementation follows the specifications in the PlanGEN paper.
"""

from typing import Dict, List, Optional, Tuple, Any
import heapq
import os
import jinja2

from .base_algorithm import BaseAlgorithm
from ..utils.llm_interface import LLMInterface

class REBASE(BaseAlgorithm):
    """Implementation of the REBASE algorithm as specified in the PlanGEN paper.
    
    REBASE (REward-BAlanced SEarch) is a tree search method that balances
    exploration and exploitation in the search space.
    """
    
    def __init__(
        self,
        max_depth: int = 5,
        max_width: int = 3,
        pruning_threshold: float = 0.5,
        **kwargs,
    ):
        """Initialize the REBASE algorithm.
        
        Args:
            max_depth: Maximum depth of the tree
            max_width: Maximum width (branching factor) at each level
            pruning_threshold: Threshold for pruning branches (0-1)
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        self.max_depth = max_depth
        self.max_width = max_width
        self.pruning_threshold = pruning_threshold
        
        # Load templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "rebase")
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the REBASE algorithm on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        formatted_constraints = "\n".join([f"- {constraint}" for constraint in constraints])
        
        # Initialize the root node
        root = {
            "steps": [],
            "score": 0,
            "depth": 0,
            "complete": False,
            "children": []
        }
        
        # Initialize tracking variables
        best_plan = None
        best_score = float('-inf')
        all_nodes = []  # Track all explored nodes for metadata
        
        # Priority queue for nodes to explore, ordered by score
        # Using negative score because heapq is a min-heap
        nodes_to_explore = [(-root["score"], 0, root)]  # (neg_score, node_id, node)
        node_counter = 1
        
        while nodes_to_explore and node_counter < 1000:  # Safety limit
            # Get the highest scoring node to explore
            _, _, current_node = heapq.heappop(nodes_to_explore)
            
            # Check if current plan is complete
            if self._is_complete(problem_statement, current_node["steps"]):
                current_node["complete"] = True
                plan_text = "\n".join(current_node["steps"])
                
                # Evaluate the complete plan
                feedback, score = self._verify_plan(
                    problem_statement,
                    constraints,
                    plan_text
                )
                
                # Update best plan if needed
                if score > best_score:
                    best_plan = plan_text
                    best_score = score
                
                # Add to explored nodes
                all_nodes.append({
                    "steps": current_node["steps"],
                    "score": score,
                    "depth": current_node["depth"],
                    "complete": True,
                    "feedback": feedback
                })
                
                # We found a complete solution, but continue exploring
                # other paths that might be better
                continue
            
            # Skip if we've reached max depth
            if current_node["depth"] >= self.max_depth:
                continue
            
            # Calculate dynamic width based on node's score
            # Higher scoring nodes get more children
            if current_node["score"] > 0:
                score_ratio = min(1.0, current_node["score"] / 100)
                dynamic_width = max(1, int(self.max_width * score_ratio))
            else:
                dynamic_width = 1  # Minimum exploration for low scoring paths
            
            # Generate and evaluate child nodes
            next_steps = self._generate_next_steps(
                problem_statement,
                current_node["steps"],
                dynamic_width
            )
            
            for next_step in next_steps:
                new_steps = current_node["steps"] + [next_step]
                new_plan = "\n".join(new_steps)
                
                # Evaluate the new plan
                feedback, score = self._evaluate_step(
                    problem_statement,
                    constraints,
                    formatted_constraints,
                    new_plan
                )
                
                # Create new node
                new_node = {
                    "steps": new_steps,
                    "score": score,
                    "depth": current_node["depth"] + 1,
                    "complete": False,
                    "feedback": feedback,
                    "children": []
                }
                
                # Add to explored nodes
                all_nodes.append({
                    "steps": new_steps,
                    "score": score,
                    "depth": current_node["depth"] + 1,
                    "complete": False,
                    "feedback": feedback
                })
                
                # Add to exploration queue with hierarchical pruning
                # Even low-scoring nodes get at least one child (as per paper)
                current_node["children"].append(new_node)
                heapq.heappush(nodes_to_explore, (-score, node_counter, new_node))
                node_counter += 1
        
        # If we haven't found a complete solution, use the best scoring plan
        if best_plan is None and all_nodes:
            best_node = max(all_nodes, key=lambda x: x["score"])
            best_plan = "\n".join(best_node["steps"])
            best_score = best_node["score"]
        
        # Prepare metadata
        metadata = {
            "algorithm": "REBASE",
            "max_depth": self.max_depth,
            "max_width": self.max_width,
            "pruning_threshold": self.pruning_threshold,
            "nodes_explored": len(all_nodes),
            "all_nodes": all_nodes,
            "constraints": constraints
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
        
        # Load the step template
        template = self.template_env.get_template("step.jinja")
        
        # Generate num_steps different next steps
        for i in range(num_steps):
            # Use slightly different temperature for diversity
            temperature = self.temperature + (i * 0.1)
            
            # Render the template
            prompt = template.render(
                problem_statement=problem_statement,
                intermediate_steps=intermediate_steps_text
            )
            
            # Generate the next step
            next_step = self.llm_interface.generate(
                prompt=prompt,
                temperature=temperature
            )
            
            # Clean up the response
            next_step = next_step.strip()
            
            # If the step starts with a number and period (like "1."), remove it
            if next_step and next_step[0].isdigit() and len(next_step) > 2 and next_step[1:3] in ['. ', ') ']:
                next_step = next_step[3:].strip()
            
            next_steps.append(next_step)
        
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
        # Load the reward template
        template = self.template_env.get_template("reward.jinja")
        
        # Render the template
        prompt = template.render(
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
        
        # Load the completion template
        template = self.template_env.get_template("completion.jinja")
        
        # Render the template
        prompt = template.render(
            problem_statement=problem_statement,
            intermediate_steps=intermediate_steps_text
        )
        
        # Generate the completion check
        response = self.llm_interface.generate(prompt=prompt)
        
        # Check if the response indicates completion
        return response.strip() == "1"