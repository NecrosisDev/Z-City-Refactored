# Team and PvE Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This grouped catalog covers team/PvE modes with broad NPC, map, persistence, vehicle, wave, readiness, player-class and objective dependencies. Only fetched executable files are treated as verified.

## Summary matrix

| Registry ID | Directory | Base | Files verified | Effective launch rule | Major dependencies |
|---|---|---|---|---|---|
| `hl2dm` | `hl2dm` | none | `sh_hl2dm.lua`, `sv_hl2dm.lua`, `cl_hl2dm.lua` | unconditional `true` | teams/spawns, classes, inventory, attachments, canister airstrike |
| `coop` | `coop` | none | `sh_coop.lua`, `sv_coop.lua`, `cl_coop.lua` | requires `trigger_changelevel` | HL2 maps/NPCs, SQL, persistence, classes, inventory, possession |
| `defense` | `defense` | none | `sh_defense.lua`, `sv_defense.lua`, `sv_defense_waves.lua`, `sv_defense_roles.lua`, `sv_defense_support.lua`, `cl_defense.lua` | spawn + nav area | wave/music/economy data, NPC bases, timers, commander support, classes |
| `criresp` | `criresp` | none | `sh_criresp.lua`, `sv_criresp.lua`, `cl_criresp.lua` | >3 SWAT points, suspect point, >5 playing players | readiness/customization, fake ragdoll, physical bullets, armor/inventory |
| `pathowogen` | `pathowogen` | none | `sh_uwu.lua`, `sv_uwu.lua`, `cl_uwu.lua`, `sv_dialogue.lua` | hard-disabled (`CanLaunch()==false`) | Glide/simfphys, extraction, fake ragdoll, classes, organism, inventory, loot, dialogue/UI |

---

## `MODE-hl2dm` — Half-Life 2 Deathmatch

### Contract

- Files: `sh_hl2dm.lua` `17bf8ca8...`; `sv_hl2dm.lua` `aa260da7...`; `cl_hl2dm.lua` `7da758b7...`.
- Chance `.05`, big-map mode, no loot, unconditional launch.
- Intermission reapplies teams and sends payload-free start. Equipment assigns Combine/Rebel subclasses, classes, sling inventory and one Elite leader.
- Winner uses alive team counts. Elite can request `env_headcrabcanister` airstrikes through `ZB_RequestAirStrike`; two strikes per player, shared 70-second cooldown.

### Verified defects

- Server computes winner but sends no end payload; client reads `int(3)`.
- Equal-team branch catches `0==0` before everybody-died branch.
- Guilt argument shift; role/subclass leakage; inventory/timer/organism/music/entity validity assumptions.
- Airstrike cooldown is global across leaders; launch ignores team/spawn prerequisites.

### Validation

Registry parity; zero/one-team/all-dead; packet capture; role cleanup; missing dependencies/points; timer disconnect; invalid canister; multi-leader cooldown and sky trace.

---

## `MODE-coop` — HL2 campaign CO-OP

### Contract

- Files: `sh_coop.lua` `629ea48b...`; `sv_coop.lua` `4fb5ef31...`; `cl_coop.lua` `9a0f1d90...`.
- `ROUND_TIME=9000`, chance `1`, requires changelevel trigger.
- Spawn fallback: custom points, master `info_player_start`, then origin.
- Equipment restores/selects roles via optional `hg.CoopPersistence` and map schema `PlayerEqipment`.
- SQLite `coop_maps` tracks progress. Dead players can possess supported NPCs.
- Completed map schedules persistence save and `changelevel hg.NextMap`.

### Verified defects

- Empty friendly-fire hook; listens `ZB_RoundStart` while core emits `ZB_StartRound`.
- Zombie possession validator exists but target search omits zombies.
- Nil `CurrentRound()` assumptions, immediate-end/changelevel race, empty next map.
- Dead/spectators can be moved before alive check; inventory/timer/persistence assumptions.
- NPC removed before replacement succeeds; literal `d2_*` key is not wildcard logic.

### Validation

Campaign map/trigger/point combinations; zero/spectator-only; persistence absent/partial/full; save/changelevel race; possession classes/limits/reset; inventory/timers; SQL restart.

---

## `MODE-defense` — NPC Defense

### Verified files and ownership

