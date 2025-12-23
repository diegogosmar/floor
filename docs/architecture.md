# Architecture Documentation

## Open Floor Protocol Multi-Agent System Architecture

### Overview

This system implements the Open Floor Protocol (OFP) 1.0.0 specification for managing multi-agent conversations with floor control, envelope routing, and capability discovery.

### Components

#### 1. Floor Manager (`src/floor_manager/`)

Manages floor control primitives for conversations:
- **FloorControl**: Grants, releases, and tracks floor ownership
- **FloorQueue**: Manages queue of floor requests

#### 2. Envelope Router (`src/envelope_router/`)

Routes conversation envelopes between agents:
- **EnvelopeRouter**: Routes envelopes to registered agents
- **ConversationEnvelope**: OFP-compliant envelope format

#### 3. Agent Registry (`src/agent_registry/`)

Manages agent registration and capability discovery:
- **AgentRegistry**: Registers agents and tracks capabilities
- **AgentCapabilities**: Defines agent capabilities

#### 4. Agents (`src/agents/`)

Agent implementations:
- **BaseAgent**: Abstract base class for agents
- **ExampleAgent**: Example implementation

### Data Flow

```
Agent → EnvelopeRouter → FloorManager → Agent Registry → Target Agent
```

### Technology Stack

- **FastAPI**: Web framework for API endpoints
- **PostgreSQL**: Persistent storage for agent registry and conversations
- **Redis**: Caching and message queue
- **Python 3.11+**: Runtime environment

### Deployment

The system is containerized using Docker Compose with separate services for:
- API server
- PostgreSQL database
- Redis cache

