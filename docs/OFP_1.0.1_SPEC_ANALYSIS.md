# OFP 1.0.1 Specification Analysis

Based on: [Open Floor Inter-Agent Message Specification Version 1.0.1](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)

## Key Findings from Official Spec

### ✅ 1. NO Central Agent Registration

**From Spec Section 0.5 - Discovery**:
- Discovery happens via `getManifests` and `publishManifests` events
- Agents request manifests dynamically when needed
- No central registry mentioned
- **Validation**: Our Phase 1 (removing agent registry) is CORRECT ✅

**From Spec Section 1.17-1.18**:
```
getManifests Event: "Request manifest information from one or more agents"
publishManifests Event: "Response to getManifests containing agent manifest(s)"
```
- This is **dynamic discovery**, not static registration
- Agents respond to requests, no central database

### ✅ 2. Floor Manager Architecture

**From Spec Section 0.2**:
> "The conversational floor manager acts as a hub to coordinate the conversation."

**From Spec Section 0.4.3 - Floor Management**:
> "The floor manager is in control of which conversants are engaged in a conversation at any given moment."

**Key Point**: Floor Manager is a SINGLE component that:
- Coordinates conversations (hub)
- Routes messages (implicit)
- Manages floor control

**Validation**: Our Phase 2 (merging envelope router into Floor Manager) is CORRECT ✅

### ⚠️ 3. Floor Manager vs Convener - CLARIFICATION NEEDED

**From Spec Section 0.4.3**:
> "In some cases a **convener agent** may also be present to mediate the conversation on the floor in a manner analogous to a chair moderating a meeting."

**From Spec Section 2.2 - Minimal Conversation Floor Manager Behaviors**:
> "These are the minimal floor management behaviors to be implemented by a floor manager **in the absence of a convener**."

**CRITICAL INSIGHT**:
- **Convener** = OPTIONAL agent that mediates conversations (like a meeting chair)
- **Floor Manager** = Required component with MINIMAL behaviors if no convener
- If convener present: Floor Manager can delegate floor decisions to convener
- If no convener: Floor Manager uses minimal behavior (simple queue)

**Our Current Understanding** (needs adjustment):
- ❌ "FloorControl is the Convener" - WRONG
- ✅ "FloorControl implements floor management logic" - CORRECT
- ✅ "Floor Manager can have minimal behavior or use a convener" - CORRECT

**Correct Architecture**:
```
FloorManager
  ├── Envelope Processing (built-in)
  ├── Envelope Routing (built-in)
  └── Floor Control Logic
      ├── Option A: Minimal Behavior (no convener)
      └── Option B: Delegate to Convener Agent (if present)
```

### ✅ 4. Privacy Flag Behavior

**From Spec Section 2.2**:
> "Privacy flags are ignored on ALL events apart from utterance"

**Validation**: Our implementation in `FloorManager.route_envelope()` is CORRECT ✅

### 📋 5. Floor Control Events (Section 1.19-1.22)

**requestFloor (1.19)**:
- Agent requests floor access
- Can include priority information
- Floor Manager decides whether to grant

**grantFloor (1.20)**:
- Floor Manager grants floor to an agent
- Includes `floorGranted` in conversation object

**revokeFloor (1.21)**:
- Floor Manager revokes floor (e.g., timeout, override)
- Includes reason (e.g., `@timeout`, `@override`)

**yieldFloor (1.22)**:
- Agent voluntarily releases floor
- Floor Manager processes queue for next agent

### 📋 6. Conversation Object Structure (Section 1.6)

**NEW in 1.0.1**:
```json
{
  "conversation": {
    "id": "...",
    "assignedFloorRoles": {
      "convener": "tag:example.com,2025:convener_agent"
    },
    "floorGranted": {
      "speakerUri": "tag:example.com,2025:agent1",
      "grantedAt": "2025-01-06T..."
    },
    "conversants": [...]
  }
}
```

**Key Fields**:
- `assignedFloorRoles`: Who has floor roles (e.g., convener)
- `floorGranted`: Current floor holder information
- `conversants`: Participants (removed `persistentState` in 1.0.1)

**Validation**: Our implementation in `floor_control.py` includes this ✅

### 📋 7. Minimal Floor Manager Behaviors (Section 2.2)

**On Receipt of Events** (Table from Spec):

