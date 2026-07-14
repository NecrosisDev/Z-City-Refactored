# Trauma Clean Source Inventory

- **Status:** SOURCE-VERIFIED structural inventory; semantic review incomplete
- **Source:** `Trauma_Clean.zip`
- **SHA-256:** `03d6b1b917ebd33ba0a472dbc7ecf09118eb743aaadbbdd8dab1505476dc13f8`
- **Extracted root:** `Trauma_Clean`
- **Runtime verification:** Not performed
- **Supersedes:** `trauma-inventory.md` for implementation guidance

## Scope

This inventory describes the current Trauma prototype supplied for comparison. It measures review surface and identifies attempted concepts. It does not certify that a feature is active, correct, secure, performant, or compatible with vanilla Z-City.

Documentation contained inside Trauma is treated as **CLAIMED** evidence until verified against executable source and runtime fixtures.

## Snapshot metrics

| Metric | Count |
|---|---:|
| Files | 1,289 |
| Lua files | 1,035 |
| Lua source bytes | 8,850,553 |
| `hook.Add` calls | 1,173 |
| `timer.Create` calls | 93 |
| `timer.Simple` calls | 559 |
| `timer.Remove` calls | 100 |
| `util.AddNetworkString` calls | 327 |
| `net.Receive` calls | 340 |
| `net.Start` calls | 467 |
| `CreateConVar` calls | 240 |
| `CreateClientConVar` calls | 121 |
| `concommand.Add` calls | 207 |
| `file.Write` calls | 45 |

Counts are lexical. They include inherited Z-City, bundled vendor code, comments/dead paths, compatibility declarations, and opposite-realm definitions.

## Delta from the historical Trauma archive

Compared with `Trauma.zip` (`0286d0f...`):

| Change | Count |
|---|---:|
| Added files | 249 |
| Removed files | 0 |
| Changed files | 197 |
| Added Lua files | 7 |
| Removed Lua files | 0 |
| Changed Lua files | 197 |

Registration deltas:

| Metric | Delta |
|---|---:|
| `hook.Add` | +23 |
| `timer.Create` | +3 |
| `timer.Simple` | +13 |
| network declarations | 0 |
| network receivers | 0 |
| network sends | +2 |
| server ConVar creation | +4 |
| client ConVar creation | +2 |
| console commands | +7 |
| file writes | +3 |

The current archive is not merely a packaging cleanup. It changes a substantial portion of executable Lua and adds new diagnostics/restoration code, release documentation, assets, and vendor data.

## Newly added Lua files

The seven new Lua paths are:

- `gamemodes/trauma/gamemode/libraries/livetest/cl_guide.lua`;
- `gamemodes/trauma/gamemode/libraries/livetest/sv_guide.lua`;
- `lua/autorun/00_trauma_dependencies.lua`;
- `lua/autorun/client/cl_restored_projectile_trails.lua`;
- `lua/autorun/server/sv_zc_codex_possess_floor_probe_loader.lua`;
- `lua/autorun/sh_restored_feature_controls.lua`;
- `lua/zc_codex_possess_floor_probe.lua`.

These names suggest dependency reporting, live-test guidance, restored feature controls, projectile presentation, and possession diagnostics. The names are not proof of correctness or integration.

## Added non-code evidence

The archive adds substantial internal documentation, including:

- per-mode documents;
- release/readiness evidence;
- dependency and third-party notices;
- minimap and bot audits;
- operations guidance;
- a mode shipping matrix.

Use these documents to find claims and intended behavior. Do not use them as build authority without source and runtime verification.

## Duplicate literal groups

Static literal analysis found:

| Type | Duplicate groups |
|---|---:|
| Network declarations | 5 |
| Network receivers | 30 |
| Hook event/identifier pairs | 7 |
| ConVars | 29 |
| Named timers | 5 |

Duplicate network declarations remain:

- `defense_commander_notification`;
- `projectileFarSound`;
- `select_mode`;
- `send_tourniquets`;
- `updtime`.

Duplicates are review leads. Some may be intentional shared/opposite-realm declarations. Each requires realm, load-order, replacement, and ownership analysis.

## Major attempt groups

