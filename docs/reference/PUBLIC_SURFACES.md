# Public Surfaces Inventory

**Work package:** `WP-RESEARCH-001`  
**Scope:** bootstrap, gamemode entry, mode registry, round lifecycle, and mode-selection UI  
**Status:** `partial / executable-source verified`  
**Runtime source baseline:** commit `429ec928203cec963176dfb6afd086dcdd01c181`  
**Reviewed:** 2026-07-12

## Purpose

This file inventories cross-file contracts that are easy to break during refactoring: globals, hooks, network channels, convars, commands, and persistence paths. It records only surfaces found in the currently traced source; absence from this file does not mean a surface does not exist.

## Global namespaces and identifiers

| Surface | Owner/definition | Realm | Verified consumers/notes |
|---|---|---|---|
| `hg` | `lua/autorun/loader.lua` reuses/creates table | server + client local copies | global addon APIs; gamemode entry reuses it |
| `hg.Version` | global loader | server + client | currently `Release 1.4.1`; root README states `1.4.0` |
| `hg.loaded` | global loader | server + client | false during load, true before `HomigradRun`; remains false on `ixhl2rp` early return |
| `zb` | gamemode entry/shared libraries | server + client local copies | mode registry, round state, map points, teams, admin UI |
| `zb.modes` | gamemode loader | server + client | `modeName -> TYPE-MODE-TABLE` |
| `zb.modesHooks` | gamemode loader | server + client | `modeName -> hookName -> function`; reset on loader execution |
| `MODE` | gamemode loader + mode files | temporary shared global scratch state | created per mode, finalized, then set `nil`; unsafe for concurrent/reentrant assembly |
| `GM` | Garry's Mod gamemode table | shared entry | name/author metadata, Sandbox derivation, gamemode methods |
| `CurrentRound()` | server round library and separate client definition | realm-local global function | server resolves base/submode; client indexes `zb.modes[zb.CROUND]` |
| `NextRound(round)` | server round library | server | writes `zb.nextround`, forces `coop` on changelevel maps |
| `COMMANDS` | pre-existing command registry | mainly server writers in traced code | `bigmap`, `setmode`, `setforcemode`, `endround`; owner/dispatcher not yet traced |
| `ZBATTLE_BIGMAP` | server round library | server | map-size threshold; writable through admin command and `data/zbattle/mapsizes.json` |
| `VFIRE_DISABLED` | server round start | server global | set true when current mode name is `coop`; downstream owner not yet traced |

## Hook surface

### Hooks emitted by traced code

| Hook | Emitter | When | Arguments/return contract |
|---|---|---|---|
| `HomigradRun` | global loader | after `lua/homigrad` include completes and `hg.loaded = true` | no explicit args |
| `ZB_PreRoundStart` | server round system | end-period timer transitions state `3 -> 0` | no explicit args |
| `TTTPrepareRound` | server round system | same transition as `ZB_PreRoundStart` | compatibility emission; no explicit args |
| `ZB_StartRound` | server round system | after mode `RoundStart`/next-mode selection | no explicit args |
| `ZB_EndRound` | server round system | after mode `EndRound` | no explicit args |
| `RoundInfoCalled` | client `RoundInfo` receiver | after mode string read, before assigning `zb.CROUND` | `modeName: string` |
| dynamic mode hook names | mode registry dispatcher | one dispatcher installed for every function key found on every mode | selected mode table as first callback argument; forwards up to six returns only if first is non-`nil` |

### Hooks consumed/registered by traced code

