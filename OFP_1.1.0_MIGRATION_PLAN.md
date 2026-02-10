# Piano di Migrazione OFP 1.0.1 → 1.1.0

**Data**: 2026-02-08
**Progetto**: Open Floor Protocol Multi-Agent System
**Obiettivo**: Aggiornare l'implementazione da OFP 1.0.1 a OFP 1.1.0

## Analisi delle Differenze

### 1. Versione Schema
**Cambiamento**: 
- Da: `"version": "1.0.1"`
- A: `"version": "1.1.0"`

**Impatto**: Basso
- Aggiornare campo version in SchemaObject
- Aggiornare URL schema JSON

### 2. Conversation Object - Struttura Invariata ✅

**Analisi**: Le seguenti caratteristiche sono già implementate correttamente:
- ✅ `id` (obbligatorio) 
- ✅ `conversants` (opzionale, obbligatorio se >2 partecipanti)
- ✅ `assignedFloorRoles` (opzionale) - già implementato
- ✅ `floorGranted` (opzionale) - già implementato

**Nota**: Nella spec 1.1.0:
- `assignedFloorRoles` è un dictionary che mappa ruoli a array di speakerURIs
- `floorGranted` è un array di speakerURIs (non più object con metadata)

**Azione richiesta**: Verificare che l'implementazione corrente corrisponda esattamente alla spec 1.1.0

### 3. Floor Roles - Novità 🆕

**Spec 1.1.0 introduce**:
- `assignedFloorRoles` come dictionary: `{"convener": ["tag:example.com,2025:0001"]}`
- Solo ruolo `convener` definito (max cardinality: 1)
- Gli agenti dichiarano nel manifest quali ruoli possono svolgere

**Verifica necessaria**:
- ✅ Struttura `assignedFloorRoles` corretta
- ✅ Supporto ruolo `convener` 
- ❓ Verifica che sia implementato come dictionary (non object generico)

### 4. FloorGranted - Struttura Semplificata

**Spec 1.1.0**:
```json
"floorGranted": [
  "tag:user1.example.com,2025:1234",
  "tag:agent2.example.com,2025:5678"
]
```

**Implementazione attuale (1.0.1)**:
```python
floorGranted: Optional[Dict[str, Any]] = Field(
    None,
    description="Current floor grant information (speakerUri, grantedAt, etc.)"
)
```

**⚠️ BREAKING CHANGE**: 
- Da: `Dict[str, Any]` (object con metadata)
- A: `List[str]` (array di speakerURIs)

**Impatto**: MEDIO-ALTO
- Modificare tipo di dato in ConversationObject
- Aggiornare FloorControl per usare lista invece di dizionario
- Aggiornare test

### 5. Event Types - Invariati ✅

**Verifica**: Tutti gli event types esistenti sono identici in 1.1.0:
- ✅ utterance, context
- ✅ invite, uninvite, acceptInvite, declineInvite, bye
- ✅ getManifests, publishManifests
- ✅ requestFloor, grantFloor, revokeFloor, yieldFloor

**Nessun cambiamento richiesto**

### 6. Minimal Behaviors - Invariati ✅

**Verifica**: Le minimal behaviors sono identiche in 1.1.0
- Floor Manager behaviors (Spec Section 2.2)
- Servicing Assistant behaviors (Spec Section 2.1)

**Nessun cambiamento richiesto**

### 7. Privacy Flag - Invariato ✅

**Verifica**: Privacy flag handling identico
- Solo per `utterance` events
- Ignorato per tutti gli altri event types

**Nessun cambiamento richiesto**

## Checklist Modifiche Richieste

### Critical (Breaking Changes)
- [ ] **Modificare `floorGranted` da `Dict[str, Any]` a `List[str]`**
  - File: `src/floor_manager/envelope.py`
  - Linea: ~82
  - Impatto: FloorControl, test, esempi

### High Priority
- [ ] **Aggiornare versione schema a 1.1.0**
  - File: `src/floor_manager/envelope.py`
  - Linea: ~37
  - Cambiare default da `"1.0.1"` a `"1.1.0"`

- [ ] **Verificare struttura `assignedFloorRoles`**
  - File: `src/floor_manager/envelope.py`
  - Linea: ~78-81
  - Assicurarsi che sia `Dict[str, List[str]]` (non `Dict[str, str]`)

- [ ] **Aggiornare URL schema JSON**
  - File: `src/floor_manager/envelope.py`
  - Aggiornare riferimento URL a schema 1.1.0

### Medium Priority
- [ ] **Aggiornare FloorControl per gestire `floorGranted` come lista**
  - File: `src/floor_manager/floor_control.py`
  - Metodi: `_grant_floor()`, `_revoke_floor()`, `get_floor_holder()`

