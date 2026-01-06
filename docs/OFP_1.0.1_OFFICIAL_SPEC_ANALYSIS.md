# OFP 1.0.1 Official Specification Analysis

**Source**: [Open Floor Inter-Agent Message Specification Version 1.0.1](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)

## Executive Summary

After reviewing the official OFP 1.0.1 specification, our refactoring Phases 1-2 are **VALIDATED** ✅. However, Phase 3 needs adjustment based on correct terminology understanding.

## Critical Clarifications from Official Spec

### 1. ✅ NO Central Agent Registration (Phase 1 VALIDATED)

**From Spec Section 0.5 - Discovery**:
- Discovery is **dynamic** via `getManifests` and `publishManifests` events
- Agents request manifests when needed, not from a central registry
- No mention of agent registration anywhere in spec

**Quote from Spec**:
> "getManifests Event: Request manifest information from one or more agents"
> "publishManifests Event: Response to getManifests containing agent manifest(s)"

**Conclusion**: ✅ Our Phase 1 (removing agent registry) is **100% CORRECT**

### 2. ✅ Floor Manager Includes Routing (Phase 2 VALIDATED)

**From Spec Section 0.2**:
> "The conversational floor manager acts as a **hub** to coordinate the conversation."

**From Spec Section 0.4.3**:
> "The floor manager is in control of which conversants are engaged in a conversation at any given moment."

**Key Insight**: 
- Floor Manager = Hub = Coordinator
- No separate "EnvelopeRouter" component mentioned
- Routing is implicit in the hub role

**Conclusion**: ✅ Our Phase 2 (merging envelope router into Floor Manager) is **100% CORRECT**

### 3. ⚠️ Floor Manager vs Convener - CRITICAL CLARIFICATION

This is where we need to adjust our understanding:

**From Spec Section 0.4.3**:
> "In some cases a **convener agent** may also be present to mediate the conversation on the floor in a manner analogous to a chair moderating a meeting."

**From Spec Section 2.2 - Minimal Conversation Floor Manager Behaviors**:
> "These are the minimal floor management behaviors to be implemented by a floor manager **in the absence of a convener**."

**CRITICAL UNDERSTANDING**:

1. **Floor Manager** = The system component (what we're building)
   - Always present
   - Coordinates conversations
   - Routes messages
   - Manages floor control
   - Has **minimal behaviors** if no convener present

2. **Convener** = An OPTIONAL **AGENT** (not a system component)
   - Optional participant in conversation
   - Acts like a "meeting chair"
   - Mediates conversation flow
   - If present: Floor Manager can delegate decisions to it
   - If absent: Floor Manager uses minimal behaviors

**Our Current Misunderstanding**:
- ❌ "FloorControl is the Convener" - WRONG
- ❌ "We need to rename FloorControl to Convener" - WRONG

**Correct Understanding**:
- ✅ Floor Manager = Our main system component
- ✅ FloorControl = Floor Manager's floor control logic
- ✅ Convener = Optional external agent (not our code)

### 4. Correct Architecture Per Spec

```
┌─────────────────────────────────────────────────────────┐
│                   FLOOR MANAGER                         │
│                  (Our System Component)                 │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │   Envelope Processing & Routing (built-in)     │   │
│  │   - Receive envelopes                          │   │
│  │   - Route to agents                            │   │
│  │   - Hub functionality                          │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │   Floor Control Logic                          │   │
│  │   - requestFloor → grantFloor                  │   │
│  │   - yieldFloor → next agent                    │   │
│  │   - Priority queue                             │   │
│  │   - Minimal behaviors (per spec 2.2)           │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  Optional: Can delegate to Convener Agent if present   │
└─────────────────────────────────────────────────────────┘

                        ↕ Envelopes

┌──────────┐    ┌──────────┐    ┌─────────────────┐
│ Agent A  │    │ Agent B  │    │ Convener Agent  │
│          │    │          │    │   (Optional)    │
└──────────┘    └──────────┘    └─────────────────┘
```

## Minimal Floor Manager Behaviors (Section 2.2)

**Direct from Spec** - Table of behaviors:

| Event Received | Floor Manager Action |
|---------------|---------------------|
| **requestFloor** | If floor available: send **grantFloor**<br>If not: queue request, send **grantFloor** when available |
| **yieldFloor** | Release floor, send **grantFloor** to next in queue (if any) |
| **grantFloor** | Pass through (Floor Manager sends this, doesn't receive) |
| **revokeFloor** | Pass through (Floor Manager sends this) |
| **utterance** | Pass through (privacy flag ONLY respected for utterance) |
| **invite** | Delegate/Pass through |
| **uninvite** | Delegate/Pass through |
| **acceptInvite** | Delegate/Pass through |
| **declineInvite** | Delegate/Pass through |
| **bye** | Delegate/Pass through |
| **getManifests** | Delegate/Pass through |
| **publishManifests** | Delegate/Pass through |

**Key Insights**:
1. Floor Manager **processes** floor control (requestFloor, yieldFloor)
2. Floor Manager **sends** grantFloor and revokeFloor
3. Floor Manager **routes** (pass through) all other events
4. Privacy flag ONLY respected for utterance events

## New Features in 1.0.1

### 1. Conversation Object Updates (Section 1.6)

**NEW Fields**:
```json
{
  "conversation": {
    "id": "conv_001",
    "assignedFloorRoles": {
      "convener": "tag:example.com,2025:convener_agent"
    },
    "floorGranted": {
      "speakerUri": "tag:example.com,2025:agent1",
      "grantedAt": "2025-01-06T12:00:00Z"
    },
    "conversants": [
      {
        "identification": {
          "speakerUri": "tag:example.com,2025:agent1",
          "conversationalName": "Agent 1"
        }
      }
    ]
  }
}
```

**Changes from 1.0.0**:
- ✅ Added `assignedFloorRoles` (tracks who has floor roles like convener)
- ✅ Added `floorGranted` (current floor holder info)
- ❌ Removed `persistentState` from conversants (state management issues)
- ✅ Conversants now only have `identification` section

**Our Implementation Status**:
- ✅ `assignedFloorRoles` - Implemented in `floor_control.py`
- ✅ `floorGranted` - Implemented in `floor_control.py`
- ⚠️ Need to verify `persistentState` is not used

### 2. New Event: acceptInvite (Section 1.14)

**NEW in 1.0.1**:
```json
{
  "eventType": "acceptInvite",
  "to": {
    "speakerUri": "tag:example.com,2025:inviter"
  }
}
```

**Purpose**: Explicit acceptance of an invite

**Our Implementation Status**: ❌ Not implemented yet

### 3. dialogHistory Moved (Section 1.12)

**Change**:
- ❌ Removed from Context event (Context event removed entirely)
- ✅ Moved to Invite event parameters

**Our Implementation Status**: ⚠️ Need to verify

### 4. Privacy Flag Clarification (Section 2.2)

**From Spec**:
> "Privacy flags are ignored on ALL events apart from utterance"

**Our Implementation**: ✅ Already correct in `manager.py`:
```python
is_private = (
    event.to is not None
    and event.to.private
    and event.eventType == EventType.UTTERANCE  # Only for utterance!
)
```

## Validation of Our Refactoring

### ✅ Phase 1: Remove Agent Registry
**Spec Validation**: 100% CORRECT
- No agent registration in spec
- Dynamic discovery via getManifests/publishManifests
- Agents identified only by speakerUri

### ✅ Phase 2: Merge Envelope Router into Floor Manager  
**Spec Validation**: 100% CORRECT
- Floor Manager is the "hub"
- No separate router component in spec
- Routing is implicit in Floor Manager role

### ⚠️ Phase 3: Terminology Correction NEEDED
**Spec Validation**: Need to adjust approach
- ❌ Don't rename FloorControl to "Convener"
- ✅ "Convener" is an optional AGENT, not our component
- ✅ Keep FloorControl or rename to FloorManagement
- ✅ Document that our system implements "Floor Manager"

## Revised Phase 3 Plan

**OLD Plan** (incorrect):
- Rename `FloorControl` → `Convener`

**NEW Plan** (correct):
1. Keep `FloorControl` class name (or rename to `FloorManagement`)
2. Clarify in documentation:
   - Our system = **Floor Manager** (per spec)
   - `FloorControl` class = Floor Manager's floor control logic
   - "Convener" in spec = Optional external agent (not our code)
3. Update comments to reference "Floor Manager" not "Convener"
4. Document that we implement "Minimal Floor Manager Behaviors" per Section 2.2

## Implementation Checklist vs Spec

### ✅ Implemented Correctly

1. **Floor Manager Structure** ✅
   - [x] Envelope routing (built-in)
   - [x] Floor control logic
   - [x] Hub functionality

2. **Floor Control Events** ✅
   - [x] requestFloor handling
   - [x] grantFloor generation
   - [x] revokeFloor generation
   - [x] yieldFloor handling
   - [x] Priority queue

3. **Conversation Metadata** ✅
   - [x] assignedFloorRoles
   - [x] floorGranted

4. **Privacy Flag** ✅
   - [x] Only respected for utterance

### ❌ Not Yet Implemented

1. **Discovery Events** ❌
   - [ ] getManifests event handling
   - [ ] publishManifests event handling

2. **New Events** ❌
   - [ ] acceptInvite event (NEW in 1.0.1)

3. **Conversants Tracking** ⚠️
   - [ ] Track conversants in conversation object
   - [ ] Ensure no persistentState

## Recommended Actions

### Immediate (Complete Current Refactoring)

1. ✅ **Keep Phases 1-2 as is** (validated by spec)

2. ⚠️ **Revise Phase 3**:
   - Don't rename to "Convener"
   - Update documentation to clarify:
     - We implement "Floor Manager" (per spec)
     - "Convener" = optional agent (not our component)
   - Update comments in code

3. ✅ **Continue Phases 4-8** (documentation, examples, tests)

### Future Enhancements

4. 📋 **Add Discovery** (not critical for basic operation):
   - Implement getManifests handling
   - Implement publishManifests handling

5. 📋 **Add acceptInvite** (NEW in 1.0.1):
   - Add to EventType enum
   - Add minimal handling (pass through)

6. 📋 **Conversants Tracking**:
   - Track conversants in conversation object
   - Verify no persistentState usage

## References

- [OFP 1.0.1 Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)
- Section 0.4.3: Floor Management and Convener
- Section 2.2: Minimal Conversation Floor Manager Behaviors
- Section 1.6: Conversation Object (assignedFloorRoles, floorGranted)
- Section 1.14: acceptInvite Event (NEW)
- Section 1.19-1.22: Floor Control Events


