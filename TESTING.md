# Testing Guide for PlanGEN

This document describes the testing strategy, conventions, and best practices for the PlanGEN project.

## Table of Contents

- [Overview](#overview)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Shared Fixtures](#shared-fixtures)
- [Testing Best Practices](#testing-best-practices)
- [Continuous Integration](#continuous-integration)

## Overview

PlanGEN uses pytest as its primary testing framework, with comprehensive unit tests, integration tests, and regression tests to ensure library reliability and prevent regressions.

### Test Coverage Goals

- **Minimum target coverage**: 80%
- **New code coverage**: 75% for patches
- **Focus areas**: Public API, core algorithms, agents, and model interfaces

## Test Organization

Tests are organized in the `tests/` directory with the following structure:

```
tests/
├── conftest.py                          # Shared fixtures
├── test_api.py                          # Public API tests
├── test_api_integration.py              # API integration tests
├── test_agents.py                       # Agent unit tests
├── test_constraint_agent.py             # ConstraintAgent specific tests
├── test_models.py                       # Model interface tests
├── test_prompts.py                      # Prompt manager tests
├── test_plangen.py                      # PlanGEN class tests
├── test_integration.py                  # End-to-end integration tests
├── test_integration_all_algorithms.py   # Algorithm integration tests
├── test_tree_of_thought.py              # TreeOfThought algorithm tests
├── test_rebase.py                       # REBASE algorithm tests
├── test_mixture_of_algorithms.py        # MixtureOfAlgorithms tests
├── test_visualization.py                # Visualization component tests
├── test_visualization_algorithms.py     # Algorithm visualization tests
└── test_regression_issue_*.py           # Regression tests for specific issues
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
   - `test_agents.py`, `test_models.py`, `test_prompts.py`

2. **Integration Tests**: Test interactions between components
   - `test_integration.py`, `test_api_integration.py`, `test_integration_all_algorithms.py`

3. **Algorithm Tests**: Test specific planning algorithms
   - `test_tree_of_thought.py`, `test_rebase.py`, `test_mixture_of_algorithms.py`

4. **Visualization Tests**: Test graph rendering and visualization
   - `test_visualization.py`, `test_visualization_algorithms.py`

5. **Regression Tests**: Prevent previously fixed bugs from reoccurring
   - `test_regression_issue_*.py`

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestPlanGen

# Run specific test method
pytest tests/test_api.py::TestPlanGen::test_create_default
```

### Running Tests with Coverage

```bash
# Run tests with coverage report
pytest tests/ --cov=plangen --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=plangen --cov-report=html

# Generate XML coverage report (for CI)
pytest tests/ --cov=plangen --cov-report=xml
```

### Running Integration Tests

Some integration tests are skipped by default unless specific environment variables are set:

```bash
# Run integration tests that require API keys
OPENAI_API_KEY=your_key pytest tests/

# Run all integration tests
INTEGRATION_TESTS=1 pytest tests/
```

### Test Markers

```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run only integration tests (if marked)
pytest tests/ -m integration
```

## Test Coverage

### Current Coverage Status

The project maintains test coverage tracking through Codecov. Coverage reports are generated on every pull request and commit to the main branch.

### Coverage Configuration

Coverage settings are defined in:
- `codecov.yml`: Codecov-specific configuration
- `pyproject.toml`: pytest-cov configuration

### Viewing Coverage Reports

1. **Locally**: Run `pytest --cov=plangen --cov-report=html` and open `htmlcov/index.html`
2. **CI/CD**: View coverage reports on Codecov dashboard
3. **Pull Requests**: Coverage changes are commented on PRs automatically

## Writing Tests

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>_<expected_behavior>`

Examples:
```python
def test_extract_constraints_returns_constraints()
def test_solve_with_invalid_input_raises_error()
def test_best_of_n_selects_highest_scoring_solution()
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_constraint_agent_extracts_constraints(mock_model, mock_prompt_manager):
    # Arrange: Set up test data and mocks
    agent = ConstraintAgent(mock_model, mock_prompt_manager)
    problem = "Schedule a meeting"
    mock_model.generate.return_value = "Extracted constraints"

    # Act: Execute the functionality being tested
    result = agent.extract_constraints(problem)

    # Assert: Verify the expected behavior
    assert result == "Extracted constraints"
    mock_model.generate.assert_called_once()
```

### Mocking Strategy

- Use `unittest.mock.MagicMock` for creating mock objects
- Mock external dependencies (API calls, file I/O, etc.)
- Use shared fixtures from `conftest.py` when possible
- Patch at the point of use, not at the definition

Example:
```python
from unittest.mock import patch, MagicMock

@patch("plangen.models.OpenAIModelInterface")
def test_with_openai(mock_openai):
    mock_openai.return_value = MagicMock()
    plangen = PlanGen.with_openai(model_name="gpt-4o")
    assert plangen is not None
```

## Shared Fixtures

The `tests/conftest.py` file provides shared fixtures that can be used across all tests:

- `mock_model`: Mock model interface
- `mock_prompt_manager`: Mock prompt manager
- `sample_problem`: Sample problem statement
- `sample_constraints`: Sample constraints
- `sample_solutions`: Sample solutions
- `temp_directory`: Temporary directory for file operations

### Using Fixtures

```python
def test_my_function(mock_model, sample_problem):
    # Fixtures are automatically injected
    result = my_function(mock_model, sample_problem)
    assert result is not None
```

## Testing Best Practices

### 1. Test Independence

- Each test should be independent and not rely on other tests
- Use fixtures for setup and teardown
- Don't share state between tests

### 2. Test Isolation

- Mock external dependencies
- Use temporary directories for file operations
- Don't make real API calls in unit tests

### 3. Descriptive Test Names

- Test names should clearly describe what is being tested
- Include the expected behavior in the test name

### 4. Test Documentation

- Add docstrings to test methods explaining the purpose
- Document any non-obvious setup or assertions

### 5. Regression Tests

- When fixing a bug, add a regression test
- Name regression tests after the issue number: `test_regression_issue_N.py`
- Include issue number and description in docstrings

Example:
```python
def test_verification_agent_has_verify_solutions_method():
    """Regression test for issue #26: Verify VerificationAgent has verify_solutions method."""
    agent = VerificationAgent(mock_model, mock_prompt_manager)
    assert hasattr(agent, 'verify_solutions')
```

### 6. Edge Cases and Error Handling

- Test boundary conditions
- Test error cases and exceptions
- Verify error messages are meaningful

### 7. Avoid Flaky Tests

- Don't rely on timing or external state
- Use deterministic test data
- Mock random number generators if needed

## Continuous Integration

### GitHub Actions Workflow

Tests run automatically on:
- Every push to main
- Every pull request
- Manual workflow dispatch

The CI pipeline:
1. Runs tests on Python 3.9, 3.10, and 3.11
2. Generates coverage reports
3. Uploads coverage to Codecov
4. Updates coverage badge

### Local Pre-commit Checks

Before committing, run:

```bash
# Run all tests
pytest tests/

# Check code formatting
black --check .

# Run linter
ruff check .

# Type checking
mypy plangen/
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Codecov documentation](https://docs.codecov.io/)
- [Python testing best practices](https://docs.python-guide.org/writing/tests/)

## Contributing

When contributing tests:

1. Ensure all tests pass locally before submitting
2. Add tests for new features
3. Update tests when modifying existing features
4. Maintain or improve code coverage
5. Follow the testing conventions outlined in this document

For questions or issues related to testing, please open an issue on GitHub.
