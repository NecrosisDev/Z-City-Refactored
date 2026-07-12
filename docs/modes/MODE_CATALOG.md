# ZCity Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This catalog records actual registration IDs, files, inheritance, lifecycle, data/network contracts, dependencies, verified defects, and validation. Directory names and client presentation entries are not treated as launchable modes until server registration is verified.

## Verified dependency graph

```text
zb.modes
├─ tdm                                  standalone base
│  └─ cstrike                           MODE.base = "tdm"
├─ dm                                   standalone
└─ hmcd                                 standalone registry entry
   ├─ standard                          server MODE.Types + SubModes
   ├─ wildwest                          server MODE.Types + SubModes
   ├─ gunfreezone                       server MODE.Types + SubModes
   ├─ soe                               server MODE.Types + SubModes
   ├─ suicidelunatic                    client presentation only in traced files
   └─ supermario                        client presentation + server branch, but no verified server type registration
```

`zb:GetMode(submode)` maps a registered `MODE.Types` key back to its owning registry key. `RoundInfo` sends the base key (`hmcd`); Homicide separately sends its active `MODE.Type`.

## Summary matrix

| ID | Directory | Base | Files verified | Effective launch contract | Primary dependencies |
|---|---|---|---|---|---|
| `tdm` | `tdm` | none | `sh_tdm.lua`, `sv_tdm.lua`, `cl_tdm.lua` | unconditional `true` | teams, inventory, classes, roles, attachments, armor, weapons, map points |
| `cstrike` | `tdm_cstrike` | `tdm` | `sh_cstrike.lua`, `sv_cstrike.lua`, `cl_cstrike.lua` | unconditional `true`; earlier point validator overwritten | TDM, bomb/hostage entities, organism, map points, harm tracking |
| `dm` | `dm` | none | `sh_dm.lua`, `sv_dm.lua`, `cl_dm.lua` | unconditional `true` | organism, appearance, armor, weapons, zone globals, entity iteration, harm tracking |
| `hmcd` | `homicide` | none | `sh_homicide.lua`, `sv_homicide.lua`, `cl_homicide.lua` | unconditional `true`; four server submodes use chance functions | organism, fake ragdoll, appearance, inventory, classes, roles, loot, weapons, persistence |

---

## `MODE-tdm` — Team Deathmatch

### Files and metadata

- `sh_tdm.lua` blob `1aa70fac82fc2556b71e0ada95a0b6b931eabfdc`.
- `sv_tdm.lua` blob `5dfaa969145a20912b76a278ea6e861fc0196c83`.
- `cl_tdm.lua` blob `c6e4254634502d2055c105ae321fd27e75b46a42`.
- `PrintName = "Team Deathmatch"`; `BuyTime = 40`; `StartMoney = 6500`; `start_time = 20`; `ROUND_TIME = 240`; `Chance = 0.04`; `ForBigMaps = true`; `buymenu = true`.
- Map points `HMCD_TDM_CT`/`HMCD_TDM_T` are registered, but current `CanLaunch()` returns true without checking them.

### Lifecycle and buy contract

1. `Intermission()` cleans the map, resets teams/money, and broadcasts `tdm_start` without fields.
2. Client `tdm_start` reads a string into `zb.rtype`, starts music, and removes fade.
3. `GiveEquipment()` sets class/role/cosmetics/inventory and baseline equipment.
4. `RoundStart()` unfreezes players; `ShouldRoundEnd()` delegates to alive-team winner logic; `EndRound()` awards results and broadcasts `tdm_roundend`.
5. Client sends `tdm_buyitem` as `{category, itemName}` or `{category, itemName, attachmentID}`. Server re-resolves item and checks time/money/weapon ownership, but not alive state, rate/size, `TeamBased`, or attachment membership.

### Verified defects

- Base TDM `tdm_start` sender/receiver schema mismatch; Counter-Strike writes the string expected by the inherited receiver.
- Dot-defined `MODE.GuiltCheck(Attacker, ...)` receives dispatcher-injected mode table as its first argument.
- Arbitrary client attachment IDs can reach `hg.AddAttachmentForce`; `TeamBased` metadata is not enforced.
- Opening movement is suppressed through both mode movement logic and a client `StartCommand` hook.
- Empty public callbacks may suppress intended fallback behavior.

### Required validation

Dedicated-server cycle; missing points; team balance/disconnect/incapacitation; packet capture; malformed/oversized/rate-limited purchases; attachment allowlist; wrong-team/dead-player purchase; movement prediction under latency.

---

## `MODE-cstrike` — Counter-Strike multi-round TDM derivative

### Files, inheritance, and lifecycle

