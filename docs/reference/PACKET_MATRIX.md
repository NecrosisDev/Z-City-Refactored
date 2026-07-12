# Cross-Mode Packet and Trust-Boundary Matrix

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified; unresolved endpoints explicitly labeled  
**Reviewed:** 2026-07-12

## Purpose

This is the canonical inventory for verified round, mode and organism network channels. A row is `paired` only when both writer and reader are located and their conditional schemas agree. Registration alone does not prove a live protocol.

## Status legend

| Status | Meaning |
|---|---|
| `paired` | Writer/reader and schema agree. |
| `mismatch` | Both endpoints exist but field count/type/branch differs. |
| `one-sided` | Only writer or reader is located. |
| `overloaded` | Same name carries multiple directions/schemas. |
| `legacy/duplicate` | Overlapping generation or duplicate registration. |
| `dormant` | Registration/function exists but no live caller/consumer was found. |

## Client-input validation standard

Every C -> S endpoint must validate sender authorization, active subsystem/mode/phase, alive/incapacitated/team/role state, primitive/table size and type, server-side identifier resolution, ownership/distance/line of sight, rate limits and replay/non-idempotent state transitions.

---

## Core round synchronization

| Channel | Direction | Ordered schema | Authority / validation | Status and defects |
|---|---|---|---|---|
| `RoundInfo` | S -> C | `string modeName`, `int4 roundState` | Server transitions/late join; client updates local round and invokes client mode callbacks. | `paired`. |
| `FadeScreen` | S -> C | none | `zb.AddFade` broadcasts after end; no repository client receiver located. | `writer-only/dormant`; other fade paths exist. |
| `updtime` | S -> C | `float ROUND_TIME`, `float ROUND_START`, `float ROUND_BEGIN` | `hg.UpdateRoundTime` writes; client reads exact fields. | `paired`. |
| `ZB_ChooseSpecPly` | C -> S | `uint32 key` | Dead-player/key branch checks; no explicit rate limit/general key allowlist. | `paired` with response below. |
| `ZB_SpectatePlayer` | S -> C | `entity spectated`, `entity previous`, `int4 viewMode` | Server response to validated spectator input. | `paired`. |

## Round administration and queues

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `ZB_SendModesInfo` | S -> admin C | Lua table mode records | paired; implicit schema |
| `ZB_SendRoundList` | S -> admin C | table list, string next, string force | paired; implicit schema |
| `ZB_RequestRoundList` | admin C -> S | none | admin check; no rate limit |
| `ZB_UpdateRoundList` | admin C -> S | table list, bool forceUpdate | no explicit table length/type/ID/duplicate bounds; bool unused |
| `ZB_NotifyRoundListChange` | S -> admins | string actor | paired |
| `AdminSetGameMode` | admin C -> S | string command, string mode, bool queue | duplicate receivers; later `CanLaunch` condition is ineffective after admin guard |
| `AdminEndRound` | admin C -> S | none | paired; no rate limit |
| `AdminSetGameQueue` | admin C -> S | Lua table | duplicate/legacy; unbounded shape |
| `SendAvailableModes` | S -> admin C | Lua table | current manager has no receiver; writer-only legacy |
| `SendGameQueue` | S -> admins | Lua table `zb.QueuedModes` | current manager uses `ZB_SendRoundList`; writer-only legacy |
| `RequestGameQueue` | none found | none | registration-only dormant |
| queue notification legacy family | S -> admins | none or actor/action strings | current manager has no readers |

The active `ZB_*` queue and legacy `AdminSetGameQueue`/`SendGameQueue` families operate on different server lists, creating two queue models rather than only duplicate transport.

## TDM and Counter-Strike

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `tdm_start` | S -> C | base TDM writes none; client reads string; CStrike writes string | base mode mismatch |
| `tdm_roundend` | S -> C | none | paired |
| `tdm_open_buymenu` | S -> one C | none | paired; client rechecks alive/time |
| `tdm_buyitem` | C -> S | Lua table `{category,itemName[,attachmentID]}` | server catalog/money/time checks; no table/rate/alive/team/TeamBased/attachment allowlist bounds |
| `CS_Intermission` | S -> C | bool team, int6 rounds | paired in nested Derma file |
| `CS_Killfeed` | S -> C | two team bools, killer/victim strings | paired |
| `CS_Roundover` | S -> C | bool winner, string text | server passes numeric `0|1|3` to `WriteBool`, collapsing identity |
| `bomb_look` | S -> one C | entity bomb/null | paired |
| `bomb_enter` | C -> S | string code | no mode/phase/ownership/distance/LOS/rate/length/digit validation |
| `bomb_planted` | S -> C | none | paired |

