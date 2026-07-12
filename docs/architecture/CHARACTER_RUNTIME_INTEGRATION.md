# Character Runtime Integration Graph

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** organism/fake/movement/class ownership graph verified; weapon, inventory, appearance, armor, NPC and vehicle boundaries remain partial  
**Reviewed:** 2026-07-12

## Purpose

This document is the cross-system authority map for the player-character runtime. It connects four systems that cannot be safely refactored independently:

1. organism/physiology;
2. fake-ragdoll/physical body;
3. ordinary movement/prediction;
4. player-class definition/runtime.

The current implementation has no single character-runtime owner. State is distributed across the player entity, one mutable organism table, one or more ragdolls, shared class-definition tables, movement fields, NWVars, custom network packets, modes, weapons, inventory, appearance, armor, vehicles and global hooks.

## High-level graph

```text
Round / Mode
  ├─ assigns team, role, class, appearance, inventory, armor, equipment
  ├─ mutates organism extensions and movement state
  └─ controls spawn/reset/death/winner lifecycle

Player Class
  ├─ On / Off / Think / Damage / Guilt / Spawn
  ├─ model, bodygroups, identity, NPC faction, loadout, armor
  ├─ organism and movement modifiers
  └─ can force FakeUp / transformation

Input + SetupMove
  ├─ buttons, view, weapon stance, carried mass
  ├─ class fields + NW multipliers
  ├─ organism limbs/pain/blood/O2/stamina/consciousness
  ├─ ordinary movement, jump, slip, dive
  └─ may trigger fake/light-stun

Damage / Collision
  ├─ redirects player damage to fake body when active
  ├─ custom OBB organ/bone/artery damage
  ├─ wounds, pain, blood, O2, brain/spine/limbs
  ├─ class Damage + project hooks
  └─ unconsciousness, fake, amputation or death

Organism Think (~10 Hz)
  ├─ stamina -> lungs -> liver -> blood -> pain
  ├─ metabolism -> random events -> pulse
  ├─ class Think (currently shared-table throttled)
  ├─ virus / brain-spasm / external hooks
  ├─ needfake / needotrub / movement ability / life
  └─ owner/PVS snapshots

Fake-Ragdoll Controller (per frame while active)
  ├─ body physics, pose, crawl, grab, use, choke, weapon action
  ├─ organism power, limbs, pain, blood, O2, stamina
  ├─ class/faction/assimilation behavior
  ├─ hidden player position and camera/render ownership
  └─ get-up / death / vehicle transition
```

## Runtime authority matrix

| State/operation | Current primary writer | Additional writers/consumers | Authority problem |
|---|---|---|---|
| Class ID | server `SetPlayerClass`; also unauthenticated `playerclass` C -> S receiver | modes, death reset, client message | client can request arbitrary class; server/client data differ |
| Appearance/model | class `On`, mode setup, appearance system | fake creation/render, ragdoll model, armor/UI | no transaction or one owner; class exit rarely restores |
| Equipment/inventory/armor | mode and class functions | round reset, weapons, fake body render, organism weight | duplicate grants and incomplete cleanup |
| Organism table | Tier 0/Tier 1 server | damage, modules, modes, classes, items, fake/body | implicit schema and shared mutable aliases |
| Organism owner | Tier 0 transfer/fake/death paths | player, fake body, death body, client copies | no generation token; delayed callbacks can target stale owner |
| Standing movement | shared `SetupMove` | organism stamina, class modifiers, weapons, mode hooks | server/client prediction uses realm-local mutable state |
| Physical-body movement | fake server Think | player input, organism, class, weapons, constraints | no fixed budget/controller token; overlaps standing movement state |
| Fake/death body | fake server lifecycle | organism, damage, camera/render, NPCs, vehicles | server fields + NWEntities + packet + proxies overlap |
| Unconscious/fake decision | organism core and hooks | damage, modes, class, brain/spasm | order-dependent writes to `needfake`, `needotrub`, `fake`, `otrub` |
| Get-up | `hg.FakeUp` | organism gates, fake hooks, spawn/round/class | respawns player; global override and partial restore |
| Death body | fake death hooks | organism transfer, wounds, camera/spectator | custom body suppresses engine ragdoll; disconnect path inconsistent |
| Client physiology | `organism_send` | NetVars, partial packets, fake aliases | unversioned overlapping transport |
| Client fake state | NWEntity proxies primarily | `Player Ragdoll` packet/index, entity creation | no sequence/generation; undefined `ReadEntity2` dependency |
| NPC faction | class entry/exit and per-player hooks | modes, NPC systems, bullseye | repeated global scans and stale relationships/hooks |

## Lifecycle sequences

### Initial join/spawn

