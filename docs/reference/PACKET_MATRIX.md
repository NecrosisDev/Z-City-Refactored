# Cross-System Packet and Trust-Boundary Matrix

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified; unresolved endpoints explicitly labeled  
**Reviewed:** 2026-07-12

This is the canonical inventory for verified round, mode, organism, fake-ragdoll, and player-class channels. `paired` requires both endpoints and matching conditional schemas; registration alone does not prove a live protocol.

## Status and validation standard

- `paired`: writer/reader agree.
- `mismatch`: endpoints exist but field type/count/branch differs.
- `one-sided`: only writer or reader located.
- `overloaded`: same name carries multiple directions/schemas.
- `legacy/duplicate`: overlapping generation/registration.
- `dormant`: no live caller/consumer found.

Every C -> S endpoint must validate authorization, active subsystem/mode/phase, alive/incapacitated/team/role state, primitive/table shape/size, server-side ID resolution, ownership/distance/line of sight, rate limits, and replay/non-idempotent transitions.

## Core round and spectator synchronization

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `RoundInfo` | S -> C | string mode ID, int4 state | paired; server authoritative |
| `FadeScreen` | S -> C | none | writer-only/dormant; other fade paths exist |
| `updtime` | S -> C | float round time/start/begin | paired |
| `ZB_ChooseSpecPly` | C -> S | uint32 key | dead/key checks; no explicit rate/general allowlist |
| `ZB_SpectatePlayer` | S -> C | entity current, entity previous, int4 mode | paired response |

## Round administration and queues

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| `ZB_SendModesInfo` | S -> admin C | Lua table records | paired; implicit schema |
| `ZB_SendRoundList` | S -> admin C | table list, string next, string force | paired; implicit schema |
| `ZB_RequestRoundList` | admin C -> S | none | admin check; no rate |
| `ZB_UpdateRoundList` | admin C -> S | table list, bool force | no length/type/ID/duplicate bounds; bool unused |
| `AdminSetGameMode` | admin C -> S | strings command/mode, bool queue | duplicate receivers; later launch eligibility condition ineffective |
| `AdminEndRound` | admin C -> S | none | admin check; no rate |
| `AdminSetGameQueue` | admin C -> S | Lua table | duplicate/legacy; unbounded |
| `SendAvailableModes` | S -> admin C | Lua table | current manager has no reader |
| `SendGameQueue` | S -> admins | Lua table `zb.QueuedModes` | separate legacy server list; no current reader |
| `RequestGameQueue` | none found | none | registration-only |
| queue notification family | S -> admins | none or actor/action strings | no current readers |

Active `ZB_*` and legacy queue protocols operate on different server lists, not only different transport names.

## Competitive modes and objectives

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| `tdm_start` | S -> C | base writes none; client reads string; CStrike writes string | base mismatch |
| `tdm_roundend` | S -> C | none | paired |
| `tdm_open_buymenu` | S -> one C | none | paired; client alive/time recheck |
| `tdm_buyitem` | C -> S | Lua table category/item/optional attachment | no table/rate/alive/team/TeamBased/attachment allowlist bounds |
| `CS_Intermission` | S -> C | bool team, int6 rounds | paired |
| `CS_Killfeed` | S -> C | two team bools, killer/victim strings | paired |
| `CS_Roundover` | S -> C | bool winner, string text | numeric `0|1|3` passed to bool, collapsing identity |
| `bomb_look` | S -> one C | entity bomb/null | paired |
| `bomb_enter` | C -> S | string code | no mode/phase/ownership/distance/LOS/rate/length/digit validation |
| `bomb_planted` | S -> C | none | paired |
| `dm_start` | S -> C | vector center, float distance | paired |
| `dm_end` | S -> C | entity winner/null, entity mostViolent/null | paired; delayed sampling/global state |

## Homicide and Fear

