# ZCity Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** commit `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

## Purpose

This catalog records actual registered mode identifiers, source files, realm parity, inheritance, submodes, lifecycle contracts, public surfaces, dependencies, defects, and validation. Directory names are not treated as mode IDs until `MODE.name` is verified.

## Dependency graph established so far

```text
zb.modes
├─ tdm                       (standalone mode; no `base` observed)
└─ hmcd                      (standalone registry entry; no `base` observed)
   ├─ standard               (`MODE.Types.standard` submode)
   ├─ wildwest               (`MODE.Types.wildwest` submode)
   ├─ gunfreezone            (`MODE.Types.gunfreezone` submode)
   ├─ soe                    (`MODE.Types.soe` submode)
   ├─ suicidelunatic         (client-visible and server type definition pending exact range citation)
   └─ supermario             (client-visible and server type definition pending exact range citation)
```

`zb:GetMode(submode)` resolves any `MODE.Types[submode]` key back to the owning base registry key. `RoundInfo` sends the base mode name (`hmcd`); Homicide's own `HMCD_RoundStart` payload sends the active `MODE.Type`.

---

## `MODE-tdm` — Team Deathmatch

### Identity and files

- **Registry key:** `tdm`.
- **Base:** none observed.
- **Files verified:**
  - `gamemodes/zcity/gamemode/modes/tdm/sh_tdm.lua` — shared buy catalog and movement/leg-attack hooks.
  - `gamemodes/zcity/gamemode/modes/tdm/sv_tdm.lua` — authoritative lifecycle, equipment, economy, network receivers.
  - `gamemodes/zcity/gamemode/modes/tdm/cl_tdm.lua` — HUD, start/end presentation, buy menu and purchase sender.
- **Realm parity:** server and client both set `MODE.name = "tdm"`; shared file uses the loader-provided table through `local MODE = MODE`.
- **Registration order dependency:** all three realm files must populate the same temporary mode before `InitMode`; effective sibling order remains dependent on unsorted `file.Find`, but realm-separated files do not execute together in one realm except the shared file plus that realm's file.

### Verified metadata and launch contract

- `PrintName = "Team Deathmatch"`.
- `BuyTime = 40`, `StartMoney = 6500`, `start_time = 20`, `buymenu = true`, `ROUND_TIME = 240`, `Chance = 0.04`, `ForBigMaps = true`.
- `CanLaunch()` currently returns `true`; map-point checks for `HMCD_TDM_T` and `HMCD_TDM_CT` are commented out.
- Team spawn points use those map-point groups when available, then the gamemode spawn system falls back to random spawn behavior.

### Lifecycle and data flow

1. Round preparation calls `Intermission()`:
   - `game.CleanUpMap()`;
   - each player runs `SetupTeam` and receives `TDM_Money = 6500`;
   - server broadcasts `tdm_start` with **no written payload**.
2. Client `tdm_start` receiver plays audio, then calls `net.ReadString()` into `zb.rtype`, starts dynamic music, and removes fade.
3. `GiveEquipment()` asynchronously updates inventory/player class/role/cosmetics and grants baseline melee, medical, radio, and hands equipment.
4. `RoundStart()` unfreezes all players.
5. `ShouldRoundEnd()` delegates to `zb:CheckWinner(zb:CheckAliveTeams(true))`.
6. `EndRound()` schedules `tdm_roundend`, awards experience/skill based on the winning team, and client opens the end menu.

### Buy-system contract

- Shared `MODE.BuyItems[category][displayName]` entries contain `Type`, `ItemClass`, `Price`, `Category`, optional `Attachments`, optional `Amount`, and optional `TeamBased`.
- Client buy menu sends `tdm_buyitem` as a Lua table:
  - `{category, displayName}` for item/ammunition purchase;
  - `{category, displayName, attachmentID}` for attachment purchase.
- Server checks active mode `buymenu`, 40-second window, table type, category/name existence, money, and weapon ownership for attachment purchases.
- Server does **not** verify player alive state, payload length/size, value types beyond lookup, team restrictions, or whether the requested attachment is present in the selected item's allowed `Attachments` list.
- Attachment purchases therefore trust arbitrary client-provided attachment IDs after only weapon ownership and money checks.

### Hooks/public surfaces

- Mode functions registered as hook candidates include `HG_MovementCalc_2`, `PlayerCanLegAttack`, `GuiltCheck`, lifecycle methods, `ShowSpare1`, and empty helpers.
- Network channels: `tdm_start`, `tdm_roundend`, `tdm_open_buymenu`, `tdm_buyitem`.
- Player state: NWInt `TDM_Money`; inventory netvar; roles/classes; `ply.organism.allowholster`.
- Map-point registrations: `zb.Points.HMCD_TDM_CT`, `zb.Points.HMCD_TDM_T`.

### Verified defects and risks

