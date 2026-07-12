# Team and PvE Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This document extends [`MODE_CATALOG.md`](MODE_CATALOG.md) for larger team/PvE modes whose dependencies span NPCs, map progression, persistence, wave orchestration, and player classes. Additional files may exist in these mode directories; only fetched files are treated as verified.

## Summary matrix

| Registry ID | Directory | Base | Files verified | Effective launch rule | Major external dependencies |
|---|---|---|---|---|---|
| `hl2dm` | `hl2dm` | none observed | `sh_hl2dm.lua`, `sv_hl2dm.lua`, `cl_hl2dm.lua` | unconditional `true` | team/spawn system, player classes, map points, inventory, attachments, airstrike entity |
| `coop` | `coop` | none observed | `sh_coop.lua`, `sv_coop.lua`, `cl_coop.lua` | first valid `trigger_changelevel` required | HL2 campaign maps, NPCs, SQL, `hg.CoopPersistence`, classes, inventory, map progression, possession |
| `defense` | `defense` | none observed | `sh_defense.lua`, `sv_defense.lua`, partial `cl_defense.lua` | at least one spawn and one nav area | wave-definition/music globals, NPC bases, timers, spawn/map points, support UI, player classes |

---

## `MODE-hl2dm` — Half-Life 2 Deathmatch

### Verified files and contract

- Shared `sh_hl2dm.lua` blob `17bf8ca8498acee06520a7f62b6a70e066ee80b4` registers `HL2DM_SNIPERSPAWN` and `HL2DM_CROSSBOWSPAWN` map-point types.
- Server `sv_hl2dm.lua` blob `aa260da7cdde118ac02864d8ad91d86a90ed57ea` registers `name = "hl2dm"`, `PrintName`, `Chance = 0.05`, `ForBigMaps = true`, no loot, unconditional `CanLaunch()`.
- Client `cl_hl2dm.lua` blob `7da758b7a69192704131ce6a6561081a81ae7f62` owns introduction HUD, dynamic music, Elite airstrike radial action, and end menu.
- Intermission cleans the map, reapplies current teams, and broadcasts `hl2dm_start` with no payload; client expects no payload.
- Equipment assigns one Elite/leader, Shotgunner and optional Combine sniper; one Medic/Grenadier/Rebel sniper; sets player classes and sling inventory.
- Winner is based on alive team counts. `hl2dm_roundend` is broadcast after two seconds.
- Elite leader can request an airstrike through `ZB_RequestAirStrike`; server uses the requesting player's eye trace, a shared 70-second global cooldown, and two per-player strikes to spawn `env_headcrabcanister`.

### Public surfaces

- Channels: `hl2dm_start`, `hl2dm_roundend`, `ZB_RequestAirStrike`.
- NWString `PlayerRole`; player fields `subClass`, `leader`, `noSound`; `ACD_StrikesLeft` player-keyed table; shared cooldown `ACD_NextAirstrikeTime`.
- Map points: inherited team spawns `HMCD_TDM_T`/`HMCD_TDM_CT`, plus HL2DM sniper points.
- Hook `PostCleanupMap/ACD_ResetAirstrikes`; client hook `radialOptions/CMB_Airstrike`.

### Verified defects and risks

1. **End payload mismatch:** server computes `winnerteam` but writes no value; client reads `net.ReadInt(3)`. The value is unused after reading, but the contract is invalid and outcome presentation cannot use the result.
2. **Unreachable all-dead branch:** `elseif team0 == team1` catches `0 == 0` before the later everybody-died condition.
3. **Dispatcher argument shift:** dot-defined `GuiltCheck(Attacker, ...)` receives the injected mode table first.
4. **Round-state leakage:** `ClearPlayerRoles()` clears only NWString; `ply.leader` and `ply.subClass` are not reset in the traced mode and can persist into later rounds/classes.
5. **Inventory shape assumption:** `inv["Weapons"]` is written without ensuring it exists.
6. **Timer validity:** delayed `ply.noSound = false` does not check `IsValid(ply)`.
7. **Client nil assumptions:** HUD indexes team data for only teams 0/1; radial menu assumes `lply.organism`; DynaMusic/PluvTown are used without local availability checks.
8. **Canister validity:** entity creation is not checked before method calls.
9. **Global airstrike cooldown:** one leader blocks every other leader; intended scope is not documented.
10. **Unconditional launch:** team and required spawn-point availability are not validated.

### Required validation

Server/client registry parity; zero/one-team and all-dead outcomes; exact end payload; role/subclass cleanup across repeated and different modes; missing inventory/organism/DynaMusic; absent sniper/team points; disconnected timer subject; invalid canister class; multiple leaders and cooldown/strike reset; sky-access trace failures.

---

## `MODE-coop` — Half-Life 2 campaign CO-OP

### Verified files and contract

