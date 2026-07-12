# Z-City Refactored Documentation

This directory is the maintained, code-grounded knowledgebase for the refactor. It is the single documentation index for the active research branch.

## Session startup

Every agent must read these files in order:

1. [`../AGENTS.md`](../AGENTS.md) — cumulative operating contract.
2. [`WORK_PACKAGE.md`](WORK_PACKAGE.md) — current scope, evidence, validation, risks, and exact continuation action.
3. The architecture documents, catalogs, integration records, and reference matrices linked by the active work package.

## Active research state

- **Branch:** `docs/architecture-baseline`
- **Review surface:** PR `#1`
- **Phase:** code-grounded repository research plus local-archive integration documentation
- **Rule:** continue all research work packages on this branch; do not create per-package branches.
- **Runtime rule:** documentation work does not authorize merging the local archive or changing runtime Lua.

## Knowledge authority

1. Reproducible tests and runtime evidence.
2. Executable code from an explicitly identified source artifact.
3. Evidence-linked architecture documents, catalogs, integration records, and decision records.
4. Comments, historical notes, and inherited documentation.

Every claim must be labeled `Verified`, `Inferred`, `Legacy Claim`, or `Planned`. Archive evidence must identify its artifact hash and must not be silently generalized to repository `main`. When documentation and implementation disagree, the identified implementation remains authoritative until runtime evidence proves otherwise.

## Current documents

### Architecture

- [`architecture/PROJECT_SETUP.md`](architecture/PROJECT_SETUP.md) — repository layout, addon/gamemode split, namespaces, subsystem boundaries, persistence, dependencies, and structural risks.
- [`architecture/BOOTSTRAP_AND_LOAD_ORDER.md`](architecture/BOOTSTRAP_AND_LOAD_ORDER.md) — global addon bootstrap, gamemode bootstrap, Lua realm routing, recursive load order, mode registration, and round startup.
- [`architecture/ORGANISM_SYSTEM.md`](architecture/ORGANISM_SYSTEM.md) — organism attachment/ownership, canonical state, physiology order, organ hitboxes, damage, replication, fake-ragdoll coupling, defects, and validation.
- [`architecture/FAKE_RAGDOLL_SYSTEM.md`](architecture/FAKE_RAGDOLL_SYSTEM.md) — custom ragdoll creation, ownership, networking, active physics control, death/get-up, vehicles, camera/render, integration risks, and validation.
- [`architecture/MOVEMENT_SYSTEM.md`](architecture/MOVEMENT_SYSTEM.md) — prediction, speed/inertia/jump calculation, organism/class/weapon modifiers, animation, footsteps, fake transitions, and validation.
- [`architecture/PLAYER_CLASS_SYSTEM.md`](architecture/PLAYER_CLASS_SYSTEM.md) — class registry, lifecycle, transport, concrete class capabilities, organism/movement/fake integration, security defects, and migration boundaries.
- [`architecture/CHARACTER_RUNTIME_INTEGRATION.md`](architecture/CHARACTER_RUNTIME_INTEGRATION.md) — combined authority graph and lifecycle for organism, fake-ragdoll, movement, player classes, and weapon-facing contracts.
- [`architecture/WEAPON_AND_BALLISTICS_SYSTEM.md`](architecture/WEAPON_AND_BALLISTICS_SYSTEM.md) — firearm base, ammunition, bullet, reload, attachment, projectile, explosive, damage, and presentation ownership.
- [`architecture/WEAPON_COMBAT_INTERFACES.md`](architecture/WEAPON_COMBAT_INTERFACES.md) — current implicit weapon capability contracts consumed by fake-body and character runtime.
- [`architecture/BOT_AND_NPC_SYSTEM.md`](architecture/BOT_AND_NPC_SYSTEM.md) — local archive player-bot scheduler/arbiter/control, botfill, navigation, VJ compatibility, stock NPC and zombie extensions, shipping disablement, risks, and validation.

### Integration records

