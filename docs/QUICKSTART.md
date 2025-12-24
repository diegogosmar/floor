# Quick Start Guide - Open Floor Protocol

## 🚀 Quick Start in 5 Minutes

### 1. Start Services

```bash
# Go to project directory
cd /path/to/floor

# Start services with Docker Compose
docker-compose up -d

# Wait for services to be ready (about 10 seconds)
sleep 10

# Verify they are active
docker-compose ps
```

### 2. Verify It Works

```bash
# Health check
curl http://localhost:8000/health

# You should see: {"status":"healthy"}
```

### 3. Test with Demo Agents (Recommended)

**Option A: Python Demo Script**
```bash
# Install httpx if needed
pip install httpx

# Test complete multi-agent conversation
python examples/agents/demo_agents.py

# Test floor control priority
python examples/agents/demo_agents.py priority
```

**Option B: Bash Script**
```bash
# Complete workflow test
./examples/test_workflow.sh
```

### 4. Quick Manual Test

```bash
# Register an agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:my_agent",
    "agent_name": "My Test Agent",
    "capabilities": ["text_generation"]
  }'

# Request floor
curl -X POST http://localhost:8000/api/v1/floor/request \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv",
    "speakerUri": "tag:test.com,2025:my_agent",
    "priority": 5
  }'

# Check floor holder
curl http://localhost:8000/api/v1/floor/holder/test_conv
```

### 5. Explore the API

Open in browser: **http://localhost:8000/docs**

Here you can:
- See all available endpoints
- Test APIs directly from the browser
- Read documentation for each endpoint

## 📖 Complete Documentation

For a detailed guide on how to launch and test the system:
- **[docs/LAUNCH_AND_TEST.md](LAUNCH_AND_TEST.md)** ⭐ **Complete Guide**
- [docs/SETUP.md](SETUP.md) - Detailed setup
- [docs/ARCHITECTURE_DETAILED.md](ARCHITECTURE_DETAILED.md) - Architecture

## Next Steps

1. **Read complete documentation**: `docs/SETUP.md`
2. **Explore orchestration patterns**: `src/orchestration/`
3. **Create your agent**: See `src/agents/example_agent.py`
4. **Test with pytest**: 
   ```bash
   # Install pytest-asyncio first
   pip install pytest-asyncio
   
   # Run tests
   pytest tests/
   ```

## Useful Commands

```bash
# View logs
docker-compose logs -f api

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Clean everything (WARNING: deletes data)
docker-compose down -v
```

## Support

- **Documentation**: `docs/`
- **Swagger UI**: http://localhost:8000/docs
- **Architecture**: `docs/architecture.md`
- **API Reference**: `docs/api.md`
