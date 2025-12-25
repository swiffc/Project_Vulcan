# Contributing to Project Vulcan

Thank you for your interest in contributing to Project Vulcan! This document outlines the contribution process and the standards we follow.

## Code Style

-   **Python:** We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. We use `black` for formatting and `ruff` for linting.
-   **TypeScript/JavaScript:** We follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript). We use `prettier` for formatting and `eslint` for linting.

## Pull Request Process

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with a clear and concise commit message.
4.  Push your changes to your fork.
5.  Create a pull request to the `main` branch of the original repository.
6.  Make sure all tests and linting checks pass in the CI pipeline.

## Testing

-   All new features and bug fixes must include tests.
-   Python tests are written using `pytest`.
-   TypeScript/JavaScript tests are written using `jest`.

## Documentation

-   All new features must be documented in the `README.md` and `docs/` directory.
-   API endpoints must be documented in `docs/API.md`.
