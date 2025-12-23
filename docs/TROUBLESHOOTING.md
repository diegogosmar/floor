# Troubleshooting Guide - Open Floor Protocol

## Common Errors and Solutions

### 1. structlog Error: `KeyError: 'INFO'`

**Symptom**:
```
KeyError: 'INFO'
File "/app/src/main.py", line 18, in <module>
    wrapper_class=structlog.make_filtering_bound_logger(settings.LOG_LEVEL),
```

**Cause**: `structlog.make_filtering_bound_logger()` requires a numeric logging level, not a string.

**Solution**: ✅ **FIXED** - Code now automatically converts string to logging level.

**Verify**: Restart services:
```bash
docker-compose restart api
```

### 2. PostgreSQL Error: `database "ofp_user" does not exist`

**Symptom**:
```
FATAL:  database "ofp_user" does not exist
```

**Cause**: Something is trying to connect using the username as database name instead of the correct database name.

**Solution**: ✅ **FIXED** - Healthcheck updated to specify the correct database.

**Verify**:
```bash
# Restart services
docker-compose down
docker-compose up -d

# Verify PostgreSQL is ready
docker-compose exec postgres psql -U ofp_user -d ofp_db -c "SELECT 1;"
```

### 3. Pydantic Warning: `Field name "schema" shadows an attribute`

**Symptom**:
```
UserWarning: Field name "schema" shadows an attribute in parent "BaseModel"
```

**Cause**: The `schema` field in `SchemaObject` shadows a `BaseModel` attribute.

**Solution**: ✅ **IMPROVED** - Added configuration to avoid conflicts. It's just a warning and doesn't block execution.

### 4. Port Already in Use

**Symptom**:
```
Error: bind: address already in use
```

**Solution**:
```bash
# Find process using the port
lsof -i :8000

# Kill process or change port in .env
# PORT=8001
```

### 5. Services Don't Start

**Symptom**: `docker-compose up` fails

**Solution**:
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Restart everything
docker-compose down -v
docker-compose up -d
```

### 6. API Not Responding

**Symptom**: `curl http://localhost:8000/health` doesn't work

**Solution**:
```bash
# Verify container is active
docker-compose ps

# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### 7. Agents Don't Register

**Symptom**: Agent registration fails

**Solution**:
```bash
# Verify API is active
curl http://localhost:8000/health

# Check speakerUri format (must be valid URI)
# Correct: "tag:example.com,2025:agent_1"
# Wrong: "agent_1"

# Check logs
docker-compose logs api | grep -i registry
```

### 8. Floor Not Granted

**Symptom**: Floor request fails or is not granted

**Solution**:
```bash
# Verify agent is registered
curl http://localhost:8000/api/v1/agents/ | jq

# Check floor holder
curl http://localhost:8000/api/v1/floor/holder/CONV_ID | jq

# Check floor manager logs
docker-compose logs api | grep -i floor
```

### 9. Import Errors in Python

**Symptom**: `ModuleNotFoundError` when running Python scripts

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or use PYTHONPATH
PYTHONPATH=. python examples/agents/demo_agents.py
```

### 10. Docker Compose Warning: `version is obsolete`

**Symptom**:
```
WARN[0000] docker-compose.yml: the attribute `version` is obsolete
```

**Solution**: ✅ **FIXED** - Removed `version` attribute from docker-compose.yml (no longer needed in Docker Compose v2+).

## Useful Debug Commands

### Check Service Status

```bash
# Service status
docker-compose ps

# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/api/v1/agents/ | jq
```

### Logs

```bash
# All logs
docker-compose logs

# API only
docker-compose logs api

# Follow logs
docker-compose logs -f api

# Last 50 lines
docker-compose logs --tail=50 api
```

### Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U ofp_user -d ofp_db

# Verify connection
docker-compose exec postgres psql -U ofp_user -d ofp_db -c "SELECT version();"

# List databases
docker-compose exec postgres psql -U ofp_user -d postgres -c "\l"
```

### Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Ping Redis
docker-compose exec redis redis-cli ping

# Redis info
docker-compose exec redis redis-cli info
```

### Complete Reset

```bash
# WARNING: Deletes all data!
docker-compose down -v
docker-compose up -d
```

## Verify Applied Fixes

After applying fixes, verify:

```bash
# 1. Restart services
docker-compose restart

# 2. Wait a few seconds
sleep 5

# 3. Verify health
curl http://localhost:8000/health

# 4. Check logs (should not have errors)
docker-compose logs api | tail -20

# 5. Test agent registration
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:test_agent",
    "agent_name": "Test Agent",
    "capabilities": ["text_generation"]
  }'
```

## Support

If problems persist:

1. Check logs: `docker-compose logs`
2. Verify configuration: `.env` file
3. Consult documentation: `docs/`
4. Open an issue in the repository
