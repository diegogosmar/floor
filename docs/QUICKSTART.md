# Quick Start Guide - Open Floor Protocol

## 🚀 Avvio Rapido in 5 Minuti

### 1. Avvia i Servizi

```bash
# Vai nella directory del progetto
cd /Users/diego.gosmar/Documents/OFP/FLOOR

# Avvia servizi con Docker Compose
docker-compose up -d

# Attendi che i servizi siano pronti (circa 10 secondi)
sleep 10

# Verifica che siano attivi
docker-compose ps
```

### 2. Verifica che Funzioni

```bash
# Health check
curl http://localhost:8000/health

# Dovresti vedere: {"status":"healthy"}
```

### 3. Testa con Agenti Demo (Consigliato)

**Opzione A: Script Python Demo**
```bash
# Installa httpx se necessario
pip install httpx

# Test conversazione multi-agente completa
python examples/agents/demo_agents.py

# Test priorità floor control
python examples/agents/demo_agents.py priority
```

**Opzione B: Script Bash**
```bash
# Test workflow completo
./examples/test_workflow.sh
```

### 4. Test Manuale Rapido

```bash
# Registra un agente
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:my_agent",
    "agent_name": "My Test Agent",
    "capabilities": ["text_generation"]
  }'

# Richiedi floor
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv",
    "speakerUri": "tag:test.com,2025:my_agent",
    "priority": 5
  }'

# Verifica floor holder
curl http://localhost:8000/api/v1/floor/holder/test_conv
```

### 5. Esplora l'API

Apri nel browser: **http://localhost:8000/docs**

Qui puoi:
- Vedere tutti gli endpoint disponibili
- Testare le API direttamente dal browser
- Leggere la documentazione di ogni endpoint

## 📖 Documentazione Completa

Per una guida dettagliata su come lanciare e testare il sistema:
- **[docs/LAUNCH_AND_TEST.md](LAUNCH_AND_TEST.md)** ⭐ **Guida Completa**
- [docs/SETUP.md](SETUP.md) - Setup dettagliato
- [docs/ARCHITECTURE_DETAILED.md](ARCHITECTURE_DETAILED.md) - Architettura

## Prossimi Passi

1. **Leggi la documentazione completa**: `docs/SETUP.md`
2. **Esplora i pattern di orchestrazione**: `src/orchestration/`
3. **Crea il tuo agente**: Vedi `src/agents/example_agent.py`
4. **Testa con pytest**: `pytest tests/`

## Comandi Utili

```bash
# Visualizza log
docker-compose logs -f api

# Riavvia servizi
docker-compose restart

# Ferma servizi
docker-compose down

# Pulisci tutto (ATTENZIONE: cancella dati)
docker-compose down -v
```

## Supporto

- **Documentazione**: `docs/`
- **Swagger UI**: http://localhost:8000/docs
- **Architettura**: `docs/architecture.md`
- **API Reference**: `docs/api.md`

