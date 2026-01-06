# OFP 1.0.1 Refactoring Plan

## Critical Feedback Received

> "There is currently no concept or need to register agents in OFP. I'm not sure why you found it necessary."

> "There is no component called an envelope router. This function is satisfied by the Floor Manager."

> "What you call the 'floor manager' may actually be the 'convener'. In OFP 1.0.1 we define minimal what the floor manager should do in the absence of a convener but if a convener is present then the floor manager delegates this to the convener."

## Current Architecture Problems

### 1. Agent Registration (❌ DOES NOT EXIST IN OFP)

**Current Implementation**:
- `src/agent_registry/` - Complete agent registry module
- `src/api/registry.py` - Registration API endpoints
- Agents must register before participating
- Registry tracks capabilities and manifests

**OFP 1.0.1 Reality**:
- **No agent registration concept**
- Agents are identified only by their `speakerUri` in envelopes
- No central registry needed
- Agents simply send envelopes to participate

**Action**: REMOVE `src/agent_registry/` and related APIs

### 2. Envelope Router (❌ WRONG SEPARATION)

**Current Implementation**:
- `src/envelope_router/router.py` - Separate routing component
- Routes envelopes between agents
- Manages delivery and privacy flags

**OFP 1.0.1 Reality**:
- Envelope routing is **part of the Floor Manager**
- Not a separate component
- Floor Manager handles all envelope processing

**Action**: MERGE `EnvelopeRouter` into `FloorManager`

### 3. Floor Manager vs Convener (⚠️ TERMINOLOGY CONFUSION)

**Current Implementation**:
- `FloorControl` = What we call "Floor Manager"
- `ConvenerOrchestrator` = Orchestration pattern on top
- Confusion about which is which

**OFP 1.0.1 Reality**:
- **Floor Manager** = Minimal envelope processing (pass-through mode)
- **Convener** = Makes floor decisions (what our `FloorControl` does)
- If convener present: Floor Manager delegates to Convener
- If no convener: Floor Manager has minimal behavior

**Action**: CLARIFY terminology and architecture

## OFP 1.0.1 Correct Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FLOOR MANAGER                        │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │   Envelope Processing (built-in)                │   │
│  │   - Receive envelopes                           │   │
│  │   - Parse events                                │   │
│  │   - Route to handlers                           │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │   Convener (if present)                         │   │
│  │   - requestFloor → grantFloor decisions         │   │
│  │   - Priority queue management                   │   │
│  │   - yieldFloor → next agent                     │   │
│  │   - revokeFloor on timeout                      │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │   Minimal Behavior (if no convener)             │   │
│  │   - Simple pass-through                         │   │
│  │   - Basic floor control                         │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

                        ↕
                 OFP Envelopes
                        ↕

┌──────────┐    ┌──────────┐    ┌──────────┐
│ Agent A  │    │ Agent B  │    │ Agent C  │
│          │    │          │    │          │
│ (no reg  │    │ (no reg  │    │ (no reg  │
│ required)│    │ required)│    │ required)│
└──────────┘    └──────────┘    └──────────┘
```

## Refactoring Plan

### Phase 1: Remove Agent Registry (❌ DELETE)

**Files to Remove**:
- `src/agent_registry/registry.py`
- `src/agent_registry/capabilities.py`
- `src/api/registry.py`
- `tests/test_agent_registry.py`

**Files to Update**:
- `src/main.py` - Remove registry router
- `src/orchestration/convener.py` - Remove registry dependency
- `examples/agents/complete_ofp_demo.py` - Remove registration calls
- All documentation mentioning agent registration

**Impact**:
- Agents no longer register
- Capability discovery removed (not part of OFP)
- Simpler architecture matching OFP spec

### Phase 2: Merge Envelope Router into Floor Manager

**Current Structure**:
```
src/
  floor_manager/
    floor_control.py
  envelope_router/
    router.py
    envelope.py  <-- Keep (data models)
```

**Target Structure**:
```
src/
  floor_manager/
    manager.py          # Main Floor Manager (includes routing)
    convener.py         # Convener logic (floor decisions)
    envelope.py         # Envelope models (moved)
