"""
Base Algorithm class for PlanGEN
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ..agents.constraint_agent import ConstraintAgent
from ..agents.verification_agent import VerificationAgent
from ..utils.llm_interface import LLMInterface
from ..visualization.observers import Observable


class BaseAlgorithm(ABC, Observable):
    """Base class for all PlanGEN algorithms."""

    def __init__(
        self,
        llm_interface: Optional[LLMInterface] = None,
        constraint_agent: Optional[ConstraintAgent] = None,
        verification_agent: Optional[VerificationAgent] = None,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        max_iterations: int = 5,
    ):
        """Initialize the base algorithm.

        Args:
            llm_interface: Optional LLM interface to use
            constraint_agent: Optional constraint agent to use
            verification_agent: Optional verification agent to use
            model_name: Name of the model to use if llm_interface is not provided
            temperature: Temperature for LLM generation
            max_iterations: Maximum number of iterations for the algorithm
        """
        # Initialize Observable
        Observable.__init__(self)

        self.llm_interface = llm_interface or LLMInterface(
            model_name=model_name,
            temperature=temperature,
        )

        self.constraint_agent = constraint_agent or ConstraintAgent(
            llm_interface=self.llm_interface,
        )

        self.verification_agent = verification_agent or VerificationAgent(
            llm_interface=self.llm_interface,
        )

        self.max_iterations = max_iterations
        self.temperature = temperature
        self.algorithm_name = self.__class__.__name__

        self.plan_generation_prompt_template = (
            "Create a detailed plan to solve the following problem. "
            "Your plan should be step-by-step, clear, and address all aspects of the problem.\n\n"
            "Problem statement:\n{problem_statement}\n\n"
            "Constraints to consider:\n{constraints}\n\n"
            "Your plan:"
        )

    @abstractmethod
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the algorithm on the given problem statement.

        Args:
            problem_statement: The problem statement to solve

        Returns:
            Tuple of (best_plan, best_score, metadata)

        Raises:
            ValueError: If the problem statement is empty
            RuntimeError: If there's an error during algorithm execution
        """
        pass

    def _generate_plan(
        self,
        problem_statement: str,
        constraints: List[str],
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a plan for the given problem statement and constraints.

        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints to consider
            temperature: Optional temperature override

        Returns:
            Generated plan
        """
        # Format constraints as a numbered list
        formatted_constraints = "\n".join(
            f"{i+1}. {constraint}" for i, constraint in enumerate(constraints)
        )

        prompt = self.plan_generation_prompt_template.format(
            problem_statement=problem_statement,
            constraints=formatted_constraints,
        )

        return self.llm_interface.generate(
            prompt=prompt,
            temperature=temperature or self.temperature,
        )

    def _verify_plan(
        self, problem_statement: str, constraints: List[str], plan: str
    ) -> Tuple[str, float]:
        """Verify a plan against constraints and provide a reward score.

        Args:
            problem_statement: The original problem statement
            constraints: List of constraints extracted by the constraint agent
            plan: The plan to verify

        Returns:
            Tuple of (feedback, score)
        """
        return self.verification_agent.run(problem_statement, constraints, plan)
