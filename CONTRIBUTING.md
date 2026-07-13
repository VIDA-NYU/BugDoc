# Contributing to BugDoc

Thank you for your interest in contributing to BugDoc! This guide will help you get started with development.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VIDA-NYU/BugDoc.git
   cd BugDoc
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   
   On Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```
   
   On Windows:
   ```bash
   .venv\Scripts\activate
   ```

4. **Install the project in development mode:**
   ```bash
   pip install -e "bugdoc_api[dev]"
   pip install -e bugdoc_cli
   ```

5. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

This will set up automatic code quality checks before each commit.

## Running Tests Locally

### Run all tests

```bash
pytest test/ -v
```

### Run tests with coverage

```bash
pytest test/ -v --cov=bugdoc --cov=bugdoc_cli --cov-report=html
```

Then open `htmlcov/index.html` to view the coverage report.

### Run a specific test file

```bash
pytest test/test_standalone.py -v
```

### Run a specific test

```bash
pytest test/test_standalone.py::TestStandaloneModeBase::test_standalone_mode_initialization -v
```

### Run tests with markers

```bash
# Run only unit tests
pytest test/ -v -m unit

# Run integration tests
pytest test/ -v -m integration

# Skip slow tests
pytest test/ -v -m "not slow"
```

## Code Quality

### Pre-commit hooks

Pre-commit hooks will automatically run quality checks before each commit. These checks include:

- **Code formatting** (black)
- **Import sorting** (isort)
- **Linting** (flake8)
- **Type checking** (mypy)
- **Security scanning** (bandit)
- **General checks** (trailing whitespace, merge conflicts, etc.)

To manually run these checks:

```bash
pre-commit run --all-files
```

### Manual formatting and linting

If you need to run individual tools:

```bash
# Format code with black
black bugdoc_api/bugdoc bugdoc_cli test examples

# Sort imports with isort
isort bugdoc_api/bugdoc bugdoc_cli test --profile black

# Check linting with flake8
flake8 bugdoc_api/bugdoc bugdoc_cli test --max-line-length=100

# Check linting with ruff
ruff check bugdoc_api/bugdoc bugdoc_cli test

# Type check with mypy
mypy bugdoc_api/bugdoc --ignore-missing-imports

# Security scan with bandit
bandit -r bugdoc_api/bugdoc bugdoc_cli -ll
```

## Code Style Guidelines

- **Python Style:** [PEP 8](https://www.python.org/dev/peps/pep-0008/) via [Black](https://black.readthedocs.io/)
- **Line Length:** 100 characters (enforced by Black)
- **Import Style:** isort with Black profile
- **Type Hints:** Encouraged but not mandatory

### Code Style Example

```python
"""Module docstring describing the purpose."""

from typing import Optional

import numpy as np


def my_function(param1: str, param2: Optional[int] = None) -> dict:
    """
    Short description.

    Longer description with more details about what the function does.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to None.

    Returns:
        A dictionary with results.

    Raises:
        ValueError: If param1 is empty.
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    result = {"param1": param1}
    if param2 is not None:
        result["param2"] = param2

    return result
```

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "feat: add new feature" -m "Detailed description of changes"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear title describing the changes
   - Detailed description of what changed and why
   - Reference to any related issues (e.g., "Closes #123")

5. **Ensure all checks pass:**
   - GitHub Actions workflows must pass
   - Code review approval required
   - Conversations must be resolved

6. **Merge strategy:**
   - Use "Squash and merge" for single-commit PRs
   - Use "Create a merge commit" for multi-commit PRs

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat:** A new feature
- **fix:** A bug fix
- **docs:** Documentation only changes
- **style:** Changes that don't affect code meaning (formatting, missing semicolons, etc.)
- **refactor:** Code change that neither fixes a bug nor adds a feature
- **perf:** Code change that improves performance
- **test:** Adding missing tests or correcting existing tests
- **chore:** Changes to build process, dependencies, or tooling

### Examples

```bash
git commit -m "feat: add parameter exploration algorithm"
git commit -m "fix: correct parameter sorting in minimal pairs"
git commit -m "docs: update API documentation"
git commit -m "test: add coverage for edge cases"
```

## Testing Requirements

- All new features must have accompanying tests
- All bug fixes must include a test that reproduces the issue
- Minimum 70% code coverage is encouraged
- Tests should be clear and well-documented

## Documentation

- Update docstrings for all public functions and classes
- Follow Google-style docstrings (see example above)
- Update README.md if adding new public APIs
- Add examples to the docs folder if appropriate

## Troubleshooting

### Pre-commit hooks failing

If a pre-commit hook fails, you can:

1. Let it auto-fix issues (black, isort will fix many issues):
   ```bash
   pre-commit run --all-files
   git add .
   git commit -m "style: auto-format code"
   ```

2. Fix issues manually based on the error messages:
   ```bash
   # See what changed
   git diff
   # Fix manually
   git add .
   git commit
   ```

### Tests failing locally but passing in CI

- Ensure you're using the same Python version as CI (usually 3.10)
- Check for platform-specific issues (especially on Windows)
- Verify all dependencies are installed: `pip install -e "bugdoc_api[dev]"`

### Import errors

- Make sure you've activated the virtual environment
- Reinstall the package: `pip install -e "bugdoc_api[dev]" --force-reinstall`
- Check for circular imports

## Questions?

- Open an [issue](https://github.com/VIDA-NYU/BugDoc/issues)
- Check existing issues and discussions first
- For major changes, open an issue for discussion before implementing

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

Thank you for contributing to BugDoc!
