# Models

LLM model interfaces for PlanGEN.

## Overview

PlanGEN supports multiple LLM providers through a common interface. For most use cases, use the high-level [PlanGen](plangen.md) factory methods instead.

## Classes

### BaseModelInterface

Abstract base class defining the model interface contract.

```python
class BaseModelInterface(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str: ...

    @abstractmethod
    def batch_generate(
        self,
        prompts: list[str],
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> list[str]: ...
```

### OpenAIModelInterface

OpenAI API implementation.

```python
from plangen.models import OpenAIModelInterface

model = OpenAIModelInterface(model_name="gpt-4o", temperature=0.7)
response = model.generate("What is 2+2?")
```

Requires `OPENAI_API_KEY` environment variable.

### BedrockModelInterface

AWS Bedrock implementation.

```python
from plangen.models import BedrockModelInterface

model = BedrockModelInterface(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)
response = model.generate("What is 2+2?")
```

Requires AWS credentials configured.

## Custom Models

Implement `BaseModelInterface` to add support for other providers:

```python
from plangen.models import BaseModelInterface

class MyModelInterface(BaseModelInterface):
    def generate(self, prompt, **kwargs) -> str:
        # Your implementation
        pass

    def batch_generate(self, prompts, **kwargs) -> list[str]:
        return [self.generate(p, **kwargs) for p in prompts]
```

## See Also

- [PlanGen](plangen.md) - High-level API with model factory methods