- Shared `sh_coop.lua` blob `629ea48b727a41331c8cd8c773a36a8a678e93d5` registers `HMCD_COOP_SPAWN` and a map-to-`PlayerEqipment` table covering early HL2 campaign maps (`PlayerEqipment` is the consistent misspelled schema key).
- Server `sv_coop.lua` blob `4fb5ef31d340556b5eeed9d97fa0e5484e646bd4` registers `name = "coop"`, `PrintName`, `ROUND_TIME = 9000`, `Chance = 1`, `ForBigMaps = true`, no automatic loot spawn, and launch only when a valid `trigger_changelevel` exists.
- Client `cl_coop.lua` blob `9a0f1d90bdf6521991a1a3ef424cec5202c86dde` owns introduction/waiting HUD, music, and payload-free end menu.
- Intermission cleans the map, caches CO-OP points, moves non-spectators to team 0, and sends payload-free `coop_start`.
- Spawn fallback order: configured map points, master `info_player_start` entities, then `(0,0,0)`.
- Equipment selects/restores Gordon, medic, grenadier, refugee or rebel roles using optional `hg.CoopPersistence` and per-map class schema.
- SQLite table `coop_maps(map, completed)` tracks completed maps; command `clearmaps` drops it.
- Round ends when no eligible non-Combine/Metrocop/zombie players remain. If `hg.MapCompleted`, a delayed save and `changelevel hg.NextMap` are scheduled.
- Dead players can possess nearby supported NPCs with `E`; possession converts the NPC into a player class and optionally transfers its weapon.

### Public surfaces

- Channels: `coop_start`, `coop_roundend` (both payload-free).
- Convars: `zb_coop_rts`, `zb_coop_rts_cmb`, `zb_coop_rts_zmb`, `zb_coop_autochangelevel`, `zb_coop_maxpossesses`.
- Globals/services: `hg.NextMap`, `hg.FriendlyClasses`, `hg.MapCompleted`, `hg.CoopPersistence`, SQL table `coop_maps`, command `clearmaps`.
- Hooks: `EntityTakeDamage/dontfuckingdamagethem`, `PlayerButtonDown/checks`, `ZB_RoundStart/RTSoff`, `PostCleanupMap/RTScleanup`, `OnEntityCreated/CoopAlyxWeapon`.
- Player state: `RTSUses`, `PlayerClassName`, `subClass`, inventory, role, `noSound`.

### Verified defects and risks

1. **Guilt argument shift:** dot-defined `GuiltCheck` is dispatched with mode table as first argument.
2. **Empty friendly-fire hook:** `EntityTakeDamage` identifies friendly player-to-NPC damage but performs no action.
3. **Round-hook name mismatch:** CO-OP resets possession uses on `ZB_RoundStart`, while the verified round system emits `ZB_StartRound`; only `PostCleanupMap` may currently reset it.
4. **Zombie possession discovery mismatch:** `CanPossessNPC` supports zombies when enabled, but the `PlayerButtonDown` search only considers friendly and Combine tables, so zombie targets are not selected through the traced input path.
5. **Nil-current-round assumptions:** multiple global hooks call `CurrentRound().name` without verifying a mode exists.
6. **Immediate end plus delayed changelevel:** `ShouldRoundEnd()` returns true while independently scheduling save/changelevel; global end lifecycle can run concurrently with transition logic.
7. **Empty next map:** `hg.NextMap` initializes to `""`; changelevel is not guarded against empty/invalid destination.
8. **All-player equipment pass:** spawn position is assigned before the alive check, so dead/spectator entries from `player.GetAll()` can be moved.
9. **Inventory shape assumptions:** default equipment indexes `Inventory.Weapons` without nil/shape guards.
10. **Timer validity:** delayed `noSound` reset lacks a validity check in the main equipment path.
11. **Persistence is optional but stateful:** restore/default role selection depends on external APIs and `MarkPlayerRestored`; partial implementations can duplicate or lose equipment.
12. **Possession race:** NPC is removed before player spawn/class/weapon conversion completes; failure leaves neither source NPC nor guaranteed replacement state.
13. **Map schema coverage:** wildcard `d2_*` is a literal table key in the traced lookup and will not match arbitrary `d2_` maps without separate pattern logic.
14. **Client shared-color mutation:** HUD mutates alpha on persistent color objects and assumes DynaMusic/role/player class availability.

### Required validation

Campaign maps with/without custom spawn points and changelevel triggers; literal versus wildcard map schema; zero players/all spectators; empty `hg.NextMap`; save/changelevel concurrency; complete/partial/absent persistence service; disconnected timers; inventory absence; possession limits/reset hook, friendly/Combine/zombie targets, weapon transfer failure, and map cleanup; SQL persistence across restart.

---

## `MODE-defense` — NPC Defense

### Verified files and contract

