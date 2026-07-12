# Public Surfaces Inventory

**Work package:** `WP-RESEARCH-001`  
**Scope:** bootstrap, gamemode entry, mode registry, round lifecycle, admin mode UI, TDM, and initial Homicide trace  
**Status:** `partial / executable-source verified`  
**Runtime source baseline:** commit `429ec928203cec963176dfb6afd086dcdd01c181`  
**Reviewed:** 2026-07-12

## Purpose

This file inventories cross-file contracts that are easy to break during refactoring: globals, hooks, network channels, convars, commands, persistence, authorization, and payload schemas. It records only surfaces found in currently traced source; absence from this file does not prove a surface does not exist.

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
| `TDM_OpenedBuyMenu` | `cl_tdm.lua` | client | global panel reference used to replace/close the TDM buy menu |
| `StartTime` | `cl_homicide.lua` assignment lacks `local` in traced receiver | client global | set when `HMCD_RoundStart` arrives; ownership collision risk pending full client trace |

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
| `ZB_TraitorWinOrNot` | Homicide end-round | traitor outcome established | `traitor player`, `winner identifier` |
| dynamic mode hook names | mode registry dispatcher | one dispatcher installed for every function key found on every mode | selected mode table as first callback argument; forwards up to six returns only if first is non-`nil` |

### Hooks consumed/registered by traced code

| Hook | Identifier | Owner/action |
|---|---|---|
| `InitPostEntity` | `zcity` | global loader loads `lua/initpost` |
| `InitPostEntity` | `loadbigmap` | server round system loads map threshold |
| `InitPostEntity` | `OwOmooooove` | server gamemode entry rebuilds spawn cache |
| `InitPostEntity` | `RequestModeData` | admin client requests mode/queue data two seconds later |
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
| `PlayerButtonDown` | `OpenAdminMenuF6` | admin client opens mode/end-round menu on F6 |
| `StartCommand` | `TDM_DisallowMoveOrShoting` | client removes attack/movement inputs during TDM opening period |
| `PlayerDeath` | `HMCD_TraitorDeathTracking` | Homicide broadcasts traitor alive state |
| `PlayerSpawn` | `HMCD_TraitorSpawnTracking` | Homicide broadcasts traitor alive state |
| `PlayerCanPickupWeapon` | `HMCD_TraitorRadioPickup` | Homicide handles duplicate traitor radios |
| `Player_Death` | `HMCD_PlayerDeath` | project death hook handles Homicide rewards/messages |
| `RoundStateChange` | `ResetNextRoundMainTraitors` | Homicide attempts reset only for stale state `2`; emitter not yet verified |

## Network channels

`Direction` describes verified endpoints in traced files. A channel remains `partial` until all writers/readers and conditional branches are paired.

### Core round and admin mode controls

