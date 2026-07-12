# Team and PvE Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This document extends [`MODE_CATALOG.md`](MODE_CATALOG.md) for larger team/PvE modes whose dependencies span NPCs, map progression, persistence, wave orchestration, player classes, readiness lobbies, and specialized objective systems. Additional files may exist in these directories; only fetched files are treated as verified.

## Summary matrix

| Registry ID | Directory | Base | Files verified | Effective launch rule | Major external dependencies |
|---|---|---|---|---|---|
| `hl2dm` | `hl2dm` | none observed | `sh_hl2dm.lua`, `sv_hl2dm.lua`, `cl_hl2dm.lua` | unconditional `true` | team/spawn system, player classes, map points, inventory, attachments, airstrike entity |
| `coop` | `coop` | none observed | `sh_coop.lua`, `sv_coop.lua`, `cl_coop.lua` | first valid `trigger_changelevel` required | HL2 campaign maps, NPCs, SQL, `hg.CoopPersistence`, classes, inventory, map progression, possession |
| `defense` | `defense` | none observed | `sh_defense.lua`, `sv_defense.lua`, partial `cl_defense.lua` | at least one spawn and one nav area | wave-definition/music globals, NPC bases, timers, spawn/map points, support UI, player classes |
| `criresp` | `criresp` | none observed | `sh_criresp.lua`, `sv_criresp.lua`, `cl_criresp.lua` | >3 SWAT points, >0 suspect points, >5 playing players | readiness lobby, SWAT loadout UI, fake ragdoll/organism, physical bullets, map zones, bodygroups, armor/inventory |

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

1. Server computes `winnerteam` but writes no value; client reads `net.ReadInt(3)`.
2. Equal-team branch catches `0 == 0` before the later everybody-died condition.
3. Dot-defined `GuiltCheck` receives the injected mode table first.
4. `ClearPlayerRoles()` clears only NWString; `leader`/`subClass` can leak.
5. Inventory shape, delayed player validity, HUD team data, organism, DynaMusic/PluvTown and canister creation are assumed valid.
6. Airstrike cooldown is global across leaders; intent is undocumented.
7. Launch does not validate teams or required points.

### Required validation

Registry parity; zero/one-team/all-dead; exact end payload; role cleanup; missing dependencies/points; disconnected timer; invalid canister; multiple leaders; sky access.

---

## `MODE-coop` — Half-Life 2 campaign CO-OP

### Verified files and contract

- Shared `sh_coop.lua` blob `629ea48b727a41331c8cd8c773a36a8a678e93d5` registers `HMCD_COOP_SPAWN` and a map-to-`PlayerEqipment` table (`PlayerEqipment` is the consistent misspelling).
- Server `sv_coop.lua` blob `4fb5ef31d340556b5eeed9d97fa0e5484e646bd4` registers `name = "coop"`, `ROUND_TIME = 9000`, `Chance = 1`, `ForBigMaps = true`, no automatic loot, and requires a valid `trigger_changelevel`.
- Client `cl_coop.lua` blob `9a0f1d90bdf6521991a1a3ef424cec5202c86dde` owns introduction/waiting HUD, music, and payload-free end menu.
- Intermission cleans the map, caches points, moves non-spectators to team 0, and sends `coop_start`.
- Spawn fallback: configured points, master `info_player_start`, then `(0,0,0)`.
- Equipment restores/selects roles through optional `hg.CoopPersistence` and per-map schema.
- SQLite `coop_maps(map, completed)` tracks maps; `clearmaps` drops it.
- If `hg.MapCompleted`, round end schedules save and `changelevel hg.NextMap`.
- Dead players can possess supported NPCs with `E`.

### Public surfaces

- Channels: `coop_start`, `coop_roundend`.
- Convars: `zb_coop_rts`, `zb_coop_rts_cmb`, `zb_coop_rts_zmb`, `zb_coop_autochangelevel`, `zb_coop_maxpossesses`.
- Globals/services: `hg.NextMap`, `hg.FriendlyClasses`, `hg.MapCompleted`, `hg.CoopPersistence`, SQL `coop_maps`, command `clearmaps`.
- Hooks: `EntityTakeDamage/dontfuckingdamagethem`, `PlayerButtonDown/checks`, `ZB_RoundStart/RTSoff`, `PostCleanupMap/RTScleanup`, `OnEntityCreated/CoopAlyxWeapon`.

### Verified defects and risks

1. Guilt argument shift.
2. Friendly-fire hook performs no action.
3. Listens for `ZB_RoundStart`, while core emits `ZB_StartRound`.
4. Zombie possession is supported by validator but omitted from target discovery.
5. Several hooks call `CurrentRound().name` without nil guard.
6. Immediate round end races delayed save/changelevel; `hg.NextMap` can be empty.
7. Spawn position is assigned before alive check, moving dead/spectator players.
8. Inventory shape, timer subjects and persistence consistency are assumed.
9. NPC is removed before possession replacement succeeds.
10. Literal `d2_*` table key does not wildcard-match maps.
11. Client mutates persistent colors and assumes optional services.

