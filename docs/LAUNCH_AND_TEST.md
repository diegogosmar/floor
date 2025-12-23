# 🚀 Come Lanciare il Floor Manager e Testarlo con Agenti di Esempio

Questa guida ti mostra passo-passo come avviare il sistema Open Floor Protocol e testarlo con agenti di esempio.

## 📋 Indice

1. [Prerequisiti](#prerequisiti)
2. [Avvio del Sistema](#avvio-del-sistema)
3. [Test con Agenti Demo](#test-con-agenti-demo)
4. [Test Manuale con curl](#test-manuale-con-curl)
5. [Test con Script Python](#test-con-script-python)
6. [Scenari di Test](#scenari-di-test)

## Prerequisiti

```bash
# Verifica Python 3.11+
python --version

# Verifica Docker
docker --version
docker-compose --version

# Installa httpx se vuoi usare gli script Python
pip install httpx
```

## Avvio del Sistema

### Step 1: Avvia i Servizi

```bash
# Vai nella directory del progetto
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Avvia tutti i servizi (PostgreSQL, Redis, API)
docker-compose up -d

# Attendi qualche secondo che i servizi siano pronti
sleep 5

# Verifica che siano attivi
docker-compose ps
```

Dovresti vedere 3 servizi attivi:
- `ofp_postgres` (PostgreSQL)
- `ofp_redis` (Redis)
- `ofp_api` (FastAPI)

### Step 2: Verifica che Funzioni

```bash
# Health check
curl http://localhost:8000/health

# Risposta attesa: {"status":"healthy"}
```

### Step 3: Apri Swagger UI (Opzionale ma Consigliato)

Apri nel browser: **http://localhost:8000/docs**

Qui puoi vedere tutti gli endpoint disponibili e testarli direttamente.

## Test con Agenti Demo

### Opzione 1: Script Python Demo (Consigliato)

Abbiamo creato script Python che simulano agenti che interagiscono con il Floor Manager:

```bash
# Test conversazione multi-agente completa
python examples/agents/demo_agents.py

# Test priorità floor control
python examples/agents/demo_agents.py priority
```

Lo script:
1. ✅ Crea 3 agenti demo (Text, Image, Data)
2. ✅ Li registra nel registry
3. ✅ Testa floor control con priorità
4. ✅ Simula conversazione multi-agente
5. ✅ Mostra invio utterance tra agenti

**Output esempio**:
```
============================================================
DEMO: Conversazione Multi-Agente con Floor Control
============================================================

📝 Registrazione agenti...
✅ Text Agent registrato con successo
✅ Image Agent registrato con successo
✅ Data Agent registrato con successo

🎤 Test Floor Control:
------------------------------------------------------------

1. Text Agent richiede floor (priority 5)...
🎤 Text Agent ha ottenuto il floor
   Floor holder: tag:demo.com,2025:text_agent

2. Image Agent richiede floor (priority 3)...
⏳ Image Agent è in coda per il floor
   Floor holder: tag:demo.com,2025:text_agent

...
```

### Opzione 2: Test Manuale con curl

#### 1. Registra Agenti di Esempio

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

#### 2. Verifica Agenti Registrati

```bash
# Lista tutti gli agenti
curl http://localhost:8000/api/v1/agents/ | jq

# Trova agenti per capability
curl http://localhost:8000/api/v1/agents/capability/text_generation | jq
```

#### 3. Test Floor Control

```bash
# Definisci conversation ID
CONV_ID="conv_test_$(date +%s)"

# Agent 1 richiede floor (priority 5)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:example.com,2025:text_agent\",
    \"priority\": 5
  }" | jq

# Verifica chi ha il floor
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq

# Agent 2 richiede floor (priority 3 - sarà in coda)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:example.com,2025:image_agent\",
    \"priority\": 3
  }" | jq

# Agent 1 invia utterance ad Agent 2
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"sender_speakerUri\": \"tag:example.com,2025:text_agent\",
    \"target_speakerUri\": \"tag:example.com,2025:image_agent\",
    \"text\": \"Ciao ImageBot, puoi generare un'immagine di un tramonto?\"
  }" | jq

# Agent 1 rilascia floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:example.com,2025:text_agent\"
  }" | jq

# Verifica nuovo floor holder (dovrebbe essere Agent 2)
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq
```

## Test con Script Python

### Script Demo Completo

Crea un file `test_floor_demo.py`:

```python
#!/usr/bin/env python3
"""
Test completo del Floor Manager con agenti demo
"""

import asyncio
from examples.agents.demo_agents import DemoAgent
from datetime import datetime

async def main():
    print("🚀 Test Floor Manager con Agenti Demo")
    print("=" * 60)
    
    # Crea agenti
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
        # Registra
        await text.register()
        await image.register()
        
        # Test floor
        await text.request_floor(conv_id, priority=5)
        await image.request_floor(conv_id, priority=3)
        
        # Invia utterance
        await text.send_utterance(conv_id, image.speaker_uri, "Hello!")
        
        # Release
        await text.release_floor(conv_id)
        
        print("\n✅ Test completato!")
        
    finally:
        await text.close()
        await image.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Esegui:
```bash
python test_floor_demo.py
```

## Scenari di Test

### Scenario 1: Conversazione Sequenziale

**Obiettivo**: Testare che gli agenti prendano il floor in sequenza.

```bash
# Usa lo script demo
python examples/agents/demo_agents.py
```

**Cosa testa**:
- Registrazione agenti
- Richiesta floor sequenziale
- Coda floor con priorità
- Release floor e passaggio al prossimo

### Scenario 2: Priorità Floor

**Obiettivo**: Verificare che le priorità funzionino correttamente.

```bash
python examples/agents/demo_agents.py priority
```

**Cosa testa**:
- Agenti con priorità diverse
- Comportamento quando un agente con priorità più alta richiede floor

### Scenario 3: Multi-Party Conversation

**Obiettivo**: Testare conversazione con 3+ agenti simultanei.

```bash
# Esegui test workflow completo
./examples/test_workflow.sh
```

**Cosa testa**:
- Registrazione multipla agenti
- Floor control multi-party
- Invio utterance tra più agenti
- Discovery per capability

## Verifica Funzionamento

### Check Logs

```bash
# Logs in tempo reale
docker-compose logs -f api

# Cerca errori
docker-compose logs api | grep -i error
```

### Check Status

```bash
# Status servizi
docker-compose ps

# Health check
curl http://localhost:8000/health

# Lista agenti
curl http://localhost:8000/api/v1/agents/ | jq
```

### Check Floor State

```bash
# Per ogni conversation_id, verifica floor holder
CONV_ID="conv_test_001"
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq
```

## Troubleshooting

### Problema: Script Python non trova moduli

```bash
# Assicurati di essere nella directory root del progetto
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Installa dipendenze
pip install httpx

# Esegui con PYTHONPATH
PYTHONPATH=. python examples/agents/demo_agents.py
```

### Problema: Agenti non si registrano

```bash
# Verifica che l'API sia attiva
curl http://localhost:8000/health

# Controlla log
docker-compose logs api | tail -20

# Verifica formato speakerUri (deve essere URI valido)
# Esempio corretto: "tag:example.com,2025:agent_1"
```

### Problema: Floor non viene concesso

```bash
# Verifica che l'agente sia registrato
curl http://localhost:8000/api/v1/agents/ | jq

# Controlla floor holder
curl http://localhost:8000/api/v1/floor/holder/CONV_ID | jq

# Verifica log floor manager
docker-compose logs api | grep -i floor
```

## Prossimi Passi

1. **Esplora Swagger UI**: http://localhost:8000/docs
2. **Modifica agenti demo**: Vedi `examples/agents/demo_agents.py`
3. **Crea il tuo agente**: Estendi `DemoAgent` o `BaseAgent`
4. **Testa pattern orchestrazione**: Vedi `src/orchestration/`

## Riferimenti

- **Setup Completo**: `docs/SETUP.md`
- **Architettura**: `docs/ARCHITECTURE_DETAILED.md`
- **API Reference**: http://localhost:8000/docs
- **Quick Start**: `docs/QUICKSTART.md`

