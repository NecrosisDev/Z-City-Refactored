# Cross-Mode Packet and Trust-Boundary Matrix

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified; unresolved endpoints explicitly labeled  
**Reviewed:** 2026-07-12

## Purpose

This is the authoritative inventory for network channels used by the round framework and verified mode files. Each row records direction, ordered schema, authority, validation, phase/rate/size boundaries, and known duplicate or legacy state.

A channel is `paired` only when both writer and reader have been located and their conditional branches agree. Registration alone does not prove a live protocol.

## Status legend

| Status | Meaning |
|---|---|
| `paired` | Writer and reader are verified and schemas agree. |
| `mismatch` | Both endpoints are verified but field count/type/branch differs. |
| `one-sided` | Only writer or reader is located. |
| `overloaded` | Same channel is used in both directions or for multiple schemas. |
| `legacy/duplicate` | Overlapping protocol generation or duplicate registration exists. |
| `inactive-dependent` | Endpoint loads even when normal mode selection is disabled. |

## Trust-boundary rules

Client-authored packets must be rejected unless all applicable checks are present: sender authorization; active mode/phase; alive/incapacitated/team/role state; bounded primitive sizes; server-side identifier resolution; rate limits; ownership/distance/line-of-sight; and replay protection for non-idempotent transitions.

---

## Core round synchronization

| Channel | Direction | Ordered schema | Authority / validation | Status and defects |
|---|---|---|---|---|
| `RoundInfo` | S -> C | `string modeName`, `int4 roundState` | `libraries/sv_roundsystem.lua` sends during transitions and late join; `cl_init.lua` owns the receiver. | `paired`; client invokes local mode transition callbacks. |
| `FadeScreen` | S -> C | none | `libraries/sv_roundsystem.lua:zb.AddFade` broadcasts after `zb:EndRound`. No repository `net.Receive("FadeScreen")` exists in the traced client entry or current mode/admin UI; round presentation instead uses `RoundInfo` to set `zb.fade` and server `Player:ScreenFade`. | `writer-only/dormant`; redundant presentation generation unless an external addon consumes it. |
| `updtime` | S -> C | `float ROUND_TIME`, `float ROUND_START`, `float ROUND_BEGIN` | `init.lua:hg.UpdateRoundTime` owns server state and broadcasts; `cl_init.lua` reads the three floats into `zb.ROUND_*`. Called from round preparation/start paths. | `paired`. |
| `ZB_SpectatePlayer` | S -> C | `entity spectated`, `entity previous`, `int4 viewMode` | `init.lua` sends from the validated dead-player `ZB_ChooseSpecPly` handler for attack/attack2/reload; `cl_init.lua` reads and updates spectator camera state. | `paired`; request channel accepts only a 32-bit key but has no explicit rate limit or key allowlist before branch checks. |

## Round administration and mode queue protocols

| Channel | Direction | Ordered schema | Authorization / validation | Status and defects |
|---|---|---|---|---|
| `ZB_SendModesInfo` | S -> C admin | Lua table of `{key,name,description,bigMap,canLaunch}` records | Server chooses admin recipients. | `paired` with current manager UI. |
| `ZB_SendRoundList` | S -> C admin | Lua table future list, `string nextRound`, `string forceMode` | Server chooses admin recipients. | `paired`; implicit unversioned table schema. |
| `ZB_RequestRoundList` | C -> S | none | Requires valid admin. | `paired`; no payload/rate limit. |
| `ZB_UpdateRoundList` | C -> S | Lua table queue, `bool forceUpdate` | Requires admin; decoded table lacks explicit length/type/registered-ID/duplicate limits; bool is read but unused. | `paired`, high-trust table input. |
| `ZB_NotifyRoundListChange` | S -> C admins | `string actorName` | Server recipients. | `paired`; client requests refreshed data. |
| `SendAvailableModes` | S -> C admin | Lua table `{key,name}` records | `sv_roundsystem.lua` sends on admin initial spawn, with a duplicate same-identifier hook/implementation. | No receiver in `cl_modeselect_menu.lua`; `legacy/writer-only`. |
| `AdminSetGameMode` | C -> S | `string command`, `string modeKey`, `bool addToQueue` | Admin check; duplicate receivers; effective later handler cannot enforce `CanLaunch` because its authorization condition is false after the admin guard. | `legacy/duplicate`; current UI still sends it for force-mode toggling. |
| `AdminEndRound` | C -> S | none | Admin check. | `paired`; no rate limit. |
| `AdminSetGameQueue` | C -> S | Lua table queue | Admin check; duplicate receivers; no shape/size/ID limits. | `legacy/duplicate`; current manager instead sends `ZB_UpdateRoundList`. |
| `RequestGameQueue` | none verified | none verified | Registered in `sv_roundsystem.lua`; no repository sender or receiver found in the traced server/client queue implementation. | `registration-only/dormant`. |
| `SendGameQueue` | S -> C admins | Lua table `zb.QueuedModes` | `sv_roundsystem.lua:zb.SyncQueueToAdmins` writes it; that function is defined twice. `cl_modeselect_menu.lua` has no receiver and uses `ZB_SendRoundList`. | `legacy/writer-only`. |
| `QueueEmptiedNotification` | S -> C admins | none | Sent by `zb.NotifyQueueEmptied` and delayed after legacy `AdminSetGameQueue` clears the queue. No repository client receiver in the current manager. | `legacy/writer-only`. |
| `QueueModifiedNotification` | S -> C admins except actor | `string actorName`, `string action` | Sent by `zb.NotifyQueueModified`; no repository client receiver in the current manager, which uses `ZB_NotifyRoundListChange`. | `legacy/writer-only`. |

