"""
Test script for the time slot verification mechanism.
"""

from plangen.examples.calendar import TimeSlot, TimeSlotVerifier


def main():
    """Test the time slot verification mechanism."""
    print("Testing time slot verification...")

    # Create a verifier
    verifier = TimeSlotVerifier()

    # Add busy times from the problem
    busy_times = [
        "9:30-10:00",  # Alexander
        "10:30-11:00",  # Alexander
        "12:30-13:00",  # Alexander
        "14:30-15:00",  # Alexander
        "16:00-17:00",  # Alexander
        "9:00-9:30",  # Elizabeth
        "11:30-12:30",  # Elizabeth
        "13:00-14:30",  # Elizabeth
        "9:00-14:30",  # Walter
        "15:30-17:00",  # Walter
    ]

    for busy in busy_times:
        verifier.add_busy_slot(busy)

    # Test some meeting slots
    test_slots = [
        "9:00-9:30",
        "14:30-15:00",
        "15:00-15:30",
        "15:30-16:00",
    ]

    for slot in test_slots:
        is_valid, reason = verifier.is_valid_meeting_slot(slot)
        print(f"Slot {slot}: {'Valid' if is_valid else 'Invalid'} - {reason}")

    # Find earliest slot
    earliest = verifier.find_earliest_slot()
    if earliest:
        print(f"Earliest available slot: {earliest}")
    else:
        print("No available slot found")


if __name__ == "__main__":
    main()