- `sh_defense.lua` blob `c442fdab...`: point registries and `STANDARD`/`EXTENDED`/`ZOMBIE` mode data.
- `sv_defense.lua` blob `5880d943...`: core lifecycle, voting, preparation, timers, entity tracking and cleanup.
- `sv_defense_waves.lua` blob `03aaf158...`: spawn visibility/nav search, wave queue, NPC creation/targeting and `OnNPCKilled`.
- `sv_defense_roles.lua` blob `fc7b5f46...`: roles, base equipment, commander points, wave rewards and player spawning.
- `sv_defense_support.lua` blob `d69c1a90...`: commander menu/purchases, airdrops, support team and player reinforcements.
- `cl_defense.lua` blob `8ce0d36a...`: HUD, voting, outlines, wave music, commander UI/support requests and end presentation.

### Lifecycle and subsystem contract

- Chance `.02`, loot enabled, launch requires at least one usable player spawn and one nav area.
- Intermission resets mode state, cleans the map, assigns team 1, calls `EndWave()` while wave is zero, then opens a 15-second vote.
- Voting accepts option 1..3 with one-second per-player submit/change limits; ties are selected randomly.
- Preparation respawns/equips players, sends a 30-second deadline, then starts wave 1.
- Wave definitions come from `DEFENSE_WAVE_DEFINITIONS`; music comes from `DEFENSE_MUSIC`.
- Wave spawning queues one timer per planned NPC, searches nav/ground locations outside player visibility, supports engine NPCs, ZBase, VJ/NextBot classes, assigns targets, and tracks entities in `DefenseWaveEntities`.
- Completion is detected both through `OnNPCKilled` and a two-second tracked/full-world scan.
- Roles are Commander, Medic, Engineer and Soldier. Commander gains supply points per wave and double points for boss waves.
- Commander support owns `RequestSupport`, `defense_commander_menu`, `defense_commander_purchase`, `defense_commander_notification`, role and point channels.
- End broadcasts, ends wave, clears roles/timers/state, then removes broad NPC/project/integration class patterns.

### Verified packet contracts

- Vote: deadline float; submit int4; change previous+new int4; updates/results use small unversioned Lua tables; selected mode uses string.
- `npc_defense_newwave` writes float deadline + int4 wave; traced client reads only deadline.
- `RequestSupport` accepts a server-catalogued support string after role/mode/incapacitation, two-second sender and global 290-second cooldown checks.
- Commander menu is bidirectional on one name: client request has no payload; server reply is `DEFENSE_COMMANDER_ITEMS` table.
- Commander purchase accepts a Lua table, caps raw message length to 8192, table entries to 20, quantity to 10, resolves catalog items server-side and applies a one-second sender limit.
- `defense_commander_notification` writes string message + int16 point delta.
- `defense_highlight_last_npcs`, `defense_commander_points` and final role-assigned client ownership still require line-level pairing.

### Verified defects

1. Dot-defined `GuiltCheck` receives shifted arguments.
2. Core, wave and role files place many internal services directly on `MODE`, publishing them as hook names (`CreateTimer`, `SpawnWave`, `FindNavMeshSpawnPoint`, `AssignPlayerRoles`, `OnWaveComplete`, and others).
3. Timer names are global and generic (`vote_end_timer`, `prep_phase_timer`, `new_wave_timer`, spawn names), with hotload/collision risk.
4. Intermission calls `EndWave()` at wave zero, invoking music cleanup, ragdoll/weapon sweep and `OnWaveComplete()` before voting.
5. Wave tracking duplicates `OnNPCKilled`, tracked-table scans and full-world scans; debug output runs during normal changes.
6. End cleanup removes every NPC and classes matching broad `npc_vj_`, `sent_vj_`, `zb_`, or `terminator_nextbot_` patterns, including unrelated/admin/integration entities.
7. New-wave packet has an unread int4 field.
8. HUD assumes team 1 and mutates shared role colors.
9. `StartWave()`/`EndWave()` index music tables by current wave without a documented nil-safe data contract.
10. Wave spawn creates one named timer per NPC and performs repeated all-nav-area searches; high-wave cost is not budgeted.
11. Global replacement of `SpawnZBaseNPC` wraps an external function and changes behavior outside the mode unless all callers are compatible.
12. Commander purchase table schema is implicit; quantity is capped above but not explicitly type/lower-bound normalized before arithmetic.
13. `RequestSupport` role/mode/catalog/cooldown checks exist, but global cooldown lets one commander block all others and delayed delivery captures sender/mode state.
14. Airdrop and support entities are created with partial validity checks; fall timers are not consistently mode-owned through `MODE:CreateTimer`.
15. Reinforcement support can respawn players during an active wave and reapply equipment independently from the role lifecycle.
16. `RoundEnd/CleanupSupportTeam` listens to a generic hook name; verified core lifecycle emits `ZB_EndRound`, so cleanup emission compatibility is unresolved.
17. Fallback `gamemode_restart` can race the global round lifecycle when `zb.EndMatch` is absent.
18. Duplicate network registrations across auxiliary files obscure ownership even where schemas match.