- `sh_cstrike.lua` blob `66a341d157a06b6c09bffd5a4ad34e22570e4ffc`: `base = "tdm"`, `name = "cstrike"`, map-point registrations.
- `sv_cstrike.lua` blob `f194fe0a1693e31f796de705572d4b8dcd03a0ad`: lifecycle, objectives, series state, economy.
- `cl_cstrike.lua` blob `843e2b89ed0431ccbf044c11853881a0e531e13a`: inherited HUD extension.
- `KillMoney = 1000`; `StartMoney = 1000`; `start_time = 20`; `Rounds = 5`; `ROUND_TIME = 240`; `CooldownRounds = 5`; `ForBigMaps = false`.
- `Intermission()` chooses bomb/hostage, sends objective points, spawns objective after three seconds, writes round type through inherited `tdm_start`, and sends `CS_Intermission`.
- `RoundStartPost()` queues another `cstrike` round; `EndRound()` computes objective winner, pays teams, emits `tdm_roundend`/`CS_Roundover`, tracks series wins, and clears state when leaving.

### Public state

Channels `CS_Intermission`, `CS_Killfeed`, `CS_Roundover` plus inherited TDM channels; convar `zb_killfeed`; command `tdm_setrounds`; project command `nextcsround`; `zb.RoundsLeft`, `zb.Winners`, `zb.rtype`, `zb.nextcsround`, bomb/hostage globals; global `HostageInZone` and `winreason` assignment.

### Verified defects

- A point-validating `CanLaunch()` is overwritten by a later unconditional definition.
- Delayed objective spawning indexes `team_t[math.random(#team_t)]`; empty teams can call `math.random(0)`.
- `CS_Roundover` writes numeric winner `0|1|3` through `net.WriteBool`; all numeric values are truthy in Lua, so team identity is lost.
- Unsorted directory order can register child before base.
- Multi-round state is split between mode and global round selection, creating off-by-one/cleanup risk.
- `HarmDone` pays `amt * KillMoney`, behaving as damage-based economy despite the name.
- Objective creation assumes valid players, entities, organism state, and points.

### Required validation

Reversed registration order; missing point permutations; zero-player/one-team start; bomb and hostage outcomes; all packet schemas; exact series count; reconnect/team persistence; money bounds/friendly fire; mode exit/re-entry cleanup.

---

## `MODE-dm` — Free-for-all Deathmatch with shrinking zone

### Files and lifecycle

- `sh_dm.lua` blob `04291057292379f244b13eabc7a17170447d32c4`: zone radius and opening attack suppression.
- `sv_dm.lua` blob `f645861dedac8c5e6d0ff5159cae00c369a71d87`: `name = "dm"`, lifecycle, loadouts, server zone processing.
- `cl_dm.lua` blob `4e7cce0fd01c100e8a687974f10609ebe7429a8e`: zone rendering/audio/end UI.
- `Intermission()` averages non-spectator positions into `zonepoint`, chooses farthest distance, and sends `dm_start` vector+float.
- One loadout is selected for all alive players. A server `Think` hook scans all entities every 0.5 seconds after the opening lock, stunning players, blasting doors, and dissolving props outside the zone.
- Round ends with one or fewer alive; `dm_end` sends winner and most-violent entities.

### Verified defects

- No participants causes `centerpoint:Div(0)`.
- Zone state uses unscoped globals on both realms and can remain stale across rounds/hotload.
- Zone hooks fall through when `CurrentRound()` is nil and may use unset state.
- Full entity sweep every 0.5 seconds has no spatial partition or budget.
- Delayed player callback lacks `IsValid`; winner and most-violent player may receive duplicate full rewards.
- Missing zone state returns `0xFFFFFFFF`, hiding initialization failure.
- Remote-music/global remnants remain in client code.

### Required validation

Zero/one/many players; spectator-only/reconnect; zone on/off; full shrink; entity stress; stale state across mode changes; loadout failures; duplicate-reward identity; audio cleanup.

---

## `MODE-hmcd` — Homicide base and submode family

### Files and registration

- `sh_homicide.lua` blob `79d5b5e889ed17dec6c38dfb7e389695e0d83803`.
- `sv_homicide.lua` blob `af101a8e73b170ca67e5a8c951ec83dd0655e0c8`.
- `cl_homicide.lua` blob `6e15a2b3eae790d1e9525c78a5344f3efcfd1de3`.
- `start_time = 1`; `end_time = 7`; `ROUND_TIME = 600`; random/override spawn, freeze, loot flags enabled; `Chance = 0.2`; unconditional `CanLaunch()`.
- Server `SubModes()` returns only `soe`, `standard`, `wildwest`, and `gunfreezone`.
- Client presentation also defines `suicidelunatic` and `supermario`; the traced server file has a `supermario` branch but no verified `MODE.Types.supermario`/`suicidelunatic` definition. These are `Legacy Claim`/unresolved, not verified launchable submodes.

