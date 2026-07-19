# Trauma Clean Networking Assessment

- **Status:** SOURCE-VERIFIED structural assessment; endpoint-level semantic review incomplete
- **Source:** `Trauma_Clean.zip`
- **SHA-256:** `03d6b1b917ebd33ba0a472dbc7ecf09118eb743aaadbbdd8dab1505476dc13f8`
- **Destination comparison baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Runtime packet capture:** Not performed
- **Target contract:** `../zcity/network-contract-and-trust-boundaries.md`

## Purpose

This document inventories Trauma Clean's networking attempts at the concept-family level and determines which ideas may inform the new project. It does not approve any Trauma file, channel, payload, receiver, or synchronization subsystem for migration.

Trauma is a prototype and evidence source. The migration unit is a bounded requirement or endpoint contract with verified vanilla behavior, not a source file or packet-name group.

## Structural surface

Static lexical inventory of Trauma Clean found:

| Metric | Count |
|---|---:|
| `util.AddNetworkString` calls | 327 |
| `net.Receive` calls | 340 |
| `net.Start` calls | 467 |
| duplicate declaration literal groups | 5 |
| duplicate receiver literal groups | 30 |

Compared with the historical Trauma archive:

| Metric | Delta |
|---|---:|
| network declarations | 0 |
| network receivers | 0 |
| network sends | +2 |

The clean archive therefore did not simplify the network model by reducing declarations or receivers. It retained the broad legacy/custom/vendor surface while adding or changing other implementation and diagnostic code.

Counts are lexical. They can include dead code, comments, opposite-realm definitions, compatibility declarations, inherited Z-City behavior, and bundled vendor code. They describe review size, not active runtime endpoints.

## Duplicate declaration leads

The current inventory identified repeated declaration literals for:

- `defense_commander_notification`;
- `projectileFarSound`;
- `select_mode`;
- `send_tourniquets`;
- `updtime`.

A repeated declaration is not automatically a defect. Each group still requires:

- exact source paths and realms;
- loader and lexical order;
- sender and receiver graph;
- whether definitions are compatible or divergent;
- active receiver replacement behavior;
- ownership and lifetime classification;
- runtime registration evidence.

The 30 duplicate receiver literal groups are a higher-risk lead because one active receiver can replace another under the same message name. Exact groups must be generated from the current archive before implementation decisions are made.

## Attempt families

### Legacy compatibility and stock packet retention

Trauma retains substantial destination-style packet and NWVar behavior while layering additional synchronization, compatibility guards, and replacement systems around it.

**Observed intent:** preserve stock clients and systems while introducing new architecture.

**Risk:** compatibility becomes a second writable authority rather than a projection. Packet order, receiver replacement, Lua refresh, and partial-load failure can select different effective owners.

**Disposition:** adapt the compatibility requirement; rewrite implementation as one-way measured projections from one project authority.

### Expanded snapshots and custom framework synchronization

Trauma attempts broad synchronization for custom modes, roles, classes, abilities, configuration, content, map metadata, and runtime framework state.

**Observed intent:** make data-driven systems available to joining clients and editors.

**Risk:** large or overlapping snapshots can duplicate source tables, expose unnecessary data, lack atomic completion, and create high late-join bandwidth or decode cost.

**Disposition:** rewrite as a small core join snapshot with bounded, versioned, permission-aware contributors. Do not port a monolithic framework snapshot.

### Organism, medical, narcotic, and inspection traffic

Trauma adds or changes physiology, wound, drug, infection, temperature, inspection, HUD, text-effect, and medical-interaction synchronization.

**Observed intent:** expose richer health state and presentation.

**Risk:** whole-table or loosely typed replication can leak private information, serialize unstable entity references, overlap NetVars and packets, and apply stale data after fake/death/respawn ownership transfers.

**Disposition:** rewrite replication around a typed organism schema, explicit visibility sets, owner/representation generations, bounded deltas, and authorized inspection responses. Reject developer-mode whole-table replication.

### Editor, administration, and persistence traffic

Trauma attempts runtime editors, role/class/configuration mutation, context properties, possession, scaling, medical tools, NPC tools, and other administrator commands.

**Observed intent:** make server behavior configurable in-game.

