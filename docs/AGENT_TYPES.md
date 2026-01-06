# Agent Types - Fake vs Real LLM

## Overview

There are two types of agents in this project:

1. **Demo Agents** (`demo_agents.py`) - **NO LLM, NO API CALLS**
2. **LLM Agents** (`LLMAgent`) - **Uses real LLM (OpenAI, Anthropic, etc.)**

## Demo Agents (`demo_agents.py`)

**What they are:**
- Simple HTTP clients that simulate agents
- They communicate with the Floor Manager via REST API
- They send pre-written messages (no LLM involved)

**What they do:**
- Register with Floor Manager
- Request/release floor
- Send hardcoded messages like "Hello Image Agent, can you generate an image?"

**Do they use OpenAI?**
- ❌ **NO** - They don't use any LLM
- ❌ **NO** - They don't make API calls to OpenAI
- ✅ They only make HTTP calls to your local Floor Manager API (`http://localhost:8000`)

**Example:**
```python
# This is what demo_agents.py does - just sends hardcoded text
await agent.send_utterance(
    conversation_id,
    target_speaker_uri,
    "Hello Image Agent, can you generate an image?"  # Hardcoded message
)
```

## LLM Agents (`LLMAgent`)

**What they are:**
- Real agents that use LLM models (OpenAI GPT, Anthropic Claude, etc.)
- They generate intelligent responses using AI

**What they do:**
- Process incoming messages with LLM
- Generate contextual responses
- Maintain conversation history

**Do they use OpenAI?**
- ✅ **YES** - Only if you explicitly create an `LLMAgent` with `llm_provider="openai"`
- ✅ They make API calls to OpenAI (or other providers)
- ✅ They use your `$OPENAI_API_KEY` environment variable

**Example:**
```python
# This uses OpenAI and costs money
from src.agents.llm_agent import LLMAgent

agent = LLMAgent(
    speakerUri="tag:example.com,2025:llm_agent",
    agent_name="LLM Assistant",
    llm_provider="openai",  # This will use OpenAI
    model_name="gpt-4o-mini"
)

# This makes a real API call to OpenAI
response = await agent.process_utterance(...)
```

## When is OpenAI Used?

OpenAI is **ONLY** used when:

1. ✅ You explicitly create an `LLMAgent` with `llm_provider="openai"`
2. ✅ You call `agent.process_utterance()` or `agent.handle_envelope()`
3. ✅ The `LLMAgent` class is imported and instantiated

OpenAI is **NOT** used when:

1. ❌ Running `demo_agents.py` (it's just HTTP client)
2. ❌ Running Floor Manager API (it's just a coordinator)
3. ❌ Using `ExampleAgent` (it just echoes messages)
4. ❌ Just importing `LLMAgent` without instantiating it

## Check What's Using OpenAI

To see if anything is currently using OpenAI:

```bash
# Check running Python processes
ps aux | grep python | grep -i "llm\|openai"

# Check network connections to OpenAI
lsof -i | grep openai.com

# Check if LLMAgent is imported anywhere
grep -r "LLMAgent\|from.*llm_agent" examples/ src/ --exclude-dir=__pycache__
```

## Cost Tracking

**Demo Agents (`demo_agents.py`):**
- Cost: **$0.00** (no API calls)

**LLM Agents:**
- Cost: Depends on model and usage
  - GPT-4o-mini: ~$0.15 per 1M input tokens
  - GPT-4o: ~$2.50 per 1M input tokens

## Summary

**Your `demo_agents.py` output shows:**
- ✅ Agents registering with Floor Manager
- ✅ Floor control working
- ✅ Messages being sent
- ❌ **NO OpenAI API calls**
- ❌ **NO costs incurred**

**To use OpenAI, you would need to:**
1. Import `LLMAgent`
2. Create an instance with `llm_provider="openai"`
3. Call `process_utterance()` or `handle_envelope()`

**Current status:** Your OpenAI key is safe - nothing is using it unless you explicitly run code that uses `LLMAgent`.





