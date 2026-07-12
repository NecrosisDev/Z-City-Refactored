# Additional Standalone Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This grouped catalog covers standalone competitive modes that do not justify separate documents. Every entry records the actual registry ID rather than assuming it matches the directory name.

## Summary matrix

| Registry ID | Directory | Files verified | Launch rule | Primary dependencies |
|---|---|---|---|---|
| `riot` | `riot` | `sh_riot.lua`, `sv_riot.lua`, `cl_riot.lua` | at least five active players | teams, classes, roles, handcuffs, armor, inventory, TDM spawn points |
| `gwars` | `gwars` | `sh_gwars.lua`, `sv_gwars.lua`, `cl_gwars.lua` | unconditional `true` | teams, classes, roles, weapons, armor, spawn points, SWAT reinforcement |
| `superfighters` | `sfd` | `sh_sfd.lua`, `sv_sfd.lua`, `cl_sfd.lua` | unconditional `true` | RandomSpawns points, organism, inventory, appearance, loot boxes, external music |
| `scugarena` | `scugarena` | `sh_arena.lua`, `sv_arena.lua`, `cl_arena.lua` | unconditional `true`, but chance `0.00` | Slugcat class, organism, spear/grenade weapons, experience/skill, external music |

---

## `MODE-riot` — Riot

### Verified contract

- `sh_riot.lua` blob `e137e56c4f01c4044b1695347e6f6c1252aa108b` registers `RIOT_TDM_LAW` and `RIOT_TDM_RIOTERS` map-point types.
- `sv_riot.lua` blob `5b92a709a6e18a8566bc6c986df1c42265b422df` registers `name = "riot"`, `PrintName = "Riot"`, no loot, `ForBigMaps = false`, chance `0.03`, and requires at least five non-spectator players.
- `cl_riot.lua` blob `632b913939a790bbca55085c80a7e503cc613422` owns payload-free start/end presentation and external sound playback.
- Equipment shuffles `player.GetAll()`, calculates approximately half law enforcement, then assigns rioters to team 0 and law enforcement to team 1.
- Rioters receive terrorist class, role, randomized melee/consumable equipment and occasional armor. Law receives police class, restraint/police equipment and armor.
- Alive checks exclude handcuffed players and return two team arrays to the shared winner function.

### Public surfaces

- Channels: `riot_start`, `riot_roundend`, both payload-free and matched by client receivers.
- Player state: class, role, `CurPluv`, handcuffed netvar, inventory and armor.
- Registered Riot-specific map points exist, but the effective team spawn method reads `HMCD_TDM_T` and `HMCD_TDM_CT` instead.
- Client global `RiotSound` stores the sound station.

### Verified defects and risks

1. `MODE.OverideSpawnPos` is misspelled; if the framework expects `OverrideSpawn`/`OverrideSpawnPos`, the intended behavior is inactive.
2. The two Riot-specific point types are never used by `GetTeamSpawn`; TDM points are used instead.
3. Player counts and partition indices include spectators before spectators are skipped inside assignment loops. This can leave active players unassigned or distort side sizes depending on shuffled spectator positions.
4. `CanLaunch()` validates only player count, not required spawn points.
5. Dot-defined `GuiltCheck` receives the dispatcher-injected mode table as its first argument.
6. Law inventory code assumes `Inventory.Weapons` exists.
7. The local `lawArmor` table is unused.
8. Team labels in `CheckAlivePlayers` (`swatPlayers`, `banditPlayers`) are semantically reversed relative to assigned roles, increasing maintenance error risk.
9. Client HUD assumes only team 0/1 and mutates persistent Color alpha fields.
10. External sound station and PluvTown dependencies lack explicit cleanup/availability contracts.

### Required validation

Five-player threshold with zero/many spectators; all shuffle positions; missing TDM/Riot points; handcuffed-last-player outcome; inventory/class/weapon failures; repeated round state cleanup; music station cleanup; verify intended spawn-override property spelling against framework consumers.

---

## `MODE-gwars` — Gang Wars

### Verified contract