```

**Actions**:
1. Move `src/envelope_router/envelope.py` → `src/floor_manager/envelope.py`
2. Merge `EnvelopeRouter` class into `FloorManager` class
3. Rename `FloorControl` → `Convener`
4. Create new `FloorManager` class that:
   - Includes envelope routing (built-in)
   - Delegates to `Convener` if present
   - Has minimal behavior if no convener

### Phase 3: Correct Terminology

**Rename**:
- `floor_control.py` → `convener.py` (the class that makes floor decisions)
- `FloorControl` → `Convener`
- Create new `FloorManager` class

**New `FloorManager` class**:
```python
class FloorManager:
    """
    Floor Manager per OFP 1.0.1
    
    Responsibilities:
    - Receive and route envelopes
    - Delegate to convener if present
    - Minimal behavior if no convener
    """
    
    def __init__(self, convener: Optional[Convener] = None):
        self.convener = convener
        self._routes: Dict[str, Callable] = {}
    
    async def process_envelope(self, envelope: OpenFloorEnvelope):
        """Process incoming envelope"""
        for event in envelope.events:
            if event.eventType == EventType.REQUEST_FLOOR:
                if self.convener:
                    await self.convener.handle_floor_request(...)
                else:
                    # Minimal behavior: first-come-first-served
                    await self._minimal_floor_grant(...)
            # ... other events
```

### Phase 4: Update APIs

**Remove**:
- `/api/v1/agents/*` endpoints (registration, heartbeat, list agents)

**Keep**:
- `/api/v1/floor/*` endpoints (request, release, holder)
- `/api/v1/envelopes/*` endpoints (send, utterance)

**Update**:
- API documentation to reflect no registration needed
- Examples to show direct envelope sending

### Phase 5: Update Documentation

**Files to Update**:
- `README.md` - Remove agent registration mentions
- `docs/ARCHITECTURE_DETAILED.md` - Correct architecture diagram
- `docs/OFP_AGENT_INTEGRATION.md` - Remove registration steps
- `docs/GETTING_STARTED.md` - Simplify (no registration)
- `examples/agents/COMPLETE_OFP_DEMO.md` - Remove registration examples

**Key Messages**:
1. "No agent registration required in OFP"
2. "Floor Manager includes envelope routing (not separate)"
3. "Convener makes floor decisions"
4. "Floor Manager delegates to Convener if present"

### Phase 6: Update Examples

**Files to Update**:
- `examples/agents/complete_ofp_demo.py` - Remove registration
- `examples/agents/demo_agents.py` - Remove registration
- `examples/agents/llm_agent_example.py` - Simplify

**New Flow**:
```python
# OLD (incorrect)
await registry.register_agent(agent)
await floor_manager.request_floor(...)

# NEW (correct per OFP)
# Just send envelope directly - no registration!
envelope = create_envelope(
    sender_speakerUri="tag:example.com,2025:agent1",
    ...
)
await floor_manager.process_envelope(envelope)
```

## Implementation Order

1. ✅ **Phase 1**: Remove agent registry (biggest architectural change)
2. ✅ **Phase 2**: Merge envelope router into floor manager
3. ✅ **Phase 3**: Correct terminology (FloorControl → Convener, create FloorManager)
4. ✅ **Phase 4**: Update APIs (remove registration endpoints)
5. ✅ **Phase 5**: Update all documentation
6. ✅ **Phase 6**: Update all examples
7. ✅ **Phase 7**: Update tests
8. ✅ **Phase 8**: Verify OFP compliance

## Benefits of Refactoring

1. **Matches OFP 1.0.1 spec exactly**
2. **Simpler architecture** (no unnecessary registry)
3. **Clearer terminology** (Floor Manager vs Convener)
4. **Easier for agents to join** (no registration needed)
5. **Better separation of concerns**

## Breaking Changes

- ⚠️ All `/api/v1/agents/*` endpoints removed
- ⚠️ `src.agent_registry` module removed
- ⚠️ Agent registration no longer required or supported
- ⚠️ `FloorControl` renamed to `Convener`

## Migration Guide for Users

**Before (incorrect)**:
```python
# Register agent
await registry.register_agent(capabilities)

# Request floor
await floor_control.request_floor(...)
```

**After (correct per OFP)**:
```python
# No registration needed!
# Just create and send envelopes

# Request floor via envelope
envelope = create_floor_request_envelope(
    conversation_id="conv_001",
    sender_speakerUri="tag:example.com,2025:myagent"
)
await floor_manager.process_envelope(envelope)
```

## Timeline

- **Phase 1-3**: Core architecture (2-3 hours)
- **Phase 4**: API updates (1 hour)
- **Phase 5**: Documentation (2 hours)
- **Phase 6**: Examples (1 hour)
- **Phase 7**: Tests (1 hour)
- **Phase 8**: Verification (1 hour)

**Total Estimated Time**: 8-10 hours

## References

- [OFP 1.0.1 Specification](https://github.com/open-voice-interoperability/openfloor-docs/tree/main/specifications/ConversationEnvelope/1.0.0)
- Feedback received: "No agent registration in OFP"
- Feedback received: "Envelope router is part of Floor Manager"
- Feedback received: "Floor Manager delegates to Convener"