### Required validation

Campaign maps/points/triggers; wildcard schema; zero/all spectators; empty next map; save/changelevel race; persistence permutations; possession targets/limits/reset; inventory/timers; SQL restart.

---

## `MODE-defense` — NPC Defense

### Verified files and contract

- `sh_defense.lua` blob `c442fdab7cf3dfcc6c8d3a41dd748decce550f97` registers points and `STANDARD`/`EXTENDED`/`ZOMBIE` UI submodes.
- `sv_defense.lua` blob `5880d943c792f66f236e1bbd018c444f25a70168` registers `name = "defense"`, `ROUND_TIME = 10000`, chance `0.02`, loot, and requires a spawn plus nav area.
- `cl_defense.lua` blob `8ce0d36a80371fe8c78c76d5223f122b1efd655a` owns HUD, voting, outlines, music, support UI and end menu; later ranges remain partial.
- Intermission resets wave state, cleans map, assigns team 1, calls `EndWave()`, and starts a 15-second vote.
- Vote accepts 1..3 with per-player one-second rate limit and random tie selection.
- Preparation respawns/equips, sends 30-second countdown, then starts wave 1.
- Tracked entities plus a full entity scan every two seconds determine wave completion.
- End removes broad NPC/NextBot/class-pattern entities and falls back to delayed `gamemode_restart` if `zb.EndMatch` is absent.

### Public surfaces and unresolved dependencies

- Vote channels: `defense_start_vote`, `defense_submit_vote`, `defense_change_vote`, `defense_vote_result`, `defense_vote_update`, `defense_show_selected_mode`.
- Wave channels: `npc_defense_start`, `npc_defense_newwave`, `npc_defense_roundend`, `npc_defense_prepphase`, `StartWaveMusic`, `StopWaveMusic`, `defense_boss_incoming`.
- Client receives `defense_highlight_last_npcs` and sends `RequestSupport`; top-level server counterparts are unresolved.
- Unresolved: `DEFENSE_WAVE_DEFINITIONS`, `DEFENSE_MUSIC`, `StartNewWave`, `SpawnWave`, `OnWaveComplete`, `ClearPlayerRoles`, support system, wave entity creation, `zb.EndMatch`.

### Verified defects and risks

1. Guilt argument shift.
2. Unnamespaced timers can collide.
3. Intermission calls `EndWave()` at wave 0.
4. Double entity traversal and debug prints.
5. End cleanup can delete unrelated VJ/ZBase/NextBot/project entities.
6. Server writes deadline+wave on `npc_defense_newwave`; traced client reads only deadline.
7. Client assumes team 1.
8. Support command authorization/validation/cost/cooldown unresolved.
9. Missing methods imply additional files or incomplete mode.
10. Restart can race global lifecycle; table payload schemas are implicit; UI/music cleanup needs validation.

### Required validation

Enumerate all files; resolve wave/support; launch prerequisites; vote lifecycle; timer collisions; all submodes/bosses; NPC integrations; unrelated entity survival; packet schema; support security; restart race.

---

## `MODE-criresp` — Crisis Response

### Verified files and lifecycle

- `sh_criresp.lua` blob `0a545b437c09eba05f056634e7c5c7fecd8db052` registers SWAT/suspect spawn points, sniper zone/spawn points, model, five primaries, eight gear choices, five gear slots and default gear.
- `sv_criresp.lua` blob `17f222f42c6f3299fcbfd0d6a8b01b2497d13453` registers `name = "criresp"`, `ROUND_TIME = 480`, `start_time = 90`, `end_time = 9`, chance `0.05`, and replicated/admin-controlled `criresp_over20`.
- `cl_criresp.lua` blob `7551b3252a75f9a7d1e2a038326af7e588360310` owns a large readiness/customization/settings/how-to UI, presentation, music and end report.
- `AssignTeams()` shuffles all connected players, assigns 1..6 SWAT based on capped connected count, assigns remaining capped players suspects, and leaves excess users unassigned until Intermission forces everyone spectator/dead.
- Intermission clears readiness/sniper state, sets all players spectator/dead, sends `criresp_start`, and runs a three-second readiness sync. All assigned-ready accelerates `zb.START_TIME` to two seconds.
- Round start assigns future teams. Suspects spawn immediately; SWAT/sniper spawn through 90-second per-player timers. A global 91-second timer grants a ram to one spawned SWAT.
- Suspects outside a point-derived sniper AABB are repeatedly targeted by a world-fired physical `.338` bullet; cooldown scales with number outside.
- Round end sends winner and four uint8 suspect statistics, cleans timers/state, restores armor visibility, and awards team results.