| Hook | Identifier | Owner/action |
|---|---|---|
| `InitPostEntity` | `zcity` | global loader loads `lua/initpost` |
| `InitPostEntity` | `loadbigmap` | server round system loads map threshold |
| `InitPostEntity` | `OwOmooooove` | server gamemode entry rebuilds spawn cache |
| `Think` | `zb-think` | server round lifecycle, throttled to once per second |
| `PlayerInitialSpawn` | `zb_SendRoundInfo` | sends current round state and sync vars |
| `PlayerInitialSpawn` | `ZB_SendModesOnSpawn` | sends admin mode/queue data after one second |
| `PlayerInitialSpawn` | `SendGameModesToClient` | sends admin mode display list; duplicated later in `sv_roundsystem.lua` with same identifier |
| `ShutDown` | `savechances` | persists mode chances JSON |
| `CanListenOthers` | `RoundStartChat` | allows broad chat during states `0` and `3` |
| `ZB_PreRoundStart` | `reset_spawns` | clears cached team spawn choices |
| Sandbox spawn hooks | shared identifier `BlockSpawn` | shared gamemode applies admin/single-player spawn policy across nine hook names |
| `PlayerNoClip` | `FeelFreeToTurnItOff` | allows noclip exit and admin noclip entry |
| `SpawnMenuOpen` | `SpawnMenuWhitelist` | client permits only admins/superadmins |
| `HG_CalcView` | `zzzzzzzUwU` | client spectator camera |
| `RenderScreenspaceEffects` | `huyhuyUwU` | client round fade overlay |

## Network channels

`Direction` describes the verified sender/receiver in traced files. `Unresolved` means the opposite endpoint or complete payload contract still needs tracing.

| Channel | Direction | Verified payload | Authorization/trust | Evidence/notes |
|---|---|---|---|---|
| `RoundInfo` | server -> client | `string modeName`, `int(4) roundState` | server authoritative | sent at start/end/pre-round and late join; client invokes local mode callbacks |
| `FadeScreen` | server -> clients | none | server authoritative | `zb.AddFade()` broadcast; client receiver not yet traced |
| `updtime` | server unresolved -> client | three floats: round time/start/begin | sender unresolved | client stores `zb.ROUND_TIME`, `ROUND_START`, `ROUND_BEGIN` |
| `ZB_SpectatePlayer` | server unresolved -> client | entity spectated, entity previous, int(4) view mode | sender unresolved | registered in `init.lua`; client receiver traced |
| `ZB_SendModesInfo` | server -> admin client | table of mode info records | server chooses admin recipients | client replaces `zb.availableModes` |
| `ZB_SendRoundList` | server -> admin client | table round list, string next round, string force mode | server chooses admin recipients | client inserts next round at list index 1 then clears local `nextround` |
| `ZB_RequestRoundList` | admin client -> server | none | server checks valid player + `IsAdmin()` | server replies with modes and list |
| `ZB_UpdateRoundList` | admin client -> server | table list, bool `forceUpdate` | server checks valid player + `IsAdmin()`; no shape/size/ID validation | traced UI always writes `true`; receiver reads but does not use bool |
| `ZB_NotifyRoundListChange` | server -> admins | string modifying player name | server recipients | client displays chat notice then requests fresh list |
| `SendAvailableModes` | server -> admin client | table `{key, name}` records | server checks admin before send | server hook/registration block duplicated later in same file |
| `AdminSetGameMode` | admin client -> server | string command, string mode key, bool add-to-queue | server checks `IsAdmin()`; mode key/command validation incomplete | UI writes `setforcemode` or other commands; server receiver duplicated later |
| `AdminEndRound` | admin client -> server | none | server checks `IsAdmin()` | invokes `zb:EndRound()` |
| `AdminSetGameQueue` | admin client unresolved -> server | table mode queue | server checks `IsAdmin()`; no shape/size/ID validation | receiver duplicated later in same file |
| `RequestGameQueue` | client unresolved -> server unresolved | unresolved | unresolved | network string registered; receiver/sender not yet located |
| `SendGameQueue` | server -> admins | table queued modes | server admin enumeration | `zb.SyncQueueToAdmins()`; function duplicated later |
| `QueueEmptiedNotification` | server -> admins | none | server recipients | emitted after empty queue |
| `QueueModifiedNotification` | server -> admins other than actor | string actor name, string action | server recipients | client receiver not yet traced |

## ConVars

| Name | Creator | Realm/flags | Default | Contract/risks |
|---|---|---|---|---|
| `hg_loadcontent` | global loader | archive, notify, replicated | `1` | intended Workshop resource toggle; all `resource.AddWorkshop` calls currently commented out |
| `zb_forcemode` | server round system | server convar, no flags passed | `random` | immediately reset to `random` on source load; non-empty values copied into local `forcemode` at round start |
| `hg_newspectate` | client entry | archived client convar | `1` | smooth spectator camera toggle |
| `hg_font` | client entry | archived client convar | `Bahnschrift` | UI font selection |
| `zb_dev` | consumed by round system | owner not yet traced | unresolved | suppresses some RTV/long timers and affects coop transition time |

