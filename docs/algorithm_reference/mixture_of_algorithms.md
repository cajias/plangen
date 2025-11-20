# Mixture of Algorithms

MixtureOfAlgorithms is a meta-algorithm that automatically selects and switches between different planning algorithms (BestOfN, TreeOfThought, REBASE) based on problem characteristics and intermediate results.

## Overview

MixtureOfAlgorithms acts as an intelligent orchestrator:

1. Analyzes problem characteristics
2. Selects the most appropriate algorithm
3. Monitors performance during execution
4. Can switch algorithms if needed
5. Returns the best solution found

## How It Works

```
Problem → Analyze Characteristics
              ↓
    ┌─────────┴─────────┐
    │   Simple?         │
    │   • Yes → BestOfN │
    │   • No  → Continue │
    └─────────┬─────────┘
              ↓
    ┌─────────┴──────────┐
    │   Need Exploration? │
    │   • Yes → ToT      │
    │   • No  → Continue  │
    └─────────┬──────────┘
              ↓
    ┌─────────┴──────────┐
    │   Need Refinement?  │
    │   • Yes → REBASE   │
    │   • No  → BestOfN  │
    └─────────┬──────────┘
              ↓
         Execute Selected
              ↓
         Monitor Results
              ↓
    ┌─────────┴─────────┐
    │   Poor Results?    │
    │   • Yes → Switch   │
    │   • No  → Continue │
    └───────────────────┘
```

## When to Use

MixtureOfAlgorithms is ideal for:

- **Unknown problem types** where the best approach isn't clear
- **Production systems** needing automatic optimization
- **Diverse problem sets** with varying characteristics
- **Prototyping** to find the best algorithm for later optimization

Best for:
- Applications with varied problems
- When you want optimal results automatically
- Rapid development and testing

## Parameters

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_algorithm_switches` | int | 2 | Maximum number of algorithm changes |
| `llm_interface` | ModelProtocol | Required | Language model interface |

### Advanced Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `selection_strategy` | str | "adaptive" | How to select algorithm |
| `performance_threshold` | float | 0.6 | Minimum acceptable score |
| `enable_switching` | bool | True | Allow mid-execution switches |

## Usage Examples

### Basic Usage

```python
from plangen import PlanGen

plangen = PlanGen.create()

# Automatically selects best algorithm
result = plangen.solve(
    problem="Your problem here",
    algorithm="mixture"
)

print(result["selected_solution"])
print(f"Used algorithm: {result['metadata']['algorithm_used']}")
```

### With Algorithm Class

```python
from plangen.algorithms import MixtureOfAlgorithms
from plangen.models import OpenAIModelInterface

# Create model
model = OpenAIModelInterface(model_name="gpt-4o")

# Create mixture algorithm
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=3,
    llm_interface=model
)

# Run on problem
problem = "Design a distributed caching system"
solution, score, metadata = mixture.run(problem)

print(f"Solution (score: {score}):\n{solution}")
print(f"\nAlgorithm path: {metadata['algorithm_path']}")
print(f"Switches made: {metadata['num_switches']}")
```

### With Custom Parameters

```python
from plangen.algorithms import MixtureOfAlgorithms

mixture = MixtureOfAlgorithms(
    max_algorithm_switches=2,
    performance_threshold=0.7,  # Switch if score < 0.7
    enable_switching=True,
    llm_interface=model
)

solution, score, metadata = mixture.run(problem)
```

## Selection Logic

### Problem Characteristics

MixtureOfAlgorithms analyzes:

1. **Complexity**: Simple vs. complex problems
2. **Structure**: Single-step vs. multi-step
3. **Constraints**: Number and type of constraints
4. **Domain**: Recognized problem types

### Algorithm Selection Rules

```python
if problem.is_simple():
    return BestOfN(n_plans=5)
elif problem.needs_exploration():
    return TreeOfThought(branching_factor=3, max_depth=5)
elif problem.needs_refinement():
    return REBASE(max_iterations=5)
else:
    return BestOfN(n_plans=5)  # Default
