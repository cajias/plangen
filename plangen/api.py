"""Public API for the PlanGEN framework.

This module provides a clean, well-documented public interface for using the PlanGEN
framework. It is designed to be intuitive and easy to use, hiding the complexity
of the underlying implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterator, Protocol, Self

if TYPE_CHECKING:
    from plangen.algorithms.base_algorithm import BaseAlgorithm
    from plangen.plangen import PlanGEN

from plangen.types import PlanResult, SolveResult, VerificationResult

# Constants
DEFAULT_SCORE_THRESHOLD = 0.5

# Type definitions for better code readability
PlanType = str
ScoreType = float
ConstraintType = str
FeedbackType = str
MetadataType = dict[str, Any]
PlanResultType = tuple[PlanType, ScoreType, MetadataType]


# Define model protocol
class ModelProtocol(Protocol):
    """Protocol for model interfaces."""

    def generate(
        self: Self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The prompt to generate from
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        ...

    def batch_generate(
        self: Self,
        prompts: list[str],
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> list[str]:
        """Generate text from multiple prompts.

        Args:
            prompts: List of prompts to generate from
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            List of generated texts
        """
        ...


# Define verifier protocol
class VerifierProtocol(Protocol):
    """Protocol for verifiers."""

    def verify(
        self: Self,
        problem: str,
        constraints: list[ConstraintType],
        plan: PlanType,
    ) -> tuple[FeedbackType, ScoreType]:
        """Verify a plan against constraints.

        Args:
            problem: Problem statement
            constraints: List of constraints
            plan: Plan to verify

        Returns:
            Tuple of (feedback, score)
        """
        ...


class PlanGen:
    """Main entry point for the PlanGEN library.

    This class provides a simplified interface to the PlanGEN framework,
    hiding the complexity of the underlying implementation.

    Attributes:
        model: The model interface
        prompt_manager: The prompt manager
        num_solutions: Number of solutions to generate
    """

    @classmethod
    def create(
        cls: type[Self],
        model: str | None = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        api_key: str | None = None,
        **kwargs: object,
    ) -> PlanGen:
        """Create a new PlanGen instance with simplified configuration.

        Args:
            model: Model identifier string ('gpt-4o', 'claude-3-sonnet', etc.)
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate (None for model default)
            api_key: Optional API key (if not provided, uses environment variables)
            **kwargs: Additional parameters passed to the model

        Returns:
            Configured PlanGen instance
        """
        from .plangen import PlanGEN
        from .prompts import PromptManager
        from .utils import LLMInterface

        # Create LLM interface based on model name
        llm_interface = LLMInterface(
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            **kwargs,
        )

        # Create prompt manager
        prompt_manager = PromptManager()

        # Create PlanGEN instance with defaults
        plangen_instance = PlanGEN(
            model=llm_interface,
            prompt_manager=prompt_manager,
        )

        # Create PlanGen wrapper
        return cls(plangen_instance)

    @classmethod
    def with_model(cls: type[Self], model: ModelProtocol) -> PlanGen:
        """Create a PlanGen instance with a custom model implementation.

        Args:
            model: Custom model instance implementing the ModelProtocol

        Returns:
            Configured PlanGen instance
        """
        from .plangen import PlanGEN
        from .prompts import PromptManager

        # Create PlanGEN instance with custom model
        plangen_instance = PlanGEN(
            model=model,
            prompt_manager=PromptManager(),
        )

        return cls(plangen_instance)

    @classmethod
    def with_openai(
        cls: type[Self],
        model_name: str = "gpt-4o",
        api_key: str | None = None,
        **kwargs: object,
    ) -> PlanGen:
        """Create a PlanGen instance with OpenAI model.

        Args:
            model_name: OpenAI model name
            api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY)
            **kwargs: Additional parameters passed to the model

        Returns:
            Configured PlanGen instance with OpenAI model
        """
        from .models import OpenAIModelInterface
        from .plangen import PlanGEN
        from .prompts import PromptManager

        # Create OpenAI model interface
        model = OpenAIModelInterface(
            model_name=model_name,
            api_key=api_key,
            **kwargs,
        )

        # Create PlanGEN instance
        plangen_instance = PlanGEN(
            model=model,
            prompt_manager=PromptManager(),
        )

        return cls(plangen_instance)

    @classmethod
    def with_bedrock(
        cls: type[Self],
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        region: str = "us-east-1",
        **kwargs: object,
    ) -> PlanGen:
        """Create a PlanGen instance with AWS Bedrock model.

        Args:
            model_id: Bedrock model ID
            region: AWS region
            **kwargs: Additional parameters passed to the model

        Returns:
            Configured PlanGen instance with Bedrock model
        """
        from .models import BedrockModelInterface
        from .plangen import PlanGEN
        from .prompts import PromptManager

        # Create Bedrock model interface
        model = BedrockModelInterface(
            model_id=model_id,
            region=region,
            **kwargs,
        )

        # Create PlanGEN instance
        plangen_instance = PlanGEN(
            model=model,
            prompt_manager=PromptManager(),
        )

        return cls(plangen_instance)

    def __init__(self: Self, plangen_instance: PlanGEN) -> None:
        """Initialize a PlanGen instance with a PlanGEN instance.

        Args:
            plangen_instance: PlanGEN instance
        """
        self._plangen = plangen_instance

    def solve(
        self: Self,
        problem: str,
        algorithm: str = "default",
        _verifier: VerifierProtocol | None = None,
        **algorithm_params: object,
    ) -> SolveResult | PlanResult:
        """Solve a problem using the PlanGEN workflow.

        Args:
            problem: Problem statement to solve
            algorithm: Algorithm to use ('default', 'best_of_n', 'tree_of_thought', 'rebase')
            verifier: Optional custom verifier for specialized verification
            **algorithm_params: Additional parameters for the specific algorithm

        Returns:
            SolveResult if using default workflow, PlanResult if using specific algorithm

        Example:
            ```python
            plangen = PlanGen.create(model="gpt-4o")
            result = plangen.solve(
                "Design an algorithm to find the kth largest element in an unsorted array.",
                algorithm="best_of_n",
                n_plans=5
            )
            print(result["selected_solution"])
            ```
        """
        if algorithm != "default":
            # Create the algorithm instance
            algorithm_instance = Algorithm.create(
                algorithm_type=algorithm,
                model=self._plangen.model,
                **algorithm_params,
            )

            # Run the algorithm directly if not using default
            best_plan, score, metadata = algorithm_instance.run(problem)
            return PlanResult(
                problem=problem,
                selected_solution=best_plan,
                score=score,
                metadata=metadata,
            )

        # Use the default PlanGEN workflow
        return self._plangen.solve(problem)

    def solve_stream(
        self: Self,
        problem: str,
    ) -> Iterator[dict[str, Any]]:
        """Solve a problem using the PlanGEN workflow with streaming.

        Args:
            problem: Problem statement to solve

        Yields:
            Dictionary with step information:
                - step: Name of the current step ('extract_constraints', 'generate_solutions', 
                        'verify_solutions', 'select_solution', or 'error')
                - status: 'in_progress', 'complete', or 'error'
                - data: Step-specific data (constraints, solutions, verification results, etc.)
                - error: Error message if status is 'error'

        Example:
            ```python
            plangen = PlanGen.create(model="gpt-4o")
            for update in plangen.solve_stream("Your problem here"):
                print(f"{update['step']}: {update['status']}")
                if update['status'] == 'complete':
                    print(f"Data: {update['data']}")
            ```
        """
        yield from self._plangen.solve_stream(problem)

    def generate_plan(
        self: Self,
        problem: str,
        constraints: list[str] | None = None,
        **kwargs: object,
    ) -> str:
        """Generate a single plan for the given problem.

        Args:
            problem: Problem statement
            constraints: Optional list of constraints (extracted automatically if not provided)
            **kwargs: Additional parameters for generation

        Returns:
            Generated plan
        """
        # Extract constraints if not provided
        if constraints is None:
            constraints = self.extract_constraints(problem)

        # Generate a single solution
        return self._plangen.solution_agent.generate_solutions(
            problem,
            constraints,
            num_solutions=1,
            **kwargs,
        )[0]

    def extract_constraints(self: Self, problem: str) -> list[str]:
        """Extract constraints from a problem statement.

        Args:
            problem: Problem statement

        Returns:
            List of extracted constraints
        """
        return self._plangen.constraint_agent.extract_constraints(problem)

    def verify_plan(
        self: Self,
        problem: str,
        plan: str,
        constraints: list[str] | None = None,
        verifier: VerifierProtocol | None = None,
    ) -> tuple[str, float] | VerificationResult:
        """Verify a plan against constraints.

        Args:
            problem: Problem statement
            plan: Plan to verify
            constraints: Optional list of constraints (extracted automatically if not provided)
            verifier: Optional custom verifier

        Returns:
            Tuple of (feedback, score) for backward compatibility, or VerificationResult
        """
        # Extract constraints if not provided
        if constraints is None:
            constraints = self.extract_constraints(problem)

        # Use custom verifier if provided
        if verifier is not None:
            return verifier.verify(problem, constraints, plan)

        # Use the default verification agent
        verification_result = self._plangen.verification_agent.verify_solution(
            plan,
            constraints,
        )

        # Extract feedback and score from verification result
        feedback = verification_result.get("feedback", "")
        score = verification_result.get("score", 0.0)

        return feedback, score


class Algorithm:
    """Base class for PlanGEN algorithms."""

    @classmethod
    def create(
        cls: type[Self],
        algorithm_type: str,
        model: ModelProtocol | None = None,
        _verifier: VerifierProtocol | None = None,
        **kwargs: object,
    ) -> Algorithm:
        """Create an algorithm instance.

        Args:
            algorithm_type: Algorithm type ('best_of_n', 'tree_of_thought', 'rebase', 'mixture')
            model: Optional model interface
            verifier: Optional verifier
            **kwargs: Algorithm-specific parameters

        Returns:
            Configured algorithm instance
        """
        from .algorithms import (REBASE, BestOfN, MixtureOfAlgorithms,
                                 TreeOfThought)
        from .utils import LLMInterface

        # Convert model to LLMInterface if needed
        llm_interface = model if model is not None else LLMInterface()

        # Create the appropriate algorithm based on type
        if algorithm_type == "best_of_n":
            # Extract BestOfN specific parameters
            n_plans = kwargs.get("n_plans", 5)
            sampling_strategy = kwargs.get("sampling_strategy", "diverse")
            parallel = kwargs.get("parallel", True)

            algorithm_instance = BestOfN(
                n_plans=n_plans,
                sampling_strategy=sampling_strategy,
                parallel=parallel,
                llm_interface=llm_interface,
            )

        elif algorithm_type == "tree_of_thought":
            # Extract TreeOfThought specific parameters
            max_depth = kwargs.get("max_depth", 5)
            branching_factor = kwargs.get("branching_factor", 3)
            beam_width = kwargs.get("beam_width", 2)

            algorithm_instance = TreeOfThought(
                max_depth=max_depth,
                branching_factor=branching_factor,
                beam_width=beam_width,
                llm_interface=llm_interface,
            )

        elif algorithm_type == "rebase":
            # Extract REBASE specific parameters
            max_iterations = kwargs.get("max_iterations", 5)
            improvement_threshold = kwargs.get("improvement_threshold", 0.1)

            algorithm_instance = REBASE(
                max_iterations=max_iterations,
                improvement_threshold=improvement_threshold,
                llm_interface=llm_interface,
            )

        elif algorithm_type == "mixture":
            # Extract MixtureOfAlgorithms specific parameters
            max_algorithm_switches = kwargs.get("max_algorithm_switches", 2)

            algorithm_instance = MixtureOfAlgorithms(
                max_algorithm_switches=max_algorithm_switches,
                llm_interface=llm_interface,
            )

        else:
            msg = f"Unknown algorithm type: {algorithm_type}"
            raise ValueError(msg)

        # Wrap the algorithm instance
        return cls(algorithm_instance)

    def __init__(self: Self, algorithm_instance: BaseAlgorithm) -> None:
        """Initialize an Algorithm instance with an algorithm instance.

        Args:
            algorithm_instance: Algorithm instance
        """
        self._algorithm = algorithm_instance

    def run(self: Self, problem: str) -> PlanResultType:
        """Run the algorithm on the given problem.

        Args:
            problem: Problem statement

        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        return self._algorithm.run(problem)


