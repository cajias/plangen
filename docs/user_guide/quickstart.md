# Quick Start Guide

This guide will help you get started with PlanGEN quickly.

## Simple Example

Here's a minimal example using the new public API:

```python
from dotenv import load_dotenv
from plangen import PlanGen

# Load environment variables from .env file (containing API keys)
load_dotenv()

# Create a PlanGen instance (automatically uses OpenAI's gpt-4o by default)
plangen = PlanGen.create()

# Define a problem
problem = """
Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
Walter: Busy at 9:00-14:30, 15:30-17:00.
Find an earliest time slot that works for all participants.
"""

# Solve the problem
result = plangen.solve(problem)

# Print the selected solution
print(result["selected_solution"])
```

## Using a Specific Model

You can specify which model to use when creating a PlanGen instance:

### OpenAI

```python
from plangen import PlanGen

# Create a PlanGen instance with a specific OpenAI model
plangen = PlanGen.with_openai(
    model_name="gpt-4-turbo",
    temperature=0.7,
    max_tokens=1024
)

# Solve a problem
problem = "Your problem statement here"
result = plangen.solve(problem)
```

### AWS Bedrock

```python
from plangen import PlanGen

# Create a PlanGen instance with a specific AWS Bedrock model
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1",
    temperature=0.7,
    max_tokens=1024
)

# Solve a problem
problem = "Your problem statement here"
result = plangen.solve(problem)
```

## Using a Specific Algorithm

You can specify which planning algorithm to use when solving a problem:

```python
from plangen import PlanGen

# Create a PlanGen instance
plangen = PlanGen.create()

# Solve a problem using the BestOfN algorithm
result = plangen.solve(
    problem="Your problem statement here",
    algorithm="best_of_n",
    n_plans=5,
    sampling_strategy="diverse",
    parallel=True
)
```

Available algorithms are:
- `"best_of_n"` - Generates multiple plans and selects the best one
- `"tree_of_thought"` - Explores multiple reasoning paths in a tree structure
- `"rebase"` - Uses recursive refinement to improve plans
- `"mixture"` - Dynamically selects the best algorithm for the problem

## Using a Custom Verifier

For specialized verification of solutions, you can provide a custom verifier:

```python
from plangen import PlanGen, Verifiers

# Create a PlanGen instance
plangen = PlanGen.create()

# Create a domain-specific verifier
verifier = Verifiers.calendar()

# Solve a problem with the custom verifier
result = plangen.solve(
    problem="Your calendar scheduling problem here",
    verifier=verifier
)
```

## Manual Process Control

If you want more control over the individual steps of the planning process:

```python
from plangen import PlanGen

# Create a PlanGen instance
plangen = PlanGen.create()

# Extract constraints from a problem
problem = "Your problem statement here"
constraints = plangen.extract_constraints(problem)
print(f"Extracted constraints: {constraints}")

# Generate a single plan
plan = plangen.generate_plan(problem, constraints)
print(f"Generated plan: {plan}")

# Verify the plan
feedback, score = plangen.verify_plan(problem, plan, constraints)
print(f"Verification score: {score}")
print(f"Feedback: {feedback}")
```

## Next Steps

- Check out the [Examples](../examples/index.md) for more advanced use cases
- Learn about [Custom Prompts](custom_prompts.md) to customize the behavior of PlanGEN
- Explore the [Algorithm Reference](../algorithm_reference/index.md) to understand the different planning algorithms