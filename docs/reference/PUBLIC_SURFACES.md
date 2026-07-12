# Public Surfaces Inventory

**Work package:** `WP-RESEARCH-001`  
**Scope:** bootstrap, mode/round framework, admin mode UI, and all currently cataloged mode surfaces  
**Status:** `partial / executable-source verified`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Reviewed:** 2026-07-12

This inventory tracks refactor-sensitive globals, hooks, network channels, convars, commands, persistence and trust boundaries. Absence is not evidence that a surface does not exist.

## Core globals and registries

| Surface | Owner | Realm | Contract/risk |
|---|---|---|---|
| `hg` / `hg.loaded` | global loader | local server/client copies | global addon namespace; loaded false during bootstrap, true before `HomigradRun`; ixhl2rp early return leaves false |
| `zb` | gamemode/bootstrap libraries | local server/client copies | mode registry, round state, points, teams, admin UI and many subsystem globals |
| `zb.modes` | mode loader | server/client | mode name -> table; server/client keys must match network-visible IDs |
| `zb.modesHooks` | mode loader | server/client | mode -> function key -> callback; reset on loader execution |
| `MODE` | loader/mode files | temporary global | assembly scratch table; every function becomes a hook candidate |
| `CurrentRound()` / `NextRound()` | round system/client | realm-local globals | resolves base/submode and future mode; broad consumer surface |
| `COMMANDS` | unresolved command framework | primarily server | admin command entries; dispatcher/normalization/collision behavior untraced |
| mode/client globals | individual modes | mixed | repeated `StartTime`, `dmmusic`, `hmcdEndMenu`, winner flags, zone/extraction state and stations collide across modes/hotload |

## Core hook contract

### Emitted

| Hook | Emitter | Contract |
|---|---|---|
| `HomigradRun` | global loader | no args, after main addon load |
| `ZB_PreRoundStart` | round system | state `3 -> 0` preparation |
| `TTTPrepareRound` | round system | compatibility emission at same transition |
| `ZB_StartRound` | round system | after mode start/next selection |
| `ZB_EndRound` | round system | after mode end |
| `RoundInfoCalled` | client RoundInfo receiver | mode name before assigning client state |
| `ZB_TraitorWinOrNot` | Homicide | traitor entity + winner identifier |
| dynamic mode function names | mode loader | invokes selected mode function as `func(modeTable, ...)`; dot-defined methods suffer argument shift |

### High-impact registrations

| Hook | Identifier/owner | Risk |
|---|---|---|
| `Think` | `zb-think` | core lifecycle, once/sec |
| `PlayerInitialSpawn` | round sync + admin sync | multiple handlers; one duplicate identifier in round system |
| `RoundStateChange` | Homicide reset | waits for stale state `2`; emitter unresolved |
| `ZB_RoundStart` | CO-OP reset | core verified emitter is `ZB_StartRound`, so listener likely dead |
| `PostCleanupMap` | airstrike/Fear/CO-OP systems | global cleanup hooks; inactive-mode effects require gating audit |
| dynamic `Think/ScareThatGuy<UserID>` | Fear event | per-player hook; cleanup/UserID reuse risk |
| dynamic `PlayerUse/dooruse<EntIndex>` | Fear environment | global hook names; no-door/cleanup risk |
| `Boxes Think` | Event/Superfighters | emitted from multiple timers/paths rather than conventional hook registration |

## Core round/admin channels

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `RoundInfo` | S -> C | string mode, int4 state | matched; server authoritative |
| `FadeScreen` | S -> C | none | client endpoint not fully traced |
| `updtime` | S -> C | float round time, float start, float begin | sender unresolved |
| `ZB_SendModesInfo` | S -> admin C | table mode records | server recipient-gated; table schema implicit |
| `ZB_SendRoundList` | S -> admin C | table list, string next, string force | table schema implicit |
| `ZB_RequestRoundList` | admin C -> S | none | admin checked |
| `ZB_UpdateRoundList` | admin C -> S | table list, bool forceUpdate | admin checked; no shape/size/ID bounds; bool read but unused |
| `AdminSetGameMode` | admin C -> S | string command, string mode, bool queue | duplicate receivers; later eligibility condition unreachable after admin guard |
| `AdminEndRound` | admin C -> S | none | admin checked |
| `AdminSetGameQueue` | C -> S | table queue | duplicate/legacy; admin checked but unvalidated |
| `SendGameQueue` / `RequestGameQueue` / queue notifications | mixed | tables/strings/none | overlapping legacy protocol; active clients unresolved |

**Duplicate hazard:** `sv_roundsystem.lua` repeats multiple network registrations, receivers, a `PlayerInitialSpawn` hook identifier and `zb.SyncQueueToAdmins`; later name-keyed definitions are expected effective but need runtime proof.

## Competitive/Homicide packet highlights

| Channel | Direction | Schema / defect |
|---|---|---|
| `tdm_start` | S -> C | base TDM writes nothing; client reads string; CStrike writes expected string |
| `tdm_buyitem` | C -> S | table `{category,item[,attachment]}`; no alive/rate/size/team/attachment-allowlist validation |
| `CS_Roundover` | S -> C | winner written bool despite numeric team identity |
| `dm_start` | S -> C | vector zone center + float radius |
| `HMCD_RoundStart` | S -> C | variable role/type packet; traitor count can exceed roster entries and desynchronize reads |
| `HMCD_UpdateTraitorAssistants` | S -> C | uint8 count then color/name/SteamID entries; client endpoint unresolved |
| `hmcd_roundend` | S -> C | uint count+entities for traitors, then gunners; duplicate registration and entity validity assumptions |
| `check_lightness` | S <-> C (Fear) | server sends entity; clients return vector | bounded vector only; client-authoritative, global target, no target ID/visibility/rate authority |

