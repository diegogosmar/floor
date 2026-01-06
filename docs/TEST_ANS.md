# Test ANS (Agent Name Server)

## 🎯 Overview

Questa guida ti mostra come testare ANS in diversi modi:
1. **Test rapido** - Health check e API REST
2. **Test completo** - Demo script con workflow completo
3. **Test manuale** - Usando curl o Python direttamente

## 📋 Prerequisiti

Assicurati di avere installate le dipendenze:

```bash
pip install -r requirements.txt
```

## 🚀 Test Rapido (5 minuti)

### Step 1: Avvia ANS Server

```bash
# Terminal 1
uvicorn src.ans.main:app --port 8001 --reload
```

**Verifica**: Apri `http://localhost:8001/docs` per vedere la documentazione API interattiva.

### Step 2: Health Check

```bash
# Terminal 2
curl http://localhost:8001/health
```

**Output atteso**:
```json
{"status":"healthy","service":"ANS"}
```

### Step 3: Lista Manifest (vuota inizialmente)

```bash
curl http://localhost:8001/api/v1/manifests/list
```

**Output atteso**:
```json
[]
```

## 🎨 Test Completo (Demo Script)

### Step 1: Avvia ANS Server

```bash
# Terminal 1
uvicorn src.ans.main:app --port 8001 --reload
```

### Step 2: Esegui Demo Script

```bash
# Terminal 2
python examples/ans_demo.py
```

Il demo esegue automaticamente:
1. ✅ Pubblica un manifest di esempio
2. ✅ Cerca agenti per capability
3. ✅ Workflow completo con più agenti

## 🔧 Test Manuale con curl

### 1. Pubblica un Manifest (REST API)

```bash
curl -X POST http://localhost:8001/api/v1/manifests/search \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.example.com,2025:my_agent",
    "serviceUrl": "http://localhost:8002",
    "organization": "Test Corp",
    "conversationalName": "Test Agent",
    "capabilities": ["text_generation", "translation"]
  }'
```

**Nota**: Questo endpoint REST è per comodità. Per OFP-compliance, usa `/api/v1/manifests/publish` con envelope OFP.

### 2. Cerca Agent per Capability

```bash
curl "http://localhost:8001/api/v1/manifests/search?capability=text_generation"
```

### 3. Lista Tutti i Manifest

```bash
curl http://localhost:8001/api/v1/manifests/list
```

## 🐍 Test Manuale con Python

### Script di Test Base

```python
import asyncio
from src.ans.client import ANSClient
from src.ans.models import ManifestData, ConversantIdentification

async def test_ans():
    client = ANSClient("http://localhost:8001")
    
    # 1. Pubblica manifest
    manifest = ManifestData(
        identification=ConversantIdentification(
            speakerUri="tag:test.example.com,2025:test_agent",
            serviceUrl="http://localhost:8002",
            conversationalName="Test Agent",
            capabilities=["test"]
        )
    )
    
    success = await client.publish_manifest(manifest)
    print(f"Published: {success}")
    
    # 2. Cerca agenti
    agents = await client.search_by_capability("test")
    print(f"Found {len(agents)} agents")
    
    # 3. Lista tutti
    all_agents = await client.get_manifests()
    print(f"Total agents: {len(all_agents)}")
    
    await client.close()

asyncio.run(test_ans())
```

## 🧪 Test OFP-Compliant (Envelope)

### Pubblica Manifest con Envelope OFP

```python
import asyncio
import httpx
from src.floor_manager.envelope import (
    OpenFloorEnvelope,
    ConversationObject,
    EventObject,
    EventType,
    ConversantIdentification
)

async def test_ofp_publish():
    # Crea envelope OFP-compliant
    envelope = OpenFloorEnvelope(
        schema_obj="https://openfloorprotocol.org/schema/1.0.1",
        conversation=ConversationObject(
            id="test_publish",
            convener="tag:ans.example.com,2025:server"
        ),
        events=[
            EventObject(
                eventType=EventType.PUBLISH_MANIFESTS,
                data={
                    "manifests": [{
                        "identification": {
                            "speakerUri": "tag:test.example.com,2025:ofp_agent",
                            "serviceUrl": "http://localhost:8002",
                            "conversationalName": "OFP Test Agent"
                        },
                        "capabilities": ["ofp_compliant"]
                    }]
                }
            )
        ]
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/manifests/publish",
            json=envelope.model_dump(mode="json")
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

asyncio.run(test_ofp_publish())
```

## ✅ Checklist di Test

- [ ] ANS server si avvia senza errori
- [ ] Health check restituisce `{"status":"healthy"}`
- [ ] Lista manifest iniziale è vuota `[]`
- [ ] Pubblicazione manifest funziona
- [ ] Ricerca per capability funziona
- [ ] Lista manifest mostra i manifest pubblicati
- [ ] Client library funziona correttamente
- [ ] Envelope OFP-compliant funziona

## 🐛 Troubleshooting

### Errore: "Cannot connect to ANS"

**Causa**: ANS server non è avviato.

**Soluzione**:
```bash
uvicorn src.ans.main:app --port 8001
```

### Errore: "Port 8001 already in use"

**Causa**: Porta già occupata.

**Soluzione**: Usa una porta diversa:
```bash
uvicorn src.ans.main:app --port 8002
# Poi aggiorna l'URL nel client: ANSClient("http://localhost:8002")
```

### Errore: "Module not found"

**Causa**: Dipendenze non installate.

**Soluzione**:
```bash
pip install -r requirements.txt
```

## 📚 Risorse

- **Documentazione**: [README_ANS.md](../README_ANS.md)
- **Quick Start**: [ANS_QUICKSTART.md](ANS_QUICKSTART.md)
- **Proposal**: [MANIFEST_SERVER_PROPOSAL.md](MANIFEST_SERVER_PROPOSAL.md)

