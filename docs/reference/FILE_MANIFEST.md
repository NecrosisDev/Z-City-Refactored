# Loaded-File and Effective-Realm Manifest

**Work package:** `WP-RESEARCH-001`  
**Research branch:** `docs/architecture-baseline`  
**Runtime source baseline:** commit `429ec928203cec963176dfb6afd086dcdd01c181` (runtime Lua unchanged on this branch)  
**Status:** `partial / static-source verified`  
**Last reviewed:** 2026-07-12

## Purpose

This manifest records which repository trees participate in runtime loading, the effective realm rules that apply, known entry files, and unresolved enumeration gaps. It is not a simple repository tree: files that exist but are not loaded, are loaded by the engine outside these loaders, or are data/assets/binaries are separated explicitly.

## Initialization roots

| Phase | Root/entry | Invoked by | Effective realm | Local order | Evidence |
|---|---|---|---|---|---|
| Global autorun | `lua/autorun/loader.lua` | Garry's Mod autorun | shared execution with server/client guards | immediate `Run()` | source blob `c250ed...` |
| Global main tree | `lua/homigrad/` | global `IncludeDir("homigrad")` | per `SYS-BOOTSTRAP-GLOBAL` filename rule | files in directory, then child directories; siblings unsorted | `loader.lua:AddFile/IncludeDir` |
| Global post-entity tree | `lua/initpost/` | `InitPostEntity` hook `zcity` | same global filename rule | files in directory, then child directories; siblings unsorted | `loader.lua` |
| Gamemode server entry | `gamemodes/zcity/gamemode/init.lua` | selected gamemode server bootstrap | server | sends `cl_init.lua`, `shared.lua`, `loader.lua`; includes shared then loader | source blob `d001d9...` |
| Gamemode client entry | `gamemodes/zcity/gamemode/cl_init.lua` | selected gamemode client bootstrap | client | includes shared then loader | source blob `fa6181...` |
| Gamemode shared entry | `gamemodes/zcity/gamemode/shared.lua` | included by both entry files | shared, but contains client-only guarded sections and unguarded rendering calls | before gamemode loader | source blob `017552...` |
| Gamemode libraries | `gamemodes/zcity/gamemode/libraries/` | `LoadFromDir` | per substring rule | child directories first, then current files; siblings unsorted | loader blob `b1754d...` |
| Gamemode modes | `gamemodes/zcity/gamemode/modes/` | `LoadModes` | per substring rule | top-level files first, then top-level folders; each folder child-first | loader blob `b1754d...` |

## Realm classification contracts

### Global addon loader

A Lua filename is classified using the first three characters and the last three characters before `.lua`.

| Marker | Effective behavior |
|---|---|
| `sv_*.lua` or `*_sv.lua` | included on server only |
| `sh_*.lua` or `*_sh.lua` | sent by server and included on server/client |
| `cl_*.lua` or `*_cl.lua` | sent by server; included on client only |
| no recognized exact marker | sent by server and included on server/client |

**Critical invariant:** unmarked files under `lua/homigrad/` and `lua/initpost/` are shared by default.

### Gamemode loader

The gamemode loader searches the full path string for marker substrings.

| Substring | Effective behavior |
|---|---|
| contains `sv_` | included by server path; client execution depends on the server-only include path being absent clientside |
| contains `shared.lua` or `sh_` | sent by server and included on both realms |
| contains `cl_` | sent by server and included on client |
| no recognized substring | not included by `IncluderFunc` |

**Critical invariant:** unmarked files in gamemode library/mode trees are ignored rather than shared. A marker in a parent directory can also affect classification because the full path is searched.

## Verified gamemode entry files

| Path | Realm | Direct responsibilities established by source | Risks/notes |
|---|---|---|---|
| `gamemodes/zcity/gamemode/init.lua` | server | initializes `zb`/`hg`, default state, sends/includes bootstrap files, defines spawn/spectator/server behavior | not a minimal bootstrap; contains extensive runtime behavior; stale state comment names `2` as end |
| `gamemodes/zcity/gamemode/cl_init.lua` | client | initializes client round state, includes loader, receives round/time/spectator state, owns HUD/camera/menu/presentation logic | very large entry file; client state comment conflicts with executable state `3` |
| `gamemodes/zcity/gamemode/shared.lua` | shared | identifies/derives gamemode, defines teams, spawn/noclip/menu policy, team/alive helpers | unguarded `Material`, `surface`, and `render` references occur in a shared file; dedicated-server safety must be runtime-tested |
| `gamemodes/zcity/gamemode/loader.lua` | shared | routes libraries/modes, builds registries, dispatches mode hooks, persists chances server-side | unsorted order, substring realm detection, global `MODE` scratch state |

## Verified `lua/initpost/` top-level files

These paths were present in the reviewed repository tree and are classified by the global loader.

| Path | Effective realm | Phase |
|---|---|---|
| `lua/initpost/cl_atlases.lua` | client | after `InitPostEntity` |
| `lua/initpost/cl_derma_skin.lua` | client | after `InitPostEntity` |
| `lua/initpost/cl_derma_skin_hokmah.lua` | client | after `InitPostEntity` |
| `lua/initpost/sh_initpost.lua` | shared | after `InitPostEntity` |
| `lua/initpost/sv_initpost.lua` | server | after `InitPostEntity` |
| `lua/initpost/menu-n-derma/derma/**` | per individual filename | after `InitPostEntity`; child directory after root files under global traversal |

