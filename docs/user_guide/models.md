# Models Guide

PlanGEN supports multiple language model backends through a unified interface. This guide explains how to use different models and configure them for your needs.

## Supported Models

PlanGEN currently supports:

- **OpenAI Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **AWS Bedrock Models**: Claude 3 (Opus, Sonnet, Haiku), Amazon Titan

## OpenAI Models

### Setup

Install the required dependency (already included in PlanGEN):

```bash
pip install openai
```

Set your API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or in a `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

### Using OpenAI Models

```python
from plangen import PlanGen

# Use default model (gpt-4o)
plangen = PlanGen.with_openai()

# Use specific model
plangen = PlanGen.with_openai(
    model_name="gpt-4-turbo",
    temperature=0.7,
    max_tokens=2048
)

# Use GPT-3.5 for faster, cheaper responses
plangen = PlanGen.with_openai(
    model_name="gpt-3.5-turbo",
    temperature=0.5
)
```

### Available OpenAI Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gpt-4o` | Latest GPT-4 optimized model | Best overall performance |
| `gpt-4-turbo` | Fast GPT-4 model | Complex reasoning tasks |
| `gpt-4` | Original GPT-4 | Highest quality, slower |
| `gpt-3.5-turbo` | Fast and cost-effective | Simple tasks, prototyping |

### OpenAI Model Parameters

```python
plangen = PlanGen.with_openai(
    model_name="gpt-4o",
    temperature=0.7,          # Randomness (0.0-2.0)
    max_tokens=2048,          # Maximum response length
    top_p=1.0,                # Nucleus sampling (0.0-1.0)
    frequency_penalty=0.0,    # Reduce repetition (-2.0-2.0)
    presence_penalty=0.0,     # Encourage new topics (-2.0-2.0)
)
```

## AWS Bedrock Models

### Setup

Install AWS SDK (already included in PlanGEN):

```bash
pip install boto3
```

Configure AWS credentials:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Using Bedrock Models

```python
from plangen import PlanGen

# Use default model (Claude 3 Sonnet)
plangen = PlanGen.with_bedrock()

# Use specific model
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-opus-20240229-v1:0",
    region="us-east-1",
    temperature=0.7,
    max_tokens=2048
)

# Use Claude 3 Haiku for faster responses
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region="us-west-2"
)
```

### Available Bedrock Models

| Model ID | Description | Best For |
|----------|-------------|----------|
| `anthropic.claude-3-opus-20240229-v1:0` | Highest capability | Most complex tasks |
| `anthropic.claude-3-sonnet-20240229-v1:0` | Balanced performance | General use (default) |
| `anthropic.claude-3-haiku-20240307-v1:0` | Fast and efficient | Simple tasks, high throughput |
| `amazon.titan-text-express-v1` | AWS native model | AWS-specific workloads |

### Bedrock Model Parameters

```python
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1",
    temperature=0.7,          # Randomness (0.0-1.0)
    max_tokens=2048,          # Maximum response length
    top_p=0.9,                # Nucleus sampling (0.0-1.0)
    top_k=250,                # Top-K sampling
)
```

## Custom Model Interface

You can implement your own model interface for other providers:

```python
from typing import List, Dict, Any, Optional
from plangen.models.base import ModelProtocol

class CustomModelInterface(ModelProtocol):
    """Custom model interface implementation."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
    
    def generate(
        self,
        system_message: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response from the model."""
        # Implement your model API call here
        response = your_model_api.generate(
            system=system_message,
            user=user_message,
            temperature=temperature or 0.7,
            max_tokens=max_tokens or 1024,
        )
        return response.text
    
    def batch_generate(
        self,
        prompts: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> List[str]:
        """Generate responses for multiple prompts."""
        return [
            self.generate(
                prompt["system"],
                prompt["user"],
                temperature,
                max_tokens,
            )
            for prompt in prompts
        ]

# Use your custom model
from plangen import PlanGen

model = CustomModelInterface(model_name="my-model")
plangen = PlanGen.with_model(model)
```

