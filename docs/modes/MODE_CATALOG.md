# ZCity Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This catalog records actual registration IDs, files, inheritance, lifecycle, data/network contracts, dependencies, verified defects, and required validation. Directory names are not treated as mode IDs until `MODE.name` is found.

## Verified dependency graph

```text
zb.modes
├─ tdm                                  standalone base
│  └─ cstrike                           MODE.base = "tdm"
├─ dm                                   standalone
└─ hmcd                                 standalone registry entry
   ├─ standard                          MODE.Types submode
   ├─ wildwest                          MODE.Types submode
   ├─ gunfreezone                       MODE.Types submode
   ├─ soe                               MODE.Types submode
   ├─ suicidelunatic                    client-visible; server body not fully ranged
   └─ supermario                        client-visible; server body not fully ranged
```

`zb:GetMode(submode)` maps a `MODE.Types` key back to its owning registry key. `RoundInfo` sends the base key (`hmcd`); Homicide separately sends its active `MODE.Type`.

## Summary matrix

| ID | Directory | Base | Files verified | Launch contract | Primary dependencies |
|---|---|---|---|---|---|
| `tdm` | `tdm` | none | `sh_tdm.lua`, `sv_tdm.lua`, `cl_tdm.lua` | unconditional `true` | teams, inventory, classes, roles, attachments, armor, weapons, map points |
| `cstrike` | `tdm_cstrike` | `tdm` | `sh_cstrike.lua`, `sv_cstrike.lua`, `cl_cstrike.lua` | effective unconditional `true`; earlier point validator overwritten | all TDM contracts, bomb/hostage entities, organism, map points, harm tracking |
| `dm` | `dm` | none | `sh_dm.lua`, `sv_dm.lua`, `cl_dm.lua` | unconditional `true` | organism, appearance, armor, weapons, zone globals, entity iteration, harm tracking |
| `hmcd` | `homicide` | none | `sh_homicide.lua`, `sv_homicide.lua`, `cl_homicide.lua` | unconditional `true`; submode chance functions gate map size | organism, fake ragdoll, appearance, inventory, classes, roles, loot, weapons, persistence |

---

## `MODE-tdm` — Team Deathmatch

### Files and metadata

- `sh_tdm.lua` blob `1aa70fac82fc2556b71e0ada95a0b6b931eabfdc`.
- `sv_tdm.lua` blob `5dfaa969145a20912b76a278ea6e861fc0196c83`.
- `cl_tdm.lua` blob `c6e4254634502d2055c105ae321fd27e75b46a42`.
- `PrintName = "Team Deathmatch"`; `BuyTime = 40`; `StartMoney = 6500`; `start_time = 20`; `ROUND_TIME = 240`; `Chance = 0.04`; `ForBigMaps = true`; `buymenu = true`.
- Map points registered: `HMCD_TDM_CT`, `HMCD_TDM_T`; current `CanLaunch()` ignores them and returns true.

### Lifecycle

1. `Intermission()` cleans the map, resets teams/money, and broadcasts `tdm_start` without writing fields.
2. Client `tdm_start` reads a string into `zb.rtype`, starts music, and removes fade.
3. `GiveEquipment()` sets class/role/cosmetics/inventory and gives baseline equipment.
4. `RoundStart()` unfreezes players.
5. `ShouldRoundEnd()` delegates to alive-team winner logic.
6. `EndRound()` awards skill/experience and broadcasts `tdm_roundend`.

### Buy contract

- `BuyItems[category][displayName]` fields: `Type`, `ItemClass`, `Price`, `Category`, optional `Attachments`, `Amount`, `TeamBased`.
- Client sends `tdm_buyitem` table `{category, itemName}` or `{category, itemName, attachmentID}`.
- Server re-resolves category/item and checks time/money/weapon ownership, but not player alive state, rate/size, `TeamBased`, or attachment membership.

### Verified defects

