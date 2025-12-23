# 🚀 How to Launch the Floor Manager and Test It with Example Agents

This guide shows you step-by-step how to start the Open Floor Protocol system and test it with example agents.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Startup](#system-startup)
3. [Testing with Demo Agents](#testing-with-demo-agents)
4. [Manual Testing with curl](#manual-testing-with-curl)
5. [Testing with Python Scripts](#testing-with-python-scripts)
6. [Test Scenarios](#test-scenarios)

## Prerequisites

```bash
# Verify Python 3.11+
python --version

# Verify Docker
docker --version
docker-compose --version

# Install httpx if you want to use Python scripts
pip install httpx
```

## System Startup

### Step 1: Start Services

```bash
# Go to project directory
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Start all services (PostgreSQL, Redis, API)
docker-compose up -d

# Wait a few seconds for services to be ready
sleep 5

# Verify they are active
docker-compose ps
```

You should see 3 active services:
- `ofp_postgres` (PostgreSQL)
- `ofp_redis` (Redis)
- `ofp_api` (FastAPI)

### Step 2: Verify It Works

```bash
# Health check
curl http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

### Step 3: Open Swagger UI (Optional but Recommended)

Open in browser: **http://localhost:8000/docs**

Here you can see all available endpoints and test them directly.

## Testing with Demo Agents

### Option 1: Python Demo Script (Recommended)

We've created Python scripts that simulate agents interacting with the Floor Manager:

```bash
# Test complete multi-agent conversation
python examples/agents/demo_agents.py

# Test floor control priority
python examples/agents/demo_agents.py priority
```

The script:
1. ✅ Creates 3 demo agents (Text, Image, Data)
2. ✅ Registers them in the registry
3. ✅ Tests floor control with priorities
4. ✅ Simulates multi-agent conversation
5. ✅ Shows utterance sending between agents

**Example output**:
```
============================================================
DEMO: Multi-Agent Conversation with Floor Control
============================================================

📝 Registering agents...
✅ Text Agent registered successfully
✅ Image Agent registered successfully
✅ Data Agent registered successfully

🎤 Floor Control Test:
------------------------------------------------------------

1. Text Agent requests floor (priority 5)...
🎤 Text Agent obtained the floor
   Floor holder: tag:demo.com,2025:text_agent

2. Image Agent requests floor (priority 3)...
⏳ Image Agent is queued for the floor
   Floor holder: tag:demo.com,2025:text_agent

...
```

### Option 2: Manual Testing with curl

#### 1. Register Example Agents

```bash
# Agent 1: Text Generation Agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:example.com,2025:text_agent",
    "agent_name": "Text Generation Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001",
    "conversationalName": "TextBot"
  }'

# Agent 2: Image Generation Agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:example.com,2025:image_agent",
    "agent_name": "Image Generation Agent",
    "capabilities": ["image_generation"],
    "serviceUrl": "http://localhost:8002",
    "conversationalName": "ImageBot"
  }'

# Agent 3: Data Analysis Agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:example.com,2025:data_agent",
    "agent_name": "Data Analysis Agent",
    "capabilities": ["data_analysis"],
    "serviceUrl": "http://localhost:8003",
    "conversationalName": "DataBot"
  }'
```

#### 2. Verify Registered Agents

```bash
# List all agents
curl http://localhost:8000/api/v1/agents/ | jq

# Find agents by capability
curl http://localhost:8000/api/v1/agents/capability/text_generation | jq
```

#### 3. Test Floor Control

```bash
# Define conversation ID
CONV_ID="conv_test_$(date +%s)"

# Agent 1 requests floor (priority 5)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:example.com,2025:text_agent\",
    \"priority\": 5
  }" | jq

# Check who has the floor
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq

# Agent 2 requests floor (priority 3 - will be queued)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:example.com,2025:image_agent\",
    \"priority\": 3
  }" | jq

# Agent 1 sends utterance to Agent 2
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"sender_speakerUri\": \"tag:example.com,2025:text_agent\",
    \"target_speakerUri\": \"tag:example.com,2025:image_agent\",
    \"text\": \"Hello ImageBot, can you generate an image of a sunset?\"
  }" | jq