## Model Selection Guidelines

### By Use Case

| Use Case | Recommended Model | Reason |
|----------|------------------|--------|
| Production applications | GPT-4o, Claude 3 Sonnet | Best balance of quality and speed |
| Complex reasoning | GPT-4 Turbo, Claude 3 Opus | Highest capability |
| High-throughput systems | GPT-3.5 Turbo, Claude 3 Haiku | Fast and cost-effective |
| Prototyping | GPT-3.5 Turbo | Quick iteration, low cost |
| AWS-native applications | Claude 3 on Bedrock | Better AWS integration |

### By Cost

From least to most expensive (per token):

1. GPT-3.5 Turbo
2. Claude 3 Haiku
3. Claude 3 Sonnet
4. GPT-4o
5. GPT-4 Turbo
6. Claude 3 Opus
7. GPT-4

### By Performance

From fastest to slowest:

1. GPT-3.5 Turbo
2. Claude 3 Haiku
3. GPT-4o
4. Claude 3 Sonnet
5. GPT-4 Turbo
6. Claude 3 Opus
7. GPT-4

## Model Comparison

### OpenAI vs. AWS Bedrock

| Feature | OpenAI | AWS Bedrock |
|---------|--------|-------------|
| Setup complexity | Simple | Moderate (requires AWS) |
| Pricing model | Pay-per-token | Pay-per-token |
| Model variety | GPT models only | Multiple providers |
| Integration | Direct API | Through AWS SDK |
| Enterprise features | Limited | Advanced (VPC, IAM) |

## Best Practices

### 1. Start with Balanced Models

Begin with GPT-4o or Claude 3 Sonnet for general use:

```python
# Good default choice
plangen = PlanGen.with_openai(model_name="gpt-4o")
```

### 2. Use Cheaper Models for Simple Tasks

For constraint extraction or simple verification:

```python
# Use cheaper model for simple operations
cheap_plangen = PlanGen.with_openai(model_name="gpt-3.5-turbo")
constraints = cheap_plangen.extract_constraints(problem)

# Use powerful model for complex reasoning
powerful_plangen = PlanGen.with_openai(model_name="gpt-4o")
result = powerful_plangen.solve(problem, constraints=constraints)
```

### 3. Adjust Temperature by Task

- **Low temperature (0.1-0.3)**: Verification, consistency
- **Medium temperature (0.5-0.7)**: General planning
- **High temperature (0.8-1.0)**: Creative solutions

```python
# Deterministic verification
verifier = PlanGen.create(temperature=0.2)

# Creative solution generation
generator = PlanGen.create(temperature=0.8)
```

### 4. Monitor Costs

Track API usage and costs:

```python
import logging

# Enable logging to monitor API calls
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('plangen.models')

# Log will show API call details
```

### 5. Implement Fallbacks

Use multiple models for reliability:

```python
def solve_with_fallback(problem):
    try:
        # Try primary model
        plangen = PlanGen.with_openai(model_name="gpt-4o")
        return plangen.solve(problem)
    except Exception as e:
        # Fallback to alternative model
        print(f"Primary model failed: {e}, trying fallback...")
        plangen = PlanGen.with_bedrock()
        return plangen.solve(problem)
```

## Troubleshooting

### API Key Issues

```python
# Check if API key is set
import os

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not set")
```

### Rate Limiting

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def solve_with_retry(problem):
    plangen = PlanGen.create()
    return plangen.solve(problem)
```

### Timeout Issues

```python
# Set shorter max_tokens for faster responses
plangen = PlanGen.create(max_tokens=512)
```

## Next Steps

- Learn about [Configuration](configuration.md) for advanced settings
- Explore [Custom Prompts](custom_prompts.md) to optimize model behavior
- See [Examples](../examples/index.md) for practical use cases