## Verified gamemode library paths

Top-level files below are classified directly by their filename. Directory internals require recursive enumeration.

| Path | Effective realm | Current known responsibility |
|---|---|---|
| `libraries/cl_modeselect_menu.lua` | client | mode selection/admin UI |
| `libraries/cl_scrappersfonts.lua` | client | font/presentation setup |
| `libraries/sh_giverole.lua` | shared | role assignment helpers |
| `libraries/sh_pluvis.lua` | shared | Pluv-related shared behavior |
| `libraries/sh_simplex.lua` | shared | simplex utility/noise functionality |
| `libraries/sh_ulxcommands.lua` | shared | ULX command integration; realm safety requires trace |
| `libraries/sv_admin_tools.lua` | server | admin tools |
| `libraries/sv_antiafk.lua` | server | anti-AFK behavior |
| `libraries/sv_lootspawn.lua` | server | loot spawning |
| `libraries/sv_roundsystem.lua` | server | `SYS-ROUND-LIFECYCLE` |
| `libraries/sv_teamsetup.lua` | server | team setup/balancing |
| `libraries/!core/**` | per individual path substring | core gamemode library phase; loads before top-level library files because traversal is child-first |
| `libraries/experience/**` | per individual path substring | experience system |
| `libraries/guilt/**` | per individual path substring | guilt system |
| `libraries/mappoints/**` | per individual path substring | map-point definitions/storage |
| `libraries/rtv/**` | per individual path substring | map voting/RTV |

## Verified mode directories

Directory presence is verified; registration, exact files, base relationships, realm parity, reachability, and stability are not yet complete.

```text
coop
criresp
defense
dm
eventhandler
gwars
hl2dm
homicide
homicide_fear
pathowogen
riot
scugarena
sfd
tdm
tdm_cstrike
```

Expected convention is `cl_<mode>.lua`, `sh_<mode>.lua`, and `sv_<mode>.lua`, but each directory must be enumerated and traced rather than assumed to follow the convention.

## Global addon runtime tree boundaries

The global loader recursively includes all Lua files beneath `lua/homigrad/`. These verified top-level directories form the current subsystem discovery queue:

```text
abnormalty_detection
achievements
adminsystem
admintools
clothes
dynamic_anims_util
dynamic_music_v2
dynmusic
explosives
fake
gunposmenu
headgib
hud
libraries
liquidystuff
movement
new_appearance
new_inventory
optionsmenu
organism
pathowogen
phys_bullets
phys_silk
playerclass
playermodel_selector
pluvtown
roleplus
synthesizer
z_box_systems
zchat
zmanip
```

Because unmarked files are shared, every individual file must be classified for client exposure, server-only API use, and load-order dependency. Directory names are not realm boundaries.

## Engine-loaded and non-loader trees

The following repository trees exist outside the two recursive loader roots and require separate engine/content registration rules:

| Tree | Loading model / status |
|---|---|
| `lua/entities/` | Garry's Mod scripted-entity discovery; bases and concrete classes require class manifest |
| `lua/weapons/` | Garry's Mod SWEP discovery; bases and concrete weapons require class manifest |
| `gamemodes/zcity/entities/` | gamemode-scoped entity tree; exact discovery/override behavior requires trace |
| `lua/effects/` | Garry's Mod effect registration/discovery |
| `lua/includes/modules/` | modules loaded through explicit `require`/include consumers; inventory pending |
| `lua/bin/` | compiled server modules; contains `gmsv_eightbit_*` binaries |
| `lua/glide/` | bundled/adapted Glide code; loader ownership pending |
| `lua/wos/dynabase/` | bundled wOS DynaBase code; loader ownership pending |
| `data_static/glide/` | packaged static data, not writable `DATA` persistence |
| source-attribution `*_source.txt` files | documentation/provenance only; not Lua-loaded |

## Current manifest gaps

1. Full recursive path list for `lua/homigrad`, `lua/initpost`, gamemode libraries, and modes.
2. Detection of discovered Lua files that no loader includes.
3. Exact server/client/shared include sequence under real `file.Find` enumeration.
4. Engine-discovered SWEP, SENT, effect, and gamemode entity class lists.
5. Explicit `include`, `AddCSLuaFile`, `require`, `resource.Add*`, and dynamic file-load calls outside the two loaders.
6. Duplicate class/global/hook registration and hotload behavior.
7. Files containing server-sensitive logic that are shared or client-delivered.

## Runtime validation design

The least invasive complete validation is a temporary development-only trace wrapper, not a permanent runtime subsystem:

1. wrap/log `include` and `AddCSLuaFile` before project startup;
2. record monotonic sequence, path, realm, caller source, engine phase, and success/error;
3. snapshot registered hooks, net strings where inspectable, convars, commands, SWEPs, SENTs, and globals after `HomigradRun`, gamemode load, and `InitPostEntity`;
4. compare dedicated-server and client manifests;
5. remove or disable instrumentation after producing a versioned evidence artifact.

Expected output should identify every discovered path as `executed server`, `executed client`, `sent client`, `not loaded`, `engine discovered`, or `unknown`, plus first/last load order and duplicate count.

## Next trace

Enumerate every file under the two loader roots and each mode directory, then replace directory-level entries above with exact path rows. In parallel, trace explicit loading calls outside the recursive loaders so the final manifest covers runtime reality rather than only loader-owned code.