| Event | Minimal Floor Manager Behavior |
|-------|-------------------------------|
| requestFloor | If floor available: send grantFloor. If not: queue request, send grantFloor when available |
| yieldFloor | Release floor, send grantFloor to next in queue (if any) |
| grantFloor | Pass through (Floor Manager sends this, doesn't receive it) |
| revokeFloor | Pass through (Floor Manager sends this) |
| utterance | Pass through with privacy flag respected |
| invite | Delegate/Pass through |
| uninvite | Delegate/Pass through |
| acceptInvite | Delegate/Pass through |
| declineInvite | Delegate/Pass through |
| bye | Delegate/Pass through |
| getManifests | Delegate/Pass through |
| publishManifests | Delegate/Pass through |

**Key Insight**: Floor Manager:
1. **Processes** floor control events (requestFloor, yieldFloor)
2. **Sends** grantFloor and revokeFloor
3. **Routes** (pass through) all other events

### ✅ 8. No "Envelope Router" Component

**From entire spec**:
- No mention of "EnvelopeRouter" as a separate component
- Routing is implicit in Floor Manager's hub role
- Messages flow through Floor Manager

**Validation**: Phase 2 (merging router into Floor Manager) is CORRECT ✅

## Architecture Corrections Needed

### Current (After Phase 1-2)
```
FloorManager (includes routing) ✅
  └── FloorControl (floor decisions) ⚠️ Terminology issue
```

### Correct Per Spec
```
FloorManager (hub + routing + floor management)
  └── Floor Control Logic
      ├── Minimal Behavior (built-in)
      └── Optional: Delegate to Convener Agent
```

**Terminology Issue**:
- Our `FloorControl` class implements floor management logic
- This is NOT the "Convener" (which is an optional agent)
- This IS the Floor Manager's floor control logic
- Rename: `FloorControl` → `FloorControlLogic` or keep as `FloorControl`

**Important**: The "Convener" in the spec is an **OPTIONAL AGENT**, not a component of our system. Our system implements the **Floor Manager** with its floor control logic.

## Action Items Based on Spec

### ✅ Phase 1 VALIDATED
- Removing agent registry is CORRECT
- Dynamic discovery via getManifests/publishManifests is the spec way

### ✅ Phase 2 VALIDATED  
- Merging envelope router into Floor Manager is CORRECT
- Floor Manager is the hub that coordinates everything

### ⚠️ Phase 3 CLARIFICATION
- Don't rename `FloorControl` to `Convener` 
- The "Convener" in spec is an optional **agent**, not our component
- Our `FloorControl` is the Floor Manager's floor control logic
- Consider renaming: `FloorControl` → `FloorManagement` for clarity

### ✅ Implementation Checklist

1. **Floor Manager** (src/floor_manager/manager.py) ✅
   - [x] Envelope routing (built-in)
   - [x] Process floor control events
   - [x] Delegate to floor control logic
   - [x] Pass through other events

2. **Floor Control Logic** (src/floor_manager/floor_control.py) ✅
   - [x] requestFloor → grantFloor logic
   - [x] yieldFloor → next agent logic  
   - [x] Priority queue
   - [x] Update conversation metadata (assignedFloorRoles, floorGranted)
   - [x] Privacy flag only for utterance

3. **Conversation Object** ✅
   - [x] assignedFloorRoles
   - [x] floorGranted
   - [x] Remove persistentState (if present)

4. **Discovery** ❌ NOT IMPLEMENTED
   - [ ] getManifests event handling
   - [ ] publishManifests event handling
   - [ ] Dynamic manifest discovery
   - **NOTE**: This is NOT agent registration, it's dynamic discovery

5. **Events** ⚠️ PARTIALLY IMPLEMENTED
   - [x] requestFloor
   - [x] grantFloor
   - [x] revokeFloor
   - [x] yieldFloor
   - [ ] acceptInvite (NEW in 1.0.1)
   - [ ] getManifests
   - [ ] publishManifests

## Recommended Next Steps

1. ✅ **Keep Phase 1-2 as is** (validated by spec)

2. ⚠️ **Adjust Phase 3**: 
   - Don't rename to "Convener" (that's an optional agent)
   - Consider: `FloorControl` → `FloorManagement` for clarity
   - Document that "Convener" in spec = optional agent, not our component

3. ✅ **Continue with remaining phases** (documentation, examples, tests)

4. 📋 **Add in future**: 
   - getManifests/publishManifests handling (dynamic discovery)
   - acceptInvite event
   - Proper conversants tracking

## References

- [OFP 1.0.1 Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)
- Section 0.4.3: Floor Management
- Section 2.2: Minimal Conversation Floor Manager Behaviors
- Section 1.19-1.22: Floor Control Events