# Agent 1 releases floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:example.com,2025:text_agent\"
  }" | jq

# Check new floor holder (should be Agent 2)
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq
```

## Testing with Python Scripts

### Complete Demo Script

Create a file `test_floor_demo.py`:

```python
#!/usr/bin/env python3
"""
Complete test of Floor Manager with demo agents
"""

import asyncio
from examples.agents.demo_agents import DemoAgent
from datetime import datetime

async def main():
    print("🚀 Test Floor Manager with Demo Agents")
    print("=" * 60)
    
    # Create agents
    text = DemoAgent(
        "tag:test.com,2025:text",
        "Text Agent",
        ["text_generation"]
    )
    
    image = DemoAgent(
        "tag:test.com,2025:image",
        "Image Agent",
        ["image_generation"]
    )
    
    conv_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Register
        await text.register()
        await image.register()
        
        # Test floor
        await text.request_floor(conv_id, priority=5)
        await image.request_floor(conv_id, priority=3)
        
        # Send utterance
        await text.send_utterance(conv_id, image.speaker_uri, "Hello!")
        
        # Release
        await text.release_floor(conv_id)
        
        print("\n✅ Test completed!")
        
    finally:
        await text.close()
        await image.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Run:
```bash
python test_floor_demo.py
```

## Test Scenarios

### Scenario 1: Sequential Conversation

**Goal**: Test that agents take the floor sequentially.

```bash
# Use the demo script
python examples/agents/demo_agents.py
```

**What it tests**:
- Agent registration
- Sequential floor requests
- Floor queue with priorities
- Floor release and passing to next

### Scenario 2: Floor Priority

**Goal**: Verify that priorities work correctly.

```bash
python examples/agents/demo_agents.py priority
```

**What it tests**:
- Agents with different priorities
- Behavior when an agent with higher priority requests floor

### Scenario 3: Multi-Party Conversation

**Goal**: Test conversation with 3+ simultaneous agents.

```bash
# Run complete workflow test
./examples/test_workflow.sh
```

**What it tests**:
- Multiple agent registration
- Multi-party floor control
- Utterance sending between multiple agents
- Capability discovery

## Verify Functionality

### Check Logs

```bash
# Real-time logs
docker-compose logs -f api

# Search for errors
docker-compose logs api | grep -i error
```

### Check Status

```bash
# Service status
docker-compose ps

# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/api/v1/agents/ | jq
```

### Check Floor State

```bash
# For each conversation_id, check floor holder
CONV_ID="conv_test_001"
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq
```

## Troubleshooting

### Problem: Python Script Cannot Find Modules

```bash
# Make sure you're in the project root directory
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Install dependencies
pip install httpx

# Run with PYTHONPATH
PYTHONPATH=. python examples/agents/demo_agents.py
```

### Problem: Agents Don't Register

```bash
# Verify API is active
curl http://localhost:8000/health

# Check logs
docker-compose logs api | tail -20

# Verify speakerUri format (must be valid URI)
# Correct example: "tag:example.com,2025:agent_1"
```

### Problem: Floor Not Granted

```bash
# Verify agent is registered
curl http://localhost:8000/api/v1/agents/ | jq

# Check floor holder
curl http://localhost:8000/api/v1/floor/holder/CONV_ID | jq

# Verify floor manager logs
docker-compose logs api | grep -i floor
```

## Next Steps

1. **Explore Swagger UI**: http://localhost:8000/docs
2. **Modify demo agents**: See `examples/agents/demo_agents.py`
3. **Create your agent**: Extend `DemoAgent` or `BaseAgent`
4. **Test orchestration patterns**: See `src/orchestration/`

## References

- **Complete Setup**: `docs/SETUP.md`
- **Architecture**: `docs/ARCHITECTURE_DETAILED.md`
- **API Reference**: http://localhost:8000/docs
- **Quick Start**: `docs/QUICKSTART.md`
