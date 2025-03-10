"""
Time slot verification utilities for meeting scheduling.
"""

import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import List, Optional, Tuple


@dataclass
class TimeSlot:
    """Represents a time slot with start and end times."""

    start: time
    end: time

    @classmethod
    def from_str(cls, time_str: str) -> Optional["TimeSlot"]:
        """Create a TimeSlot from a string like '9:00-10:00' or '9:00 to 10:00'."""
        # Try different formats
        patterns = [
            r"(\d{1,2}):(\d{2})\s*(?:-|to)\s*(\d{1,2}):(\d{2})",  # 9:00-10:00 or 9:00 to 10:00
            r"(\d{1,2})(\d{2})\s*(?:-|to)\s*(\d{1,2})(\d{2})",  # 0900-1000 or 0900 to 1000
        ]

        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                try:
                    start_hour, start_min, end_hour, end_min = map(int, match.groups())
                    return cls(
                        time(hour=start_hour, minute=start_min),
                        time(hour=end_hour, minute=end_min),
                    )
                except ValueError:
                    continue
        return None

    def overlaps(self, other: "TimeSlot") -> bool:
        """Check if this time slot overlaps with another."""
        return self.start < other.end and self.end > other.start

    def duration_minutes(self) -> int:
        """Get the duration of the time slot in minutes."""
        start_dt = datetime.combine(datetime.today(), self.start)
        end_dt = datetime.combine(datetime.today(), self.end)
        return int((end_dt - start_dt).total_seconds() / 60)

    def __str__(self) -> str:
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"


class TimeSlotVerifier:
    """Verifies time slots against scheduling constraints."""

    def __init__(self, business_hours: Tuple[time, time] = (time(9), time(17))):
        """Initialize the verifier.

        Args:
            business_hours: Tuple of (start_time, end_time) for business hours
        """
        self.business_hours = TimeSlot(business_hours[0], business_hours[1])
        self.busy_slots: List[TimeSlot] = []

    def add_busy_slot(self, busy_time: str) -> bool:
        """Add a busy time slot.

        Args:
            busy_time: String representing busy time (e.g., "9:00-10:00")

        Returns:
            True if successfully added, False if invalid format
        """
        slot = TimeSlot.from_str(busy_time)
        if slot:
            self.busy_slots.append(slot)
            return True
        return False

    def is_valid_meeting_slot(
        self, meeting_slot: str, duration_minutes: int = 30
    ) -> Tuple[bool, str]:
        """Check if a meeting slot is valid.

        Args:
            meeting_slot: String representing meeting time (e.g., "9:00-9:30")
            duration_minutes: Expected duration in minutes

        Returns:
            Tuple of (is_valid, reason)
        """
        slot = TimeSlot.from_str(meeting_slot)
        if not slot:
            return False, "Invalid time slot format"

        # Check business hours
        if not (
            self.business_hours.start <= slot.start
            and slot.end <= self.business_hours.end
        ):
            return False, "Outside business hours"

        # Check duration
        if slot.duration_minutes() != duration_minutes:
            return False, f"Duration must be exactly {duration_minutes} minutes"

        # Check conflicts with busy slots
        for busy in self.busy_slots:
            if slot.overlaps(busy):
                return False, f"Conflicts with busy slot {busy}"

        return True, "Valid time slot"

    def find_earliest_slot(self, duration_minutes: int = 30) -> Optional[TimeSlot]:
        """Find the earliest available time slot of given duration.

        Args:
            duration_minutes: Duration needed in minutes

        Returns:
            TimeSlot if found, None if no slot available
        """
        # Sort busy slots
        sorted_busy = sorted(self.busy_slots, key=lambda x: x.start)

        # Start with business hours start
        current = self.business_hours.start

        # Try each potential slot until we find one that works
        while current < self.business_hours.end:
            # Create potential slot
            current_dt = datetime.combine(datetime.today(), current)
            end_dt = current_dt + timedelta(minutes=duration_minutes)

            if end_dt.time() > self.business_hours.end:
                break

            potential = TimeSlot(current, end_dt.time())

            # Check if slot works
            is_valid = True
            for busy in sorted_busy:
                if potential.overlaps(busy):
                    is_valid = False
                    # Jump to end of this busy slot
                    current = busy.end
                    break

            if is_valid:
                return potential

            # Try next slot if current didn't work and we didn't jump
            if current == potential.start:
                current_dt = end_dt
                current = current_dt.time()

        return None