- Shared `sh_defense.lua` blob `c442fdab7cf3dfcc6c8d3a41dd748decce550f97` registers NPC/player/defense points and three UI-facing submodes: `STANDARD` 6 waves, `EXTENDED` 12 waves, `ZOMBIE` 6 waves.
- Server `sv_defense.lua` blob `5880d943c792f66f236e1bbd018c444f25a70168` registers `name = "defense"`, `PrintName`, `ROUND_TIME = 10000`, `Chance = 0.02`, `ForBigMaps = true`, loot enabled, and launch when a spawn and nav area exist.
- Client `cl_defense.lua` blob `8ce0d36a80371fe8c78c76d5223f122b1efd655a` is at least 1045 lines and owns HUD, voting, outlines, music, support request UI, and end menu; later ranges remain partially untraced.
- Intermission resets wave state, cleans map, assigns team 1, calls `EndWave()`, and starts a 15-second vote.
- Vote accepts bounded int 1..3 with one-second per-player rate limits, supports changes, and selects randomly among tied highest results.
- Preparation respawns players, grants equipment, sends a 30-second countdown, then starts wave 1.
- Wave tracking uses a mode-owned entity registry plus a full-entity discovery scan every two seconds; zero remaining tracked NPCs ends the wave.
- End round broadcasts, ends wave, clears timers/state, and removes broad NPC/NextBot/class-pattern entities.

### Public surfaces and unresolved dependencies

- Vote channels: `defense_start_vote`, `defense_submit_vote`, `defense_change_vote`, `defense_vote_result`, `defense_vote_update`, `defense_show_selected_mode`.
- Wave channels: `npc_defense_start`, `npc_defense_newwave`, `npc_defense_roundend`, `npc_defense_prepphase`, `StartWaveMusic`, `StopWaveMusic`, `defense_boss_incoming`.
- Client also receives `defense_highlight_last_npcs` and sends `RequestSupport`; registrations/handlers are not present in the fetched top-level server file and imply additional loaded files or missing contracts.
- Unresolved external globals/methods: `DEFENSE_WAVE_DEFINITIONS`, `DEFENSE_MUSIC`, `StartNewWave`, `SpawnWave`, `OnWaveComplete`, `ClearPlayerRoles`, support system, wave entity creation, role/equipment definitions, `zb.EndMatch`.
- `MODE.Timers` stores globally named timers; client convar `cl_wavemusic`; player fields `HasVoted`, vote timestamps, roles.

### Verified defects and risks

1. **Guilt argument shift:** dot-defined `GuiltCheck` receives the mode table first.
2. **Unnamespaced timers:** names such as `vote_end_timer`, `vote_update_timer`, and `prep_phase_timer` can collide with other systems/instances.
3. **Intermission calls `EndWave()` at wave 0:** this invokes `OnWaveComplete()` and waiting-music/cleanup logic before voting; behavior depends on unresolved external implementation.
4. **Double entity traversal:** tracked entities are checked, then every entity is scanned every two seconds; debug `print` statements run on count/death changes.
5. **Overbroad cleanup:** end round removes every NPC and classes containing `npc_vj_`, `sent_vj_`, `zb_`, or `terminator_nextbot_`, including unrelated spawned/admin/integration entities.
6. **Countdown schema asymmetry:** server writes float deadline plus int4 wave on `npc_defense_newwave`; traced client reads only the float and discards wave data.
7. **HUD team assumption:** client indexes `teams[lply:Team()]` with only team 1 defined.
8. **Unresolved support channel:** client sends arbitrary support command strings; server authorization, validation, cost/cooldown and handler are unverified.
9. **Missing-top-level methods:** fetched server file calls wave/role methods not defined there; launch safety cannot be established until all directory files are enumerated.
10. **Fallback restart:** if `zb.EndMatch` is missing, delayed `gamemode_restart` follows cleanup; repeated invocation/race with global round system requires testing.
11. **Vote table transport:** server repeatedly broadcasts Lua tables; payload size is currently small but schema/version is implicit.
12. **Shared color mutation and UI lifecycle:** client mutates persistent role colors and creates full-screen vote panels/music timers requiring cleanup across disconnect/mode change/hotload.

### Required validation

Enumerate every Defense file first; resolve all external wave/support methods/globals; zero-player/no-nav/no-spawn launch; vote tie/change/disconnect/reconnect; timer name collision/hotload; all three submodes and boss waves; NPC base variants (engine, VJ, ZBase, NextBot); unrelated NPC/entity survival; wave-count packet; player team/HUD guard; music/panel cleanup; fallback EndMatch/restart path; support authorization and rate limits.

## Next trace

1. Enumerate unresolved Defense files and pair support/highlight/wave endpoints.
2. Trace CO-OP persistence and changelevel owner files, then validate the round-hook name against all emitters.
3. Trace HL2DM inherited/common team dependencies and airstrike integration.
4. Continue remaining mode directories while updating the global inheritance and public-surface matrices.