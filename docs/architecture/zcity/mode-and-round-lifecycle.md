# Z-City Mode and Round Lifecycle

**Status:** Observed from the current `main` implementation. Runtime verification is still required.

## Scope

This document describes how the current Z-City gamemode discovers modes, converts mode functions into hooks, selects the active mode, advances round state, and resets players. It is a behavior baseline, not an endorsement of the architecture.

Primary source paths:

- `gamemodes/zcity/gamemode/init.lua`
- `gamemodes/zcity/gamemode/cl_init.lua`
- `gamemodes/zcity/gamemode/shared.lua`
- `gamemodes/zcity/gamemode/loader.lua`
- `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`
- `gamemodes/zcity/gamemode/modes/**`

## 1. Gamemode bootstrap

### Server

`init.lua` performs the following high-level sequence:

1. Ensures `zb` and `hg` exist.
2. Initializes `zb.ROUND_STATE` to `0` when absent.
3. sends `cl_init.lua`, `shared.lua`, and `loader.lua` to clients;
4. includes `shared.lua`;
5. includes `loader.lua`;
6. defines server-only player, spawn, spectator, and gamemode behavior.

### Client

`cl_init.lua` includes `shared.lua` and `loader.lua`, then defines client round state, spectator state, round-time synchronization, and visual/UI behavior.

### Shared gamemode base

`shared.lua`:

- identifies the gamemode as ZCity;
- derives from Sandbox;
- establishes the base team definitions;
- controls spawn-menu and noclip access;
- exposes common team/alive-player queries.

This means Z-City is structurally a Sandbox-derived gamemode with a custom round layer rather than an isolated round engine.

## 2. Library loading

`loader.lua` loads `zcity/gamemode/libraries` recursively before loading modes.

Observed behavior:

- realm is inferred by substring checks for `sv_`, `sh_`, `shared.lua`, and `cl_`;
- subdirectories are loaded before files in each directory;
- there is no explicit dependency manifest;
- no protected include boundary is used;
- accidental names can affect realm classification;
- load order depends on file/directory enumeration plus the folders-first policy.

### Required invariant

Libraries required by mode files must already exist before mode discovery starts. This invariant is implicit and enforced through naming/directory placement rather than declared dependencies.

## 3. Mode discovery and registration

Modes are loaded from `zcity/gamemode/modes`.

For each top-level mode file or folder:

1. the global `MODE` variable is assigned a new table;
2. one file or a directory tree is included;
3. `InitMode()` processes the resulting table;
4. the table is assigned into `zb.modes[MODE.name]`;
5. `MODE` is cleared.

### Consequences of the global `MODE` capture model

- mode files rely on ambient mutable state;
- asynchronous work during loading cannot safely depend on `MODE`;
- a mode file that fails before cleanup may leave partial state;
- nested or reentrant mode loading is unsafe;
- tooling cannot identify ownership without reproducing loader context.

## 4. Mode inheritance

A mode can specify `MODE.base`.

The loader then:

1. calls `table.Inherit(MODE, zb.modes[MODE.base])`;
2. attempts to copy nested tables so child edits do not mutate the base;
3. invokes `MODE:AfterBaseInheritance()` when present.

Observed risks:

- the base must already have loaded, so inheritance depends on discovery order;
- missing bases are not handled as a structured dependency failure;
- nested copy behavior is implemented procedurally and requires runtime validation;
- inheritance combines data and executable callbacks in the same table;
- the implementation uses broad table iteration and mutable globals.

## 5. Mode functions become hook handlers

After registration, every function found directly in the mode table is passed to `addModeHook`.

`addModeHook` stores one callback per mode and hook name in `zb.modesHooks`, then registers a global dispatcher with an identifier based only on the hook/event name.

At runtime the dispatcher:

1. resolves `zb.CROUND_MAIN`, then `zb.CROUND`, then defaults to `tdm`;
2. finds the callback for the active mode and event;
3. calls it with the mode table as the first argument;
4. propagates up to six return values when the first is non-`nil`.

### Important behavior

A function name in a mode table is treated as though it were a Garry's Mod hook name. This is convenient but conflates:

- lifecycle methods such as `RoundStart`;
- utility methods such as `GetTeamSpawn`;
- true engine hook handlers;
- internal methods that were never intended to become global dispatch targets.

The current dispatcher normally prevents inactive mode callbacks from running, but registrations and global side effects performed directly by mode files remain global.

## 6. Mode chance persistence

Server-side mode chances are read from and written to:

`data/zbattle/modeschances.json`

The loader exposes administrative console commands to inspect, modify, and save chance values. Administrative checks are present in the current repository implementation.

Persistence occurs on explicit save and on `ShutDown`.

Risks:

- storage is coupled directly to the loader;
- validation is minimal;
- unknown/stale mode keys can survive in the file;
- writes are not transactional;
- a malformed or partial file falls back to an empty table without a structured diagnostic.

## 7. Active-mode resolution

`CurrentRound()` is the central compatibility function.

Observed behavior:

- maps containing `trigger_changelevel` are forced toward `coop`;
- `zb.CROUND` defaults to `hmcd`;
- `zb:GetMode(zb.CROUND)` resolves a base mode or a type/submode alias;
- the resolved key is cached in `zb.CROUND_MAIN`;
- the function returns both the resolved mode table and the original round/type key.

`NextRound(round)` writes `zb.nextround`, except that changelevel maps force `coop`.

### Required compatibility invariant

Many systems call global `CurrentRound()` directly. Replacing the round engine must preserve this call surface until all consumers are migrated.

## 8. Round states

The code initializes and uses these effective states:

