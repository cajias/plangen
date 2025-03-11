# PlanGen

The `PlanGen` class is the main entry point for the PlanGEN framework, providing a simplified interface for solving problems using large language models.

```python
from plangen import PlanGen
```

## Factory Methods

### `PlanGen.create`

```python
@classmethod
def create(
    cls,
    model: Optional[str] = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    api_key: Optional[str] = None,
    **kwargs,
) -> "PlanGen"
```

Create a new PlanGen instance with simplified configuration.

**Parameters:**
- `model`: Model identifier string ('gpt-4o', 'claude-3-sonnet', etc.)
- `temperature`: Temperature for generation (0.0-1.0)
- `max_tokens`: Maximum tokens to generate (None for model default)
- `api_key`: Optional API key (if not provided, uses environment variables)
- `**kwargs`: Additional parameters passed to the model

**Returns:**
- Configured PlanGen instance

**Example:**
```python
# Create with default model (gpt-4o)
plangen = PlanGen.create()

# Create with custom parameters
plangen = PlanGen.create(
    model="gpt-4-turbo",
    temperature=0.5,
    max_tokens=2048
)
```

### `PlanGen.with_model`

```python
@classmethod
def with_model(cls, model: ModelProtocol) -> "PlanGen"
```

Create a PlanGen instance with a custom model implementation.

**Parameters:**
- `model`: Custom model instance implementing the ModelProtocol

**Returns:**
- Configured PlanGen instance

**Example:**
```python
from my_custom_models import MyCustomModel

# Create a custom model
model = MyCustomModel()

# Create PlanGen with custom model
plangen = PlanGen.with_model(model)
```

### `PlanGen.with_openai`

```python
@classmethod
def with_openai(
    cls,
    model_name: str = "gpt-4o",
    api_key: Optional[str] = None,
    **kwargs,
) -> "PlanGen"
```

Create a PlanGen instance with OpenAI model.

**Parameters:**
- `model_name`: OpenAI model name
- `api_key`: OpenAI API key (if not provided, uses OPENAI_API_KEY)
- `**kwargs`: Additional parameters passed to the model

**Returns:**
- Configured PlanGen instance with OpenAI model

**Example:**
```python
# Create with default OpenAI model (gpt-4o)
plangen = PlanGen.with_openai()

# Create with custom OpenAI model and parameters
plangen = PlanGen.with_openai(
    model_name="gpt-3.5-turbo",
    temperature=0.8,
    max_tokens=512
)
```

### `PlanGen.with_bedrock`

```python
@classmethod
def with_bedrock(
    cls,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
    region: str = "us-east-1",
    **kwargs,
) -> "PlanGen"
```

Create a PlanGen instance with AWS Bedrock model.

**Parameters:**
- `model_id`: Bedrock model ID
- `region`: AWS region
- `**kwargs`: Additional parameters passed to the model

**Returns:**
- Configured PlanGen instance with Bedrock model

**Example:**
```python
# Create with default Bedrock model (Claude 3 Sonnet)
plangen = PlanGen.with_bedrock()

# Create with custom Bedrock model and parameters
plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-opus-20240229-v1:0",
    region="us-west-2",
    temperature=0.6
)
```

## Methods

### `solve`

```python
def solve(
    self,
    problem: str,
    algorithm: str = "default",
    verifier: Optional[VerifierProtocol] = None,
    **algorithm_params,
) -> Dict[str, Any]
```

Solve a problem using the PlanGEN workflow.

**Parameters:**
- `problem`: Problem statement to solve
- `algorithm`: Algorithm to use ('default', 'best_of_n', 'tree_of_thought', 'rebase', 'mixture')
- `verifier`: Optional custom verifier for specialized verification
- `**algorithm_params`: Additional parameters for the specific algorithm

**Returns:**
- Dictionary with the solution and intermediate results

**Example:**
```python
# Solve a problem using the default workflow
result = plangen.solve("Design an algorithm to find the kth largest element in an unsorted array.")

# Solve a problem using a specific algorithm
result = plangen.solve(
    "Design an algorithm to find the kth largest element in an unsorted array.",
    algorithm="best_of_n",
    n_plans=5
)
```

### `generate_plan`

```python
def generate_plan(
    self,
    problem: str,
    constraints: Optional[List[str]] = None,
    **kwargs,
) -> str
```

Generate a single plan for the given problem.

**Parameters:**
- `problem`: Problem statement
- `constraints`: Optional list of constraints (extracted automatically if not provided)
- `**kwargs`: Additional parameters for generation

**Returns:**
- Generated plan

**Example:**
```python
# Generate a plan with automatically extracted constraints
plan = plangen.generate_plan("Find an algorithm to sort a list of numbers.")

# Generate a plan with predefined constraints
constraints = [
    "The algorithm should have O(n log n) time complexity",
    "The algorithm should be stable",
    "The algorithm should use O(1) extra space"
]
plan = plangen.generate_plan("Find an algorithm to sort a list of numbers.", constraints)
```

### `extract_constraints`

```python
def extract_constraints(self, problem: str) -> List[str]
```

Extract constraints from a problem statement.

**Parameters:**
- `problem`: Problem statement

**Returns:**
- List of extracted constraints

**Example:**
```python
constraints = plangen.extract_constraints(
    "Schedule a 30-minute meeting for 3 people. Alexander is busy from 9-10am and 2-3pm."
)
print(constraints)
# ['Meeting duration: 30 minutes', 'Alexander is busy from 9-10am', 'Alexander is busy from 2-3pm']
```

### `verify_plan`

```python
def verify_plan(
    self,
    problem: str,
    plan: str,
    constraints: Optional[List[str]] = None,
    verifier: Optional[VerifierProtocol] = None,
) -> Tuple[str, float]
```

Verify a plan against constraints.

**Parameters:**
- `problem`: Problem statement
- `plan`: Plan to verify
- `constraints`: Optional list of constraints (extracted automatically if not provided)
- `verifier`: Optional custom verifier

**Returns:**
- Tuple of (feedback, score)

**Example:**
```python
# Verify a plan with automatically extracted constraints
feedback, score = plangen.verify_plan(
    "Find an algorithm to sort a list of numbers.",
    "I will use QuickSort to sort the list. QuickSort works by..."
)
print(f"Score: {score}, Feedback: {feedback}")

# Verify with a custom verifier
from plangen import Verifiers
verifier = Verifiers.math()
feedback, score = plangen.verify_plan(
    "Solve the equation 2x + 3 = 7.",
    "x = 2",
    verifier=verifier
)
```