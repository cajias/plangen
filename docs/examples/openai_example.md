# OpenAI Example

Complete example using OpenAI models with PlanGEN.

```python
from plangen import PlanGen

# Create PlanGen with OpenAI
plangen = PlanGen.with_openai(
    model_name="gpt-4o",
    temperature=0.7,
    max_tokens=2048
)

# Define problem
problem = """
Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday.
Alexander: Busy 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00
Elizabeth: Busy 9:00-9:30, 11:30-12:30, 13:00-14:30
Walter: Busy 9:00-14:30, 15:30-17:00
Find earliest available time.
"""

# Solve
result = plangen.solve(problem)
print(result["selected_solution"])
```

See [Simple Example](simple_example.md) for more details.
