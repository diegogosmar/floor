# Setup e Testing Guide - Open Floor Protocol Multi-Agent System

## Indice

1. [Prerequisiti](#prerequisiti)
2. [Setup Iniziale](#setup-iniziale)
3. [Avvio del Sistema](#avvio-del-sistema)
4. [Testing Base](#testing-base)
5. [Testing Multi-Agent](#testing-multi-agent)
6. [Pattern di Orchestrazione](#pattern-di-orchestrazione)
7. [Troubleshooting](#troubleshooting)

## Prerequisiti

- **Python 3.11+**
- **Docker e Docker Compose**
- **Git**
- **curl** o **HTTPie** per test API

## Setup Iniziale

### 1. Clone e Setup Ambiente

```bash
# Se non hai già clonato il repository
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione Ambiente

```bash
# Copia file di esempio
cp .env.example .env

# Modifica .env con le tue configurazioni (opzionale per sviluppo locale)
# Le configurazioni di default funzionano per Docker Compose
```

### 3. Verifica Struttura Progetto

```bash
# Verifica che la struttura sia corretta
tree -L 3 -I '__pycache__|*.pyc|venv' src/
```

Dovresti vedere:
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

## Avvio del Sistema

### Opzione 1: Docker Compose (Consigliato)

```bash
# Avvia tutti i servizi
docker-compose up -d

# Verifica che i servizi siano attivi
docker-compose ps

# Visualizza i log
docker-compose logs -f api
```

I servizi saranno disponibili su:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Swagger UI**: http://localhost:8000/docs

### Opzione 2: Sviluppo Locale

```bash
# Avvia solo PostgreSQL e Redis con Docker
docker-compose up -d postgres redis

# In un altro terminale, avvia l'API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing Base

### 1. Health Check

```bash
# Verifica che l'API sia attiva
curl http://localhost:8000/health

# Risposta attesa:
# {"status":"healthy"}
```

### 2. Registrazione Agente

```bash
# Registra un agente di esempio
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:example.com,2025:agent_1",
    "agent_name": "Example Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001"
  }'

# Risposta attesa:
# {
#   "success": true,
#   "speakerUri": "tag:example.com,2025:agent_1",
#   "capabilities": {...}
# }
```

### 3. Lista Agenti Registrati

```bash
curl http://localhost:8000/api/v1/agents/

# Trova agenti per capability
curl http://localhost:8000/api/v1/agents/capability/text_generation
```

### 4. Floor Control

```bash
# Richiedi floor per una conversazione
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "speakerUri": "tag:example.com,2025:agent_1",
    "priority": 5
  }'

# Verifica chi ha il floor
curl http://localhost:8000/api/v1/floor/holder/conv_001

# Rilascia floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "speakerUri": "tag:example.com,2025:agent_1"
  }'
```

### 5. Invio Utterance

```bash
# Invia un utterance
curl -X POST http://localhost:8000/api/v1/envelopes/utterance \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "sender_speakerUri": "tag:example.com,2025:agent_1",
    "target_speakerUri": "tag:example.com,2025:agent_2",
    "text": "Hello, how can you help me?"
  }'
```

### 6. Validazione Envelope

```bash
# Valida un envelope OFP
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

## Testing Multi-Agent

### Script di Test Multi-Agent

Crea un file `test_multi_agent.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"
CONV_ID="conv_multi_001"

echo "=== Registrazione Agenti ==="

# Registra Agent 1
curl -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_1",
    "agent_name": "Text Agent",
    "capabilities": ["text_generation"],
    "serviceUrl": "http://localhost:8001"
  }'

# Registra Agent 2
curl -X POST $BASE_URL/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_2",
    "agent_name": "Image Agent",
    "capabilities": ["image_generation"],
    "serviceUrl": "http://localhost:8002"
  }'

echo -e "\n=== Floor Control Multi-Agent ==="

# Agent 1 richiede floor
curl -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_1\",
    \"priority\": 5
  }"

# Agent 2 richiede floor (sarà in coda)
curl -X POST $BASE_URL/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_2\",
    \"priority\": 3
  }"

# Verifica holder
curl $BASE_URL/floor/holder/$CONV_ID

# Agent 1 rilascia floor
curl -X POST $BASE_URL/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_1\"
  }"

# Verifica nuovo holder (dovrebbe essere agent_2)
curl $BASE_URL/floor/holder/$CONV_ID
```

Esegui lo script:

```bash
chmod +x test_multi_agent.sh
./test_multi_agent.sh
```

## Pattern di Orchestrazione

### 1. Convener-Based Orchestration

```python
from src.orchestration.convener import ConvenerOrchestrator, ConvenerStrategy
from src.floor_manager.floor_control import FloorControl
from src.agent_registry.registry import AgentRegistry

# Inizializza componenti
floor_control = FloorControl()
registry = AgentRegistry()
convener = ConvenerOrchestrator(
    convener_speakerUri="tag:convener.com,2025:convener_1",
    floor_control=floor_control,
    agent_registry=registry,
    strategy=ConvenerStrategy.ROUND_ROBIN
)

# Invita partecipanti
await convener.invite_participant("conv_001", "tag:test.com,2025:agent_1")
await convener.invite_participant("conv_001", "tag:test.com,2025:agent_2")

# Concedi floor al prossimo
next_speaker = await convener.grant_floor_to_next("conv_001")
```

### 2. Collaborative Floor Passing

```python
from src.orchestration.collaborative import CollaborativeOrchestrator
from src.floor_manager.floor_control import FloorControl

floor_control = FloorControl()
collaborative = CollaborativeOrchestrator(floor_control)

# Agenti richiedono floor autonomamente
await collaborative.handle_floor_request("conv_001", "tag:test.com,2025:agent_1", priority=5)
await collaborative.handle_floor_request("conv_001", "tag:test.com,2025:agent_2", priority=3)

# Agente cede floor
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

# Delega a specialista
sub_conv_id = await hybrid.delegate_to_specialist(
    "conv_main_001",
    "tag:specialist.com,2025:specialist_1",
    "Analyze this data"
)

# Richiama delega
await hybrid.recall_delegation(sub_conv_id)
```

## Testing con Pytest

```bash
# Esegui tutti i test
pytest

# Esegui test specifici
pytest tests/test_floor_manager.py
pytest tests/test_envelope_router.py
pytest tests/test_agent_registry.py

# Con coverage
pytest --cov=src --cov-report=html

# Test verbose
pytest -v
```

## Troubleshooting

### Problema: Porta già in uso

```bash
# Verifica quale processo usa la porta
lsof -i :8000

# Modifica PORT nel .env o ferma il processo
```

### Problema: Database non raggiungibile

```bash
# Verifica che PostgreSQL sia attivo
docker-compose ps postgres

# Controlla i log
docker-compose logs postgres

# Riavvia il servizio
docker-compose restart postgres
```

### Problema: Agenti non si registrano

```bash
# Verifica che il registry sia inizializzato
curl http://localhost:8000/api/v1/agents/

# Controlla i log dell'API
docker-compose logs api | grep -i registry
```

### Debug Mode

```bash
# Avvia con log level DEBUG
LOG_LEVEL=DEBUG uvicorn src.main:app --reload

# Oppure modifica .env
echo "LOG_LEVEL=DEBUG" >> .env
```

## Prossimi Passi

1. **Esplora Swagger UI**: http://localhost:8000/docs
2. **Leggi Architecture Docs**: `docs/architecture.md`
3. **Vedi API Reference**: `docs/api.md`
4. **Esempi Docker Compose**: `examples/` (da creare)

## Supporto

Per problemi o domande:
- Controlla i log: `docker-compose logs`
- Verifica la documentazione OFP: https://github.com/open-voice-interoperability/openfloor-docs
- Apri un issue nel repository