class Visualization:
    """Visualization tools for PlanGEN."""

    @classmethod
    def create_graph(
        cls: type[Self],
        result: dict[str, Any],
        output_format: str = "png",
        output_path: str | None = None,
        **kwargs: object,
    ) -> str:
        """Create a visual graph of the planning process.

        Args:
            result: Result from PlanGen.solve()
            output_format: Output format ('png', 'svg', 'html')
            output_path: Path to save the visualization (None for auto-generated)
            **kwargs: Additional visualization parameters

        Returns:
            Path to the generated visualization file
        """
        from .visualization import GraphRenderer

        # Create a graph renderer
        renderer = GraphRenderer()

        # Extract metadata from the result
        metadata = result.get("metadata", {})

        # Render the graph based on the output format
        if output_format == "png":
            return renderer.render_png(metadata, output_path, **kwargs)
        if output_format == "svg":
            return renderer.render_svg(metadata, output_path, **kwargs)
        if output_format == "html":
            return renderer.render_html(metadata, output_path, **kwargs)
        msg = f"Unsupported output format: {output_format}"
        raise ValueError(msg)

    @classmethod
    def render_to_html(
        cls: type[Self],
        result: dict[str, Any],
        output_path: str | None = None,
        **kwargs: object,
    ) -> str:
        """Render the planning process as an interactive HTML visualization.

        Args:
            result: Result from PlanGen.solve()
            output_path: Path to save the HTML file (None for auto-generated)
            **kwargs: Additional rendering parameters

        Returns:
            Path to the HTML file
        """
        return cls.create_graph(
            result,
            output_format="html",
            output_path=output_path,
            **kwargs,
        )