## Deathmatch

| Channel | Direction | Ordered schema | Status |
|---|---|---|---|
| `dm_start` | S -> C | vector center, float distance | paired |
| `dm_end` | S -> C | entity winner/null, entity mostViolent/null | paired; delayed winner sampling/global client state |

## Homicide and Fear

### `HMCD_RoundStart`

| Branch | Ordered schema | Status |
|---|---|---|
| Common | bool traitor, bool gunner, string type, bool default-screen-time, string subrole, bool main-traitor, two strings, uint13 traitor count | prefix paired |
| Main-traitor roster | repeated color + appearance name only for traitors with appearance, then profession string | mismatch: client loops transmitted traitor count, not actual roster count |
| Role-selection | common prefix with default-screen-time false and no roster | structurally paired but upstream feature disabled |

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `HMCD(StartPlayersRoleSelection)` | both | outbound role string; inbound no payload | sender membership check; overloaded; feature disabled |
| `HMCD(EndPlayersRoleSelection)` | S -> C | none | paired |
| `HMCD(SetSubRole)` | S -> C expected | string | client reader only |
| `HMCDPoliceRole` | unresolved | unresolved | registration-only dormant |
| `hmcd_announce_traitor_lose` | S -> C | entity, bool alive | paired |
| `HMCD_TraitorDeathState` | S -> main-traitor C | appearance name, bool alive | paired |
| `HMCD_RequestTraitorStatuses` | C -> S | none | main-traitor check; no rate limit |
| `hmcd_roundend` | S -> C | counted traitor entities, counted gunner entities | paired; duplicate registration and client entity assumptions |
| `HMCD_UpdateTraitorAssistants` | S -> main-traitor C | uint8 count, repeated color/name/SteamID | paired |
| `check_lightness` | both | S -> C entity; C -> S vector | global target slot; client-authored measurement not bound to requested client/entity |

Fear inherits Homicide transport. `CanLaunch=false` does not prevent its receiver/direct-hook registrations from loading.

## HL2DM and CO-OP

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `hl2dm_start` | S -> C | none | paired |
| `hl2dm_roundend` | S -> C | server writes none; client reads int3 winner | mismatch |
| `ZB_RequestAirStrike` | C -> S | none; target derived from eye trace | leader/strikes/global cooldown checks; active-mode/alive/incapacitated/state validation incomplete |
| `coop_start` | S -> C | none | paired |
| `coop_roundend` | S -> C | none | paired |

## Organism, injury and blood effects

| Channel | Direction | Ordered schema | Authority / validation | Status and defects |
|---|---|---|---|---|
| `organism_send` | S -> C | Lua table snapshot; bool force; bool spectatorProtection; bool moreInfo; bool add/merge | Server owner/PVS/event paths; unreliable option. Client reads owner from table. | paired but unversioned/high-cost; client calls `owner:IsNPC()` before validity check; developer mode can send entire table |
| `organism_sendply` | unresolved | unresolved | Registered server-side; commented client receiver only. | dormant/registration-only |
| `VirusStageUpdate` | S -> infected C | int8 stage | Server stage timer writes; no repository client receiver found. | writer-only |
| `pulse` | S -> owner C | none | `hg.organism.Pulse` writes, but repository search found no caller and no receiver. | dormant function/registration |
| `bloodsquirt2` | S -> C | entity, bone string, matrix, position vector, direction vector | Server blood/vomit path; client validates entity, then uses transmitted matrix/bone/effect timer. | paired; large effect timer and model/bone assumptions |
| `bloodsquirt` | S -> C | same entity/bone/matrix/position/direction pattern | Writer ownership not yet fully paired; client reader verified. | reader-side verified/one-sided |
| `addfountain` | S -> C | entity, force vector | client reader verified; writer not yet paired. | one-sided |
| `hg_bloodimpact` | S -> C | position vector, velocity vector, float multiplier, int8 amount | client clamps amount 0..32; sender not yet paired. | one-sided |
| wounds NetVars | S -> C state | wound/arterial-wound Lua tables via NetVar | Server updates during clear, bleeding, damage and amputation. | overlapping authority with `organism_send` |

### Organism command trust boundaries

| Command | Input | Validation / defect |
|---|---|---|
| `hg_fixdislocation` | limb group, target-self/eye-trace flag | alive/conscious/movement/pain/cooldown checks; missing/non-numeric args can reach `math.Round(nil)`; other-target interaction lacks explicit distance cap beyond eye trace |
| `hmcd_holdbreath`, `+hmcd_holdbreath`, `-hmcd_holdbreath` | no meaningful data | self organism/alive/stamina/O2/cooldown checks; immediate partial snapshot |

