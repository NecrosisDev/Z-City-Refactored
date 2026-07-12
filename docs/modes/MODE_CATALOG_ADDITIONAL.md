# Additional Standalone Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This grouped catalog covers standalone competitive and administrator-driven modes that do not justify separate documents. Actual registry IDs are verified from `MODE.name`; directory names are not assumed.

## Summary matrix

| Registry ID | Directory | Files verified | Launch rule | Primary dependencies |
|---|---|---|---|---|
| `riot` | `riot` | `sh_riot.lua`, `sv_riot.lua`, `cl_riot.lua` | at least five active players | teams, classes, roles, handcuffs, armor, inventory, TDM points |
| `gwars` | `gwars` | `sh_gwars.lua`, `sv_gwars.lua`, `cl_gwars.lua` | unconditional `true` | teams, classes, roles, weapons, armor, TDM points, SWAT reinforcement |
| `superfighters` | `sfd` | `sh_sfd.lua`, `sv_sfd.lua`, `cl_sfd.lua` | unconditional `true` | RandomSpawns, organism, inventory, appearance, loot boxes, remote music |
| `scugarena` | `scugarena` | `sh_arena.lua`, `sv_arena.lua`, `cl_arena.lua` | unconditional `true`, chance `0.00` | Slugcat class, organism, spear/grenade weapons, rewards, remote music |
| `event` | `eventhandler` | `sh_event.lua`, `sv_event.lua`, `cl_event.lua` | unconditional `true`, chance `0` | admin/eventer permissions, global strings, persistent custom loot, boxes, UI |

---

## `MODE-riot` — Riot

### Verified contract

- `sh_riot.lua` blob `e137e56c4f01c4044b1695347e6f6c1252aa108b` registers `RIOT_TDM_LAW` and `RIOT_TDM_RIOTERS`.
- `sv_riot.lua` blob `5b92a709a6e18a8566bc6c986df1c42265b422df` registers `name = "riot"`, chance `0.03`, no loot, and requires at least five non-spectators.
- `cl_riot.lua` blob `632b913939a790bbca55085c80a7e503cc613422` owns payload-free start/end presentation and sound.
- Equipment shuffles all players, assigns rioters team 0 and law team 1, then winner logic excludes dead/handcuffed players.
- Channels `riot_start`/`riot_roundend` are payload-free and matched.

### Verified defects and risks

1. `OverideSpawnPos` is misspelled.
2. Registered Riot points are unused; `GetTeamSpawn` reads TDM points.
3. Spectators are counted and shuffled before being skipped during assignment, distorting side sizes/unassigned players.
4. Launch does not validate points.
5. Dot-defined `GuiltCheck` receives shifted arguments.
6. Law inventory assumes `Inventory.Weapons`; `lawArmor` is unused.
7. Team variable names are reversed relative to roles.
8. Client assumes teams 0/1, mutates Color alpha, and lacks explicit audio/PluvTown cleanup contracts.

### Required validation

Threshold with spectators/AFK; shuffle partitions; missing points; handcuffed last player; inventory/class/weapon failures; repeated-round cleanup; spawn-override property consumer.

---

## `MODE-gwars` — Gang Wars

### Verified contract

- `sh_gwars.lua` blob `e1151afb68fff8f01901cde9393aafe8d25c6fff` contains only commented point registration.
- `sv_gwars.lua` blob `df4f35a18e3ee5aa2752bc2f49d3a716b999fec4` registers `name = "gwars"`, `ROUND_TIME = 180`, chance `0.02`, no loot, unconditional launch.
- `cl_gwars.lua` blob `bd520a9c1f6b772bf8af6ad1a5f80bdd1e634479` owns start/end presentation and layered fear/SWAT music.
- Teams 0/1 receive Bloodz/Groove classes and equipment. At 120 seconds up to four dead non-spectators respawn as team 2 SWAT.
- Channels `gwars_start`/`gwars_roundend` are payload-free and matched.

### Verified defects and risks

1. `OverideSpawnPos` misspelling and unconditional launch despite TDM-point use.
2. `ShouldRoundEnd()` references undefined/global `boringround`.
3. Guilt argument shift.
4. Weapon grants are used without validity checks; delayed player callback lacks validity check.
5. Team 2 SWAT is excluded from alive/winner logic and therefore normally penalized at end.
6. SWAT selection is first-match rather than randomized/queued and does not comprehensively reset prior state.
7. Client HUD defines only teams 0/1; team 2 can index nil.
8. Global music stations are not visibly stopped and assume organism/fear data.

### Required validation

Missing points; failed grants; delayed disconnects; team 2 HUD/winner semantics; repeated state cleanup; ties/all-dead; audio teardown.

