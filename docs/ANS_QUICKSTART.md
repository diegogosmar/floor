# ANS: Agent Name Server - Quick Start

## 🎯 What is ANS?

**ANS: Agent Name Server** - Public directory service for OFP-compliant agent discovery.

**Analogia**: Come **DNS** risolve `google.com` → `142.250.185.14`, **ANS** risolve `capability:text_generation` → `tag:example.com,2025:agent` + `https://agent.example.com`

## 🚀 Quick Start (3 Steps)

### 1. Start ANS

```bash
uvicorn src.ans.main:app --port 8001 --reload
```

**Verify**: `curl http://localhost:8001/health`

### 2. Publish Agent Manifest

```python
from src.ans.client import ANSClient
from src.ans.models import ManifestData, ConversantIdentification

client = ANSClient("http://localhost:8001")

manifest = ManifestData(
    identification=ConversantIdentification(
        speakerUri="tag:example.com,2025:my_agent",
        serviceUrl="http://localhost:8002",
        conversationalName="My AI Agent",
        capabilities=["text_generation"]
    )
)

await client.publish_manifest(manifest)
```

### 3. Discover Agents

```python
# Search by capability
agents = await client.search_by_capability("text_generation")

# Use discovered agent
if agents:
    agent = agents[0]
    print(f"Found: {agent.identification.conversationalName}")
    print(f"Service URL: {agent.identification.serviceUrl}")
```

## 📋 Run Demo

```bash
# Terminal 1: Start ANS
uvicorn src.ans.main:app --port 8001

# Terminal 2: Run demo
python examples/ans_demo.py
```

## 🔧 API Endpoints

- `POST /api/v1/manifests/publish` - Publish manifest (OFP envelope)
- `POST /api/v1/manifests/get` - Get manifests (OFP envelope)
- `GET /api/v1/manifests/search` - Search (REST API)
- `GET /health` - Health check

## 📚 Full Documentation

- **Usage Guide**: [docs/MANIFEST_SERVER_USAGE.md](MANIFEST_SERVER_USAGE.md)
- **Proposal**: [docs/MANIFEST_SERVER_PROPOSAL.md](MANIFEST_SERVER_PROPOSAL.md)