### Network and customization contract

- `criresp_start`: no payload; client opens menu and sends customization.
- `criresp_ready`: no payload; server requires assigned player during state 0, then marks permanently ready for that intermission.
- `criresp_readycount`: uint8 ready + uint8 total.
- `criresp_begin`: no payload; client closes menu and starts presentation/audio.
- `criresp_over20`: client/admin sends bool; server checks `IsAdmin()` and mutates replicated convar.
- `criresp_custom`: client sends uint8 primary, bodygroup string, uint4 gear count, then uint8 gear IDs. Server bounds string to 48 chars, count to configured slots, IDs to gear list and de-duplicates; it does not restrict sender to assigned/SWAT/intermission, rate-limit updates, or validate bodygroup values/model compatibility before later application.
- `cri_roundend`: uint4 winner, then uint8 killed/incapacitated/arrested/total; client reads exact order and locks gameplay input for 8.5 seconds.

### Public surfaces and state

- Convars: server `criresp_over20`; client `criresp_menumusic`, `criresp_menumusic_vol`, `criresp_loadout`, `criresp_gear`, `criresp_bodygroups`.
- Player fields: `criresp_ready`, `criresp_custom`, `criresp_sniper`, `criresp_nextsnipe`, team/class/role/inventory/armor/bodygroups.
- Mode/file locals: `assigned`, `sniperPly`, `shieldGiven`, `sniperZone`; global timer names `criresp_readysync`, `criresp_sniperzone`, `SWATSpawn`, and `SWATSpawn<EntIndex>`.
- Client globals/reused state include `song`, `songfade`, and external menu globals referenced by HUD/end lock.
- Physical bullet path depends on fake ragdoll/old ragdoll bone lookup and `FireLuaBullets`.

### Verified defects and risks

1. Dot-defined `GuiltCheck` receives the injected mode table first.
2. Team cap and SWAT count use all connected players, including prior spectators/AFK users; assignment eligibility is not filtered through `zb:CheckPlaying()` despite launch using it.
3. Sniper is deliberately excluded from SWAT alive count, so SWAT can be declared eliminated while its sniper remains alive.
4. Winner conversion assumes shared `CheckWinner` returns `1` for SWAT and `2` for suspects; this mapping must be runtime-verified.
5. `shieldGiven` is global to the round and determined by delayed SWAT spawn order; disconnected/failed shield holder can consume the sole slot.
6. SWAT/sniper inventory code assumes `Inventory.Weapons` exists.
7. Primary/sidearm/equipment and armor APIs remain partially guarded; bodygroup customization accepts arbitrary numeric tokens and applies them later.
8. `criresp_custom` is callable at any phase by any client and lacks rate limits; stored customization persists until overwritten.
9. Generic timer `SWATSpawn` can collide; per-player timers use current EntIndex and depend on explicit end cleanup.
10. Sniper zone accepts any two point records, but if their `pos` values are missing the AABB can retain infinite bounds.
11. If no external clear line is found, sniper source falls back only ~64 units horizontally from the target, undermining the intended outside sniper model and potentially firing from inside geometry.
12. Sniper bullet attacker may be the sniper player while inflictor remains world; guilt/reward/kill attribution requires validation.
13. Repeating sniper shots have no global budget and can scale with every suspect outside the zone every 0.5 seconds.
14. Readiness has no unready/revoke path and can accelerate global round start as soon as every assigned entry sends once.
15. The client mode is over 1,100 lines and combines settings, customization, readiness, gameplay HUD, audio and end screen, increasing UI lifecycle/hotload regression risk.
16. Client end lock consumes attacks, movement, jump, duck, use, reload and selected binds for 8.5 seconds; interaction with global end-state input/camera handling is unverified.
17. Resource font delivery and multiple sound/material paths are assumed present; no fallback presentation contract is documented.

### Required validation

Spectator/AFK/cap assignment; six-player minimum and over-20 toggle; all-ready acceleration and disconnect/reconnect; unready expectation; SWAT/suspect/sniper winner semantics; sniper-only SWAT survival; missing/malformed zone points; physical bullet attribution/performance/LOS; customization phase/rate/bodygroups/gear/shield; inventory/model/resource failures; timer cleanup/hotload; client input locks and UI/audio teardown.

## Next trace

1. Enumerate unresolved Defense files and pair support/highlight/wave endpoints.
2. Trace CO-OP persistence/changelevel owner files and verify round-hook emitters.
3. Trace Crisis Response readiness/team eligibility against shared playing-player APIs and packet limits.
4. Continue unresolved mode directories while updating inheritance and public-surface matrices.