- [ ] **Aggiornare FloorManager**
  - File: `src/floor_manager/manager.py`
  - Verificare compatibilità con nuova struttura

- [ ] **Aggiornare esempi**
  - File: `examples/agents/*.py`
  - Aggiornare tutti gli esempi che usano floorGranted

### Low Priority
- [ ] **Aggiornare documentazione**
  - File: `README.md` - aggiornare riferimenti da 1.0.1 a 1.1.0
  - File: `docs/*.md` - aggiornare tutti i riferimenti
  - File: `OFP_1.0.1_COMPLIANCE_REPORT.md` - creare nuovo `OFP_1.1.0_COMPLIANCE_REPORT.md`

- [ ] **Aggiornare test suite**
  - File: `tests/*.py`
  - Aggiornare test per nuova struttura floorGranted

- [ ] **Aggiornare schema version in tutte le occorrenze**
  - Cercare tutti i file con `"1.0.1"` e aggiornare a `"1.1.0"`

## Piano di Implementazione

### Fase 1: Analisi e Preparazione ✅
1. ✅ Recuperare specifiche OFP 1.1.0
2. ✅ Analizzare differenze
3. ✅ Creare piano di migrazione (questo documento)

### Fase 2: Modifiche Core (Breaking Changes)
1. Modificare tipo `floorGranted` in `envelope.py`
2. Aggiornare versione schema a 1.1.0
3. Aggiornare `FloorControl` per nuova struttura
4. Verificare `assignedFloorRoles` come `Dict[str, List[str]]`

### Fase 3: Aggiornamento Componenti
1. Aggiornare `FloorManager`
2. Aggiornare test suite
3. Aggiornare esempi (demo agents, LLM agents)

### Fase 4: Documentazione
1. Aggiornare README.md
2. Creare OFP_1.1.0_COMPLIANCE_REPORT.md
3. Aggiornare tutti i documenti in `docs/`
4. Aggiornare CONTRIBUTING.md

### Fase 5: Testing e Validazione
1. Eseguire test suite completa
2. Testare esempi demo
3. Testare GUI Streamlit
4. Validare compliance con spec 1.1.0

## Rischi e Mitigazioni

### Rischio 1: Breaking Changes in `floorGranted`
**Impatto**: ALTO - Modifica struttura dati core
**Mitigazione**: 
- Implementare migrazione graduale
- Testare approfonditamente
- Aggiornare tutti i componenti dipendenti

### Rischio 2: Compatibilità Backward
**Impatto**: MEDIO - Client esistenti potrebbero non funzionare
**Mitigazione**:
- Considerare supporto temporaneo per entrambe le versioni
- Documentare breaking changes chiaramente
- Fornire guida di migrazione per client

### Rischio 3: Test Coverage
**Impatto**: MEDIO - Test potrebbero fallire dopo modifiche
**Mitigazione**:
- Aggiornare test prima di modificare codice
- Eseguire test dopo ogni modifica
- Verificare coverage rimanga >80%

## Stima Tempi

| Fase | Complessità | Tempo Stimato |
|------|-------------|---------------|
| Fase 1: Analisi | ✅ Completata | - |
| Fase 2: Core Changes | Alta | 3-4 ore |
| Fase 3: Componenti | Media | 2-3 ore |
| Fase 4: Documentazione | Bassa | 1-2 ore |
| Fase 5: Testing | Media | 2-3 ore |
| **TOTALE** | | **8-12 ore** |

## Note Aggiuntive

### Differenze Minime tra 1.0.1 e 1.1.0
L'analisi mostra che le differenze tra 1.0.1 e 1.1.0 sono **minime**:
1. Versione schema (cambio numerico)
2. Struttura `floorGranted` (da Dict a List)
3. Nessun nuovo event type
4. Nessuna modifica ai minimal behaviors

Questo suggerisce che la migrazione sarà **relativamente semplice** ma richiede **attenzione ai dettagli** per il breaking change su `floorGranted`.

### Compatibilità
Considerare implementare:
- Validazione che accetti entrambe le versioni temporaneamente
- Converter per migrare dati da 1.0.1 a 1.1.0
- Deprecation warnings per strutture vecchie

## Conclusione

La migrazione da OFP 1.0.1 a 1.1.0 è **fattibile** con:
- ✅ Poche modifiche strutturali
- ⚠️ Un breaking change importante (`floorGranted`)
- ✅ Nessun nuovo event type o behavior
- ✅ Stima: 8-12 ore di lavoro

**Raccomandazione**: Procedere con la migrazione seguendo il piano in 5 fasi, prestando particolare attenzione alla modifica di `floorGranted` e aggiornando tutti i test prima di considerare la migrazione completa.
