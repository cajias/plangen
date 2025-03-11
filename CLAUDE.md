# Project-Specific Claude Directives

## Important Note
When working with this project, Claude should also load CLAUDE.global.md for additional directives.

## Project Context
PlanGEN is a Python framework for solving complex problems using large language models (LLMs) in a multi-agent approach. It implements the workflow described in the paper "PlanGEN: Generative Planning with Large Language Models." The framework enables constraint extraction, solution generation, verification, and solution selection through various planning algorithms.

## Architecture Overview
- **Multi-agent system**: Specialized agents for constraint extraction, solution generation, verification, and selection
- **Planning algorithms**: BestOfN, TreeOfThought, REBASE, and MixtureOfAlgorithms
- **Model support**: OpenAI and AWS Bedrock integrations
- **Template-based prompting**: Jinja2 templates for customizable LLM interactions
- **Visualization capabilities**: Graph-based visualization of planning processes

## Public API
The project provides a clean public API through the following main classes:
- `PlanGen`: Main entry point with factory methods for easy initialization
- `Algorithm`: Interface for different planning algorithms
- `Visualization`: Tools for visualizing planning processes
- `Verifiers`: Factory for domain-specific verification tools

## Override: GitHub Interaction Guidelines
- For this project, monitor issues labeled "enhancement" and "bug"
- When suggesting code changes, focus on maintaining the existing architecture pattern

## Project-Specific Commands
- When I comment "generate test cases", analyze the current module and generate comprehensive tests
- When I comment "optimize performance", focus on identifying performance bottlenecks
- When I comment "visualize plan", implement visualization for the current planning algorithm

## Special Tools and Dependencies
- Python 3.9+ (supports 3.9-3.12)
- Test command: `pytest tests/`
- Lint command: `ruff check .`
- Format command: `black .`
- Type check: `mypy .`

## Key Dependencies
- openai ≥1.12.0
- pydantic ≥2.6.1
- tenacity ≥8.2.3
- numpy ≥1.20.0
- langgraph ≥0.1.11
- boto3 ≥1.34.0
- jinja2 ≥3.1.2
- python-dotenv ≥1.0.0

## Development Environment Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/plangen.git
cd plangen

# Using Poetry (recommended)
poetry install
poetry shell

# Alternative: Using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Example Usage (Simple API)
```python
from plangen import PlanGen

# Create PlanGen instance (automatically uses OpenAI's gpt-4o if OPENAI_API_KEY is set)
plangen = PlanGen.create()

# Alternative: Explicitly specify model
# plangen = PlanGen.with_openai(model_name="gpt-4o")
# plangen = PlanGen.with_bedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

# Solve a problem
problem = "Your problem statement here"
result = plangen.solve(problem)
print(result["selected_solution"])
```

## Example Usage (Legacy API)
```python
from plangen import PlanGEN
from plangen.models import OpenAIModelInterface
from plangen.prompts import PromptManager

# Initialize components
model = OpenAIModelInterface(model_name="gpt-4")
prompt_manager = PromptManager()
plangen = PlanGEN(model=model, prompt_manager=prompt_manager, num_solutions=3)

# Solve a problem
problem = "Your problem statement here"
result = plangen.solve(problem)
```

## Documentation
Comprehensive documentation is available in the docs/ directory:
- API Reference: Complete reference for all public classes and methods
- User Guide: Step-by-step guides for common use cases
- Algorithm Reference: Detailed explanation of available planning algorithms
- Examples: Annotated example code for various scenarios

## Language Selection
This project is primarily a Python project. Claude should refer to the language-specific Python directives.
