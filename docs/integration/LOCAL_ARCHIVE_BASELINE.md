# Local Trauma Archive Integration Baseline

**Artifact:** uploaded `Trauma.zip`  
**SHA-256:** `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652`  
**Archive root:** `TMod/`  
**Reviewed:** 2026-07-12  
**Status:** `Verified (local archive) / not yet integrated`

## Purpose and evidence boundary

This document records the executable structure of the uploaded local mod so it can be compared with repository `main` without treating either side as automatically authoritative. Claims marked `Verified (local archive)` are established only for the archive hash above. They do not establish that the same file, behavior, or fix exists in repository `main`.

Repository runtime remains commit `429ec928203cec963176dfb6afd086dcdd01c181`; the active documentation branch contains no runtime merge.

## Artifact inventory

| Root | Files | Lua files | Loading model |
|---|---:|---:|---|
| Entire `TMod/` | 1,040 | 1,028 | deployment wrapper |
| `gamemodes/trauma/gamemode/` | 203 | 203 | selected gamemode bootstrap and recursive loader |
| `lua/homigrad/` | 242 | 242 | global recursive loader |
| `lua/autorun/` | 24 | 24 | engine autorun |
| `lua/entities/` | 212 | 212 | engine SENT discovery |
| `lua/weapons/` | 262 | 261 | engine SWEP discovery |
| `lua/initpost/` | 6 | 6 | deferred recursive loader |

The archive is a full deployment tree, not a patch bundle. Integration must remove the outer `TMod/` wrapper and map its children to repository roots.

## Project identity and bootstrap drift

`lua/autorun/loader.lua` identifies the archive as:

- `hg.Version = "Release 1.5.0"`
- `hg.ProjectName = "Trauma"`
- `hg.ProjectID = "trauma"`
- legacy identity `Z-City` / `zcity`
- selected gamemode path `gamemodes/trauma`

This differs from repository `main`, which still presents the upstream Z-City identity and `gamemodes/zcity` paths. The rename affects gamemode selection, data paths, command names, network/debug labels, workshop dependencies, documentation paths, and compatibility aliases. It cannot be integrated safely as a blind overwrite.

## Local archive load contracts

### Global addon loader

`lua/autorun/loader.lua` recursively loads `lua/homigrad/`, then loads `lua/initpost/` after `InitPostEntity`.

- Exact `sv_`, `sh_`, and `cl_` prefix/suffix routing is used.
- Unmarked files are shared.
- Current-directory files load before child directories.
- `file.Find` output is not explicitly sorted.
- The loader exits early for `ixhl2rp`.
- The archive advertises multiple workshop dependencies and bundled integrations.

### Gamemode loader

`gamemodes/trauma/gamemode/loader.lua` differs materially from the repository baseline:

- files and folders are explicitly sorted;
- child directories load before current-directory files;
- mode files are wrapped in temporary `hook.Add` and `timer.Create` capture;
- captured resources are delegated to `zb.modeLifecycle`;
- prior mode ownership is deactivated before definitions are rebuilt;
- `zb.RegisterModeTable` supports programmatic table registration;
- mode screenspace effects can route through the Trauma post-process compositor;
- server mode loading is deferred until the surrounding gamemode initialization is ready.

The local loader therefore contains lifecycle and determinism work that must be compared semantically, not reduced to a path rename.

## Major local-only or materially changed subsystem families

Verified archive families include:

- mode lifecycle and round-base infrastructure;
- spawn contracts and combatant-aware helpers;
- player bot driver, behavior arbiter, navigation learning, survival configuration, debug visualization, and botfill;
- VJ Base compatibility for faction perception, organisms, corpses, bleeding, knockdown, relations, and spawn tuning;
- Glide adapters and vehicle compatibility;
- expanded organism, fake-ragdoll, movement, inventory, appearance, armor, weapon, projectile, explosive, and administration code;
- performance logging/profiling and disk logging;
- TTT trap compatibility and other external adapters.

These families must be classified as one of: archive-only addition, modified upstream file, renamed file, replacement system, bundled third-party code, or generated/content artifact.

## Shipping bot state

The archive intentionally disables player bots through `lua/autorun/000_trauma_disable_bots.lua`.

The file:

- sets `hg.BotsDisabled = true` before the recursive Homigrad loader runs;
- forces `hg_bots_enable` and `hg_botfill` off;
- kicks player bots observed through spawn/entity hooks;
- repeats cleanup on gamemode load and `InitPostEntity`;
- leaves bot APIs loadable so mode registration does not fail.

Consequently, the archive contains a large bot implementation that is dormant in the shipped configuration. Integration must preserve this distinction between **code present** and **feature enabled**.

## Integration risks established by the archive

1. **Identity split:** `trauma` and `zcity` paths/data/commands coexist through compatibility aliases.
2. **Loader semantic drift:** sorted mode loading and lifecycle capture differ from repository behavior.
3. **Bundled dependency ownership:** Glide, VJ Base, DynaBase, vFire and other code may overlap workshop-managed copies.
4. **Dormant system ambiguity:** bot code is loaded but globally disabled.
5. **Persistence migration:** some systems read legacy `zcity` data and write new `trauma` data; others still write `zcity_*` paths.
6. **Security surface growth:** local admin/debug/config transports and commands require explicit permission, bounds and rate review.
7. **No integrated runtime evidence:** neither a dedicated-server smoke test nor repository-versus-archive regression run has been captured.

## Required integration comparison

The merge package must produce a machine-readable manifest with, for every archive path:

- destination repository path after removing `TMod/`;
- repository counterpart, if any;
- content hash on both sides;
- classification: identical, modified, archive-only, repository-only, rename, generated, bundled dependency, or excluded;
- subsystem owner and realm;
- required migration/compatibility action;
- validation test.

Runtime changes should then be imported in dependency-ordered subsystem commits rather than one archive replacement commit.

## Validation gates

Before merging runtime code:

1. verify server/client include manifests and deterministic mode order;
2. boot the gamemode on a clean dedicated server with only declared dependencies;
3. verify no bundled/workshop class collisions;
4. exercise round selection, spawn, fake/get-up, organism, inventory, weapon, vehicle and NPC paths;
5. test bot-disabled shipping behavior and a separate development build with bots enabled;
6. inspect all client-to-server packets and admin/debug commands;
7. verify legacy `zcity` persistence migration and new `trauma` writes;
8. compare profiler/network/error output against the repository baseline.

## Next action

Generate the complete repository-versus-archive path/hash delta, then use it to define subsystem import packages. Until that delta exists, no statement that the archive is “integrated” or “newer everywhere” is justified.