| Channel | Direction | Verified payload | Authorization/trust | Evidence/notes |
|---|---|---|---|---|
| `RoundInfo` | server -> client | `string modeName`, `int(4) roundState` | server authoritative | sent at start/end/pre-round and late join; client invokes local mode callbacks |
| `FadeScreen` | server -> clients | none | server authoritative | `zb.AddFade()` broadcast; client receiver not yet traced |
| `updtime` | server unresolved -> client | three floats: round time/start/begin | sender unresolved | client stores `zb.ROUND_TIME`, `ROUND_START`, `ROUND_BEGIN` |
| `ZB_SpectatePlayer` | server unresolved -> client | entity spectated, entity previous, int(4) view mode | sender unresolved | registered in `init.lua`; client receiver traced |
| `ZB_SendModesInfo` | server -> admin client | table of records: key/name/description/big-map/can-launch | server sends only to admins in traced paths | client replaces `zb.availableModes` and refreshes open manager |
| `ZB_SendRoundList` | server -> admin client | table future list, string next round, string force mode | server sends only to admins in traced paths | client inserts next round at index 1, then clears local `nextround` |
| `ZB_RequestRoundList` | admin client -> server | none | server checks valid player + `IsAdmin()` | sent on manager open, admin InitPostEntity, and change notification; server replies with info/list |
| `ZB_UpdateRoundList` | admin client -> server | table copied client list, bool `true` | server checks valid player + `IsAdmin()`; no shape/size/ID validation | receiver reads `forceUpdate` but does not use it |
| `ZB_NotifyRoundListChange` | server -> admins | string modifying player name | server recipients | client displays chat notice then requests fresh list |
| `SendAvailableModes` | server -> admin client | table `{key, name}` records | server checks admin before send | no receiver found in traced `cl_modeselect_menu.lua`; legacy/other consumer pending |
| `AdminSetGameMode` | admin client -> server | string command, string mode key, bool add-to-queue | server checks `IsAdmin()`; command/key validation incomplete | traced UI sends `setforcemode`; duplicate server receivers, later one expected effective |
| `AdminEndRound` | admin client -> server | no payload | server checks `IsAdmin()` | F6 menu sends; server calls `zb:EndRound()` |
| `AdminSetGameQueue` | client sender unresolved -> server | table mode queue | server checks `IsAdmin()`; no shape/size/ID validation | receiver duplicated; current traced UI instead uses `ZB_UpdateRoundList` |
| `RequestGameQueue` | endpoints unresolved | unresolved | unresolved | registered server-side but no traced use |
| `SendGameQueue` | server -> admins | table queued modes | server admin enumeration | sync function duplicated; no receiver found in traced current UI |
| `QueueEmptiedNotification` | server -> admins | none | server recipients | emitted by legacy queue handler; client receiver unresolved |
| `QueueModifiedNotification` | server -> admins other than actor | string actor name, string action | server recipients | client receiver unresolved |

### TDM channels

| Channel | Direction | Verified payload | Authorization/trust | Evidence/notes |
|---|---|---|---|---|
| `tdm_start` | server -> clients | server writes nothing; client reads one string | server authoritative | verified sender/receiver schema mismatch; client assigns read value to `zb.rtype` |
| `tdm_roundend` | server -> clients | no payload | server authoritative | client opens end-round player menu |
| `tdm_open_buymenu` | server -> one client | no payload | triggered by mode `ShowSpare1` for alive player | client opens buy menu only if locally alive and within 40 seconds |
| `tdm_buyitem` | any client -> server | Lua table `{category, itemName [, attachmentID]}` | no admin requirement; server checks mode, time, catalog lookup and money | no explicit alive/rate/size/team restriction; attachment ID not checked against allowed item list |

### Homicide channels verified so far

| Channel | Direction | Verified payload | Authorization/trust | Evidence/notes |
|---|---|---|---|---|
| `HMCD_RoundStart` | server -> individual clients | variable ordered role/type payload with conditional traitor roster | server authoritative | exact branch pairing incomplete; 13-bit traitor count controls conditional reads |
| `HMCD(StartPlayersRoleSelection)` | server -> selected main traitor; client response on same name | server writes role-selection string; client-to-server acknowledgement payload not yet traced | server receiver trusts membership in `MODE.ChoosingPlayersList` | feature currently hard-disabled by `ShouldStartRoleRound` |
| `HMCD(EndPlayersRoleSelection)` | server -> clients | no payload observed | server authoritative | emitted when role-selection timer ends; client receiver pending |
| `HMCD(SetSubRole)` | endpoints/payload partial | unresolved | unresolved | registered in server mode file |
| `HMCDPoliceRole` | endpoints/payload partial | unresolved | unresolved | registered in server mode file |
| `hmcd_announce_traitor_lose` | server -> clients | entity traitor, bool alive | server authoritative | emitted during end-round loss paths |
| `HMCD_TraitorDeathState` | server -> main traitors | string appearance name, bool alive | server selects main-traitor recipients | also sent in response to status request |
| `HMCD_RequestTraitorStatuses` | client -> server | no payload | server requires requester traitor + main traitor | returns one death-state message per traitor with appearance |
| `hmcd_roundend` | server -> clients | uint(13) traitor count + entities, then uint(13) gunner count + entities | server authoritative | network string registered more than once; client decoder pending full trace |
| `HMCD_UpdateTraitorAssistants` | endpoints/payload partial | unresolved | unresolved | registered in server Homicide file |

## ConVars

