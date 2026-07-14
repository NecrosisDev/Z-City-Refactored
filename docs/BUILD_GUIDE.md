# Z-City Refactor Build Guide

- **Status:** Normative implementation guide
- **Applies to:** `fix/repo-foundation-hardening` and successor implementation branches
- **Source authority:** `architecture/source-baselines.md`
- **Decision authority:** accepted ADRs under `decisions/`

## Purpose

This is the entry point for writing the new code. It converts the research documents into an ordered, test-gated migration process. It does not authorize broad rewrites, direct Trauma file ports, or removal of legacy behavior without evidence.

## Non-negotiable rules

1. **Use exact source names.** “Vanilla,” “destination baseline,” “Trauma,” and “working branch” have distinct meanings defined in `architecture/source-baselines.md`.
2. **One authority per state.** Compatibility aliases and legacy packets may project state, but they must not become additional writable authorities.
3. **No unowned runtime resources.** New hooks, timers, delayed tasks, receivers, commands, entities, constraints, and cleanup callbacks must follow `architecture/standards/runtime-ownership-and-generations.md`.
4. **No gameplay parity claim from static inspection.** Evidence and test requirements are defined in `architecture/standards/evidence-and-testing.md`.
5. **No permanent global interception.** Do not replace `hook.Add`, `timer.Create`, `timer.Simple`, networking functions, or equivalent engine APIs to infer ownership.
6. **No direct vendor bundling as architecture.** Optional systems integrate through capability adapters and remain absent-safe.
7. **No destructive migration without a compatibility path.** Preserve legacy `hg`, `zb`, hook, net, entity, and weapon surfaces until their callers are inventoried and migrated.
8. **No hidden fallback for critical initialization.** Required phases fail closed with structured diagnostics. Optional phases fail isolated.
9. **No client authority over gameplay state.** Client requests are bounded, rate-limited, permission-checked, generation-checked, and validated server-side.
10. **No implementation without rollback.** Every work package defines how to disable or revert the new path without corrupting persistent or runtime state.

## Authority model

### Evidence authority

Use this order when deciding what the existing system actually does:

1. Reproducible automated acceptance results tied to a source snapshot.
2. Reproducible runtime observations tied to a source snapshot and environment.
3. Direct executable-source inspection at an exact commit or archive hash.
4. Inference from several source paths.
5. Comments, names, Trauma documentation, and design intent.

### Design authority

Use this order when deciding what the new system should do:

1. Accepted ADRs.
2. Cross-cutting standards under `architecture/standards/`.
3. This build guide and an approved work-package plan.
4. Subsystem architecture documents.
5. The comparison ledger.
6. Source inventories and prototype documentation.

An ADR may change the target design. It cannot retroactively change what the baseline code does.

## Required identifiers

New implementation work uses stable identifiers:

| Item | Format | Example |
|---|---|---|
| Requirement | `ZC-REQ-<AREA>-NNN` | `ZC-REQ-MODE-001` |
| Acceptance test | `ZC-AT-<AREA>-NNN` | `ZC-AT-MODE-004` |
| Work package | `ZC-WP-NNN` | `ZC-WP-003` |
| Defect | Existing `ZC-FND-NNN` series | `ZC-FND-007` |
| ADR | Existing `ADR-NNNN` series | `ADR-0004` |

A code change must link the requirement, relevant defect or decision, and acceptance tests it satisfies.

## Work-package contract

Before implementation, create a work-package record containing:

- stable work-package ID and title;
- exact source baseline and target branch;
- problem statement and linked defect/requirement IDs;
- verified current call graph and compatibility surfaces;
- selected Trauma disposition, when applicable;
- explicit server/client ownership;
- state authority and generation rules;
- resources created and cleanup behavior;
- network schema and trust boundary changes;
- persistence and migration effects;
- performance budget and expected hot-path cost;
- acceptance-test IDs and fixtures;
- rollout switch or compatibility adapter;
- rollback procedure;
- removal criteria for the legacy path.

If any required field is unknown, the work package remains analysis-only.

## Implementation gates

### Gate 0 — Source freeze

Required:

- exact archive hash or commit for every compared source;
- exhaustive symbol/registration search for the affected subsystem;
- upstream drift review;
- no unresolved ambiguity about which baseline a claim describes.

### Gate 1 — Behavioral contract

Required:

- entry points and lifecycle documented;
- inputs, outputs, state mutations, realm, ordering, and failure behavior identified;
- compatibility invariants written;
- Trauma concept classified as adopt, adapt, rewrite, reject, defer, or keep Z-City.

### Gate 2 — Test harness

Required:

- acceptance-test IDs defined;
- fixtures and expected outcomes recorded from the destination baseline;
- failure injection available for cleanup-sensitive work;
- relevant static, smoke, parity, security, and performance checks runnable.

### Gate 3 — Compatibility implementation

Required:

- new authority exists behind a disabled-by-default switch or legacy adapter;
- old public surfaces remain projections, not independent writers;
- diagnostics can distinguish old and new paths;
- rollback restores the previous path without restart where practical.

### Gate 4 — Controlled migration

Required:

- one owner or caller group migrated at a time;
- stale-generation and cleanup tests pass;
- no duplicate authority, registration, packet, or persistent write;
- baseline parity tests pass unless an intentional change is approved.

### Gate 5 — Legacy removal

Required:

- exhaustive search shows no remaining runtime consumers;
- compatibility telemetry shows no legacy use during the agreed observation window;
- removal and downgrade behavior are tested;
- public migration notes exist.

### Gate 6 — Release evidence

Required:

- clean install and upgrade tests;
- map cleanup, disconnect, shutdown, and Lua-refresh tests;
- server/client security review;
- performance comparison against the destination baseline;
- operator-facing dependency and health report.

## Ordered build plan

### Phase 0 — Documentation and analysis infrastructure

Deliverables:

- source snapshot registry;
- repository indexes for Z-City and Trauma;
- evidence/test standard;
- runtime ownership standard;
- traceability format;
- upstream drift ledger.

Exit condition: an engineer can identify the exact source, decision, tests, and rollback requirements for a proposed change without relying on chat history.

### Phase 1 — Observation and low-risk foundation corrections

Initial candidates:

- project-owned immutable metadata with temporary legacy aliases (`ZC-FND-001`);
- correct the accidental global `tbl2` leak (`ZC-FND-007`);
- correct misleading state comments only after wire-value audit (`ZC-FND-009`);
- structured dependency/capability report without changing gameplay (`ZC-FND-012`);
- server-side lifecycle and resource diagnostics that do not intercept global APIs.

Explicit exclusions:

- do not change Workshop delivery yet;
- do not replace the loader yet;
- do not alter round, spawn, fake, organism, or weapon authority.

Exit condition: the baseline starts cleanly, diagnostics are actionable, and behavior remains parity-tested.

### Phase 2 — Loader, mode registry, and owned resources

Build:

- deterministic phased discovery;
- explicit legacy-mode adapter;
- declared mode callables;
- ownership scopes and generation guards;
- transactional activation/deactivation;
- validated mode-chance persistence.

Preserve:

- current mode identifiers and inheritance outcomes;
- active-mode precedence;
- method invocation and multi-return behavior;
- `MODE.saved` continuity until migrated.

Exit condition: repeated mode transitions and reloads do not leak, duplicate, or remove foreign resources.

### Phase 3 — Round, admission, spawn, spectator, and snapshots

Build:

- explicit round-reset transaction;
- character admission plan/result contract;
- spawn resolve/validate/reserve/place phases;
- server-authoritative round and late-join snapshots;
- authoritative spectator state and validated client requests.

Exit condition: join, spawn, death, spectator, respawn, round transition, and preserved-player fixtures pass for every supported stock mode.

### Phase 4 — Character representation and organism ownership

Build:

- explicit upright/fake/recovering/vehicle/corpse representation state;
- representation and organism owner generations;
- transactional fake entry, recovery, death conversion, and cleanup;
- typed organism field registry and deterministic simulation phases;
- event-scoped damage context and visibility-bounded replication.

Exit condition: no state loss, duplication, stale callback, or dual authority across player/ragdoll/death transitions.

### Phase 5 — Weapon, aiming, vehicle, projectile, and damage pipeline

Build in this order:

1. typed weapon capability adapter;
2. weapon-instance identity and snapshot/restore;
3. switch/drop/pickup/reload/ammo ownership;
4. ADS, ready stance, obstruction, and authoritative muzzle origin;
5. vehicle free aim through an optional adapter;
6. hitscan, physical bullet, projectile, penetration, effects, and explosion transactions.

Exit condition: upright, fake, vehicle, player, and bot paths consume one authoritative weapon/fire contract.

### Phase 6 — Bots and NPCs

Prerequisites:

- stable mode, spawn, representation, organism, and weapon contracts.

Build:

- shared combatant capabilities;
- explicit behavior arbitration;
- mode objectives and team policy adapters;
- navigation diagnostics and recovery;
- bounded VJ Base integration.

Exit condition: bots can complete representative mode objectives without bypassing player-equivalent authority or disabling legacy systems globally.

### Phase 7 — UI, administration, persistence, map tools, and optional adapters

Build:

- data-driven presentation consuming bounded snapshots;
- explicit admin permissions and server validation;
- versioned persistence with atomic writes and recovery;
- map schemas and cache invalidation;
- absent-safe Glide, VJ Base, DynaBase, vFire, and Pathowogen adapters.

Exit condition: core gameplay loads and remains functional with every optional dependency absent.

### Phase 8 — Legacy removal and release hardening

Deliverables:

- compatibility surface usage report;
- removed legacy paths with migration notes;
- release smoke matrix;
- security and performance evidence;
- operator runbook and dependency manifest.

## Stop conditions

Stop implementation and return to analysis when:

- the current and target authority cannot be named;
- a source path is missing from the inventory;
- a new system would create a second writable authority;
- cleanup cannot be attributed or tested;
- client input is trusted without validation;
- a behavior change lacks an approved requirement;
- a test passes only because assertions were weakened;
- a vendor dependency becomes mandatory unintentionally;
- a compatibility adapter has no removal criteria;
- the rollback path would lose persistent or live player state.

## Definition of done

A work package is complete only when:

1. code and documentation reference the same requirement and test IDs;
2. the target authority is singular and documented;
3. all created resources are owned and cleaned;
4. baseline parity or intentional differences are test-verified;
5. client trust and payload limits are reviewed;
6. hot reload, cleanup, disconnect, and shutdown are considered;
7. performance impact is measured for hot paths;
8. rollback is tested;
9. the comparison ledger and defect register are updated;
10. legacy removal criteria are explicit.