### Validation

- All vote transitions, changes, ties, reconnects and timer cleanup.
- Every submode/wave/boss definition and missing/malformed data table.
- Engine, ZBase, VJ and NextBot spawn paths; nav absence and no-hidden-spawn conditions.
- Large-wave timer/nav/entity-scan budgets and duplicate death counting.
- Commander purchase/support fuzzing, point arithmetic, refunds, cooldown scope and delayed sender disconnect/mode switch.
- Role assignment with low populations where random removal can exhaust player arrays.
- Unrelated NPC/addon entity survival through round end.
- Packet bit-count capture, especially new-wave, commander points/role and highlight endpoints.
- Runtime hook instrumentation for all accidentally published wave/spawn/timer helpers.

---

## `MODE-criresp` — Crisis Response

### Contract

- Files: `sh_criresp.lua` `0a545b43...`; `sv_criresp.lua` `17f222f4...`; `cl_criresp.lua` `7551b325...`.
- `ROUND_TIME=480`, start 90, chance `.05`, requires points and six playing players.
- Readiness lobby/customization; suspects spawn immediately, SWAT/sniper via delayed timers; world-fired `.338` bullets enforce sniper AABB.
- `criresp_custom`: primary uint8, bodygroup string, gear count uint4, gear IDs uint8; IDs/count/string length partially bounded.
- End sends winner plus four uint8 suspect statistics and locks client input during presentation.

### Verified defects

- Guilt argument shift; assignment cap/SWAT counts all connected players rather than playing eligibility.
- Sniper excluded from SWAT alive count; winner mapping needs runtime proof.
- One shield consumed by delayed spawn order; inventory/equipment validity assumptions.
- Customization allowed any phase/client, no rate limits, arbitrary numeric bodygroups.
- Generic/per-EntIndex timers; malformed point AABB; near-target fallback sniper source; attribution/performance uncertainty.
- Ready cannot be revoked; client combines settings/lobby/gameplay/audio/end UI and locks broad input set.

### Validation

Spectator/AFK/cap assignment; readiness/disconnect; winner/sniper semantics; zone/physical bullet attribution and load; customization phase/rate/schema; resources/timers/input/UI cleanup.

---

## `MODE-pathowogen` — Pathowogen extraction/assimilation scenario

### Files, launch and high-level flow

- `sh_uwu.lua` blob `e722d1d6e7a64f8f8ab4d4456138daafe7677aa6`: registry ID `pathowogen`, point types for helicopter, Delta extraction, boxes and vehicles.
- `sv_uwu.lua` blob `13137dcf922759dd1f609467bbfb77c075350e43`: 1,081-line authoritative scenario, loot, assimilation, extraction, vehicles and consequences.
- `cl_uwu.lua` blob `794bfe9b98ef8dc39305b4197b31711ff25dfcb0`: briefings/dialogue, extraction markers, vehicle/extraction music and end report.
- `sv_dialogue.lua` blob `5675d86b01c367bc6f84a701c327ea7f916bc53e`: commander/contractor message tables.
- Additional verified client UI files exist under `derma/` but are not yet behavior-traced.
- Chance `.05`, big-map/random-spawn/loot-on-time flags, but `CanLaunch()` hard-returns false.
- Round assigns furries, survivors and optional traitor/contractor; spawns props/vehicles; initiates helicopter or close-quarters Delta extraction; tracks assimilated/dead/escaped players and sends a detailed consequence table at end.

### Public surfaces

