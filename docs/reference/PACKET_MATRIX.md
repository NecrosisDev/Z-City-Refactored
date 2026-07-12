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

Client-authored packets must be rejected unless all applicable checks are present:

1. sender validity and authorization;
2. active mode and round phase;
3. alive/incapacitated/team/role state;
4. bounded primitive sizes before table/string processing;
5. server-side catalog resolution of identifiers;
6. rate/cooldown limits;
7. ownership, distance and line-of-sight for world interactions;
8. duplicate/replay protection where state transitions are non-idempotent.

---

## Core round synchronization

| Channel | Direction | Ordered schema | Authority / validation | Status and defects |
|---|---|---|---|---|
| `RoundInfo` | S -> C | `string modeName`, `int4 roundState` | Server authoritative; sent during transitions and late join. | `paired`; client invokes local mode transition callbacks. |
| `FadeScreen` | S -> C | none | Server broadcast. | Client receiver not yet line-paired in this matrix; `one-sided`. |
| `updtime` | S -> C | `float ROUND_TIME`, `float ROUND_START`, `float ROUND_BEGIN` | Sender ownership unresolved. | Client reader verified; `one-sided`. |
| `ZB_SpectatePlayer` | S -> C | `entity spectated`, `entity previous`, `int4 viewMode` | Sender unresolved. | Client reader verified; `one-sided`. |

## Round administration and mode queue protocols

| Channel | Direction | Ordered schema | Authorization / validation | Status and defects |
|---|---|---|---|---|
| `ZB_SendModesInfo` | S -> C admin | Lua table of `{key,name,description,bigMap,canLaunch}` records | Server chooses admin recipients. | `paired` with current manager UI. |
| `ZB_SendRoundList` | S -> C admin | Lua table future list, `string nextRound`, `string forceMode` | Server chooses admin recipients. | `paired`; implicit unversioned table schema. |
| `ZB_RequestRoundList` | C -> S | none | Requires valid admin. | `paired`; no payload/rate limit. |
| `ZB_UpdateRoundList` | C -> S | Lua table queue, `bool forceUpdate` | Requires admin; decoded table lacks explicit length/type/registered-ID/duplicate limits; bool is read but unused. | `paired`, high-trust table input. |
| `ZB_NotifyRoundListChange` | S -> C admins | `string actorName` | Server recipients. | `paired`; client requests refreshed data. |
| `SendAvailableModes` | S -> C admin | Lua table `{key,name}` records | Server admin check. | No receiver in current manager; `legacy/one-sided`. |
| `AdminSetGameMode` | C -> S | `string command`, `string modeKey`, `bool addToQueue` | Admin check; duplicate receivers; effective later handler does not enforce `CanLaunch` because authorization condition is always false after guard. | `legacy/duplicate`. |
| `AdminEndRound` | C -> S | none | Admin check. | `paired`; no rate limit. |
| `AdminSetGameQueue` | C -> S | Lua table queue | Admin check; duplicate receivers; no shape/size/ID limits. | `legacy/duplicate`. |
| `RequestGameQueue` | unresolved | unresolved | unresolved | Registered with no verified live endpoints. |
| `SendGameQueue` | S -> C admins | Lua table queue | Server admin recipients. | Current UI uses newer `ZB_*` protocol; `legacy/one-sided`. |
| `QueueEmptiedNotification` | S -> C admins | none | Server recipients. | Client receiver unresolved; `legacy/one-sided`. |
| `QueueModifiedNotification` | S -> C admins | `string actorName`, `string action` | Server recipients. | Client receiver unresolved; `legacy/one-sided`. |

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
| `CS_Intermission` | S -> C one player | `bool isTeam0`, `int6 roundsRemaining` | Server authoritative. | `paired`; consumer is nested `derma/cl_intermission.lua`. |
| `CS_Killfeed` | S -> C | `bool killerTeam0`, `bool victimTeam0`, `string killerName`, `string victimName` | Produced by direct harm hook. | `paired`; names are presentation-only. |
| `CS_Roundover` | S -> C | Server calls `WriteBool(winner)` where winner is numeric `0|1|3`; then `string winnerText`. Client reads bool + string. | Server authoritative. | `mismatch`: every Lua number is truthy, so team identity collapses. |
| `bomb_look` | S -> C one player | `entity bombOrNull` | Entity interaction owner sends. | `paired`; client opens/closes bomb UI. |
| `bomb_enter` | C -> S | `string code` | Server assumes alive player, organism movement state, `ply.bomb`, and bomb entity. No mode/phase/ownership/distance/LOS/rate/code-length/digit validation. | `paired`, critical interaction trust gap. |
| `bomb_planted` | S -> C | none | Server authoritative. | `paired`; presentation receiver in nested Derma file. |