**Risk:** a permission check alone does not bound payload structure, frequency, persistence writes, validation cost, broadcast fan-out, or revision conflicts. Generic tables can replace more state than the user intended.

**Disposition:** rewrite as explicit bounded commands with request IDs, permissions, expected revisions, validation, atomic persistence, result codes, audit metadata, and rate/cost limits.

### Weapon, projectile, explosion, and effect traffic

Trauma adds or modifies weapon configuration, physical bullet/projectile behavior, explosions, trails, remote effects, camera effects, and fake/vehicle weapon interactions.

**Observed intent:** synchronize richer combat presentation and configurable weapon behavior.

**Risk:** effects can become gameplay authority, mutable shared weapon definitions can be broadcast as state, and projectile messages can outlive holder, weapon, representation, or round generations.

**Disposition:** rewrite around server-authoritative fire/damage state, compact presentation events, immutable authored definitions plus revisioned overrides, and holder/weapon/representation generations.

### Mode, bot, NPC, minimap, map-tool, and onboarding traffic

Trauma introduces mode-specific requests/results, bot/NPC diagnostics and controls, minimap baking/sync, map points and traitor controls, votes, onboarding, and UI support messages.

**Observed intent:** expose subsystem state and controls to clients.

**Risk:** each subsystem can create its own late-join path, permission model, naming convention, and retry behavior. Bots/NPCs can also become hidden clients of player-only packet assumptions.

**Disposition:** evaluate each feature after its gameplay authority exists. Shared infrastructure must use the central endpoint registry, visibility policy, and snapshot contributor model.

### Diagnostics, readiness, payload, and rate concepts

Later Trauma work attempts broader self-tests, live-test guidance, readiness reports, health status, and in some experiments payload/rate or crash-guard concepts.

**Observed intent:** make failures and overload visible.

**Risk:** readiness can report registration presence while active receiver ownership, packet semantics, gameplay correctness, privacy, and runtime cost remain unverified. A generic guard can conceal bad contracts rather than fix them.

**Disposition:** adapt aggregate endpoint telemetry, duplicate-owner detection, payload statistics, stale-drop counters, and rate rejection reporting. Separate health checks from parity, security, performance, and acceptance tests.

### Optional providers and bundled vendor traffic

The archive includes or modifies Glide, vFire, DynaBase/wOS, VJ, Pathowogen, and related integration/vendor code.

**Observed intent:** make optional ecosystems work with Trauma features.

**Risk:** project behavior can depend on vendor packet names or bundled implementation details, and vendor updates can silently change network contracts.

**Disposition:** reject bundled-provider networking as project authority. Provider adapters must be isolated, absent-safe, capability-detected, and translate into project-owned contracts.

## Refined concepts worth retaining

The following Trauma-derived concepts are justified as requirements, not implementations:

1. **Endpoint metadata:** owner, direction, schema, visibility, permissions, rate policy, lifetime, and compatibility status.
2. **Generation-aware delivery:** stale messages and asynchronous completions must be rejected after mode, round, life, representation, weapon, entity, or data transitions.
3. **Ordered snapshot contributors:** late join needs explicit completion and contributor presence rather than incidental broadcasts.
4. **Bounded administrator results:** editor/admin commands need request/result/revision contracts and rollback-safe persistence.
5. **Passive observability:** registration history, duplicate active owners, packet counts, sizes, handler cost, stale drops, and rejection reasons.
6. **Compatibility measurement:** legacy channels may remain temporarily only as observable one-way projections with removal criteria.
7. **Provider isolation:** optional integrations translate through stable project endpoints and remain inert when absent.

## Concepts requiring clean rewrite

The requirement may be valid, but the implementation should not be migrated when it relies on:

- unrestricted `net.WriteTable` / `net.ReadTable` as a public contract;
- whole-system or whole-organism table replication;
- multiple late-join broadcasts without sequence and completion state;
- receiver-local permission checks without shared rate, payload, and expected-state policy;
- duplicate writable state across packets, NWVars, globals, and replacement layers;
- shared SWEP definition mutation distributed as runtime authority;
- anonymous delayed application after packet reception;
- implicit entity validity as the only stale-message defense;
- compressed or chunked transfers without total/decompressed limits and expiry;
- vendor packet names or vendor internals as core project contracts;
- broad receiver interception or replacement as permanent architecture.

