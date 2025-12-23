# Detailed Architecture - Open Floor Protocol Multi-Agent System

## Overview

This document describes the multi-layer architecture of the Open Floor Protocol system conforming to OFP 1.0.0 specification.

## Multi-Layer Architecture

### Layer 1: Floor Manager

**Responsibility**: Management of floor control primitives and coordination of conversational turns.

**Components**:
- `FloorControl`: Implements requestFloor, grantFloor, revokeFloor, yieldFloor
- `FloorQueue`: Manages floor request queue with priority

**Features**:
- State machine for floor transitions
- Priority queue for concurrent requests
- Timeout handling for floor grants
- Support for multi-party conversations

**API Endpoints**:
- `POST /api/v1/floor/request` - Request floor
- `POST /api/v1/floor/release` - Release floor
- `GET /api/v1/floor/holder/{conversation_id}` - Get floor holder

### Layer 2: Conversation Envelope Router

**Responsibility**: Routing of conversation envelope JSON between heterogeneous agents, ensuring interoperability.

**Components**:
- `EnvelopeRouter`: Routing based on speakerUri
- `OpenFloorEnvelope`: Envelope structure conforming to OFP 1.0.0
- JSON schema validation

**Features**:
- Envelope validation against OFP 1.0.0 schema
- Multi-party routing
- Support for private/public events
- Retry logic for delivery failure

**API Endpoints**:
- `POST /api/v1/envelopes/send` - Send complete envelope
- `POST /api/v1/envelopes/utterance` - Send simplified utterance
- `POST /api/v1/envelopes/validate` - Validate envelope

### Layer 3: Agent Capability Registry

**Responsibility**: Dynamic registry of agent manifests for discovery and delegation.

**Components**:
- `AgentRegistry`: Storage and discovery of agents
- `AgentCapabilities`: Capability definition per agent

**Features**:
- Manifest storage per agent
- Discovery by capability type
- Heartbeat tracking
- Automatic cleanup of stale agents

**API Endpoints**:
- `POST /api/v1/agents/register` - Register agent
- `GET /api/v1/agents/{speakerUri}` - Get agent
- `GET /api/v1/agents/capability/{type}` - Find agents by capability
- `POST /api/v1/agents/heartbeat` - Update heartbeat

## Orchestration Patterns

### 1. Convener-Based Orchestration

**Use**: Structured workflows with explicit floor control.

**Implementation**: `src/orchestration/convener.py`

**Strategies**:
- Round-robin: Circular turns between participants
- Priority-based: Floor based on priority
- Context-aware: Floor based on conversational context

**Example**:
```python
convener = ConvenerOrchestrator(
    convener_speakerUri="tag:convener.com,2025:convener_1",
    strategy=ConvenerStrategy.ROUND_ROBIN
)
await convener.invite_participant("conv_001", "agent_1")
await convener.grant_floor_to_next("conv_001")
```

### 2. Collaborative Floor Passing

**Use**: Emergent behavior and self-organization.

**Implementation**: `src/orchestration/collaborative.py`

**Features**:
- Agents negotiate autonomously
- Floor manager arbitrates only conflicts
- Supports emergent behavior

**Example**:
```python
collaborative = CollaborativeOrchestrator(floor_control)
await collaborative.handle_floor_request("conv_001", "agent_1", priority=5)
await collaborative.handle_floor_yield("conv_001", "agent_1", reason="@complete")
```

### 3. Hybrid Delegation Model

**Use**: Complex tasks requiring different expertise.

**Implementation**: `src/orchestration/hybrid.py`

**Features**:
- Master agent maintains main control
- Temporary delegation to specialist agents
- Sub-conversations for sub-tasks
- Merge results into main conversation

**Example**:
```python
hybrid = HybridOrchestrator(master_speakerUri="master_1", ...)
sub_conv = await hybrid.delegate_to_specialist(
    "conv_main", "specialist_1", "Analyze data"
)
await hybrid.merge_sub_conversation(sub_conv, result)
```

## Data Flow

```
┌─────────────┐
│   Agent 1   │
└──────┬──────┘
       │ OpenFloorEnvelope
       ▼
┌─────────────────────┐
│ Envelope Router     │───► OFP 1.0.0 Schema Validation
└──────┬──────────────┘
       │
       ├──► Floor Manager ──► Verify Floor Holder
       │
       └──► Agent Registry ──► Capability Discovery
       │
       ▼
┌─────────────┐
│   Agent 2   │
└─────────────┘
```

## Agent Identification (OFP 1.0.0)

According to OFP 1.0.0 specification, agents are identified by:

- **speakerUri**: Unique, persistent URI (e.g., `tag:example.com,2025:agent_1`)
- **serviceUrl**: Agent service URL (e.g., `http://localhost:8001`)

The `speakerUri` must be:
- Unique for the entire agent lifetime
- Persistent
- Ideally a URN or Tag URI

## Conversation Envelope Structure

Conforming to OFP 1.0.0:

```json
{
  "openFloor": {
    "schema": {
      "version": "1.0.0",
      "url": "https://github.com/.../schema.json"
    },
    "conversation": {
      "id": "conv_001",
      "conversants": [...]
    },
    "sender": {
      "speakerUri": "tag:example.com,2025:agent_1",
      "serviceUrl": "http://localhost:8001"
    },
    "events": [
      {
        "to": {
          "speakerUri": "tag:example.com,2025:agent_2",
          "private": false
        },
        "eventType": "utterance",
        "parameters": {...}
      }
    ]
  }
}
```

## Supported Event Types

- **Utterance Events**: `utterance`, `context`
- **Conversation Management**: `invite`, `uninvite`, `declineInvite`, `bye`
- **Discovery**: `getManifests`, `publishManifests`
- **Floor Management**: `requestFloor`, `grantFloor`, `revokeFloor`, `yieldFloor`

## Technology Stack

- **Python 3.11+**: Runtime
- **FastAPI**: Web framework REST API
- **PostgreSQL**: Persistent storage (agent registry, conversation state)
- **Redis**: Caching and message queue
- **Pydantic**: Data validation and serialization
- **Structlog**: Structured logging

## Deployment

### Docker Compose

Services:
- `api`: FastAPI application
- `postgres`: PostgreSQL database
- `redis`: Redis cache

### Multi-Agent Setup

See `examples/docker-compose.multi-agent.yml` for example with 3+ agents.

## Extensibility

The system is designed to be extended:

1. **New Orchestration Patterns**: Implement new patterns in `src/orchestration/`
2. **New Event Types**: Extend `EventType` enum and implement handlers
3. **Custom Agents**: Extend `BaseAgent` for new agent types
4. **Semantic Cache**: Integrate semantic caching for optimization

## Performance Considerations

- **Floor Queue**: Max size configurable (default: 100)
- **Router Queue**: Max size configurable (default: 1000)
- **Registry**: Max agents configurable (default: 1000)
- **Heartbeat Timeout**: Configurable for automatic cleanup

## Security

- CORS configured for cross-origin requests
- Input validation via Pydantic
- Schema validation for OFP envelopes
- (Future: Authentication/Authorization for production)

## Monitoring & Observability

- Structured logging with structlog
- Health check endpoint
- (Future: Prometheus metrics, distributed tracing)

## References

- **OFP Specification**: https://github.com/open-voice-interoperability/openfloor-docs
- **Assistant Manifest Spec**: OFP Assistant Manifest Specification 1.0.0
- **Architecture Docs**: `docs/architecture.md`
- **API Docs**: `docs/api.md`
