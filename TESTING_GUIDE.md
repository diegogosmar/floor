# Testing Guide - OFP 1.0.1 Floor Manager

Complete guide for testing the OFP 1.0.1 compliant Floor Manager.

## 🚀 Quick Test (3 Minutes)

### Step 1: Start Services

```bash
cd /path/to/floor

# Start Floor Manager and dependencies
docker-compose up -d

# Wait for services to start
sleep 5

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME      COMMAND         SERVICE   STATUS    PORTS
floor-api "uvicorn..."    api       running   0.0.0.0:8000->8000/tcp
floor-db  "postgres..."   postgres  running   5432/tcp
floor-redis "redis..."    redis     running   6379/tcp
```

### Step 2: Health Check

```bash
# Test Floor Manager health
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

### Step 3: Run Complete OFP Demo

```bash
# Run the complete OFP 1.0.1 demo
python examples/agents/complete_ofp_demo_simple.py
```

**Expected Output**:
```
🚀 COMPLETE OPEN FLOOR PROTOCOL 1.0.1 DEMONSTRATION
✅ Floor Manager is running and healthy

STEP 1: Create Agents (No Registration Required)
   ✅ Created: Coordinator Agent (priority: 10)
   ✅ Created: Data Analyst Agent (priority: 7)
   ✅ Created: Assistant Agent (priority: 5)

STEP 2: Floor Requests (Priority Queue)
🙋 Assistant Agent requesting floor (priority: 5)...
   ✅ Floor GRANTED to Assistant Agent

✅ DEMO COMPLETED SUCCESSFULLY!
```

✅ **If you see this, the system is working correctly!**

## 🧪 Detailed Testing

### Test 1: Floor Manager API

#### 1.1 Request Floor

```bash
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv_001",
    "speakerUri": "tag:test.com,2025:agent_1",
    "priority": 5
  }'
```

Expected response:
```json
{
  "conversation_id": "test_conv_001",
  "granted": true,
  "holder": "tag:test.com,2025:agent_1"
}
```

#### 1.2 Check Floor Holder

```bash
curl http://localhost:8000/api/v1/floor/holder/test_conv_001 | jq
```

Expected response:
```json
{
  "conversation_id": "test_conv_001",
  "holder": "tag:test.com,2025:agent_1",
  "has_floor": true,
  "assignedFloorRoles": {},
  "floorGranted": {
    "speakerUri": "tag:test.com,2025:agent_1",
    "grantedAt": "2025-01-06T..."
  }
}
```

#### 1.3 Release Floor (Yield)

```bash
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv_001",
    "speakerUri": "tag:test.com,2025:agent_1"
  }'
```

Expected response:
```json
{
  "conversation_id": "test_conv_001",
  "released": true
}
```

### Test 2: Priority Queue

#### 2.1 Request Floor from Multiple Agents

```bash
# Agent 1 (priority 5)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_priority",
    "speakerUri": "tag:test.com,2025:agent_1",
    "priority": 5
  }'

# Agent 2 (priority 10 - higher)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_priority",
    "speakerUri": "tag:test.com,2025:agent_2",
    "priority": 10
  }'

# Agent 3 (priority 3 - lower)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_priority",
    "speakerUri": "tag:test.com,2025:agent_3",
    "priority": 3
  }'
```

**Expected Behavior**:
- Agent 1 gets floor immediately (first to request)
- Agent 2 queued (higher priority, will be next)
- Agent 3 queued (lower priority, will be last)

#### 2.2 Verify Queue Order

```bash
# Release floor from Agent 1
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_priority",
    "speakerUri": "tag:test.com,2025:agent_1"
  }'

# Check who has floor now (should be Agent 2, priority 10)
curl http://localhost:8000/api/v1/floor/holder/test_priority | jq '.holder'
# Expected: "tag:test.com,2025:agent_2"
```

### Test 3: Envelope Processing

#### 3.1 Send Utterance

```bash
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv_001",
    "sender_speakerUri": "tag:test.com,2025:agent_1",
    "text": "Hello from Agent 1!",
    "private": false
  }'
```

Expected response:
```json
{
  "success": true,
  "conversation_id": "test_conv_001",
  "envelope": {
    "schema": {"version": "1.0.1"},
    "conversation": {"id": "test_conv_001"},
    "sender": {"speakerUri": "tag:test.com,2025:agent_1"},
    "events": [...]
  }
}
```

#### 3.2 Send Private Utterance

```bash
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv_001",
    "sender_speakerUri": "tag:test.com,2025:agent_1",
    "target_speakerUri": "tag:test.com,2025:agent_2",
    "text": "Private message to Agent 2",
    "private": true
  }'
