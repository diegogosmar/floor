# Database Architecture - PostgreSQL & Redis

## Overview

The Open Floor Protocol (OFP) system uses two complementary data storage technologies:

- **PostgreSQL**: Relational database for persistent storage
- **Redis**: In-memory data store for caching and message queuing

Both services are configured and available in the Docker Compose setup, but the current implementation uses in-memory data structures. This document explains their roles, configuration, current status, and planned implementation.

## PostgreSQL

### Purpose

PostgreSQL is a robust, open-source relational database management system (RDBMS) that will be used for:

1. **Agent Registry Persistence**
   - Store agent registrations with their capabilities
   - Maintain agent metadata (speakerUri, serviceUrl, capabilities)
   - Track agent heartbeat timestamps
   - Enable agent discovery queries

2. **Conversation State Storage**
   - Store conversation history and metadata
   - Track conversation participants
   - Maintain conversation context over time
   - Enable conversation replay and analysis

3. **Floor Control Persistence**
   - Store floor control state (current holder, request queue)
   - Enable recovery after system restarts
   - Support distributed floor management

### Current Configuration

PostgreSQL is configured in `src/config.py`:

```python
POSTGRES_HOST: str = "postgres"
POSTGRES_PORT: int = 5432
POSTGRES_DB: str = "ofp_db"
POSTGRES_USER: str = "ofp_user"
POSTGRES_PASSWORD: str = "ofp_password"
```

The connection URL is constructed as:
```
postgresql://ofp_user:ofp_password@postgres:5432/ofp_db
```

### Docker Setup

PostgreSQL 15 is configured in `docker-compose.yml`:

```yaml
postgres:
  image: postgres:15-alpine
  container_name: ofp_postgres
  environment:
    POSTGRES_DB: ${POSTGRES_DB:-ofp_db}
    POSTGRES_USER: ${POSTGRES_USER:-ofp_user}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ofp_password}
  ports:
    - "${POSTGRES_PORT:-5432}:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### Current Status

**Status**: ⚠️ **Configured but not yet implemented**

The current implementation uses in-memory Python dictionaries:

- `AgentRegistry._agents`: `Dict[str, AgentCapabilities]` - stores agents in memory
- `FloorControl._floor_holders`: `dict[str, dict]` - stores floor state in memory
- `FloorQueue._queues`: `dict[str, List[dict]]` - stores queue in memory

**Why in-memory for now?**
- Faster development and testing
- Simpler implementation for MVP
- No data loss concerns for development
- Easy to reset state by restarting

### Planned Implementation

According to `docs/IMPLEMENTATION_STATUS.md`, database persistence is planned:

- [ ] SQLAlchemy models for agent registry
- [ ] Conversation history storage
- [ ] Alembic migrations for schema management
- [ ] Connection pooling and transaction management

**Future Schema (Example)**:

```sql
-- Agent Registry
CREATE TABLE agents (
    speaker_uri VARCHAR PRIMARY KEY,
    agent_name VARCHAR NOT NULL,
    service_url VARCHAR,
    capabilities JSONB,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Floor Control
CREATE TABLE floor_holders (
    conversation_id VARCHAR PRIMARY KEY,
    speaker_uri VARCHAR NOT NULL,
    granted_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP
);
```

### Verification

To verify PostgreSQL is running:

```bash
# Check container status
docker-compose ps postgres

# Connect to PostgreSQL
docker-compose exec postgres psql -U ofp_user -d ofp_db

# Check version
docker-compose exec postgres psql -U ofp_user -d ofp_db -c "SELECT version();"

# List databases
docker-compose exec postgres psql -U ofp_user -d postgres -c "\l"
```

## Redis

### Purpose

Redis is an in-memory data structure store that will be used for:

1. **Caching**
   - Cache agent capabilities for fast lookups
   - Cache floor control state for quick access
   - Cache conversation metadata
   - Reduce database load

2. **Message Queue**
   - Queue floor requests for processing
   - Queue envelope routing tasks
   - Support asynchronous processing
   - Enable distributed message passing

3. **Session Management**
   - Store temporary session data
   - Manage distributed locks for floor control
   - Support pub/sub for real-time updates

### Current Configuration

Redis is configured in `src/config.py`:

```python
REDIS_HOST: str = "redis"
REDIS_PORT: int = 6379
REDIS_DB: int = 0
REDIS_PASSWORD: str = ""
```

The connection URL is constructed as:
```
redis://redis:6379/0
```

### Docker Setup

Redis 7 is configured in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: ofp_redis
  ports:
    - "${REDIS_PORT:-6379}:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
```

The `--appendonly yes` flag enables persistence (AOF - Append Only File).

### Current Status

**Status**: ⚠️ **Configured but not yet implemented**

The current implementation uses in-memory Python structures:

- `FloorQueue._queues`: `dict[str, List[dict]]` - Python dictionary
- `EnvelopeRouter._queue`: `asyncio.Queue` - Python asyncio queue
- `AgentRegistry._agents`: `Dict[str, AgentCapabilities]` - Python dictionary

**Why in-memory for now?**
- Sufficient for single-instance deployments
- Simpler implementation
- No network latency
- Easy to debug and test

### Planned Implementation

Redis will replace in-memory structures for:

1. **Floor Queue in Redis**
   ```python
   # Future: Use Redis lists for floor queues
   await redis.lpush(f"floor:queue:{conversation_id}", request_json)
   await redis.rpop(f"floor:queue:{conversation_id}")
   ```

2. **Agent Registry Cache**
   ```python
   # Future: Cache agent lookups
   await redis.setex(
       f"agent:{speakerUri}",
       ttl=300,
       value=json.dumps(agent_data)
   )
   ```

3. **Distributed Locks**
   ```python
   # Future: Lock floor control operations
   async with redis.lock(f"floor:lock:{conversation_id}", timeout=5):
       # Grant floor atomically
   ```

4. **Pub/Sub for Real-time Updates**
   ```python
   # Future: Publish floor events
   await redis.publish(
       f"floor:events:{conversation_id}",
       json.dumps(event_data)
   )
   ```

### Verification

To verify Redis is running:

```bash
# Check container status
docker-compose ps redis

# Connect to Redis CLI
docker-compose exec redis redis-cli

# Ping Redis
docker-compose exec redis redis-cli ping
# Expected: PONG

# Get Redis info
docker-compose exec redis redis-cli info

# Check keys (when implemented)
docker-compose exec redis redis-cli keys "*"
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    OFP Application                       │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Floor        │  │ Envelope     │  │ Agent        │   │
│  │ Manager      │  │ Router       │  │ Registry     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         │ (Future)        │ (Future)       │ (Future)   │
│         ▼                 ▼                 ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Redis      │  │   Redis      │  │   Redis      │   │
│  │   Queue      │  │   Cache      │  │   Cache      │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         └─────────────────┴─────────────────┘            │
│                          │                               │
│                          ▼                               │
│                  ┌──────────────┐                        │
│                  │  PostgreSQL  │                        │
│                  │  Persistent  │                        │
│                  │  Storage     │                        │
│                  └──────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## Current vs. Future Architecture

### Current (In-Memory)

```
Application → Python Dictionaries/Lists → Memory
```

**Pros:**
- Fast (no network latency)
- Simple to implement
- Easy to debug
- No external dependencies

**Cons:**
- Data lost on restart
- Not scalable (single instance)
- No persistence
- Memory limits

### Future (PostgreSQL + Redis)

```
Application → Redis (Cache/Queue) → PostgreSQL (Persistent)
```

**Pros:**
- Data persistence
- Scalable (multiple instances)
- Distributed caching
- Message queuing
- Recovery after restarts

**Cons:**
- Network latency
- More complex setup
- Requires connection management
- Additional infrastructure

## Migration Path

When implementing database persistence:

1. **Phase 1: Add SQLAlchemy Models**
   - Define models for agents, conversations, floor state
   - Create Alembic migrations
   - Add database connection pool

2. **Phase 2: Migrate Agent Registry**
   - Replace `AgentRegistry._agents` dict with database queries
   - Add caching layer with Redis
   - Implement connection retry logic

3. **Phase 3: Migrate Floor Control**
   - Store floor state in PostgreSQL
   - Use Redis for floor queue
   - Implement distributed locks

4. **Phase 4: Add Conversation Storage**
   - Store conversation history
   - Enable conversation replay
   - Add conversation analytics

## Configuration

### Environment Variables

Both databases can be configured via environment variables in `.env`:

```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ofp_db
POSTGRES_USER=ofp_user
POSTGRES_PASSWORD=ofp_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### Connection Strings

The application constructs connection strings automatically:

- **PostgreSQL**: `postgresql://user:password@host:port/database`
- **Redis**: `redis://host:port/db` or `redis://:password@host:port/db`

## Troubleshooting

### PostgreSQL Issues

**Connection refused:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

**Database doesn't exist:**
```bash
# Verify database exists
docker-compose exec postgres psql -U ofp_user -d postgres -c "\l"

# Create database if needed (usually auto-created)
docker-compose exec postgres psql -U ofp_user -d postgres -c "CREATE DATABASE ofp_db;"
```

### Redis Issues

**Connection refused:**
```bash
# Check if Redis is running
docker-compose ps redis

# Check logs
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli ping
```

**Memory issues:**
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Check max memory setting
docker-compose exec redis redis-cli config get maxmemory
```

## Best Practices

### PostgreSQL

1. **Connection Pooling**: Use SQLAlchemy connection pools
2. **Indexes**: Add indexes on frequently queried columns (speakerUri, conversation_id)
3. **Migrations**: Use Alembic for schema versioning
4. **Backups**: Regular backups of persistent data
5. **Monitoring**: Monitor query performance and connection counts

### Redis

1. **TTL**: Set expiration times for cached data
2. **Memory Limits**: Configure maxmemory and eviction policies
3. **Persistence**: Use AOF (Append Only File) for durability
4. **Connection Pooling**: Reuse Redis connections
5. **Monitoring**: Monitor memory usage and hit rates

## References

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Redis Documentation**: https://redis.io/docs/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Redis Python Client**: https://redis-py.readthedocs.io/

## Related Documentation

- [ARCHITECTURE_DETAILED.md](ARCHITECTURE_DETAILED.md) - Overall system architecture
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Current implementation status
- [SETUP.md](SETUP.md) - Setup instructions including database configuration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

