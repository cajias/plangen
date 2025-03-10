"""
Best of N algorithm for PlanGEN.

This module implements the Best of N algorithm, which generates multiple candidate
solutions and selects the best one based on verification scores. The algorithm
supports various sampling strategies and can be configured for different problem
domains.

Example:
    ```python
    from plangen.algorithms import BestOfN
    from plangen.examples.calendar import CalendarVerifier

    # Initialize with domain-specific verifier
    algorithm = BestOfN(
        n_plans=5,
        sampling_strategy="diverse",
        verifier=CalendarVerifier(),
        parallel=True
    )

    # Run the algorithm
    best_plan, score, metadata = algorithm.run(problem_statement)
    ```
"""

import concurrent.futures
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from ..utils.llm_interface import LLMInterface
from ..utils.template_loader import TemplateError, TemplateLoader
from ..verification import BaseVerifier
from .base_algorithm import BaseAlgorithm


class BestOfN(BaseAlgorithm):
    """Implementation of the Best of N algorithm.

    This algorithm generates N independent plans and selects the best one based on
    verification scores. It supports different sampling strategies and can be
    configured for specific problem domains through custom verifiers.

    Attributes:
        n_plans: Number of plans to generate
        sampling_strategy: Strategy for generating diverse plans
        parallel: Whether to generate plans in parallel
        min_similarity: Minimum similarity threshold for diverse sampling
        max_retries: Maximum number of retries for diverse sampling
        domain: Optional domain name for domain-specific templates
    """

    SAMPLING_STRATEGIES = ["basic", "diverse", "adaptive"]

    def __init__(
        self,
        n_plans: int = 3,
        sampling_strategy: str = "basic",
        parallel: bool = False,
        min_similarity: float = 0.3,
        max_retries: int = 5,
        domain: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the Best of N algorithm.

        Args:
            n_plans: Number of plans to generate
            sampling_strategy: Strategy for plan generation. Options:
                - "basic": Simple independent sampling
                - "diverse": Enforce diversity between plans
                - "adaptive": Adjust sampling based on feedback
            parallel: Whether to generate plans in parallel
            min_similarity: Minimum similarity threshold for diverse sampling
            max_retries: Maximum number of retries for diverse sampling
            domain: Optional domain name for domain-specific templates
            **kwargs: Additional arguments passed to BaseAlgorithm

        Raises:
            ValueError: If sampling_strategy is not recognized
        """
        super().__init__(**kwargs)

        if sampling_strategy not in self.SAMPLING_STRATEGIES:
            raise ValueError(
                f"Unknown sampling strategy: {sampling_strategy}. "
                f"Must be one of {self.SAMPLING_STRATEGIES}"
            )

        self.n_plans = n_plans
        self.sampling_strategy = sampling_strategy
        self.parallel = parallel
        self.min_similarity = min_similarity
        self.max_retries = max_retries
        self.domain = domain

        # Initialize template loader
        self.template_loader = TemplateLoader()

    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Best of N algorithm on the given problem statement.

        Args:
            problem_statement: The problem statement to solve

        Returns:
            Tuple of (best_plan, best_score, metadata)

        Raises:
            ValueError: If the problem statement is empty
            RuntimeError: If there's an error during algorithm execution
        """
        if not problem_statement.strip():
            raise ValueError("Problem statement cannot be empty")

        try:
            # Extract constraints
            constraints = self.constraint_agent.run(problem_statement)

            # Select sampling function based on strategy
            if self.sampling_strategy == "diverse":
                sample_fn = self._diverse_sampling
            elif self.sampling_strategy == "adaptive":
                sample_fn = self._adaptive_sampling
            else:
                sample_fn = self._basic_sampling

            # Generate and evaluate plans
            if self.parallel:
                results = self._parallel_generate(
                    problem_statement, constraints, sample_fn
                )
            else:
                results = self._sequential_generate(
                    problem_statement, constraints, sample_fn
                )

            plans, scores, feedbacks = zip(*results)

            # Find the best plan
            best_idx = max(range(len(scores)), key=lambda i: scores[i])
            best_plan = plans[best_idx]
            best_score = scores[best_idx]

            # Prepare metadata
            metadata = {
                "algorithm": "Best of N",
                "n_plans": self.n_plans,
                "sampling_strategy": self.sampling_strategy,
                "parallel": self.parallel,
                "all_scores": scores,
                "all_feedbacks": feedbacks,
                "constraints": constraints,
                "best_index": best_idx,
                "mean_score": np.mean(scores),
                "std_score": np.std(scores),
            }

            return best_plan, best_score, metadata

        except Exception as e:
            raise RuntimeError(f"Error running Best of N algorithm: {str(e)}")

    def _sequential_generate(
        self, problem_statement: str, constraints: List[str], sample_fn: Callable
    ) -> List[Tuple[str, float, str]]:
        """Generate plans sequentially.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            sample_fn: Sampling function to use

        Returns:
            List of (plan, score, feedback) tuples
        """
        results = []
        for i in range(self.n_plans):
            plan = sample_fn(
                problem_statement,
                constraints,
                results,  # Pass previous results for adaptive/diverse sampling
            )

            feedback, score = self._verify_plan(problem_statement, constraints, plan)
            results.append((plan, score, feedback))

        return results

    def _parallel_generate(
        self, problem_statement: str, constraints: List[str], sample_fn: Callable
    ) -> List[Tuple[str, float, str]]:
        """Generate plans in parallel.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            sample_fn: Sampling function to use

        Returns:
            List of (plan, score, feedback) tuples
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            results_so_far = []

            for i in range(self.n_plans):
                future = executor.submit(
                    self._generate_and_verify,
                    problem_statement,
                    constraints,
                    sample_fn,
                    results_so_far.copy(),  # Copy to avoid concurrent modification
                )
                futures.append(future)

                # For diverse/adaptive sampling, we need to wait for each result
                if self.sampling_strategy in ["diverse", "adaptive"]:
                    result = future.result()
                    results_so_far.append(result)

            # Wait for remaining futures if any
            if self.sampling_strategy == "basic":
                results = [f.result() for f in futures]
            else:
                results = results_so_far

        return results

    def _generate_and_verify(
        self,
        problem_statement: str,
        constraints: List[str],
        sample_fn: Callable,
        previous_results: List[Tuple[str, float, str]],
    ) -> Tuple[str, float, str]:
        """Generate and verify a single plan.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            sample_fn: Sampling function to use
            previous_results: Previous (plan, score, feedback) tuples

        Returns:
            Tuple of (plan, score, feedback)
        """
        plan = sample_fn(problem_statement, constraints, previous_results)
        feedback, score = self._verify_plan(problem_statement, constraints, plan)
        return plan, score, feedback

    def _basic_sampling(
        self,
        problem_statement: str,
        constraints: List[str],
        previous_results: List[Tuple[str, float, str]],
    ) -> str:
        """Basic sampling strategy - independent samples.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            previous_results: Ignored in basic sampling

        Returns:
            Generated plan
        """
        try:
            # Get the template for basic plan generation
            template_path = self.template_loader.get_algorithm_template(
                algorithm="best_of_n", template_type="plan", domain=self.domain
            )

            # Render the template
            prompt = self.template_loader.render_template(
                template_path=template_path,
                variables={
                    "problem_statement": problem_statement,
                    "constraints": constraints,
                },
            )

            # Generate the plan
            return self.llm_interface.generate(
                prompt=prompt, temperature=self.temperature
            )
        except Exception as e:
            # Log the error and fall back to base implementation
            print(f"Error in basic sampling: {str(e)}")
            return super()._generate_plan(
                problem_statement, constraints, self.temperature
            )

    def _diverse_sampling(
        self,
        problem_statement: str,
        constraints: List[str],
        previous_results: List[Tuple[str, float, str]],
    ) -> str:
        """Diverse sampling strategy - enforces diversity between plans.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            previous_results: Previous (plan, score, feedback) tuples

        Returns:
            Generated plan
        """
        if not previous_results:
            return self._basic_sampling(
                problem_statement, constraints, previous_results
            )

        previous_plans = [r[0] for r in previous_results]

        try:
            # Get the template for diverse plan generation
            template_path = self.template_loader.get_algorithm_template(
                algorithm="best_of_n", template_type="diverse_plan", domain=self.domain
            )

            # Render the template with existing plans
            prompt = self.template_loader.render_template(
                template_path=template_path,
                variables={
                    "problem_statement": problem_statement,
                    "constraints": constraints,
                    "existing_plans": previous_plans,
                },
            )

            # Generate with higher temperature for more diversity
            return self.llm_interface.generate(
                prompt=prompt,
                temperature=self.temperature * (1 + len(previous_results) * 0.1),
            )
        except Exception as e:
            # Log the error and fall back to base implementation
            print(f"Error in diverse sampling: {str(e)}")
            plan = super()._generate_plan(
                problem_statement,
                constraints,
                temperature=self.temperature * (1 + len(previous_results) * 0.1),
            )

            # Check similarity with previous plans
            if self._is_diverse_enough(plan, previous_plans):
                return plan

        # If we couldn't generate a diverse plan, return the last attempt
        # This should never happen in practice as we're in the exception handler above
        # but we need to have a valid fallback
        return self._basic_sampling(problem_statement, constraints, [])

    def _adaptive_sampling(
        self,
        problem_statement: str,
        constraints: List[str],
        previous_results: List[Tuple[str, float, str]],
    ) -> str:
        """Adaptive sampling strategy - learns from previous attempts.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            previous_results: Previous (plan, score, feedback) tuples

        Returns:
            Generated plan
        """
        if not previous_results:
            return self._basic_sampling(
                problem_statement, constraints, previous_results
            )

        try:
            # Get the template for adaptive plan generation
            template_path = self.template_loader.get_algorithm_template(
                algorithm="best_of_n", template_type="adaptive_plan", domain=self.domain
            )

            # Format previous plans with their feedback and scores
            plans_with_feedback = [
                (plan, feedback, score) for plan, score, feedback in previous_results
            ]

            # Render the template with previous plans and feedback
            prompt = self.template_loader.render_template(
                template_path=template_path,
                variables={
                    "problem_statement": problem_statement,
                    "constraints": constraints,
                    "plans_with_feedback": plans_with_feedback,
                },
            )

            # Analyze previous results for temperature adjustment
            prev_scores = [r[1] for r in previous_results]
            score_trend = (
                np.mean(prev_scores[-2:]) - np.mean(prev_scores[:-2])
                if len(prev_scores) > 2
                else 0
            )
            adapted_temp = self.temperature * (
                1 - score_trend * 0.1
            )  # Reduce temp if improving

            # Generate the plan
            return self.llm_interface.generate(prompt=prompt, temperature=adapted_temp)
        except Exception as e:
            # Log the error and fall back to base implementation
            print(f"Error in adaptive sampling: {str(e)}")

            # Fall back to diverse sampling if adaptive fails
            return self._diverse_sampling(
                problem_statement, constraints, previous_results
            )

    def _is_diverse_enough(self, plan: str, previous_plans: List[str]) -> bool:
        """Check if a plan is diverse enough from previous plans.

        Args:
            plan: New plan to check
            previous_plans: List of previous plans

        Returns:
            True if plan is diverse enough, False otherwise
        """
        # Simple similarity check based on shared words
        plan_words = set(plan.lower().split())

        for prev_plan in previous_plans:
            prev_words = set(prev_plan.lower().split())
            similarity = len(plan_words & prev_words) / len(plan_words | prev_words)

            if similarity > self.min_similarity:
                return False

        return True

    def _create_adaptive_prompt(
        self,
        problem_statement: str,
        constraints: List[str],
        previous_results: List[Tuple[str, float, str]],
    ) -> str:
        """Create a prompt that incorporates insights from previous attempts.

        This method is deprecated and will be removed in a future version.
        Use the template-based approach instead.

        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            previous_results: Previous (plan, score, feedback) tuples

        Returns:
            Adapted system prompt
        """
        # Extract best and worst results
        sorted_results = sorted(previous_results, key=lambda x: x[1], reverse=True)
        best_plan, best_score, best_feedback = sorted_results[0]

        if len(sorted_results) > 1:
            worst_plan, worst_score, worst_feedback = sorted_results[-1]
        else:
            worst_plan, worst_score, worst_feedback = (
                best_plan,
                best_score,
                best_feedback,
            )

        # Create a prompt that includes insights from previous attempts
        return (
            f"Create a plan to solve the following problem. Learn from the strengths and "
            f"weaknesses of previous plans.\n\n"
            f"Problem statement:\n{problem_statement}\n\n"
            f"Constraints to consider:\n"
            + "\n".join([f"- {constraint}" for constraint in constraints])
            + f"\n\nBest previous plan (score: {best_score}):\n{best_plan}\n\n"
            f"Feedback on best plan:\n{best_feedback}\n\n"
            f"Worst previous plan (score: {worst_score}):\n{worst_plan}\n\n"
            f"Feedback on worst plan:\n{worst_feedback}\n\n"
            f"Your improved plan:"
        )
        best_plan, best_score, best_feedback = sorted_results[0]
        worst_plan, worst_score, worst_feedback = sorted_results[-1]

        # Create prompt with insights
        prompt = (
            "Based on previous attempts, consider these insights:\n"
            f"What worked well (score {best_score}):\n{best_feedback}\n"
            f"What didn't work (score {worst_score}):\n{worst_feedback}\n"
            "\nGenerate a new plan that:"
            "\n- Incorporates successful elements from the best plan"
            "\n- Avoids issues identified in the worst plan"
            "\n- Satisfies all original constraints"
        )

        return prompt