- **Payload mismatch:** `tdm_start` sender writes nothing; receiver reads a string.
- **Hook argument shift:** dot-defined `MODE.GuiltCheck(Attacker, ...)` is called by dispatcher as `func(ModeTable, ...)`.
- **Attachment injection:** arbitrary client attachment ID reaches `hg.AddAttachmentForce` if the player owns the referenced weapon and has money.
- **Unused `TeamBased`:** catalog restriction is never enforced in the receiver.
- **Duplicate start lock:** shared movement hook plus client `StartCommand`; authority/prediction behavior unverified.
- **Empty public callbacks:** `GetPlySpawn`, `RoundThink`, `CanSpawn`, `PlayerDeath`, `AddHudPaint` may intentionally override defaults or accidentally suppress inherited behavior.

### Required validation

Full dedicated-server cycle; missing map points; team balance/disconnect/incapacitation; `tdm_start` packet capture; malformed/oversized/rate-limited purchases; arbitrary attachments; wrong-team/dead-player purchases; movement lock under latency.

---

## `MODE-cstrike` — Counter-Strike multi-round TDM derivative

### Files, inheritance, and metadata

- `sh_cstrike.lua` blob `66a341d157a06b6c09bffd5a4ad34e22570e4ffc` sets `MODE.base = "tdm"`, `MODE.name = "cstrike"`, `PrintName = "Counter-Strike"`, and registers `BOMB_ZONE_A`, `BOMB_ZONE_B`, `HOSTAGE_DELIVERY_ZONE` map-point types.
- `sv_cstrike.lua` blob `f194fe0a1693e31f796de705572d4b8dcd03a0ad` owns lifecycle/economy/objectives.
- `cl_cstrike.lua` blob `843e2b89ed0431ccbf044c11853881a0e531e13a` extends inherited TDM HUD through `AddHudPaint`.
- `KillMoney = 1000`; `StartMoney = 1000`; `start_time = 20`; `Rounds = 5`; `ROUND_TIME = 240`; `CooldownRounds = 5`; `ForBigMaps = false`.
- Registration requires `tdm` to already exist. Mode-directory order is unsorted, so base-before-child stability requires runtime confirmation.

### Lifecycle and objectives

- `Intermission()` initializes/preserves multi-round state (`zb.RoundsLeft`, `zb.Winners`), chooses `bomb` or `hostage`, sends map points, spawns a bomb holder or hostage after three seconds, broadcasts `tdm_start` **with** the round-type string, and sends per-player `CS_Intermission`.
- `RoundStartPost()` queues another `cstrike` round while `RoundsLeft > 1`.
- `ShouldRoundEnd()` evaluates bomb state/team survival or hostage survival/delivery.
- `EndRound()` computes objective winner, pays teams, emits inherited `tdm_roundend` and `CS_Roundover`, tracks series wins, clears state when leaving the mode, and resolves the final series winner.
- `DontKillPlayer`/`OverrideBalance` preserve multi-round players/teams after the first round.

### Public surfaces

- Channels: `CS_Intermission`, `CS_Killfeed`, `CS_Roundover`, inherited `tdm_start`/`tdm_roundend`/buy channels.
- Convar `zb_killfeed`; command `tdm_setrounds`; project command `nextcsround`.
- Globals/state: `zb.RoundsLeft`, `zb.Winners`, `zb.rtype`, `zb.nextcsround`, `zb.bomb`, `zb.bombexploded`, `zb.hostage`, `zb.hostagepoints`, `zb.hostageLastTouched`; global `HostageInZone` and global `winreason` assignment.

### Verified defects and risks

1. **Launch validator overwritten:** first `CanLaunch()` requires team/objective points; a later `CanLaunch()` returns `true`, so point validation is dead.
2. **Empty-team random error:** delayed objective spawn performs `team_t[math.random(#team_t)]`; unconditional launch permits zero-sized team lists and `math.random(0)`.
3. **Winner encoding loss:** `net.WriteBool(winner)` receives numeric winner `0`, `1`, or `3`; all numbers, including `0`, are truthy in Lua, so the boolean cannot encode the winning team.
4. **Inheritance-order risk:** unsorted mode directory enumeration can register `cstrike` before `tdm`, while `InitMode` requires the base registry entry immediately.
5. **Potential series off-by-one/state coupling:** `RoundsLeft`, `RoundStartPost`, global next-round selection, and `EndRound` decrement/finalization interact across separate systems; runtime sequence must establish exact round count.
6. **Objective assumptions:** bomb/hostage creation assumes valid team player, valid spawned entity, organism initialization, and map-point tables.
7. **Damage-paid economy:** `HarmDone` awards `amt * KillMoney`, despite `KillMoney` naming and a shared accumulator; this appears damage-based rather than kill-based and can create extreme money changes.
8. **Global helper/state collision:** `HostageInZone`, `winreason`, and multiple `zb.*` fields are not mode-contained.