1. **`tdm_start` payload mismatch:** server broadcasts no fields, while client immediately reads a string. The exact runtime result must be captured, but sender and receiver contracts are statically inconsistent.
2. **Hook argument shift:** `MODE.GuiltCheck` is defined with dot syntax as `function MODE.GuiltCheck(Attacker, Victim, add, harm, amt)`, while the mode dispatcher calls every function as `func(ModeTable, ...)`. This shifts all expected hook arguments by one unless the intended hook contract explicitly includes the mode table, unlike the function's parameter names.
3. **Arbitrary attachment request:** `tItem[3]` is passed to `hg.AddAttachmentForce` without membership validation against `item.Attachments`.
4. **Client-authoritative catalog selector:** the server safely re-resolves category/item, but attachment choice and request frequency remain client-controlled and lack explicit rate limits.
5. **Unused team restrictions:** catalog entries contain `TeamBased`, but the traced purchase receiver does not enforce it.
6. **Empty lifecycle/public methods:** `GetPlySpawn`, `RoundThink`, `CanSpawn`, `PlayerDeath`, and `AddHudPaint` are registered or consumed despite empty bodies; whether these intentionally override inherited/default behavior must be verified.
7. **Start lock duplication:** movement is suppressed through both a shared mode hook and a client `StartCommand` hook; server authority and prediction consistency require runtime validation.

### Validation required

- Capture `tdm_start` receive behavior and remove/fix the schema mismatch only after confirming no hidden writer.
- Assert server/client mode registration and callback sets.
- Run a full TDM cycle with and without map points, two teams, disconnects, incapacitation, end awards, and map cleanup.
- Fuzz `tdm_buyitem` with malformed/oversized tables, unknown categories/items, arbitrary attachments, wrong-team items, dead players, rapid requests, insufficient money, and invalid entity classes.
- Verify movement lock and buy-time boundaries under latency.

### Evidence

- `sh_tdm.lua` blob `1aa70fac82fc2556b71e0ada95a0b6b931eabfdc`.
- `sv_tdm.lua` blob `5dfaa969145a20912b76a278ea6e861fc0196c83`.
- `cl_tdm.lua` blob `c6e4254634502d2055c105ae321fd27e75b46a42`.

---

## `MODE-hmcd` — Homicide base registry entry and submode family

### Identity and files

- **Registry key:** `hmcd` (directory name is `homicide`).
- **Base:** none observed.
- **Files verified:**
  - `gamemodes/zcity/gamemode/modes/homicide/sh_homicide.lua` — name, presentation metadata, roles, subroles, professions, selection configuration, shared helper.
  - `gamemodes/zcity/gamemode/modes/homicide/sv_homicide.lua` — type definitions, loot, role assignment, police/SWAT/National Guard, lifecycle, networking and rewards.
  - `gamemodes/zcity/gamemode/modes/homicide/cl_homicide.lua` — type names/objectives, `HMCD_RoundStart` decoder, presentation and client role state.
- **Submode mechanism:** `MODE.Types`; `MODE.Type` defaults to `standard` and is assigned for an active round.
- **Client-visible type names:** `standard`, `soe`, `gunfreezone`, `suicidelunatic`, `wildwest`, `supermario`.
- **Shared role-choice type configuration:** role/profession selection is configured for `standard` and `soe`.

### Verified base metadata

- `start_time = 1`, `end_time = 7`, `ROUND_TIME = 600`.
- `randomSpawns = true`, `shouldfreeze = true`, `OverrideSpawn = true`, `LootSpawn = true`, `LootOnTime = true`.
- `Chance = 0.2`, `LootDivTime = 500`.
- `SetupChances()` initializes a chance entry for every `MODE.Types` key.
- `CanLaunch()` currently returns `true`.
- The mode owns large nested contracts for `SubRoles`, `Professions`, `RoleChooseRoundTypes`, `Roles`, `Types`, loot tables, words/actions, and player flags.

### Player/round state owned by the mode

- Player flags: `isTraitor`, `isGunner`, `isPolice`, `MainTraitor`, `SubRole`, `Profession`, plus appearance/organism/inventory/class mutations.
- Mode state: `Type`, `saved.PoliceTime`, `PoliceSpawned`, `deadPoliceCount`, `swatDeployed`, `spawnedPoliceCount`, `roundStartType`, `ChoosingPlayersList`, `RoleChooseRound`, `StartRoundTime`, traitor words/count, and next-round traitor request table.
- Persistent player counters use `SetPData` for Homicide wins/kills.

### Type selection and synchronization

- Homicide submodes use `MODE.Types[typeID]` with chance, map-size `ChanceFunction`, loot, messages, traitor/gunner/police equipment, police timing, launch behavior and skill settings.
- `standard`, `wildwest`, `gunfreezone`, and `soe` server type definitions are directly verified in traced ranges; remaining type bodies require exact server-range completion.
- `HMCD_RoundStart` is a mode-specific variable-length payload. Client reads, in order:
  1. local traitor bool;
  2. local gunner bool;
  3. type string;
  4. `screen_time_is_default` bool;
  5. subrole string;
  6. main-traitor bool;
  7. traitor word string;
  8. second word string;
  9. traitor count with `TraitorExpectedAmtBits` (13);
  10. conditional main-traitor roster entries of color + string;
  11. profession string.
