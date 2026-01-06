# Getting Started - OFP 1.0.1 Floor Manager

This guide will help you get the **Open Floor Protocol 1.0.1 Floor Manager** up and running quickly.

## What is the Floor Manager?

Per [OFP 1.0.1 Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md), the Floor Manager is the central component that:

- **Routes conversation envelopes** between agents (built-in functionality)
- **Manages floor control** (requestFloor, grantFloor, yieldFloor, revokeFloor)
- **Implements minimal floor management behaviors** (Spec Section 2.2)
- **Acts as the conversational "hub"** for multi-agent coordination

**Important Notes**:
- ✅ Per OFP 1.0.1: **NO central agent registry** (agents identified only by `speakerUri`)
- ✅ Envelope routing is **built into** Floor Manager (not a separate component)
- ✅ "Convener" in spec = optional AGENT that mediates (not our system component)

## 🚀 Quick Start

> **💡 For complete details, see [OFP 1.0.1 Spec Analysis](OFP_1.0.1_OFFICIAL_SPEC_ANALYSIS.md)**

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

### Step 2: Health Check

```bash
# Check Floor Manager health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### Step 3: Test with Demo Agents ⭐

**Option A: Complete OFP Flow Demo** ⭐⭐⭐ **RECOMMENDED**
```bash
# Demonstrates COMPLETE Open Floor Protocol 1.0.1 flow:
# • Agents identified only by speakerUri (NO registration)
# • requestFloor with priority queue
# • grantFloor by Floor Manager (autonomous decision)
# • Floor yield and handoff between agents

python examples/agents/complete_ofp_demo_simple.py
```

This shows the **real OFP 1.0.1 protocol** with the Floor Manager API:
- ✅ No agent registration (per spec)
- ✅ Floor Manager makes autonomous decisions
- ✅ Priority-based floor control
- See output example below.

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

## 📊 Complete OFP Demo Output

When you run `python examples/agents/complete_ofp_demo_simple.py`, you'll see:

```
======================================================================
🚀 COMPLETE OPEN FLOOR PROTOCOL 1.0.1 DEMONSTRATION
======================================================================

This demo shows:
  1. Agents identified only by speakerUri (no registration)
  2. requestFloor with priority
  3. Floor Manager grants floor autonomously
  4. Agent utterances
  5. yieldFloor and floor handoff

🏥 Checking Floor Manager health...
   ✅ Floor Manager is running and healthy

======================================================================
STEP 1: Create Agents (No Registration Required)
======================================================================

📝 Per OFP 1.0.1: Agents are identified only by speakerUri
   NO central registry or registration process exists

   ✅ Created: Coordinator Agent (priority: 10)
   ✅ Created: Data Analyst Agent (priority: 7)
   ✅ Created: Assistant Agent (priority: 5)

======================================================================
STEP 2: Floor Requests (Priority Queue)
======================================================================

💡 All agents will request floor. Watch Floor Manager grant by priority!

🙋 Assistant Agent requesting floor (priority: 5)...
   ✅ Floor GRANTED to Assistant Agent

🙋 Data Analyst Agent requesting floor (priority: 7)...
   ⏳ Data Analyst Agent queued for floor

🙋 Coordinator Agent requesting floor (priority: 10)...
   ⏳ Coordinator Agent queued for floor

======================================================================
STEP 3: Check Floor Holder
======================================================================

🎤 Current floor holder: Assistant Agent
   URI: tag:demo.com,2025:assistant
   Floor Manager: tag:floor.manager,2025:manager

======================================================================
STEP 4: Agents Speak (Priority Order)
======================================================================

💬 Assistant Agent: 'Hello! I'm ready to assist.'

👋 Assistant Agent yielding floor...
   ✅ Floor released by Assistant Agent

💬 Data Analyst Agent: 'I've analyzed the data. Here are my findings...'

👋 Data Analyst Agent yielding floor...
   ✅ Floor released by Data Analyst Agent

💬 Coordinator Agent: 'Excellent work everyone! Let's proceed.'

👋 Coordinator Agent yielding floor...
   ✅ Floor released by Coordinator Agent

======================================================================
✅ DEMO COMPLETED SUCCESSFULLY!
======================================================================

📝 Summary:
   ✓ Agents created (no registration needed per OFP 1.0.1)
   ✓ Floor requested by multiple agents
   ✓ Floor Manager granted floor by priority
   ✓ Agents spoke in order
   ✓ Floor yielded properly

======================================================================
🎓 Understanding the Flow
======================================================================

The Floor Manager acts as an autonomous state machine:

1. REQUEST: Agents request floor with priority (no registration)
2. QUEUE: Floor Manager maintains priority queue of requests
3. GRANT: Floor Manager grants floor to highest priority agent
4. SPEAK: Agent with floor can send utterances
5. YIELD: Agent yields floor when done
6. NEXT: Floor Manager grants floor to next agent in queue
7. REPEAT: Steps 4-6 repeat until conversation ends

