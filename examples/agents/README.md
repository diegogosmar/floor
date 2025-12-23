# Demo Agents - Example Agents to Test the Floor Manager

These Python scripts demonstrate how to create agents that interact with the Open Floor Protocol Floor Manager.

## 🚀 Quick Start

### Prerequisites

```bash
# Make sure you have httpx installed
pip install httpx

# Or install all dependencies
pip install -r ../../requirements.txt
```

### Start the Floor Manager

```bash
# From project root
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Start services
docker-compose up -d

# Verify it works
curl http://localhost:8000/health
```

### Run Demo

```bash
# Test complete multi-agent conversation
python examples/agents/demo_agents.py

# Test floor control priority
python examples/agents/demo_agents.py priority
```

## 📋 What the Scripts Do

### `demo_agents.py`

Main script that includes:

1. **DemoAgent Class**: Python class that simulates an agent
   - Registry registration
   - Floor request/release
   - Utterance sending
   - Heartbeat updates

2. **demo_multi_agent_conversation()**: 
   - Creates 3 agents (Text, Image, Data)
   - Tests floor control with priorities
   - Simulates multi-agent conversation
   - Shows utterance sending between agents

3. **demo_floor_priority()**:
   - Tests priority behavior in floor control
   - Shows how agents with different priorities compete for the floor

## 💡 How to Use DemoAgent

```python
from examples.agents.demo_agents import DemoAgent
import asyncio

async def main():
    # Create an agent
    agent = DemoAgent(
        speaker_uri="tag:example.com,2025:my_agent",
        agent_name="My Agent",
        capabilities=["text_generation"]
    )
    
    try:
        # Register
        await agent.register()
        
        # Request floor
        await agent.request_floor("conv_001", priority=5)
        
        # Send utterance
        await agent.send_utterance(
            "conv_001",
            target_speaker_uri="tag:example.com,2025:other_agent",
            text="Hello!"
        )
        
        # Release floor
        await agent.release_floor("conv_001")
        
    finally:
        await agent.close()

asyncio.run(main())
```

## 🎯 Test Scenarios

### Scenario 1: Sequential Conversation

```bash
python examples/agents/demo_agents.py
```

Tests:
- ✅ Multiple agent registration
- ✅ Sequential floor control
- ✅ Priority queue
- ✅ Floor passing between agents
- ✅ Utterance sending

### Scenario 2: Priority Test

```bash
python examples/agents/demo_agents.py priority
```

Tests:
- ✅ Agents with different priorities
- ✅ Behavior when an agent with higher priority requests floor
- ✅ Queue ordering by priority

## 🔧 Customization

You can modify `demo_agents.py` to:

- Add more agents
- Change priorities
- Modify messages
- Test specific scenarios

## 📚 References

- **Complete Documentation**: `../../docs/LAUNCH_AND_TEST.md`
- **API Reference**: http://localhost:8000/docs
- **BaseAgent**: `../../src/agents/base_agent.py`
