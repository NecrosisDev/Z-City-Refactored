# Bootstrap and Load Order

**Repository:** `NecrosisDev/Z-City-Refactored`  
**Source commit:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** Initial verified trace

## Scope

This document describes the two independent loading systems that assemble Z-City at runtime:

1. the global addon loader under `lua/autorun/loader.lua`;
2. the Z-City gamemode loader under `gamemodes/zcity/gamemode/loader.lua`.

These loaders do not use identical filename rules or recursion order. Code should not be moved between their trees without re-evaluating realm and dependency behavior.

## Startup overview

```text
Garry's Mod starts
├─ autorun discovers lua/autorun/loader.lua
│  ├─ initialize hg
│  ├─ load lua/homigrad/
│  ├─ set hg.loaded
│  └─ run HomigradRun
│
├─ selected gamemode starts
│  ├─ server: gamemode/init.lua
│  ├─ client: gamemode/cl_init.lua
│  ├─ both include shared.lua
│  └─ both include gamemode/loader.lua
│     ├─ load gamemode/libraries/
│     └─ assemble gamemode/modes/
│
└─ InitPostEntity
   └─ global loader loads lua/initpost/
```

The exact interleaving of global addon initialization and gamemode initialization should be validated in a runtime trace. The source establishes each local sequence but does not itself provide a single global ordering contract for all engine callbacks.

## Global addon loader

**Path:** `lua/autorun/loader.lua`

### Namespace initialization

The loader initializes or reuses:

```lua
hg = hg or {}
```

It records the release string and repository identity, then creates the replicated/archive `hg_loadcontent` convar. Workshop mounting calls are currently commented out.

### Realm detection

The loader checks both a three-character filename prefix and a three-character suffix before `.lua`.

| Filename pattern | Realm behavior |
|---|---|
| `sv_*.lua`, `*_sv.lua` | Included on server only |
| `sh_*.lua`, `*_sh.lua` | Sent by server and included on both realms |
| `cl_*.lua`, `*_cl.lua` | Sent by server and included on client only |
| No recognized marker | Sent and included as shared code |

Examples:

```text
sv_damage.lua       -> server
sh_damage.lua       -> shared
cl_damage.lua       -> client
damage_sv.lua       -> server
damage_sh.lua       -> shared
damage_cl.lua       -> client
damage.lua          -> shared by default
```

The default is important: an unmarked file under the recursively loaded addon tree executes on both server and client.

### Recursive traversal

The global `IncludeDir` function performs this order for each directory:

1. retrieve files and child directories with `file.Find`;
2. iterate current-directory files;
3. include each `.lua` file through realm routing;
4. recurse into child directories.

```text
Directory
├─ files first
└─ child directories second
```

The loader does not call `table.sort`. A dependency on alphabetical or otherwise stable enumeration is therefore implicit rather than enforced by this source.

### Main run phase

The main run function:

1. logs the start time;
2. sets `hg.loaded = false`;
3. exits early for active gamemode `ixhl2rp`;
4. recursively loads `homigrad`;
5. sets `hg.loaded = true`;
6. prints elapsed time;
7. runs `hook.Run("HomigradRun")`.

It is invoked immediately from the autorun file.

### Post-entity phase

The loader registers an `InitPostEntity` hook that:

1. marks local post-initialization state;
2. recursively loads `initpost`;
3. prints a loading message.

Code under `lua/initpost/` must therefore be treated as a later initialization phase.

### Operational checks

Five seconds after startup, the loader warns when:

- `ulx` is not a table, indicating ULX/ULib is unavailable;
- the game is running in single-player.

These warnings indicate expected operating conditions, but they do not prove every feature strictly requires ULX/ULib or multiplayer. Dependency behavior must be traced per subsystem.

## Gamemode entry points

### Server

**Path:** `gamemodes/zcity/gamemode/init.lua`

The server sends and includes the shared/client bootstrap files:

```text
AddCSLuaFile(cl_init.lua)
AddCSLuaFile(shared.lua)
include(shared.lua)
AddCSLuaFile(loader.lua)
include(loader.lua)
```

Substantial server behavior is also defined directly in `init.lua`, including spawning and spectator handling. It is therefore more than a minimal bootstrap file.

### Client

**Path:** `gamemodes/zcity/gamemode/cl_init.lua`

The client begins with:

```text
include(shared.lua)
include(loader.lua)
```

It then defines extensive client behavior, including round synchronization, spectator camera handling, HUD, fonts, menus, and presentation code.

### Shared setup

**Path:** `gamemodes/zcity/gamemode/shared.lua`

The shared layer:

- initializes `zb` and `hg` when needed;
- derives from Sandbox;
- defines teams;
- applies Sandbox spawn and noclip restrictions;
- provides alive/player/team collection helpers.

Because `shared.lua` runs before the gamemode loader on both realms, any globals or helpers required by loader code must be established here or by the already-running global addon layer.

## Gamemode loader

**Path:** `gamemodes/zcity/gamemode/loader.lua`

### Realm routing

The gamemode loader uses substring checks rather than the global loader's exact three-character prefix/suffix map.

| Match | Behavior |
|---|---|
| filename contains `sv_` | Included by server |
| filename is/contains `shared.lua` or contains `sh_` | Sent and included as shared |
| filename contains `cl_` | Sent by server and included by client |
| no match | Not included by `IncluderFunc` |