The active queue UI is the `ZB_*` generation. The legacy family shares server state (`zb.QueuedModes`) that is distinct from the active `zb.RoundList`, so retaining both is not merely redundant networking: it creates two queue models with duplicate receivers and divergent synchronization.

## TDM

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `tdm_start` | S -> C | Base TDM writes nothing; client reads `string rtype`. CStrike writes the expected string. | Server authoritative. | `mismatch` for base TDM; paired only through CStrike override. |
| `tdm_roundend` | S -> C | none | Server authoritative. | `paired`. |
| `tdm_open_buymenu` | S -> C one player | none | Server sends through `ShowSpare1`; client rechecks alive/time. | `paired`. |
| `tdm_buyitem` | C -> S | Lua table `{category,itemName[,attachmentID]}` | Server re-resolves category/item and checks time/money/weapon ownership; does not bound table, rate-limit, require alive/correct team, enforce `TeamBased`, or verify attachment membership. | `paired`, high-risk client table. |

## Counter-Strike objective mode and bomb entity

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `CS_Intermission` | S -> C one player | `bool isTeam0`, `int6 roundsRemaining` | Server authoritative. | `paired`; nested Derma consumer. |
| `CS_Killfeed` | S -> C | `bool killerTeam0`, `bool victimTeam0`, `string killerName`, `string victimName` | Produced by direct harm hook. | `paired`. |
| `CS_Roundover` | S -> C | `WriteBool(winner)` where winner is numeric `0|1|3`, then `string winnerText` | Server authoritative. | `mismatch`: every Lua number is truthy, so team identity collapses. |
| `bomb_look` | S -> C one player | `entity bombOrNull` | Entity interaction owner sends. | `paired`. |
| `bomb_enter` | C -> S | `string code` | No mode/phase/ownership/distance/LOS/rate/code-length/digit validation. | `paired`, critical trust gap. |
| `bomb_planted` | S -> C | none | Server authoritative. | `paired`. |

Server `BombInSite` requires two site points; the client returns true when fewer than two exist, so prediction can disagree with authority.

## Deathmatch

| Channel | Direction | Ordered schema | Validation | Status |
|---|---|---|---|---|
| `dm_start` | S -> C | `vector zonePosition`, `float zoneDistance` | Server authoritative. | `paired`. |
| `dm_end` | S -> C | `entity winnerOrNull`, `entity mostViolentOrNull` | Server authoritative; winner sampled in delayed end path. | `paired`; client retains global result state until next start. |

## Homicide

### `HMCD_RoundStart`

| Branch | S -> C ordered schema | Reader behavior | Status |
|---|---|---|---|
| Common prefix | `bool isTraitor`, `bool isGunner`, `string type`, `bool screenTimeIsDefault`, `string subRole`, `bool mainTraitor`, `string word1`, `string word2`, `uint13 traitorCount` | Client reads exact prefix. | paired prefix |
| Main-traitor normal-start roster | Repeated `color`, `string appearanceName` only for traitors with `CurAppearance`; no roster count; then `string profession` | Client loops exactly `traitorCount` entries. | `mismatch`; missing appearance desynchronizes stream. |
| Pre-role-selection branch | Same prefix with `screenTimeIsDefault=false`; no roster; profession follows count. | Role selection is hard-disabled. | structurally paired but unreachable |

### Other Homicide channels

| Channel | Direction | Ordered schema | Authorization / validation | Status and defects |
|---|---|---|---|---|
| `HMCD(StartPlayersRoleSelection)` | both | S -> C `string role`; C -> S no payload | Server accepts only players in `ChoosingPlayersList`. | `overloaded`; feature hard-disabled upstream. |
| `HMCD(EndPlayersRoleSelection)` | S -> C | none | Server authoritative. | `paired`. |
| `HMCD(SetSubRole)` | S -> C | `string subRole` | Sender not located. | `one-sided`. |
| `HMCDPoliceRole` | unresolved | unresolved | Only registration located. | `one-sided/dormant`. |
| `hmcd_announce_traitor_lose` | S -> C | `entity traitor`, `bool alive` | Server authoritative. | `paired`. |
| `HMCD_TraitorDeathState` | S -> C main traitors | `string appearanceName`, `bool alive` | Server recipient selection. | `paired`. |
| `HMCD_RequestTraitorStatuses` | C -> S | none | Requires main traitor; no rate limit. | `paired`. |
| `hmcd_roundend` | S -> C | counted traitor and gunner entity lists | Server authoritative. | `paired`; duplicate registration. |
| `HMCD_UpdateTraitorAssistants` | S -> C main traitor | `uint8 count`, repeated `color`, `string name`, `string SteamID` | Server-selected recipient. | `paired`. |