```

**Expected**: Privacy flag respected (only Agent 2 receives it per OFP 1.0.1)

### Test 4: Automated Tests

#### 4.1 Run Python Tests

```bash
cd /path/to/floor

# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v
```

Expected output:
```
tests/test_floor_manager.py::test_request_floor_immediate_grant PASSED
tests/test_floor_manager.py::test_request_floor_queue PASSED
tests/test_floor_manager.py::test_release_floor PASSED
tests/test_floor_manager.py::test_priority_queue PASSED
tests/test_agents.py::test_agent_creation PASSED
...
```

#### 4.2 Run Specific Test

```bash
# Test floor control only
pytest tests/test_floor_manager.py -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test 5: Demo Agents

#### 5.1 Basic Demo

```bash
# Install dependencies
pip install httpx

# Run basic demo
python examples/agents/demo_agents.py
```

#### 5.2 Priority Demo

```bash
# Run priority-based demo
python examples/agents/demo_agents.py priority
```

### Test 6: LLM Integration (Optional)

#### 6.1 Test OpenAI Connection

```bash
# Set API key
export OPENAI_API_KEY="sk-your-key-here"

# Quick test
python examples/agents/quick_llm_test.py
```

Expected output:
```
Testing OpenAI connection...
✅ OpenAI API key is working!
Response: Hello! How can I assist you today?
```

#### 6.2 Test Full LLM Example

```bash
# Run LLM example with OpenAI and Ollama
python examples/agents/llm_agent_example.py
```

## 🔍 Verification Checklist

Use this checklist to verify OFP 1.0.1 compliance:

### Core Functionality
- [ ] Floor Manager starts successfully
- [ ] Health check returns healthy status
- [ ] Floor can be requested
- [ ] Floor can be granted
- [ ] Floor can be yielded
- [ ] Priority queue works correctly

### OFP 1.0.1 Compliance
- [ ] No agent registration required (agents use speakerUri only)
- [ ] Floor Manager acts as central hub
- [ ] Envelope routing is built-in (not separate component)
- [ ] Privacy flag only respected for utterance events
- [ ] Conversation metadata includes assignedFloorRoles and floorGranted
- [ ] Floor control events work (requestFloor, grantFloor, yieldFloor, revokeFloor)

### API Endpoints
- [ ] `/health` returns 200
- [ ] `/api/v1/floor/request` works
- [ ] `/api/v1/floor/release` works
- [ ] `/api/v1/floor/holder/{id}` works
- [ ] `/api/v1/envelopes/utterance` works
- [ ] `/api/v1/agents/*` does NOT exist (removed per OFP 1.0.1)

### Examples
- [ ] `complete_ofp_demo_simple.py` runs successfully
- [ ] `demo_agents.py` runs successfully
- [ ] LLM examples run (if API keys available)

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose restart

# Clean restart
docker-compose down
docker-compose up -d
```

### Port 8000 Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it (replace PID)
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Python Module Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# For async tests
pip install pytest-asyncio

# For LLM examples
pip install openai anthropic ollama
```

### Tests Failing

```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv

# Run specific test
pytest tests/test_floor_manager.py::test_request_floor_immediate_grant -vv
```

## 📊 Test Results

After running all tests, you should see:

### Expected Success Rate
- ✅ Core functionality: 100%
- ✅ OFP 1.0.1 compliance: 95%
- ✅ API endpoints: 100%
- ✅ Examples: 100%

### Known Limitations (5%)
- ⏳ getManifests/publishManifests not handled (not critical)
- ⏳ acceptInvite event not handled (not critical)
- ⏳ Conversants tracking not implemented (not critical)

## 🎯 Quick Smoke Test

Run this one-liner to verify everything works:

```bash
cd /path/to/floor && \
docker-compose up -d && \
sleep 5 && \
curl http://localhost:8000/health && \
python examples/agents/complete_ofp_demo_simple.py
```

If all steps complete successfully: ✅ **System is working!**

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **OFP 1.0.1 Spec**: [Official Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)
- **Compliance Report**: [OFP_1.0.1_COMPLIANCE_REPORT.md](OFP_1.0.1_COMPLIANCE_REPORT.md)
- **Getting Started**: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)

---

**Need help?** Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or review the logs with `docker-compose logs api`.