---

## `MODE-superfighters` — Superfighters 3D

### Verified contract

- Directory `sfd`; registry ID `superfighters`.
- `sh_sfd.lua` blob `c943cc8b68a8185d0372af5ed7d659d9ece80b68` blocks attacks/leg attacks for five seconds.
- `sv_sfd.lua` blob `ff0e001e1f12fd62841a57541b7010014f1beae0` enables random spawns/loot, disables guilt, sets `noBoxes = true`, chance `0.04`, unconditional launch.
- `cl_sfd.lua` blob `a0a9b18812c2de7cc503798c8b1c29b74274d427` receives start vector, plays remote music, overlays player health and receives winner entity.
- Intermission selects `table.Random(RandomSpawns)` and sends its position; start mutates organism recoil/superfighter flags; end samples winner after two seconds.
- Channels: `supfight_start` vector and `supfight_end` entity.

### Verified defects and risks

1. Missing/empty RandomSpawns causes invalid `zonepoint.pos`; launch does not validate.
2. Incapacitation-aware `CheckAlivePlayers` disagrees with `ShouldRoundEnd` using `zb:CheckAlive(true)`.
3. Inventory and organism state are assumed; mutations have no traced reset.
4. `noBoxes = true` conflicts with emitting `Boxes Think`.
5. Delayed winner can change after authoritative end; delayed player callback lacks validity check.
6. Remote URLs and reused globals (`StartTime`, `ZonePos`, `dmmusic`, `hmcdEndMenu`, `won`) create reliability/state/privacy risk.
7. Client assumes organism and mutates shared colors.

### Required validation

Spawn points; incapacitation; disconnect/death during winner delay; inventory/organism absence; flag reset; boxes; offline audio; repeated UI/winner cleanup.

---

## `MODE-scugarena` — Slug Arena

### Verified contract

- Directory files are `sh_arena.lua`, `sv_arena.lua`, `cl_arena.lua`.
- `sh_arena.lua` blob `47973f582e7964c39d05956f2984ca7538561f91` blocks attacks for 20 seconds.
- `sv_arena.lua` blob `afc21591bf0b2f673e5745337c205e01c4a733cf` registers `name = "scugarena"`, no loot, guilt disabled, random spawns, chance `0.00`, unconditional launch.
- `cl_arena.lua` blob `4fe7136af632bcb5b5974d8d83c15aa1a522f051` owns remote music, intro/end UI and winner state.
- All active players become `Slugcat`; `scug=normal` gets spear, `saint` gets impact grenade; end uses incapacitation-aware alive check then delayed winner.
- Channels: payload-free `scugarena_start`, entity `scugarena_end`.

### Verified defects and risks

1. Chance zero makes ordinary selection effectively unreachable while forced launch remains possible.
2. No minimum-player requirement; zero/one player can immediately end.
3. Unknown/missing `scug` receives no explicit fallback weapon.
4. Delayed callback/winner validity and resampling risks.
5. Remote audio/reused globals/client winner flags leak across mode changes; organism and color assumptions remain.
6. Weapon grants are not validated.

### Required validation

Weighted/forced launch; zero/one player; subtype fallback; incapacitated winner; delayed disconnect; class/weapons; repeated cleanup; offline audio/organism absence.

---

## `MODE-event` — Administrator-configurable Event

### Verified files and lifecycle

- Directory `eventhandler`; registry ID `event`.
- `sh_event.lua` blob `3b0fa7cebe57ce6d9a46b74054296b6929e3546b` only aliases the temporary mode table.
- `sv_event.lua` blob `a2132d6c4e64ee46a7ac76f8baf4e749a9aac0fb` registers no loot by default, guilt disabled, random spawns, `ForBigMaps = true`, chance `0`, unconditional launch, `EndLogicType = 2`, mutable `EventersList`, and custom loot persistence.
- `cl_event.lua` blob `895da4168328dc32cee7cb12de9cb8c1eb6d573e` owns start/end HUD, eventer list, winner UI, Steam profile links and custom-loot manager.
- Intermission cleans map, applies appearance/team 0 and samples a `RandomSpawns` point into global `zonepoint`, though current zone logic is commented.
- Round start replaces `EventersList` with all current admins, broadcasts SteamIDs, grants hands/roles, and may start loot timers.
- End logic is configurable: all remaining alive are eventers, one-or-fewer alive, or never automatic. End samples first alive entity after two seconds and sends it.

### Network, commands and persistence

