```
██████╗ ██╗      █████╗ ███╗   ██╗ ██████╗ ███████╗███╗   ██╗
██╔══██╗██║     ██╔══██╗████╗  ██║██╔════╝ ██╔════╝████╗  ██║
██████╔╝██║     ███████║██╔██╗ ██║██║  ███╗█████╗  ██╔██╗ ██║
██╔═══╝ ██║     ██╔══██║██║╚██╗██║██║   ██║██╔══╝  ██║╚██╗██║
██║     ███████╗██║  ██║██║ ╚████║╚██████╔╝███████╗██║ ╚████║
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝
```

<p align="center"><em>An implementation of Google's PlanGen multi-agent planning framework</em></p>

<p align="center">
  <img src="https://img.shields.io/github/languages/top/cajias/plangen?style=for-the-badge" alt="Language">
  <a href="https://github.com/cajias/plangen/actions"><img src="https://img.shields.io/github/actions/workflow/status/cajias/plangen/python-tests.yml?style=for-the-badge" alt="Build"></a>
  <a href="https://github.com/cajias/plangen/stargazers"><img src="https://img.shields.io/github/stars/cajias/plangen?style=for-the-badge" alt="Stars"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
</p>

**PlanGEN is a multi-agent framework for solving complex problems with large language models** — an open implementation of the workflow from the paper [*PlanGEN: Generative Planning with Large Language Models*](https://github.com/cajias/plangen). It coordinates specialized agents to extract constraints, generate candidate plans, verify them, and select the best one. Built for researchers and engineers who want pluggable planning algorithms (Best-of-N, Tree-of-Thought, REBASE, Mixture-of-Algorithms) behind a clean Python API.

<table>
<tr><td><b>Multi-agent workflow</b></td><td>Dedicated <code>ConstraintAgent</code>, <code>SolutionAgent</code>, <code>VerificationAgent</code>, and <code>SelectionAgent</code> collaborate to turn a raw problem into a verified, selected plan.</td></tr>
<tr><td><b>Interchangeable algorithms</b></td><td>Swap planning strategies without changing your code: <code>BestOfN</code>, <code>TreeOfThought</code>, <code>REBASE</code>, and <code>MixtureOfAlgorithms</code> share a common <code>run()</code> interface.</td></tr>
<tr><td><b>Multiple LLM backends</b></td><td>First-class support for OpenAI and AWS Bedrock through a unified model protocol — <code>PlanGen.with_openai(...)</code> and <code>PlanGen.with_bedrock(...)</code>.</td></tr>
<tr><td><b>Clean public API</b></td><td>A fluent <code>PlanGen</code> facade hides the internals; the legacy <code>PlanGEN</code> class remains for backward compatibility.</td></tr>
<tr><td><b>Pluggable verification</b></td><td>Bring your own verifier via the <code>Verifiers</code> helpers to score plans against domain-specific constraints.</td></tr>
<tr><td><b>Visualization</b></td><td>Render plan graphs and observe the planning process with the built-in <code>Visualization</code> and observer utilities (NetworkX + Matplotlib).</td></tr>
<tr><td><b>Customizable prompts</b></td><td>Override any stage's prompt through <code>PromptManager</code> for tighter control over agent behavior.</td></tr>
</table>

## Installation

PlanGEN targets Python 3.9–3.12.

```bash
# From PyPI
pip install plangen

# With Poetry
poetry add plangen
```

For the latest development build from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ plangen
```

See [Development](#development) for a source install.

## Usage

PlanGEN is a Python library. The recommended entry point is the fluent `PlanGen` facade.

```python
from plangen import PlanGen

# Configure a backend (reads OPENAI_API_KEY from the environment)
plangen = PlanGen.with_openai(model_name="gpt-4o")

problem = """
Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
Walter: Busy at 9:00-14:30, 15:30-17:00.
Find an earliest time slot that works for all participants.
"""

# Default multi-agent workflow
result = plangen.solve(problem)
print(result["selected_solution"])
```

### Choosing an algorithm

`solve()` accepts an `algorithm` name and forwards extra parameters to it:

```python
result = plangen.solve(
    problem,
    algorithm="best_of_n",   # "default" | "best_of_n" | "tree_of_thought" | "rebase"
    n_plans=5,
)
```

### Using AWS Bedrock

```python
from plangen import PlanGen

plangen = PlanGen.with_bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1",
)
result = plangen.solve(problem)
```

### Driving an algorithm directly

Every algorithm exposes the same `run()` signature, returning the best plan, its score, and metadata:

```python
from plangen.algorithms import BestOfN, TreeOfThought, REBASE, MixtureOfAlgorithms
from plangen.models import OpenAIModelInterface

model = OpenAIModelInterface(model_name="gpt-4o")

best_of_n = BestOfN(n_plans=5, sampling_strategy="diverse", parallel=True, llm_interface=model)
best_plan, score, metadata = best_of_n.run(problem)
```

More runnable scripts live in the [`examples/`](examples/) directory (e.g. `calendar_scheduling.py`, `test_best_of_n.py`, `test_tree_of_thought.py`, `test_rebase.py`).

## Configuration

PlanGEN reads credentials from environment variables (a [`.env`](.env.example) file is supported via `python-dotenv`):

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | API key for the OpenAI backend. |
| `AWS_PROFILE` | AWS profile for the Bedrock backend. |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` | Explicit AWS credentials if not using a profile. |

Copy `.env.example` to `.env` and fill in your values to get started.

## How it works

PlanGEN runs a problem through a four-stage multi-agent pipeline; a planning algorithm orchestrates the solution/verification loop:

```
problem
  │
  ├─▶ ConstraintAgent   ── extract constraints from the problem
  │
  ├─▶ SolutionAgent     ── generate candidate plans
  │        ▲   │
  │        │   ▼
  ├─▶ VerificationAgent ── score plans against constraints  ◀─┐
  │                                                            │ algorithm loop
  ├─▶ (BestOfN | TreeOfThought | REBASE | MixtureOfAlgorithms)─┘
  │
  └─▶ SelectionAgent    ── pick the best verified plan
            │
            ▼
        SolveResult
```

The chosen algorithm decides how solutions are explored — sampling many in parallel (Best-of-N), branching and backtracking (Tree-of-Thought), iterative refinement (REBASE), or dynamically switching strategies (Mixture-of-Algorithms).

## Development

The project uses [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/cajias/plangen.git
cd plangen

# Install all dependencies (including dev tooling)
poetry install
poetry shell

# OR with pip from source
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Common tasks:

```bash
poetry run pytest            # run the test suite
poetry run ruff check .      # lint
poetry run black .           # format
poetry run mypy plangen      # type-check
```

CI runs the test suite across Python 3.9, 3.10, and 3.11 via the [`python-tests.yml`](.github/workflows/python-tests.yml) workflow.

## License

No `LICENSE` file is currently present in this repository. The project metadata (`pyproject.toml` / `setup.py`) declares the **MIT License**, but until a `LICENSE` file is added the licensing terms are not formally distributed with the source. Please open an issue if you need clarification before relying on it.