Server `BombInSite` requires two site points. Client `BombInSite` returns true when fewer than two points exist, so client prediction/presentation can disagree with authoritative placement.

## Deathmatch

| Channel | Direction | Ordered schema | Validation | Status |
|---|---|---|---|---|
| `dm_start` | S -> C | `vector zonePosition`, `float zoneDistance` | Server authoritative. | `paired`. |
| `dm_end` | S -> C | `entity winnerOrNull`, `entity mostViolentOrNull` | Server authoritative; winner sampled in delayed end path. | `paired`; client trusts entity flags and retains global result state until next start. |

## Homicide

### `HMCD_RoundStart`

| Branch | S -> C ordered schema | Reader behavior | Status |
|---|---|---|---|
| Common prefix | `bool isTraitor`, `bool isGunner`, `string type`, `bool screenTimeIsDefault`, `string subRole`, `bool mainTraitor`, `string word1`, `string word2`, `uint13 traitorCount` | Client reads exact prefix. | paired prefix |
| Main-traitor normal-start roster | Repeated `color`, `string appearanceName` **only for traitors with `CurAppearance`**; no roster count; then `string profession` | Client loops exactly `traitorCount` entries before reading profession. | `mismatch`; missing appearance causes stream underwrite/desynchronization. |
| Pre-role-selection branch | Same prefix with `screenTimeIsDefault=false`; no roster; profession follows count. | Role selection is currently hard-disabled. | structurally paired but unreachable |

### Other Homicide channels

| Channel | Direction | Ordered schema | Authorization / validation | Status and defects |
|---|---|---|---|---|
| `HMCD(StartPlayersRoleSelection)` | S -> C and C -> S | S -> C: `string role`; C -> S: no payload acknowledgement | Server accepts only players in `ChoosingPlayersList`. | `overloaded`; feature hard-disabled upstream. |
| `HMCD(EndPlayersRoleSelection)` | S -> C | none | Server authoritative. | `paired`; closes panel. |
| `HMCD(SetSubRole)` | S -> C | `string subRole` | Sender not located. | `one-sided`; client receiver only. |
| `HMCDPoliceRole` | unresolved | unresolved | Only registration located. | `one-sided/dormant`. |
| `hmcd_announce_traitor_lose` | S -> C | `entity traitor`, `bool alive` | Server authoritative. | `paired`. |
| `HMCD_TraitorDeathState` | S -> C main traitors | `string appearanceName`, `bool alive` | Server builds recipient list; request path requires requester to be main traitor. | `paired`. |
| `HMCD_RequestTraitorStatuses` | C -> S | none | Requires `isTraitor && MainTraitor`; no rate limit. | `paired`; response is one death-state packet per appearance-backed traitor. |
| `hmcd_roundend` | S -> C | `uint13 traitorCount`, repeated entity; `uint13 gunnerCount`, repeated entity | Server authoritative. Client sets flags without validating read entities before member access. | `paired`; network string registered multiple times. |
| `HMCD_UpdateTraitorAssistants` | S -> C main traitor | `uint8 count`, repeated `color`, `string name`, `string SteamID` | Server-selected recipient. | `paired`; independent count fixes the start-packet roster problem for later updates. |

## Fear

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `check_lightness` | S -> C then C -> S on same channel | S -> C: `entity playerToSample`; C -> S: `vector lightColor` | Server accepts vector length <= sqrt(3), nonnegative components, and first response per sender while global `checkedPlayer` is set. It does not bind response to the requested entity/client or authenticate measurement. | `overloaded`, race/spoof risk. |

Fear inherits all Homicide channels. `CanLaunch=false` does not prevent these receivers/direct hooks from loading.

## Half-Life 2 Deathmatch

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `hl2dm_start` | S -> C | none | Server authoritative. | `paired`. |
| `hl2dm_roundend` | S -> C | Server writes nothing; client reads `int3 winnerTeam`. | Server authoritative. | `mismatch`. |
| `ZB_RequestAirStrike` | C -> S | none; server derives target from sender eye trace | Requires `ply.leader`, per-player remaining strikes, global cooldown. No explicit active-mode/round/alive/incapacitated/rate check; leader flag can leak. | `paired`, authorization-state risk. |

## CO-OP

| Channel | Direction | Ordered schema | Validation | Status |
|---|---|---|---|---|
| `coop_start` | S -> C | none | Server authoritative. | `paired`. |
| `coop_roundend` | S -> C | none | Server authoritative. | `paired`. |

NPC possession is driven by direct `PlayerButtonDown` server logic rather than a network channel.

## Defense