| Value | Observed meaning |
|---:|---|
| `0` | intermission / players may join / waiting to start |
| `1` | active round |
| `3` | round ended / end delay before next intermission |

Comments in `init.lua` and `cl_init.lua` describe `2` as the end state, but the server round system uses `3`. This is a documentation and contract defect. Consumers must be audited before defining a replacement enum.

## 9. Round polling

A global `Think` hook calls `zb:Think(CurTime())`.

`zb:Think` throttles itself to roughly once per second and calls:

1. `PreRound()`;
2. `RoundThink()`;
3. `EndRoundThink()`.

This means round timing is polling-based rather than driven by a single state-machine scheduler.

## 10. Intermission and round start

During state `0`, `PreRound()`:

- may start RTV according to round count, player count, current state, and mode-specific exceptions;
- initializes `zb.START_TIME` from the mode's `start_time`;
- calls `zb:RoundStart()` when the start time expires.

The full `RoundStart()` behavior must be documented separately from the remainder of `sv_roundsystem.lua`, but the surrounding contract is clear: mode selection, player reset, equipment, and timing all converge at this transition.

## 11. Active round

During state `1`:

- `RoundThink()` delegates to `CurrentRound():RoundThink(...)` when available;
- `ShouldRoundEnd()` asks the mode whether the round should end;
- a global boring-round timeout can end the round unless the mode explicitly returns `false`;
- an optional `BoringRoundFunction` is called before timeout termination.

The distinction between `nil`, `true`, and `false` is behaviorally significant:

- `false` suppresses the global timeout path;
- truthy values can end immediately;
- `nil` permits timeout-based termination.

## 12. End transition

`zb:EndRound()`:

1. sets state `3`;
2. increments round count;
3. broadcasts `RoundInfo`;
4. calls the mode's `EndRound()`;
5. runs `ZB_EndRound`;
6. triggers the global fade;
7. saves achievements.

During state `3`, `EndRoundThink()`:

- computes `zb.END_TIME` from the mode's `end_time`;
- applies a special first-coop-round delay;
- fades players near the transition;
- returns the state to `0` after the delay;
- runs `ZB_PreRoundStart` and the compatibility hook `TTTPrepareRound`;
- selects `zb.nextround` or `hmcd`;
- optionally freezes players;
- broadcasts new round information;
- updates round-time synchronization;
- resets players;
- auto-balances;
- clears mode `saved` state;
- calls mode `Intermission()` and `GiveEquipment()`.

### Coupling found at the transition

The round system directly references:

- StormFox/TTT compatibility behavior;
- achievements;
- PluvTown state;
- organism reset;
- fake-ragdoll recovery;
- experience grants;
- player classes;
- team balancing;
- networking and screen fades.

A clean refactor must extract these into ordered transition participants without changing their effective order until tests prove a safe change.

## 13. Player reset behavior

`zb:KillPlayers()` iterates active non-spectators.

Observed behavior includes:

- experience grant;
- mode-specific `DontKillPlayer` escape path;
- organism clear and forced fake-up for preserved players;
- flashlight shutdown;
- silent kill;
- respawn;
- player-class assignment.

This is not merely a kill operation. It is a broad round-reset transaction and must be renamed or wrapped accordingly in the future architecture.

## 14. Networking

Known round-related channels include:

- `RoundInfo` — current mode name and round state;
- `updtime` — round duration/start/begin timestamps;
- `FadeScreen` — global fade request;
- `ZB_SpectatePlayer` — spectator target/mode state.

The client initializes local round fields independently and then updates them from the server. Joining players receive `RoundInfo` during `PlayerInitialSpawn`.

Required future work:

- define exact payload schemas;
- define authoritative sender and receiver realm;
- identify duplicate declarations;
- establish rate and trust boundaries;
- ensure late joiners receive a complete snapshot, not only partial state.

## 15. Verified architectural problems

1. Mode ownership is implicit.
2. Load order is implicit and inheritance-order-sensitive.
3. Global `MODE` capture is fragile.
4. Function discovery conflates methods and hooks.
5. Round states are inconsistently documented.
6. The round transition directly invokes unrelated subsystems.
7. Persistent state and runtime loading are coupled.
8. Errors can leave partial registrations.
9. Cleanup ownership for hooks and timers created by mode files is absent.
10. Compatibility globals are widespread and cannot be removed abruptly.

## 16. Behavior that must be preserved during refactor

- `CurrentRound()` compatibility and alias resolution;
- `zb.CROUND` versus `zb.CROUND_MAIN` distinction;
- coop override on changelevel maps;
- mode inheritance semantics where used;
- active-mode-only hook dispatch;
- meaningful `nil` versus `false` round-end behavior;
- transition hook order;
- late-join round information;
- player reset ordering;
- mode chance persistence and administrative access;
- Sandbox derivation and admin spawn-menu expectations.

## 17. Required runtime tests

Before replacing this system, build tests for:

1. cold boot on server and client;
2. hot reload of libraries and modes;
3. each effective round-state transition;
4. alias/submode resolution;
5. base-mode inheritance;
6. `ShouldRoundEnd` return semantics;
7. transition hook order;
8. player reset order and spectator exclusion;
9. late join during every state;
10. map cleanup and changelevel-map coop behavior;
11. missing/malformed chance storage;
12. mode errors during load, start, think, and end.

## 18. Refactor boundary

The first implementation target is not a new round engine. It is an observational compatibility layer that can:

- register explicit mode metadata;
- record hook/timer ownership without intercepting global APIs;
- emit lifecycle diagnostics;
- compare observed transition order against this baseline;
- keep the existing round implementation authoritative until parity tests pass.
