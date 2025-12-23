# LLM Integration Guide

This guide shows how to integrate real LLM providers (OpenAI, Anthropic, Ollama) with Open Floor Protocol agents.

## Overview

By default, agents use simple echo responses. To use real LLM models, you can use the `LLMAgent` class which supports multiple providers.

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5, GPT-4o, etc.
- **Anthropic**: Claude 3 (Haiku, Sonnet, Opus)
- **Ollama**: Local LLM models (Llama, Mistral, etc.)

## Quick Start

### 1. Install Dependencies

**First, install project dependencies:**
```bash
# From project root directory
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Install all project dependencies (includes structlog, httpx, etc.)
pip install -r requirements.txt
```

**Then install LLM provider libraries:**
```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# For Ollama (optional - can use HTTP API)
pip install ollama
```

### 2. Set API Keys

The code automatically reads API keys from environment variables:

```bash
# OpenAI (required for OpenAI provider)
export OPENAI_API_KEY="sk-..."

# Anthropic (required for Anthropic provider)
export ANTHROPIC_API_KEY="sk-ant-..."

# Ollama (no key needed, but must be running locally)
# Install: https://ollama.ai
# Run: ollama serve
```

**Note**: If you already have `$OPENAI_API_KEY` set in your environment, the code will use it automatically - no additional configuration needed!

**Quick Test**: Run `python examples/agents/quick_llm_test.py` to verify your API key is working.

### 3. Create an LLM Agent

```python
from src.agents.llm_agent import LLMAgent

# OpenAI agent
agent = LLMAgent(
    speakerUri="tag:example.com,2025:my_agent",
    agent_name="My Assistant",
    llm_provider="openai",
    model_name="gpt-4o-mini",
    system_prompt="You are a helpful assistant."
)

# Process a message
response = await agent.process_utterance(
    conversation_id="conv_001",
    utterance_text="Hello!",
    sender_speakerUri="tag:example.com,2025:user"
)

print(response)
```

## Examples

### OpenAI Agent

```python
import asyncio
from src.agents.llm_agent import LLMAgent
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "sk-..."

async def main():
    agent = LLMAgent(
        speakerUri="tag:example.com,2025:gpt_agent",
        agent_name="GPT Assistant",
        llm_provider="openai",
        model_name="gpt-4o-mini"
    )
    
    response = await agent.process_utterance(
        conversation_id="conv_test",
        utterance_text="What is the capital of France?",
        sender_speakerUri="tag:example.com,2025:user"
    )
    
    print(response)

asyncio.run(main())
```

### Anthropic Claude Agent

```python
import asyncio
from src.agents.llm_agent import LLMAgent
import os

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

async def main():
    agent = LLMAgent(
        speakerUri="tag:example.com,2025:claude_agent",
        agent_name="Claude Assistant",
        llm_provider="anthropic",
        model_name="claude-3-haiku-20240307"
    )
    
    response = await agent.process_utterance(
        conversation_id="conv_test",
        utterance_text="Explain quantum computing.",
        sender_speakerUri="tag:example.com,2025:user"
    )
    
    print(response)

asyncio.run(main())
```

### Ollama (Local LLM) Agent

```python
import asyncio
from src.agents.llm_agent import LLMAgent

async def main():
    # Make sure Ollama is running: ollama serve
    # Pull model: ollama pull llama3
    
    agent = LLMAgent(
        speakerUri="tag:example.com,2025:ollama_agent",
        agent_name="Local LLM Assistant",
        llm_provider="ollama",
        model_name="llama3"  # or "mistral", "codellama", etc.
    )
    
    response = await agent.process_utterance(
        conversation_id="conv_test",
        utterance_text="Hello!",
        sender_speakerUri="tag:example.com,2025:user"
    )
    
    print(response)

asyncio.run(main())
```

## Integration with Floor Manager

To use LLM agents with the Floor Manager:

```python
import asyncio
import httpx
from src.agents.llm_agent import LLMAgent

async def register_and_use_llm_agent():
    # Create LLM agent
    agent = LLMAgent(
        speakerUri="tag:example.com,2025:llm_agent",
        agent_name="LLM Assistant",
        llm_provider="openai",
        model_name="gpt-4o-mini"
    )
    
    # Register with Floor Manager
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8000/api/v1/agents/register",
            json={
                "speakerUri": agent.speakerUri,
                "agent_name": agent.agent_name,
                "capabilities": ["text_generation"],
                "serviceUrl": agent.serviceUrl
            }
        )
    
    # Request floor
    await client.post(
        "http://localhost:8000/api/v1/floor/request",
        json={
            "conversation_id": "conv_001",
            "speakerUri": agent.speakerUri,
            "priority": 5
        }
    )
    
    # Process messages when floor is granted
    # (This would typically be done via webhook or polling)

asyncio.run(register_and_use_llm_agent())
```

## Configuration Options

### Model Selection

**OpenAI:**
- `gpt-4o-mini` (cheapest, fast)
- `gpt-4o` (balanced)
- `gpt-4` (most capable)
- `gpt-3.5-turbo` (legacy)

**Anthropic:**
- `claude-3-haiku-20240307` (fastest, cheapest)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-opus-20240229` (most capable)

**Ollama:**
- `llama3` (Meta's Llama 3)
- `mistral` (Mistral AI)
- `codellama` (Code-focused)
- Any model available in Ollama

### System Prompts

Customize agent behavior with system prompts:

```python
agent = LLMAgent(
    speakerUri="tag:example.com,2025:specialist",
    agent_name="Data Analyst",
    llm_provider="openai",
    model_name="gpt-4o-mini",
    system_prompt="""You are a data analysis specialist.
    You help analyze data, create visualizations, and provide insights.
    Be precise and data-driven in your responses."""
)
```

## Conversation History

`LLMAgent` automatically maintains conversation history per conversation ID:

- Last 10 messages are kept in memory
- History is separate per `conversation_id`
- System prompt is included in every request

## Error Handling

The agent handles errors gracefully:

```python
try:
    response = await agent.process_utterance(...)
except Exception as e:
    # Agent returns error message instead of crashing
    print(f"Error: {e}")
```

## Cost Considerations

**OpenAI:**
- GPT-4o-mini: ~$0.15 per 1M input tokens
- GPT-4o: ~$2.50 per 1M input tokens

**Anthropic:**
- Claude Haiku: ~$0.25 per 1M input tokens
- Claude Opus: ~$15 per 1M input tokens

**Ollama:**
- Free (runs locally)
- Requires local GPU/CPU resources

## Best Practices

1. **Use appropriate models**: Use cheaper models (gpt-4o-mini, claude-haiku) for simple tasks
2. **Set system prompts**: Define clear roles and behaviors
3. **Monitor costs**: Track API usage, especially with expensive models
4. **Handle rate limits**: Implement retry logic for production
5. **Cache responses**: Consider caching for repeated queries

## Running Examples

```bash
# Quick test (verifies API key and makes a simple call)
python examples/agents/quick_llm_test.py

# Full examples (all providers)
python examples/agents/llm_agent_example.py

# Make sure API keys are set (if not already in your environment)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

**If you already have `$OPENAI_API_KEY` set**, you can run the examples directly - they will automatically use your environment variable!

## Troubleshooting

### "OPENAI_API_KEY not set"
- Set environment variable: `export OPENAI_API_KEY="sk-..."`
- Or set in code: `os.environ["OPENAI_API_KEY"] = "sk-..."`

### "Module not found: openai"
- Install: `pip install openai`

### Ollama connection errors
- Make sure Ollama is running: `ollama serve`
- Check URL: Default is `http://localhost:11434`
- Pull model: `ollama pull llama3`

### Rate limit errors
- Implement exponential backoff
- Use cheaper models for testing
- Consider caching responses

## Next Steps

- See `examples/agents/llm_agent_example.py` for complete examples
- Integrate with Floor Manager for multi-agent conversations
- Customize system prompts for specific use cases
- Add caching layer for cost optimization