```

### Switching Triggers

Algorithm switching occurs when:

- Current algorithm produces low scores
- Better algorithm identified for problem type
- Stuck in local optimum
- Maximum iterations reached without good result

## Use Case Examples

### Unknown Problem Type

```python
# Let MixtureOfAlgorithms choose
mixture = MixtureOfAlgorithms(llm_interface=model)

problems = [
    "Schedule a meeting...",  # → Likely BestOfN
    "Design an algorithm...", # → Likely TreeOfThought
    "Write and debug code...", # → Likely REBASE
]

for problem in problems:
    solution, score, metadata = mixture.run(problem)
    print(f"Problem: {problem[:30]}...")
    print(f"Used: {metadata['algorithm_used']}")
    print(f"Score: {score}\n")
```

### Production System

```python
# Handle diverse user queries
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=2,
    performance_threshold=0.75,
    llm_interface=model
)

def solve_user_problem(user_input):
    """Automatically handles any problem type."""
    solution, score, metadata = mixture.run(user_input)
    
    return {
        'solution': solution,
        'confidence': score,
        'method': metadata['algorithm_used'],
        'switches': metadata.get('num_switches', 0)
    }
```

### Benchmarking

```python
# Test all algorithms on same problem
from plangen.algorithms import BestOfN, TreeOfThought, REBASE

problem = "Your test problem"

# Manual testing
algorithms = {
    'BestOfN': BestOfN(n_plans=5, llm_interface=model),
    'TreeOfThought': TreeOfThought(llm_interface=model),
    'REBASE': REBASE(llm_interface=model),
}

results = {}
for name, alg in algorithms.items():
    solution, score, metadata = alg.run(problem)
    results[name] = score

# Automatic selection
mixture = MixtureOfAlgorithms(llm_interface=model)
solution, score, metadata = mixture.run(problem)

print("Manual results:", results)
print(f"Mixture selected: {metadata['algorithm_used']} (score: {score})")
```

## Understanding the Output

### Metadata Structure

```python
metadata = {
    'algorithm': 'mixture_of_algorithms',
    'algorithm_used': 'tree_of_thought',  # Final algorithm
    'algorithm_path': [
        {'algorithm': 'best_of_n', 'score': 0.65, 'reason': 'initial_selection'},
        {'algorithm': 'tree_of_thought', 'score': 0.89, 'reason': 'poor_initial_score'}
    ],
    'num_switches': 1,
    'selection_reasoning': 'Problem requires multi-step reasoning',
    'total_time': 45.2,
    'time_by_algorithm': {
        'best_of_n': 15.3,
        'tree_of_thought': 29.9
    }
}
```

### Algorithm Path

The `algorithm_path` shows the sequence of algorithms used:

```python
[
    {'algorithm': 'best_of_n', 'score': 0.6, 'reason': 'initial_selection'},
    {'algorithm': 'rebase', 'score': 0.85, 'reason': 'needs_refinement'},
    {'algorithm': 'rebase', 'score': 0.92, 'reason': 'continue_refining'}
]
```

## Performance Characteristics

### Time Complexity

Depends on selected algorithm(s):

- **Best case**: Single BestOfN execution
- **Average case**: Single TreeOfThought or REBASE
- **Worst case**: Multiple algorithm switches

### API Calls

Variable based on:
- Number of algorithm switches
- Algorithms selected
- Problem complexity

```python
# Example cost calculation
BestOfN: ~10 calls
Switch analysis: ~2 calls
TreeOfThought: ~30 calls
Total with one switch: ~42 calls
```

## Comparison with Direct Algorithm Use

| Aspect | Mixture | Direct Algorithm |
|--------|---------|------------------|
| Ease of use | Very Easy | Requires knowledge |
| Performance | Good | Can be optimal |
| Flexibility | High | Low |
| Predictability | Medium | High |
| Cost | Variable | Predictable |
| Control | Less | More |

## Advanced Features

### Custom Selection Strategy

```python
class CustomMixture(MixtureOfAlgorithms):
    def analyze_problem(self, problem):
        """Custom problem analysis."""
        analysis = super().analyze_problem(problem)
        
        # Add custom heuristics
        if 'schedule' in problem.lower():
            analysis['recommended'] = 'best_of_n'
        elif 'algorithm' in problem.lower():
            analysis['recommended'] = 'tree_of_thought'
        elif 'code' in problem.lower():
            analysis['recommended'] = 'rebase'
        
        return analysis