### Vote and lifecycle channels

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `defense_start_vote` | S -> C | `float voteDeadline` | Server authoritative. | `paired`. |
| `defense_submit_vote` | C -> S | `int4 vote` | Valid player, one-second sender rate limit, vote 1..3, active Defense + vote phase, one initial vote. | `paired`. |
| `defense_change_vote` | C -> S | `int4 previousVote`, `int4 newVote` | One-second rate limit, new vote 1..3, active Defense + vote phase; server ignores transmitted previous value and uses stored vote. | `paired`; redundant client field. |
| `defense_vote_update` | S -> C | Lua table vote counts | Server authoritative; unversioned table. | `paired`. |
| `defense_vote_result` | S -> C | `string selectedMode`, Lua table vote counts | Server authoritative. | `paired`. |
| `defense_show_selected_mode` | S -> C | `string selectedMode` | Server authoritative. | `paired`. |
| `npc_defense_start` | S -> C | none | Server authoritative. | `paired`; duplicate client receivers reset commander hint state. |
| `npc_defense_prepphase` | S -> C | none | Server authoritative. | `paired`; commander UI also listens for hint display. |
| `npc_defense_newwave` | S -> C | `float deadline`, `int4 wave` | Server authoritative. | `mismatch`: traced client reads only the float. |
| `npc_defense_roundend` | S -> C | none | Server authoritative. | `paired`. |
| `StartWaveMusic` | S -> C | `string soundPath` | Server selects from mode data. | `paired`; client resource/path validation remains presentation concern. |
| `StopWaveMusic` | S -> C | none | Server authoritative. | `paired`. |
| `defense_boss_incoming` | S -> C | none | Server authoritative. | Client endpoint exists in large UI file; paired by source inventory. |
| `defense_highlight_last_npcs` | S -> C | Lua table of remaining NPC entity indices | `sv_defense_hooks.lua` broadcasts when tracked count is 1–3 and the list changes or periodic resend is due; client resolves valid entities and outlines them. | `paired`; unversioned Lua table and periodic world-state broadcast. |

### Commander, support and administration channels

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `RequestSupport` | C -> S | `string supportType` | Two-second sender rate limit; Commander role; active Defense; global 290-second cooldown; incapacitation check; server catalog resolution. Does not explicitly require alive before role/mode handling, though role is normally assigned alive. | `paired`. |
| `defense_commander_menu` | C -> S and S -> C | C -> S: none; S -> C: Lua table `DEFENSE_COMMANDER_ITEMS` | Commander + alive; one-second request and five-second send limits. | `overloaded`, paired. |
| `defense_commander_purchase` | C -> S | Lua table item requests | Commander + alive + active mode + incapacitation check; raw message length <=8192; table <=20; server item catalog resolution; per-request quantity capped at 10; one-second rate. | `paired`; table shape remains implicit and quantity lower/type bounds need validation. |
| `defense_commander_notification` | S -> C | `string message`, `int16 pointDelta` | Server authoritative. | `paired`; registered in multiple auxiliary files. |
| `defense_commander_points` | none verified | none verified | Network string is registered, but repository search found no writer or reader. Commander points are replicated through `NWInt("CommanderPoints")`. | `registration-only/dormant`. |
| `defense_player_role_assigned` | S -> C | `string role` | Server sends to assigned Commander from role setup/admin helper; repository search found no client receiver. Clients infer role through `NWString("PlayerRole")`. | `writer-only`; redundant with NWVar state. |
| `defense_admin_command` | C -> S | `string command`, Lua table `args` | Requires admin/superadmin. Command allowlist is inline (`start_wave`, `end_wave`, `set_wave`, `add_points`); numeric arguments must be positive. No sender located in repository, no table size/type/rate/active-mode guard, and `start_wave` calls `MODE:StartWave(wave)` although the method ignores the argument. | `reader-only/admin trust boundary`. |

## Crisis Response

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `criresp_start` | S -> C | none | Server authoritative. | `paired`; opens menu and triggers customization send. |
| `criresp_ready` | C -> S | none | Active mode, round state 0, sender must be in assigned table. No unready/revoke; no explicit rate limit. | `paired`. |
| `criresp_readycount` | S -> C | `uint8 ready`, `uint8 total` | Server authoritative. | `paired`. |
| `criresp_begin` | S -> C | none | Server authoritative. | `paired`. |
| `criresp_custom` | C -> S | `uint8 primary`, `string bodygroups`, `uint4 gearCount`, repeated `uint8 gearID` | Bodygroup string capped at 48 chars; count capped to slots; IDs catalog-checked/deduplicated. No mode/phase/assignment/SWAT/rate check; bodygroup values/model compatibility not validated. | `paired`, persistent client-state risk. |
| `criresp_over20` | C -> S | `bool enabled` | Requires admin; mutates replicated convar. | `paired`; no rate limit. |
| `cri_roundend` | S -> C | `uint4 winner`, `uint8 killed`, `uint8 incapacitated`, `uint8 arrested`, `uint8 total` | Server authoritative. | `paired`; client applies 8.5-second input lock. |

