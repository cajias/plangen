"""
Time slot verification utilities for calendar scheduling problems.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass
class TimeSlot:
    """Represents a time slot with start and end times."""

    start: int  # Minutes since midnight
    end: int  # Minutes since midnight

    @classmethod
    def from_str(cls, time_str: str) -> Optional["TimeSlot"]:
        """Create a TimeSlot from a string like '9:30-10:00'.

        Args:
            time_str: String representation of time slot

        Returns:
            TimeSlot object or None if parsing fails
        """
        pattern = r"(\d{1,2}):(\d{2})(?:\s*(?:-|to)\s*)(\d{1,2}):(\d{2})"
        match = re.match(pattern, time_str)

        if not match:
            return None

        start_hour, start_min, end_hour, end_min = map(int, match.groups())

        # Convert to minutes since midnight
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        return cls(start_minutes, end_minutes)

    def __str__(self) -> str:
        """Convert to string representation like '9:30-10:00'.

        Returns:
            String representation of time slot
        """
        start_hour, start_min = divmod(self.start, 60)
        end_hour, end_min = divmod(self.end, 60)

        return f"{start_hour}:{start_min:02d}-{end_hour}:{end_min:02d}"

    def overlaps(self, other: "TimeSlot") -> bool:
        """Check if this time slot overlaps with another.

        Args:
            other: Another TimeSlot to check against

        Returns:
            True if slots overlap, False otherwise
        """
        # Check if one slot starts during the other
        return self.start < other.end and self.end > other.start

    def duration(self) -> int:
        """Get the duration of this time slot in minutes.

        Returns:
            Duration in minutes
        """
        return self.end - self.start


class TimeSlotVerifier:
    """Utility for verifying time slots in calendar scheduling problems."""

    def __init__(self, day_start: int = 9 * 60, day_end: int = 17 * 60):
        """Initialize the time slot verifier.

        Args:
            day_start: Start of day in minutes since midnight (default: 9:00)
            day_end: End of day in minutes since midnight (default: 17:00)
        """
        self.busy_slots: List[TimeSlot] = []
        self.day_start = day_start
        self.day_end = day_end

    def add_busy_slot(self, slot: Union[str, TimeSlot]) -> bool:
        """Add a busy time slot.

        Args:
            slot: Time slot string (e.g., '9:30-10:00') or TimeSlot object

        Returns:
            True if slot was added, False if invalid
        """
        if isinstance(slot, str):
            time_slot = TimeSlot.from_str(slot)
            if not time_slot:
                return False
        else:
            time_slot = slot

        self.busy_slots.append(time_slot)
        return True

    def is_valid_meeting_slot(
        self, slot: Union[str, TimeSlot], duration: Optional[int] = None
    ) -> Tuple[bool, str]:
        """Check if a time slot is valid for a meeting.

        Args:
            slot: Time slot string (e.g., '9:30-10:00') or TimeSlot object
            duration: Optional meeting duration in minutes

        Returns:
            Tuple of (is_valid, reason)
        """
        if isinstance(slot, str):
            time_slot = TimeSlot.from_str(slot)
            if not time_slot:
                return False, "Invalid time slot format"
        else:
            time_slot = slot

        # Check if slot is within working hours
        if time_slot.start < self.day_start:
            return (
                False,
                f"Meeting starts before working hours ({self.day_start//60}:00)",
            )

        if time_slot.end > self.day_end:
            return False, f"Meeting ends after working hours ({self.day_end//60}:00)"

        # Check if duration matches (if specified)
        if duration and time_slot.duration() != duration:
            return (
                False,
                f"Meeting duration ({time_slot.duration()} min) doesn't match required duration ({duration} min)",
            )

        # Check for overlaps with busy slots
        for busy in self.busy_slots:
            if time_slot.overlaps(busy):
                return False, f"Meeting overlaps with busy slot {busy}"

        return True, "Valid meeting slot"

    def find_earliest_slot(self, duration: int = 30) -> Optional[TimeSlot]:
        """Find the earliest available time slot of the given duration.

        Args:
            duration: Meeting duration in minutes

        Returns:
            TimeSlot object or None if no slot found
        """
        # Sort busy slots by start time
        sorted_busy = sorted(self.busy_slots, key=lambda x: x.start)

        # Start from the beginning of the day
        current = self.day_start

        # Check each potential slot
        for busy in sorted_busy:
            # If there's enough time before this busy slot, we found a slot
            if busy.start - current >= duration:
                return TimeSlot(current, current + duration)

            # Move current time to after this busy slot
            current = max(current, busy.end)

        # Check if there's still time at the end of the day
        if self.day_end - current >= duration:
            return TimeSlot(current, current + duration)

        return None