### Required validation

Force registration in reversed directory order; launch on maps with each missing point set; zero-player/one-team start; bomb plant/defuse/explosion and hostage rescue/death; packet schema for all CS channels; five-round series count; reconnect/team preservation; money bounds and friendly-fire behavior; mode exit/re-entry cleanup.

---

## `MODE-dm` — Free-for-all Deathmatch with shrinking zone

### Files and metadata

- `sh_dm.lua` blob `04291057292379f244b13eabc7a17170447d32c4` defines `MapSize = 7500`, `ZoneTimeToShrink = 120`, global-backed `GetZoneRadius`, and opening attack suppression.
- `sv_dm.lua` blob `f645861dedac8c5e6d0ff5159cae00c369a71d87` defines `name = "dm"`, `PrintName = "Deathmatch"`, `LootSpawn = false`, `GuiltDisabled = true`, `randomSpawns = true`, `ForBigMaps = false`, `Chance = 0.04`, and unconditional `CanLaunch()`.
- `cl_dm.lua` blob `4e7cce0fd01c100e8a687974f10609ebe7429a8e` owns zone rendering/audio and end UI.
- Replicated convar `deathmatch_nozone` disables the zone.

### Lifecycle and zone contract

- `Intermission()` cleans the map, forces non-spectators to team 0, averages player positions for `zonepoint`, chooses farthest distance as `zonedistance`, and sends vector+float through `dm_start`.
- `RoundStart()` chooses one loadout for all alive players, grants weapons/attachments/armor/medicine/grenades/class state.
- Server `Think` hook `bober` runs every 0.5 seconds after opening lock and iterates **all entities**; players outside radius are stunned, doors blasted, and many props dissolved.
- `ShouldRoundEnd()` ends at one or fewer alive players.
- `EndRound()` computes total harm by attacker, rewards winner and most-violent player, and sends both entities via `dm_end`.
- Client renders sphere, modulates looping zone audio, and displays winner/most-violent results.

### Verified defects and risks

1. **Empty-player division:** `centerpoint:Div(#poses)` runs even when there are no non-spectator players.
2. **Global zone state:** server writes `zonepoint`/`zonedistance`; client writes `ZonePos`/`zonedistance`; unscoped names can collide with other systems or stale rounds.
3. **Nil-current-mode guard:** server/client zone hooks only return when `CurrentRound()` exists and is not DM; a nil current round falls through and may use unset zone globals.
4. **High-cost entity sweep:** every 0.5 seconds the server scans all entities and may create dissolvers/blast doors; no spatial partition/budget is used.
5. **Disconnected timer capture:** delayed `ply.noSound = false` lacks an `IsValid(ply)` guard.
6. **Double reward:** round winner and most-violent player can be the same entity and receive both full reward grants.
7. **External URL remnants:** client retains remote music URL machinery and global `dmmusic`, even though the restart path is currently commented/uninvoked in the traced HUD.
8. **Shared replicated convar creation:** client and server both use `CreateConVar` fallback for `deathmatch_nozone`; ownership/replication startup order requires runtime validation.
9. **Zone radius sentinel:** absent/non-number `zonedistance` returns `0xFFFFFFFF`, masking missing initialization rather than reporting it.

### Required validation

Zero/one/many players; reconnect and spectator-only transitions; zone disabled/enabled; full shrink duration; entity-count stress test; door/prop exclusions; stale/nil zone state across mode changes/hotload; loadout entity failures; winner/most-violent identity overlap; client audio station cleanup.

---

## `MODE-hmcd` — Homicide base and submode family

### Files and metadata

