# ANS: Agent Name Server

## 🎯 Overview

**ANS: Agent Name Server** - Public directory service for OFP-compliant agent manifests. Enables dynamic discovery of agents using native OFP events (`getManifests`/`publishManifests`).

**Analogia**: Come **DNS** (Domain Name Server) risolve nomi di dominio in indirizzi IP, **ANS** risolve capability/identità di agenti in serviceUrl e manifest.

**Esempio**:
- DNS: `google.com` → `142.250.185.14`
- ANS: `capability:text_generation` → `tag:example.com,2025:agent` + `https://agent.example.com`

## 🚀 Quick Start

### Start ANS

```bash
# Terminal 1: Start ANS (Agent Name Server)
uvicorn src.ans.main:app --port 8001 --reload
```

**Server URL**: `http://localhost:8001`

### Run Demo

```bash
# Terminal 2: Run demo
python examples/ans_demo.py
```

## 📋 Features

- ✅ **OFP 1.0.1 Compliant** - Uses native `getManifests`/`publishManifests` events
- ✅ **Dynamic Discovery** - Agents publish and discover manifests
- ✅ **Capability Search** - Find agents by capabilities
- ✅ **REST API** - Convenience endpoints for non-OFP clients
- ✅ **Client Library** - Easy integration with Floor Manager

## 📚 Documentation

- **Usage Guide**: [docs/MANIFEST_SERVER_USAGE.md](docs/MANIFEST_SERVER_USAGE.md) (ANS: Agent Name Server)
- **Proposal**: [docs/MANIFEST_SERVER_PROPOSAL.md](docs/MANIFEST_SERVER_PROPOSAL.md) (ANS: Agent Name Server)

## 🔧 API Endpoints

### OFP-Compliant

- `POST /api/v1/manifests/publish` - Publish manifests (OFP envelope)
- `POST /api/v1/manifests/get` - Get manifests (OFP envelope)

### REST API (Convenience)

- `GET /api/v1/manifests/search` - Search manifests
- `GET /api/v1/manifests/list` - List all manifests
- `GET /health` - Health check

## 💻 Client Usage

```python
from src.ans.client import ANSClient

client = ANSClient("http://localhost:8001")

# Publish manifest
await client.publish_manifest(manifest_data)

# Discover agents
agents = await client.search_by_capability("text_generation")
```

## 🎯 Next Steps

1. Extend to PostgreSQL (currently in-memory)
2. Add Web UI for browsing
3. Deploy publicly at ans.openfloorprotocol.org

