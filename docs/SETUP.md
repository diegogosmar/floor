# Setup and Testing Guide - Open Floor Protocol Multi-Agent System

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [System Startup](#system-startup)
4. [Basic Testing](#basic-testing)
5. [Multi-Agent Testing](#multi-agent-testing)
6. [Orchestration Patterns](#orchestration-patterns)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.11+**
- **Docker and Docker Compose**
- **Git**
- **curl** or **HTTPie** for API testing

## Initial Setup

### 1. Clone and Environment Setup

```bash
# If you haven't already cloned the repository
cd /path/to/floor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy example file
cp .env.example .env

# Modify .env with your configurations (optional for local development)
# Default configurations work for Docker Compose
```

### 3. Verify Project Structure

```bash
# Verify the structure is correct
tree -L 3 -I '__pycache__|*.pyc|venv' src/
```

You should see:
```
src/
├── api/              # FastAPI routers
├── floor_manager/    # Floor control primitives
├── envelope_router/  # Envelope routing
├── agent_registry/   # Agent capability registry
├── agents/          # Agent implementations
├── orchestration/    # Orchestration patterns
└── main.py          # FastAPI app entry point
```

## System Startup

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Verify services are active
docker-compose ps

# View logs
docker-compose logs -f api
```

Services will be available at:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Swagger UI**: http://localhost:8000/docs

### Option 2: Local Development

```bash
# Start only PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# In another terminal, start the API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Basic Testing

### 1. Health Check

```bash
# Verify API is active
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### 2. Agent Registration

```bash
# Register an example agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:example.com,2025:agent_1",
    "agent_name": "Example Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001"
  }'

# Expected response:
# {
#   "success": true,
#   "speakerUri": "tag:example.com,2025:agent_1",
#   "capabilities": {...}
# }
```

### 3. List Registered Agents

```bash
curl http://localhost:8000/api/v1/agents/

# Find agents by capability
curl http://localhost:8000/api/v1/agents/capability/text_generation
```

### 4. Floor Control

```bash
# Request floor for a conversation
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "speakerUri": "tag:example.com,2025:agent_1",
    "priority": 5
  }'

# Check floor holder
curl http://localhost:8000/api/v1/floor/holder/conv_001

# Release floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "speakerUri": "tag:example.com,2025:agent_1"
  }'
```

### 5. Send Utterance

```bash
# Send an utterance
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "sender_speakerUri": "tag:example.com,2025:agent_1",
    "target_speakerUri": "tag:example.com,2025:agent_2",
    "text": "Hello, how can you help me?"
  }'
```

### 6. Envelope Validation

```bash
# Validate an OFP envelope
curl -X POST http://localhost:8000/api/v1/envelopes/validate \
  -H "Content-Type: application/json" \
  -d '{
    "openFloor": {
      "schema": {"version": "1.0.0"},
      "conversation": {"id": "conv_001"},
      "sender": {"speakerUri": "tag:example.com,2025:agent_1"},
      "events": [{
        "eventType": "utterance",
        "parameters": {
          "dialogEvent": {
            "speakerUri": "tag:example.com,2025:agent_1",
            "features": {
              "text": {
                "mimeType": "text/plain",
                "tokens": [{"token": "Hello"}]
              }
            }
          }
        }
      }]
    }
  }'
```

## Multi-Agent Testing

### Multi-Agent Test Script

Create a file `test_multi_agent.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"
CONV_ID="conv_multi_001"

echo "=== Agent Registration ==="

# Register Agent 1
curl -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_1",
    "agent_name": "Text Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001"
  }'

# Register Agent 2
curl -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_2",
    "agent_name": "Image Agent",
    "capabilities": ["image_generation"],
    "serviceUrl": "http://localhost:8002"
  }'

echo -e "\n=== Multi-Agent Floor Control ==="

# Agent 1 requests floor
curl -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_1\",
    \"priority\": 5
  }"

