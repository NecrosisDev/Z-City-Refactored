# Destination–Trauma Comparison Ledger

- **Status:** Normative concept-disposition ledger
- **Destination baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Current Trauma prototype:** `Trauma_Clean.zip` (`03d6b1b...`)
- **Source registry:** `source-baselines.md`

This ledger controls which Trauma-derived requirements or mechanics may enter the new project. It is decision-oriented rather than file-oriented. Trauma is evidence, not the baseline; see `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`.

Rows created from the historical Trauma archive retain their concept-level disposition, but exact paths and implementation claims must be revalidated against Trauma Clean before an implementation work package reaches **Ready**.

## Decision states

| State | Meaning |
|---|---|
| Unreviewed | Attempt identified but not traced. |
| Keep Z-City | Destination-baseline behavior remains preferred temporarily or permanently. |
| Adopt | Trauma's concept and implementation are suitable with minimal integration work. |
| Adapt | A bounded portion can be integrated behind project APIs. |
| Rewrite | The requirement is valid but the implementation should not be carried forward. |
| Reject | The attempt is unnecessary, harmful, or outside scope. |
| Deferred | More behavioral evidence or prerequisite work is required. |

## Review requirements

Each resolved row must eventually link to:

- exact source identities and paths;
- source-verified destination behavior;
- relevant later upstream vanilla delta;
- current Trauma Clean implementation evidence;
- observed defect or approved requirement;
- authority, lifecycle, cleanup, realm, and networking analysis;
- security and performance implications;
- stable requirement and acceptance-test IDs;
- rollout, rollback, and legacy-removal strategy;
- an ADR when the decision is architecturally significant;
- an approved work package before code migration.

## Decision ledger

