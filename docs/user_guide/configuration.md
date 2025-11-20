# Configuration Guide

This guide explains how to configure PlanGEN for different use cases and environments.

## Environment Variables

PlanGEN uses environment variables for API keys and configuration. Create a `.env` file in your project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o

# AWS Bedrock Configuration (if using Bedrock)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Optional: Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Load environment variables in your code:

```python
from dotenv import load_dotenv

load_dotenv()  # Load from .env file
```

## Model Configuration

### Temperature

Temperature controls the randomness of the model's output:

- **Low temperature (0.1-0.3)**: More deterministic and focused output
- **Medium temperature (0.5-0.7)**: Balanced creativity and consistency (recommended)
- **High temperature (0.8-1.0)**: More creative and diverse output

```python
from plangen import PlanGen

# Low temperature for deterministic output
plangen = PlanGen.create(temperature=0.2)

# High temperature for creative solutions
plangen = PlanGen.create(temperature=0.9)
```

### Max Tokens

Control the maximum length of generated responses:

```python
from plangen import PlanGen

# Shorter responses for simple problems
plangen = PlanGen.create(max_tokens=512)

# Longer responses for complex problems
plangen = PlanGen.create(max_tokens=4096)
```

### Model Selection

Choose the appropriate model for your use case:

```python
from plangen import PlanGen

# Fast and cost-effective
plangen = PlanGen.with_openai(model_name="gpt-3.5-turbo")

# Best performance
plangen = PlanGen.with_openai(model_name="gpt-4o")

# For AWS Bedrock
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1"
)
```

## Algorithm Configuration

### Default Algorithm

Configure the default algorithm for your application:

```python
from plangen import PlanGen

plangen = PlanGen.create()

# The solve method uses BestOfN by default
result = plangen.solve(problem)
```

### Custom Algorithm Parameters

Each algorithm has specific parameters:

```python
from plangen import PlanGen

plangen = PlanGen.create()

# BestOfN configuration
result = plangen.solve(
    problem,
    algorithm="best_of_n",
    n_plans=10,  # Generate 10 plans
    sampling_strategy="diverse",  # Use diverse sampling
    parallel=True  # Generate in parallel
)

# TreeOfThought configuration
result = plangen.solve(
    problem,
    algorithm="tree_of_thought",
    branching_factor=3,  # 3 branches per node
    max_depth=5,  # Maximum depth of 5
    beam_width=2  # Keep top 2 branches
)

# REBASE configuration
result = plangen.solve(
    problem,
    algorithm="rebase",
    max_iterations=10,  # Maximum 10 refinement iterations
    improvement_threshold=0.1  # Stop if improvement < 0.1
)
```

## Prompt Configuration

### Custom Prompts

Customize the prompts used by PlanGEN:

```python
from plangen import PlanGen
from plangen.prompts import PromptManager

# Create a custom prompt manager
prompt_manager = PromptManager()

# Update constraint extraction prompt
prompt_manager.update_prompt(
    "constraint_extraction",
    """You are an expert at analyzing problems and identifying constraints.
    
    Problem: {problem}
    
    List all constraints, requirements, and limitations in the problem.
    Format your response as a numbered list."""
)

# Create PlanGen with custom prompts
plangen = PlanGen.with_model(model)
plangen._plangen.prompt_manager = prompt_manager
```

## Verification Configuration

### Custom Verifiers

Use domain-specific verifiers for better validation:

```python
from plangen import PlanGen, Verifiers

plangen = PlanGen.create()

# Use a calendar scheduling verifier
verifier = Verifiers.calendar()

result = plangen.solve(
    problem="Schedule a meeting...",
    verifier=verifier
)
```

### Verification Thresholds

Configure verification score thresholds:

```python
from plangen.algorithms import BestOfN

best_of_n = BestOfN(
    n_plans=5,
    min_score_threshold=0.7,  # Only accept plans with score >= 0.7
    llm_interface=model
)
```

## Visualization Configuration

### Enable Visualization

Configure visualization for debugging and analysis:

```python
from plangen.visualization import GraphRenderer
from plangen.algorithms import TreeOfThought

# Create a graph renderer
renderer = GraphRenderer(output_dir="./visualizations")

# Create algorithm with visualization
tot = TreeOfThought(
    branching_factor=3,
    max_depth=5,
    llm_interface=model
)

# Register the renderer as an observer
tot.add_observer(renderer)

# Run the algorithm (visualization will be generated)
best_plan, score, metadata = tot.run(problem)
```

## Logging Configuration

### Basic Logging

Configure Python logging for PlanGEN:

```python
import logging

# Set logging level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get PlanGEN logger
logger = logging.getLogger('plangen')
logger.setLevel(logging.DEBUG)
```

### Advanced Logging

Configure logging to file:

```python
import logging
from logging.handlers import RotatingFileHandler

# Create file handler
handler = RotatingFileHandler(
    'plangen.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# Add handler to PlanGEN logger
logger = logging.getLogger('plangen')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
```

## Performance Configuration

### Caching

Enable caching for improved performance:

```python
from plangen import PlanGen
from functools import lru_cache

# Cache constraint extraction results
@lru_cache(maxsize=128)
def cached_extract_constraints(problem):
    plangen = PlanGen.create()
    return tuple(plangen.extract_constraints(problem))
```

### Parallel Processing

Enable parallel plan generation:

```python
from plangen import PlanGen

plangen = PlanGen.create()

# Enable parallel processing for BestOfN
result = plangen.solve(
    problem,
    algorithm="best_of_n",
    n_plans=10,
    parallel=True  # Generate plans in parallel
)
```

## Best Practices

1. **Use environment variables** for sensitive information like API keys
2. **Start with default parameters** and adjust based on results
3. **Choose the right model** for your use case (cost vs. performance)
4. **Enable logging** for production environments
5. **Use custom verifiers** for domain-specific problems
6. **Configure appropriate timeouts** for API calls
7. **Monitor API usage** and costs
8. **Test configurations** with simple problems first

## Next Steps

- Learn about [Models](models.md) in detail
- Explore [Custom Prompts](custom_prompts.md)
- See [Verification](verification.md) for advanced verification strategies