## Pathowogen

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `zb_furbriefing` | S -> C player | none | Server role assignment. | `paired`. |
| `zb_furfurbriefing` | S -> C player | none | Server role assignment. | `paired`. |
| `zb_furtraitorbriefing` | S -> C player | none | Server role assignment. | `paired`. |
| `zb_contractortransmit` | S -> C traitors | `string text` | Server recipient selection. | `paired`; duplicate sends can occur because transmit is called inside a loop while sending to full list. |
| `zb_commandertransmit` | S -> C humans/squad | `string text` | Server recipient selection. | `paired`. |
| `zb_extractionheli` | S -> C | `entity helicopter` | Server authoritative. | `paired`; client global state persists until round-start reset. |
| `zb_extractionpoint` | S -> C selected players | `vector point` | Server authoritative. | `paired`. |
| `zb_traitorextractionpoint` | S -> C traitors | `vector point` | Server authoritative. | `paired`; server loops eligible traitors but sends to full list each iteration. |
| `ZB_Pathowogen_RoundEnd` | S -> C | `uint3 winCondition`, Lua table player consequence report | Server authoritative; table includes entity keys/state. | `paired`; unversioned, potentially large table. |

Pathowogen is normally disabled by `CanLaunch=false`, but all receivers remain loaded.

## Riot, Gang Wars, Superfighters, Slug Arena

| Channel | Direction | Ordered schema | Status / defects |
|---|---|---|---|
| `riot_start` | S -> C | none | paired |
| `riot_roundend` | S -> C | none | paired |
| `gwars_start` | S -> C | none | paired |
| `gwars_roundend` | S -> C | none | paired |
| `supfight_start` | S -> C | `vector zonePoint` | paired; launch does not validate point existence |
| `supfight_end` | S -> C | `entity winnerOrNull` | paired; winner sampled after delay |
| `scugarena_start` | S -> C | none | paired |
| `scugarena_end` | S -> C | `entity winnerOrNull` | paired; winner sampled after delay |

## Event mode

| Channel | Direction | Ordered schema | Validation | Status and defects |
|---|---|---|---|---|
| `event_start` | S -> C | none | Server authoritative. | paired |
| `event_end` | S -> C | `entity winnerOrNull` | Server authoritative. | paired; delayed winner sampling |
| `event_eventers_update` | S -> C | Lua table SteamIDs | Server authoritative. | paired; unversioned table |
| `event_loot_sync` | S -> C authorized users | Lua table `{weight,class}` entries | Server selects admins/eventers. | paired; no explicit total-size/schema version |
| `event_loot_add` | C -> S | Lua table `{weight,class}` | Requires admin or current EventersList membership. Checks field presence only; no type/range/class/catalog/rate/size limits. | paired, high-risk persistent input |
| `event_loot_remove` | C -> S | `uint16 itemIndex` | Requires admin/eventer and existing index; no rate limit. | paired |
| `event_loot_request` | C -> S and S -> C | C -> S: no payload; S -> C: no payload opens menu | Server requires admin/eventer for request; client also exposes admin-only menu command. | `overloaded`; server concommand sends this channel to client. |
| `event_loot_update` | unresolved | unresolved | Registered but no verified endpoints. | one-sided/dormant |

Event loot is persisted to `data/zbattle/event_loot/loot_table_<hostname>.txt`; client-authored additions therefore cross both network and persistence trust boundaries.

## Highest-priority protocol defects

1. `HMCD_RoundStart` roster count/record-count desynchronization.
2. `bomb_enter` lacks world-interaction, phase, format, ownership and rate validation.
3. Admin queue protocols accept unbounded/untyped Lua tables and overlap across two generations.
4. Base TDM and HL2DM have guaranteed sender/reader field mismatches.
5. Counter-Strike winner IDs are encoded as bools.
6. Defense new-wave writes an unread field; commander purchase/admin endpoints rely on implicit Lua-table schemas.
7. Fear light measurement trusts client-authored samples through a global request slot.
8. Crisis customization is accepted outside the intended mode/phase/role and persists.
9. Event loot additions accept weakly validated client data and persist it.
10. Disabled/zero-chance modes retain live receivers and global/direct-hook state.

## Required runtime validation

- Capture every channel during a dedicated-server cycle for each mode and assert exact read/write bit counts.
- Fuzz every client-to-server endpoint with wrong phase, role/team, dead/incapacitated sender, oversized strings/tables, invalid IDs/entities and rapid replay.
- Instrument duplicate `net.Receive` registrations and prove the effective handler.
- Verify every one-sided/dormant registration against external addons before removal.
- Introduce protocol versions or explicit record counts before changing variable packet schemas.
- Freeze authoritative round results before delayed presentation packets.