## Team/PvE packet highlights

| Channel | Direction | Schema / defect |
|---|---|---|
| `hl2dm_roundend` | S -> C | server writes none; client reads int3 |
| `npc_defense_newwave` | S -> C | float deadline + int4 wave; traced client reads only float |
| `RequestSupport` | C -> S | string command | server endpoint/authorization/cost/rate unresolved |
| `criresp_custom` | C -> S | uint8 primary, bodygroup string, uint4 count, uint8 gear IDs | partial bounds; any phase/client, no rate/bodygroup model validation |
| `cri_roundend` | S -> C | uint4 winner + four uint8 statistics | matched in traced endpoints |
| `ZB_RequestAirStrike` | C -> S | no payload; server uses sender eye trace | leader/strike/cooldown checks; entity/sky validity incomplete |

## Pathowogen surfaces

| Channel | Direction | Schema / notes |
|---|---|---|
| `zb_furbriefing`, `zb_furfurbriefing`, `zb_furtraitorbriefing` | S -> C | no payload; create role-specific panels |
| `zb_commandertransmit`, `zb_contractortransmit` | S -> C | string message | server loops can resend to full recipient list repeatedly |
| `zb_extractionheli` | S -> C | entity helicopter | client stores `zb.uwucopter`; validity/state lifecycle incomplete |
| `zb_extractionpoint`, `zb_traitorextractionpoint` | S -> C | vector point | client global extraction state; repeated sends possible |
| `ZB_Pathowogen_RoundEnd` | S -> C | uint3 outcome + Lua table keyed by players | unbounded/versionless complex table; entity disconnect semantics unresolved |

Other Pathowogen surfaces:
- point registries `UWU_GlideHeli`, `UWU_DeltaSquad`, `SCRAPPERS_BIGBOX`, `SCRAPPERS_SMALLBOX`, `SCRAPPERS_VEHICLE`;
- player local var `zb_Pathowogen_Extraction`;
- global simfphys convars modified without restoration;
- Glide vehicle APIs, fake-ragdoll weld extraction, class/organism/inventory/armor/loot contracts;
- global timers and EntIndex-based extraction timers.

## Fear surfaces

- Mode registry ID `fear`, base `hmcd`, inherited submodes renamed `standard2`/`soe2`; hard-disabled launch.
- Network/player state: `disappearance`, `afterlife`, `willsuicide`, light color, custom collision, shadows/sound suppression.
- Event registry `MODE.Events`, `MODE.StartedEvents[UserID]`; `scary_black_guy` spawns `ent_zc_anim` and uses dynamic Think hook.
- External entities/services: `bot_fear`, fake ragdoll, `hg.BreakNeck`, visibility/light sampling, SendLua, global audio stations and screen effects.
- Risk: directly registered hooks/timers may remain active while mode is unavailable/inactive; exact gating matrix pending.

## ConVars and persistence

| Surface | Owner | Contract/risk |
|---|---|---|
| `hg_loadcontent` | global loader | replicated/archive toggle; workshop mounting calls commented |
| `zb_forcemode` | round system | server force mode, reset to `random` on source load |
| client presentation convars | spectator/Homicide/Crisis/Defense/Event | user settings; repeated/global acquisition patterns |
| `sv_simfphys_fuel`, `sv_simfphys_fuelscale` | external addon, mutated by Pathowogen | global server behavior changed without restoration |
| `data/zbattle/modeschances.json` | mode registry | mode/submode -> number; weak validation |
| `data/zbattle/mapsizes.json` | round system | map -> threshold; weak decode/type guards |
| Homicide PData counters | Homicide | integer-like wins/kills |
| Event loot JSON | Event mode | hostname-derived path, unversioned/unvalidated shape |
| CO-OP SQLite + external persistence | CO-OP | map completion and player state; partial/optional integration |

## Command surface highlights

- Mode chances: `zb_getmodeschances`, `zb_setmodechance`, `zb_savemodeschances`, `zb_checkchances`, `zb_rerollchances`.
- Project `COMMANDS`: `bigmap`, `setmode`, `setforcemode`, `endround`; registry owner/dispatcher still untraced.
- Homicide: `hmcd_request_main_traitor` writes state whose consumer is commented.
- Event: numerous concommands misuse `args` table as scalar, breaking settings/eventer operations.
- CO-OP/Counter-Strike/other mode-specific commands require inclusion in the final command matrix.

## Cross-system regression rules derived from current evidence

1. Do not change a packet until every writer/reader and conditional branch is listed.
2. Replace Lua-table network payloads only after recording size, shape, ownership and legacy clients.
3. Consolidate duplicate protocols only after runtime-confirming effective last-writer behavior.
4. Treat all client-supplied tables/strings/vectors as untrusted: type, length, count, ID, phase, permission and rate validation are required.
5. Freeze authoritative winner/round results before delayed presentation callbacks.
6. Centralize mode-owned global timers/hooks/audio/render/convar changes and prove cleanup on end, disconnect, cleanup, hotload and mode switch.
7. Classify every function-valued `MODE` member before retaining automatic hook registration.

## Next trace

1. Produce the full cross-mode packet matrix from all cataloged modes.
2. Produce the mode-function classification/collision matrix.
3. Resolve Defense auxiliary files, Homicide endpoints, Counter-Strike entities and legacy admin queue clients.
4. Trace `COMMANDS`, spawn override, map-point fallback, round-hook emitters and inactive-mode direct hooks.
5. Continue public-surface inventory during organism/fake-ragdoll/movement research.