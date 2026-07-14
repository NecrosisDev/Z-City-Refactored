# Trauma Source Inventory

**Status:** Initial structural inventory with selected semantic review. Counts are static observations and require realm-aware runtime verification.

## Snapshot identity

| Field | Value |
|---|---|
| Source | `Trauma.zip` |
| SHA-256 | `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652` |
| Archive size | 4,425,563 bytes |
| Extracted root | `TMod` |
| Lua files | 1,028 |
| Lua source size | approximately 8.62 MB |

Machine-readable metrics are stored in `../data/trauma-snapshot-2026-07-14.json`.

## Static registration surface

| Metric | Count |
|---|---:|
| `hook.Add` calls | 1,150 |
| `timer.Create` calls | 90 |
| `timer.Simple` calls | 546 |
| `util.AddNetworkString` calls | 327 |
| `net.Receive` calls | 340 |
| `net.Start` calls | 465 |
| `CreateConVar` calls | 236 |
| `CreateClientConVar` calls | 119 |
| `concommand.Add` calls | 200 |
| `file.Write` calls | 42 |

These counts include inherited Z-City code, bundled third-party code, experimental replacements, comments/dead paths, and overlapping implementations. They measure review surface, not feature count.

## Literal duplicate groups

Static literal-name analysis found:

| Type | Duplicate groups |
|---|---:|
| Network-string declarations | 5 |
| Network receivers | 30 |
| Hook event/identifier pairs | 9 |
| ConVars | 30 |
| Named timers | 4 |

Duplicate network declarations include:

- `defense_commander_notification`;
- `projectileFarSound`;
- `select_mode`;
- `send_tourniquets`;
- `updtime`.

Duplicates are not automatically defects. Shared files may intentionally define opposite-realm receivers, and ConVars may be retrieved through create-if-missing patterns. Each group requires realm, load-order, and replacement analysis.

## Major implementation areas

### Shared addon systems

The `lua/homigrad` tree includes:

- achievements;
- administration and context tools;
- bot driving and behavior arbitration;
- clothes and appearance;
- combatant and NPC relation abstractions;
- dynamic animation utilities;
- multiple music systems;
- explosives and an explosion manager;
- fake-ragdoll, vehicle, play-dead, and rendering changes;
- HUD and health inspection;
- inventory;
- movement;
- organism, medical, narcotic, infection, and Pathowogen behavior;
- physical bullets;
- player classes;
- postmortem systems;
- self-tests and performance reporting;
- VJ Base support;
- chat, manipulation, and zombie systems.

### Gamemode systems

`gamemodes/trauma/gamemode` includes:

- legacy libraries and round systems;
- a mode lifecycle manager;
- custom gamemode V1/V2 infrastructure;
- schemas, storage, networking, editors, abilities, and stock-mode adapters;
- experience and guilt systems;
- map points and map tooling;
- minimap;
- onboarding;
- RTV;
- spawn contracts and validation;
- weapon-balance schemas and editors;
- many stock and experimental modes.

### External integrations and bundled systems

The archive includes substantial optional/vendor material:

- Glide base entities, vehicle entities, effects, tools, weapons, and multiple adapters;
- vFire entities/effects/management;
- wOS DynaBase source and loaders;
- focused VJ Base integration files;
- Pathowogen-facing code;
- compatibility autoruns and direct vendor modifications.

Every file in these areas must be classified as one of:

1. original project code;
2. copied third-party code;
3. compatibility adapter;
4. direct vendor modification;
5. project feature incorrectly coupled to a vendor system.

Bundled optional systems are not accepted as the future dependency strategy.

## Attempt groups

### 1. Identity and bootstrap

Trauma attempts to add explicit project identity, logging, Workshop delivery, deferred loading, and compatibility patches.

Preliminary disposition:

- project metadata: adapt;
- compatibility aliases: retain temporarily;
- multiple bootstraps and numeric autorun ordering: reject as final design;
- deferred/post-entity concepts: rewrite after hot-reload documentation;
- Workshop list: replace with a truthful manifest.

### 2. Deterministic loading

Trauma explicitly sorts some file/folder discovery.

Benefit: removes some dependence on unspecified `file.Find` ordering.

Remaining problem: lexical prefixes still substitute for declared dependencies, and side-effect registration remains the load model.

Disposition: adapt, then replace with phased manifests.

### 3. Mode lifecycle ownership

Trauma captures hooks/timers during mode loading and callback execution, activates registrations for the current mode, removes them on transition, and guards callbacks with a generation counter.

The goal is valid. Temporary replacement of global `hook.Add`, `timer.Create`, and `timer.Simple` is rejected.

Detailed decision: `trauma-lifecycle-assessment.md`.

### 4. Custom gamemode framework

Trauma's `customgm` system attempts:

- data-driven modes;
- reusable modules;
- runtime-editable configuration;
- validation and sanitation;
- storage and submission workflows;
- class, role, organism, ability, and stock-mode adapters;
- separation between authored definitions and active round state.

