# Trauma Attempt Inventory

## Status

This document inventories what the uploaded `Trauma.zip` attempts to add or change. It is not an endorsement of those implementations.

## Snapshot metrics

A static scan found:

| Item | Count |
|---|---:|
| Lua files | 1,028 |
| `hook.Add` calls | 1,150 |
| `hook.Remove` calls | 53 |
| `timer.Create` calls | 90 |
| `timer.Simple` calls | 546 |
| `timer.Remove` calls | 94 |
| `util.AddNetworkString` calls | 321 |
| Unique literal network declarations | 316 |
| `net.Receive` calls | 333 |
| Unique literal receivers | 303 |
| `net.Start` calls | 451 |
| Unique literal starts | 289 |
| ConVar creation calls | 351 |
| Unique literal ConVar names | 283 |
| Console command registrations | 200 |

These counts include legacy Z-City code, bundled third-party code, experimental systems, and overlapping implementations. They describe review surface rather than independent features.

## Major modification areas

### Core and gamemode systems

- Custom gamemode framework: 34 Lua files
- Organism-related files: 40
- Bot-related files: 40
- Spawn framework: 7
- Self-test framework: 4

### External integrations and bundled systems

- Glide-related Lua files: 115
- DynaBase/wOS files: 14
- VJ Base adapter files: 9
- vFire-related files: 5

The Glide count demonstrates a major architectural problem: Trauma does not merely adapt an optional dependency; it includes a broad vendor snapshot and multiple overlapping adapters.

## Duplicate literal network declarations

The archive declares these names more than once:

- `defense_commander_notification`
- `projectileFarSound`
- `select_mode`
- `send_tourniquets`
- `updtime`

Duplicate declarations are usually tolerated by Garry's Mod, but they obscure ownership and make protocol review more difficult.

# Attempt groups

## 1. Project identity and bootstrap

Trauma attempts to:

- Rename the project while retaining `hg` and `zb` compatibility.
- Add project identifiers and logging.
- Restore Workshop resource delivery.
- Add late handling for deferred `initpost` files.
- Guard `sv_` files more carefully in the addon loader.

### Initial decision

| Attempt | Decision |
|---|---|
| Explicit project metadata | Adapt |
| Preserve compatibility namespaces | Adopt concept |
| Late `initpost` fallback | Rewrite and test |
| Bundled Workshop dependency list | Reject as core behavior |
| Recursive addon loader | Keep temporarily; replace incrementally |

## 2. Deterministic load ordering

Trauma explicitly sorts files and folders in the gamemode loader.

### Benefit

This removes reliance on unspecified `file.Find` ordering.

### Remaining problems

- Numeric filename prefixes remain the de facto dependency mechanism.
- Child folders still load before parent files.
- Registration remains side-effect driven.
- A global temporary `MODE` table remains in use.

### Initial decision

**Adapt.** Explicit sorting is an immediate improvement. The mature design should use manifests and declared dependencies.

## 3. Mode lifecycle ownership

Trauma attempts to ensure that hooks and timers declared by inactive modes are not left globally active.

It uses two interception layers:

1. The mode loader temporarily replaces `hook.Add` and `timer.Create` while loading each mode.
2. `sh_mode_lifecycle.lua` temporarily replaces `hook.Add`, `timer.Create`, and `timer.Simple` while mode callbacks execute.

Captured registrations are stored by mode and activated or removed as the active mode changes. A generation counter suppresses delayed `timer.Simple` callbacks after mode deactivation.

### Valid goal

Vanilla mode files can register direct hooks and timers that remain active outside their intended mode. Explicit lifecycle ownership is required.

### Implementation risks

- Global functions are replaced during nested execution.
- Ownership is inferred instead of declared.
- Cached references to the original functions bypass tracking.
- Unrelated libraries called from a mode callback can be attributed to that mode.
- Reentrancy and nested mode calls are difficult to reason about.
- `timer.Simple` callbacks are suppressed rather than explicitly owned and cancelled.
- Restoration depends on every interception path remaining exception-safe.
- Persistent-event exceptions are maintained through a hard-coded allowlist.
- Runtime behavior can vary based on which call path happened to create a registration.

### Initial decision

**Rewrite.** Preserve lifecycle ownership as a requirement, but reject global interception. New systems must register through explicit owner/context APIs. Legacy direct registrations will be inventoried and migrated individually.

## 4. Custom gamemode framework

Trauma adds a substantial `customgm` subsystem containing:

- Schemas
- Abilities
- Reusable modules
- Runtime configuration
- Storage
- Network synchronization
- Submission workflows
- Class and role overrides
- Organism integration
- Editors and HUD
- V2 stock-mode adapters

### Valid goals

- Data-driven game modes
- Reusable mode modules
- Runtime-editable configuration
- Separation between authored definitions and active round state
- Compatibility with existing stock modes

### Risks

- It creates a second framework around the existing implicit framework.
- V1 and V2 concepts overlap.
- Per-mode adapters duplicate stock-mode knowledge.
- Storage, validation, networking, runtime mutation, editing, and compatibility are tightly coupled.
- Canonical-source hash checks and detours depend on exact upstream source revisions.
- It can obscure whether behavior originates from vanilla mode code, an adapter, or generated configuration.