- The conditional sender branches must be exhaustively paired with this decoder before the payload is considered stable.

### Lifecycle and dependencies

- Depends on organism state, appearance, inventory/netvars, player classes, roles, attachments, armor, fake-ragdoll-compatible entities, map size, loot spawning, skills/experience, PData, radio/weapon systems, and round orchestration.
- `CheckAlivePlayers` groups viable non-police players by traitor side and excludes incapacitated innocents.
- Police reinforcement converts dead, non-spectator, non-AFK players into police/SWAT/National Guard after mode/type-specific timers.
- `EndRound()` clears reinforcement timers/state, captures traitors/gunners, resets player role flags, awards skill/experience, emits `ZB_TraitorWinOrNot`, and broadcasts `hmcd_roundend` with entity arrays sized by a 13-bit count.

### Network/hook surfaces found in traced ranges

- Channels include `HMCDPoliceRole`, `HMCD(StartPlayersRoleSelection)`, `HMCD(EndPlayersRoleSelection)`, `HMCD(SetSubRole)`, `hmcd_announce_traitor_lose`, `HMCD_RoundStart`, `HMCD_TraitorDeathState`, `HMCD_RequestTraitorStatuses`, `hmcd_roundend`, `HMCD_UpdateTraitorAssistants`, plus additional untraced channels in the remaining file ranges.
- Hooks include direct `PlayerDeath`, `PlayerSpawn`, `PlayerCanPickupWeapon`, project `Player_Death`, `RoundStateChange`, and mode-function hook candidates.
- Admin command `hmcd_request_main_traitor` writes `MODE.NextRoundMainTraitors` outside active rounds.

### Verified defects and risks

1. **Role-selection hard disable:** `MODE.ShouldStartRoleRound()` begins with `do return false end`; its configured role-selection logic is unreachable.
2. **Requested main traitor path disabled:** `hmcd_request_main_traitor` writes `NextRoundMainTraitors`, but the selection loop that consumes this table is commented out.
3. **Stale state reset:** `RoundStateChange` resets `NextRoundMainTraitors` only when `new == 2`; the verified round-state machine ends at state `3`, and no emitter for this hook has yet been verified.
4. **Undefined police attachment variable:** at least `standard` and `wildwest` police equipment create `local glock` but call `hg.AddAttachmentForce(ply, gun, ...)` before a later local `gun` declaration. Those calls resolve an unrelated/global `gun` or `nil`, not the Glock.
5. **Lua truthiness misuse:** conditions `if math.random(0,1) then` are always true in Lua because `0` is truthy. The attachment calls above therefore always execute, intensifying the undefined-variable failure; similar conditions must be inventoried project-wide.
6. **Nil AFK comparison:** `SpawnForce` filters with `ply.afkTime2 > 60` without the nil guard used by `GetActivePlayers`; a player lacking `afkTime2` can cause a comparison error.
7. **Complex variable payload:** `HMCD_RoundStart` contains conditional fields and roster loops without a version/schema discriminator; any sender/receiver branch disagreement desynchronizes all subsequent reads.
8. **Mode table as global hook surface:** many helper methods and direct dot-defined functions are registered as hook candidates, risking argument shifts and unintended global hook collisions.
9. **Duplicate network registration:** `hmcd_roundend` is registered more than once in the same server file.
10. **Large cross-system blast radius:** round start/end directly mutates organism, inventory, appearance, classes, weapons, attachments, roles, persistence and entities; local validation cannot establish integration safety.

### Validation required

- Generate a complete server/client schema table for every Homicide channel and conditional branch.
- Run every submode with minimum/typical/high player counts, no AFK timestamp, missing appearance/inventory/organism state, spectators, disconnects, incapacitation, and failed weapon/entity grants.
- Validate traitor/gunner/profession assignment invariants and main-traitor selection.
- Exercise police, SWAT and National Guard reinforcement for every type; assert equipment and attachment entities are valid.
- Trace every function-valued member into one of: engine hook, project hook, lifecycle method, network helper, internal helper, or data callback.
- Verify end-state messages/entity counts and client decode for zero, one and many traitors/gunners.

### Evidence

- `sh_homicide.lua` blob `79d5b5e889ed17dec6c38dfb7e389695e0d83803`.
- `sv_homicide.lua` blob `af101a8e73b170ca67e5a8c951ec83dd0655e0c8`.
- `cl_homicide.lua` blob `6e15a2b3eae790d1e9525c78a5344f3efcfd1de3`.

## Next mode trace

1. Finish the untraced Homicide server/client ranges and formalize all submode type schemas.
2. Trace `tdm_cstrike`, `dm`, and other likely TDM-derived/related modes to determine whether inheritance is explicit or behavior is copied.
3. Trace `homicide_fear` and any mode resolving through `hmcd` types.
4. Continue all known mode directories, recording actual file names and registration keys rather than assuming directory-name identity.
5. Produce a mode-function collision matrix against all emitted engine/project hooks.