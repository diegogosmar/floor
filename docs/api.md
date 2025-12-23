# API Documentation

## Open Floor Protocol API

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### Health Check

```
GET /health
```

Returns system health status.

#### Floor Control

```
POST /floor/request
```

Request floor for a conversation.

```
POST /floor/release
```

Release floor for a conversation.

#### Agent Registry

```
POST /agents/register
```

Register an agent with capabilities.

```
GET /agents/{agent_id}
```

Get agent information.

```
GET /agents/capability/{capability_type}
```

Find agents by capability.

#### Envelope Routing

```
POST /envelopes/send
```

Send an envelope to an agent.

```
POST /envelopes/broadcast
```

Broadcast envelope to all agents.

### Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

