"""
Tree of Thought algorithm for PlanGEN.

This module implements the Tree of Thought algorithm, which explores multiple reasoning
paths in a tree structure, allowing for backtracking and exploration of alternatives.
The algorithm supports domain-specific verification and templates.

Example:
    ```python
    from plangen.algorithms import TreeOfThought
    from plangen.examples.calendar import CalendarVerifier

    # Initialize with domain-specific verifier
    algorithm = TreeOfThought(
        branching_factor=3,
        max_depth=5,
        beam_width=2,
        domain="calendar",
        verifier=CalendarVerifier()
    )

    # Run the algorithm
    best_plan, score, metadata = algorithm.run(problem_statement)
    ```
"""

import copy
import heapq
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..utils.llm_interface import LLMInterface
from ..utils.template_loader import TemplateLoader
from ..verification import BaseVerifier
from .base_algorithm import BaseAlgorithm


class TreeOfThought(BaseAlgorithm):
    """Implementation of the Tree of Thought algorithm as specified in the PlanGEN paper.

    This algorithm explores multiple reasoning paths in a tree structure, allowing for
    backtracking and exploration of alternatives.

    Attributes:
        branching_factor: Number of branches to explore at each node
        max_depth: Maximum depth of the tree
        beam_width: Number of paths to keep at each level
        domain: Optional domain name for domain-specific templates
    """

    def __init__(
        self,
        branching_factor: int = 3,
        max_depth: int = 5,
        beam_width: int = 2,
        domain: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the Tree of Thought algorithm.

        Args:
            branching_factor: Number of branches to explore at each node
            max_depth: Maximum depth of the tree
            beam_width: Number of paths to keep at each level
            domain: Optional domain name for domain-specific templates and verification
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        self.branching_factor = branching_factor
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.domain = domain

        # Initialize template loader
        self.template_loader = TemplateLoader()

    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Tree of Thought algorithm on the given problem statement.

        Args:
            problem_statement: The problem statement to solve

        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        formatted_constraints = "\n".join(
            [f"- {constraint}" for constraint in constraints]
        )

        # Initialize the tree with a root node
        root = {"id": "root", "steps": [], "score": 0, "depth": 0, "complete": False}

        # Initialize beam with the root node
        beam = [root]

        # Track the best plan and score
        best_plan = None
        best_score = float("-inf")

        # Track all explored paths for metadata
        all_paths = []

        # Notify observers about the algorithm start
        self.notify_observers(
            {
                "algorithm_type": "TreeOfThought",
                "event": "algorithm_start",
                "problem_statement": problem_statement,
                "constraints": constraints,
                "new_nodes": [root],
            }
        )

        # Explore the tree up to max_depth
        for depth in range(self.max_depth):
            next_beam = []
            depth_nodes = []  # Collect nodes at this depth for visualization

            for node in beam:
                node_id = node.get("id", f"node_{id(node)}")

                # Check if the current plan is complete
                if self._is_complete(problem_statement, node["steps"]):
                    node["complete"] = True

                    # Evaluate the complete plan
                    plan_text = "\n".join(node["steps"])
                    feedback, score = self._verify_plan(
                        problem_statement, constraints, plan_text
                    )

                    # Update the best plan if needed
                    if score > best_score:
                        best_plan = plan_text
                        best_score = score

                    # Add to all paths
                    path_info = {
                        "id": f"complete_{node_id}_{depth}",
                        "parent_id": node_id,
                        "steps": node["steps"],
                        "score": score,
                        "feedback": feedback,
                        "depth": depth,
                        "complete": True,
                    }
                    all_paths.append(path_info)
                    depth_nodes.append(path_info)

                    # Add to next beam to keep this complete solution
                    node["score"] = score  # Update with actual score
                    next_beam.append(node)
                    continue

                # Generate branching_factor next steps
                next_steps = self._generate_next_steps(
                    problem_statement, node["steps"], self.branching_factor
                )

                # Evaluate each next step
                for i, next_step in enumerate(next_steps):
                    new_steps = node["steps"] + [next_step]
                    new_plan_text = "\n".join(new_steps)

                    # Evaluate the new plan
                    step_feedback, step_score = self._evaluate_step(
                        problem_statement,
                        constraints,
                        formatted_constraints,
                        new_plan_text,
                    )

                    # Create a new node
                    new_node_id = f"node_{node_id}_{depth}_{i}"
                    new_node = {
                        "id": new_node_id,
                        "parent_id": node_id,
                        "steps": new_steps,
                        "score": step_score,
                        "depth": depth + 1,
                        "complete": False,
                        "feedback": step_feedback,
                    }

                    # Add to next beam
                    next_beam.append(new_node)

                    # Add to all paths and depth nodes
                    all_paths.append(new_node)
                    depth_nodes.append(new_node)

            # Notify observers about the new depth exploration
            self.notify_observers(
                {
                    "algorithm_type": "TreeOfThought",
                    "event": "depth_exploration",
                    "depth": depth,
                    "new_nodes": depth_nodes,
                }
            )

            # If we have any complete solutions, prioritize them
            complete_solutions = [node for node in next_beam if node["complete"]]
            if complete_solutions:
                # Sort complete solutions by score
                complete_solutions.sort(key=lambda x: x["score"], reverse=True)

                # Take the best complete solution
                best_complete = complete_solutions[0]
                best_plan = "\n".join(best_complete["steps"])
                best_score = best_complete["score"]

                # Notify observers about the completion
                self.notify_observers(
                    {
                        "algorithm_type": "TreeOfThought",
                        "event": "complete_solution_found",
                        "solution": best_complete,
                    }
                )

                # We can stop here as we found a complete solution
                break

            # Keep only the beam_width best plans based on score
            next_beam.sort(key=lambda x: x["score"], reverse=True)
            beam = next_beam[: self.beam_width]

            # Notify observers about the beam update
            self.notify_observers(
                {
                    "algorithm_type": "TreeOfThought",
                    "event": "beam_update",
                    "depth": depth,
                    "beam": beam,
                }
            )

            # If all paths in the beam are complete, we can stop
            if all(node["complete"] for node in beam):
                break

        # If we didn't find a complete solution, use the best scoring path
        if best_plan is None and beam:
            best_node = max(beam, key=lambda x: x["score"])
            best_plan = "\n".join(best_node["steps"])
            best_score = best_node["score"]

            # Notify observers about the best incomplete solution
            self.notify_observers(
                {
                    "algorithm_type": "TreeOfThought",
                    "event": "incomplete_solution_selected",
                    "solution": best_node,
                }
            )

        # Prepare metadata
        metadata = {
            "algorithm": "Tree of Thought",
            "branching_factor": self.branching_factor,
            "max_depth": self.max_depth,
            "beam_width": self.beam_width,
            "all_paths": all_paths,
            "constraints": constraints,
        }

        # Notify observers about the algorithm completion
        self.notify_observers(
            {
                "algorithm_type": "TreeOfThought",
                "event": "algorithm_complete",
                "best_plan": best_plan,
                "best_score": best_score,
                "metadata": {
                    "branching_factor": self.branching_factor,
                    "max_depth": self.max_depth,
                    "beam_width": self.beam_width,
                    "total_paths": len(all_paths),
                },
            }
        )

        return best_plan, best_score, metadata

    def _generate_next_steps(
        self, problem_statement: str, intermediate_steps: List[str], num_steps: int
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

        # Get the appropriate template
        template_path = self.template_loader.get_algorithm_template(
            algorithm="tree_of_thought", template_type="step", domain=self.domain
        )

        # Generate num_steps different next steps
        for i in range(num_steps):
            # Use slightly different temperature for diversity
            temperature = self.temperature + (i * 0.1)

            # Render the template
            prompt = self.template_loader.render_template(
                template_path=template_path,
                variables={
                    "problem_statement": problem_statement,
                    "intermediate_steps": intermediate_steps_text,
                },
            )

            # Generate the next step
            next_step = self.llm_interface.generate(
                prompt=prompt, temperature=temperature
            )

            next_steps.append(next_step.strip())

        return next_steps

    def _evaluate_step(
        self,
        problem_statement: str,
        constraints: List[str],
        formatted_constraints: str,
        plan: str,
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
        # Get the appropriate template
        template_path = self.template_loader.get_algorithm_template(
            algorithm="tree_of_thought", template_type="reward", domain=self.domain
        )

        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "plan": plan,
                "constraints": formatted_constraints,
            },
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

        # Get the appropriate template
        template_path = self.template_loader.get_algorithm_template(
            algorithm="tree_of_thought", template_type="completion", domain=self.domain
        )

        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "intermediate_steps": intermediate_steps_text,
            },
        )

        # Generate the completion check
        response = self.llm_interface.generate(prompt=prompt)

        # Check if the response indicates completion
        return response.strip() == "1"
