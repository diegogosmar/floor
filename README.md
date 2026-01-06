# Open Floor Protocol (OFP) Multi-Agent System

A Python-based implementation of the Open Floor Protocol 1.0.1 specification for multi-agent conversation management and floor control.

## Overview

This project implements the **Floor Manager** per Open Floor Protocol (OFP) 1.0.1 specification, providing:

- **Floor Manager**: Core OFP component managing floor control and envelope routing
- **Floor Control Logic**: Minimal floor management behaviors (requestFloor → grantFloor, yieldFloor, etc.)
- **Envelope Processing**: OFP 1.0.1 compliant JSON envelope handling
- **Agent Support**: Base classes and example agents for testing

**Per OFP 1.0.1**: No central agent registry (agents identified only by speakerUri). Dynamic discovery via getManifests/publishManifests events.

## Architecture

### System Architecture per OFP 1.0.1

```
src/
├── floor_manager/     # Floor Manager (core OFP component)
│   ├── manager.py       # Main Floor Manager (includes envelope routing)
│   ├── floor_control.py # Floor control logic (minimal behaviors)
│   └── envelope.py      # OFP 1.0.1 envelope models
├── agents/            # Agent implementations (BaseAgent, ExampleAgent, LLMAgent)
├── orchestration/     # Optional orchestration patterns (Convener Agent, etc.)
├── api/               # FastAPI REST endpoints
│   ├── floor.py         # Floor control API
│   └── envelope.py      # Envelope processing API
└── main.py            # FastAPI application entry point
```

### Floor Manager (Core OFP 1.0.1 Component)

The **Floor Manager** is the central component per OFP Specification Section 0.4.3:

```
┌─────────────────────────────────────────────┐
│           FLOOR MANAGER                     │
│  (Implements OFP 1.0.1 Spec Section 2.2)   │
│                                             │
│  • Envelope Processing & Routing (built-in) │
│  • Floor Control Logic (minimal behaviors)  │
│  • Priority Queue Management                │
│  • Conversation State Management            │
└─────────────────────────────────────────────┘
                    ↕
            OFP 1.0.1 Envelopes
                    ↕
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Agent A  │  │ Agent B  │  │ Agent C  │
    └──────────┘  └──────────┘  └──────────┘
```

**Key Features**:
1. **Envelope Routing** (built-in): Routes OFP envelopes between agents (no separate router component)
2. **Floor Control**: Implements minimal floor management behaviors (Spec Section 2.2)
3. **Priority Queue**: Manages floor requests by priority
4. **State Machine**: Floor as autonomous state machine

**Important Terminology** (per OFP 1.0.1 Spec):
- **Floor Manager** = Our system component (what this project implements)
- **Convener Agent** = Optional AGENT that mediates conversations (like a meeting chair)
- The Floor Manager can work standalone OR delegate to a Convener Agent if present

📊 **Visual Architecture Diagrams**: See [OFP 1.0.1 Spec Analysis](docs/OFP_1.0.1_OFFICIAL_SPEC_ANALYSIS.md) for detailed architecture based on official specification.

### Optional Orchestration Patterns

- **Convener Agent Pattern**: Optional agent that mediates conversations (per OFP Spec Section 0.4.3)
- **Collaborative**: Autonomous floor negotiation with minimal arbitration
- **Hybrid Delegation**: Master agent delegates to specialists while maintaining control

**Note**: These are optional patterns. The Floor Manager works without them.

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

**Option A: Complete OFP Flow Demo** ⭐ **RECOMMENDED**
```bash
# Demonstrates COMPLETE Open Floor Protocol 1.0.1 flow:
# • Agent registration with manifests
# • getManifests (capability discovery)  
# • requestFloor with priority queue
# • grantFloor by autonomous Convener
# • Floor yield and handoff between agents

python examples/agents/complete_ofp_demo.py
```

This shows the **real OFP protocol in action** with the Floor Manager API. See [Complete OFP Demo Guide](examples/agents/COMPLETE_OFP_DEMO.md) for details.

**Option B: Interactive GUI Demo** 🎨 **NEW!**

```bash
# Install Streamlit (if not already installed)
pip install streamlit

# Launch interactive web GUI
streamlit run streamlit_app.py
```

Opens in browser at `http://localhost:8501`. Features:
- 💬 Real-time chat with AI agents
- 🎤 Visual floor status display
- 👥 Multiple agents (Budget Analyst, Travel Agent, Coordinator)
- 🤖 AI-powered responses (GPT-4o-mini)
- 🎯 Priority queue visualization