`HMCD_RoundStart` common prefix is paired: traitor/gunner bools, type string, default-screen bool, subrole string, main-traitor bool, two strings, uint13 traitor count. The main-traitor branch serializes only appearance-backed roster records while the client loops the total traitor count, causing stream desynchronization.

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| `HMCD(StartPlayersRoleSelection)` | both | outbound role string; inbound empty ack | membership check; overloaded; feature disabled |
| `HMCD(EndPlayersRoleSelection)` | S -> C | none | paired |
| `HMCD(SetSubRole)` | expected S -> C | string | client reader only |
| `HMCDPoliceRole` | unresolved | unresolved | registration-only |
| `hmcd_announce_traitor_lose` | S -> C | entity, bool | paired |
| `HMCD_TraitorDeathState` | S -> main-traitor C | string appearance, bool alive | paired |
| `HMCD_RequestTraitorStatuses` | C -> S | none | main-traitor check; no rate |
| `hmcd_roundend` | S -> C | counted traitor entities then gunners | paired; duplicate registration/entity assumptions |
| `HMCD_UpdateTraitorAssistants` | S -> main-traitor C | uint8 count, repeated color/name/SteamID | paired |
| `check_lightness` | both | S -> C entity; C -> S vector | global target slot; client measurement not bound to requested entity/client |

Fear inherits Homicide transport despite `CanLaunch=false`.

## HL2DM and CO-OP

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| `hl2dm_start` | S -> C | none | paired |
| `hl2dm_roundend` | S -> C | server none; client int3 winner | mismatch |
| `ZB_RequestAirStrike` | C -> S | none; server eye-trace target | leader/strikes/global cooldown; active-mode/alive/state checks incomplete |
| `coop_start`, `coop_roundend` | S -> C | none | paired |

## Organism, injury, and blood effects

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| `organism_send` | S -> C | Lua snapshot; bool force/protection/moreInfo/add | paired but unversioned/high-cost; client calls owner method before validity; developer sends whole table |
| `organism_sendply` | unresolved | unresolved | registration + commented reader only |
| `VirusStageUpdate` | S -> infected C | int8 stage | no reader |
| `pulse` | S -> owner C | none | no caller/reader found |
| `bloodsquirt2` | S -> C | entity, bone string, matrix, position, direction | paired; effect/model assumptions |
| `bloodsquirt` | S -> C | same pattern | client reader; writer not fully paired |
| `addfountain` | S -> C | entity, force vector | reader only |
| `hg_bloodimpact` | S -> C | position, velocity, float multiplier, int8 amount | reader only; client clamps amount |
| wound NetVars | S -> C | Lua wound tables | overlaps organism snapshot authority |

Commands `hg_fixdislocation` and breath controls are separate trust surfaces; dislocation parsing can reach `math.Round(nil)` and other-target range is implicit in eye trace.

## Fake-ragdoll and get-up transport

| Channel/state | Direction | Schema | Validation/status |
|---|---|---|---|
| `Player Ragdoll` | S -> C | entity player, entity ragdoll/null | reader calls undefined/custom `net.ReadEntity2()` expecting entity+index; no generation/transition type; actual ownership mainly follows NWEntity proxies |
| NWEntity `FakeRagdoll` | S -> C state | entity ragdoll/null | client proxy performs ownership, organism alias, render/camera and `Fake`/`FakeUp` hooks; asynchronous with packet/entity creation |
| NWEntity `FakeRagdollOld` | S -> C state | entity old body/null | smooth get-up state; stale/ordering risk |
| NWEntity `RagdollDeath` | S -> C state | entity death body/null | overridden `GetRagdollEntity` and client death body ownership |
| ragdoll NWEntity `ply` | S -> C state | owner player | client identity link; creation/PVS timing risk |
| `Override Spawn` | S -> C | entity player | marks client spawn suppression during respawn-based get-up; duplicates global server `OverrideSpawn` concept; no transaction/generation |

Critical defects: three overlapping ownership channels (server fields/NW state/custom packet), undefined reader helper, no sequence/generation, NULL ambiguity, and no rollback if respawn/get-up fails.

## Player-class transport

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| `playerclass` | S -> C | string class ID (`"nil"` clears), Lua table data | client writes class, calls new `On(data)`, emits hook; old client class `Off` is not called; table unversioned/unbounded |
| `playerclass` | C -> S | string class ID, Lua table data | **critical:** server checks only `IsValid(ply)` then calls `SetPlayerClass`; no legitimate repository sender, permission, mode/role/phase, rate, size/depth/type, or allowlist validation |

The same overloaded channel lets a client request any registered class and arbitrary data, potentially triggering model/loadout/armor/organism/movement/fake/NPC relationship changes. This is the highest-priority verified security boundary.