| Name | Creator | Realm/flags | Default | Contract/risks |
|---|---|---|---|---|
| `hg_loadcontent` | global loader | archive, notify, replicated | `1` | intended Workshop resource toggle; all `resource.AddWorkshop` calls currently commented out |
| `zb_forcemode` | server round system | server convar, no flags passed | `random` | immediately reset to `random` on source load; non-empty values copied into local `forcemode` at round start |
| `hg_newspectate` | client entry | archived client convar | `1` | smooth spectator camera toggle |
| `hg_font` | client entry/Homicide client | archived client convar | `Bahnschrift` | repeated guarded acquisition; UI font selection |
| `hmcd_subrole_traitor_soe` | Homicide shared/client | archived + userinfo client convar | `traitor_default_soe` | client-selected traitor subrole; server validation path pending |
| `hmcd_subrole_traitor` | Homicide shared/client | archived + userinfo client convar | `traitor_default` | client-selected standard traitor subrole; server validation path pending |
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
| `hmcd_request_main_traitor` | Homicide server | valid admin outside active round | marks SteamID in `NextRoundMainTraitors`, but the consumer selection path is commented out |

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
| player PData `zb_hmcd_t_wins` | Homicide | incremented for winning traitor | integer-like value read with default `0`; type normalization pending |
| player PData `zb_hmcd_ino_t_kills` | Homicide | incremented for innocent killing traitor | integer-like value read with default `0`; type normalization pending |

## Verified duplicate/override hazards in `sv_roundsystem.lua`

The source contains two server blocks registering overlapping admin mode/queue surfaces. Later name-keyed registrations are expected to replace earlier handlers/functions, but runtime confirmation remains required.

- `util.AddNetworkString` repeats `SendAvailableModes`, `AdminSetGameMode`, `AdminEndRound`, `AdminSetGameQueue`, `SendGameQueue`, `QueueEmptiedNotification`, and related names.
- `hook.Add("PlayerInitialSpawn", "SendGameModesToClient", ...)` appears twice with the same identifier; the later callback is expected to replace the earlier one.
- `net.Receive("AdminSetGameMode", ...)` and `net.Receive("AdminSetGameQueue", ...)` appear twice; later handlers are expected effective.
- `zb.SyncQueueToAdmins` is assigned twice; later assignment replaces the earlier function.
- The later `AdminSetGameMode` handler rejects non-admins, then tests `if !(ply:IsSuperAdmin() or ply:IsAdmin()) and not zb.modes[modeKey]:CanLaunch()`. The left side is always false for anyone who passed the guard, so launch eligibility is not enforced there.
- Current `cl_modeselect_menu.lua` uses the newer `ZB_*` list protocol for manager synchronization, while several older `SendGameQueue`/`AdminSetGameQueue` surfaces remain registered. This indicates overlapping protocol generations, not one coherent API.
- Both queue receivers trust decoded admin-supplied tables without validating length, types, registered mode IDs, duplicate entries, or resource limits.

**Regression implication:** implementation must first identify live consumers, then consolidate to one protocol and one registration per semantic operation. Removing a duplicate by appearance alone may revive or delete legacy behavior unexpectedly.

## Verified mode-specific contract defects

- **TDM:** `tdm_start` sender/receiver schema mismatch; dot-defined `GuiltCheck` receives dispatcher-injected mode table; arbitrary attachment IDs can reach `hg.AddAttachmentForce`; `TeamBased` purchase metadata is not enforced.
- **Homicide:** role selection is hard-disabled; requested-main-traitor consumer is commented out; stale state `2` reset; undefined `gun` used by police attachment calls; `math.random(0,1)` conditions always true in Lua; nil AFK comparison in `SpawnForce`; variable payload lacks versioning.

See `docs/modes/MODE_CATALOG.md` for evidence, integration dependencies, and validation procedures.

## Next trace

1. Locate unresolved legacy admin queue consumers and decide whether they are live, dead, or external-facing.
2. Complete all Homicide payload sender/receiver pairs and server type definitions.
3. Inventory every `util.AddNetworkString`, `net.Receive`, `net.Start`, `hook.Add`, `hook.Run`, convar, console command, and `COMMANDS.*` assignment while tracing remaining modes.
4. Record duplicate names, effective last-writer behavior, payload schemas, authorization, rate/size limits, and consumers.
5. Convert confirmed defects into dependency-ordered implementation packages only after adjacent consumers are fully mapped.