# Architettura Dettagliata - Open Floor Protocol Multi-Agent System

## Panoramica

Questo documento descrive l'architettura multi-layer del sistema Open Floor Protocol conforme alla specifica OFP 1.0.0.

## Architettura Multi-Layer

### Layer 1: Floor Manager

**Responsabilità**: Gestione delle primitive di floor control e coordinamento dei turni conversazionali.

**Componenti**:
- `FloorControl`: Implementa requestFloor, grantFloor, revokeFloor, yieldFloor
- `FloorQueue`: Gestisce coda di richieste floor con priorità

**Caratteristiche**:
- State machine per transizioni floor
- Priority queue per richieste concorrenti
- Timeout handling per floor grants
- Supporto per multi-party conversations

**API Endpoints**:
- `POST /api/v1/floor/request` - Richiedi floor
- `POST /api/v1/floor/release` - Rilascia floor
- `GET /api/v1/floor/holder/{conversation_id}` - Ottieni floor holder

### Layer 2: Conversation Envelope Router

**Responsabilità**: Routing di conversation envelope JSON tra agenti eterogenei, garantendo interoperabilità.

**Componenti**:
- `EnvelopeRouter`: Routing basato su speakerUri
- `OpenFloorEnvelope`: Struttura envelope conforme OFP 1.0.0
- Validazione schema JSON

**Caratteristiche**:
- Validazione envelope contro schema OFP 1.0.0
- Routing multi-party
- Supporto per eventi privati/pubblici
- Retry logic per delivery failure

**API Endpoints**:
- `POST /api/v1/envelopes/send` - Invia envelope completo
- `POST /api/v1/envelopes/utterance` - Invia utterance semplificato
- `POST /api/v1/envelopes/validate` - Valida envelope

### Layer 3: Agent Capability Registry

**Responsabilità**: Registro dinamico dei manifest degli agenti per discovery e delegazione.

**Componenti**:
- `AgentRegistry`: Storage e discovery di agenti
- `AgentCapabilities`: Definizione capability per agente

**Caratteristiche**:
- Storage manifest per agente
- Discovery per capability type
- Heartbeat tracking
- Cleanup automatico agenti stale

**API Endpoints**:
- `POST /api/v1/agents/register` - Registra agente
- `GET /api/v1/agents/{speakerUri}` - Ottieni agente
- `GET /api/v1/agents/capability/{type}` - Trova agenti per capability
- `POST /api/v1/agents/heartbeat` - Aggiorna heartbeat

## Pattern di Orchestrazione

### 1. Convener-Based Orchestration

**Uso**: Workflow strutturati con controllo esplicito del floor.

**Implementazione**: `src/orchestration/convener.py`

**Strategie**:
- Round-robin: Turni circolari tra partecipanti
- Priority-based: Floor basato su priorità
- Context-aware: Floor basato su contesto conversazionale

**Esempio**:
```python
convener = ConvenerOrchestrator(
    convener_speakerUri="tag:convener.com,2025:convener_1",
    strategy=ConvenerStrategy.ROUND_ROBIN
)
await convener.invite_participant("conv_001", "agent_1")
await convener.grant_floor_to_next("conv_001")
```

### 2. Collaborative Floor Passing

**Uso**: Comportamento emergente e auto-organizzazione.

**Implementazione**: `src/orchestration/collaborative.py`

**Caratteristiche**:
- Agenti negoziano autonomamente
- Floor manager arbitra solo conflitti
- Supporta emergent behavior

**Esempio**:
```python
collaborative = CollaborativeOrchestrator(floor_control)
await collaborative.handle_floor_request("conv_001", "agent_1", priority=5)
await collaborative.handle_floor_yield("conv_001", "agent_1", reason="@complete")
```

### 3. Hybrid Delegation Model

**Uso**: Task complessi che richiedono expertise diverse.

**Implementazione**: `src/orchestration/hybrid.py`

**Caratteristiche**:
- Master agent mantiene controllo principale
- Delega temporanea a specialist agents
- Sotto-conversazioni per sub-task
- Merge risultati in conversazione principale

