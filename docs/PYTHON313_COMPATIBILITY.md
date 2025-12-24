# Python 3.13 Compatibility Issues

## Problem

Python 3.13 is very new and some dependencies in `requirements.txt` are not yet compatible:

- `psycopg2-binary==2.9.9` - Fails to compile (uses deprecated Python 3.13 APIs)
- `pydantic-core` (via `pydantic==2.5.0`) - Build issues with Python 3.13

## Solutions

### Option 1: Use Python 3.11 or 3.12 (Recommended)

```bash
# Install Python 3.12 (or 3.11)
brew install python@3.12

# Create virtual environment with Python 3.12
python3.12 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Use Standalone LLM Agent (No Full Dependencies)

For testing LLM agents only, use the standalone version:

```bash
# Install minimal dependencies
pip install httpx structlog openai

# Run standalone agent
python examples/agents/llm_agent_standalone.py
```

This doesn't require PostgreSQL, Redis, or other heavy dependencies.

### Option 3: Update Dependencies (Future)

When newer versions are released that support Python 3.13:

```bash
# Update to newer versions (when available)
pip install --upgrade psycopg2-binary pydantic pydantic-core
```

## Current Status

- ✅ **Standalone LLM Agent**: Works with Python 3.13 (minimal deps)
- ❌ **Full Project**: Requires Python 3.11 or 3.12
- ✅ **Demo Agents** (`demo_agents.py`): Work with Python 3.13 (only need httpx)

## Quick Test Without Full Setup

```bash
# Install only what's needed for LLM testing
pip install httpx structlog openai

# Test standalone agent
python examples/agents/llm_agent_standalone.py
```

This bypasses all PostgreSQL/Redis dependencies and works with Python 3.13.