- [`integration/LOCAL_ARCHIVE_BASELINE.md`](integration/LOCAL_ARCHIVE_BASELINE.md) — immutable identity, structure, loader drift, project rename, subsystem families, bot shipping state, integration risks, and required repository-versus-archive delta for uploaded `Trauma.zip`.
- [`integration/LOCAL_ARCHIVE_COMPARISON_MANIFEST.md`](integration/LOCAL_ARCHIVE_COMPARISON_MANIFEST.md) — complete reproducible local file/hash inventory, exact duplicate and binary evidence, bounded core-file comparison, and repository-side comparison limitation.
- [`integration/local_archive_manifest/README.md`](integration/local_archive_manifest/README.md) — pinned archive/manifest identities and deterministic regeneration instructions.

### Living catalogs

- [`SYSTEM_CATALOG.md`](SYSTEM_CATALOG.md) — runtime systems, ownership, entry points, dependencies, public surfaces, integration state, and validation.
- [`BEHAVIOR_CATALOG.md`](BEHAVIOR_CATALOG.md) — externally observable runtime and gameplay behaviors.
- [`TYPE_CATALOG.md`](TYPE_CATALOG.md) — shared tables, registries, identifiers, payloads, schemas, and compatibility contracts.
- [`modes/MODE_CATALOG.md`](modes/MODE_CATALOG.md) — TDM, Counter-Strike, Deathmatch, Homicide, and Fear.
- [`modes/MODE_CATALOG_TEAM_AND_PVE.md`](modes/MODE_CATALOG_TEAM_AND_PVE.md) — HL2DM, CO-OP, Defense, Crisis Response, and Pathowogen.
- [`modes/MODE_CATALOG_ADDITIONAL.md`](modes/MODE_CATALOG_ADDITIONAL.md) — Riot, Gang Wars, Superfighters, Slug Arena, and Event.
- [`decisions/README.md`](decisions/README.md) — compact architectural decisions that must not be repeatedly rediscovered.

### Reference inventories and matrices

- [`reference/FILE_MANIFEST.md`](reference/FILE_MANIFEST.md) — loader roots, realm classification, known loaded trees, engine-discovered trees, and remaining enumeration gaps.
- [`reference/PUBLIC_SURFACES.md`](reference/PUBLIC_SURFACES.md) — globals, hooks, network channels, convars, commands, persistence, trust boundaries, and duplicate registration hazards.
- [`reference/MODE_FUNCTION_MATRIX.md`](reference/MODE_FUNCTION_MATRIX.md) — classification of verified function-valued mode members, dispatcher argument behavior, inheritance, collisions, and incomplete source-enumeration boundaries.
- [`reference/PACKET_MATRIX.md`](reference/PACKET_MATRIX.md) — cross-mode writers/readers, ordered schemas, trust, validation, rate/size limits, duplicate/legacy status, and unresolved endpoints.

## Dependency-ordered research queue

1. Obtain a recursive repository tree/archive and complete the repository-versus-local-archive classification.
2. Complete weapon lifecycle, physical bullet, ammunition, projectile, armor, explosive, damage and presentation traces on both identified sources.
3. Trace inventory, equipment, appearance and clothing ownership across round/class/fake/death transitions.
4. Extend bot/NPC documentation into complete packet/public-surface/type/catalog coverage and enabled-runtime evidence.
5. Trace UI, HUD, camera, spectator and screen effects.
6. Trace persistence, administration, security and external integrations.
7. Add runtime load-order/hook/packet/performance instrumentation.
8. Produce the cross-system regression matrix, verified defect catalog and implementation-ready import/remediation packages.

## Maintenance rules

- Keep this file compact; detailed evidence belongs in linked documents, code references, commits, PR discussion, and validation records.
- Update documents atomically when new evidence changes a claim.
- Do not create duplicate indexes or empty placeholder documents.
- Identify whether evidence comes from repository `main`, the documentation branch, or a hashed local artifact.
- Each completed trace must leave exact paths, symbols, dependencies, failure modes, validation steps, evidence gaps, and the next dependency-ordered action.