Risks:

- V1 and V2 overlap;
- a second framework wraps the legacy framework instead of replacing it cleanly;
- adapters duplicate intimate stock-mode knowledge;
- storage, validation, runtime mutation, UI, and networking are tightly coupled;
- canonical source hash checks depend on exact upstream revisions;
- behavior origin becomes difficult to trace.

Disposition: rewrite from extracted requirements after stock modes are documented.

### 5. Round lookup optimization

Trauma attempts to cache changelevel detection and mode alias resolution.

Disposition:

- event-driven changelevel cache: adapt;
- pure mode-resolution cache: adopt after invalidation tests;
- lifecycle activation from a getter such as `CurrentRound()`: reject.

### 6. Spawn contracts and validation

Trauma introduces explicit team/FFA/solo contracts, named groups, nav requirements, safety checks, LOS-based opposing clusters, and persisted cache results.

The concept is useful, but current behavior can fail open, reject previously playable maps, produce random validation results, and retain stale invalid caches.

Disposition: rewrite after complete Z-City spawn documentation.

### 7. Organism, medical, and health UI

Trauma expands medical state, wounds, narcotics, infection, role behavior, screen effects, status text, inspection, and networking.

The concepts must be inventoried individually. Monolithic UI/network/interaction files and broad detours are not accepted as architecture.

Disposition: deferred until the vanilla organism and damage pipeline is documented.

### 8. Bots and NPCs

Trauma contains a large bot driver, behavior modules, mode bot files, debug tools, population management, NPC relations, a combatant abstraction, and VJ Base integration. A global bot-disabling autorun is also present.

This indicates unresolved overlap between replacement and legacy bot systems.

Disposition: deferred; do not port the global disable path or broad detours.

### 9. Optional adapters

- Glide: multiple adapters plus bundled source — reject bundling; design one optional adapter.
- VJ Base: review focused files individually behind one capability boundary.
- DynaBase/wOS: optional adapter only; core startup remains independent.
- vFire: optional fire capability interface; reject vendor bundling.
- Pathowogen: treat as an optional mode/content integration, not a required base.

### 10. Self-testing and observability

Trauma adds shared/client/server self-tests and performance reporting.

Valid goals:

- dependency availability;
- registration/content checks;
- runtime health;
- smoke-test automation;
- performance evidence.

Risk: broad passing counts can certify registration while gameplay remains broken.

Disposition: rewrite into separate static audits, production health checks, smoke tests, behavioral acceptance tests, and benchmarks.

## Lifecycle dialects

The snapshot uses multiple similarly named lifecycle events, including variants of:

- `PlayerSpawn`;
- `Player Spawn`;
- `PlayerDeath`;
- `Player_Death`;
- `Org Think`;
- `Org Clear`;
- `ZB_PreRoundStart`;
- `ZB_RoundStart`;
- `RoundStateChange`.

Some are intentional internal events. Others may be compatibility aliases or duplicate pathways. They must be traced by producer and consumer before consolidation.

## Cross-cutting risks

1. Multiple loaders initialize overlapping code.
2. Filename ordering substitutes for declared dependencies.
3. Legacy and replacement systems remain active together.
4. Global API interception infers ownership incorrectly.
5. Cleanup is incomplete across mode changes, map cleanup, refresh, disconnect, and shutdown.
6. Client delivery may expose unnecessary implementation.
7. Network receivers lack a central schema, direction, permission, and rate registry.
8. Optional dependencies become effectively mandatory through bundling.
9. Self-tests may validate structure rather than behavior.
10. Compatibility guards can suppress errors while preserving invalid state.
11. Runtime mutation makes it difficult to restore canonical definitions.
12. Prototype-specific public names risk becoming permanent API debt.

## Current overall disposition

| Category | Disposition |
|---|---|
| Explicit identity and capabilities | Adapt |
| Deterministic discovery | Adapt |
| Mode ownership | Rewrite |
| Generation guards | Adopt |
| Custom gamemode framework | Rewrite from requirements |
| Spawn framework | Deferred pending parity map |
| Medical expansion | Inventory individually |
| Bot/NPC expansion | Deferred pending foundation contracts |
| Bundled third-party addons | Reject |
| Optional adapters | Rewrite around capability boundaries |
| Self-tests | Rewrite under evidence taxonomy |

## Next analysis targets

1. Complete player spawn/death/fake/spectator/respawn mapping.
2. Enumerate direct hooks, timers, receivers, commands, and globals inside each stock mode.
3. Map organism initialization, damage, clear, incapacitation, and death.
4. Map weapon deploy, ADS, obstruction, firing, bullet, and damage dispatch.
5. Inventory network messages by owner, realm, payload, validation, and frequency.
6. Separate vendor code from adapters.
7. Extract CustomGM requirements without carrying its runtime implementation.
