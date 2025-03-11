# Installation Guide

This guide will help you install PlanGEN and set up your environment.

## Requirements

PlanGEN requires:
- Python 3.9 or later (up to 3.12)
- Dependencies listed in `pyproject.toml`

## Installation Options

### Using Poetry (Recommended)

[Poetry](https://python-poetry.org/) is the recommended way to install PlanGEN, as it handles dependency management and virtual environments automatically.

1. First, install Poetry if you don't have it already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/plangen.git
   cd plangen
   ```

3. Install dependencies and create a virtual environment:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Using pip

Alternatively, you can install PlanGEN using pip:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/plangen.git
   cd plangen
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Setting Up API Keys

PlanGEN supports multiple LLM providers. Depending on which provider you plan to use, you'll need to set up the appropriate API keys:

### OpenAI

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your-api-key-here
```

For persistent configuration, add it to your `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

### AWS Bedrock

For AWS Bedrock, you need to set up your AWS credentials. The recommended way is to use the AWS CLI:

```bash
aws configure
```

Alternatively, you can set environment variables or use a `.env` file:

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## Verifying Installation

To verify that PlanGEN is installed correctly, run one of the example scripts:

```bash
python examples/simple_example.py
```

If everything is set up correctly, you should see output from PlanGEN solving a simple problem.

## Next Steps

Now that you have PlanGEN installed, you can:

- Follow the [Quick Start Guide](quickstart.md) to learn how to use PlanGEN
- Explore the [Examples](../examples/index.md) to see how to use PlanGEN for various use cases
- Read the [API Reference](../api_reference/index.md) for detailed information about PlanGEN's API