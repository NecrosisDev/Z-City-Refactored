# ADR-0003 — Explicit Character Representation State

- **Status:** Accepted for architecture; implementation deferred pending compatibility tests
- **Date:** 2026-07-14
- **Scope:** Player, fake ragdoll, recovery ragdoll, vehicle representation, death ragdoll, organism ownership, and client presentation

## Context

Current Z-City represents one character through several mutable entities and references: the player, active fake ragdoll, old/recovery ragdoll, death ragdoll, vehicle/seat, organism owner, networked entity fields, registries, and client camera follow state.

Transitions are not represented by one authoritative state machine. They are inferred from mutable fields, global flags, hook timing, entity validity, timers, and packet arrival. Recovery invokes ordinary player spawn under a global bypass flag, and vehicle entry intentionally force-fakes most players.

Trauma expands these mechanics but does not resolve the underlying authority problem. It adds more fake, vehicle, combat, rendering, organism, and adapter paths around the same mutable identity model.

## Decision

The refactored project will introduce one server-authoritative character representation record and transition generation.

The record will identify:

- stable character/player identity;
- current representation state;
- active physical entity;
- organism owner and generation;
- vehicle and seat when applicable;
- corpse/recovery entity when applicable;
- transition generation and reason;
- lifecycle owner for hooks, timers, constraints, callbacks, and network publications.

Initial representation states will distinguish at least:

1. upright;
2. entering fake;
3. fake controlled;
4. fake incapacitated;
5. recovering;
6. vehicle represented;
7. dead/corpse;
8. removed.

Exact names and subdivisions may change, but the state and generation semantics may not be replaced by entity-validity inference.

## Transition requirements

Every transition must:

1. validate the expected current generation and state;
2. prepare resources without publishing partial authority;
3. commit the new representation atomically from the project's perspective;
4. publish one versioned snapshot;
5. reject stale delayed work and client updates;
6. clean old resources through explicit ownership;
7. support rollback or fail-closed cleanup after preparation failure;
8. emit structured diagnostics.

## Compatibility strategy

Existing fields and hooks remain compatibility projections during migration, including:

- `ply.FakeRagdoll`;
- `NWEntity("FakeRagdoll")`;
- `hg.ragdollFake`;
- `ragdoll.ply`;
- `FakeRagdollOld` / `OldRagdoll`;
- `RagdollDeath`;
- `Ragdoll_Create`, `Fake`, `Fake Up`, `Should Fake Up`, and related hooks;
- the `Player Ragdoll` packet.

The compatibility layer may mirror authoritative state outward. Legacy fields must not remain independent writers after migration.

## Vehicle boundary

Vehicle support will use a capability-detected adapter that defines:

- whether fake representation is required or prohibited;
- pose source and seat transform;
- parenting and constraint policy;
- weapon and free-aim policy;
- camera policy;
- seat-switch transaction;
- exit and high-speed ejection policy;
- cleanup when seat, parent, vehicle, player, or adapter disappears.

Core fake code will not contain vendor-specific vehicle behavior.

## Recovery boundary

Recovery will become a dedicated character transition. It will not depend on ordinary `Player:Spawn()` applying correctly under a mutable global bypass flag.

State preservation must be registered by owner and tested for health, armor, organism, class, team, inventory, weapon, ammo, appearance, status effects, and mode state.

## Trauma disposition

- **Adopt:** generation semantics and transition diagnostics as requirements.
- **Adapt:** bounded camera, ragdoll combat, play-dead, and vehicle mechanics after separation.
- **Rewrite:** identity, authority transfer, recovery, networking, delayed work, prediction, and adapter integration.
- **Reject:** global transition flags, duplicated authorities, broad detours, and bundled vendor implementations.

## Consequences

### Positive

- stale timers and packets can be rejected deterministically;
- fake, organism, death, vehicle, weapon, and camera systems share one identity contract;
- entity removal can distinguish expected cleanup from gameplay-authoritative death;
- adapters become optional and bounded;
- diagnostics can show one current state and transition history.

### Costs

- broad compatibility mapping is required;
- fake, organism, movement, player-class, weapon, vehicle, networking, and camera code must migrate together at defined boundaries;
- runtime parity fixtures are mandatory before authority changes;
- legacy hooks and fields must be projected for an extended migration period.

## Acceptance criteria before implementation becomes authoritative

1. Current fake/get-up/death/vehicle behavior fixtures exist.
2. Player, organism, fake, movement, class, inventory, weapon, and vehicle ownership graphs are complete.
3. Every current delayed task and callback is assigned a lifecycle owner.
4. Packet and field compatibility projections are specified.
5. Rapid transition, packet reordering, disconnect, cleanup, refresh, and removal tests exist.
6. At least one stock vehicle and each supported optional vehicle adapter pass the same contract suite.
7. Rollback behavior is tested for failed ragdoll creation, missing physics objects, invalid bones, removed seats, and adapter loss.