This is the core of OFP 1.0.1 floor control!
```

**Key Observations** (Per OFP 1.0.1):
- ✅ **No agent registration** - Agents identified only by speakerUri
- ✅ **Floor Manager** grants floor autonomously (priority queue)
- ✅ **Minimal behaviors** implemented (Spec Section 2.2)
- ✅ Priority queue: higher priority agents get floor first

## 🎉 Success!

You now have:
- ✅ **Floor Manager running** (OFP 1.0.1 compliant)
- ✅ **Multi-agent system working** (no registration needed)
- ✅ **Complete OFP 1.0.1 protocol demonstrated**
- ✅ **Floor control with priority queue** working
- ✅ **Envelope routing** integrated in Floor Manager

## 🔍 What Just Happened? (OFP 1.0.1 Architecture)

Per [OFP 1.0.1 Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md):

### Floor Manager (Your Running System)

The Floor Manager is the central OFP component that:

1. **Receives Envelopes**: Agents send OFP 1.0.1 JSON envelopes
2. **Routes Messages**: Built-in routing to target agents (not a separate component)
3. **Manages Floor Control**: Processes requestFloor, grantFloor, yieldFloor, revokeFloor
4. **Priority Queue**: Manages floor requests by priority
5. **Autonomous Decisions**: Makes floor control decisions automatically

### Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         FLOOR MANAGER                       │
│    (OFP 1.0.1 Spec Section 2.2)            │
│                                             │
│  • Envelope Processing & Routing            │
│  • Floor Control Logic                      │
│  • Priority Queue Management                │
│  • Conversation State Management            │
└─────────────────────────────────────────────┘
                    ↕
            OFP 1.0.1 Envelopes
                    ↕
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Agent A  │  │ Agent B  │  │ Agent C  │
    │ (no reg) │  │ (no reg) │  │ (no reg) │
    └──────────┘  └──────────┘  └──────────┘
```

### Key Concepts

1. **No Agent Registration**: Per OFP 1.0.1, agents are identified ONLY by their `speakerUri` in envelopes. No central registry exists.

2. **Floor Manager = Hub**: The Floor Manager acts as the central "hub" that coordinates all conversation flow.

3. **Minimal Behaviors**: The Floor Manager implements minimal floor management behaviors per Spec Section 2.2:
   - requestFloor → grantFloor (if available) or queue
   - yieldFloor → grantFloor to next in queue
   - Priority-based queue management

4. **Envelope Routing Built-In**: Routing is not a separate component; it's built into the Floor Manager.

5. **Convener Agent (Optional)**: The spec mentions an optional "Convener Agent" that can mediate conversations (like a meeting chair). This is NOT our Floor Manager - it's an optional external agent.

## 📋 Next Steps

### Test Floor Control API Directly

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

### Send Utterances

```bash
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "sender_speakerUri": "tag:test.com,2025:agent_1",
    "text": "Hello from Agent 1!",
    "private": false
  }'
```

### Test with LLM Agents (Optional)

See [LLM Integration Guide](LLM_INTEGRATION.md) for using real AI agents with OpenAI, Anthropic, or Ollama.

## 🔧 Troubleshooting

### Floor Manager not responding

```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs api

# Restart services
docker-compose restart
```

### Port already in use

```bash
# Stop existing services
docker-compose down

# Check what's using port 8000
lsof -i :8000

# Start again
docker-compose up -d
```

### Python module errors

```bash
# Make sure you're in the project directory
cd /path/to/floor

# Install dependencies
pip install -r requirements.txt

# For async tests
pip install pytest-asyncio
```

## 📚 Additional Resources

- **OFP 1.0.1 Specification**: [Official Spec](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)
- **Spec Analysis**: [OFP_1.0.1_OFFICIAL_SPEC_ANALYSIS.md](OFP_1.0.1_OFFICIAL_SPEC_ANALYSIS.md)
- **Architecture Details**: [ARCHITECTURE_DETAILED.md](ARCHITECTURE_DETAILED.md)
- **LLM Integration**: [LLM_INTEGRATION.md](LLM_INTEGRATION.md)
- **Testing Guide**: [TESTING.md](TESTING.md)

## 🎯 What Makes This OFP 1.0.1 Compliant?

✅ **No Central Registry**: Agents identified only by speakerUri (Spec Section 0.5)
✅ **Floor Manager as Hub**: Central component coordinating conversation (Spec Section 0.2)
✅ **Minimal Behaviors**: Implements required floor management behaviors (Spec Section 2.2)
✅ **Envelope Routing**: Built into Floor Manager, not separate (Spec Section 0.2)
✅ **Privacy Flag**: Only respected for utterance events (Spec Section 2.2)
✅ **Conversation Metadata**: Includes assignedFloorRoles and floorGranted (Spec Section 1.6)
✅ **Floor Control Events**: requestFloor, grantFloor, yieldFloor, revokeFloor (Spec Sections 1.19-1.22)

---

**Ready to build multi-agent systems?** Start with the demo above, then explore the [LLM Integration Guide](LLM_INTEGRATION.md) to connect real AI agents!