- `sh_gwars.lua` blob `e1151afb68fff8f01901cde9393aafe8d25c6fff` contains only commented TDM point registration.
- `sv_gwars.lua` blob `df4f35a18e3ee5aa2752bc2f49d3a716b999fec4` registers `name = "gwars"`, `PrintName = "Gang Wars"`, `ROUND_TIME = 180`, chance `0.02`, no loot, `ForBigMaps = false`, and unconditional launch.
- `cl_gwars.lua` blob `bd520a9c1f6b772bf8af6ad1a5f80bdd1e634479` owns start/end presentation and layered music that reacts to fear and SWAT arrival.
- Intermission copies `HMCD_TDM_CT/T` points, reapplies existing teams and sends payload-free start.
- Equipment gives team 0 Bloodz and team 1 Groove classes/roles, one random firearm plus ammo and medical equipment.
- At 120 seconds, up to four dead non-spectators respawn as team 2 SWAT at a copied T point or random fallback.
- End awards/penalizes skill based on the winner from the two-array team winner check.

### Public surfaces

- Channels: `gwars_start`, `gwars_roundend`, payload-free and matched.
- Player state: classes `bloodz`, `groove`, `swat`; roles; `CurPluv`; team 2 reinforcement; inventory/equipment.
- Mode state: local `swatSpawned`, copied `CTPoints/TPoints`; client globals `GWARS_LoopStation`, `GWARS_LoopStation2`.

### Verified defects and risks

1. `MODE.OverideSpawnPos` is misspelled.
2. Unconditional launch ignores required TDM spawn points.
3. `ShouldRoundEnd()` returns `endround or boringround`, but `boringround` is not defined in the file and resolves as a global/nil.
4. Dot-defined `GuiltCheck` receives shifted arguments.
5. Random weapon grant is used immediately without `IsValid`; failed `Give` causes method access on invalid/nil weapon.
6. Delayed `noSound` reset lacks player validity check.
7. SWAT AR-15 grant is used immediately without validity check.
8. SWAT team 2 is not included in `CheckAlivePlayers()`, so reinforcement survival does not affect the two-gang winner condition.
9. End rewards compare every player's current team to a winner derived only from teams 0/1; SWAT is always penalized unless winner semantics change unexpectedly.
10. SWAT selection uses first dead players rather than randomized/queued criteria and does not reset their prior role/class state comprehensively.
11. Client music stations are globals, are not visibly stopped in the traced end receiver, and depend on organism/fear fields and external audio files.
12. HUD team table defines only teams 0/1; a live SWAT player on team 2 can index nil presentation data.

### Required validation

Missing spawn points; failed weapon grants; disconnect during delayed callbacks; SWAT arrival with zero/many dead players; team 2 HUD and winner behavior; repeated rounds and state reset; all-dead/tie conditions; audio station teardown; classify expected role of SWAT in round victory.

---

## `MODE-superfighters` — Superfighters 3D

### Verified contract

- Directory is `sfd`, but `MODE.name = "superfighters"` in both server/client.
- `sh_sfd.lua` blob `c943cc8b68a8185d0372af5ed7d659d9ece80b68` blocks attack/leg attack for five seconds when `zb.CROUND == "superfighters"`.
- `sv_sfd.lua` blob `ff0e001e1f12fd62841a57541b7010014f1beae0` enables random spawns/loot, disables guilt, sets `noBoxes = true`, chance `0.04`, and unconditional launch.
- `cl_sfd.lua` blob `a0a9b18812c2de7cc503798c8b1c29b74274d427` receives start vector, plays remote soundtrack URLs, renders player health/name overlays, and receives winner entity.
- Intermission cleans map, applies appearance, assigns team 0, selects `table.Random(zb.GetMapPoints("RandomSpawns"))`, and writes its position to `supfight_start`.
- Round start grants hands/radio/sling, sets organism recoil multiplier and `superfighter` flag, and gives role.
- Round think emits global hook `Boxes Think` every two seconds.
- End waits two seconds, sends first alive entity or NULL through `supfight_end`.

### Public surfaces

- Channels: `supfight_start` vector; `supfight_end` entity.
- Global/shared state: server `zonepoint`; client `StartTime`, `ZonePos`, `dmmusic`; player organism `recoilmul`, `superfighter`; winner entity gets clientside `won = true`.
- External URL audio list is embedded clientside.

### Verified defects and risks