| Area | Trauma attempt | Decision | Reason / prerequisite |
|---|---|---|---|
| Boot/loading | Additional loaders, numeric filename ordering, deferred bootstrap, dependency/restoration autoruns, compatibility patches | Deferred | The destination boot map exists, but the complete autorun tree, later upstream delta, partial failure, and hot-reload behavior still require runtime fixtures. Multiple boot paths must not be copied. |
| Deterministic loading | Sort files/directories before inclusion | Adapt | Determinism is useful, but explicit dependency phases are preferable to relying on lexical filenames. |
| Mode registration | Global `MODE` capture plus V2 structured mode definitions | Rewrite | Keep explicit structured registration; remove ambient mutable capture for new modes and bridge legacy modes temporarily. |
| Mode lifecycle | Explicit activation, deactivation, generation, and diagnostics | Adapt | The lifecycle requirement is valid. Final APIs must use project ownership scopes. See `sources/trauma-mode-lifecycle-comparison.md`. |
| Hook ownership | Capture mode hooks and remove them on deactivation | Rewrite | Required capability, but Trauma's temporary replacement of global `hook.Add` is rejected. Use explicit owner APIs. |
| Timer ownership | Capture named timers and generation-guard simple timers | Rewrite | Required capability. Anonymous delayed work must receive cancellable owned IDs; global timer interception is rejected. |
| Generation guards | Ignore delayed callbacks from inactive generations | Adopt | Integrate into owned tasks, death/spectator delays, packet sequencing, organism transfers, representation changes, weapon transactions, character admission, and asynchronous completions. |
| Persistent hooks | Hard-coded event allowlist remains global | Reject | Lifetime must be declared per resource, not inferred from event name. |
| Static registration capture | Loader observes registrations made by mode files | Adapt for migration audit only | Use offline/generated manifests to seed semantic review. Do not ship global interception as runtime architecture. |
| Lifecycle diagnostics | Active mode, generation, hook and timer counts | Adapt | Expand with owner, source, realm, lifetime, replacement history, lifecycle phase, packet generation, stale-work rejection, and leak reporting. |
| Legacy mode dispatcher | Mode-table function names automatically become hook handlers | Keep Z-City temporarily | Preserve behavior until every mode method is classified. Replace only behind parity tests. |
| Active registries | Dense array plus reverse-position map and pruning | Adapt | Useful collection primitive. Encapsulate storage, declare ordering semantics, and separate lifecycle ownership. |
| Self-tests | Shared/server/client command-driven diagnostics | Rewrite | Separate static audit, health checks, load smoke, parity, integration, fault, security, and performance tests. |
| Player lifecycle tracing | Additional lifecycle diagnostics and ownership tracking | Adapt | Add observational per-player phase tracing first. Do not replace spawn/death/spectator authority until parity tests pass. |
| Character admission | Expanded class, inventory, loadout, spawn, and lifecycle coordination | Rewrite | Destination Z-City splits team, inventory, teleport, class, balancing, intermission, and equipment across multiple owners. Define one ordered server-authoritative admission transaction rather than porting another parallel coordinator. See `zcity/player-class-inventory-equipment-boundary.md`. |
| Character admission diagnostics | Per-player setup state, validation, and failure reporting | Adapt | Preserve bounded phase tracing, generation, plan/result records, and invariant checks without exposing private data. |
| Player class definitions | Expanded data-driven class and organism customization | Deferred | Current class schema, publishers, mode overrides, movement effects, organism presets, appearance, and replication must be exhaustively enumerated first. |
| Inventory construction | Expanded inventories, loadouts, items, and persistence | Deferred | `hg.CreateInv` is lifecycle-critical, but its definition, persistence, death/drop/disconnect behavior, and mode consumers remain unenumerated. |
| Equipment grant orchestration | Additional loadout/equipment systems and mode integrations | Rewrite | Preserve mode-owned outcomes and current order after balancing/intermission, but replace distributed direct grants with an explicit equipment plan committed by admission/round reset. |
| Preserved-player reset | Additional lifecycle preservation and state transfer behavior | Rewrite | `DontKillPlayer` bypasses kill, respawn, and round-reset class application. Each mode requires fixtures before a unified refresh contract replaces it. |
| Late-join synchronization | Expanded synchronization across custom systems | Rewrite | Current synchronization is fragmented, while Trauma adds more channels. Define one versioned server-authoritative snapshot with ordered contributors and completion state under `zcity/network-contract-and-trust-boundaries.md`. |
| Round snapshot | Multiple state and timing updates across channels | Rewrite | Replace fragmented mode/state/timing delivery with one sequenced snapshot. Preserve `RoundInfo` and `updtime` as compatibility projections during migration. |
| Packet metadata | Broader schema and ownership concepts across Trauma networking | Adapt | Adopt owner, direction, schema version, rate policy, authority, visibility, lifetime, and generation metadata through the central endpoint registry; do not port Trauma's network surface wholesale. See `zcity/network-contract-and-trust-boundaries.md`. |
| Client request validation | Numerous custom receivers with local validation patterns | Rewrite | Centralize bounded enums, rate controls, expected-state checks, permission checks, payload limits, work limits, and rejection diagnostics. |
| Spectator state replication | Additional spectator and custom-system synchronization | Rewrite | Destination Z-City already duplicates target/view state across packets and NWVars. Select one authority and expose compatibility projections. |
| Network proliferation | Additional subsystem messages to patch synchronization gaps | Reject | New channels must not substitute for a coherent snapshot, ownership registry, or stable subsystem contract. |
| Round reset | Additional lifecycle hooks and reset integrations | Rewrite | Current `KillPlayers` is already a broad transaction. Replace only with an ordered coordinator preserving `DontKillPlayer`, organism, fake-up, class, balance, and equipment semantics. |
| Death delayed work | Generation-wrapped `timer.Simple` callbacks | Rewrite | Generation guards are useful, but delayed tasks must be named internally, cancellable, attributable, and released on disconnect/transition. |
| Spectator admission | Additional mode and UI integrations | Keep Z-City temporarily | Current behavior remains while hard-coded team restoration and client-request handling are replaced behind mode authority. |
| Spawn contracts | Explicit team/FFA/solo topology and validation | Deferred | Core selection and fallback behavior is documented; every shipping mode's return shape and runtime behavior still require fixtures. |
| Spawn validation cache | Cache valid and invalid spawn clusters by map/mode/count | Rewrite | Cache identity lacks configuration, implementation, validation, and source revisions; invalid results can become stale. |
| Spawn candidate metadata | Named groups, topology, and validation reporting | Adapt | Preserve candidate source, policy, validation reasons, reservation state, and fallback reason without adopting Trauma's full framework. |
| Organism schema | Expanded fields, module conventions, health UI, custom-mode extensions | Rewrite | Destination Z-City has a large implicit schema duplicated across reset, simulation, networking, and clients. Introduce one typed field registry; do not add another parallel schema. |
| Organism ownership | Additional adapters, transfer handling, fake/death integration | Rewrite | Shared-table compatibility remains initially, but player/fake/death/NPC transfers require explicit identity and owner generations. Broad detours are rejected. |
| Physiology modules | Expanded medical, narcotic, infection, temperature, and status modules | Adapt | Evaluate each mechanic independently behind deterministic phases and registered read/write fields. Preserve only evidence-backed behavior. |
| Organism damage context | Additional damage detours and compatibility patches | Rewrite | Replace global penetration overrides and ambient inflictor fields with one per-event context. Separate geometry, mutation, effects, and replication while preserving fixtures. |
| Organism replication | Large snapshots, partial tables, health packets and delta concepts | Rewrite | Adopt schema/version/delta requirements, but replace whole-table serialization and overlapping NetVar/packet authority with explicit visibility sets and owner generations. |
| Organism diagnostics | Self-tests, statistics, inspection, and health visibility | Adapt | Keep bounded server health, authorized inspection, bandwidth, phase-order, stale-owner, and invalid-state diagnostics. Do not expose private physiology by default. |
| Medical/health presentation | Large HUD, inspection, texts, screen effects, and interactions | Adapt | Salvage mechanics and data-driven presentation selectively. Reject monolithic UI combining server state, networking, interaction, rendering, and prose generation. |
| Whole-table developer replication | Send complete organism state in developer mode | Reject | Developer convenience does not justify serializing arbitrary entities/tables or bypassing visibility and schema limits. |
| Organism compatibility surface | Current hooks, fields, table sharing, damage outcomes, and packet names | Keep Z-City temporarily | Preserve until representation, movement, class, item, packet, and injury fixtures establish a compatible migration boundary. |
| Fake-ragdoll identity | Extended fake, recovery, death conversion, play-dead, vehicle, and rendering behavior | Rewrite | Current identity has multiple writable authorities and no generation. Replace with ADR-0003 state while preserving compatibility projections and fixtures. |
| Fake-ragdoll mechanics | Camera, ragdoll combat, play-dead, vehicle, and presentation improvements | Adapt | Evaluate each mechanic behind bounded representation, camera, weapon, and vehicle policies. Do not port overlapping replacement paths. |
| Fake-ragdoll delayed work | Timers and callbacks across fake, recovery, death, collision, fire, and vehicles | Rewrite | Bind every task to relevant player, round, and representation generations with cancellation and attribution. |
| Vehicle/fake integration | Direct parenting, constraints, seat switching, camera, weapon, and ejection behavior | Rewrite | Use one optional vehicle capability adapter. Core fake and weapon behavior remains valid when Glide or another provider is absent. |
| Bots | Driver, arbitration, survival, rescue, squads, and mode-specific bots | Deferred | Treat as a separate architecture after player/mode/spawn/weapon contracts stabilize. Existing reports show major defects and overlapping authorities. |
| Networking | Hundreds of declarations, receivers, and sends across realms | Rewrite | The target contract, stable requirements, acceptance tests, and Trauma attempt-family dispositions now exist. Implementation remains blocked on the generated endpoint graph, duplicate-owner resolution, exact payload/visibility/rate audit, and runtime packet/bandwidth evidence. See `zcity/network-contract-and-trust-boundaries.md` and `sources/trauma-networking-assessment.md`. |
| Optional adapters | Glide, VJ Base, DynaBase, vFire, Pathowogen and others | Rewrite | Adapters must be capability-detected, inert when absent, isolated from vendor code, generation-safe, and tested independently. |
| Bundled vendor systems | Large portions of Glide, DynaBase, vFire and related content included | Reject as default architecture | Prefer external dependencies or isolated vendor packages. Project adapters must not be mixed with vendor internals. |
| Minimap | Bake, sync, client map, and relation hooks | Unreviewed | Requires separate stability, authority, privacy, performance, and value assessment. |
| Onboarding | Structured intro, input icons, keybind and rich-text systems | Adapt | Useful if data-driven and generated from verified mechanics and current settings. |
| Map tools | Map points, traitor controls, validation and map checks | Adapt | Useful, but schemas, authority, permissions, migration, and cache invalidation need formal definitions. |
| Weapon balance | Runtime schema/editor/application layer | Rewrite | Retain immutable authored definitions, validated versioned overrides, per-instance resolution, rollback, server authority, and diagnostics. Reject shared SWEP-table mutation. |
| Weapon obstruction | Muzzle/barrel and side-obstruction logic | Deferred | Requires exact mapping of fire origin, ADS, hip fire, ready states, sprint, vehicles, fake combat, bots, and presentation origins. |
| Fake-ragdoll weapon ownership | Additional ragdoll combat and weapon handling | Rewrite | Attach weapon ownership and delayed actions to the authoritative character representation generation. Fake state must not become a second weapon authority. |
| Vehicle weapon integration | Vehicle aiming, camera, seated weapons, free aim, and fire behavior | Rewrite | Place eligibility, pose, aim, muzzle, obstruction, camera, fire, seat, exit, and ejection behind the vehicle adapter boundary. |
| Physical bullets/projectiles | Expanded physical bullet and projectile behavior | Deferred | Map damage dispatch, organism penetration, prediction, lag compensation, effects, networking, and cleanup first. Future work uses event-scoped damage context. |
| Explosion manager | Central explosive/shrapnel processing | Deferred | Potentially valuable, but it must not become a second damage authority or bypass projectile, entity, and organism contracts. |
| Bot/NPC weapon behavior | Bot aiming, muzzle, obstruction, fire, reload, and mode integration | Deferred | Define the shared player weapon capability contract first; bot paths must be explicit adapters rather than silent forks. |
| Weapon networking | Additional weapon/editor/projectile messages | Rewrite | Require owner, direction, schema, permission, holder/representation generation, rate policy, payload limits, and stale-update rejection. |
| Client performance | Shared performance registry, budgets, effect toggles | Adapt | Keep truthful controls; avoid a single toggle masking correctness bugs. Measure before dynamic degradation. |
| Content loading | Configurable Workshop loading | Rewrite | Destination baseline `429ec92` has commented resource calls; upstream `3716789` re-enables them. Replace both with a truthful manifest and dependency report. See `zcity/upstream-delta-429ec92-to-3716789.md`. |
| Administration | Context properties, possession, scaling, medical and NPC tools | Deferred | Inventory permissions and server authority before porting. Every action requires explicit access and validation. |

