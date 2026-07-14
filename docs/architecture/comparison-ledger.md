# Vanilla–Trauma Comparison Ledger

This ledger controls what enters the new project. It is decision-oriented rather than file-oriented. Trauma is evidence, not the baseline; see `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`.

## Decision states

| State | Meaning |
|---|---|
| Unreviewed | Attempt identified but not traced. |
| Keep Z-City | Current behavior remains preferred. |
| Adopt | Trauma's concept and implementation are suitable with minimal integration work. |
| Adapt | A bounded portion can be integrated behind project APIs. |
| Rewrite | The requirement is valid but the implementation should not be carried forward. |
| Reject | The attempt is unnecessary, harmful, or outside project scope. |
| Deferred | More behavioral evidence or prerequisite work is required. |

## Review requirements

Each resolved row must eventually link to:

- verified Z-City behavior documentation;
- current repository behavior;
- Trauma implementation evidence;
- observed defect or requirement;
- lifecycle and cleanup analysis;
- realm and networking analysis;
- performance implications;
- acceptance tests;
- an ADR when the decision is architecturally significant.

## Decision ledger

| Area | Trauma attempt | Decision | Reason / prerequisite |
|---|---|---|---|
| Boot/loading | Additional loaders, numeric filename ordering, deferred bootstrap, compatibility autoruns | Deferred | First boot map exists, but the complete autorun tree and hot-reload behavior still require runtime tracing. Multiple boot paths must not be copied. |
| Deterministic loading | Sort files/directories before inclusion | Adapt | Determinism is useful, but explicit dependency phases are preferable to relying on lexical filenames. |
| Mode registration | Global `MODE` capture plus V2 structured mode definitions | Rewrite | Keep explicit structured registration; remove ambient mutable capture for new modes and bridge legacy modes temporarily. |
| Mode lifecycle | Explicit activation, deactivation, generation, and diagnostics | Adapt | The lifecycle model is valid. Final APIs must use Z-City ownership scopes. See `sources/trauma-lifecycle-assessment.md`. |
| Hook ownership | Capture mode hooks and remove them on deactivation | Rewrite | Required capability, but Trauma's temporary replacement of global `hook.Add` is rejected. Use explicit owner APIs. |
| Timer ownership | Capture named timers and generation-guard simple timers | Rewrite | Required capability. Anonymous delayed work must receive cancellable owned IDs; global timer interception is rejected. |
| Generation guards | Ignore delayed callbacks from inactive mode generations | Adopt | Low-cost protection with clear semantics; integrate into owned tasks, death/spectator delays, packet sequencing, organism owner transfers, representation changes, weapon transactions, character admission, and asynchronous completions. |
| Persistent hooks | Hard-coded event allowlist remains global | Reject | Lifetime must be declared per resource, not inferred from event name. |
| Static registration capture | Loader captures registrations made by mode files | Deferred | May be useful as temporary migration/audit tooling, not as permanent runtime architecture. |
| Lifecycle diagnostics | Active mode, generation, hook and timer counts | Adapt | Expand with owner, source, realm, lifetime, replacement history, player/organism/representation/admission lifecycle phase, packet generation, and leak reporting. |
| Legacy mode dispatcher | Mode-table function names automatically become hook handlers | Keep Z-City temporarily | Preserve behavior until every mode method is classified. Replace only behind parity tests. |
| Active registries | Dense array plus reverse-position map and pruning | Adapt | Useful collection primitive. Encapsulate live storage, declare ordering semantics, and separate lifecycle ownership. |
| Self-tests | Shared/server/client command-driven diagnostics | Rewrite | Keep the concept but separate static audit, production health checks, smoke tests, behavioral tests, and performance tests. |
| Player lifecycle tracing | Additional lifecycle diagnostics and ownership tracking | Adapt | Add observational per-player phase tracing first. Do not replace spawn/death/spectator authority until parity tests pass. |
| Character admission | Expanded class, inventory, loadout, spawn, and lifecycle coordination | Rewrite | Current Z-City splits team, inventory, teleport, class, balancing, intermission, and equipment across multiple owners. Define one ordered server-authoritative admission transaction rather than porting another parallel coordinator. See `zcity/player-class-inventory-equipment-boundary.md`. |
| Character admission diagnostics | Per-player setup state, validation, and failure reporting | Adapt | Preserve bounded phase tracing, generation, plan/result records, and invariant checks without exposing private inventory or class data to unauthorized clients. |
| Player class definitions | Expanded data-driven class and organism customization | Deferred | The concept is useful, but current class schema, all publishers, mode overrides, movement effects, organism presets, appearance, and replication must be enumerated first. |
| Inventory construction | Expanded inventories, loadouts, items, and persistence | Deferred | `hg.CreateInv` is proven lifecycle-critical, but its definition, persistence, death/drop/disconnect behavior, and mode consumers remain unenumerated. |
| Equipment grant orchestration | Additional loadout/equipment systems and mode integrations | Rewrite | Preserve mode-owned outcomes and current order after balancing/intermission, but replace distributed direct grants with an explicit equipment plan committed by character admission/round reset. |
| Preserved-player reset | Additional lifecycle preservation and state transfer behavior | Rewrite | `DontKillPlayer` currently bypasses kill, respawn, and round-reset class application. Each mode requires fixtures before a unified preserved-player refresh contract can replace it. |
| Late-join synchronization | Expanded state synchronization across custom systems | Rewrite | Current synchronization is fragmented, while Trauma adds more channels. Define one versioned server-authoritative snapshot with ordered subsystem contributors and a completion contract. |
| Round snapshot | Multiple state and timing updates across channels | Rewrite | Replace fragmented mode/state/timing delivery with one sequenced snapshot. Preserve `RoundInfo` and `updtime` as compatibility projections until clients and modes migrate. |
| Packet metadata | Broader schema and ownership concepts across Trauma networking | Adapt | Adopt explicit owner, direction, schema version, rate policy, authority, and generation metadata; do not port Trauma's network surface wholesale. |
| Client request validation | Numerous custom receivers with local validation patterns | Rewrite | Centralize bounded enums, rate controls, expected-state checks, permission checks, payload limits, and rejection diagnostics. |
| Spectator state replication | Additional spectator and custom-system synchronization | Rewrite | Current Z-City already duplicates target/view state across messages and NWVars. Select one authority and expose compatibility projections. |
| Network proliferation | Additional subsystem-specific messages to patch synchronization gaps | Reject | New channels must not substitute for a coherent snapshot, ownership registry, or stable subsystem contract. |
| Round reset | Additional lifecycle hooks and reset integrations | Rewrite | Current `KillPlayers` is already a broad transaction. Replace only with an ordered coordinator that preserves `DontKillPlayer`, organism, fake-up, class, balance, and equipment semantics. |
| Death delayed work | Generation-wrapped `timer.Simple` callbacks | Rewrite | Generation guards are useful, but delayed tasks must be named internally, cancellable, attributable, and released on disconnect/transition. |
| Spectator admission | Additional mode and UI integrations | Keep Z-City temporarily | Current behavior must remain while hard-coded team restoration and client-request handling are documented and replaced behind mode authority. |
| Spawn contracts | Explicit team/FFA/solo topology and validation | Deferred | Core Z-City selection and fallback behavior is documented in `zcity/player-lifecycle.md`; every stock mode's return shape and runtime behavior still require mapping. |
| Spawn validation cache | Cache valid and invalid spawn clusters by map/mode/count | Rewrite | Cache key lacks configuration/implementation/validation versions; invalid results can become stale. |
| Spawn candidate metadata | Named groups, topology, and validation reporting | Adapt | Preserve candidate source, policy, validation reasons, reservation state, and fallback reason without adopting Trauma's full framework. |
| Organism schema | Expanded fields, module conventions, health UI, custom-mode extensions | Rewrite | Z-City already has a large implicit schema duplicated across reset, simulation, networking, and clients. Introduce one typed field registry; do not adopt another parallel schema. |
| Organism ownership | Additional organism adapters, transfer handling, fake/death integration | Rewrite | Shared-table compatibility must remain initially, but player/fake/death/NPC transfers require explicit identity and owner-generation tokens. Broad detours are rejected. |
| Physiology modules | Expanded medical, narcotic, infection, temperature, and status modules | Adapt | Evaluate each module independently behind deterministic phases and registered read/write fields. Preserve only evidence-backed mechanics. |
| Organism damage context | Additional damage detours and compatibility patches | Rewrite | Replace global penetration overrides and ambient inflictor fields with one per-event context. Separate geometry, mutation, effects, and replication while preserving outcomes through fixtures. |
| Organism replication | Large snapshots, partial tables, additional health packets and delta concepts | Rewrite | Adopt schema/version/delta requirements, but replace whole-table serialization and overlapping NetVar/packet authority with explicit visibility sets and owner generations. |
| Organism diagnostics | Self-tests, statistics, inspection, and health visibility | Adapt | Keep bounded server health, admin inspection, bandwidth, phase-order, stale-owner, and invalid-state diagnostics. Do not expose private physiology by default. |
| Medical/health presentation | Large HUD, inspection, texts, screen effects, and interactions | Adapt | Salvage mechanics and data-driven presentation selectively. Reject monolithic UI that combines server state, networking, interaction, rendering, and prose generation. |
| Whole-table developer replication | Send complete organism state in developer mode | Reject | Developer convenience does not justify serializing arbitrary entities/tables or bypassing field visibility and schema limits. |
| Organism compatibility surface | Current hooks, field names, table sharing, damage outcomes, and packet names | Keep Z-City temporarily | Preserve until fake-ragdoll, movement, class, item, packet, and injury fixtures establish a compatible migration boundary. |
| Fake-ragdoll identity | Extended fake, recovery, death conversion, play-dead, vehicle, and rendering behavior | Rewrite | Current identity has multiple writable authorities and no generation. Replace with the explicit representation state in ADR-0003 while preserving compatibility projections and gameplay fixtures. |
| Fake-ragdoll mechanics | Camera, ragdoll combat, play-dead, vehicle, and presentation improvements | Adapt | Evaluate each mechanic behind bounded representation, camera, weapon, and vehicle policies. Do not port overlapping replacement paths. |
| Fake-ragdoll delayed work | Timers and callbacks across fake, get-up, death, collision, fire, and vehicles | Rewrite | Bind every task to player, round, and representation generations with cancellation and attribution. |
| Vehicle/fake integration | Direct vehicle parenting, constraints, seat switching, camera, weapon, and ejection behavior | Rewrite | Use one optional vehicle capability adapter. Core fake and weapon behavior must remain valid when Glide or another provider is absent. |
| Bots | Bot driver, behavior arbitration, survival, rescue, squads, mode-specific bots | Deferred | Treat as a separate architecture after player/mode/spawn/weapon contracts are stable. Existing behavior reports show major defects. |
| Networking | Hundreds of declarations, receivers, and sends across realms | Rewrite | Core round/spectator, organism, and fake authority risks are documented; the full addon registry, duplicate-name resolution, visibility model, and trust-boundary audit remain required. |
| Optional adapters | Glide, VJ Base, DynaBase, vFire, Pathowogen and others | Rewrite | Adapters must be capability-detected, inert when absent, isolated from vendored code, and tested independently. |
| Bundled vendor systems | Large portions of Glide, DynaBase, vFire and related content included in project | Reject as default architecture | Prefer external dependencies or isolated vendor packages. Project adapters must not be mixed with vendor internals. |
| Minimap | Bake, sync, client map, and relation hooks | Unreviewed | Requires separate stability and value assessment. |
| Onboarding | Structured intro, input icons, keybind and rich-text systems | Adapt | Good concept if data-driven and generated from verified mechanics/settings. |
| Map tools | Map points, traitor controls, validation and map checks | Adapt | Useful, but schemas, authority, permissions, migration, and cache invalidation need formal definitions. |
| Weapon balance | Runtime schema/editor/application layer | Rewrite | Retain immutable authored definitions, validated versioned override layers, per-instance resolution, rollback, server authority, and diagnostics. Reject irreversible shared SWEP-table mutation. See `sources/trauma-weapon-combat-assessment.md`. |
| Weapon obstruction | Muzzle/barrel and side-obstruction logic | Deferred | Requires exact mapping of fire origin, ADS, hip fire, low/high ready, sprint, vehicles, fake combat, bots, and presentation origins before any trace replacement. |
| Fake-ragdoll weapon ownership | Additional ragdoll combat and weapon handling | Rewrite | Attach weapon ownership and delayed actions to the authoritative character representation generation. The fake system must not become a second weapon authority. |
| Vehicle weapon integration | Vehicle aiming, camera, seated weapons, free aim, and fire behavior | Rewrite | Place eligibility, pose, aim, muzzle, obstruction, camera, fire, seat, exit, and ejection behind the vehicle adapter boundary. |
| Physical bullets/projectiles | Expanded physical bullet and projectile behavior | Deferred | Map current damage dispatch, organism penetration, prediction, lag compensation, effects, networking, and cleanup first. Future work must use event-scoped damage context. |
| Explosion manager | Central explosive/shrapnel processing | Deferred | Potentially valuable, but it must not become a second damage authority or bypass projectile, entity, and organism contracts. |
| Bot/NPC weapon behavior | Bot aiming, muzzle, obstruction, fire, reload, and mode integration | Deferred | Define the shared player weapon capability contract first; bot-specific paths must be explicit adapters rather than silent forks. |
| Weapon networking | Additional weapon/editor/projectile messages | Rewrite | Require owner, direction, schema version, permission, holder/representation generation, rate policy, payload limits, and stale-update rejection. |
| Client performance | Shared performance registry, budgets, effect toggles | Adapt | Keep truthful user/server controls; avoid a single toggle masking correctness bugs. Measure before enabling dynamic degradation. |
| Content loading | Configurable Workshop loading | Rewrite | Current repository ConVar controls a block with commented resource calls. Replace with a truthful manifest and dependency report. |
| Administration | Expanded context properties, possession, scaling, medical and NPC tools | Deferred | Inventory permissions and server authority before porting. Every action requires explicit access and validation. |

