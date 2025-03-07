# PlanGEN

PlanGEN is a framework for solving complex problems using a multi-agent approach with large language models (LLMs). It implements the PlanGEN workflow described in the paper "PlanGEN: Generative Planning with Large Language Models".

## Features

- Multi-agent workflow for complex problem solving
- Constraint extraction
- Solution generation
- Solution verification
- Solution selection
- Support for multiple LLM backends (OpenAI, AWS Bedrock)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/plangen.git
cd plangen

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

## Usage

### Basic Usage

```python
from plangen import PlanGEN
from plangen.models import OpenAIModelInterface
from plangen.prompts import PromptManager

# Initialize the model interface
model = OpenAIModelInterface(
    model_name="gpt-4",
    api_key="your-api-key"
)

# Initialize the prompt manager
prompt_manager = PromptManager()

# Initialize PlanGEN
plangen = PlanGEN(
    model=model,
    prompt_manager=prompt_manager,
    num_solutions=3
)

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

# Print the results
print("Constraints:", result["constraints"])
print("Selected Solution:", result["selected_solution"]["selected_solution"])
```

### Using AWS Bedrock

```python
from plangen import PlanGEN
from plangen.models import BedrockModelInterface
from plangen.prompts import PromptManager

# Initialize the Bedrock model interface
model = BedrockModelInterface(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0.7,
    max_tokens=1024,
    region="us-east-1"
)

# Initialize the prompt manager
prompt_manager = PromptManager()

# Initialize PlanGEN
plangen = PlanGEN(
    model=model,
    prompt_manager=prompt_manager,
    num_solutions=2
)

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

# Print the results
print("Constraints:", result["constraints"])
print("Selected Solution:", result["selected_solution"]["selected_solution"])
```

### Customizing Prompts

```python
from plangen import PlanGEN
from plangen.models import OpenAIModelInterface
from plangen.prompts import PromptManager

# Initialize the model interface
model = OpenAIModelInterface(
    model_name="gpt-4",
    api_key="your-api-key"
)

# Initialize the prompt manager
prompt_manager = PromptManager()

# Update prompts for better performance
prompt_manager.update_prompt(
    "constraint_extraction",
    """
    You are an expert scheduler. Please analyze the following problem and identify all constraints:
    
    {problem}
    
    List all constraints in the problem, including:
    - Meeting duration
    - Time window
    - Participant availability/unavailability
    - Any other requirements
    
    Format your response as a clear, numbered list of constraints.
    """
)

# Initialize PlanGEN with custom prompts
plangen = PlanGEN(
    model=model,
    prompt_manager=prompt_manager,
    num_solutions=3
)

# Solve a problem
problem = "Your problem statement here"
result = plangen.solve(problem)
```

## Examples

See the `examples` directory for more detailed examples:

- `calendar_scheduling.py`: Calendar scheduling problem using OpenAI
- `calendar_scheduling_bedrock.py`: Calendar scheduling problem using AWS Bedrock

## License

This project is licensed under the MIT License - see the LICENSE file for details.