**Esempio**:
```python
hybrid = HybridOrchestrator(master_speakerUri="master_1", ...)
sub_conv = await hybrid.delegate_to_specialist(
    "conv_main", "specialist_1", "Analyze data"
)
await hybrid.merge_sub_conversation(sub_conv, result)
```

## Flusso Dati

```
┌─────────────┐
│   Agent 1   │
└──────┬──────┘
       │ OpenFloorEnvelope
       ▼
┌─────────────────────┐
│ Envelope Router     │───► Validazione Schema OFP 1.0.0
└──────┬──────────────┘
       │
       ├──► Floor Manager ──► Verifica Floor Holder
       │
       └──► Agent Registry ──► Discovery Capability
       │
       ▼
┌─────────────┐
│   Agent 2   │
└─────────────┘
```

## Identificazione Agenti (OFP 1.0.0)

Per la specifica OFP 1.0.0, gli agenti sono identificati da:

- **speakerUri**: URI univoco persistente (es: `tag:example.com,2025:agent_1`)
- **serviceUrl**: URL del servizio agente (es: `http://localhost:8001`)

Il `speakerUri` deve essere:
- Unico per tutta la lifetime dell'agente
- Persistente
- Idealmente un URN o Tag URI

## Struttura Conversation Envelope

Conforme a OFP 1.0.0:

```json
{
  "openFloor": {
    "schema": {
      "version": "1.0.0",
      "url": "https://github.com/.../schema.json"
    },
    "conversation": {
      "id": "conv_001",
      "conversants": [...]
    },
    "sender": {
      "speakerUri": "tag:example.com,2025:agent_1",
      "serviceUrl": "http://localhost:8001"
    },
    "events": [
      {
        "to": {
          "speakerUri": "tag:example.com,2025:agent_2",
          "private": false
        },
        "eventType": "utterance",
        "parameters": {...}
      }
    ]
  }
}
```

## Event Types Supportati

- **Utterance Events**: `utterance`, `context`
- **Conversation Management**: `invite`, `uninvite`, `declineInvite`, `bye`
- **Discovery**: `getManifests`, `publishManifests`
- **Floor Management**: `requestFloor`, `grantFloor`, `revokeFloor`, `yieldFloor`

## Stack Tecnologico

- **Python 3.11+**: Runtime
- **FastAPI**: Web framework REST API
- **PostgreSQL**: Persistent storage (agent registry, conversation state)
- **Redis**: Caching e message queue
- **Pydantic**: Data validation e serialization
- **Structlog**: Structured logging

## Deployment

### Docker Compose

Servizi:
- `api`: FastAPI application
- `postgres`: PostgreSQL database
- `redis`: Redis cache

### Multi-Agent Setup

Vedi `examples/docker-compose.multi-agent.yml` per esempio con 3+ agenti.

## Estensibilità

Il sistema è progettato per essere esteso:

1. **Nuovi Pattern di Orchestrazione**: Implementa nuovi pattern in `src/orchestration/`
2. **Nuovi Event Types**: Estendi `EventType` enum e implementa handlers
3. **Custom Agents**: Estendi `BaseAgent` per nuovi tipi di agenti
4. **Semantic Cache**: Integra caching semantico per ottimizzazione

## Performance Considerations

- **Floor Queue**: Max size configurabile (default: 100)
- **Router Queue**: Max size configurabile (default: 1000)
- **Registry**: Max agents configurabile (default: 1000)
- **Heartbeat Timeout**: Configurabile per cleanup automatico

## Security

- CORS configurato per cross-origin requests
- Input validation tramite Pydantic
- Schema validation per envelope OFP
- (Futuro: Authentication/Authorization per produzione)

## Monitoring & Observability

- Structured logging con structlog
- Health check endpoint
- (Futuro: Prometheus metrics, distributed tracing)

## Riferimenti

- **OFP Specification**: https://github.com/open-voice-interoperability/openfloor-docs
- **Assistant Manifest Spec**: OFP Assistant Manifest Specification 1.0.0
- **Architecture Docs**: `docs/architecture.md`
- **API Docs**: `docs/api.md`