## Verified source documents

- `zcity/boot-and-loading.md`
- `zcity/mode-and-round-lifecycle.md`
- `zcity/player-lifecycle.md`
- `zcity/player-class-inventory-equipment-boundary.md`
- `zcity/round-and-spectator-networking.md`
- `zcity/organism-lifecycle-and-damage.md`
- `zcity/fake-ragdoll-lifecycle.md`
- `zcity/weapon-and-combat-interfaces.md`
- `zcity/verified-defects.md`
- `sources/trauma-inventory.md`
- `sources/trauma-lifecycle-assessment.md`
- `sources/trauma-weapon-combat-assessment.md`
- `../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`
- `../decisions/ADR-0003-EXPLICIT_CHARACTER_REPRESENTATION_STATE.md`

## Behavioral spine required before gameplay ports

No gameplay subsystem will be ported until these flows are documented and assigned acceptance tests:

1. addon boot and load order;
2. gamemode selection and round lifecycle;
3. player initial spawn, spawn, death, fake death, spectating, respawn, class, inventory, and equipment;
4. organism initialization, damage, clearing, incapacitation, and death;
5. weapon deployment, aiming, obstruction, firing, and damage dispatch;
6. map cleanup, shutdown, and hot-reload behavior.

Core organism ownership, reset, simulation, damage, incapacitation, death, and replication are mapped. Item 4 still requires exhaustive medical-item consumers, packet/NetVar consumers, runtime phase/load-order evidence, and combined fake-ragdoll/movement/class integration tests.

The ordinary player lifecycle, round/spectator network contracts, core fake-ragdoll representation lifecycle, and top-level class/inventory/equipment orchestration boundary are mapped. Item 3 still requires exact `CreateInv` and `SetPlayerClass` definitions/consumers, every mode-specific lifecycle branch, movement integration, replication, cleanup, and runtime transition fixtures.

Weapon-related Trauma concepts now have a preliminary bounded disposition, but item 5 remains blocked on exact current-Z-City source enumeration. No weapon implementation is accepted from Trauma before that graph exists.

These flows form the compatibility spine. Higher-level ports before them would reproduce Trauma's layering problems.