📖 **See**: [GUI Demo Guide](docs/GUI_DEMO.md) for detailed instructions.

**Option C: Basic Floor Control Demo**
```bash
# Install dependency if needed
pip install httpx

# Test basic multi-agent conversation
python examples/agents/demo_agents.py

# Test floor control priority
python examples/agents/demo_agents.py priority
```

**Option C: Bash Script**
```bash
# Complete workflow test
./examples/test_workflow.sh
```

**Option D: Swagger UI (Interactive)**
```bash
# Open in browser
open http://localhost:8000/docs
# Or visit: http://localhost:8000/docs
```

#### 4. Test with LLM Agents (Optional)

**Note**: Demo agents use hardcoded responses. For real AI-powered agents, use LLM agents:

```bash
# First, install project dependencies (required)
pip install -r requirements.txt

# Then install LLM provider libraries
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

- **🚀 How to Launch and Test**: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) ⭐ **START HERE**
- **📋 OFP 1.0.1 Spec Analysis**: [docs/OFP_1.0.1_OFFICIAL_SPEC_ANALYSIS.md](docs/OFP_1.0.1_OFFICIAL_SPEC_ANALYSIS.md) - Official specification analysis and compliance
- **🔄 Refactoring Status**: [REFACTORING_STATUS.md](REFACTORING_STATUS.md) - Current refactoring progress per OFP 1.0.1
- **🎭 Simple OFP Demo**: [examples/agents/complete_ofp_demo_simple.py](examples/agents/complete_ofp_demo_simple.py) - Floor control without agent registration
- **⚙️ Detailed Setup**: [docs/SETUP.md](docs/SETUP.md)
- **🏗️ Architecture**: [docs/ARCHITECTURE_DETAILED.md](docs/ARCHITECTURE_DETAILED.md)
- **🧠 LLM Integration**: [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) - How to use real LLM providers (OpenAI, Anthropic, Ollama)
- **🧪 Testing**: [docs/TESTING.md](docs/TESTING.md) - How to run tests
- **📖 Quick Reference**: [docs/QUICKSTART.md](docs/QUICKSTART.md)

## Development

### Running Tests

**Important**: Make sure `pytest-asyncio` is installed in your virtual environment:

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Verify pytest-asyncio is installed
pip list | grep pytest-asyncio

# If missing, install it explicitly
pip install pytest-asyncio>=0.23.0
```

Then run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_floor_manager.py
```

**Troubleshooting**: If you see "async def functions are not natively supported", see [Testing Guide](docs/TESTING.md) for detailed troubleshooting steps.

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

## Open Floor Protocol 1.0.1

This implementation follows the Open Floor Protocol 1.0.1 specification for:
- Floor control primitives (autonomous state machine with convener)
- Conversation envelope format (with assignedFloorRoles and floorGranted)
- Agent capability discovery
- Message routing and delivery
- Privacy flag handling (only for utterance events)

**Key OFP 1.0.1 Features**:
- Floor Manager acts as autonomous Convener
- `assignedFloorRoles` and `floorGranted` in conversation object
- `acceptInvite` event support
- Privacy flag only respected for utterance events

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** on GitHub
2. **Clone your fork** and create a feature branch
3. **Make your changes** following our [coding standards](CONTRIBUTING.md#coding-standards)
4. **Add tests** for new functionality
5. **Ensure all tests pass**: `pytest`
6. **Update documentation** if needed
7. **Submit a Pull Request** - We'll review and merge it!

📖 **For detailed guidelines**, see [CONTRIBUTING.md](CONTRIBUTING.md) - It includes:
- Complete development setup instructions
- Pull Request process and best practices
- Coding standards and style guide
- Testing requirements
- Commit message conventions
- OFP 1.0.1 compliance guidelines

**Quick PR Process:**
- Fork → Branch → Code → Test → PR → Review → Merge ✅

## Related Projects

This implementation is part of the Open Floor Protocol implementations collection:

- **floor-implementations**: https://github.com/open-voice-interoperability/floor-implementations
  - Collection of different Floor Manager implementations
  - This Python implementation is included in the collection
  - See [docs/ADD_TO_FLOOR_IMPLEMENTATIONS.md](docs/ADD_TO_FLOOR_IMPLEMENTATIONS.md) for details

## Support

For issues and questions, please open an issue in the repository.