### Bootstrap, dependencies, and observability

Attempts include project identity, disk logging, dependency checks, feature controls, compatibility autoruns, live-test guidance, and broad self-test/readiness reporting.

**Disposition:** adapt requirements; rewrite implementation under the project evidence taxonomy. Avoid multiple competing bootstrap paths and silent compatibility fallbacks.

### Deterministic loading and mode lifecycle

Attempts include lexical ordering, mode activation/deactivation, generation guards, registration capture, cleanup, diagnostics, and retained state.

**Disposition:** adopt generation guards; rewrite ownership and activation; reject permanent global API interception. See `trauma-mode-lifecycle-comparison.md`.

### Custom gamemode framework

Attempts include schemas, V1/V2 definitions, modules, runtime configuration, storage, submissions, roles, classes, abilities, organism integration, editors, networking, and stock-mode adapters.

**Disposition:** extract requirements only after exhaustive stock-mode contracts. Do not port V1/V2 runtime layers or hash-pinned stock adapters wholesale.

### Spawn and map contracts

Attempts include team/FFA/solo topology, named spawn groups, safety validation, LOS separation, nav requirements, cache persistence, map points, traitor controls, minimap baking, and validation.

**Disposition:** adapt metadata and diagnostics; rewrite authority, validation, caching, and persistence after mode fixtures exist.

### Organism, medical, narcotic, and presentation systems

Attempts include expanded physiology, wounds, narcotics, infection, temperature, inspection, HUD, text effects, screen effects, interactions, packets, and NetVars.

**Disposition:** inventory mechanics individually. Rewrite schema ownership, damage context, replication, and visibility. Reject whole-table replication and monolithic UI authority.

### Fake-ragdoll, vehicle, and weapon systems

Attempts include representation changes, play-dead, ragdoll combat, vehicle constraints, free aim, camera changes, weapon balance, obstruction, physical bullets, projectiles, and explosions.

**Disposition:** adapt bounded mechanics; rewrite identity, weapon instance, fire authority, delayed work, networking, and optional vehicle integration.

### Bots and NPCs

Attempts include behavior arbitration, mode-specific bots, navigation, survival/rescue/squad behavior, debug tools, population control, combatant abstractions, VJ integration, and a global legacy-bot disable path.

**Disposition:** defer implementation until player-equivalent mode/spawn/representation/weapon contracts exist. Reject global disabling and parallel silent authorities.

### Administration and persistence

Attempts include context properties, possession, scaling, medical/NPC tools, editors, runtime mutations, file writes, and configuration systems.

**Disposition:** inventory permissions and persistence schemas. Require explicit server authority, bounded payloads, revisioned atomic writes, and rollback.

### Optional and bundled providers

The archive includes or modifies substantial Glide, vFire, DynaBase/wOS, VJ, and Pathowogen-related code.

**Disposition:** reject bundling as default architecture. Separate each file into project code, adapter, vendor code, direct vendor modification, or incorrectly coupled feature. Future adapters must be absent-safe and provider-independent.

## Cross-cutting risks retained in the clean archive

1. Legacy and replacement systems remain present together.
2. Multiple autoruns and loaders can establish overlapping authority.
3. Lexical filename order substitutes for declared dependencies.
4. Large quantities of anonymous delayed work remain.
5. Registrations, entities, and references do not share one ownership model.
6. Networking lacks one schema/direction/permission/rate registry.
7. Runtime mutation complicates restoration of authored definitions.
8. Optional dependencies remain entangled with project behavior.
9. Broad self-test/readiness claims can pass while gameplay remains broken.
10. Internal Trauma documentation can overstate implementation maturity.
11. Vendor updates and project fixes are mixed in the same tree.
12. Compatibility guards can suppress errors while leaving invalid state active.

## Build-guide rule

No Trauma file is a unit of migration. The migration unit is a requirement or bounded mechanic with:

- exact destination-baseline behavior;
- exact Trauma source paths;
- disposition;
- authority and lifecycle design;
- acceptance tests;
- compatibility and rollback strategy.

Use `../comparison-ledger.md`, accepted ADRs, and `../../BUILD_GUIDE.md` to authorize implementation.
