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

1. **Floor Manager Layer**: Manages floor control primitives (requestFloor, grantFloor, revokeFloor, yieldFloor) and coordinates conversational turns
2. **Conversation Envelope Router**: Routes OFP 1.0.0 compliant JSON envelopes between heterogeneous agents
3. **Agent Capability Registry**: Maintains agent manifests per Assistant Manifest Specification, enabling dynamic capability discovery

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

## 🚀 Quick Start - Lancia il Floor Manager e Testa con Agenti Demo

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL 15 (or use Docker)
- Redis 7 (or use Docker)

### Avvio Rapido (3 Passi)

#### 1. Avvia i Servizi

```bash
# Clone e vai nella directory
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Avvia servizi (PostgreSQL, Redis, API)
docker-compose up -d

# Attendi qualche secondo
sleep 5
```

#### 2. Verifica che Funzioni

```bash
# Health check
curl http://localhost:8000/health
# Risposta: {"status":"healthy"}
```

#### 3. Testa con Agenti Demo

**Opzione A: Script Python (Consigliato)**
```bash
# Installa dipendenza se necessario
pip install httpx

# Test conversazione multi-agente completa
python examples/agents/demo_agents.py

# Test priorità floor control
python examples/agents/demo_agents.py priority
```

**Opzione B: Script Bash**
```bash
# Test workflow completo
./examples/test_workflow.sh
```

**Opzione C: Swagger UI (Interattivo)**
```bash
# Apri nel browser
open http://localhost:8000/docs
# Oppure visita: http://localhost:8000/docs
```

### Test Manuale Rapido

```bash
# 1. Registra un agente
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_1",
    "agent_name": "Test Agent",
    "capabilities": ["text_generation"]
  }'

# 2. Richiedi floor
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test",
    "speakerUri": "tag:test.com,2025:agent_1",
    "priority": 5
  }'

# 3. Verifica floor holder
curl http://localhost:8000/api/v1/floor/holder/conv_test
```

### 📚 Documentazione Completa

- **🚀 Come Lanciare e Testare**: [docs/LAUNCH_AND_TEST.md](docs/LAUNCH_AND_TEST.md) ⭐ **INIZIA QUI**
- **⚙️ Setup Dettagliato**: [docs/SETUP.md](docs/SETUP.md)
- **🏗️ Architettura**: [docs/ARCHITECTURE_DETAILED.md](docs/ARCHITECTURE_DETAILED.md)
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

## License

[Specify your license here]

## Support

For issues and questions, please open an issue in the repository.