```text
PlayerInitialSpawn
  -> organism Add/Clear (delayed)
  -> round/mode synchronization
  -> class/mode assignment
  -> appearance/equipment/armor/inventory
  -> ordinary spawn/movement
```

Risks:

- multiple delayed handlers and no one readiness barrier;
- class can run before expected organism/inventory/appearance state;
- first-player round logic can create/remove a temporary bot and end a round;
- client class/organism/fake state arrives through separate channels.

### Class assignment

```text
SetPlayerClass
  -> old Off
  -> write class ID/NetVar
  -> broadcast class + table
  -> new On(raw server args)
  -> reset movement NW multipliers
  -> PlayerClass hook
```

Risks:

- unauthorized client transition;
- nil/table realm mismatch;
- no rollback;
- movement multipliers clobbered after On;
- organism/fake/equipment/NPC mutations partly persist after exit.

### Standing movement command

```text
SetupMove (server + client)
  -> organism/class/weapon/mass/state modifiers
  -> speed/inertia/jump/input rewrite
  -> slip/dive/fake transitions
  -> animation/footstep state
FinishMove / organism stamina feedback
```

Risks:

- realm-local time and stale client physiology;
- prediction-replayed mutable fields;
- multiple multiplier mechanisms and hook ordering;
- ordinary and fake controller ownership inferred rather than explicit.

### Injury to unconscious fake

```text
EntityTakeDamage / collision
  -> fake-body redirection when active
  -> custom organ/bone/wound mutation
  -> class Damage / project hooks
  -> organism tick computes consciousness/mobility
  -> needotrub / needfake
  -> hg.Fake creates physical body
  -> client NW proxy/camera/render transition
```

Risks:

- damage and tick ordering;
- owner transfer during delayed effects;
- packet/NW entity timing;
- partial body creation;
- duplicated movement/damage state.

### Active fake control

```text
server Think/Fake every frame
  -> read player input/view
  -> read organism limbs/pain/O2/blood/consciousness/stamina
  -> read class/weapon state
  -> control ragdoll physics/constraints
  -> mutate organism stamina/pain/choking/assimilation
  -> reposition hidden player
```

Risks:

- frame-rate coupling and global cost;
- model/physics/weapon assumptions;
- direct class logic embedded in generic control;
- no stable body generation for delayed callbacks.

### Get-up

```text
FakeUp
  -> Should Fake Up hooks + velocity/stun/space checks
  -> save health/armor/weapon/view
  -> global + network OverrideSpawn
  -> Spawn player
  -> restore selected fields/position/velocity
  -> clear fake refs/NW state
  -> remove old body later
  -> restore collision/render/movement
```

Risks:

- every spawn hook participates;
- no finally block for global override;
- class/mode/inventory/organism state can reset during Spawn;
- packet/NW/proxy/old-body state can disagree;
- delayed cleanup can use disconnected/reused player index.

### Death/disconnect

```text
DoPlayerDeath
  -> reuse/create custom body
  -> mark RagdollDeath + wounds
  -> organism death/owner state
  -> client camera/render/death state
PostPlayerDeath
  -> remove engine body and clear fake lookup
```

Disconnect adds a separate organism-copy/clear path with API-shape mismatches. Round/mode cleanup and map cleanup add more removal paths.

## Hook and scheduling graph

| Cadence/event | Systems executed | Ordering concern |
|---|---|---|
| server global Think, ~10 Hz | organism registry and every `Org Think` callback | core physiology and extension hook registration order |
| server Think, every frame | fake active-body control | frame cost, mutation before/after organism ticks |
| shared SetupMove, every command | ordinary movement and custom movement stages | server/client prediction/order divergence |
| FinishMove | stamina feedback | can use movement result after prediction changes |
| EntityTakeDamage | organism/custom damage + class Damage/project hooks | reentrancy and fake redirection |
| PlayerSpawn / project spawn | round, class, organism, fake override, appearance/equipment | duplicate names and override semantics |
| PlayerDeath/PostPlayerDeath | class reset, organism death, custom ragdoll | ordering changes body/state preservation |
| class On/Off | appearance, equipment, organism, movement, NPC hooks | no transaction and often incomplete Off |
| NWVar/entity replication | fake/client ownership | asynchronous relative to custom packet/entity creation |

Runtime instrumentation is required to record actual order, duration and return values for these shared hooks.

## Shared fields without one schema

### Player fields

Examples include:

- `PlayerClassName`, `subClass`, `leader`, role/team fields;
- `FakeRagdoll`, old/death ragdoll references, fake timers and view mode;
- movement speed/history/jump/crouch/carry fields;
- class movement multipliers and sound/gesture state;
- inventory/armor/appearance/active weapon state;
- organism pointer and additional mode/class extension fields.

### Ragdoll fields

Examples include owner player, organism alias, bullseye, physics/control state, constraints/welds, vehicle parent, fire state, weapons/render state, wounds and death/fake flags.