class Verifiers:
    """Factory for domain-specific verifiers."""

    @classmethod
    def create(
        cls: type[Self], verifier_type: str, **kwargs: object
    ) -> VerifierProtocol:
        """Create a verifier for a specific domain.

        Args:
            verifier_type: Verifier type ('math', 'code', etc.)
            **kwargs: Verifier-specific parameters

        Returns:
            Configured verifier instance
        """
        if verifier_type == "math":
            return cls.math(**kwargs)
        msg = f"Unknown verifier type: {verifier_type}"
        raise ValueError(msg)

    @classmethod
    def math(cls: type[Self], **kwargs: object) -> VerifierProtocol:
        """Create a math problem verifier.

        Args:
            **kwargs: Math verifier parameters

        Returns:
            Math verifier instance
        """
        from .verification.strategies.math_verifier import MathVerifier

        return MathVerifier(**kwargs)

    @classmethod
    def custom(
        cls: type[Self], verify_function: Callable, **kwargs: object
    ) -> VerifierProtocol:
        """Create a custom verifier with a function.

        Args:
            verify_function: Function that implements verification logic
            **kwargs: Additional parameters

        Returns:
            Custom verifier instance
        """
        from .verification import BaseVerifier

        class CustomVerifier(BaseVerifier):
            def verify_solution(
                self: Self,
                problem_statement: str,
                solution: str,
                constraints: list[str],
            ) -> dict[str, Any]:
                # Call the user's verify function and adapt to the expected interface
                feedback, score = verify_function(
                    problem_statement, constraints, solution
                )
                return {
                    "is_valid": score > DEFAULT_SCORE_THRESHOLD,
                    "score": score * 100,
                    "reason": feedback,
                }

            def is_applicable(self: Self, _problem_statement: str) -> bool:
                # Custom verifiers are always applicable
                return True

            def extract_domain_constraints(
                self: Self,
                _problem_statement: str,
                _general_constraints: list[str],
            ) -> list[str]:
                # Custom verifiers don't extract additional constraints
                return []

            def verify(
                self: Self,
                problem: str,
                constraints: list[str],
                plan: str,
            ) -> tuple[str, float]:
                # Support the VerifierProtocol interface
                return verify_function(problem, constraints, plan)

        return CustomVerifier(**kwargs)