## Canonical evidence documents

- `source-baselines.md`
- `standards/evidence-and-testing.md`
- `standards/runtime-ownership-and-generations.md`
- `zcity/boot-and-loading.md`
- `zcity/mode-and-round-lifecycle.md`
- `zcity/player-lifecycle.md`
- `zcity/player-class-inventory-equipment-boundary.md`
- `zcity/round-and-spectator-networking.md`
- `zcity/network-contract-and-trust-boundaries.md`
- `zcity/organism-lifecycle-and-damage.md`
- `zcity/fake-ragdoll-lifecycle.md`
- `zcity/weapon-and-combat-interfaces.md`
- `zcity/upstream-delta-429ec92-to-3716789.md`
- `zcity/verified-defects.md`
- `sources/trauma-clean-inventory.md`
- `sources/trauma-mode-lifecycle-comparison.md`
- `sources/trauma-networking-assessment.md`
- `sources/trauma-lifecycle-assessment.md`
- `sources/trauma-weapon-combat-assessment.md`
- `../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`
- `../decisions/ADR-0003-EXPLICIT_CHARACTER_REPRESENTATION_STATE.md`
- `../decisions/ADR-0004-DECLARED_MODE_CALLABLES_AND_OWNED_RESOURCES.md`

## Behavioral spine and implementation boundary

