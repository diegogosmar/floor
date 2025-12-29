# Getting Started - How to Launch and Test the Floor Manager

## 🚀 Quick Start

> **💡 For a complete step-by-step guide, see [docs/LAUNCH_AND_TEST.md](LAUNCH_AND_TEST.md)**

### Prerequisites

```bash
# Verify Python version
python --version  # Must be 3.11+

# Verify Docker
docker --version
docker-compose --version
```

### Step 1: Start Services

```bash
# Go to project directory
cd /path/to/floor

# Start services (PostgreSQL, Redis, API)
docker-compose up -d

# Wait a few seconds
sleep 5

# Verify they are active
docker-compose ps
```

### Step 2: Verify Installation

```bash
# Health check
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

### Step 3: Test with Demo Agents ⭐

**Option A: Complete OFP Flow Demo** ⭐⭐⭐ **RECOMMENDED**
```bash
# Demonstrates COMPLETE Open Floor Protocol 1.0.1 flow:
# • Agent registration with manifests
# • getManifests (capability discovery)  
# • requestFloor with priority queue
# • grantFloor by autonomous Convener
# • Floor yield and handoff between agents

python examples/agents/complete_ofp_demo.py
```

This shows the **real OFP protocol in action** with the Floor Manager API. See output example below.

**Option B: Basic Floor Control Demo**
```bash
# Install httpx if needed
pip install httpx

# Test basic multi-agent conversation
python examples/agents/demo_agents.py

# Test floor control priority
python examples/agents/demo_agents.py priority
```

> **ℹ️ Note**: Demo agents (`demo_agents.py`) are **HTTP simulators** that do not use LLM or external APIs. 
> - ✅ **Free** - No API costs
> - ✅ **Fast** - No LLM calls
> - ✅ **Safe** - Does not use your OpenAI key
> 
> To use agents with **real LLMs** (OpenAI, Anthropic, etc.), see:
> - `examples/agents/llm_agent_example.py` - LLM examples
> - `examples/agents/quick_llm_test.py` - Quick LLM test
> - `docs/LLM_INTEGRATION.md` - Complete LLM integration guide

**Option C: Swagger UI (Interactive)**
```bash
# Open in browser
open http://localhost:8000/docs
```

**Option D: Bash Script**
```bash
# Complete workflow test
./examples/test_workflow.sh
```

## 📋 Test Base

### Test 1: Agent Registration

```bash
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_1",
    "agent_name": "Test Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001"
  }'
```

**Expected response**:
```json
{
  "success": true,
  "speakerUri": "tag:test.com,2025:agent_1",
  "capabilities": {...}
}
```

### Test 2: List Agents

```bash
# List all agents
curl http://localhost:8000/api/v1/agents/ | jq

# Find agents by capability
curl http://localhost:8000/api/v1/agents/capability/text_generation | jq
```

### Test 3: Floor Control

```bash
# Request floor
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "speakerUri": "tag:test.com,2025:agent_1",
    "priority": 5
  }'

# Check floor holder
curl http://localhost:8000/api/v1/floor/holder/conv_test_001 | jq

# Release floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "speakerUri": "tag:test.com,2025:agent_1"
  }'
```

### Test 4: Send Utterance

```bash
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "sender_speakerUri": "tag:test.com,2025:agent_1",
    "target_speakerUri": "tag:test.com,2025:agent_2",
    "text": "Hello, can you help me?"
  }'
```

## 🧪 Complete Test Workflow

### Option 1: Automatic Script

```bash
# Run complete test workflow
./examples/test_workflow.sh

# The script tests:
# - Registration of 3 agents
# - Multi-agent floor control
# - Utterance sending
# - Capability discovery
# - Heartbeat updates
```

### Option 2: Manual Step-by-Step Test

See `docs/SETUP.md` for detailed step-by-step instructions.

## 🎯 Multi-Agent Test Scenario

### Scenario: 3 Agents Collaborate

```bash
# Terminal 1: Start API (if not already started)
docker-compose up -d

# Terminal 2: Register Agent 1
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_text",
    "agent_name": "Text Agent",
    "capabilities": ["text_generation"]
  }'

# Terminal 3: Register Agent 2
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_image",
    "agent_name": "Image Agent",
    "capabilities": ["image_generation"]
  }'

# Terminal 4: Register Agent 3
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_data",
    "agent_name": "Data Agent",
    "capabilities": ["data_analysis"]
  }'

# Now test floor control with priorities
CONV_ID="conv_multi_001"

# Agent 1 requests floor (priority 5)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_text\",
    \"priority\": 5
  }"

# Agent 2 requests floor (priority 3 - will be queued)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_image\",
    \"priority\": 3
  }"

# Check floor holder (should be agent_text)
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq

# Agent 1 releases floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_text\"
  }"

# Check new floor holder (should be agent_image)
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq
```

## 🔍 Verify Functionality

### Check Logs

```bash
# API logs
docker-compose logs api

# Logs with follow
docker-compose logs -f api

# Specific service logs
docker-compose logs postgres
docker-compose logs redis
```

### Check Status

```bash
# Service status
docker-compose ps

# API health check
curl http://localhost:8000/health

# List registered agents
curl http://localhost:8000/api/v1/agents/ | jq
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U ofp_user -d ofp_db

# Example query (if you have tables)
# SELECT * FROM agents;
```

## 🐛 Troubleshooting

### Issue: Port 8000 already in use

```bash
# Find process
lsof -i :8000

# Kill process or change port in .env
# PORT=8001
```

### Issue: Services don't start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Database connection error

```bash
# Verify PostgreSQL is active
docker-compose ps postgres

# Check environment variables
docker-compose exec api env | grep POSTGRES

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: Agents don't register

```bash
# Verify registry is initialized
curl http://localhost:8000/api/v1/agents/

# Check logs for errors
docker-compose logs api | grep -i registry

# Verify speakerUri format (must be valid URI)
```

## 📚 Additional Documentation

- **Complete Setup**: `docs/SETUP.md`
- **Quick Start**: `docs/QUICKSTART.md`
- **Architecture**: `docs/ARCHITECTURE_DETAILED.md`
- **API Reference**: `docs/api.md`
- **Swagger UI**: http://localhost:8000/docs

## 🎓 Next Steps

1. **Explore Swagger UI**: http://localhost:8000/docs
2. **Read Architecture**: `docs/ARCHITECTURE_DETAILED.md`
3. **Test Orchestration Patterns**: See examples in `src/orchestration/`
4. **Create Your Agent**: Extend `BaseAgent` in `src/agents/`
5. **Use Real LLM Agents**: See `docs/LLM_INTEGRATION.md` to integrate OpenAI, Anthropic, etc.
6. **Run Test Suite**: 
   ```bash
   # First, install pytest-asyncio (required for async tests)
   pip install pytest-asyncio
   
   # Then run tests
   pytest tests/
   ```

## 💡 Tips

- Use `jq` to format JSON responses: `curl ... | jq`
- Swagger UI is the easiest way to explore the API
- Logs are structured JSON, use `jq` to filter them
- For local development without Docker, start only postgres/redis with Docker

## ✅ Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Docker and Docker Compose installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] Docker services started (`docker-compose up -d`)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Swagger UI accessible (http://localhost:8000/docs)
- [ ] Test workflow executed successfully

## 🆘 Support

If you have issues:
1. Check logs: `docker-compose logs`
2. Verify documentation: `docs/`
3. Check Swagger UI for API examples
4. Open an issue in the repository

