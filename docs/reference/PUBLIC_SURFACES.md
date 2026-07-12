# Public Surfaces Inventory

**Work package:** `WP-RESEARCH-001`  
**Scope:** bootstrap, mode/round framework, admin mode UI, and all currently cataloged mode surfaces  
**Status:** `partial / executable-source verified`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Reviewed:** 2026-07-12

This inventory tracks refactor-sensitive globals, hooks, network channels, convars, commands, persistence and trust boundaries. Exact packet schemas are canonical in [`PACKET_MATRIX.md`](PACKET_MATRIX.md); function dispatch is canonical in [`MODE_FUNCTION_MATRIX.md`](MODE_FUNCTION_MATRIX.md).

## Core globals and registries

| Surface | Owner | Realm | Contract/risk |
|---|---|---|---|
| `hg` / `hg.loaded` | global loader | server/client | global addon namespace and bootstrap state |
| `zb` | gamemode/bootstrap libraries | server/client | mode registry, round state, points, teams, admin UI and subsystem globals |
| `zb.modes` | mode loader | server/client | mode name -> table; realm registries must agree |
| `zb.modesHooks` | mode loader | server/client | mode -> function key -> callback |
| `MODE` | loader/mode files | temporary global | every function-valued member becomes a hook candidate |
| `CurrentRound()` / `NextRound()` | round system/client | realm-local | broad mode-state consumer surface |
| `COMMANDS` | unresolved command framework | primarily server | owner/dispatcher/collision behavior still untraced |
| mode/client globals | individual modes | mixed | repeated timing, menu, winner, zone, extraction and audio globals collide across modes/hotload |

## Core hook contract

### Emitted

| Hook | Emitter | Contract |
|---|---|---|
| `HomigradRun` | global loader | no args after main addon load |
| `ZB_PreRoundStart` | round system | state `3 -> 0` preparation |
| `TTTPrepareRound` | round system | compatibility emission at preparation |
| `ZB_StartRound` | round system | after mode start/next selection |
| `ZB_EndRound` | round system | after mode end |
| `RoundInfoCalled` | client RoundInfo receiver | mode name before client state assignment |
| `ZB_TraitorWinOrNot` | Homicide | traitor entity + winner identifier |
| dynamic mode function names | mode loader | invokes `func(modeTable, ...)`; dot-defined methods shift arguments |

### High-impact registrations

| Hook | Identifier/owner | Risk |
|---|---|---|
| `Think` | `zb-think` | core lifecycle, once/sec |
| `PlayerInitialSpawn` | round/admin sync | multiple handlers and duplicate identifier |
| `RoundStateChange` | Homicide reset | waits for stale state `2`; emitter unresolved |
| `ZB_RoundStart` | CO-OP reset | verified core emitter is `ZB_StartRound` |
| `PostCleanupMap` | airstrike/Fear/CO-OP | inactive-mode effects require gating audit |
| `RoundEnd` | Defense support cleanup | verified core emitter is `ZB_EndRound`; support-team cleanup likely dead |
| dynamic Fear hooks | Fear events/environment | cleanup and identifier reuse risks |
| `SetupOutlines` / `radialOptions` | Defense client | direct integrations load outside mode-table dispatch |

## Core round/admin channels

| Channel | Direction | Ordered schema | Validation/status |
|---|---|---|---|
| `RoundInfo` | S -> C | string mode, int4 state | paired; server authoritative |
| `FadeScreen` | S -> C | none | client endpoint not fully traced |
| `updtime` | S -> C | three floats | sender unresolved |
| `ZB_SendModesInfo` / `ZB_SendRoundList` | S -> admin C | Lua tables plus strings | recipient-gated; implicit schemas |
| `ZB_RequestRoundList` | admin C -> S | none | admin checked |
| `ZB_UpdateRoundList` | admin C -> S | table list, bool | weak table validation; bool unused |
| `AdminSetGameMode` / `AdminSetGameQueue` | admin C -> S | strings/bool or Lua table | duplicate/legacy receivers and weak validation |
| legacy queue family | mixed | tables/strings/none | active consumers unresolved |

Duplicate name-keyed network registrations and queue generations require runtime overwrite proof before consolidation.

## Competitive/Homicide packet highlights

| Channel | Direction | Schema / defect |
|---|---|---|
| `tdm_start` | S -> C | base writes nothing while client reads string |
| `tdm_buyitem` | C -> S | weakly bounded purchase table |
| `CS_Intermission` / `CS_Killfeed` | S -> C | paired nested Derma consumers |
| `CS_Roundover` | S -> C | numeric winner written through bool |
| `bomb_enter` | C -> S | no mode/phase/ownership/distance/LOS/rate/format validation |
| `HMCD_RoundStart` | S -> C | conditional traitor roster can desynchronize stream |
| role-selection family | mixed | structurally paired but hard-disabled; subrole reader-only; police registration-only |
| assistant/death-state family | S -> C | paired count/name/state protocols |
| `check_lightness` | both | client-authored vector through unauthenticated global request slot |

