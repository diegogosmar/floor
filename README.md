# Open Floor Protocol (OFP) Multi-Agent System

A Python-based implementation of the Open Floor Protocol 1.0.0 specification for multi-agent conversation management and floor control.

## Overview

This project implements a multi-agent system following the Open Floor Protocol (OFP) specification, providing:

- **Floor Control**: Management of conversation floor primitives
- **Envelope Routing**: Conversation envelope routing between agents
- **Agent Registry**: Capability discovery and agent registration
- **Agent Implementations**: Base classes and example agents

## Architecture

```
src/
├── floor_manager/     # Floor control primitives management
├── envelope_router/  # Conversation envelope routing
├── agent_registry/   # Capability discovery and registration
├── agents/           # Agent implementations
└── main.py          # FastAPI application entry point
```

## Technology Stack

- **Python**: 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Testing**: pytest, pytest-asyncio

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL 15 (or use Docker)
- Redis 7 (or use Docker)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FLOOR
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start services with Docker Compose:
```bash
docker-compose up -d
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the API server:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

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