```

### Custom Switching Logic

```python
class AdaptiveMixture(MixtureOfAlgorithms):
    def should_switch_algorithm(self, current_algorithm, current_score, iteration):
        """Custom switching logic."""
        # Switch if score below threshold
        if current_score < self.performance_threshold:
            return True
        
        # Switch if not improving
        if iteration > 3 and current_score < 0.7:
            return True
        
        # Don't switch if doing well
        if current_score >= 0.9:
            return False
        
        return super().should_switch_algorithm(
            current_algorithm, current_score, iteration
        )
```

## Best Practices

### 1. Start with Default Settings

```python
# Good for most cases
mixture = MixtureOfAlgorithms(llm_interface=model)
```

### 2. Limit Algorithm Switches

```python
# Avoid excessive switching
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=2,  # Usually sufficient
    llm_interface=model
)
```

### 3. Set Performance Thresholds

```python
# Define acceptable performance
mixture = MixtureOfAlgorithms(
    performance_threshold=0.75,  # Switch if below
    llm_interface=model
)
```

### 4. Monitor Algorithm Selection

```python
result, score, metadata = mixture.run(problem)

# Log selection for analysis
print(f"Selected: {metadata['algorithm_used']}")
print(f"Reason: {metadata['selection_reasoning']}")
print(f"Switches: {metadata['num_switches']}")
```

## Advantages

1. **Automatic optimization**: No manual algorithm selection
2. **Adaptive**: Adjusts to problem characteristics
3. **Robust**: Recovers from poor initial choices
4. **Simple API**: Easy to use for beginners
5. **Production-ready**: Handles diverse problems

## Limitations

1. **Less predictable**: Performance varies by problem
2. **Higher cost**: May use multiple algorithms
3. **Debugging harder**: More complex execution path
4. **Overhead**: Algorithm selection adds latency
5. **Less control**: Automatic decisions may not be optimal

## When to Use Direct Algorithms Instead

Use specific algorithms when:

- **Performance is critical**: Know the best algorithm
- **Cost matters**: Need predictable API usage
- **Debugging needed**: Simpler execution path
- **Domain-specific**: Have expertise in problem type
- **Benchmarking**: Testing specific approaches

## Troubleshooting

### Too Many Switches

```python
# Limit switches
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=1,
    llm_interface=model
)
```

### Poor Algorithm Selection

```python
# Adjust threshold
mixture = MixtureOfAlgorithms(
    performance_threshold=0.7,  # More lenient
    llm_interface=model
)
```

### High Cost

```python
# Use simpler algorithms
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=0,  # Disable switching
    llm_interface=model
)
```

## Example: Complete Usage

```python
from plangen import PlanGen
from plangen.algorithms import MixtureOfAlgorithms
from plangen.visualization import GraphRenderer

# Create model and visualizer
plangen = PlanGen.create()
model = plangen._plangen.model
renderer = GraphRenderer(output_dir="./mixture_viz")

# Create mixture algorithm
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=2,
    performance_threshold=0.75,
    llm_interface=model
)

# Add observer
mixture.add_observer(renderer)

# Solve problem
problem = "Design a real-time chat application with 100k users"
solution, score, metadata = mixture.run(problem)

# Analyze results
print(f"Solution (score {score}):\n{solution}")
print(f"\nAlgorithm journey:")
for step in metadata['algorithm_path']:
    print(f"  - {step['algorithm']}: {step['score']:.2f} ({step['reason']})")

print(f"\nTotal time: {metadata['total_time']:.1f}s")
print(f"Switches made: {metadata['num_switches']}")
```

## Next Steps

- Read [Algorithm Selection Guide](algorithm_selection_guide.md) for manual selection
- See [BestOfN](best_of_n.md), [TreeOfThought](tree_of_thought.md), [REBASE](rebase.md) for details on individual algorithms
- Check [Examples](../examples/mixture_of_algorithms_example.md) for more use cases