## Rejected concepts

The new project rejects:

- adding packets solely to repair an incoherent snapshot;
- treating registration presence as proof that synchronization works;
- developer convenience bypasses for private or unbounded state replication;
- client-authored arbitrary object/table replacement;
- bundled vendor networking as the default dependency model;
- silent fallback to a second authority when an optional subsystem is missing;
- global packet interception as the shipped ownership mechanism;
- retaining compatibility paths without measured use and removal criteria.

## Security and privacy boundary

Trauma's broad feature surface creates several distinct trust classes that must not share one generic policy:

| Class | Minimum policy |
|---|---|
| ordinary gameplay request | server authority, bounded action, state/generation check, per-player rate/cost limit |
| spectator request | mode and life eligibility, visibility policy, stale-target rejection |
| medical inspection | proximity/relationship/role/equipment authorization, private field allowlist, target generation |
| editor/configuration command | explicit admin permission, schema validation, revision conflict handling, atomic persistence |
| diagnostic request | permission, bounded output, payload privacy, global cost limit |
| optional-provider event | adapter capability/version check, project schema translation, absent-safe behavior |

Administrator status is not a substitute for payload validation, revision checks, or rate limits.

## Performance boundary

The current lexical counts are too broad to infer runtime bandwidth. Required performance evidence includes:

- active endpoint count after boot and after each mode activation;
- per-endpoint packet rate and encoded bytes;
- late-join total bytes and completion latency;
- receiver handler time and world-query/persistence fan-out;
- broadcast versus targeted recipient counts;
- duplicate/replaced receiver history;
- chunk buffer occupancy and expiry;
- 1, 16, 32, and 64-player representative cases;
- behavior under malformed and over-rate client traffic.

A lower packet count is not automatically better if payloads are larger or handlers are more expensive. The audit must measure both wire and server/client work.

## Evidence limitations

The following remain unknown:

- the complete active channel set under actual Trauma Clean load order;
- exact declaration, sender, and receiver paths for all literals;
- exact payload field order and bounds for all endpoints;
- active receiver after duplicate registrations and Lua refresh;
- permission, visibility, and rate policy coverage;
- late-join ordering and completion behavior;
- runtime bandwidth, handler cost, and failure behavior;
- which channels belong to project code, inherited Z-City, adapters, or bundled vendor code;
- whether internal Trauma documentation accurately reflects the current executable archive.

No endpoint should be approved from counts or names alone.

## Prerequisites for implementation

Before a networking work package reaches **Ready**:

1. Generate declaration, sender, receiver, NWVar, and NetVar inventories for destination `429ec92`, upstream `3716789`, and current Trauma Clean.
2. Classify each Trauma source as inherited stock, project attempt, compatibility layer, adapter, vendor code, or direct vendor modification.
3. Resolve duplicate declaration and receiver groups by realm, load order, and active owner.
4. Document exact payload fields, direction, permission, visibility, rate, lifetime, and generation dependencies.
5. Link each retained requirement to `NET-REQ-*` and `NET-AT-*` in `../zcity/network-contract-and-trust-boundaries.md`.
6. Capture runtime packet, bandwidth, receiver replacement, and handler-cost evidence.
7. Define compatibility projections and rollback without parallel writers.

## Current disposition summary

| Area | Decision |
|---|---|
| endpoint ownership/schema metadata | Adapt |
| lifecycle generation metadata | Adopt as a requirement |
| late-join synchronization | Rewrite |
| round/spectator synchronization | Rewrite behind compatibility projections |
| organism/medical replication | Rewrite |
| editor/admin commands | Rewrite |
| diagnostics and packet telemetry | Adapt |
| unrestricted table replication | Reject for new endpoints |
| ad hoc network proliferation | Reject |
| bundled vendor networking authority | Reject |
| legacy channels during migration | Keep temporarily as measured one-way projections |

This assessment does not authorize production Lua changes. The first justified implementation slice is a generated static registry and passive runtime registration telemetry that does not intercept or alter packet behavior.
