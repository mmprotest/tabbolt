# Contributing to TabBolt

Thanks for your interest in improving TabBolt! We welcome bug reports, feature requests, and pull requests. This document provides a quick overview of the development workflow.

## Getting Started

1. Fork the repository and clone your fork.
2. Install dependencies: `pip install -e .[dev]`
3. Install the pre-commit hooks: `pre-commit install`

## Development Workflow

- **Formatting**: Run `ruff --fix` and `black .` before committing.
- **Typing**: Run `mypy` to ensure type hints stay accurate.
- **Testing**: All code changes must be covered by tests. Use `pytest --cov` locally.
- **Docs**: Update README.md for user-facing changes.

## Tests

All tests generate PDFs on the fly using reportlab, so no assets are required. If you add new fixtures, make sure they are deterministic and self-contained.

## Commit Messages

We follow conventional commits loosely (e.g., `feat:`, `fix:`). Provide enough context for reviewers to understand the motivation.

## Pull Requests

- Include a summary of changes and testing evidence.
- Link to related issues.
- Ensure CI is green before requesting a review.

Thanks for contributing!
