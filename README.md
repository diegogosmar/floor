# Open Floor Protocol (OFP) Multi-Agent System

A Python-based implementation of the Open Floor Protocol 1.0.0 specification for multi-agent conversation management and floor control.

## Overview

This project implements a multi-agent system following the Open Floor Protocol (OFP) specification, providing:

- **Floor Control**: Management of conversation floor primitives
- **Envelope Routing**: Conversation envelope routing between agents
- **Agent Registry**: Capability discovery and agent registration
- **Agent Implementations**: Base classes and example agents

## Architecture

### Multi-Layer Architecture per OFP 1.0.0

```
src/
├── floor_manager/     # Floor Manager Layer - Floor control primitives
├── envelope_router/   # Conversation Envelope Router - OFP envelope routing
├── agent_registry/   # Agent Capability Registry - Manifest & discovery
├── agents/           # Agent implementations (BaseAgent, ExampleAgent)
├── orchestration/    # Orchestration patterns (Convener, Collaborative, Hybrid)
├── api/              # FastAPI REST endpoints
└── main.py          # FastAPI application entry point
```

### Three Main Layers

1. **Floor Manager Layer** (also called "Convener" in the specifications): Manages floor control primitives (requestFloor, grantFloor, revokeFloor, yieldFloor) and coordinates conversational turns
2. **Conversation Envelope Router**: Routes OFP 1.0.0 compliant JSON envelopes between heterogeneous agents
3. **Agent Capability Registry**: Maintains agent manifests per Assistant Manifest Specification, enabling dynamic capability discovery

📊 **Visual Architecture Diagrams**: See [Agent Integration Guide](docs/OFP_AGENT_INTEGRATION.md) for interactive Mermaid diagrams showing the complete system architecture, integration flow, floor control state machine, and capability discovery.

### Orchestration Patterns

- **Convener-Based**: Explicit floor management by convener agent (round-robin, priority-based, context-aware)
- **Collaborative**: Autonomous floor negotiation with minimal arbitration
- **Hybrid Delegation**: Master agent delegates to specialists while maintaining control

## Technology Stack

- **Python**: 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Testing**: pytest, pytest-asyncio

## 🚀 Quick Start - Launch the Floor Manager and Test with Demo Agents

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL 15 (or use Docker)
- Redis 7 (or use Docker)

### Quick Start (3 Steps)

#### 1. Start Services

```bash
# Clone the repository (if not already cloned)
git clone https://github.com/diegogosmar/floor.git
cd floor

# Start services (PostgreSQL, Redis, API)
docker-compose up -d

# Wait a few seconds
sleep 5
```

#### 2. Verify It Works

```bash
# Health check
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

#### 3. Test with Demo Agents

**Option A: Python Script (Recommended)**
```bash
# Install dependency if needed
pip install httpx

# Test complete multi-agent conversation
python examples/agents/demo_agents.py

# Test floor control priority
python examples/agents/demo_agents.py priority
```

**Option B: Bash Script**
```bash
# Complete workflow test
./examples/test_workflow.sh
```

**Option C: Swagger UI (Interactive)**
```bash
# Open in browser
open http://localhost:8000/docs
# Or visit: http://localhost:8000/docs
```

#### 4. Test with LLM Agents (Optional)

**Note**: Demo agents use hardcoded responses. For real AI-powered agents, use LLM agents:

```bash
# Install LLM provider libraries
pip install openai  # For OpenAI
# pip install anthropic  # For Anthropic
# pip install ollama  # For local LLM (optional)

# Set API key (if using OpenAI)
export OPENAI_API_KEY="sk-..."

# Quick test to verify API key works
python examples/agents/quick_llm_test.py

# Full LLM agent examples (OpenAI, Anthropic, Ollama)
python examples/agents/llm_agent_example.py
```

**Supported Providers:**
- **OpenAI**: GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic**: Claude 3 (Haiku, Sonnet, Opus)
- **Ollama**: Local LLM models (requires `ollama serve`)

📖 **See**: [LLM Integration Guide](docs/LLM_INTEGRATION.md) for detailed instructions.

### Quick Manual Test

```bash
# 1. Register an agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_1",
    "agent_name": "Test Agent",
    "capabilities": ["text_generation"]
  }'

# 2. Request floor
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test",
    "speakerUri": "tag:test.com,2025:agent_1",
    "priority": 5
  }'

# 3. Check floor holder
curl http://localhost:8000/api/v1/floor/holder/conv_test
```

### 📚 Complete Documentation

- **🚀 How to Launch and Test**: [docs/LAUNCH_AND_TEST.md](docs/LAUNCH_AND_TEST.md) ⭐ **START HERE**
- **⚙️ Detailed Setup**: [docs/SETUP.md](docs/SETUP.md)
- **🏗️ Architecture**: [docs/ARCHITECTURE_DETAILED.md](docs/ARCHITECTURE_DETAILED.md)
- **🤖 Agent Integration**: [docs/OFP_AGENT_INTEGRATION.md](docs/OFP_AGENT_INTEGRATION.md) - Manifest, floor control, OFP compliance with **interactive diagrams** 📊
- **🧠 LLM Integration**: [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) - How to use real LLM providers (OpenAI, Anthropic, Ollama)
- **📖 Quick Reference**: [docs/QUICKSTART.md](docs/QUICKSTART.md)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_floor_manager.py
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint
flake8 src tests

# Type checking
mypy src
```

## Project Structure

```
FLOOR/
├── src/
│   ├── floor_manager/      # Floor control primitives
│   │   ├── __init__.py
│   │   ├── floor_control.py
│   │   └── floor_queue.py
│   ├── envelope_router/    # Envelope routing
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── envelope.py
│   ├── agent_registry/     # Agent registry
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   └── capabilities.py
│   ├── agents/             # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   └── example_agent.py
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── database/          # Database configuration
│   │   ├── __init__.py
│   │   └── connection.py
│   └── main.py            # FastAPI app
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_floor_manager.py
│   ├── test_envelope_router.py
│   ├── test_agent_registry.py
│   └── test_agents.py
├── docker/                # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                  # Documentation
│   ├── architecture.md
│   └── api.md
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── docker-compose.yml    # Docker Compose config
└── README.md             # This file
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Open Floor Protocol 1.0.0

This implementation follows the Open Floor Protocol 1.0.0 specification for:
- Floor control primitives
- Conversation envelope format
- Agent capability discovery
- Message routing and delivery

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions, please open an issue in the repository.