### State and lifecycle

- Player state: `isTraitor`, `isGunner`, `isPolice`, `MainTraitor`, `SubRole`, `Profession`, appearance/organism/inventory/class mutations.
- Mode state: active type, police timing/reinforcement counters, role-selection list/timers, traitor words/count, next-round traitor requests.
- `Intermission()` chooses/accepts a server submode, kills/resets non-spectators, chooses traitor words, calculates traitor count, and assigns roles.
- `RoundStart()` either opens role selection or calls `SpawnPlayers`; role selection is currently impossible because `ShouldStartRoleRound()` hard-returns false.
- Police/SWAT/National Guard convert eligible dead players after timers. `EndRound()` captures traitor/gunner arrays, clears role flags, awards outcomes, emits `ZB_TraitorWinOrNot`, and sends `hmcd_roundend`.

### `HMCD_RoundStart` contract

Server writes to each player:

1. traitor bool;
2. gunner bool;
3. type string;
4. `screen_time_is_default` bool (traced normal spawn writes `true`);
5. subrole string;
6. main-traitor bool;
7. two traitor-word strings or empty strings;
8. uint(`TraitorExpectedAmtBits`) traitor count;
9. for a main traitor, color+name entries;
10. profession string.

Client reads the same order, but loops exactly the transmitted traitor count for main-traitor entries. The server count includes every traitor while the entry list includes only traitors with `CurAppearance`; one missing appearance underwrites the list and causes the client to decode profession/remaining bytes as color/name data. The packet has no version, branch discriminator beyond existing booleans, entry count separate from traitor count, or recovery boundary.

A delayed `HMCD_UpdateTraitorAssistants` packet separately sends uint8 entry count followed by color, name, and SteamID for each assistant. Spawn/death hooks rebuild and resend it to main traitors; the client receiver has not yet been located in verified files.

### Other verified payloads

- `HMCD(StartPlayersRoleSelection)`: server sends role string to main traitor; client opens role UI; client acknowledges on the same channel with no payload; server only removes sender from `ChoosingPlayersList`.
- `HMCD(EndPlayersRoleSelection)`: no payload; client closes panel.
- `HMCD(SetSubRole)`: client reads one string; sender/validation unresolved.
- `HMCD_TraitorDeathState`: appearance name string + alive bool to main traitors.
- `HMCD_RequestTraitorStatuses`: no client payload; server requires traitor+main-traitor and replies with death-state packets.
- `hmcd_roundend`: uint traitor count/entities then uint gunner count/entities. Client assigns flags to each read entity without validating entity validity.

### Verified defects

1. Role selection hard-returns false; its configured workflow is unreachable.
2. Requested-main-traitor command writes state whose selection consumer is commented out.
3. Reset hook waits for stale state `2`; verified round lifecycle ends at `3`, and the hook emitter remains unverified.
4. Standard/wildwest police attachment calls use undefined `gun` before declaration instead of `glock`.
5. `if math.random(0,1)` always succeeds because `0` is truthy.
6. `SpawnForce` compares possibly nil `afkTime2 > 60`.
7. `HMCD_RoundStart` can desynchronize when traitor count and appearance-backed entry count differ.
8. Client-only extra submodes and the server `supermario` branch appear unreachable from the verified server type registry.
9. Helpers and dot-defined functions become hook candidates and may receive shifted arguments.
10. `hmcd_roundend` registration is duplicated; client trusts read entities.
11. Reinforcement equipment assumes every `Give` returns a valid weapon before ammo/attachment calls.
12. Round start/end directly mutates many external systems, so local mode validation cannot establish integration safety.

### Required validation

- Exhaustively pair every sender/receiver and conditional packet branch.
- Test `HMCD_RoundStart` with traitors missing appearance and zero/one/many assistants.
- Locate/verify assistant, police-role, subrole, and role-selection response consumers.
- Run each verified server submode at minimum/typical/high populations, nil AFK/appearance/inventory/organism, disconnect/incapacitation/spectator, and failed equipment grants.
- Verify traitor/gunner/profession invariants, all reinforcement types, end arrays, and every function classification.
- Determine whether `suicidelunatic`/`supermario` are defined in another loaded file or are stale client-only content.

## Next mode trace

1. Locate unresolved Homicide channel endpoints and any external type augmentation.
2. Discover actual files/registration for `homicide_fear` through repository evidence.
3. Trace Counter-Strike bomb/hostage entities and unresolved CS receivers.
4. Continue remaining mode directories using actual filenames and registration IDs.
5. Produce complete inheritance/load-order and mode-function collision matrices.