"""Mixture of Algorithms for PlanGEN.

This module implements the Mixture of Algorithms approach, which dynamically selects
the best inference algorithm based on the problem's complexity and characteristics.
The approach supports domain-specific templates and verification.

Example:
    ```python
    from plangen.algorithms import MixtureOfAlgorithms
    from plangen.examples.calendar import CalendarVerifier

    # Initialize with domain-specific verifier
    algorithm = MixtureOfAlgorithms(
        max_algorithm_switches=2,
        domain="calendar",
        verifier=CalendarVerifier()
    )

    # Run the algorithm
    best_plan, score, metadata = algorithm.run(problem_statement)
    ```
"""
from __future__ import annotations

from typing import Any, Self

from plangen.agents.selection_agent import SelectionAgent
from plangen.utils.template_loader import TemplateLoader
from plangen.visualization.observers import PlanObserver

from .base_algorithm import BaseAlgorithm
from .best_of_n import BestOfN
from .rebase import REBASE
from .tree_of_thought import TreeOfThought


class MixtureOfAlgorithms(BaseAlgorithm, PlanObserver):
    """Implementation of the Mixture of Algorithms approach.

    This algorithm dynamically selects the best inference algorithm based on
    the problem's complexity and characteristics.

    Attributes:
        selection_agent: Agent for selecting algorithms
        algorithms: Dictionary of available algorithms
        max_algorithm_switches: Maximum number of algorithm switches allowed
        domain: Optional domain name for domain-specific templates
    """

    def __init__(
        self: Self,
        selection_agent: SelectionAgent | None = None,
        max_algorithm_switches: int = 2,
        domain: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize the Mixture of Algorithms approach.

        Args:
            selection_agent: Optional selection agent to use
            max_algorithm_switches: Maximum number of algorithm switches allowed
            domain: Optional domain name for domain-specific templates
            **kwargs: Additional arguments passed to BaseAlgorithm
        """
        super().__init__(**kwargs)

        # Initialize the algorithms
        self.algorithms = {
            "Best of N": BestOfN(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
                domain=domain,
                **kwargs,
            ),
            "Tree of Thought": TreeOfThought(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
                domain=domain,
                **kwargs,
            ),
            "REBASE": REBASE(
                llm_interface=self.llm_interface,
                constraint_agent=self.constraint_agent,
                verification_agent=self.verification_agent,
                domain=domain,
                **kwargs,
            ),
        }

        self.selection_agent = selection_agent or SelectionAgent(
            llm_interface=self.llm_interface,
        )
        self.max_algorithm_switches = max_algorithm_switches
        self.domain = domain

        # Initialize template loader
        self.template_loader = TemplateLoader()

    def run(self: Self, problem_statement: str) -> tuple[str, float, dict[str, Any]]:
        """Run the Mixture of Algorithms approach on the given problem statement.

        Args:
            problem_statement: The problem statement to solve

        Returns:
            Tuple of (best_plan, best_score, metadata)
        """
        # Extract constraints
        constraints = self.constraint_agent.run(problem_statement)
        "\n".join(
            [f"- {constraint}" for constraint in constraints],
        )

        # Notify observers about algorithm start
        self.notify_observers(
            {
                "algorithm_type": "MixtureOfAlgorithms",
                "event": "algorithm_start",
                "problem_statement": problem_statement,
                "constraints": constraints,
                "max_algorithm_switches": self.max_algorithm_switches,
            },
        )

        # Select initial algorithm
        current_algorithm_name = self._select_algorithm(problem_statement, constraints)
        current_algorithm = self.algorithms[current_algorithm_name]

        # Notify observers about algorithm selection
        self.notify_observers(
            {
                "algorithm_type": "MixtureOfAlgorithms",
                "event": "algorithm_selection",
                "selected_algorithm": current_algorithm_name,
                "selection_type": "initial",
                "selection_reason": "Initial algorithm selection based on problem characteristics",
            },
        )

        # Track algorithm switches
        algorithm_history = [current_algorithm_name]

        # Register this instance as an observer to all algorithms
        for algo in self.algorithms.values():
            algo.add_observer(self)

        # Run initial algorithm
        current_plan, current_score, current_metadata = current_algorithm.run(
            problem_statement,
        )

        # Notify observers about algorithm completion
        self.notify_observers(
            {
                "algorithm_type": "MixtureOfAlgorithms",
                "event": "algorithm_iteration_complete",
                "algorithm": current_algorithm_name,
                "plan": current_plan,
                "score": current_score,
                "iteration": 0,
            },
        )

        # Track all iterations for metadata
        iterations = [
            {
                "algorithm": current_algorithm_name,
                "plan": current_plan,
                "score": current_score,
                "metadata": current_metadata,
            },
        ]

        # Iteratively switch algorithms if needed
        for iteration in range(self.max_algorithm_switches):
            # Select next algorithm based on current results
            next_algorithm_name = self._select_next_algorithm(
                problem_statement,
                constraints,
                {
                    "current_plan": current_plan,
                    "current_score": current_score,
                    "current_algorithm": current_algorithm_name,
                },
            )

            # If same algorithm selected, we're done
            if next_algorithm_name == current_algorithm_name:
                # Notify observers about no algorithm switch
                self.notify_observers(
                    {
                        "algorithm_type": "MixtureOfAlgorithms",
                        "event": "algorithm_switch_skipped",
                        "reason": "Same algorithm selected",
                        "algorithm": current_algorithm_name,
                    },
                )
                break

            # Switch to next algorithm
            current_algorithm_name = next_algorithm_name
            current_algorithm = self.algorithms[current_algorithm_name]
            algorithm_history.append(current_algorithm_name)

            # Notify observers about algorithm switch
            self.notify_observers(
                {
                    "algorithm_type": "MixtureOfAlgorithms",
                    "event": "algorithm_selection",
                    "selected_algorithm": current_algorithm_name,
                    "selection_type": "switch",
                    "iteration": iteration + 1,
                    "selection_reason": f"Switching to {current_algorithm_name} based on previous results",
                },
            )

            # Run next algorithm
            next_plan, next_score, next_metadata = current_algorithm.run(
                problem_statement,
            )

            # Notify observers about algorithm completion
            self.notify_observers(
                {
                    "algorithm_type": "MixtureOfAlgorithms",
                    "event": "algorithm_iteration_complete",
                    "algorithm": current_algorithm_name,
                    "plan": next_plan,
                    "score": next_score,
                    "iteration": iteration + 1,
                },
            )

            # Track iteration
            iterations.append(
                {
                    "algorithm": current_algorithm_name,
                    "plan": next_plan,
                    "score": next_score,
                    "metadata": next_metadata,
                },
            )

            # Keep the better plan
            if next_score > current_score:
                current_plan = next_plan
                current_score = next_score
                current_metadata = next_metadata

                # Notify observers about better plan found
                self.notify_observers(
                    {
                        "algorithm_type": "MixtureOfAlgorithms",
                        "event": "better_plan_found",
                        "algorithm": current_algorithm_name,
                        "plan": current_plan,
                        "score": current_score,
                        "improvement": next_score - current_score,
                    },
                )

        # Prepare metadata
        metadata = {
            "algorithm": "Mixture of Algorithms",
            "max_algorithm_switches": self.max_algorithm_switches,
            "algorithm_history": algorithm_history,
            "iterations": iterations,
            "constraints": constraints,
        }

        # Notify observers about algorithm completion
        self.notify_observers(
            {
                "algorithm_type": "MixtureOfAlgorithms",
                "event": "algorithm_complete",
                "best_plan": current_plan,
                "best_score": current_score,
                "algorithm_history": algorithm_history,
                "final_plan": current_plan,
                "final_score": current_score,
            },
        )

        return current_plan, current_score, metadata

    def _select_algorithm(self: Self, problem_statement: str, constraints: list[str]) -> str:
        """Select an algorithm based on the problem statement and constraints.

        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints

        Returns:
            Name of the selected algorithm
        """
        # Get the template path
        template_path = self.template_loader.get_algorithm_template(
            algorithm="mixture_of_algorithms",
            template_type="algorithm_selection",
            domain=self.domain,
        )

        # Format constraints as a string
        formatted_constraints = "\n".join(
            [f"- {constraint}" for constraint in constraints],
        )

        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "constraints": formatted_constraints,
                "available_algorithms": list(self.algorithms.keys()),
            },
        )

        # Generate the algorithm selection
        response = self.llm_interface.generate(prompt=prompt)

        # Extract the algorithm name from the response
        for algorithm_name in self.algorithms:
            if algorithm_name in response:
                return algorithm_name

        # Default to Best of N if no algorithm is found
        return "Best of N"

    def _select_next_algorithm(
        self: Self,
        problem_statement: str,
        constraints: list[str],
        current_state: dict[str, Any],
    ) -> str:
        """Select the next algorithm based on current results.

        Args:
            problem_statement: The problem statement to solve
            constraints: List of constraints
            current_state: Dictionary containing current_plan, current_score, current_algorithm

        Returns:
            Name of the next algorithm to try
        """
        # Extract current state
        current_plan = str(current_state["current_plan"])
        current_score = float(current_state["current_score"])
        current_algorithm = str(current_state["current_algorithm"])

        # Get the template path
        template_path = self.template_loader.get_algorithm_template(
            algorithm="mixture_of_algorithms",
            template_type="algorithm_selection",
            domain=self.domain,
        )

        # Format constraints as a string
        formatted_constraints = "\n".join(
            [f"- {constraint}" for constraint in constraints],
        )

        # Render the template
        prompt = self.template_loader.render_template(
            template_path=template_path,
            variables={
                "problem_statement": problem_statement,
                "constraints": formatted_constraints,
                "available_algorithms": list(self.algorithms.keys()),
                "current_algorithm": current_algorithm,
                "current_plan": current_plan,
                "current_score": current_score,
            },
        )

        # Generate the algorithm selection
        response = self.llm_interface.generate(prompt=prompt)

        # Extract the algorithm name from the response
        for algorithm_name in self.algorithms:
            if algorithm_name in response and algorithm_name != current_algorithm:
                return algorithm_name

        # Default to current algorithm if no new algorithm is found
        return current_algorithm

    def update(self: Self, plan_data: dict[str, Any]) -> None:
        """Receive updates from child algorithms and delegate to observers.

        This method implements the PlanObserver interface to receive updates
        from child algorithms. It adds the current algorithm context and
        forwards the updates to this algorithm's observers.

        Args:
            plan_data: Dictionary containing updated plan information
        """
        # Get the current running algorithm
        algorithm_type = plan_data.get("algorithm_type")

        if algorithm_type:
            # Add context about the mixture of algorithms and forward to observers
            delegated_data = {
                "algorithm_type": "MixtureOfAlgorithms",
                "event": "delegated_update",
                "delegated_algorithm": algorithm_type,
                "algorithm_data": plan_data,
            }

            # Notify our observers with the delegated data
            self.notify_observers(delegated_data)