### Organism fields

Canonical physiology plus arbitrary mode/class/item extensions such as HEV, superfighter, assimilation, recoil and control flags.

### Shared class-definition fields

Methods, capabilities, movement multipliers and incorrectly shared runtime throttle (`nextThink`).

No code-generated schema validates these cross-system assumptions.

## Highest-impact current defects

1. **Arbitrary client class assignment** through `playerclass` C -> S.
2. **No body/organism ownership generation**, allowing stale callbacks and transport races.
3. **Respawn-based get-up** with global spawn override and partial state restoration.
4. **Shared class Think throttle**, starving same-class players.
5. **Prediction-unsafe movement context**, using realm-local timing/stale mutable state.
6. **Order-dependent organism modules/hooks**, with multiple writers for consciousness/fake/death state.
7. **Overlapping fake transport**, including undefined `net.ReadEntity2` behavior.
8. **No transactional class/fake transitions**, leaving partial side effects after errors.
9. **Permanent class/global hooks**, dynamic NPC hooks and relationship scans outside lifecycle ownership.
10. **Per-frame active-ragdoll cost** plus 10 Hz physiology and per-command movement with no unified budget.
11. **Hard-coded ValveBiped model profile** shared by damage, fake control and render.
12. **Duplicated equipment/appearance/armor ownership** across round, mode and class.
13. **Implicit extension fields and inconsistent cleanup** across class/mode transitions.
14. **Multiple hook naming conventions**, including spaced/unspaced fake/spawn/get-up events.

## Required cross-system validation harness

### State tracing

For every player, log a stable lifecycle generation and:

- class ID/data;
- organism table ID, owner and ownerX;
- current/old/death ragdoll IDs;
- ordinary/fake controller ownership;
- mode/team/role;
- spawn/death/get-up transition;
- client packet/NW proxy arrival sequence.

### Transition matrix

Test every combination of:

- spawn, class change, mode change and equipment assignment;
- standing, sprinting, crouching, jumping, carrying and vehicle state;
- damage, unconsciousness, voluntary fake and forced fake;
- active fake combat, death, get-up and disconnect;
- latency, packet loss, entity dormancy, hotload and map cleanup.

### Invariant assertions

- exactly one authoritative body generation;
- exactly one authoritative organism owner;
- class runtime state is per player, not shared definition data;
- ordinary and fake controllers are not simultaneously authoritative;
- server/client class and body IDs converge;
- global spawn override is false outside an active transaction;
- dynamic hooks/timers/constraints are removed after owner/class/body exit;
- no state mutation occurs from stale generation callbacks.

### Performance budgets

Measure separately and combined:

- SetupMove/animation/footstep cost;
- organism 10 Hz simulation and snapshot cost;
- fake per-frame physics/control/PVS cost;
- class NPC scans/hooks/presentation cost;
- damage geometry and effect cost.

## Planned architectural boundaries

These are `Planned`, not implemented changes.

### `CharacterRuntime`

Per-player lifecycle owner containing stable generation, mode/team/role/class/body state and transition transactions.

### `PhysiologyState`

Explicit schema, deterministic module phases, registered extensions and versioned public/private replication.

### `PhysicalBodyController`

State machine for standing/fake/unconscious/getting-up/dead; body creation/ownership/vehicle adapter and fixed-budget control.

### `MovementContext`

Prediction-safe input snapshot and ordered modifier pipeline for organism, class, weapon, mode, carried mass and stance.

### `ClassDefinition` + `ClassRuntime`

Immutable server-owned definitions plus per-player runtime state, bounded transition data and lifecycle-owned hooks/resources.

### Adapters

Explicit appearance, equipment/inventory, armor, weapon, NPC faction, vehicle and presentation interfaces rather than direct cross-system mutation.

## Dependency-safe research/migration order

1. Complete weapon, inventory, appearance, armor, NPC and vehicle consumer maps.
2. Add read-only lifecycle/hook/performance instrumentation and invariant checks.
3. Lock or remove unauthorized class transport before public release.
4. Define canonical schemas and ownership generation without changing behavior.
5. Separate per-player class runtime from shared definitions.
6. Introduce movement context/modifier diagnostics.
7. Introduce physical-body transition transaction/generation adapter.
8. Version organism/fake/class transport.
9. Migrate concrete classes, modes, weapons and vehicles through compatibility adapters.
10. Remove legacy globals/hooks/packets only after regression evidence.

## Next trace

1. Trace weapons consumed by movement/fake/organism, including ragdoll callbacks and physical bullets.
2. Trace inventory/equipment/appearance/armor ownership used by class and round transitions.
3. Trace NPC/bot organism, faction and fake-body consumers.
4. Refine this graph into implementation-ready work packages only after those boundaries are complete.
