# Project-Specific Claude Directives

## Important Note
When working with this project, Claude should also load CLAUDE.global.md for additional directives.

## Project Context
This is a Python library focused on plan generation and execution using various LLM algorithms.

## Override: GitHub Interaction Guidelines
- For this project, monitor issues labeled "enhancement" and "bug"
- When suggesting code changes, focus on maintaining the existing architecture pattern

## Project-Specific Commands
- When I comment "generate test cases", analyze the current module and generate comprehensive tests
- When I comment "optimize performance", focus on identifying performance bottlenecks

## Special Tools and Dependencies
- Python 3.7+
- Test command: `pytest tests/`
- Lint command: `ruff check .`

## Language Selection
This project is primarily a Python project. Claude should refer to the language-specific Python directives.
