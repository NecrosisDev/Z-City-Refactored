# Cross-Mode Packet Matrix

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / Homicide endpoint closure batch added`  
**Reviewed:** 2026-07-12

This is the authoritative packet index for the current research baseline. A row is `matched` only when both writer and reader were traced with the same ordered schema. `Partial` means at least one endpoint, conditional branch, duplicate registration, or validation rule remains unresolved. Lua-table payloads are recorded as opaque until their complete shape and size bounds are known.

## Core round and administration

| Channel | Direction | Writer / reader | Ordered schema | Authority and validation | Status |
|---|---|---|---|---|---|
| `RoundInfo` | S -> C | round system / client round receiver | string mode ID; int4 round state | server authoritative; client invokes local mode callbacks | matched |
| `FadeScreen` | S -> C | `zb.AddFade` / unresolved client | none | server recipients; reader missing | partial |
| `updtime` | S -> C | unresolved / client | float round time; float start; float begin | sender and update cadence unresolved | partial |
| `ZB_SpectatePlayer` | S -> C | unresolved / client spectator | entity target; entity previous; int4 view mode | sender/recipient rules unresolved | partial |
| `ZB_SendModesInfo` | S -> admin C | round/admin system / mode manager | Lua table of mode records | recipient admin-gated; table shape/version implicit | partial |
| `ZB_SendRoundList` | S -> admin C | round/admin system / mode manager | Lua table future list; string next; string force | recipient admin-gated; table shape implicit | partial |
| `ZB_RequestRoundList` | admin C -> S | mode manager / round/admin system | none | valid player + `IsAdmin()` | matched |
| `ZB_UpdateRoundList` | admin C -> S | mode manager / round/admin system | Lua table list; bool force update | admin checked; no length/type/ID/duplicate limits; bool ignored | unsafe/partial |
| `ZB_NotifyRoundListChange` | S -> admin C | round/admin system / manager | string actor name | recipients are admins | matched in traced protocol |
| `SendAvailableModes` | S -> admin C | legacy admin system / unresolved | Lua table `{key,name}` records | admin recipient; current client consumer not found | legacy/partial |
| `AdminSetGameMode` | admin C -> S | admin UI / duplicate receivers | string command; string mode key; bool queue | admin checked; duplicate last-writer behavior expected; launch eligibility condition unreachable in later receiver | duplicate/unsafe |
| `AdminEndRound` | admin C -> S | admin UI / server | none | `IsAdmin()` | matched |
| `AdminSetGameQueue` | C -> S | unresolved/legacy UI / duplicate receivers | Lua table queue | admin checked; no shape/size/ID bounds | duplicate/legacy |
| `RequestGameQueue` | unresolved | unresolved | unresolved | registered but active path unresolved | legacy/partial |
| `SendGameQueue` | S -> admin C | legacy sync / unresolved | Lua table queue | recipient admin; client unresolved | legacy/partial |
| `QueueEmptiedNotification` | S -> admin C | legacy queue / unresolved | none | server recipients | legacy/partial |
| `QueueModifiedNotification` | S -> admin C | legacy queue / unresolved | string actor; string action | server recipients | legacy/partial |

## TDM and Counter-Strike

| Channel | Direction | Ordered schema | Validation / defect | Status |
|---|---|---|---|---|
| `tdm_start` | S -> C | base TDM writes none; client reads string round type | schema mismatch; CStrike writes the inherited reader's expected string | mismatched |
| `tdm_roundend` | S -> C | none | server authoritative | matched |
| `tdm_open_buymenu` | S -> one C | none | server calls for alive player; client rechecks alive/time | matched |
| `tdm_buyitem` | C -> S | Lua table `{category,itemName[,attachmentID]}` | checks mode/time/catalog/money/weapon ownership; lacks alive, rate, size, team metadata and attachment allowlist validation | unsafe/partial |
| `CS_Intermission` | S -> C | objective/intermission payload not fully enumerated in current catalog | objective point/entity branches unresolved | partial |
| `CS_Killfeed` | S -> C | unresolved | writer/reader and schema unresolved | partial |
| `CS_Roundover` | S -> C | server writes numeric winner through bool; client consumes team result | all Lua numeric values are truthy, collapsing `0|1|3` identity | mismatched |

## Deathmatch

| Channel | Direction | Ordered schema | Validation / defect | Status |
|---|---|---|---|---|
| `dm_start` | S -> C | vector zone center; float radius | server authoritative; stale global zone state remains possible | matched schema |
| `dm_end` | S -> C | entity winner; entity most violent | entity validity and duplicate-reward identity require validation | matched schema/unsafe entities |

## Homicide and Fear

| Channel | Direction | Ordered schema | Authority and validation | Status |
|---|---|---|---|---|
| `HMCD_RoundStart` | S -> one C | bool traitor; bool gunner; string type; bool default screen; string subrole; bool main traitor; string word1; string word2; uint traitor count; conditional repeated color+name; string profession | server count includes all traitors while roster writes only appearance-backed entries; no independent roster count/version/recovery boundary | mismatched conditional branch |
| `HMCD(StartPlayersRoleSelection)` | S -> selected C and C -> S acknowledgement | S writes role string; C acknowledgement has no payload | server checks sender membership in choosing list; feature hard-disabled upstream | matched branch but unreachable |
| `HMCD(EndPlayersRoleSelection)` | S -> C | none | client removes the active role-selection panel | matched branch but unreachable upstream |
| `HMCD(SetSubRole)` | S -> C expected | client reader expects string; no sender found in loaded Homicide source | no server authorization or allowed-value contract can be established without a writer | reader-only/incomplete |
| `HMCDPoliceRole` | registered only | no writer or receiver found in traced Homicide files | no functional endpoint established | dormant registration |
| `hmcd_announce_traitor_lose` | S -> C | entity traitor; bool alive | client validates entity before presentation | matched schema/unsafe entity lifecycle |
| `HMCD_TraitorDeathState` | S -> main traitor C | string appearance name; bool alive | server recipient-filtered; client caches state by appearance name | matched schema |
| `HMCD_RequestTraitorStatuses` | C -> S | none | requester must be traitor and main traitor; server replies with one death-state packet per appearance-backed traitor | matched |
| `hmcd_roundend` | S -> C | uint13 traitor count + entities; uint13 gunner count + entities | duplicate registration; client trusts read entities | matched schema/unsafe entities |
| `HMCD_UpdateTraitorAssistants` | S -> main traitor C | uint8 count; repeated color, string name, string SteamID | client replaces `MODE.TraitorsLocal`; no explicit string/count version contract beyond uint8 | matched schema/partial lifecycle |
| `ZB_TraitorWinOrNot` | server hook, not net packet | traitor entity; winner identifier | project hook surface; downstream consumers need inventory | non-network public surface |
| `check_lightness` | S -> all C; C -> S | S sends entity target; each C returns vector sample | bounded vector only; no target ID, visibility, proximity, authority or per-target rate; global target race | unsafe bidirectional |

### Exact Homicide endpoint evidence

- Server writer/helpers and acknowledgement receiver: `gamemodes/zcity/gamemode/modes/homicide/sv_homicide.lua`, blob `af101a8e73b170ca67e5a8c951ec83dd0655e0c8`.
- Round-start/end and role-panel readers: `gamemodes/zcity/gamemode/modes/homicide/cl_homicide.lua`, blob `6e15a2b3eae790d1e9525c78a5344f3efcfd1de3`.
- Assistant roster and death-state readers: `gamemodes/zcity/gamemode/modes/homicide/cl_hud.lua`, blob `87356c1f96336ca160841293500b374dc668d089`.
- This closes endpoint identity for the assistant/death-state and role-selection family. Exact line offsets remain pending in the repository-wide source-line pass.

## HL2DM and CO-OP

| Channel | Direction | Ordered schema | Validation / defect | Status |
|---|---|---|---|---|
| `hl2dm_start` | S -> C | none | server authoritative | matched |
| `hl2dm_roundend` | S -> C | server writes none; client reads int3 winner | schema mismatch | mismatched |
| `ZB_RequestAirStrike` | C -> S | none; server derives target from sender eye trace | leader, remaining-strike and global cooldown checks; sky/entity validity incomplete; no explicit rate beyond cooldown | matched/partial validation |
| `coop_start` | S -> C | none | server authoritative | matched |
| `coop_roundend` | S -> C | none | server authoritative; save/changelevel may race presentation | matched schema |

## Defense

| Channel | Direction | Ordered schema | Validation / defect | Status |
|---|---|---|---|---|
| `defense_start_vote` | S -> C | current options/payload not fully enumerated | reader exists; complete schema pending | partial |
| `defense_submit_vote` | C -> S | selected option (verified range 1..3) | one-second per-player rate; vote phase/eligibility details need full pairing | partial |
| `defense_change_vote` | mixed | unresolved | endpoints/schema unresolved | partial |
| `defense_vote_result` | S -> C | unresolved | tie/random selection behavior verified, payload not fully recorded | partial |
| `defense_vote_update` | S -> C | unresolved | table/count schema unresolved | partial |
| `defense_show_selected_mode` | S -> C | unresolved | presentation endpoint only partially traced | partial |
| `npc_defense_start` | S -> C | unresolved/presentation start | endpoint pairing incomplete | partial |
| `npc_defense_newwave` | S -> C | float deadline; int4 wave | traced client reads only deadline | mismatched |
| `npc_defense_roundend` | S -> C | unresolved | client presentation known; full schema pending | partial |
| `npc_defense_prepphase` | S -> C | preparation countdown/state unresolved | full schema pending | partial |
| `StartWaveMusic` / `StopWaveMusic` | S -> C | unresolved | external music definitions/owners unresolved | partial |
| `defense_boss_incoming` | S -> C | unresolved | endpoint/schema unresolved | partial |
| `defense_highlight_last_npcs` | S -> C | unresolved | server counterpart not located in fetched top-level files | partial |
| `RequestSupport` | C -> S | string command | server handler, authorization, cost, cooldown, allowed values and rate unresolved | unsafe/partial |

## Crisis Response

| Channel | Direction | Ordered schema | Validation / defect | Status |
|---|---|---|---|---|
| `criresp_start` | S -> C | none | opens menu; client sends customization | matched |
| `criresp_ready` | C -> S | none | assigned player and state 0 checked; no revoke path | matched/limited lifecycle |
| `criresp_readycount` | S -> C | uint8 ready; uint8 total | server authoritative | matched |
| `criresp_begin` | S -> C | none | closes menu and starts presentation | matched |
| `criresp_over20` | C/admin -> S | bool | server checks `IsAdmin()` then mutates replicated convar | matched |
| `criresp_custom` | C -> S | uint8 primary; string bodygroups; uint4 gear count; repeated uint8 gear IDs | string length, count, IDs and duplicate gear partly bounded; no sender role/phase/rate/model bodygroup validation | unsafe/partial |
| `cri_roundend` | S -> C | uint4 winner; uint8 killed; uint8 incapacitated; uint8 arrested; uint8 total | matched; client input lock side effects require lifecycle validation | matched |

## Riot, Gang Wars, Superfighters and Slug Arena

| Channel | Direction | Ordered schema | Validation / defect | Status |
|---|---|---|---|---|
| `riot_start` / `riot_roundend` | S -> C | none | server authoritative | matched |
| `gwars_start` / `gwars_roundend` | S -> C | none | server authoritative | matched |
| `supfight_start` | S -> C | vector zone/spawn position | missing/empty RandomSpawns can invalidate source | matched schema/unsafe source |
| `supfight_end` | S -> C | entity winner | delayed resampling and entity validity | matched schema/unsafe timing |
| `scugarena_start` | S -> C | none | server authoritative | matched |
| `scugarena_end` | S -> C | entity winner | delayed resampling/entity validity | matched schema/unsafe timing |

## Event mode

| Channel | Direction | Ordered schema | Authority and validation | Status |
|---|---|---|---|---|
| `event_start` | S -> C | none | server authoritative | matched |
| `event_end` | S -> C | entity winner | delayed winner resampling/entity validity | matched schema/unsafe timing |
| `event_eventers_update` | S -> C | Lua table eventer identifiers | unversioned table; recipient/data exposure rules need full pairing | partial |
| `event_loot_sync` | S -> C | custom loot data, exact shape unresolved | recipient logic includes a loop-variable bug that can expose data broadly | unsafe/partial |
| `event_loot_request` | bidirectional/overloaded | C request branch has no verified payload; S branch opens/syncs menu | one name carries different direction/meaning, obscuring validation and compatibility | overloaded/partial |
| `event_loot_add` | C -> S | Lua table loot record | authorized admin/eventer path; only field-presence checks, no type/range/class/length/size/rate validation | unsafe |
| `event_loot_remove` | C -> S | uint16 index | authorization exists in mode logic; bounds/rate and concurrent mutation need full validation | partial |
| `event_loot_update` | unresolved | unresolved | registered but no verified use | legacy/unresolved |

## Pathowogen

| Channel | Direction | Ordered schema | Authority and validation | Status |
|---|---|---|---|---|
| `zb_furbriefing` | S -> selected C | none | role recipient selected server-side | matched |
| `zb_furfurbriefing` | S -> selected C | none | role recipient selected server-side | matched |
| `zb_furtraitorbriefing` | S -> selected C | none | role recipient selected server-side | matched |
| `zb_contractortransmit` | S -> C | string message | server loop can resend full recipient list repeatedly | matched schema/duplicate sends |
| `zb_commandertransmit` | S -> C | string message | same repeated-broadcast risk | matched schema/duplicate sends |
| `zb_extractionheli` | S -> C | entity helicopter | client stores global entity; validity/removal/mode-switch lifecycle incomplete | matched schema/unsafe entity lifecycle |
| `zb_extractionpoint` | S -> C | vector point | repeated sends possible; clear/reset semantics incomplete | matched schema/partial lifecycle |
| `zb_traitorextractionpoint` | S -> C | vector point | client rendering path can leak `cam.IgnoreZ(true)` on early return | matched schema/client state defect |
| `ZB_Pathowogen_RoundEnd` | S -> C | uint3 outcome; Lua table keyed by player entities with original/current identity, role, alive and escaped state | no explicit count/size/version; mutable nested/entity-keyed data and disconnect behavior unresolved | unsafe/partial |
| Pathowogen derma/UI channels | mixed | unresolved | additional verified `derma/` files not behavior-traced | unresolved |

## Cross-packet defect groups

1. **Schema mismatches:** `tdm_start`, `CS_Roundover`, `hl2dm_roundend`, `npc_defense_newwave`, conditional `HMCD_RoundStart`.
2. **Untrusted client payloads:** admin queue/list tables, `tdm_buyitem`, Fear light vectors, Crisis customization, Defense support, Event loot edits.
3. **Opaque Lua tables:** admin lists/queues, Event loot/eventers, Pathowogen end report; all lack explicit version and bounded record counts.
4. **Duplicate/overloaded names:** round admin protocol generations, duplicated Homicide registration, overloaded `event_loot_request`.
5. **Entity payloads:** winner, target, helicopter and roster entities are often read without validity or disconnect semantics.
6. **Phase/rate omissions:** many client requests lack round-state, role, alive, cooldown or flood controls.
7. **Delayed authority drift:** winner packets are built after end in several modes instead of freezing result at transition.

## Required completion trace

- Enumerate every `util.AddNetworkString`, `net.Receive`, `net.Start`, `net.Write*` and `net.Read*` in all loaded files, including auxiliary mode directories and entities.
- Record exact source blob/line for every endpoint and branch; pair conditional counts with independent record counts.
- Measure maximum encoded size and define explicit limits for strings, tables, repeated records and request frequency.
- Resolve Defense auxiliary files, Counter-Strike objective entities, remaining Fear endpoints, Pathowogen derma files and legacy admin clients.
- Runtime-capture all known mismatches and duplicate receiver effective behavior before implementation changes.