- Channels: payload-free `event_start`; entity `event_end`; table `event_eventers_update`; `event_loot_sync`; bidirectional/overloaded `event_loot_request`; client-to-server table `event_loot_add`; uint16 `event_loot_remove`; registered but unverified `event_loot_update`.
- Custom loot persists to `data/zbattle/event_loot/loot_table_<sanitized-hostname>.txt` as `CustomLootTable` JSON.
- Event properties use global strings `ZB_EventName`, `ZB_EventRole`, `ZB_EventObjective`.
- Commands: `zb_event_loot_reset`, `zb_event_loot_save`, `zb_event_lootpoll`, `zb_event_name`, `zb_event_role`, `zb_event_objective`, `zb_event_endlogic`, `zb_event_loot`, `zb_event_eventer_add`, `zb_event_eventer_remove`, `zb_event_end`, and client `zb_event_loot_menu`.
- Hooks: `Initialize/ZB_EventLoadLootTable`, `PlayerInitialSpawn/ZB_EventLootSync`, `HG_PlayerSay/ZB_EventLootCommand`, `InitPostEntity/ZB_EventLootInitCheck`.

### Verified defects and risks

1. Chance zero plus unconditional launch makes the mode admin/force-driven but still structurally launchable anywhere.
2. `EventersList` is reset to admins at RoundStart, erasing pre-round manual eventer additions; it is not cleared at EndRound, so prior eventers can remain authorized outside an active event until next RoundStart.
3. Concommand callbacks misuse `args` (a table) as scalar: `SetGlobalString(..., args)`, `tonumber(args)`, `player.GetBySteamID(args)`. Name/role/objective/end-logic/loot-enable/eventer commands therefore cannot reliably apply requested values.
4. Eventer chat command runs client `zb_event_loot_menu`, but the client command rejects non-admins; server-authorized eventers cannot open the current UI.
5. `event_loot_add` accepts a decoded table with only field presence checks: no type, range, class existence, string length, table size or rate limits. Negative/huge weights and arbitrary classes can enter persistence.
6. Loaded JSON is checked only for decode success, then indexed as `CustomLootTable[1][2]`; valid JSON with the wrong shape can error.
7. Reset recipient loop uses invoking `ply` instead of loop variable `p` in the eventer check. A non-admin eventer reset can send the full loot table to every connected player.
8. `event_loot_request` is used both client-to-server for sync and server-to-client to open the menu, obscuring direction/schema and complicating validation.
9. Registered `event_loot_update` has no verified use.
10. Loot can emit `Boxes Think` from both a five-second repeating timer and `RoundThink` every two seconds, duplicating spawn work when enabled.
11. Global timer `EventLootSpawnTimer` and multiple initialization hooks can persist/duplicate behavior outside active mode; the InitPostEntity check starts the timer whenever `LootEnabled` is true, regardless of current mode.
12. RoundStart delayed `ply.noSound = false` lacks validity check.
13. End winner is resampled after two seconds and may differ after death/disconnect; client sets per-player `won` flags and reuses global `hmcdEndMenu`.
14. Client mutates shared role colors' alpha and assumes `zb.ROUND_START`, `lply`, fonts/skins and external UI classes exist.
15. EndLogicType 1 uses `zb:CheckAlive(true)` rather than the mode's incapacitation-aware `CheckAlivePlayers`, creating inconsistent end semantics.
16. `zonepoint`, radius/mapsize variables and commented zone code are dead/stale state; launch does not validate RandomSpawns.
17. Administrative settings, eventer membership and custom loot are mutable globals with no audit trail, schema version or transactional rollback.

### Required validation

Forced launch; every end logic; eventer add/remove before/during/after round; command argument behavior; admin versus eventer UI access; malformed/oversized/rate-flooded loot payloads; wrong-shaped persistence; hostname changes; duplicate loot timers; event mode inactive with loot enabled; zero/one players; delayed winner; UI/global cleanup; authorization/data exposure.

## Cross-mode findings

- Riot/Gang Wars repeat `OverideSpawnPos`; framework consumer must be traced before correction.
- Several modes reuse TDM points rather than stable mode-specific contracts.
- Superfighters/Slug Arena/Event duplicate winner-delay, global end-menu and per-player winner patterns.
- Remote or externally stored music and global stations recur without unified lifecycle ownership.
- Dot-defined functions remain susceptible to dispatcher argument shifts.
- Delayed callbacks frequently lack validity checks; winner results are often not frozen at the authoritative transition.
- Event mode adds persistent, admin-editable configuration without schema validation, versioning or auditability.

## Next trace

1. Continue unresolved directories (`pathowogen`, `homicide_fear`, and any undiscovered mode files) using verified filenames/IDs.
2. Trace framework consumers for spawn overrides, map routing, command args and emitted round hooks.
3. Build cross-mode function classification/collision and packet matrices.
4. Add planned consolidation packages only after every consumer is mapped.