# Publishing to PyPI

## Prerequisites

1. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
2. Create PyPI account at https://pypi.org/account/register/
3. Create API token at https://pypi.org/manage/account/token/

## Publishing Steps

### 1. Update Version
```bash
# Update version in pyproject.toml
poetry version patch  # or minor, major
```

### 2. Build Package
```bash
poetry build
```

### 3. Configure PyPI Credentials
```bash
poetry config pypi-token.pypi <your-api-token>
```

### 4. Publish to PyPI
```bash
# Test on TestPyPI first (optional)
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish -r testpypi

# Publish to PyPI
poetry publish
```

## Quick Commands

```bash
# Build and publish in one go
poetry build && poetry publish

# Check what will be published
poetry build --verbose
```

## Installation After Publishing

Users can install with:
```bash
pip install ccxt-backtesting-exchange
```

## Important Notes

- Always test your package locally before publishing
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Cannot republish the same version - must increment version number
- Consider using TestPyPI for testing before publishing to main PyPI