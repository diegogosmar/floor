# Troubleshooting Guide - Open Floor Protocol

## Errori Comuni e Soluzioni

### 1. Errore structlog: `KeyError: 'INFO'`

**Sintomo**:
```
KeyError: 'INFO'
File "/app/src/main.py", line 18, in <module>
    wrapper_class=structlog.make_filtering_bound_logger(settings.LOG_LEVEL),
```

**Causa**: `structlog.make_filtering_bound_logger()` richiede un livello numerico di logging, non una stringa.

**Soluzione**: ✅ **FIXATO** - Il codice ora converte automaticamente la stringa in livello logging.

**Verifica**: Riavvia i servizi:
```bash
docker-compose restart api
```

### 2. Errore PostgreSQL: `database "ofp_user" does not exist`

**Sintomo**:
```
FATAL:  database "ofp_user" does not exist
```

**Causa**: Qualcosa sta cercando di connettersi usando il nome utente come nome database invece del nome database corretto.

**Soluzione**: ✅ **FIXATO** - Healthcheck aggiornato per specificare il database corretto.

**Verifica**:
```bash
# Riavvia i servizi
docker-compose down
docker-compose up -d

# Verifica che PostgreSQL sia pronto
docker-compose exec postgres psql -U ofp_user -d ofp_db -c "SELECT 1;"
```

### 3. Warning Pydantic: `Field name "schema" shadows an attribute`

**Sintomo**:
```
UserWarning: Field name "schema" shadows an attribute in parent "BaseModel"
```

**Causa**: Il campo `schema` in `SchemaObject` shadowa un attributo di `BaseModel`.

**Soluzione**: ✅ **MIGLIORATO** - Aggiunta configurazione per evitare conflitti. È solo un warning e non blocca l'esecuzione.

### 4. Porta già in uso

**Sintomo**:
```
Error: bind: address already in use
```

**Soluzione**:
```bash
# Trova processo che usa la porta
lsof -i :8000

# Kill processo o cambia porta in .env
# PORT=8001
```

### 5. Servizi non partono

**Sintomo**: `docker-compose up` fallisce

**Soluzione**:
```bash
# Verifica log
docker-compose logs

# Ricostruisci immagini
docker-compose build --no-cache

# Riavvia tutto
docker-compose down -v
docker-compose up -d
```

### 6. API non risponde

**Sintomo**: `curl http://localhost:8000/health` non funziona

**Soluzione**:
```bash
# Verifica che il container sia attivo
docker-compose ps

# Controlla log API
docker-compose logs api

# Riavvia API
docker-compose restart api
```

### 7. Agenti non si registrano

**Sintomo**: Registrazione agente fallisce

**Soluzione**:
```bash
# Verifica che API sia attiva
curl http://localhost:8000/health

# Controlla formato speakerUri (deve essere URI valido)
# Corretto: "tag:example.com,2025:agent_1"
# Errato: "agent_1"

# Verifica log
docker-compose logs api | grep -i registry
```

### 8. Floor non viene concesso

**Sintomo**: Richiesta floor fallisce o non viene concessa

**Soluzione**:
```bash
# Verifica che agente sia registrato
curl http://localhost:8000/api/v1/agents/ | jq

# Controlla floor holder
curl http://localhost:8000/api/v1/floor/holder/CONV_ID | jq

# Verifica log floor manager
docker-compose logs api | grep -i floor
```

### 9. Import errors in Python

**Sintomo**: `ModuleNotFoundError` quando esegui script Python

**Soluzione**:
```bash
# Installa dipendenze
pip install -r requirements.txt

# Oppure usa PYTHONPATH
PYTHONPATH=. python examples/agents/demo_agents.py
```

### 10. Docker Compose warning: `version is obsolete`

**Sintomo**:
```
WARN[0000] docker-compose.yml: the attribute `version` is obsolete
```

**Soluzione**: ✅ **FIXATO** - Rimosso attributo `version` da docker-compose.yml (non più necessario in Docker Compose v2+).

## Comandi di Debug Utili

### Verifica Stato Servizi

```bash
# Status servizi
docker-compose ps

# Health check
curl http://localhost:8000/health

# Lista agenti
curl http://localhost:8000/api/v1/agents/ | jq
```

### Logs

```bash
# Tutti i log
docker-compose logs

# Solo API
docker-compose logs api

# Follow logs
docker-compose logs -f api

# Ultimi 50 righe
docker-compose logs --tail=50 api
```

### Database

```bash
# Connetti a PostgreSQL
docker-compose exec postgres psql -U ofp_user -d ofp_db

# Verifica connessione
docker-compose exec postgres psql -U ofp_user -d ofp_db -c "SELECT version();"

# Lista database
docker-compose exec postgres psql -U ofp_user -d postgres -c "\l"
```

### Redis

```bash
# Connetti a Redis
docker-compose exec redis redis-cli

# Ping Redis
docker-compose exec redis redis-cli ping

# Info Redis
docker-compose exec redis redis-cli info
```

### Reset Completo

```bash
# ATTENZIONE: Cancella tutti i dati!
docker-compose down -v
docker-compose up -d
```

## Verifica Fix Applicati

Dopo aver applicato i fix, verifica:

```bash
# 1. Riavvia servizi
docker-compose restart

# 2. Attendi qualche secondo
sleep 5

# 3. Verifica health
curl http://localhost:8000/health

# 4. Controlla log (non dovrebbero esserci errori)
docker-compose logs api | tail -20

# 5. Testa registrazione agente
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "speakerUri": "tag:test.com,2025:test_agent",
    "agent_name": "Test Agent",
    "capabilities": ["text_generation"]
  }'
```

## Supporto

Se i problemi persistono:

1. Controlla i log: `docker-compose logs`
2. Verifica configurazione: `.env` file
3. Consulta documentazione: `docs/`
4. Apri un issue nel repository