Consequences:

- unmarked files are not shared by default here;
- matching is not constrained to the beginning or end of a filename;
- naming conventions differ materially from the global addon loader.

### Recursive traversal

`LoadFromDir` performs this order:

1. retrieve files and folders;
2. recurse through child folders;
3. include files in the current folder.

```text
Directory
├─ child directories first
└─ current files second
```

This is the reverse of the global addon loader.

The code comment explicitly calls attention to files inside folders loading first. However, sibling file and directory ordering is still not explicitly sorted.

### Library phase

The loader first executes:

```lua
LoadFromDir("zcity/gamemode/libraries")
```

Only after libraries load does it initialize mode registries and assemble modes. Gamemode libraries are therefore intended to provide the infrastructure required by mode definitions.

### Mode registry initialization

The loader establishes:

```lua
zb.modesHooks = {}
zb.modes = zb.modes or {}
```

`zb.modes` may survive hot loading, while `zb.modesHooks` is reset. Individual modes preserve a `saved` table when reinitialized.

### Mode assembly

For each top-level mode file or folder, the loader performs:

```text
MODE = {}
├─ include the mode file(s)
├─ validate/finalize MODE
├─ store MODE in zb.modes
├─ register functions through mode-hook dispatch
└─ MODE = nil
```

A mode must assign `MODE.name`. If the table is empty, finalization returns without registration.

### Inheritance

When `MODE.base` is present, the loader calls:

```lua
table.Inherit(MODE, zb.modes[MODE.base])
```

It then copies nested tables and optionally calls:

```lua
MODE:AfterBaseInheritance()
```

The base mode must already exist in `zb.modes`. Since explicit dependency sorting is absent, inherited modes have a load-order dependency on enumeration or directory arrangement.

### Mode hook dispatch

For each function stored on a mode table, the loader calls its hook-registration helper. The helper installs a Garry's Mod hook that:

1. resolves the current mode from `zb.CROUND_MAIN`, `zb.CROUND`, or fallback `tdm`;
2. obtains the registered function for that mode and hook name;
3. invokes it with the mode table as the first argument;
4. forwards up to six non-`nil` return values.

This makes mode methods convenient but conflates:

- engine hook implementations;
- lifecycle methods;
- helper functions stored directly on `MODE`.

A later registry should determine which mode functions correspond to real engine or project hooks and which are internal helpers.

### Mode chance persistence

On the server, mode chance configuration is loaded from:

```text
data/zbattle/modeschances.json
```

The loader initializes missing values from `MODE.Chance`, writes initial data when absent, saves on shutdown, and exposes admin console commands for inspecting and changing values.

## Round-system startup

**Primary path:** `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`

The round system is loaded during the gamemode library phase, before mode assembly.

It provides:

- `CurrentRound()` and `NextRound()`;
- round pre-start, active, and end-state processing;
- mode availability and weighted selection;
- round synchronization through `RoundInfo`;
- timing synchronization;
- player reset, respawn, balancing, and equipment handoff.

### Observed round states

| State | Runtime meaning |
|---:|---|
| `0` | pre-round/intermission |
| `1` | active round |
| `3` | end-round period |

Comments elsewhere state that `2` is the end state. Runtime code uses `3`; documentation should follow verified behavior and retain the mismatch as technical debt.

### Initial current mode

Server-side current-mode resolution defaults `zb.CROUND` to `hmcd` unless map/changelevel handling forces `coop`. The mode name may represent a submode/type and be mapped back to its parent registry entry.

Client-side `CurrentRound()` is simpler and directly indexes `zb.modes[zb.CROUND]`. The server and client therefore do not implement identical lookup behavior.

## Load-order invariants currently relied upon

The code appears to rely on these conditions:

1. the global addon layer initializes enough of `hg` before gamemode code consumes it;
2. gamemode `shared.lua` runs before gamemode libraries and modes;
3. gamemode libraries run before mode definitions;
4. base modes register before derived modes;
5. realm filenames match the correct loader's convention;
6. deferred UI/post-entity code does not run before `InitPostEntity`;
7. hot loads preserve only the state intentionally retained in global tables.

Not all of these invariants are explicitly enforced.

## Refactoring constraints

Until the loaders are replaced or hardened:

- do not rename realm files without checking the loader that owns their path;
- do not move files between `lua/homigrad`, `lua/initpost`, gamemode libraries, and mode folders without re-tracing initialization;
- do not assume alphabetical order unless sorting is added;
- do not add a mode inheritance relationship without guaranteeing base registration first;
- do not place server-sensitive logic in an unmarked global-addon file;
- do not treat `cl_init.lua` or `init.lua` as pure entry points;
- preserve `HomigradRun` and `InitPostEntity` phase expectations until consumers are inventoried.

## Required next verification

A generated bootstrap manifest should record, for every loaded Lua file:

- path;
- owning loader;
- effective realm;
- initialization phase;
- observed order;
- globals defined or mutated;
- hooks registered;
- network strings registered;
- convars and commands registered;
- direct include and API dependencies;
- hot-load behavior.

That manifest should become the authoritative basis for splitting monolithic systems and replacing implicit load order with explicit module registration.
