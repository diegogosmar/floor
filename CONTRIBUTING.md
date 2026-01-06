# Contributing to Floor Manager

Thank you for your interest in contributing to the Open Floor Protocol (OFP) Floor Manager! 🎉

This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Questions?](#questions)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### 🐛 Reporting Bugs

1. **Check existing issues** - Make sure the bug hasn't been reported already
2. **Create a new issue** - Use the "Bug report" template
3. **Provide details**:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment (OS, Python version, etc.)
   - Error messages/logs (if any)

### 💡 Suggesting Features

1. **Check existing issues** - See if the feature was already suggested
2. **Create a new issue** - Use the "Feature request" template
3. **Describe**:
   - Use case and motivation
   - Proposed solution (if you have one)
   - Alternatives considered
   - Additional context

### 🔧 Contributing Code

The standard workflow is:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch**
4. **Make your changes**
5. **Write/update tests**
6. **Ensure all tests pass**
7. **Update documentation**
8. **Commit your changes**
9. **Push to your fork**
10. **Open a Pull Request**

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Docker and Docker Compose (for running services)
- A GitHub account

### Step-by-Step Setup

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/floor.git
cd floor

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies (if any)
pip install pytest pytest-asyncio httpx

# 5. Start services (PostgreSQL, Redis)
docker-compose up -d

# 6. Verify setup
pytest tests/  # Should pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_floor_manager.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run async tests
pytest tests/ -v
```

### Running the Application

```bash
# Start Floor Manager
docker-compose up

# Or run directly
python -m uvicorn src.main:app --reload --port 8000
```

## Pull Request Process

### ✅ Before Submitting

1. **Update your fork**:
   ```bash
   git remote add upstream https://github.com/diegogosmar/floor.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make your changes** following the [Coding Standards](#coding-standards)

4. **Write tests** for new functionality (see [Testing Requirements](#testing-requirements))

5. **Run tests** and ensure they pass:
   ```bash
   pytest
   ```

6. **Update documentation** if needed:
   - Update README.md if adding features
   - Add docstrings to new functions/classes
   - Update API docs if changing endpoints

7. **Check for linting errors**:
   ```bash
   # If you have flake8/pylint configured
   flake8 src/
   ```

8. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   # Use conventional commits (see below)
   ```

9. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### 📝 Opening the Pull Request

1. **Go to GitHub** and navigate to your fork
2. **Click "New Pull Request"**
3. **Select your branch** to merge into `main`
4. **Fill out the PR template**:
   - Clear title (e.g., "feat: Add GUI demo with Streamlit")
   - Description of changes
   - Link related issues (e.g., "Closes #123")
   - Screenshots (if UI changes)
   - Testing notes

5. **Wait for review** - The maintainer will review your PR

### 🔍 Review Process

- **Automated checks** run first (tests, linting)
- **Maintainer reviews** the code
- **Feedback provided** - You may be asked to make changes
- **Approval** - Once approved, the PR is merged

### ⚠️ Common PR Issues

**PR is too large?**
- Break it into smaller PRs
- Each PR should focus on one feature/fix

**Tests failing?**
- Check the error messages
- Run tests locally: `pytest`
- Ask for help if stuck

**Merge conflicts?**
- Update your branch: `git pull upstream main`
- Resolve conflicts
- Push again

**Need to make changes?**
- Just push more commits to the same branch
- The PR will update automatically

## Coding Standards

### Python Style Guide

This project follows **PEP 8** with some additions:

- **Line length**: 100 characters (soft limit)
- **Indentation**: 4 spaces (no tabs)
- **Docstrings**: Google style for functions/classes
- **Type hints**: Use type hints for function parameters and return types

### Code Formatting

```python
# ✅ Good
def request_floor(
    self,
    conversation_id: str,
    speaker_uri: str,
    priority: int = 5
) -> dict:
    """
    Request floor for a conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        speaker_uri: Agent's speaker URI
        priority: Request priority (higher = more important)
    
    Returns:
        Dictionary with floor status
    """
    pass

# ❌ Bad
def request_floor(self, conv_id, speaker, prio=5):
    pass
```

### Naming Conventions

- **Functions/Methods**: `snake_case` (e.g., `request_floor`)
- **Classes**: `PascalCase` (e.g., `FloorManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_PRIORITY`)
- **Private methods**: Prefix with `_` (e.g., `_process_queue`)

### File Organization

```
src/
├── floor_manager/     # Core Floor Manager logic
├── agents/            # Agent implementations
├── api/               # FastAPI endpoints
└── orchestration/     # Optional patterns
```

### Import Organization

```python
# Standard library
import asyncio
from typing import Optional, Dict

# Third-party
import httpx
from fastapi import APIRouter

# Local
from src.floor_manager.manager import FloorManager
from src.agents.base_agent import BaseAgent
```

### Error Handling

```python
# ✅ Good - Specific exceptions
try:
    result = await self._process_envelope(envelope)
except ValueError as e:
    logger.error(f"Invalid envelope: {e}")
    raise
except TimeoutError:
    logger.warning("Processing timeout")
    return {"status": "timeout"}

# ❌ Bad - Bare except
try:
    result = await self._process_envelope(envelope)
except:
    pass
```

### Async/Await

- Use `async def` for async functions
- Always `await` async calls
- Use `asyncio.gather()` for concurrent operations

```python
# ✅ Good
async def process_multiple(self, envelopes: list) -> list:
    results = await asyncio.gather(
        *[self.process_envelope(e) for e in envelopes]
    )
    return results
```

## Testing Requirements

### Test Coverage

- **New features** must include tests
- **Bug fixes** must include regression tests
- Aim for **>80% coverage** for new code

### Writing Tests

```python
# tests/test_floor_manager.py
import pytest
from src.floor_manager.manager import FloorManager

@pytest.mark.asyncio
async def test_request_floor_success():
    """Test successful floor request."""
    manager = FloorManager()
    result = await manager.request_floor(
        conversation_id="test_conv",
        speaker_uri="tag:test,2025:agent1",
        priority=5
    )
    assert result["status"] == "granted"
    assert result["speakerUri"] == "tag:test,2025:agent1"
```

### Test Structure

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **API tests**: Test HTTP endpoints

### Running Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_floor_manager.py::test_request_floor_success

# With coverage
pytest --cov=src --cov-report=term-missing
```

## Documentation

### Code Documentation

- **Docstrings** for all public functions/classes
- **Type hints** for function signatures
- **Inline comments** for complex logic

```python
def grant_floor(
    self,
    conversation_id: str,
    speaker_uri: str
) -> dict:
    """
    Grant floor to an agent.
    
    This method updates the floor state and notifies waiting agents.
    
    Args:
        conversation_id: Conversation identifier
        speaker_uri: Agent to grant floor to
    
    Returns:
        Dictionary with grant status and timestamp
    
    Raises:
        ValueError: If conversation doesn't exist
        RuntimeError: If floor is already granted
    """
    pass
```

### README Updates

- Update README.md if adding features
- Add examples for new functionality
- Update Quick Start if setup changes

### API Documentation

- Update API docs if changing endpoints
- Add examples to docstrings
- Keep Swagger UI docs up to date

## Commit Messages

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(gui): add Streamlit interactive demo"

# Bug fix
git commit -m "fix(floor): handle priority queue edge case"

# Documentation
git commit -m "docs(readme): update quick start guide"

# Multiple changes
git commit -m "feat(api): add floor status endpoint

- Add GET /api/v1/floor/{conversation_id}/status
- Include current holder and queue
- Add tests for new endpoint"
```

## Project-Specific Guidelines

### OFP 1.0.1 Compliance

- **Always follow OFP 1.0.1 specification**
- Envelope format must match spec exactly
- Floor control primitives must be compliant
- Test with official OFP test suite if available

### Architecture Decisions

- **Floor Manager** is the central component
- **No agent registry** (per OFP 1.0.1)
- **Envelope routing** is built into Floor Manager
- **Priority queue** manages floor requests

### Code Patterns

- Use **async/await** for I/O operations
- Use **Pydantic** for data validation
- Use **FastAPI** for REST endpoints
- Follow **hexagonal architecture** principles

## Questions?

- **Open an issue** for questions/discussions
- **Check existing issues** for similar questions
- **Read the docs** in `docs/` directory
- **Ask in PR comments** if related to a specific PR

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (if we add one)
- Mentioned in release notes
- Credited in commit history

Thank you for contributing! 🙏

---

**Ready to contribute?** Start by:
1. Forking the repository
2. Creating a feature branch
3. Making your changes
4. Opening a Pull Request

We look forward to your contributions! 🚀