Broad subsystem replacement remains prohibited until these flows have source contracts and acceptance fixtures:

1. addon boot and load order;
2. gamemode selection and round lifecycle;
3. player admission, spawn, death, fake death, spectating, respawn, class, inventory, and equipment;
4. organism initialization, damage, clearing, incapacitation, and death;
5. weapon deployment, aiming, obstruction, firing, and damage dispatch;
6. map cleanup, shutdown, disconnect, and hot reload.

A bounded implementation slice may proceed earlier only through a **Ready** work package satisfying Gates 0–2 in `../BUILD_GUIDE.md`. It must not create a second authority or depend on unverified higher-level behavior.

Current status:

- organism and fake-ragdoll ownership risks are substantially source-mapped, but runtime fixtures and remaining consumers are incomplete;
- ordinary player and spectator flows are source-mapped, but mode-specific, movement, inventory/class implementation, replication, and runtime fixtures remain incomplete;
- weapon concepts have bounded dispositions, and exhaustive local source search is now available, but the complete publisher/consumer and fire graph is still pending;
- the network target contract and Trauma dispositions are defined, but the generated endpoint registry, duplicate resolution, packet captures, and bandwidth/handler-time evidence remain prerequisites;
- cleanup, shutdown, bots/NPCs, and adapter/vendor separation remain major prerequisites.

These flows form the compatibility spine. Work packages must preserve them or document and test an intentional divergence.
