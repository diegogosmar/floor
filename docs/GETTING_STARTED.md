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
cd /Users/diego.gosmar/Documents/OFP/FLOOR

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

**Option A: Python Script (Recommended)**
```bash
# Install httpx if needed
pip install httpx

# Test complete multi-agent conversation
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

**Option B: Swagger UI (Interactive)**
```bash
# Open in browser
open http://localhost:8000/docs
```

**Option C: Bash Script**
```bash
# Complete workflow test
./examples/test_workflow.sh
```

## 📋 Test Base

### Test 1: Registrazione Agente

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

**Risposta attesa**:
```json
{
  "success": true,
  "speakerUri": "tag:test.com,2025:agent_1",
  "capabilities": {...}
}
```

### Test 2: Lista Agenti

```bash
# Lista tutti gli agenti
curl http://localhost:8000/api/v1/agents/ | jq

# Trova agenti per capability
curl http://localhost:8000/api/v1/agents/capability/text_generation | jq
```

### Test 3: Floor Control

```bash
# Richiedi floor
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "speakerUri": "tag:test.com,2025:agent_1",
    "priority": 5
  }'

# Verifica chi ha il floor
curl http://localhost:8000/api/v1/floor/holder/conv_test_001 | jq

# Rilascia floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_test_001",
    "speakerUri": "tag:test.com,2025:agent_1"
  }'
```

### Test 4: Invio Utterance

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

## 🧪 Test Workflow Completo

### Opzione 1: Script Automatico

```bash
# Esegui test workflow completo
./examples/test_workflow.sh

# Lo script testa:
# - Registrazione 3 agenti
# - Floor control multi-agent
# - Invio utterance
# - Discovery per capability
# - Heartbeat updates
```

### Opzione 2: Test Manuale Step-by-Step

Vedi `docs/SETUP.md` per istruzioni dettagliate passo-passo.

## 🎯 Test Multi-Agent Scenario

### Scenario: 3 Agenti Collaborano

```bash
# Terminal 1: Avvia API (se non già avviata)
docker-compose up -d

# Terminal 2: Registra Agent 1
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_text",
    "agent_name": "Text Agent",
    "capabilities": ["text_generation"]
  }'

# Terminal 3: Registra Agent 2
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_image",
    "agent_name": "Image Agent",
    "capabilities": ["image_generation"]
  }'

# Terminal 4: Registra Agent 3
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:agent_data",
    "agent_name": "Data Agent",
    "capabilities": ["data_analysis"]
  }'

# Ora testa floor control con priorità
CONV_ID="conv_multi_001"

# Agent 1 richiede floor (priority 5)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_text\",
    \"priority\": 5
  }"

# Agent 2 richiede floor (priority 3 - sarà in coda)
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_image\",
    \"priority\": 3
  }"

# Verifica floor holder (dovrebbe essere agent_text)
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq

# Agent 1 rilascia floor
curl -X POST http://localhost:8000/api/v1/floor/release \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"speakerUri\": \"tag:test.com,2025:agent_text\"
  }"

# Verifica nuovo floor holder (dovrebbe essere agent_image)
curl http://localhost:8000/api/v1/floor/holder/$CONV_ID | jq
```

## 🔍 Verifica Funzionamento

### Check Logs

```bash
# Logs API
docker-compose logs api

# Logs con follow
docker-compose logs -f api

# Logs specifici servizio
docker-compose logs postgres
docker-compose logs redis
```

### Check Status

```bash
# Status servizi
docker-compose ps

# Health check API
curl http://localhost:8000/health

# Lista agenti registrati
curl http://localhost:8000/api/v1/agents/ | jq
```

### Check Database

```bash
# Connetti a PostgreSQL
docker-compose exec postgres psql -U ofp_user -d ofp_db

# Query esempio (se hai tabelle)
# SELECT * FROM agents;
```

## 🐛 Troubleshooting

### Problema: Porta 8000 già in uso

```bash
# Trova processo
lsof -i :8000

# Kill processo o cambia porta in .env
# PORT=8001
```

### Problema: Servizi non partono

```bash
# Verifica log
docker-compose logs

# Riavvia servizi
docker-compose restart

# Ricostruisci immagini
docker-compose build --no-cache
docker-compose up -d
```

### Problema: Database connection error

```bash
# Verifica PostgreSQL è attivo
docker-compose ps postgres

# Controlla variabili ambiente
docker-compose exec api env | grep POSTGRES

# Riavvia PostgreSQL
docker-compose restart postgres
```

### Problema: Agenti non si registrano

```bash
# Verifica registry è inizializzato
curl http://localhost:8000/api/v1/agents/

# Controlla log per errori
docker-compose logs api | grep -i registry

# Verifica formato speakerUri (deve essere URI valido)
```

## 📚 Documentazione Aggiuntiva

- **Setup Completo**: `docs/SETUP.md`
- **Quick Start**: `docs/QUICKSTART.md`
- **Architettura**: `docs/ARCHITECTURE_DETAILED.md`
- **API Reference**: `docs/api.md`
- **Swagger UI**: http://localhost:8000/docs

## 🎓 Next Steps

1. **Explore Swagger UI**: http://localhost:8000/docs
2. **Read Architecture**: `docs/ARCHITECTURE_DETAILED.md`
3. **Test Orchestration Patterns**: See examples in `src/orchestration/`
4. **Create Your Agent**: Extend `BaseAgent` in `src/agents/`
5. **Use Real LLM Agents**: See `docs/LLM_INTEGRATION.md` to integrate OpenAI, Anthropic, etc.
6. **Run Test Suite**: `pytest tests/`

## 💡 Tips

- Usa `jq` per formattare JSON responses: `curl ... | jq`
- Swagger UI è il modo più facile per esplorare l'API
- I log sono strutturati JSON, usa `jq` per filtrarli
- Per sviluppo locale senza Docker, avvia solo postgres/redis con Docker

## ✅ Checklist Setup

- [ ] Python 3.11+ installato
- [ ] Docker e Docker Compose installati
- [ ] Virtual environment creato e attivato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] File `.env` configurato
- [ ] Servizi Docker avviati (`docker-compose up -d`)
- [ ] Health check passa (`curl http://localhost:8000/health`)
- [ ] Swagger UI accessibile (http://localhost:8000/docs)
- [ ] Test workflow eseguito con successo

## 🆘 Supporto

Se hai problemi:
1. Controlla i log: `docker-compose logs`
2. Verifica documentazione: `docs/`
3. Controlla Swagger UI per esempi API
4. Apri un issue nel repository

