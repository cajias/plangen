"""
Math problem verification strategy.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from ..base_verifier import BaseVerifier


class MathVerifier(BaseVerifier):
    """Math-specific implementation of the verifier interface.

    This verifier handles mathematical problems by checking numerical answers,
    validating calculation steps, and ensuring mathematical correctness.
    """

    def __init__(self):
        """Initialize the math verifier."""
        self.domain_keywords = [
            "calculate",
            "compute",
            "solve",
            "equation",
            "math",
            "arithmetic",
            "algebra",
            "geometry",
            "calculus",
            "probability",
            "statistics",
        ]

        self.math_operations = ["+", "-", "*", "/", "=", "<", ">", "≤", "≥"]

    def is_applicable(self, problem_statement: str) -> bool:
        """Check if this verifier is applicable to the given problem.

        Args:
            problem_statement: The problem statement to check

        Returns:
            True if this is a math problem, False otherwise
        """
        problem_lower = problem_statement.lower()

        # Check for domain keywords
        for keyword in self.domain_keywords:
            if keyword in problem_lower:
                return True

        # Check for mathematical expressions
        for op in self.math_operations:
            if op in problem_statement:
                return True

        # Check for numerical patterns
        if re.search(r"\d+\s*[\+\-\*/\=]\s*\d+", problem_statement):
            return True

        return False

    def verify_solution(
        self, problem_statement: str, solution: str, constraints: List[str]
    ) -> Dict[str, Any]:
        """Verify if a solution satisfies the constraints for a math problem.

        Args:
            problem_statement: The original problem statement
            solution: The proposed solution
            constraints: List of constraints the solution must satisfy

        Returns:
            Dictionary containing verification results
        """
        # Extract numerical answer from solution
        answer = self._extract_numerical_answer(solution)

        # Extract expected answer from problem (if available)
        expected_answer = self._extract_expected_answer(problem_statement)

        # Check calculation steps
        steps_valid, steps_feedback = self._validate_calculation_steps(solution)

        # Determine validity and score
        if answer is not None:
            if expected_answer is not None:
                # If we have both actual and expected answers, compare them
                is_valid = self._compare_answers(answer, expected_answer)
                score = 100 if is_valid else 0
                reason = f"Answer {answer} {'matches' if is_valid else 'does not match'} expected answer {expected_answer}"
            else:
                # If we only have the actual answer, check if steps are valid
                is_valid = steps_valid
                score = (
                    80 if steps_valid else 40
                )  # Lower confidence without expected answer
                reason = steps_feedback
        else:
            # No numerical answer found
            is_valid = False
            score = 0
            reason = "No numerical answer found in solution"

        return {
            "is_valid": is_valid,
            "score": score,
            "reason": reason,
            "answer": answer,
            "expected_answer": expected_answer,
            "steps_valid": steps_valid,
        }

    def extract_domain_constraints(
        self, problem_statement: str, general_constraints: List[str]
    ) -> List[str]:
        """Extract math-specific constraints from the problem statement.

        Args:
            problem_statement: The problem statement
            general_constraints: General constraints already extracted

        Returns:
            List of math-specific constraints
        """
        domain_constraints = []

        # Extract numerical constraints
        numerical_constraints = self._extract_numerical_constraints(problem_statement)
        domain_constraints.extend(numerical_constraints)

        # Extract operation constraints
        operation_constraints = self._extract_operation_constraints(problem_statement)
        domain_constraints.extend(operation_constraints)

        return domain_constraints

    def _extract_numerical_answer(self, solution: str) -> Optional[float]:
        """Extract numerical answer from solution.

        Args:
            solution: The solution text

        Returns:
            Numerical answer if found, None otherwise
        """
        # Look for patterns like "answer is 42" or "= 42"
        patterns = [
            r"(?:answer|result|solution)(?:\s*is|\s*=)?\s*(-?\d+\.?\d*)",
            r"=\s*(-?\d+\.?\d*)",
            r"(-?\d+\.?\d*)\s*$",  # Answer at the end of the solution
        ]

        for pattern in patterns:
            match = re.search(pattern, solution.lower())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    def _extract_expected_answer(self, problem_statement: str) -> Optional[float]:
        """Extract expected answer from problem statement if available.

        Args:
            problem_statement: The problem statement

        Returns:
            Expected answer if found, None otherwise
        """
        # Some math problems might include the expected answer
        patterns = [
            r"(?:answer|result|solution)(?:\s*is|\s*=)?\s*(-?\d+\.?\d*)",
            r"=\s*(-?\d+\.?\d*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, problem_statement.lower())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    def _validate_calculation_steps(self, solution: str) -> Tuple[bool, str]:
        """Validate calculation steps in the solution.

        Args:
            solution: The solution text

        Returns:
            Tuple of (is_valid, feedback)
        """
        # This is a simplified implementation
        # In a real system, this would parse and validate each calculation step

        # Check for common calculation patterns
        calculation_pattern = r"\d+\s*[\+\-\*/]\s*\d+\s*=\s*\d+"
        has_calculations = bool(re.search(calculation_pattern, solution))

        # Check for step-by-step working
        has_steps = len(solution.split("\n")) > 2

        if has_calculations and has_steps:
            return True, "Solution contains valid calculation steps"
        elif has_calculations:
            return True, "Solution contains calculations but limited steps"
        elif has_steps:
            return False, "Solution has steps but no clear calculations"
        else:
            return False, "Solution lacks both steps and calculations"

    def _compare_answers(
        self, answer: float, expected: float, tolerance: float = 0.001
    ) -> bool:
        """Compare actual answer with expected answer within tolerance.

        Args:
            answer: Actual answer
            expected: Expected answer
            tolerance: Acceptable difference

        Returns:
            True if answers match within tolerance, False otherwise
        """
        return abs(answer - expected) <= tolerance

    def _extract_numerical_constraints(self, problem_statement: str) -> List[str]:
        """Extract numerical constraints from the problem statement.

        Args:
            problem_statement: The problem statement

        Returns:
            List of numerical constraints
        """
        constraints = []

        # Look for range constraints
        range_pattern = r"between\s+(-?\d+\.?\d*)\s+and\s+(-?\d+\.?\d*)"
        match = re.search(range_pattern, problem_statement.lower())
        if match:
            lower, upper = match.groups()
            constraints.append(f"The answer must be between {lower} and {upper}.")

        # Look for precision constraints
        precision_pattern = (
            r"(?:round|precision|decimal places|significant figures).*?(\d+)"
        )
        match = re.search(precision_pattern, problem_statement.lower())
        if match:
            precision = match.group(1)
            constraints.append(
                f"The answer must be rounded to {precision} decimal places."
            )

        return constraints

    def _extract_operation_constraints(self, problem_statement: str) -> List[str]:
        """Extract operation constraints from the problem statement.

        Args:
            problem_statement: The problem statement

        Returns:
            List of operation constraints
        """
        constraints = []

        # Look for required operations
        operations = {
            "add": "addition",
            "subtract": "subtraction",
            "multiply": "multiplication",
            "divide": "division",
            "square": "squaring",
            "root": "square root",
            "log": "logarithm",
            "sin": "sine",
            "cos": "cosine",
            "tan": "tangent",
        }

        for op_keyword, op_name in operations.items():
            if op_keyword in problem_statement.lower():
                constraints.append(f"The solution must use {op_name}.")

        return constraints
