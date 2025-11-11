"""
REBASE algorithm for PlanGEN.

This module implements the REBASE algorithm, which uses a recursive refinement
approach to generate and improve plans. The algorithm supports domain-specific
verification and templates.

Example:
    ```python
    from plangen.algorithms import REBASE
    from plangen.examples.calendar import CalendarVerifier

    # Initialize with domain-specific verifier
    algorithm = REBASE(
        max_iterations=5,
        improvement_threshold=0.1,
        domain="calendar",
        verifier=CalendarVerifier()
    )

    # Run the algorithm
    best_plan, score, metadata = algorithm.run(problem_statement)
    ```
"""
from __future__ import annotations

from typing import Any

from plangen.utils.template_loader import TemplateLoader

from .base_algorithm import BaseAlgorithm


class REBASE(BaseAlgorithm):
    """Implementation of the REBASE algorithm.

    This algorithm uses recursive refinement to generate and improve plans through
    iterative feedback and revision.

    Attributes:
        max_iterations: Maximum number of refinement iterations
        improvement_threshold: Minimum score improvement to continue refining
        domain: Optional domain name for domain-specific templates
    """

    def __init__(
        self,
        max_iterations: int = 5,
        improvement_threshold: float = 0.1,
        domain: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize the REBASE algorithm.

        Args:
            max_iterations: Maximum number of refinement iterations
            improvement_threshold: Minimum score improvement to continue refining
            domain: Optional domain name for domain-specific templates
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        self.domain = domain

        # Initialize template loader
        self.template_loader = TemplateLoader()

    def run(self, problem_statement: str) -> tuple[str, float, dict[str, Any]]:
        """Run the REBASE algorithm on the given problem statement.

        Args:
            problem_statement: The problem statement to solve

        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        formatted_constraints = "\n".join(
            [f"- {constraint}" for constraint in constraints],
        )
        
        # Notify observers about algorithm start
        self.notify_observers(
            {
                "algorithm_type": "REBASE",
                "event": "algorithm_start",
                "problem_statement": problem_statement,
                "constraints": constraints,
            },
        )

        # Generate initial plan
        current_plan = self._generate_initial_plan(
            problem_statement, formatted_constraints,
        )
        current_feedback, current_score = self._verify_plan(
            problem_statement, constraints, current_plan,
        )

        # Track all iterations for metadata
        iterations = [
            {"plan": current_plan, "score": current_score, "feedback": current_feedback},
        ]
        
        # Notify observers about initial plan
        self.notify_observers(
            {
                "algorithm_type": "REBASE",
                "event": "initial_plan",
                "iteration": 0,
                "plan": current_plan,
                "score": current_score,
                "feedback": current_feedback,
            },
        )

        # Iteratively refine the plan
        for iteration in range(self.max_iterations):
            # Generate refined plan
            refined_plan = self._refine_plan(
                problem_statement, formatted_constraints, current_plan, current_feedback,
            )

            # Verify refined plan
            refined_feedback, refined_score = self._verify_plan(
                problem_statement, constraints, refined_plan,
            )

            # Track iteration
            iterations.append(
                {
                    "plan": refined_plan,
                    "score": refined_score,
                    "feedback": refined_feedback,
                },
            )
            
            # Notify observers about refined plan
            self.notify_observers(
                {
                    "algorithm_type": "REBASE",
                    "event": "plan_refinement",
                    "iteration": iteration + 1,
                    "plan": refined_plan,
                    "score": refined_score,
                    "feedback": refined_feedback,
                    "previous_score": current_score,
                    "improvement": refined_score - current_score,
                },
            )

            # Check if improvement is significant
            if refined_score <= current_score + self.improvement_threshold:
                # Notify observers about stopping due to insufficient improvement
                self.notify_observers(
                    {
                        "algorithm_type": "REBASE",
                        "event": "refinement_stopped",
                        "reason": "insufficient_improvement",
                        "improvement": refined_score - current_score,
                        "threshold": self.improvement_threshold,
                    },
                )
                break

            # Update current plan
            current_plan = refined_plan
            current_score = refined_score
            current_feedback = refined_feedback

        # Prepare metadata
        metadata = {
            "algorithm": "REBASE",
            "max_iterations": self.max_iterations,
            "improvement_threshold": self.improvement_threshold,
            "iterations": iterations,
            "constraints": constraints,
        }
        
        # Notify observers about algorithm completion
        self.notify_observers(
            {
                "algorithm_type": "REBASE",
                "event": "algorithm_complete",
                "best_plan": current_plan,
                "best_score": current_score,
                "total_iterations": len(iterations) - 1,
                "metadata": {
                    "max_iterations": self.max_iterations,
                    "improvement_threshold": self.improvement_threshold,
                },
            },
        )

        return current_plan, current_score, metadata

    def _generate_initial_plan(
        self, problem_statement: str, formatted_constraints: str,
    ) -> str:
        """Generate an initial plan using the initial plan template.

        Args:
            problem_statement: The problem statement to solve
            formatted_constraints: Formatted constraints string

        Returns:
            Initial plan string
        """
        # Get the template path
        template_path = self.template_loader.get_algorithm_template(
            algorithm="rebase", template_type="initial_plan", domain=self.domain,
        )

        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "constraints": formatted_constraints,
            },
        )

        # Generate the initial plan
        return self.llm_interface.generate(prompt=prompt).strip()

    def _refine_plan(
        self,
        problem_statement: str,
        formatted_constraints: str,
        current_plan: str,
        feedback: str,
    ) -> str:
        """Refine a plan using the refinement template.

        Args:
            problem_statement: The problem statement to solve
            formatted_constraints: Formatted constraints string
            current_plan: Current plan to refine
            feedback: Feedback on the current plan

        Returns:
            Refined plan string
        """
        # Get the template path
        template_path = self.template_loader.get_algorithm_template(
            algorithm="rebase", template_type="refinement", domain=self.domain,
        )

        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "constraints": formatted_constraints,
                "current_plan": current_plan,
                "feedback": feedback,
            },
        )

        # Generate the refined plan
        return self.llm_interface.generate(prompt=prompt).strip()

    def _verify_plan(
        self, problem_statement: str, constraints: list[str], plan: str,
    ) -> tuple[str, float]:
        """Verify a plan using the verification template.

        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints
            plan: The plan to verify

        Returns:
            Tuple of (feedback, score)
        """
        try:
            # Format constraints as a string
            formatted_constraints = "\n".join(
                [f"- {constraint}" for constraint in constraints],
            )

            # Get the template path
            template_path = self.template_loader.get_algorithm_template(
                algorithm="rebase", template_type="verification", domain=self.domain,
            )

            # Render the template
            prompt = self.template_loader.render_template(
                template_path=template_path,
                variables={
                    "problem_statement": problem_statement,
                    "constraints": formatted_constraints,
                    "plan": plan,
                },
            )

            # Generate the verification
            response = self.llm_interface.generate(
                prompt=prompt,
                temperature=0.1,  # Low temperature for consistent verification
            )

            # Extract the score from the response
            try:
                # Look for "Score: X" pattern
                score_line = [
                    line
                    for line in response.split("\n")
                    if line.strip().startswith("Score:")
                ]
                if score_line:
                    score_text = score_line[0].split("Score:")[1].strip()
                    score = float(score_text)
                else:
                    # Fallback: try to find any number in the response
                    import re

                    numbers = re.findall(r"\d+", response)
                    if numbers:
                        score = float(numbers[-1])  # Use the last number found
                    else:
                        score = 50  # Default score if no number found

                # Ensure score is in 0-100 range
                score = max(0, min(100, score))

                return response, score
            except Exception:
                # Return a default score if parsing fails
                return response, 50
        except Exception as e:
            msg = f"Error verifying plan: {e!s}"
            raise ValueError(msg)
