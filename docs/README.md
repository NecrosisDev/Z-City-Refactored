# Z-City Refactored Documentation

This directory is the maintained, code-grounded knowledgebase for the refactor. It is the single documentation index for the active research branch.

## Session startup

Every agent must read these files in order:

1. [`../AGENTS.md`](../AGENTS.md) — cumulative operating contract.
2. [`WORK_PACKAGE.md`](WORK_PACKAGE.md) — current scope, evidence, validation, risks, and exact continuation action.
3. The architecture documents and catalogs linked by the active work package.

## Active research state

- **Branch:** `docs/architecture-baseline`
- **Review surface:** PR `#1`
- **Phase:** code-grounded project research and documentation baseline
- **Rule:** continue all research work packages on this branch; do not create per-package branches.

## Knowledge authority

1. Reproducible tests and runtime evidence.
2. Executable code.
3. Evidence-linked architecture documents, catalogs, and decision records.
4. Comments, historical notes, and inherited documentation.

Every claim must be labeled `Verified`, `Inferred`, `Legacy Claim`, or `Planned`. When documentation and implementation disagree, implementation remains authoritative until runtime evidence proves otherwise.

## Current documents

### Architecture

- [`architecture/PROJECT_SETUP.md`](architecture/PROJECT_SETUP.md) — repository layout, addon/gamemode split, namespaces, subsystem boundaries, persistence, dependencies, and structural risks.
- [`architecture/BOOTSTRAP_AND_LOAD_ORDER.md`](architecture/BOOTSTRAP_AND_LOAD_ORDER.md) — global addon bootstrap, gamemode bootstrap, Lua realm routing, recursive load order, mode registration, and round startup.

### Living catalogs

- [`SYSTEM_CATALOG.md`](SYSTEM_CATALOG.md) — runtime systems, ownership, entry points, dependencies, public surfaces, integration state, and validation.
- [`BEHAVIOR_CATALOG.md`](BEHAVIOR_CATALOG.md) — externally observable runtime and gameplay behaviors.
- [`TYPE_CATALOG.md`](TYPE_CATALOG.md) — shared tables, registries, identifiers, payloads, schemas, and compatibility contracts.
- [`modes/MODE_CATALOG.md`](modes/MODE_CATALOG.md) — core competitive and Homicide modes: IDs, inheritance, lifecycle contracts, dependencies, defects, and validation.
- [`modes/MODE_CATALOG_TEAM_AND_PVE.md`](modes/MODE_CATALOG_TEAM_AND_PVE.md) — HL2DM, CO-OP, and Defense research with NPC, persistence, wave, and map-progression dependencies.
- [`modes/MODE_CATALOG_ADDITIONAL.md`](modes/MODE_CATALOG_ADDITIONAL.md) — Riot, Gang Wars, Superfighters, and Slug Arena grouped by shared standalone-mode risks.
- [`decisions/README.md`](decisions/README.md) — compact architectural decisions that must not be repeatedly rediscovered.

### Reference inventories

- [`reference/FILE_MANIFEST.md`](reference/FILE_MANIFEST.md) — loader roots, realm classification, known loaded trees, engine-discovered trees, and remaining enumeration gaps.
- [`reference/PUBLIC_SURFACES.md`](reference/PUBLIC_SURFACES.md) — globals, hooks, network channels, convars, commands, persistence, trust boundaries, and duplicate registration hazards.

## Dependency-ordered research queue

1. complete loaded-file and realm manifest;
2. complete global symbol and public API registry;
3. complete hooks, network messages, console variables, and commands inventory;
4. complete round lifecycle and every registered mode;
5. organism, fake-ragdoll, movement, and player-class systems;
6. weapons, physical bullets, armor, ammunition, and explosives;
7. inventory, equipment, appearance, and clothing;
8. NPC and bot architecture;
9. UI, HUD, camera, spectator, and screen effects;
10. persistence, administration, security, and external integrations;
11. cross-system integration map, regression risks, and implementation-ready remediation packages.

## Maintenance rules

- Keep this file compact; detailed evidence belongs in the linked documents, code references, commits, PR discussion, and validation records.
- Update documents atomically when new evidence changes a claim.
- Do not create duplicate indexes or empty placeholder documents.
- Each completed trace must leave exact paths, symbols, dependencies, failure modes, validation steps, evidence gaps, and the next dependency-ordered action.