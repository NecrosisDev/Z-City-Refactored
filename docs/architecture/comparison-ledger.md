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
| Generation guards | Ignore delayed callbacks from inactive mode generations | Adopt | Low-cost protection with clear semantics; integrate into owned tasks, death/spectator delays, packet sequencing, and asynchronous completions. |
| Persistent hooks | Hard-coded event allowlist remains global | Reject | Lifetime must be declared per resource, not inferred from event name. |
| Static registration capture | Loader captures registrations made by mode files | Deferred | May be useful as temporary migration/audit tooling, not as permanent runtime architecture. |
| Lifecycle diagnostics | Active mode, generation, hook and timer counts | Adapt | Expand with owner, source, realm, lifetime, replacement history, player lifecycle phase, packet generation, and leak reporting. |
| Legacy mode dispatcher | Mode-table function names automatically become hook handlers | Keep Z-City temporarily | Preserve behavior until every mode method is classified. Replace only behind parity tests. |
| Active registries | Dense array plus reverse-position map and pruning | Adapt | Useful collection primitive. Encapsulate live storage, declare ordering semantics, and separate lifecycle ownership. |
| Self-tests | Shared/server/client command-driven diagnostics | Rewrite | Keep the concept but separate static audit, production health checks, smoke tests, behavioral tests, and performance tests. |
| Player lifecycle tracing | Additional lifecycle diagnostics and ownership tracking | Adapt | Add observational per-player phase tracing first. Do not replace spawn/death/spectator authority until parity tests pass. |
| Late-join synchronization | Expanded state synchronization across custom systems | Rewrite | Current synchronization is fragmented, while Trauma adds more channels. Define one versioned server-authoritative snapshot with ordered subsystem contributors and a completion contract. |
| Round snapshot | Multiple state and timing updates across channels | Rewrite | Replace fragmented mode/state/timing delivery with one sequenced snapshot. Preserve `RoundInfo` and `updtime` as compatibility projections until clients and modes migrate. |
| Packet metadata | Broader schema and ownership concepts across Trauma networking | Adapt | Adopt explicit owner, direction, schema version, rate policy, authority, and generation metadata; do not port Trauma's network surface wholesale. |
| Client request validation | Numerous custom receivers with local validation patterns | Rewrite | Centralize bounded enums, rate controls, expected-state checks, permission checks, payload limits, and rejection diagnostics. |
| Spectator state replication | Additional spectator and custom-system synchronization | Rewrite | Current Z-City already duplicates target/view state across messages and NWVars. Select one authority and expose compatibility projections. |
| Network proliferation | Additional subsystem-specific messages to patch synchronization gaps | Reject | New channels must not substitute for a coherent snapshot, ownership registry, or stable subsystem contract. |
| Round reset | Additional lifecycle hooks and reset integrations | Rewrite | Current `KillPlayers` is already a broad transaction. Replace only with an ordered coordinator that preserves `DontKillPlayer`, organism, fake-up, class, balance, and equipment semantics. |
| Death delayed work | Generation-wrapped `timer.Simple` callbacks | Rewrite | Generation guards are useful, but delayed tasks must be named internally, cancellable, attributable, and released on disconnect/transition. |
| Spectator admission | Additional mode and UI integrations | Keep Z-City temporarily | Current behavior must remain while hard-coded team restoration and client-request handling are documented and replaced behind mode authority. |
| Spawn contracts | Explicit team/FFA/solo topology and validation | Deferred | Core Z-City selection and fallback behavior is now documented in `zcity/player-lifecycle.md`; every stock mode's return shape and runtime behavior still require mapping. |
| Spawn validation cache | Cache valid and invalid spawn clusters by map/mode/count | Rewrite | Cache key lacks configuration/implementation/validation versions; invalid results can become stale. |
| Spawn candidate metadata | Named groups, topology, and validation reporting | Adapt | Preserve candidate source, policy, validation reasons, reservation state, and fallback reason without adopting Trauma's full framework. |
| Organism | Expanded medical modules, narcotics, infection, delta networking | Deferred | High regression risk. Map vanilla organism initialization, damage, clearing, fake/death interaction, and replication first. |
| Fake ragdoll | Extended fake, vehicle, play-dead, combat, and rendering behavior | Deferred | Core identity system. Requires full vanilla state-machine and prediction documentation. |
| Bots | Bot driver, behavior arbitration, survival, rescue, squads, mode-specific bots | Deferred | Treat as a separate architecture after player/mode/spawn contracts are stable. Existing behavior reports show major defects. |
| Networking | Hundreds of declarations, receivers, and sends across realms | Rewrite | The core round/spectator baseline is now documented in `zcity/round-and-spectator-networking.md`; full addon registry, duplicate-name resolution, and trust-boundary audit remain required. |
| Optional adapters | Glide, VJ Base, DynaBase, vFire, Pathowogen and others | Rewrite | Adapters must be capability-detected, inert when absent, isolated from vendored code, and tested independently. |
| Bundled vendor systems | Large portions of Glide, DynaBase, vFire and related content included in project | Reject as default architecture | Prefer external dependencies or isolated vendor packages. Project adapters must not be mixed with vendor internals. |
| Minimap | Bake, sync, client map, and relation hooks | Unreviewed | Requires separate stability and value assessment. |
| Onboarding | Structured intro, input icons, keybind and rich-text systems | Adapt | Good concept if data-driven and generated from verified mechanics/settings. |
| Map tools | Map points, traitor controls, validation and map checks | Adapt | Useful, but schemas, authority, permissions, migration, and cache invalidation need formal definitions. |
| Weapon balance | Runtime schema/editor/application layer | Deferred | Document weapon inheritance and mutation behavior. Avoid irreversible mutation of stock SWEP tables. |
| Weapon obstruction | Muzzle/barrel and side-obstruction logic | Deferred | Requires comparison with vanilla aiming, ADS, low/high ready, vehicles, and bot muzzle behavior. |
| Explosion manager | Central explosive/shrapnel processing | Unreviewed | Evaluate after current damage, phys-bullet, entity, and organism pipelines are mapped. |
| Client performance | Shared performance registry, budgets, effect toggles | Adapt | Keep truthful user/server controls; avoid a single toggle masking correctness bugs. Measure before enabling dynamic degradation. |
| Content loading | Configurable Workshop loading | Rewrite | Current repository ConVar controls a block with commented resource calls. Replace with a truthful manifest and dependency report. |
| Administration | Expanded context properties, possession, scaling, medical and NPC tools | Deferred | Inventory permissions and server authority before porting. Every action requires explicit access and validation. |

## Verified source documents

- `zcity/boot-and-loading.md`
- `zcity/mode-and-round-lifecycle.md`
- `zcity/player-lifecycle.md`
- `zcity/round-and-spectator-networking.md`
- `zcity/verified-defects.md`
- `sources/trauma-inventory.md`
- `sources/trauma-lifecycle-assessment.md`
- `../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`

## Behavioral spine required before gameplay ports

No gameplay subsystem will be ported until these flows are documented and assigned acceptance tests:

1. addon boot and load order;
2. gamemode selection and round lifecycle;
3. player initial spawn, spawn, death, fake death, spectating, and respawn;
4. organism initialization, damage, clearing, incapacitation, and death;
5. weapon deployment, aiming, obstruction, firing, and damage dispatch;
6. map cleanup, shutdown, and hot-reload behavior.

The ordinary player lifecycle and its core round/spectator network contracts are now mapped at the gamemode level. Fake-ragdoll, organism, player-class, inventory, equipment, mode-specific branches, and the complete addon packet registry remain prerequisites before item 3 is complete.

These flows form the compatibility spine. Higher-level ports before them would reproduce Trauma's layering problems.