## Defense

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| vote family | mixed | float deadline, int4 choices, result/update tables | mode/phase/rate checks; implicit tables |
| `npc_defense_newwave` | S -> C | float deadline, int4 wave | client reads only float; mismatch |
| wave/music/boss family | S -> C | none/string | paired |
| `defense_highlight_last_npcs` | S -> C | Lua table entity indices | paired periodic list when 1–3 tracked NPCs remain |
| `RequestSupport` | C -> S | string support type | Commander/mode/incapacitation/catalog/rate/global cooldown checks; alive implicit |
| `defense_commander_menu` | both | empty request, Lua table response | role/alive/request/send limits; overloaded |
| `defense_commander_purchase` | C -> S | Lua table requests | raw/table/count/catalog/rate/points checks; implicit item shape and weak lower/type normalization |
| `defense_commander_notification` | S -> C | string, int16 | paired |
| `defense_commander_points` | none | none | registration-only; actual points use NWInt |
| `defense_player_role_assigned` | S -> C | string role | no client receiver; actual role uses NWString |
| `defense_admin_command` | C -> S | string command, Lua table args | admin inline allowlist; no repository sender/rate/size/active-mode guard |

## Crisis Response

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `criresp_start` / `ready` / `readycount` / `begin` | mixed | no payload or two uint8 counts | partial phase/assignment validation; no unready |
| `criresp_custom` | C -> S | uint8 primary, bodygroup string, uint4 count, repeated uint8 gear IDs | partial bounds; no mode/phase/role/rate/model validation |
| `criresp_over20` | C -> S | bool | admin check; no rate limit |
| `cri_roundend` | S -> C | uint4 winner + four uint8 statistics | paired |

## Pathowogen

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| briefing family | S -> selected C | none | paired |
| commander/contractor transmit | S -> selected C | string | paired; loops can resend full list repeatedly |
| extraction heli/point family | S -> C | entity or vector | paired; client globals require cleanup |
| `ZB_Pathowogen_RoundEnd` | S -> C | uint3 outcome, Lua table player report | paired; unversioned potentially large table with entity keys |

Pathowogen is normally disabled, but receivers remain loaded.

## Riot, Gang Wars, Superfighters and Slug Arena

| Channel | Direction | Ordered schema | Status |
|---|---|---|---|
| `riot_start`, `riot_roundend` | S -> C | none | paired |
| `gwars_start`, `gwars_roundend` | S -> C | none | paired |
| `supfight_start` | S -> C | vector point | paired; launch lacks point validation |
| `supfight_end` | S -> C | entity winner/null | paired; delayed sampling |
| `scugarena_start` | S -> C | none | paired |
| `scugarena_end` | S -> C | entity winner/null | paired; delayed sampling |

## Event mode

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `event_start` | S -> C | none | paired |
| `event_end` | S -> C | entity winner/null | paired; delayed sampling |
| `event_eventers_update` | S -> C | Lua table SteamIDs | paired; implicit schema |
| `event_loot_sync` | S -> authorized C | Lua table entries | paired; no explicit total size/version |
| `event_loot_add` | C -> S | Lua table `{weight,class}` | admin/eventer only; field presence only, no type/range/class/catalog/rate/size checks; persists data |
| `event_loot_remove` | C -> S | uint16 index | admin/eventer and existing index; no rate limit |
| `event_loot_request` | both | empty request/empty open-menu signal | overloaded; server authorizes request |
| `event_loot_update` | unresolved | unresolved | registration-only dormant |

## Highest-priority protocol defects

1. `HMCD_RoundStart` traitor count versus serialized roster count.
2. `bomb_enter` world-interaction trust gap.
3. Duplicate/unbounded admin queue table protocols.
4. Base TDM, CStrike winner, HL2DM and Defense new-wave mismatches.
5. `organism_send` unversioned/high-frequency Lua-table snapshots and invalid-owner client ordering.
6. Fear client-authored light sample/global target race.
7. Crisis customization outside intended phase/role.
8. Event persistent loot edits with weak validation.
9. Defense commander/admin implicit table schemas.
10. Disabled/zero-chance modes retaining live receivers/global state.

## Required runtime validation

- Capture exact write/read bits for every channel/branch.
- Fuzz all C -> S endpoints with wrong phase/role/state, invalid IDs/entities, oversized data and rapid replay.
- Instrument duplicate `net.Receive` registrations and effective handlers.
- Measure organism snapshot bytes/CPU across player/NPC/ragdoll populations and verify private/public field exposure.
- Audit one-sided/dormant channels against external addons before removal.
- Freeze authoritative outcomes before delayed presentation packets.
