# Testing Guide

## Running Tests

### Prerequisites

Make sure you have installed all test dependencies:

```bash
# Activate your virtual environment first
source myenv/bin/activate  # or your venv path

# Install all dependencies including pytest-asyncio
pip install -r requirements.txt
```

### Verify pytest-asyncio Installation

```bash
# Check if pytest-asyncio is installed
pip list | grep pytest-asyncio

# If not installed, install it explicitly
pip install pytest-asyncio>=0.23.0
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_floor_manager.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Error: "async def functions are not natively supported"

**Problem**: `pytest-asyncio` is not installed or not recognized.

**Solution**:

1. **Install pytest-asyncio**:
   ```bash
   pip install pytest-asyncio>=0.23.0
   ```

2. **Verify installation**:
   ```bash
   pytest --version
   # Should show pytest-asyncio in plugins list
   ```

3. **Check pytest.ini configuration**:
   The file `pytest.ini` should contain:
   ```ini
   [pytest]
   asyncio_mode = auto
   ```

4. **Reinstall if needed**:
   ```bash
   pip uninstall pytest-asyncio
   pip install pytest-asyncio>=0.23.0
   ```

### Error: "Unknown config option: asyncio_mode"

**Problem**: `pytest-asyncio` is not installed or version is too old.

**Solution**:
```bash
# Upgrade pytest-asyncio to version 0.23.0 or higher
pip install --upgrade pytest-asyncio>=0.23.0
```

### Error: "Unknown pytest.mark.asyncio"

**Problem**: `pytest-asyncio` plugin is not loaded.

**Solution**:
1. Verify `pytest-asyncio` is installed: `pip list | grep pytest-asyncio`
2. Check that pytest recognizes it: `pytest --collect-only` should not show warnings
3. If still not working, try reinstalling:
   ```bash
   pip uninstall pytest-asyncio
   pip install pytest-asyncio>=0.23.0
   ```

## Test Structure

All async tests use the `@pytest.mark.asyncio` decorator:

```python
import pytest

@pytest.mark.asyncio
async def test_my_async_function():
    # Your async test code
    result = await some_async_function()
    assert result is not None
```

## Configuration

The `pytest.ini` file is configured for async tests:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

The `asyncio_mode = auto` setting automatically detects async test functions and runs them with pytest-asyncio.





