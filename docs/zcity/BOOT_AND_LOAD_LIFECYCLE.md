# Z-City Boot and Load Lifecycle

## Scope

This document records the verified startup behavior of the current `main` branch. It is a description of executable behavior, not an endorsement of the architecture.

Primary sources:

- `lua/autorun/loader.lua`
- `gamemodes/zcity/gamemode/init.lua`
- `gamemodes/zcity/gamemode/cl_init.lua`
- `gamemodes/zcity/gamemode/shared.lua`
- `gamemodes/zcity/gamemode/loader.lua`

## Project identity

**Evidence level: Verified**

The addon bootstrap initializes the global `hg` namespace and identifies itself as Z-City release 1.4.1. Repository metadata still points to the upstream `uzelezz123/Z-City` project rather than this fork.

The gamemode identifies itself as `ZCity`, derives from Sandbox, and initializes three numbered teams.

### Compatibility consequence

The names `hg`, `zb`, `HomigradRun`, and the `homigrad` source directory are active compatibility surfaces. They cannot be removed safely until all internal and external callers are inventoried.

## Addon bootstrap

**Evidence level: Verified**

`lua/autorun/loader.lua` executes independently of the ZCity gamemode. Its startup sequence is:

1. Initialize `hg` and project metadata.
2. Create the replicated `hg_loadcontent` ConVar.
3. Define filename-based realm detection.
4. Recursively include the entire `lua/homigrad` tree.
5. Set `hg.loaded = true`.
6. emit `HomigradRun`.
7. Register an `InitPostEntity` hook which recursively includes `lua/initpost`.
8. Warn after five seconds when ULX/ULib is missing or the game is running in single-player.

### Realm inference

Recognized filename markers are:

- Prefix `sv_` or suffix `_sv`
- Prefix `sh_` or suffix `_sh`
- Prefix `cl_` or suffix `_cl`

Unrecognized Lua filenames default to shared behavior:

- Sent to clients by the server.
- Included on the server.
- Included on clients.

### Risks

- A misnamed server file can be delivered to clients.
- A misnamed client file can execute server-side.
- Realm ownership is implicit and filename-dependent.
- Recursive inclusion has no manifest, dependency graph, failure isolation, or subsystem boundary.
- Load order is inherited from `file.Find` traversal rather than declared dependencies.
- `include()` failures can leave a partially initialized global namespace.

## Deferred `initpost` bundle

**Evidence level: Verified**

The current loader includes `lua/initpost` only when `InitPostEntity` fires. There is no late-load fallback in the current repository implementation.

### Contract

Files under `lua/initpost` implicitly depend on map entities and ordinary addon bootstrap already being available.

### Risks

- Lua refresh or late addon mounting after `InitPostEntity` may leave the deferred bundle unloaded.
- The bundle has no explicit readiness state beyond side effects produced by included files.

## Gamemode server startup

**Evidence level: Verified**

`gamemodes/zcity/gamemode/init.lua` performs this sequence:

1. Initialize globals `zb` and `hg`.
2. Preserve or initialize `zb.ROUND_STATE`.
3. send `cl_init.lua` and `shared.lua` to clients.
4. include `shared.lua`.
5. send and include `loader.lua`.
6. Define server player, spawn, team, and other gamemode methods after the loader returns.

### Important ordering contract

The mode library and all mode definitions are loaded before much of `init.lua` has finished defining server methods.

A mode file that performs startup work immediately can therefore observe an incomplete gamemode API. The ordinary mode-dispatch pattern masks some of this because mode methods are usually invoked later, but direct registration and initialization side effects are vulnerable.

## Gamemode client startup

**Evidence level: Verified**

`cl_init.lua` performs this sequence:

1. Initialize `zb`.
2. include `shared.lua`.
3. include `loader.lua`.
4. Define the client version of `CurrentRound()`.
5. Initialize client round state and networking receivers.
6. Register client HUD, spectator, and input behavior.

Client and server therefore load the same mode definitions through separate startup paths.

## Shared gamemode initialization

**Evidence level: Verified**

`shared.lua`:

- Defines gamemode identity.
- Derives from Sandbox.
- Configures teams.
- Defines shared UI helpers.
- Blocks ordinary spawnmenu actions for non-admins.
- Restricts noclip.
- Defines shared team/alive-player queries.

### Architectural issue

Core gamemode identity, permission policy, UI rendering, and team-query helpers are combined in one file. These responsibilities should be documented separately before they are split.

## Gamemode library loader

**Evidence level: Verified**

`gamemodes/zcity/gamemode/loader.lua` loads all files beneath `zcity/gamemode/libraries`, then loads all mode files and folders beneath `zcity/gamemode/modes`.

### Realm inference

Realm is inferred by substring search across the entire path:

- Any path containing `sv_` is included in the executing realm.
- Paths containing `shared.lua` or `sh_` are shared.
- Paths containing `cl_` are clientside.

