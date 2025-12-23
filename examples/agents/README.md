# Demo Agents - Esempi di Agenti per Testare il Floor Manager

Questi script Python dimostrano come creare agenti che interagiscono con il Floor Manager Open Floor Protocol.

## 🚀 Quick Start

### Prerequisiti

```bash
# Assicurati di avere httpx installato
pip install httpx

# Oppure installa tutte le dipendenze
pip install -r ../../requirements.txt
```

### Avvia il Floor Manager

```bash
# Dalla root del progetto
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Avvia servizi
docker-compose up -d

# Verifica che funzioni
curl http://localhost:8000/health
```

### Esegui Demo

```bash
# Test conversazione multi-agente completa
python examples/agents/demo_agents.py

# Test priorità floor control
python examples/agents/demo_agents.py priority
```

## 📋 Cosa Fanno gli Script

### `demo_agents.py`

Script principale che include:

1. **DemoAgent Class**: Classe Python che simula un agente
   - Registrazione nel registry
   - Richiesta/rilascio floor
   - Invio utterance
   - Heartbeat updates

2. **demo_multi_agent_conversation()**: 
   - Crea 3 agenti (Text, Image, Data)
   - Testa floor control con priorità
   - Simula conversazione multi-agente
   - Mostra invio utterance tra agenti

3. **demo_floor_priority()**:
   - Testa comportamento priorità nel floor control
   - Mostra come agenti con priorità diverse competono per il floor

## 💡 Come Usare DemoAgent

```python
from examples.agents.demo_agents import DemoAgent
import asyncio

async def main():
    # Crea un agente
    agent = DemoAgent(
        speaker_uri="tag:example.com,2025:my_agent",
        agent_name="My Agent",
        capabilities=["text_generation"]
    )
    
    try:
        # Registra
        await agent.register()
        
        # Richiedi floor
        await agent.request_floor("conv_001", priority=5)
        
        # Invia utterance
        await agent.send_utterance(
            "conv_001",
            target_speaker_uri="tag:example.com,2025:other_agent",
            text="Hello!"
        )
        
        # Rilascia floor
        await agent.release_floor("conv_001")
        
    finally:
        await agent.close()

asyncio.run(main())
```

## 🎯 Scenari di Test

### Scenario 1: Conversazione Sequenziale

```bash
python examples/agents/demo_agents.py
```

Testa:
- ✅ Registrazione multipla agenti
- ✅ Floor control sequenziale
- ✅ Coda con priorità
- ✅ Passaggio floor tra agenti
- ✅ Invio utterance

### Scenario 2: Test Priorità

```bash
python examples/agents/demo_agents.py priority
```

Testa:
- ✅ Agenti con priorità diverse
- ✅ Comportamento quando un agente con priorità più alta richiede floor
- ✅ Queue ordering per priorità

## 🔧 Personalizzazione

Puoi modificare `demo_agents.py` per:

- Aggiungere più agenti
- Cambiare priorità
- Modificare i messaggi
- Testare scenari specifici

## 📚 Riferimenti

- **Documentazione Completa**: `../../docs/LAUNCH_AND_TEST.md`
- **API Reference**: http://localhost:8000/docs
- **BaseAgent**: `../../src/agents/base_agent.py`

