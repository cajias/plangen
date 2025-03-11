# BestOfN

The BestOfN algorithm is one of the simplest and most effective planning algorithms in PlanGEN. It works by generating multiple plans (solutions) independently and selecting the best one based on verification scores.

## Overview

1. Generate N plans for solving the problem
2. Verify each plan against the constraints
3. Select the best plan based on verification scores

## When to Use

BestOfN is well-suited for:
- Simple to moderately complex problems
- When you want to explore diverse solutions
- When you need a quick solution without complex reasoning paths
- When parallelization is available (to speed up generation)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n_plans` | int | 5 | Number of plans to generate |
| `sampling_strategy` | str | "diverse" | Strategy for generating plans ("diverse" or "adaptive") |
| `parallel` | bool | True | Whether to generate plans in parallel |
| `llm_interface` | ModelProtocol | None | The language model interface to use |

## Sampling Strategies

### Diverse

The "diverse" sampling strategy aims to generate a diverse set of plans by increasing the temperature and encouraging the model to explore different approaches.

### Adaptive

The "adaptive" sampling strategy adjusts the plan generation based on previous verification results, learning from successful and unsuccessful plans to improve subsequent plans.

## Usage Example

### With Public API

```python
from plangen import PlanGen

# Create a PlanGen instance
plangen = PlanGen.create()

# Solve a problem using BestOfN
result = plangen.solve(
    problem="Schedule a meeting for 3 people with the following constraints...",
    algorithm="best_of_n",
    n_plans=5,
    sampling_strategy="diverse",
    parallel=True
)

# Access the selected solution
selected_solution = result["selected_solution"]
```

### With Algorithm Class

```python
from plangen import Algorithm, PlanGen

# Create a PlanGen instance
plangen = PlanGen.create()

# Create a BestOfN algorithm instance
best_of_n = Algorithm.create(
    algorithm_type="best_of_n",
    model=plangen._plangen.model,
    n_plans=5,
    sampling_strategy="diverse",
    parallel=True
)

# Run the algorithm
problem = "Schedule a meeting for 3 people with the following constraints..."
best_plan, score, metadata = best_of_n.run(problem)

print(f"Best plan (score {score}):\n{best_plan}")
```

## Advanced Configuration

For more advanced configuration, you can use the internal API:

```python
from plangen.algorithms import BestOfN
from plangen.models import OpenAIModelInterface

# Create a model interface
model = OpenAIModelInterface(model_name="gpt-4o")

# Create a BestOfN algorithm instance with custom parameters
best_of_n = BestOfN(
    n_plans=10,
    sampling_strategy="adaptive",
    parallel=True,
    llm_interface=model,
    temperature_range=(0.5, 0.9),
    max_retries=3
)

# Run the algorithm
problem = "Schedule a meeting for 3 people with the following constraints..."
best_plan, score, metadata = best_of_n.run(problem)
```

## Performance Considerations

- **Time Complexity**: O(N) where N is the number of plans
- **Space Complexity**: O(N) where N is the number of plans
- **API Calls**: 2N API calls (N for generation, N for verification)
- **Parallelization**: Can be parallelized for faster generation

## Advantages

- Simple and effective
- Easy to understand and implement
- Highly parallelizable
- Flexible sampling strategies

## Limitations

- No interaction between plans
- No refinement of plans
- Limited exploration of the solution space
- May require a large N for complex problems