## Defense

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| vote family | mixed | float deadline, int4 choices, table updates/results | mode/phase/rate checks; implicit tables |
| `npc_defense_newwave` | S -> C | float deadline, int4 wave | client reads only float |
| wave/music/boss family | S -> C | none/string | paired |
| `defense_highlight_last_npcs` | S -> C | table entity indices | paired periodic list |
| `RequestSupport` | C -> S | string support type | Commander/mode/incapacitation/catalog/rate/global cooldown; alive implicit |
| `defense_commander_menu` | both | empty request, table response | role/alive/rate; overloaded |
| `defense_commander_purchase` | C -> S | Lua table requests | raw/table/count/catalog/rate/points checks; implicit shape/lower bound |
| `defense_commander_notification` | S -> C | string, int16 | paired |
| `defense_commander_points` | none | none | registration only; NWInt used |
| `defense_player_role_assigned` | S -> C | string role | no reader; NWString used |
| `defense_admin_command` | C -> S | string command, Lua table args | admin allowlist; no sender/rate/size/active-mode guard |

## Crisis Response

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| start/ready/count/begin | mixed | empty or two uint8 counts | partial phase/assignment; no unready |
| `criresp_custom` | C -> S | uint8 primary, bodygroup string, uint4 count, uint8 IDs | partial bounds; no mode/phase/role/rate/model checks |
| `criresp_over20` | C -> S | bool | admin; no rate |
| `cri_roundend` | S -> C | uint4 winner + four uint8 stats | paired |

## Pathowogen and additional modes

| Channel family | Direction | Schema | Status |
|---|---|---|---|
| Pathowogen briefings | S -> selected C | none | paired |
| commander/contractor transmit | S -> selected C | string | repeated full-list sends possible |
| extraction body/points | S -> C | entity/vector | paired; global cleanup needed |
| `ZB_Pathowogen_RoundEnd` | S -> C | uint3 outcome, Lua table report | unversioned/large/entity keys |
| Riot/Gang start/end | S -> C | none | paired |
| Superfighters start/end | S -> C | vector / entity | launch validation and delayed sampling risks |
| Slug Arena start/end | S -> C | none / entity | delayed sampling |

Pathowogen and zero-chance modes retain readers while normally unavailable.

## Event mode

| Channel | Direction | Schema | Validation/status |
|---|---|---|---|
| start/end | S -> C | none / entity | paired; delayed result |
| eventers/loot sync | S -> C | Lua tables | implicit/unversioned |
| `event_loot_add` | C -> S | table weight/class | admin/eventer; presence only, no type/range/catalog/rate/size; persists data |
| `event_loot_remove` | C -> S | uint16 index | auth/existence; no rate |
| `event_loot_request` | both | empty | overloaded; server authorizes request |
| `event_loot_update` | unresolved | unresolved | registration only |

## Highest-priority protocol defects

1. `playerclass` permits arbitrary client class assignment and arbitrary table data.
2. `HMCD_RoundStart` total traitor count does not match serialized roster record count.
3. `bomb_enter` lacks interaction ownership, phase, format, distance and rate validation.
4. Duplicate/unbounded round-admin queue tables and two server queue models.
5. Fake-body state has no generation and overlaps server fields, NWEntities, packet/index and proxies; packet reader depends on undefined `net.ReadEntity2`.
6. `organism_send` is unversioned/high-frequency and dereferences owner before client validity check.
7. Base TDM, CStrike winner, HL2DM and Defense new-wave schemas mismatch.
8. Fear light measurement trusts a client/global target slot.
9. Crisis customization accepts persistent data outside intended phase/role.
10. Event persistent loot edits and Defense commander/admin tables remain weakly typed.

## Required runtime validation

- Capture exact write/read bits and transition generation for every channel/branch.
- Fuzz every C -> S endpoint with wrong permission/phase/role/state, invalid IDs/entities, oversized/deep tables and replay.
- Disable or guard client `playerclass` assignment before public deployment.
- Instrument duplicate receivers/effective handlers and packet/NW ordering.
- Measure organism/fake transport and forced-PVS cost across populations.
- Audit dormant/one-sided channels against external addons before removal.
- Freeze authoritative outcomes before delayed presentation packets.