### Initial decision

**Rewrite from requirements.** Preserve schema, validation, reusable-module, and editor goals. Do not port the runtime wholesale.

## 5. Round lookup and lifecycle optimization

Trauma attempts to cache:

- Presence of `trigger_changelevel`.
- Requested-to-main mode resolution.
- Revisions when modes or map state change.

### Valid goal

The current `CurrentRound()` repeatedly scans map entities for `trigger_changelevel`, despite being used in frequently executed paths.

### Risks

- Cache invalidation must cover map cleanup, entity creation/removal, Lua refresh, and mode re-registration.
- Some Trauma paths cause mode activation from round lookup, making a getter mutate lifecycle state.

### Initial decision

| Attempt | Decision |
|---|---|
| Event-driven changelevel cache | Adapt |
| Mode-resolution cache | Adopt with tests |
| Lifecycle activation inside `CurrentRound()` | Reject |

## 6. Spawn contracts and safety

Trauma adds:

- A shared spawn contract.
- Server spawn-safety checks.
- Spawn validation.
- Map-cleanup cache handling.
- Custom-gamemode integration.

### Valid goals

- Prevent blocked or dangerous spawns.
- Standardize team and random spawn policies.
- Cache expensive spatial checks.
- Provide a reusable spawn API.

### Initial decision

**Pending deep comparison.** Spawn behavior is gameplay-critical and must be documented mode by mode before adoption.

## 7. Organism, medical, narcotics, and health UI

Trauma substantially expands:

- Organism behavior and networking
- Medical actions
- Narcotics and drug interactions
- Wounds and limb information
- Inspection and assessment
- Role-specific health behavior
- Client screen effects and status text

At least one health HUD implementation is extremely large and combines server state, networking, menus, interactions, rendering, text generation, and inspection behavior.

### Initial decision

| Area | Decision |
|---|---|
| Medical and organism gameplay concepts | Inventory individually |
| Monolithic HUD architecture | Reject; salvage behavior selectively |
| Organism detours and compatibility patches | High-risk; compare lifecycle first |
| Delta networking concepts | Review separately |

## 8. Bots and NPCs

Trauma adds or changes:

- Bot-driver behavior modules
- Debugging and inspection tools
- Bot population management
- Mode-specific bot files
- Fear entities
- VJ Base organism, bleeding, corpse, relation, spawn, path, and knockdown integration
- A global bot-disabling autorun file

### Risks

- Debug, production, adapter, and replacement logic overlap.
- A global bot-disabling script indicates unresolved subsystem conflict.
- Mode-specific bot implementations duplicate behavior.
- VJ integration can alter damage, relationships, corpse ownership, path behavior, and spawning.

### Initial decision

**Rewrite after vanilla inventory.** Do not port global bot disabling or broad detours.

## 9. External integrations

### Glide

The archive contains multiple integration entry points, both `trauma_glide_adapter.lua` and `zcity_glide_adapter.lua`, shared integration files, entities, effects, tools, weapons, and vendor source.

**Decision:** Reject bundling. Replace with one optional capability-detected adapter.

### VJ Base

Nine focused files cover configuration, bleeding, corpses, factions, knockdown, organism behavior, path checks, relations, and spawning.

**Decision:** Review individually. Preserve useful concepts behind one optional adapter boundary.

### DynaBase / wOS

Trauma includes a loader and broad DynaBase source snapshot.

**Decision:** Optional adapter only. Core startup must remain independent.

### vFire

Trauma includes manager code, effects, and entities.

**Decision:** Reject vendor bundling. Define an optional fire capability interface.

## 10. Self-testing and observability

Trauma adds shared, client, server, and performance self-test files.

### Valid goals

- Verify dependency availability.
- Validate registrations and content.
- Expose runtime health.
- Detect obvious regressions without manual playtesting.

### Risks

- Tests can become implementation-shaped and pass while gameplay is broken.
- Runtime scanning can add unnecessary server cost.
- A broad self-test command is not a replacement for focused acceptance tests.

### Initial decision

**Adapt.** Keep a small boot-time/static validation layer and focused subsystem tests. Avoid permanent expensive scanning.

# Current overall disposition

| Category | Current disposition |
|---|---|
| Explicit identity and capability concepts | Adapt |
| Deterministic sorting | Adapt immediately |
| Mode ownership | Rewrite |
| Custom gamemode framework | Rewrite from requirements |
| Spawn framework | Pending vanilla comparison |
| Medical expansions | Inventory individually |
| Bot/NPC expansion | Rewrite after baseline mapping |
| Bundled third-party addons | Reject |
| Optional adapters | Rewrite around capability boundaries |
| Self-tests | Adapt selectively |

# Next inventory work

1. Enumerate every direct hook and timer declared inside vanilla mode folders.
2. Map each Trauma lifecycle capture against those declarations.
3. Document the complete vanilla round state machine.
4. Compare spawn and player reset behavior mode by mode.
5. Split Trauma's custom-gamemode requirements from its implementation.
6. Produce one decision record per accepted architectural concept.