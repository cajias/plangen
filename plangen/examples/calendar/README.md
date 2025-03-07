# Calendar Scheduling Example

This example demonstrates how to implement domain-specific verification for calendar scheduling problems using the PlanGEN framework.

## Components

- `calendar_verifier.py`: Calendar-specific implementation of the BaseVerifier interface
- `time_slot_verifier.py`: Utility classes for time slot validation
- `templates/`: Calendar-specific prompt templates

## Usage

```python
from plangen.examples.calendar import CalendarVerifier
from plangen.verification import VerifierFactory

# Create and register the calendar verifier
factory = VerifierFactory()
factory.register_verifier(CalendarVerifier())

# Get appropriate verifier for a scheduling problem
problem = "Schedule a 30-minute meeting..."
verifier = factory.get_verifier(problem)

# Verify a solution
result = verifier.verify_solution(
    problem_statement=problem,
    solution="The meeting should be scheduled from 10:00 to 10:30",
    constraints=["Must be 30 minutes", "Between 9:00 and 17:00"]
)

print(f"Valid: {result['is_valid']}")
print(f"Score: {result['score']}")
print(f"Reason: {result['reason']}")
```

## Template Customization

The `templates/rebase/` directory contains calendar-specific templates for:
- Step generation
- Solution verification
- Reward calculation
- Completion checking

You can customize these templates or use them as examples for other domains.