## Team/PvE packet highlights

| Channel | Direction | Schema / defect |
|---|---|---|
| `hl2dm_roundend` | S -> C | server writes none; client reads int3 |
| `npc_defense_newwave` | S -> C | float deadline + int4 wave; client reads only float |
| Defense vote family | mixed | paired primitives plus unversioned result/update tables |
| `RequestSupport` | C -> S | catalog string with Commander/mode/incapacitation and cooldown checks |
| `defense_commander_menu` | bidirectional | empty request, table reply; role/alive/rate checks |
| `defense_commander_purchase` | C -> S | bounded raw/table counts but implicit item schema and weak quantity typing |
| `defense_commander_notification` | S -> C | string + int16 delta |
| `defense_highlight_last_npcs` | S -> C | paired in `sv_defense_hooks.lua`; broadcasts remaining entity indices when 1–3 remain |
| `defense_commander_points` | none | registration-only; actual state uses `NWInt("CommanderPoints")` |
| `defense_player_role_assigned` | S -> C | two server writers, no client receiver; clients use `NWString("PlayerRole")` |
| `defense_admin_command` | C -> S | reader-only admin command + Lua table; no sender, rate, size or active-mode guard |
| `criresp_custom` | C -> S | partial bounds but no mode/phase/role/rate/model validation |
| `ZB_RequestAirStrike` | C -> S | no payload; active-mode/alive/state checks incomplete |

## Defense function/public-service surface

- `sv_defense.lua` owns voting, preparation, wave state, fallback spawning and timer services.
- `sv_defense_waves.lua` owns nav/visibility search, spawn queues, NPC targeting and death tracking, and globally wraps `SpawnZBaseNPC`.
- `sv_defense_roles.lua` owns role assignment, equipment, commander `NWInt` economy and wave rewards; `defense_commander_points` is dormant and role-assignment packets are redundant.
- `sv_defense_support.lua` owns support/menu/purchase receivers, airdrops and reinforcements; its generic `RoundEnd` cleanup hook does not match the verified core emitter.
- `sv_defense_hooks.lua` owns last-NPC highlight broadcasting and the admin command receiver.
- Large waves combine per-NPC timers, repeated nav enumeration, tracked-table scans and world scans without an explicit performance budget.

## Pathowogen and Fear surfaces

Pathowogen exposes briefing, dialogue, extraction entity/vector and complex end-report packets; global simfphys convars, fake-ragdoll weld extraction, timers, audio and render state lack a complete restore contract. Fear inherits Homicide, remains hard-disabled, yet loads direct hooks, network receivers, event registries, light sampling and screen/audio state that require inactive-mode gating proof.

## ConVars and persistence

| Surface | Owner | Contract/risk |
|---|---|---|
| `hg_loadcontent` | global loader | replicated/archive content toggle |
| `zb_forcemode` | round system | reset to `random` on source load |
| client presentation convars | multiple modes | repeated/global acquisition patterns |
| simfphys fuel convars | Pathowogen | global mutation without traced restoration |
| mode chances/mapsizes JSON | registry/round system | weak decode/type guards |
| Homicide PData | Homicide | integer-like counters |
| Event loot JSON | Event | unversioned persistent client-authored data |
| CO-OP SQLite/persistence | CO-OP | partial optional integration |

## Command surface highlights

- Mode chance commands are cataloged.
- Project `COMMANDS` entries include `bigmap`, `setmode`, `setforcemode`, and `endround`; registry owner/dispatcher remains untraced.
- Defense `defense_admin_command` is a direct network administration surface with no repository sender.
- Event concommands misuse the `args` table as a scalar in several paths.

## Cross-system regression rules

1. Do not change packets before every writer, reader and conditional branch is listed.
2. Record size, shape, ownership and compatibility before replacing Lua-table payloads.
3. Runtime-confirm duplicate overwrite behavior before consolidation.
4. Treat client tables/strings/vectors as untrusted and validate type, bounds, IDs, phase, permission and rate.
5. Freeze authoritative results before delayed presentation callbacks.
6. Centralize mode-owned timers/hooks/audio/render/convar state and prove cleanup.
7. Classify every function-valued `MODE` member before retaining automatic hook registration.

## Next trace

1. Pair core one-sided channels: `FadeScreen`, `updtime`, `ZB_SpectatePlayer`, and legacy queue consumers.
2. Trace `COMMANDS`, spawn overrides, map-point fallback, `zb.EndMatch`, and actual round-hook emitters.
3. Complete Pathowogen Derma/end-report and inactive-mode direct-hook audit.
4. Begin organism initialization, state, replication, damage/medical lifecycle and fake-ragdoll integration.