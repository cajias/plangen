# PlanGEN Developer Handbook

This handbook equips new contributors with a deep understanding of PlanGEN's goals, architecture, and development workflow. Use it as a reference before each work session to refresh how the pieces fit together.

## Mission and Features

PlanGEN tackles complex problems by orchestrating multiple language-model agents. The framework extracts constraints, proposes candidate plans, verifies them, and selects the best answer, while supporting multiple LLM backends and interchangeable planning algorithms【F:README.md†L9-L21】.

### Core capabilities
- Multi‑agent workflow for constraint extraction, plan generation, verification, and selection【F:README.md†L13-L21】
- Pluggable algorithms and model backends
- Rich visualization and a clean public API

## Architectural Overview

### Agents
All reasoning steps are performed by specialized agents built on a common interface.

- **BaseAgent** defines shared LLM wiring and helper methods for prompt generation and model calls【F:plangen/agents/base_agent.py†L1-L76】
- **ConstraintAgent** extracts problem constraints with a structured prompt template and response parsing【F:plangen/agents/constraint_agent.py†L1-L70】
- **SolutionAgent** turns constraints into candidate solutions, generating multiple options when requested【F:plangen/agents/solution_agent.py†L1-L60】
- **VerificationAgent** evaluates plans using domain-aware verifiers and returns feedback and scores【F:plangen/agents/verification_agent.py†L1-L62】
- **SelectionAgent** compares verified solutions and chooses the best candidate via prompt‑driven reasoning【F:plangen/agents/selection_agent.py†L1-L78】

### Algorithms
Planning strategies inherit from `BaseAlgorithm`, which supplies constraint extraction, plan generation, verification hooks, and observer support for visualization【F:plangen/algorithms/base_algorithm.py†L1-L124】.

- **BestOfN** generates N plans and picks the highest‑scoring one; supports diverse sampling and parallel generation【F:plangen/algorithms/best_of_n.py†L1-L112】
- **TreeOfThought** explores reasoning paths in a branching search tree with beam pruning and optional domain templates【F:plangen/algorithms/tree_of_thought.py†L1-L120】
- **REBASE** iteratively refines a plan until scores stop improving, tracking feedback at each step【F:plangen/algorithms/rebase.py†L1-L119】
- **MixtureOfAlgorithms** dynamically switches among BestOfN, TreeOfThought, and REBASE based on problem characteristics【F:plangen/algorithms/mixture_of_algorithms.py†L1-L158】

### Models
Language model access is abstracted through interfaces so algorithms remain backend‑agnostic.

- **OpenAIModelInterface** wraps OpenAI chat completions with retry logic and batching support【F:plangen/models/openai_model.py†L1-L106】
- **BedrockModelInterface** targets AWS Bedrock models, handling both Anthropic Claude and Amazon Titan styles【F:plangen/models/bedrock_model.py†L1-L139】

### Prompts
`PromptManager` loads Jinja2 templates, renders system messages, and allows runtime prompt overrides for experimentation【F:plangen/prompts/prompt_manager.py†L1-L86】.

### Verification
Domain‑specific verifiers plug into a common interface.

- **BaseVerifier** specifies the contract for `verify_solution`, `is_applicable`, and domain constraint extraction【F:plangen/verification/base_verifier.py†L1-L44】
- **VerifierFactory** registers available verifiers (e.g., math) and selects an appropriate one for each problem【F:plangen/verification/verifier_factory.py†L1-L62】

### Visualization
`GraphRenderer` observes algorithm progress and produces graphs for Tree of Thought exploration, REBASE refinements, or Best‑of‑N comparisons【F:plangen/visualization/graph_renderer.py†L1-L146】.

### Public API and Exports
For end users, the `PlanGen` wrapper in `api.py` offers simplified constructors for different model providers and a uniform `solve` interface【F:plangen/api.py†L1-L120】. Top‑level exports in `plangen.__init__` expose `PlanGen`, algorithm helpers, visualization utilities, and agent classes【F:plangen/__init__.py†L1-L42】.

## Documentation and Examples
Comprehensive guides, API references, and algorithm tutorials live under `docs/` with runnable examples in `examples/`【F:README.md†L23-L30】.

## Development Workflow

1. **Setup**
   ```bash
   poetry install  # or: python -m venv .venv && source .venv/bin/activate && pip install -e .
   ```
2. **Quality checks**
   ```bash
   PYENV_VERSION=3.10.17 pytest        # run tests
   ruff .                               # linting
   black .                              # formatting
   isort .                              # import sorting
   mypy .                               # type checking
   ```
   Tooling is configured in `pyproject.toml` under development dependencies【F:pyproject.toml†L45-L51】【F:pyproject.toml†L57-L68】

## Quick Tips
- Examine `tests/` for end‑to‑end usage of agents and algorithms.
- Use visualization observers during algorithm development to understand search behavior.
- Keep prompts and templates under version control; small changes can have large effects.

Revisit this handbook whenever you need a refresher on how PlanGEN pieces interact or where to extend the system.
