# Local Archive File and Comparison Manifest

**Status:** `partial comparison / complete local archive inventory`  
**Repository baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Archive SHA-256:** `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652`  
**Generated:** 2026-07-12

## Purpose

This document provides an exact file/hash inventory for the uploaded local archive and a bounded comparison against the pinned clean repository baseline. It is evidence for decomposition and port planning; it is not permission to copy the archive into the repository.

## Local archive inventory

- Files: **1,040**
- Uncompressed bytes: **12,707,995**
- Lua files: **1,028**
- Gamemode-tree files: **226**
- Global Lua-tree files: **814**
- Exact duplicate-content groups: **2** covering **12** files

The complete 1,040-row CSV is reproducible from the pinned archive using [`tools/generate_local_archive_manifest.py`](tools/generate_local_archive_manifest.py). Its canonical SHA-256 is `28f6eca648b80d6eca1419ce3e30fc60d2971ab743457d23aeee9d5a261cd4b0`; reproduction instructions and evidence policy are recorded in [`local_archive_manifest/`](local_archive_manifest/README.md).

## Major path groups

| Path group | Files |
|---|---:|
| `lua/weapons/` | 262 |
| `lua/homigrad/` | 242 |
| `gamemodes/trauma/` | 226 |
| `lua/entities/` | 212 |
| `lua/effects/` | 45 |
| `lua/autorun/` | 24 |
| `lua/wos/` | 13 |
| `lua/initpost/` | 6 |
| `lua/bin/` | 3 |
| `lua/includes/` | 3 |
| `lua/glide_helicopters_source.txt` | 1 |
| `lua/glide_source.txt` | 1 |
| `lua/vfire_source.txt` | 1 |
| `lua/wos_source.txt` | 1 |

## Candidate-path rule

- `TMod/` is a deployment wrapper and is removed from manifest paths.
- `gamemodes/trauma/**` is compared to `gamemodes/zcity/**` only as a candidate lineage mapping; the name substitution does not establish semantic equivalence.
- All other paths retain their archive-relative names as candidate repository paths.

## Verified core-file comparison

Of **13** representative core files checked by exact Git blob identity, **2** are identical and **11** differ.

| Local archive path | Repository candidate | Result | Local blob | Repository blob |
|---|---|---|---|---|
| `lua/autorun/loader.lua` | `lua/autorun/loader.lua` | **modified/diverged** | `11954d4ce22e` | `c250ed9129cf` |
| `gamemodes/trauma/gamemode/init.lua` | `gamemodes/zcity/gamemode/init.lua` | **modified/diverged** | `18426b846215` | `d001d96d58b2` |
| `gamemodes/trauma/gamemode/shared.lua` | `gamemodes/zcity/gamemode/shared.lua` | **modified/diverged** | `3d98f7db2288` | `0175529057e5` |
| `gamemodes/trauma/gamemode/cl_init.lua` | `gamemodes/zcity/gamemode/cl_init.lua` | **modified/diverged** | `7926764f352b` | `fa61811ef802` |
| `gamemodes/trauma/gamemode/loader.lua` | `gamemodes/zcity/gamemode/loader.lua` | **modified/diverged** | `19f07aec838e` | `b1754dff2d53` |
| `gamemodes/trauma/gamemode/libraries/sv_roundsystem.lua` | `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua` | **modified/diverged** | `16a4db3d1adf` | `324491c8ad47` |
| `lua/homigrad/fake/sv_control.lua` | `lua/homigrad/fake/sv_control.lua` | **modified/diverged** | `05bbb5b936d6` | `22c87ad41487` |
| `lua/homigrad/movement/sh_movedata.lua` | `lua/homigrad/movement/sh_movedata.lua` | **identical** | `7ed222c0ac99` | `7ed222c0ac99` |
| `lua/homigrad/organism/tier_1/sv_organism.lua` | `lua/homigrad/organism/tier_1/sv_organism.lua` | **modified/diverged** | `f432a54b04c1` | `4830503722f0` |
| `lua/homigrad/playerclass/sh_tier_0.lua` | `lua/homigrad/playerclass/sh_tier_0.lua` | **modified/diverged** | `418994cdc108` | `0ce6ee8c9a48` |
| `lua/homigrad/admintools/sh_player_properties.lua` | `lua/homigrad/admintools/sh_player_properties.lua` | **modified/diverged** | `acf84ec4bd0f` | `08026cea71c1` |
| `lua/weapons/homigrad_base/shared.lua` | `lua/weapons/homigrad_base/shared.lua` | **modified/diverged** | `da7df808a8f7` | `a7e7b9ba40f5` |
| `lua/weapons/homigrad_base/sh_fake.lua` | `lua/weapons/homigrad_base/sh_fake.lua` | **identical** | `9cc447f9ab3f` | `9cc447f9ab3f` |