- Channels: `zb_furbriefing`, `zb_furfurbriefing`, `zb_furtraitorbriefing`, `zb_contractortransmit`, `zb_commandertransmit`, `zb_extractionheli`, `zb_extractionpoint`, `zb_traitorextractionpoint`, `ZB_Pathowogen_RoundEnd`.
- Round-end payload: uint3 win condition + `net.WriteTable` keyed by players with original/current identity, role, alive and escaped state.
- Point registries: `UWU_GlideHeli`, `UWU_DeltaSquad`, `SCRAPPERS_BIGBOX`, `SCRAPPERS_SMALLBOX`, `SCRAPPERS_VEHICLE`, plus generic spawn points.
- External state/services: Glide helicopter/seat APIs, simfphys fuel convars, fake ragdoll/weld constraints, player classes `furry`/`commanderforces`, organism/inventory/armor/loot, appearance, physical extraction timers.
- Client globals: `zb.uwucopter`, `zb.ExtractPoint`, `zb.traitorExtract`; mode audio stations and extraction marker rendering.

### Verified defects and risks

1. **Disabled but globally loaded:** mode cannot normally launch, yet all function-valued members still become hook candidates and direct/static effects must be verified mode-gated.
2. **Recursive spawn exhaustion:** `GetRandomSpawn()` recursively retries used indices without termination; more players than spawn points can recurse indefinitely/overflow.
3. **Eligibility counts include spectators:** fur/traitor amounts use `#player.GetAll()` before spectators are skipped, distorting assignment.
4. **Nil AFK comparison:** Delta selection uses `ply.afkTime2 > 60` without guard.
5. **Entity/weapon/vehicle assumptions:** props, Glide vehicles/helicopter, seats and weapons are used without complete validity checks; failed helicopter creation is dereferenced by callers.
6. **Inventory/organism assumptions:** Delta equipment indexes `Inventory.Weapons` and mutates organism recoil without guards/reset.
7. **Global fuel mutation:** enables simfphys fuel and sets global fuel scale `.01` with no traced restoration, affecting unrelated vehicles/modes.
8. **Duplicate broadcasts:** contractor/extraction messages send the entire recipient list inside loops, generating repeated packets.
9. **Global timer names and reconnect collisions:** `UWUCopter`, `CQExtract` and extraction names based on EntIndex can collide across hotload/reconnect; extraction callbacks capture invalidatable players/mode state.
10. **Extraction timer validity:** callbacks dereference players/points after 10 seconds without complete validity/current-mode checks.
11. **Helicopter weld extraction:** examines weld entities without validating both sides, manipulates/removes fake ragdolls, kills extracted players twice, and marks escape as a side effect of physics collision.
12. **CallOnRemove bug:** callback checks `self.HasExploded` where `self` is the mode, not the removed helicopter; intended crash/explosion message likely never fires.
13. **Spawn count fallback:** `saved.PlayerCount = #player.GetAll()-1` is unexplained and includes spectators; casualty thresholds can trigger incorrectly.
14. **Commanderforces excluded from both alive teams:** reinforcement survival does not affect win condition.
15. **Global convar/state cleanup:** fuel, player class/organism, local extraction vars and spawned interests lack a complete restore contract.
16. **Client rendering leak:** `PostDrawTranslucentRenderables` calls `cam.IgnoreZ(true)` for traitor extraction, then returns early when no extraction point without restoring `IgnoreZ(false)`.
17. **Client audio lifecycle:** RoundStart clears extraction references but does not centrally stop/reset existing audio stations.
18. **Dot-defined GuiltCheck shift:** dispatcher injects mode table before expected attacker/victim parameters.
19. **Round-end table:** `net.WriteTable` contains entity keys/nested mutable data without explicit bounds/version; disconnected entities and large player counts need validation.
20. **Unsafe recursive/world integration:** interest spawn assumes point registries exist; vehicle class dependencies are optional external addons; extraction physics depends on fake ragdoll ownership/weld topology.

### Validation

- Force-launch only in isolated test environment; verify no hooks/global mutations while inactive.
- Zero/one/many players, spectators/AFK and more players than spawn points.
- Missing/malformed point registries; absent Glide/simfphys/classes/inventory/organism/armor/loot.
- Helicopter failure, seat shortage, weld entity invalidation, extraction disconnect/death/ragdoll states and close-quarters fallback.
- Verify all timers/hooks/state/convars/classes/audio/render state restore on end, cleanup, mode switch and hotload.
- Packet-count repeated broadcasts and round-end table size/schema; client UI/briefing files and dialogue lifecycle.

## Next trace

1. Close the remaining one-sided Defense highlight/commander point/role endpoints and client line-level schemas.
2. Trace CO-OP persistence/changelevel owner and round-hook naming.
3. Complete Pathowogen Derma/extraction endpoint pairing and inactive-hook audit.
4. Continue from mode matrices into organism, fake-ragdoll, movement and player-class ownership.