### Risks

- The check is not anchored to the filename.
- A directory name containing a realm marker can affect all descendant files.
- A file with no recognized marker is silently ignored by this loader.
- Server-only detection does not itself guard with `SERVER`; correctness depends on this loader being invoked from the server startup path.

## Library ordering

**Evidence level: Verified**

The current loader recursively processes child folders before files in the current folder. It does not explicitly sort the returned file or folder lists.

This creates two implicit contracts:

1. Nested libraries initialize before their parent-directory files.
2. Relative ordering between sibling files and folders depends on engine-provided `file.Find` order.

Numeric filename prefixes may appear to define priority, but the current loader does not explicitly enforce sorting.

## Mode registration

**Evidence level: Verified**

Each mode is loaded through the global temporary table `MODE`.

Registration performs the following actions:

1. Create an empty global `MODE` table.
2. include a mode file or recursively include a mode folder.
3. ignore an empty `MODE`.
4. preserve the old mode's `saved` table across reload.
5. inherit from `MODE.base` when declared.
6. copy nested tables that overlap with the base mode.
7. invoke `AfterBaseInheritance` when present.
8. store the mode in `zb.modes`.
9. initialize server mode chance data.
10. register every function on the mode table as a shared dispatcher hook.
11. clear the global `MODE` reference.

### Mode hook dispatch

For each function key found on any mode table, the loader creates or replaces one global hook named:

`zb_modehook_<hook name>`

At runtime, the dispatcher:

1. resolves the active mode from `zb.CROUND_MAIN`, then `zb.CROUND`, then `tdm`.
2. looks up the active mode's function for that hook name.
3. calls it with the active mode table as the first argument.
4. propagates up to six return values when the first is not `nil`.

### Useful property

Only one dispatcher exists per hook name, so inactive mode-table methods are not all registered as independent Garry's Mod hooks.

### Limitations

- Direct `hook.Add` and `timer.Create` calls inside mode files remain globally active regardless of selected mode.
- The global `MODE` table is mutable shared bootstrap state.
- Base mode availability depends on load order.
- Inheritance uses shallow framework behavior followed by selective nested-table copying; aliasing risk remains for nested data not covered by the copy loop.
- The copy loop in the current implementation assigns `tbl2` without `local`, leaking it globally.
- Hot reload preserves `saved`, but does not provide complete ownership cleanup for direct hooks, timers, network receivers, or other registrations.

## Round resolution interaction

**Evidence level: Verified**

The server `CurrentRound()` function:

- Forces Cooperative mode when a `trigger_changelevel` entity exists.
- Defaults `zb.CROUND` to `hmcd`.
- Resolves aliases through `zb:GetMode()` only when the requested round changes.
- Returns the resolved mode table and requested round key.

The current implementation calls `ents.FindByClass("trigger_changelevel")` whenever `CurrentRound()` or `NextRound()` evaluates the map override. Because `CurrentRound()` is used broadly, this is a repeated entity scan in a hot path.

## External dependencies

**Evidence level: Verified**

### ULX/ULib

The addon warns repeatedly when `ulx` is not a table. Startup continues. The loader does not describe which features become unavailable.

Classification: **soft dependency with undocumented failure surface**.

### Workshop content

`hg_loadcontent` exists and defaults to enabled, but every `resource.AddWorkshop` call in its guarded block is commented out.

Classification: **nonfunctional configuration surface**.

## Confirmed problems

1. Recursive, implicit addon loading.
2. Unsafe shared fallback for unknown addon filenames.
3. Unsorted library and mode traversal.
4. Substring-based gamemode realm classification.
5. Modes load before server gamemode API construction is complete.
6. Direct mode hooks and timers are not lifecycle-owned.
7. Global temporary `MODE` registration state.
8. Global `tbl2` leak during mode inheritance.
9. Repeated `trigger_changelevel` entity scans in round lookup.
10. Misleading Workshop content ConVar.
11. Upstream repository identity remains embedded in the fork.
12. Dependency failures are warned about but not represented as capabilities.

## Preserve during refactor

The following are behavioral contracts until deeper subsystem verification says otherwise:

- `hg` and `zb` remain available.
- `HomigradRun` still fires after addon bootstrap.
- Existing mode method dispatch and return propagation remain compatible.
- Client and server receive the same shared mode definitions.
- Mode `saved` data survives Lua refresh where currently expected.
- Cooperative map forcing remains behaviorally equivalent.
- Existing spawn, round, and permission behavior is not changed merely to reorganize files.

## Next verification work

- Enumerate every library and mode file in actual load order.
- Identify all mode files that register direct hooks, timers, receivers, commands, or global callbacks.
- Map `ROUND_STATE` transitions and every call site of `CurrentRound()`.
- Verify player spawn/death/fake-ragdoll behavior across each transition.
- Separate required from optional ULX use.
- Establish a manifest format that can coexist with legacy recursive loading during migration.