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
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from .base_algorithm import BaseAlgorithm
from ..utils.llm_interface import LLMInterface
from ..verification import BaseVerifier


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
    """
    
    SAMPLING_STRATEGIES = ["basic", "diverse", "adaptive"]
    
    def __init__(
        self,
        n_plans: int = 3,
        sampling_strategy: str = "basic",
        parallel: bool = False,
        min_similarity: float = 0.3,
        max_retries: int = 5,
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
    
    def run(self, problem_statement: str) -> Tuple[str, float, Dict[str, Any]]:
        """Run the Best of N algorithm on the given problem statement.
        
        Args:
            problem_statement: The problem statement to solve
            
        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
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
                problem_statement, 
                constraints,
                sample_fn
            )
        else:
            results = self._sequential_generate(
                problem_statement, 
                constraints,
                sample_fn
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
    
    def _sequential_generate(
        self,
        problem_statement: str,
        constraints: List[str],
        sample_fn: Callable
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
                results  # Pass previous results for adaptive/diverse sampling
            )
            
            feedback, score = self._verify_plan(problem_statement, constraints, plan)
            results.append((plan, score, feedback))
        
        return results
    
    def _parallel_generate(
        self,
        problem_statement: str,
        constraints: List[str],
        sample_fn: Callable
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
                    results_so_far.copy()  # Copy to avoid concurrent modification
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
        previous_results: List[Tuple[str, float, str]]
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
        previous_results: List[Tuple[str, float, str]]
    ) -> str:
        """Basic sampling strategy - independent samples.
        
        Args:
            problem_statement: The problem to solve
            constraints: List of constraints
            previous_results: Ignored in basic sampling
            
        Returns:
            Generated plan
        """
        return self._generate_plan(
            problem_statement, 
            constraints,
            temperature=self.temperature
        )
    
    def _diverse_sampling(
        self,
        problem_statement: str,
        constraints: List[str],
        previous_results: List[Tuple[str, float, str]]
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
            return self._basic_sampling(problem_statement, constraints, previous_results)
        
        previous_plans = [r[0] for r in previous_results]
        
        for _ in range(self.max_retries):
            # Generate with higher temperature for more diversity
            plan = self._generate_plan(
                problem_statement,
                constraints,
                temperature=self.temperature * (1 + len(previous_results) * 0.1)
            )
            
            # Check similarity with previous plans
            if self._is_diverse_enough(plan, previous_plans):
                return plan
        
        # If we couldn't generate a diverse plan, return the last attempt
        return plan
    
    def _adaptive_sampling(
        self,
        problem_statement: str,
        constraints: List[str],
        previous_results: List[Tuple[str, float, str]]
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
            return self._basic_sampling(problem_statement, constraints, previous_results)
        
        # Analyze previous results
        prev_scores = [r[1] for r in previous_results]
        prev_feedbacks = [r[2] for r in previous_results]
        
        # Extract insights from feedbacks
        prompt = self._create_adaptive_prompt(
            problem_statement,
            constraints,
            previous_results
        )
        
        # Generate with adapted temperature based on score trend
        score_trend = np.mean(prev_scores[-2:]) - np.mean(prev_scores[:-2]) if len(prev_scores) > 2 else 0
        adapted_temp = self.temperature * (1 - score_trend * 0.1)  # Reduce temp if improving
        
        return self._generate_plan(
            problem_statement,
            constraints,
            temperature=adapted_temp,
            system_prompt=prompt
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
        previous_results: List[Tuple[str, float, str]]
    ) -> str:
        """Create a prompt that incorporates insights from previous attempts.
        
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