# Agent 2 requests floor (will be queued)
curl -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_2\",
    \"priority\": 3
  }"

# Check holder
curl $BASE_URL/floor/holder/$CONV_ID

# Agent 1 releases floor
curl -X POST $BASE_URL/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_1\"
  }"

# Check new holder (should be agent_2)
curl $BASE_URL/floor/holder/$CONV_ID
```

Run the script:

```bash
chmod +x test_multi_agent.sh
./test_multi_agent.sh
```

## Orchestration Patterns

### 1. Convener-Based Orchestration

```python
from src.orchestration.convener import ConvenerOrchestrator, ConvenerStrategy
from src.floor_manager.floor_control import FloorControl
from src.agent_registry.registry import AgentRegistry

# Initialize components
floor_control = FloorControl()
registry = AgentRegistry()
convener = ConvenerOrchestrator(
    convener_speakerUri="tag:convener.com,2025:convener_1",
    floor_control=floor_control,
    agent_registry=registry,
    strategy=ConvenerStrategy.ROUND_ROBIN
)

# Invite participants
await convener.invite_participant("conv_001", "tag:test.com,2025:agent_1")
await convener.invite_participant("conv_001", "tag:test.com,2025:agent_2")

# Grant floor to next
next_speaker = await convener.grant_floor_to_next("conv_001")
```

### 2. Collaborative Floor Passing

```python
from src.orchestration.collaborative import CollaborativeOrchestrator
from src.floor_manager.floor_control import FloorControl

floor_control = FloorControl()
collaborative = CollaborativeOrchestrator(floor_control)

# Agents request floor autonomously
await collaborative.handle_floor_request("conv_001", "tag:test.com,2025:agent_1", priority=5)
await collaborative.handle_floor_request("conv_001", "tag:test.com,2025:agent_2", priority=3)

# Agent yields floor
await collaborative.handle_floor_yield("conv_001", "tag:test.com,2025:agent_1", reason="@complete")
```

### 3. Hybrid Delegation Model

```python
from src.orchestration.hybrid import HybridOrchestrator
from src.floor_manager.floor_control import FloorControl
from src.agent_registry.registry import AgentRegistry

floor_control = FloorControl()
registry = AgentRegistry()
hybrid = HybridOrchestrator(
    master_speakerUri="tag:master.com,2025:master_1",
    floor_control=floor_control,
    agent_registry=registry
)

# Delegate to specialist
sub_conv_id = await hybrid.delegate_to_specialist(
    "conv_main_001",
    "tag:specialist.com,2025:specialist_1",
    "Analyze this data"
)

# Recall delegation
await hybrid.recall_delegation(sub_conv_id)
```

## Testing with Pytest

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_floor_manager.py
pytest tests/test_envelope_router.py
pytest tests/test_agent_registry.py

# With coverage
pytest --cov=src --cov-report=html

# Verbose tests
pytest -v
```

## Troubleshooting

### Issue: Port already in use

```bash
# Check which process is using the port
lsof -i :8000

# Modify PORT in .env or stop the process
```

### Issue: Database unreachable

```bash
# Verify PostgreSQL is active
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Issue: Agents don't register

```bash
# Verify registry is initialized
curl http://localhost:8000/api/v1/agents/

# Check API logs
docker-compose logs api | grep -i registry
```

### Debug Mode

```bash
# Start with DEBUG log level
LOG_LEVEL=DEBUG uvicorn src.main:app --reload

# Or modify .env
echo "LOG_LEVEL=DEBUG" >> .env
```

## Next Steps

1. **Explore Swagger UI**: http://localhost:8000/docs
2. **Read Architecture Docs**: `docs/architecture.md`
3. **See API Reference**: `docs/api.md`
4. **Docker Compose Examples**: `examples/` (to be created)

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Verify OFP documentation: https://github.com/open-voice-interoperability/openfloor-docs
- Open an issue in the repository