## Console/command surfaces

### Garry's Mod console commands

| Command | Owner | Authorization | Action |
|---|---|---|---|
| `zb_getmodeschances` | mode loader | `ply:IsAdmin()` | prints JSON chances through `zChatPrint` |
| `zb_setmodechance` | mode loader | `ply:IsAdmin()` | changes in-memory chance for existing key |
| `zb_savemodeschances` | mode loader | `ply:IsAdmin()` | writes chances JSON |
| `zb_checkchances` | round system | `ply:IsAdmin()` | prints selected/future rounds |
| `zb_rerollchances` | round system | `ply:IsAdmin()` | rebuilds future list and prints it |

### Project `COMMANDS` registry entries

| Key | Authorization | Action/contract |
|---|---|---|
| `bigmap` | admin | sets map-size threshold, rerolls chances, persists map value |
| `setmode` | admin | resolves requested mode or `random`, then calls `NextRound` |
| `setforcemode` | admin | sets local force-mode value and next round when not `random` |
| `endround` | admin | calls `zb:EndRound()` |

The `COMMANDS` registry definition, dispatch path, input normalization, realm, and collision behavior remain untraced.

## Persistence surfaces

| Path | Owner | Read/write events | Schema status |
|---|---|---|---|
| `data/zbattle/modeschances.json` | mode registry | read during mode load; initially written if absent; written on shutdown/admin save | map of mode/submode identifier to number; full validation absent |
| `data/zbattle/mapsizes.json` | round system | read on `InitPostEntity`; written by `bigmap` command | map name -> numeric threshold; decode/type guards incomplete |

## Verified duplicate/override hazards in `sv_roundsystem.lua`

The source contains two server blocks registering overlapping admin mode/queue surfaces. This is not an inference from similar names: later source repeats the same network strings and definitions.

- `util.AddNetworkString` repeats `SendAvailableModes`, `AdminSetGameMode`, `AdminEndRound`, `AdminSetGameQueue`, `SendGameQueue`, `QueueEmptiedNotification`, and related names.
- `hook.Add("PlayerInitialSpawn", "SendGameModesToClient", ...)` is defined earlier and later with the same hook identifier; later registration replaces the prior callback.
- `net.Receive("AdminSetGameMode", ...)` and `net.Receive("AdminSetGameQueue", ...)` are defined earlier and later; Garry's Mod receiver storage is name-keyed, so later definitions are expected to replace earlier handlers. Runtime confirmation is still required.
- `zb.SyncQueueToAdmins` is defined earlier and later; later assignment replaces the function.
- The later `AdminSetGameMode` handler first rejects non-admins, then checks `if !(ply:IsSuperAdmin() or ply:IsAdmin()) and not zb.modes[modeKey]:CanLaunch()`. For every player who passed the first guard, the left side is false, so the launch-eligibility branch is unreachable.
- Both queue receivers trust an admin-supplied decoded table without validating length, value types, or registered mode IDs.

**Regression implication:** refactoring or deleting one block without determining which later definition is live can change behavior. The implementation package must consolidate to one registered surface per channel/hook/function, define payload schemas, validate mode IDs and bounds, and add authorized/unauthorized/malformed-message tests.

## Next trace

1. Locate all remaining senders/receivers for the channels above.
2. Inventory every `util.AddNetworkString`, `net.Receive`, `net.Start`, `hook.Add`, `hook.Run`, `CreateConVar`, `CreateClientConVar`, `concommand.Add`, and `COMMANDS.*` assignment across the repository.
3. Record duplicate names, effective last-writer behavior, payload schemas, authorization, rate/size limits, and consumers.
4. Trace the `COMMANDS` registry owner and all client admin UI send paths.
5. Convert confirmed defects into dependency-ordered implementation packages only after adjacent consumers are fully mapped.