## Fear

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `check_lightness` | both | S -> C entity; C -> S vector | Does not bind response to requested entity/client or authenticate measurement. | `overloaded`, race/spoof risk. |

Fear inherits all Homicide channels. `CanLaunch=false` does not prevent receivers/direct hooks from loading.

## Half-Life 2 Deathmatch and CO-OP

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `hl2dm_start` | S -> C | none | Server authoritative. | `paired`. |
| `hl2dm_roundend` | S -> C | server writes nothing; client reads `int3 winnerTeam` | Server authoritative. | `mismatch`. |
| `ZB_RequestAirStrike` | C -> S | none | Leader/counter/cooldown checks; active-mode/alive/state checks incomplete. | `paired`. |
| `coop_start` | S -> C | none | Server authoritative. | `paired`. |
| `coop_roundend` | S -> C | none | Server authoritative. | `paired`. |

## Defense

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| vote family | mixed | primitives plus result/update tables | Mode/phase/rate checks on votes. | `paired`; unversioned tables. |
| `npc_defense_newwave` | S -> C | `float deadline`, `int4 wave` | Server authoritative. | `mismatch`: client reads only float. |
| wave/music/boss/highlight family | S -> C | none/string/table as cataloged | Server authoritative. | `paired`; highlight uses periodic entity-index table. |
| `RequestSupport` | C -> S | `string supportType` | Commander/mode/incapacitation/cooldown/catalog checks; alive check implicit. | `paired`. |
| `defense_commander_menu` | both | empty request; Lua table response | Commander + alive + rate limits. | `overloaded`, paired. |
| `defense_commander_purchase` | C -> S | Lua table requests | Size/count/catalog/rate checks; implicit item schema and weak quantity typing. | `paired`. |
| `defense_commander_notification` | S -> C | `string`, `int16` | Server authoritative. | `paired`. |
| `defense_commander_points` | none | none | Registration only; actual state uses NWInt. | dormant. |
| `defense_player_role_assigned` | S -> C | `string role` | No client receiver; actual state uses NWString. | writer-only/redundant. |
| `defense_admin_command` | C -> S | `string`, Lua table | Admin allowlist; no sender, rate/size or active-mode guard. | reader-only. |

## Crisis Response

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `criresp_start` / `ready` / `readycount` / `begin` | mixed | cataloged primitives | Partial phase/assignment checks. | `paired`. |
| `criresp_custom` | C -> S | `uint8 primary`, bodygroup string, counted gear IDs | Partial bounds; no mode/phase/role/rate/model validation. | `paired`, persistent client-state risk. |
| `criresp_over20` | C -> S | bool | Admin only. | `paired`. |
| `cri_roundend` | S -> C | winner and four uint8 counts | Server authoritative. | `paired`. |

## Pathowogen

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| briefing family | S -> C player | none | Server role assignment. | `paired`. |
| transmit family | S -> C selected players | string | Server recipient selection. | `paired`; duplicate full-list sends can occur. |
| extraction entity/point family | S -> C | entity or vector | Server authoritative. | `paired`; duplicate traitor full-list sends and persistent globals. |
| `ZB_Pathowogen_RoundEnd` | S -> C | `uint3 winCondition`, Lua table report | Server authoritative. | `paired`; unversioned potentially large table. |

Pathowogen is normally disabled by `CanLaunch=false`, but all receivers remain loaded.

## Additional modes and Event

Riot, Gang Wars, Superfighters, Slug Arena and Event start/end channels are paired as previously cataloged. Event loot synchronization remains a persistence trust boundary: `event_loot_add` accepts weakly validated client tables; `event_loot_update` is registration-only/dormant.

## Highest-priority protocol defects

1. `HMCD_RoundStart` conditional roster desynchronization.
2. `bomb_enter` missing interaction authorization and format/rate checks.
3. Active and legacy queue generations accept weak tables, duplicate handlers and maintain divergent queue state.
4. Base TDM and HL2DM sender/reader mismatches.
5. Counter-Strike winner IDs encoded as bools.
6. Defense unread wave field and implicit commander/admin table schemas.
7. Fear client-authored light samples.
8. Crisis customization outside intended ownership/phase.
9. Event loot persistence from weak client data.
10. Disabled modes retaining live receivers/direct state.

## Required runtime validation

- Capture every channel during dedicated-server cycles and assert exact bit counts.
- Fuzz every client-to-server endpoint for phase, role/team, dead/incapacitated state, oversized data, invalid IDs/entities and replay.
- Instrument duplicate `net.Receive` registrations and prove effective handlers.
- Verify one-sided/dormant names against external addons before removal.
- Version or count variable schemas before changing them.
- Freeze authoritative results before delayed presentation packets.