1. Missing/empty `RandomSpawns` makes `table.Random`/`zonepoint.pos` invalid; launch never validates points.
2. `CheckAlivePlayers()` excludes incapacitated players, but `ShouldRoundEnd()` uses `zb:CheckAlive(true)` instead, so end semantics can disagree.
3. Inventory code assumes `Inventory.Weapons` exists.
4. Delayed player callback lacks `IsValid`.
5. Organism `recoilmul` and `superfighter` mutations have no traced reset.
6. `noBoxes = true` conflicts with emitting `Boxes Think`; intended box behavior is unclear.
7. Winner is sampled after a two-second delay, so deaths/disconnects after round end can change the announced result.
8. Client HUD assumes organism exists when calculating audio volume.
9. Remote third-party soundtrack URLs introduce availability, licensing, privacy and latency dependencies.
10. Client globals (`StartTime`, `ZonePos`, `dmmusic`, `hmcdEndMenu`, per-player `won`) can leak across mode changes/hotload; winner flags are not visibly cleared.
11. Shared color objects have alpha mutated in HUD.

### Required validation

No/malformed RandomSpawns; incapacitated-last-player; disconnect/death during two-second winner delay; inventory/organism absence; repeated mode transitions and flag reset; box behavior; remote audio failure/offline operation; player health overlay with invalid/hidden players.

---

## `MODE-scugarena` — Slug Arena

### Verified contract

- Directory `scugarena` files are named `sh_arena.lua`, `sv_arena.lua`, `cl_arena.lua`.
- `sh_arena.lua` blob `47973f582e7964c39d05956f2984ca7538561f91` blocks attack for the first 20 seconds.
- `sv_arena.lua` blob `afc21591bf0b2f673e5745337c205e01c4a733cf` registers `name = "scugarena"`, `PrintName = "Slug Arena"`, no loot, guilt disabled, random spawns, chance `0.00`, unconditional launch.
- `cl_arena.lua` blob `4fe7136af632bcb5b5974d8d83c15aa1a522f051` owns remote soundtrack playback, introduction/end UI and winner state.
- Intermission cleans map, sets every active player to class `Slugcat` and team 0, then sends payload-free `scugarena_start`.
- Round start grants hands; NWString `scug == normal` receives spear and `saint` receives impact grenade.
- End condition uses the mode's incapacitation-aware `CheckAlivePlayers`; delayed end awards experience/skill and sends winner entity.

### Public surfaces

- Channels: payload-free `scugarena_start`; entity `scugarena_end`.
- NWString `scug`; class `Slugcat`; remote soundtrack URLs; client globals/reused globals `dmmusic`, `StartTime`, `hmcdEndMenu`; winner flag `ent.won`.

### Verified defects and risks

1. `Chance = 0.00` makes ordinary weighted selection effectively unreachable, but forced/admin launch remains possible.
2. Delayed `noSound` reset lacks validity check.
3. End winner is sampled after two seconds and can change after lifecycle end.
4. Only exact `scug` values `normal` and `saint` receive weapons; missing/other value gets only hands with no documented fallback.
5. Remote soundtrack URLs and global `dmmusic` repeat the availability/licensing/state-leak risks from Superfighters.
6. Client audio volume assumes `ply.organism` exists.
7. Player `won` flags are set clientside but not visibly cleared before future rounds/modes.
8. Shared Color alpha is mutated; global end-menu identifier is reused by many modes.
9. Server creates `hands` local but selects other weapons based on subtype; invalid weapon grants are not handled.
10. No minimum-player requirement; zero-player and one-player launches can end immediately and still run delayed result/reward logic.

### Required validation

Weighted versus forced launch; zero/one player; unknown/missing `scug`; incapacitated winner; disconnect/death during delay; class/weapon availability; repeated winner-state cleanup; remote audio failures; organism absence.

## Cross-mode findings

- Riot and Gang Wars repeat the misspelled `OverideSpawnPos`; trace the actual framework property before any implementation change.
- Riot, Gang Wars and several earlier team modes reuse TDM spawn point identifiers rather than owning stable mode-specific spawn contracts.
- Superfighters and Slug Arena duplicate remote-audio/end-menu patterns and global names, increasing cross-mode state collisions.
- Dot-defined mode functions remain susceptible to dispatcher argument shifting.
- Many delayed callbacks capture players/entities without validity checks.
- Several modes sample winners after a delay rather than freezing authoritative round results at end transition.

## Next trace

1. Trace the framework consumers for spawn-override flags and map-point routing.
2. Continue unresolved mode directories (`criresp`, `eventhandler`, `pathowogen`, `homicide_fear`, and others) using verified filenames/registration IDs.
3. Build the mode-function classification/collision matrix and packet matrix across all cataloged modes.
4. Consolidate repeated UI/music/end-menu patterns only as a planned implementation package after every consumer is mapped.