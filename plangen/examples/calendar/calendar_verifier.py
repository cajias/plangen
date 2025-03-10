"""
Calendar-specific verification strategy.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from ...utils.time_slot_verifier import TimeSlot, TimeSlotVerifier
from ..base_verifier import BaseVerifier


class CalendarVerifier(BaseVerifier):
    """Calendar-specific implementation of the verifier interface.

    This verifier handles meeting scheduling problems by validating time slots,
    checking for conflicts, and ensuring the earliest valid slot is selected.
    """

    def __init__(self):
        """Initialize the calendar verifier."""
        self.domain_keywords = [
            "schedule",
            "meeting",
            "appointment",
            "calendar",
            "time slot",
            "availability",
            "busy",
            "free time",
        ]

    def is_applicable(self, problem_statement: str) -> bool:
        """Check if this verifier is applicable to the given problem.

        Args:
            problem_statement: The problem statement to check

        Returns:
            True if this is a calendar/scheduling problem, False otherwise
        """
        problem_lower = problem_statement.lower()

        # Check for domain keywords
        for keyword in self.domain_keywords:
            if keyword in problem_lower:
                return True

        # Check for time patterns (e.g., "9:00-10:00")
        time_pattern = r"\d{1,2}:\d{2}(?:\s*(?:-|to)\s*)\d{1,2}:\d{2}"
        if re.search(time_pattern, problem_statement):
            return True

        return False

    def verify_solution(
        self, problem_statement: str, solution: str, constraints: List[str]
    ) -> Dict[str, Any]:
        """Verify if a solution satisfies the constraints for a calendar problem.

        Args:
            problem_statement: The original problem statement
            solution: The proposed solution
            constraints: List of constraints the solution must satisfy

        Returns:
            Dictionary containing verification results
        """
        # Extract meeting time from solution
        meeting_time = self._extract_meeting_time(solution)

        # Extract busy times from constraints and problem statement
        busy_times = self._extract_busy_times(problem_statement, constraints)

        # Create time slot verifier
        verifier = TimeSlotVerifier()

        # Add busy times
        for busy in busy_times:
            verifier.add_busy_slot(busy)

        # Verify meeting time if found
        if meeting_time:
            is_valid, reason = verifier.is_valid_meeting_slot(meeting_time)

            # Find earliest slot for comparison
            earliest_slot = verifier.find_earliest_slot()
            is_earliest = False

            if earliest_slot and meeting_time:
                meeting_slot = TimeSlot.from_str(meeting_time)
                is_earliest = meeting_slot and meeting_slot.start == earliest_slot.start

            return {
                "is_valid": is_valid,
                "score": 100 if is_valid and is_earliest else (50 if is_valid else 0),
                "reason": reason,
                "is_earliest": is_earliest,
                "meeting_time": meeting_time,
                "earliest_slot": str(earliest_slot) if earliest_slot else None,
            }

        # No meeting time found
        return {
            "is_valid": False,
            "score": 0,
            "reason": "No specific meeting time found in solution",
            "is_earliest": False,
            "meeting_time": None,
            "earliest_slot": None,
        }

    def extract_domain_constraints(
        self, problem_statement: str, general_constraints: List[str]
    ) -> List[str]:
        """Extract calendar-specific constraints from the problem statement.

        Args:
            problem_statement: The problem statement
            general_constraints: General constraints already extracted

        Returns:
            List of calendar-specific constraints
        """
        domain_constraints = []

        # Extract time-related constraints
        time_constraints = self._extract_time_constraints(problem_statement)
        domain_constraints.extend(time_constraints)

        # Extract availability constraints
        availability_constraints = self._extract_availability_constraints(
            problem_statement
        )
        domain_constraints.extend(availability_constraints)

        return domain_constraints

    def _extract_meeting_time(self, solution: str) -> Optional[str]:
        """Extract meeting time from solution.

        Args:
            solution: The solution text

        Returns:
            Meeting time string if found, None otherwise
        """
        # Look for patterns like "schedule from 10:00 to 10:30" or "meeting at 10:00-10:30"
        patterns = [
            r"from (\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})",
            r"at (\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})",
            r"schedule (?:for|at) (\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})",
            r"(\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, solution.lower())
            if match:
                start, end = match.groups()
                return f"{start}-{end}"

        return None

    def _extract_busy_times(
        self, problem_statement: str, constraints: List[str]
    ) -> List[str]:
        """Extract busy times from problem statement and constraints.

        Args:
            problem_statement: The problem statement
            constraints: List of constraints

        Returns:
            List of busy time strings
        """
        busy_times = []

        # Combine problem statement and constraints
        text = problem_statement + "\n" + "\n".join(constraints)

        # Look for patterns like "busy at 9:30-10:00" or "unavailable from 9:30 to 10:00"
        patterns = [
            r"(?:busy|unavailable)(?:\s*(?:at|from))?\s*(\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})",
            r"(?:busy|unavailable)(?:\s*(?:at|from))?\s*(\d{1,2})(?:\s*(?:to|-)?\s*)(\d{1,2})",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                start, end = match.groups()
                # Add colon if missing
                if ":" not in start:
                    start = f"{start}:00"
                if ":" not in end:
                    end = f"{end}:00"
                busy_times.append(f"{start}-{end}")

        return busy_times

    def _extract_time_constraints(self, problem_statement: str) -> List[str]:
        """Extract time-related constraints from the problem statement.

        Args:
            problem_statement: The problem statement

        Returns:
            List of time-related constraints
        """
        constraints = []

        # Look for meeting duration
        duration_patterns = [
            r"(\d+)(?:-|\s*)minute meeting",
            r"meeting(?:\s*of|\s*for)?\s*(\d+)(?:-|\s*)minute",
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, problem_statement.lower())
            if match:
                duration = match.group(1)
                constraints.append(
                    f"The meeting duration must be exactly {duration} minutes."
                )
                break

        # Look for time range
        time_range_pattern = r"between (\d{1,2}:\d{2}) and (\d{1,2}:\d{2})"
        match = re.search(time_range_pattern, problem_statement.lower())
        if match:
            start, end = match.groups()
            constraints.append(
                f"The meeting must be scheduled between {start} and {end}."
            )

        return constraints

    def _extract_availability_constraints(self, problem_statement: str) -> List[str]:
        """Extract availability constraints from the problem statement.

        Args:
            problem_statement: The problem statement

        Returns:
            List of availability constraints
        """
        constraints = []

        # Look for patterns like "Person is busy at 9:30-10:00"
        availability_pattern = r"([A-Z][a-z]+)(?:\s*is)?\s*(?:busy|unavailable)(?:\s*at|\s*from)?\s*(\d{1,2}:\d{2})(?:\s*(?:to|-)?\s*)(\d{1,2}:\d{2})"

        matches = re.finditer(availability_pattern, problem_statement)
        for match in matches:
            person, start, end = match.groups()
            constraints.append(f"{person} is unavailable from {start} to {end}.")

        return constraints
