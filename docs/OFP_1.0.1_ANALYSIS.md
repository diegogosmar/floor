# OFP 1.0.1 Analysis - Changes from 1.0.0

## Overview

This document analyzes the differences between OFP 1.0.0 (current implementation) and OFP 1.0.1 (latest specification) and identifies required changes.

**Key Specification**: [OFP 1.0.1 Interoperable Conversation Envelope Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)

## Major Changes in 1.0.1

### 1. Floor as Autonomous State Machine with Convener

**Most Significant Change**: The floor is now clearly delineated as an **autonomous state machine** with all decision-making delegated to the **convener** (Floor Manager).

**Current Implementation (1.0.0)**:
- Floor Manager makes decisions automatically
- Simple queue-based priority system
- No explicit convener role

**1.0.1 Requirement**:
- Floor Manager **IS** the convener
- All floor decisions are made by the convener
- Floor state is managed as an autonomous state machine
- Clear separation: convener makes decisions, agents request/yield

### 2. New Conversation Object Fields

#### `assignedFloorRoles`
- **New field** in conversation object
- Contains roles assigned to conversants
- Includes `convener` role

#### `floorGranted`
- **New section** in conversation object
- Tracks current floor state
- Contains information about who has the floor

**Example Structure**:
```json
{
  "conversation": {
    "id": "conv_001",
    "assignedFloorRoles": {
      "convener": "tag:example.com,2025:floor_manager"
    },
    "floorGranted": {
      "speakerUri": "tag:example.com,2025:agent_1",
      "grantedAt": "2025-12-24T10:00:00Z"
    },
    "conversants": [...]
  }
}
```

### 3. New Event: `acceptInvite`

**Added**: `acceptInvite` event type

**Purpose**: Explicit acceptance of an invite (previously implicit)

**Current Implementation**: ❌ Not implemented

### 4. Event Changes

#### `dialogHistory` Moved
- **From**: Context event (removed)
- **To**: Invite event parameters

#### `Context` Event Removed
- Context event has been removed
- Context information now embedded in other events

**Current Implementation**: ⚠️ May need update if Context event is used

### 5. `persistentState` Removed from Conversants

**Removed**: `persistentState` field from conversant objects

**Reason**: State management issues in multi-party conversations

**Current Implementation**: ⚠️ Check if used in `ConversantObject`

### 6. Floor Management Minimal Behaviors

**1.0.1 Clarifies**:

1. **Privacy Flag Handling**:
   - Ignore privacy flag for **all events except utterance**
   - Only utterance events respect the `private` flag

2. **Event Processing**:
   - Simplify to delegate/pass-through model
   - Define how `requestFloor` translates to `grantFloor`/`revokeFloor`
   - Specify processing order of events

3. **Convener Role**:
   - Convener (Floor Manager) makes all floor decisions
   - Agents only request/yield
   - No agent-to-agent floor negotiation

## Impact Analysis

### High Priority Changes

#### 1. Update Conversation Object Model

**File**: `src/envelope_router/envelope.py`

**Changes Needed**:
```python
class ConversationObject(BaseModel):
    id: str
    conversants: Optional[List[ConversantObject]]
    assignedFloorRoles: Optional[Dict[str, str]] = Field(
        None,
        description="Assigned floor roles (e.g., convener)"
    )
    floorGranted: Optional[Dict[str, Any]] = Field(
        None,
        description="Current floor grant information"
    )
```

#### 2. Remove `persistentState` from ConversantObject

**File**: `src/envelope_router/envelope.py`

**Current**:
```python
class ConversantObject(BaseModel):
    identification: ConversantIdentification
    persistentState: Optional[Dict[str, Any]]  # ❌ Remove this
```

**Should be**:
```python
class ConversantObject(BaseModel):
    identification: ConversantIdentification
    # persistentState removed per OFP 1.0.1
```

#### 3. Add `acceptInvite` Event Type

**File**: `src/envelope_router/envelope.py`

**Add to EventType enum**:
```python
class EventType(str, Enum):
    # ... existing events ...
    ACCEPT_INVITE = "acceptInvite"  # ✅ Add this
```

#### 4. Update Floor Control to Explicitly Act as Convener

**File**: `src/floor_manager/floor_control.py`

**Changes Needed**:
- Add convener identification
- Track convener role in conversation
- Update floor grant to include `floorGranted` in conversation object
- Ensure all floor decisions are made by convener (already the case, but make explicit)

#### 5. Privacy Flag Handling

**File**: `src/envelope_router/router.py` or `src/floor_manager/floor_control.py`

**Rule**: Ignore `private` flag for all events **except** `utterance`

**Current**: ⚠️ Need to verify current behavior

#### 6. Update Schema Version

**Files**: Multiple files reference "1.0.0"

**Change**: Update to "1.0.1" where appropriate

### Medium Priority Changes

#### 7. Remove Context Event (if used)

**Check**: Search for `CONTEXT` event usage

**Action**: Remove if present, migrate to embedded context

#### 8. Move dialogHistory to Invite Event

**If used**: Update Invite event to include `dialogHistory` in parameters

### Low Priority / Documentation

#### 9. Update Documentation

- Update all references from "1.0.0" to "1.0.1"
- Update compliance documentation
- Add convener role explanation
- Document floor state machine behavior

## Implementation Plan

### Phase 1: Core Model Updates

1. ✅ Update `ConversationObject` with new fields
2. ✅ Remove `persistentState` from `ConversantObject`
3. ✅ Add `acceptInvite` event type
4. ✅ Update schema version references

### Phase 2: Floor Management Updates

5. ✅ Add convener role tracking
6. ✅ Update floor grant to set `floorGranted` in conversation
7. ✅ Implement privacy flag handling rules
8. ✅ Document floor state machine behavior

### Phase 3: Event Processing

9. ✅ Remove Context event (if used)
10. ✅ Move dialogHistory to Invite event (if used)
11. ✅ Update event processing order

### Phase 4: Testing & Documentation

12. ✅ Update all documentation
13. ✅ Add tests for new features
14. ✅ Verify backward compatibility

## Backward Compatibility

**Question**: Should we maintain 1.0.0 compatibility?

**Recommendation**: 
- Support both versions during transition
- Add version detection in envelope parsing
- Default to 1.0.1 for new conversations
- Support 1.0.0 for existing conversations

## Key Architectural Insight

**1.0.1 Clarification**: The Floor Manager **IS** the convener. This is not a new concept, but 1.0.1 makes it explicit:

- **Convener** = Floor Manager = Autonomous decision maker
- **Agents** = Request floor, yield floor, but don't decide
- **State Machine** = Floor state transitions managed by convener

This aligns with the current implementation where `FloorControl` makes all decisions, but we should:
1. Explicitly identify the Floor Manager as the convener
2. Track convener role in conversation object
3. Document the state machine behavior clearly

## References

- [OFP 1.0.1 Specification](https://github.com/open-voice-interoperability/openfloor-docs/blob/working_group/specifications/ConversationEnvelope/1.0.1/InteroperableConvEnvSpec.md)
- [OFP 1.0.0 Specification](https://github.com/open-voice-interoperability/openfloor-docs) (previous version)
- Current Implementation: `src/floor_manager/`, `src/envelope_router/`