### Interpretation

- The archive is not a uniform rewrite: some baseline files remain byte-identical while adjacent foundational files have diverged.
- Bootstrap, gamemode entry, mode loading, round flow, fake control, organism, player-class, administration and primary weapon-base files in this sample have changed.
- `movement/sh_movedata.lua` and `homigrad_base/sh_fake.lua` remain identical in the checked sample, so subsystem ownership cannot be inferred from directory-level labels alone.
- Integration work must classify individual files and features; folder-level replacement would overwrite both unchanged baseline code and unrelated experimental changes.

## Exact duplicate-content groups

### Group 1 — 10 files, SHA-256 `da481e468e913dbd4e3d5814b7c66d358d0b7a61da8028e0d0994f487fd73c2b`

- `lua/entities/ent_airdrop/cl_init.lua`
- `lua/entities/ent_hg_bugbait/cl_init.lua`
- `lua/entities/ent_hg_grenade_hl2grenade/cl_init.lua`
- `lua/entities/ent_hg_grenade_impact/cl_init.lua`
- `lua/entities/ent_hg_grenade_pipebomb/cl_init.lua`
- `lua/entities/ent_hg_jam/cl_init.lua`
- `lua/entities/ent_hg_motiontracker/cl_init.lua`
- `lua/entities/ent_hg_smokenade/cl_init.lua`
- `lua/entities/ent_hg_snowball/cl_init.lua`
- `lua/entities/firework_base/cl_init.lua`

### Group 2 — 2 files, SHA-256 `e2552f7c5cbcedaf48e235015538354c48d3f6a0d9cd8158aa160c22c37ac6ca`

- `lua/entities/hg_brassknuckles/cl_init.lua`
- `lua/entities/hg_sling/cl_init.lua`

These groups appear to be standard lightweight entity client entry files, not automatically defects. They are recorded so future tooling does not misclassify identical boilerplate as independently authored implementations.

## Binary evidence

| Path | Bytes | SHA-256 |
|---|---:|---|
| `lua/bin/gmsv_eightbit_linux.dll` | 3,026,664 | `84f7de62519a268d4ff867d32b3691754fe077f59e63891f450abb6226b9c068` |
| `lua/bin/gmsv_eightbit_win32.dll` | 421,376 | `8f88fb0dea5166f37733d29920644887410aeacb5b20d989e42bdf17601231fe` |
| `lua/bin/gmsv_eightbit_win64.dll` | 579,584 | `7af360fdbdb6fd3efff473805ae89eefa8e47b9c3a7271b79943ae3e3cd8ae0f` |

The binaries remain unapproved dependencies until source, build reproducibility, ABI, license, necessity and supported-platform evidence are established.

## Comparison limitations

The GitHub connector exposes exact file fetches but not a recursive repository tree/archive download. Therefore the local side is complete, while the repository-side classification is currently limited to exact-path checks and existing code-grounded repository documentation.

No repository-wide counts of identical, modified, archive-only, repository-only or renamed files are claimed yet. Negative results must remain bounded until a recursive tree or repository archive is available to the audit environment.

## Next action

1. Obtain a recursive repository tree or source archive for commit `429ec928203cec963176dfb6afd086dcdd01c181`.
2. Regenerate the canonical CSV from the pinned archive and join it against the repository manifest using exact paths, the explicit Trauma-to-ZCity candidate mapping and content hashes.
3. Classify every row as identical, modified, archive-only, repository-only, rename candidate, generated, vendored dependency or excluded evidence.
4. Use that result to split the existing `PORT-*` inventory into subsystem-sized, reviewable implementation work packages.
