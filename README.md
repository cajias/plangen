# PlanGEN

[![Tests](https://github.com/cajias/plangen/actions/workflows/python-tests.yml/badge.svg)](https://github.com/cajias/plangen/actions/workflows/python-tests.yml)
[![Lint](https://github.com/cajias/plangen/actions/workflows/python-lint.yml/badge.svg)](https://github.com/cajias/plangen/actions/workflows/python-lint.yml)
[![Docs](https://github.com/cajias/plangen/actions/workflows/docs-validation.yml/badge.svg)](https://github.com/cajias/plangen/actions/workflows/docs-validation.yml)
[![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/cajias/plangen)](https://github.com/cajias/plangen/blob/main/LICENSE)

PlanGEN is a framework for solving complex problems using a multi-agent approach with large language models (LLMs). It implements the PlanGEN workflow described in the paper "PlanGEN: Generative Planning with Large Language Models".

## Features

- Multi-agent workflow for complex problem solving
- Constraint extraction
- Solution generation
- Solution verification
- Solution selection
- Support for multiple LLM backends (OpenAI, AWS Bedrock)
- Multiple interchangeable planning algorithms
- Clean, well-documented public API
- Visualization capabilities

## Documentation

For comprehensive documentation, please see the [docs](docs/index.md) directory:

- [User Guide](docs/user_guide/index.md): Step-by-step guides for using PlanGEN
- [API Reference](docs/api_reference/index.md): Complete reference for all public classes and methods
- [Algorithm Reference](docs/algorithm_reference/index.md): Detailed explanation of planning algorithms
- [Examples](docs/examples/index.md): Code examples for various scenarios

## Installation

### Installing from PyPI (recommended)

PlanGEN is available on PyPI. You can install it directly using pip:

```bash
pip install plangen
```

For the latest development version, you can install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ plangen
```

### Installing with Poetry

Alternatively, you can add PlanGEN to your Poetry project:

```bash
# Add the package to your project
poetry add plangen
```

### Development Installation

For development or contributing to the project, you can install from the source:

```bash
# Clone the repository
git clone https://github.com/cajias/plangen.git
cd plangen

# Using Poetry (recommended)
poetry install
poetry shell

# OR using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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

### Using Different Planning Algorithms

PlanGEN supports multiple planning algorithms that can be used interchangeably:

```python
from plangen.algorithms import BestOfN, TreeOfThought, REBASE, MixtureOfAlgorithms
from plangen.models import OpenAIModelInterface

# Initialize the model interface
model = OpenAIModelInterface(model_name="gpt-4")

# Best of N algorithm
best_of_n = BestOfN(
    n_plans=5,
    sampling_strategy="diverse",
    parallel=True,
    llm_interface=model
)

# Tree of Thought algorithm
tree_of_thought = TreeOfThought(
    branching_factor=3,
    max_depth=5,
    beam_width=2,
    llm_interface=model
)

# REBASE algorithm
rebase = REBASE(
    max_iterations=5,
    improvement_threshold=0.1,
    llm_interface=model
)

# Mixture of Algorithms
mixture = MixtureOfAlgorithms(
    max_algorithm_switches=2,
    llm_interface=model
)

# Use any of the algorithms to solve a problem
problem_statement = "Your problem statement here"
best_plan, score, metadata = best_of_n.run(problem_statement)
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

## Algorithm Components

PlanGEN provides several interchangeable algorithm components:

1. **BaseAlgorithm**: Abstract base class that all algorithms inherit from
2. **BestOfN**: Generates multiple plans and selects the best one based on verification scores
3. **TreeOfThought**: Explores multiple reasoning paths in a tree structure, allowing for backtracking
4. **REBASE**: Uses recursive refinement to improve plans through iterative feedback
5. **MixtureOfAlgorithms**: Dynamically selects the best algorithm for the problem

All algorithms implement a common interface and can be used interchangeably:

```python
# Common interface for all algorithms
best_plan, score, metadata = algorithm.run(problem_statement)
```

## Examples

See the `examples` directory for more detailed examples:

- `calendar_scheduling.py`: Calendar scheduling problem using OpenAI
- `calendar_scheduling_bedrock.py`: Calendar scheduling problem using AWS Bedrock
- `test_best_of_n.py`: Using the Best of N algorithm
- `test_tree_of_thought.py`: Using the Tree of Thought algorithm
- `test_rebase.py`: Using the REBASE algorithm
- `test_verification.py`: Using verification strategies

## License

This project is licensed under the MIT License - see the LICENSE file for details.