- `sh_homicide.lua` blob `79d5b5e889ed17dec6c38dfb7e389695e0d83803`.
- `sv_homicide.lua` blob `af101a8e73b170ca67e5a8c951ec83dd0655e0c8`.
- `cl_homicide.lua` blob `6e15a2b3eae790d1e9525c78a5344f3efcfd1de3`.
- `start_time = 1`; `end_time = 7`; `ROUND_TIME = 600`; `randomSpawns`, `shouldfreeze`, `OverrideSpawn`, `LootSpawn`, `LootOnTime` true; `Chance = 0.2`; `LootDivTime = 500`; unconditional `CanLaunch()`.
- Owns nested `SubRoles`, `Professions`, `RoleChooseRoundTypes`, `Roles`, `Types`, loot, words/actions, and role flags.

### Player/mode state

- Player: `isTraitor`, `isGunner`, `isPolice`, `MainTraitor`, `SubRole`, `Profession`, appearance/organism/inventory/class mutations.
- Mode: `Type`, `saved.PoliceTime`, reinforcement flags/counts, role-selection timers/lists, traitor words/count, next-round traitor requests.
- Homicide type entries define chance/map-size function, loot, messages, traitor/gunner/police equipment, police timing and skill settings.
- Directly ranged server types: `standard`, `wildwest`, `gunfreezone`, `soe`; client also exposes `suicidelunatic`, `supermario`.

### Synchronization

`HMCD_RoundStart` client reads: traitor bool, gunner bool, type string, default-screen bool, subrole string, main-traitor bool, two word strings, uint(13) expected traitors, conditional color+name roster, profession string. Conditional sender branches remain to be exhaustively paired.

`EndRound()` clears reinforcement state/timers, captures traitor/gunner arrays, resets role flags, awards results, emits `ZB_TraitorWinOrNot`, and broadcasts `hmcd_roundend` as uint(13)+entities for traitors followed by uint(13)+entities for gunners.

### Public surfaces

Channels include `HMCDPoliceRole`, `HMCD(StartPlayersRoleSelection)`, `HMCD(EndPlayersRoleSelection)`, `HMCD(SetSubRole)`, `HMCD_RoundStart`, `HMCD_TraitorDeathState`, `HMCD_RequestTraitorStatuses`, `HMCD_UpdateTraitorAssistants`, `hmcd_announce_traitor_lose`, `hmcd_roundend`. Hooks include `PlayerDeath`, `PlayerSpawn`, `PlayerCanPickupWeapon`, project `Player_Death`, stale `RoundStateChange`, and all function-valued mode members. Admin command `hmcd_request_main_traitor` writes request state.

### Verified defects

1. `ShouldStartRoleRound()` hard-returns false; configured role selection is unreachable.
2. `hmcd_request_main_traitor` writes a table whose selection consumer is commented out.
3. reset hook waits for state `2`; verified lifecycle uses end state `3`, and emitter is unverified.
4. `standard` and `wildwest` police equipment call attachments with `gun` before its local declaration instead of `glock`.
5. `if math.random(0,1)` always succeeds because Lua treats `0` as truthy, so those invalid attachment calls always run.
6. `SpawnForce` compares `ply.afkTime2 > 60` without nil guard.
7. variable `HMCD_RoundStart` payload has no version/schema discriminator.
8. helpers/dot-defined functions become global hook candidates and may receive shifted arguments.
9. `hmcd_roundend` is registered multiple times.
10. round start/end mutates many external systems, creating a large integration blast radius.

### Required validation

Complete every sender/receiver and type body; run every submode at minimum/typical/high population; nil AFK/appearance/inventory/organism; disconnect/incapacitation/spectator; traitor/gunner/profession invariants; all reinforcement types; failed equipment grants; end arrays with zero/one/many entities; classify every function as engine hook, project hook, lifecycle, data callback, network helper, or internal helper.

## Next mode trace

1. Finish Homicide sender/receiver/type ranges.
2. Trace `homicide_fear` and determine whether it inherits or duplicates Homicide.
3. Trace `tdm_cstrike` entities (`bomb`, hostage interactions) and unresolved CS client receivers.
4. Continue remaining directories using actual file names/registration keys.
5. Produce a complete inheritance/load-order graph and mode-function collision matrix.