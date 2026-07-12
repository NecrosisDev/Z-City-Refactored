# Mode Function Classification Matrix

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / exact Homicide endpoint batch added`  
**Reviewed:** 2026-07-12

This is the authoritative cross-mode index for function-valued `MODE` members. The loader registers every function key as a dynamic hook candidate and calls the selected callback as `func(modeTable, ...)`; therefore classification is required before refactoring registration. Rows below contain only functions or function families verified in fetched source/catalog evidence. Missing rows are evidence gaps, not proof that no function exists.

## Classification rules

| Class | Meaning | Dispatcher expectation |
|---|---|---|
| lifecycle | Called by the round framework at a defined transition | method-style `self` is expected |
| engine hook | Name overlaps a Garry's Mod hook and may be reached by the dynamic dispatcher | method-style `self` plus engine arguments |
| project hook | Name overlaps a project-emitted hook | method-style `self` plus project arguments |
| data callback | Queried for a value such as launch eligibility, spawn position, winner or guilt | return contract must be preserved |
| network helper | Builds, validates or reacts to a network operation | should not become a generic hook without explicit intent |
| internal helper | Mode-private implementation detail | automatic hook registration is accidental exposure |
| unresolved | Function is known to exist but exact role/signature is not yet paired | do not refactor until source trace closes it |

## Framework-wide collision contract

| Function/key family | Intended class | Collision/argument risk |
|---|---|---|
| `CanLaunch` | data callback | invoked as a method in catalogs; duplicate definitions can silently replace prerequisite checks |
| `Intermission`, `RoundStart`, `RoundStartPost`, `RoundThink`, `ShouldRoundEnd`, `EndRound` | lifecycle | inherited modes may call base implementations while replacing adjacent state, producing mixed lifecycle semantics |
| `GiveEquipment`, `PlayerSpawn`, `PlayerDeath`, `HarmDone`, `GuiltCheck` | engine/project/data callback depending on framework owner | every key becomes a dynamic hook; dot-defined `GuiltCheck(Attacker,...)` receives the mode table as `Attacker` |
| `GetTeamSpawn`, spawn-override members | data callback | spelling and consumer contract are unresolved; `OverideSpawnPos` appears in multiple modes |
| mode-private helpers such as event, wave, extraction, possession and winner helpers | internal helper/network helper | currently exposed if stored directly on `MODE`; names can collide with hooks or another inherited member |

## Core competitive and Homicide family

| Mode | Verified function/member | Class | Realm | Contract and collision notes |
|---|---|---|---|---|
| `tdm` | `CanLaunch` | data callback | server | unconditional `true`; does not validate registered team points |
| `tdm` | `Intermission` | lifecycle | server | cleans map, resets teams/money, sends `tdm_start` |
| `tdm` | `GiveEquipment` | lifecycle/internal boundary | server | mutates class, role, appearance, inventory, armor and weapons; integration validity assumed |
| `tdm` | `ShouldRoundEnd` / `EndRound` | lifecycle | server | alive-team winner and awards; delayed/client presentation follows |
| `tdm` | `GuiltCheck` | data callback accidentally hook-exposed | server | dot-defined signature is shifted by dispatcher-injected mode table |
| `cstrike` | `CanLaunch` (two definitions) | data callback | server | point validator is overwritten by later unconditional definition; name-keyed last writer expected |
| `cstrike` | `Intermission` | lifecycle | server | chooses objective and schedules bomb/hostage creation; depends on inherited TDM start contract |
| `cstrike` | `RoundStartPost` | lifecycle/project callback | server | queues another `cstrike` round; collision with global next-round state |
| `cstrike` | `EndRound` | lifecycle | server | objective winner, economy, series state and mode-exit cleanup |
| `cstrike` | `HarmDone` | engine/project hook | server | damage amount is multiplied by `KillMoney`; semantics conflict with name |
| `dm` | `Intermission` | lifecycle | server | computes zone from participants; zero participants divides by zero |
| `dm` | `ShouldRoundEnd` / `EndRound` | lifecycle | server | one-or-fewer alive; winner/most-violent reward identity can duplicate |
| `dm` | zone processing helper(s) | internal helper/direct hook boundary | mixed | global zone state and a server `Think` scan operate outside a centralized ownership contract |
| `hmcd` | `CanLaunch` | data callback | server | unconditional `true` |
| `hmcd` | `SubModes` | data callback | server | returns only `soe`, `standard`, `wildwest`, `gunfreezone` in verified source |
| `hmcd` | `Intermission` / `RoundStart` / `RoundThink` / `EndRound` | lifecycle | server | broad role, reinforcement, organism, inventory, persistence and packet coupling |
| `hmcd` | `ShouldStartRoleRound` | data callback/internal helper | server | hard-returns false; configured role-selection workflow unreachable |
| `hmcd` | `GetActivePlayers` | internal helper | server | returns dead, non-spectator, non-AFK players despite the name; used by reinforcement spawning |
| `hmcd` | `SpawnPlayers` / `SpawnForce` | internal helper | server | stored on mode and therefore hook-exposed; nil AFK/equipment/state assumptions |
| `hmcd` | `EquipSWAT` / `EquipNationalGuard` | internal helper | server | loadout/class helpers stored on `MODE`, therefore registered as generic hook candidates |
| `hmcd` | `SendTraitorDeathState` | network helper | server | emits appearance name + alive state only to main-traitor recipients |
| `hmcd` | `StartPlayersRoleSelection` | network/lifecycle helper | server | sends role-selection request and extends start time; upstream predicate hard-disables this path |
| `hmcd` | role-selection acknowledgement receiver | network endpoint, not `MODE` member | server | removes sender from `ChoosingPlayersList`; no payload; membership is the authorization boundary |
| `fear` | `AfterBaseInheritance` | lifecycle/assembly callback | shared/server | aliases inherited types; requires `hmcd` to have loaded first |
| `fear` | `CanLaunch` | data callback | server | hard-disabled; does not prevent direct hooks/timers from loading |
| `fear` | `Intermission` / `RoundThink` / `ShouldRoundEnd` | lifecycle | server | replaces role/end behavior while calling inherited Homicide `RoundThink` |
| `fear` | event registry/start/stop/scare helpers | internal helpers | mixed | stored on mode or direct hooks; nil events, failed starts and cleanup leaks |
| `fear` | victim/light/disappearance/afterlife helpers | internal/network helpers | mixed | typo, global response race, untrusted samples and timer/hook ownership risks |

## Team and PvE modes

| Mode | Verified function/member | Class | Realm | Contract and collision notes |
|---|---|---|---|---|
| `hl2dm` | `CanLaunch` | data callback | server | unconditional; ignores points/team prerequisites |
| `hl2dm` | `Intermission` / `GiveEquipment` / `ShouldRoundEnd` / `EndRound` | lifecycle | server | team setup, subclass state and winner packet; end schema mismatched |
| `hl2dm` | `GuiltCheck` | data callback accidentally hook-exposed | server | dot-defined argument shift |
| `coop` | `CanLaunch` | data callback | server | requires a valid `trigger_changelevel` |
| `coop` | `Intermission` / equipment/spawn/end helpers | lifecycle/internal | server | map progression, persistence and possession are tightly coupled |
| `coop` | friendly-fire callback | engine hook | server | verified hook body performs no action |
| `coop` | possession validators/discovery/replacement helpers | internal helpers | server | zombie validation and target discovery disagree; removal precedes replacement success |
| `defense` | `CanLaunch` | data callback | server | requires a spawn and nav area |
| `defense` | `Intermission`, preparation, round end | lifecycle | server | calls unresolved `EndWave()` at wave zero and depends on external wave methods |
| `defense` | `StartNewWave`, `SpawnWave`, `OnWaveComplete`, `EndWave` | unresolved lifecycle/internal helpers | server | owners/files not yet enumerated; must not be refactored from one-sided call evidence |
| `defense` | support/highlight helpers | unresolved network helpers | mixed | endpoint, authorization, cost, cooldown and rate contracts unresolved |
| `criresp` | `CanLaunch` | data callback | server | validates points and playing-player minimum |
| `criresp` | `AssignTeams` | internal helper | server | counts all connected users rather than shared playing eligibility |
| `criresp` | `Intermission` / `RoundStart` / `EndRound` | lifecycle | server | readiness, delayed spawn, sniper enforcement and statistics |
| `criresp` | customization/readiness handlers | network helpers | server | callable too broadly; partial bounds, no phase/rate/bodygroup-model validation |
| `criresp` | `GuiltCheck` | data callback accidentally hook-exposed | server | dot-defined argument shift |
| `pathowogen` | `CanLaunch` | data callback | server | hard-disabled; loaded members/direct effects still require inactive-mode audit |
| `pathowogen` | `Intermission` / `RoundStart` / `ShouldRoundEnd` / `EndRound` | lifecycle | server | role assignment, assimilation, extraction, vehicles and consequence report |
| `pathowogen` | `GetRandomSpawn` | internal helper | server | recursive retry has no exhaustion termination |
| `pathowogen` | extraction/helicopter/Delta/assimilation helpers | internal/network helpers | server | entity, timer, weld, class and external-addon contracts are not isolated |
| `pathowogen` | `GuiltCheck` | data callback accidentally hook-exposed | server | dot-defined argument shift |

## Additional standalone and administrator modes

| Mode | Verified function/member | Class | Realm | Contract and collision notes |
|---|---|---|---|---|
| `riot` | `CanLaunch` | data callback | server | at least five non-spectators; point prerequisites ignored |
| `riot` | `Intermission` / equipment / winner / end | lifecycle | server | spectator shuffle distortion and TDM-point coupling |
| `riot` | `GuiltCheck` | data callback accidentally hook-exposed | server | dot-defined argument shift |
| `riot` | `OverideSpawnPos` | unresolved data member/callback | server/shared | misspelled; actual framework consumer not traced |
| `gwars` | `CanLaunch` | data callback | server | unconditional despite point dependency |
| `gwars` | lifecycle/equipment/SWAT reinforcement helpers | lifecycle/internal | server | delayed callbacks, team-2 exclusion and undefined `boringround` |
| `gwars` | `GuiltCheck` / `OverideSpawnPos` | data/unresolved | server | argument shift plus misspelled spawn contract |
| `superfighters` | `CanLaunch` / `ShouldRoundEnd` / `EndRound` | data/lifecycle | server | random-spawn prerequisite omitted; delayed winner resampled |
| `superfighters` | opening attack callbacks | engine/project hook candidates | shared | block attacks/leg attacks for five seconds |
| `scugarena` | `CanLaunch` / `ShouldRoundEnd` / `EndRound` | data/lifecycle | server | chance zero, no minimum population, delayed winner |
| `scugarena` | opening attack callbacks | engine/project hook candidates | shared | block attacks for twenty seconds |
| `event` | `CanLaunch` | data callback | server | unconditional with chance zero; force/admin-driven in practice |
| `event` | `Intermission` / `RoundStart` / `RoundThink` / `ShouldRoundEnd` / `EndRound` | lifecycle | server | mutable end logic, duplicate loot spawning and delayed winner |
| `event` | loot load/save/sync/add/remove/request helpers | network/persistence/internal helpers | mixed | unversioned schema, overloaded channel, weak validation and inactive timers |
| `event` | eventer/admin command callbacks | network/admin helpers | server | command callbacks misuse `args` table as scalar |

## Exact source inventory — Homicide endpoint batch

| Symbol / endpoint | Definition style | Source evidence | Expected arguments / payload | Caller / consumer | Final classification |
|---|---|---|---|---|---|
| `MODE:GetActivePlayers()` | method | `gamemodes/zcity/gamemode/modes/homicide/sv_homicide.lua`, blob `af101a8e73b170ca67e5a8c951ec83dd0655e0c8` | none beyond `self`; returns player array | `RoundThink`, delayed SWAT spawn | internal helper; accidental hook surface |
| `MODE:SpawnForce(teamtype,count)` | method | same blob | team key, bounded requested count; returns spawned count | police/SWAT/National Guard branches | internal helper; accidental hook surface |
| `MODE:EquipSWAT(ply,index)` | method | same blob | valid spawned player, one-based role index | `SpawnForce("swat",...)` | internal helper; accidental hook surface |
| `MODE:EquipNationalGuard(ply,index)` | method | same blob | valid spawned player, one-based role index | `SpawnForce("nationalguard",...)` | internal helper; accidental hook surface |
| `MODE.StartPlayersRoleSelection()` | dot function | same blob | no declared args; dispatcher would inject mode table if hook-run | `RoundStart` only when `ShouldStartRoleRound` succeeds | network/lifecycle helper; currently unreachable and signature-shift exposed |
| `MODE:SendTraitorDeathState(traitor,is_alive)` | method | same blob | traitor with `CurAppearance`, bool state | death/spawn hooks and status-request response | network helper; accidental hook surface |
| `HMCD_UpdateTraitorAssistants` client receiver | direct `net.Receive` | `gamemodes/zcity/gamemode/modes/homicide/cl_hud.lua`, blob `87356c1f96336ca160841293500b374dc668d089` | uint8 count then repeated color/name/SteamID | updates `MODE.TraitorsLocal` | endpoint paired; not a mode function |
| `HMCD_TraitorDeathState` client receiver | direct `net.Receive` | same blob | string appearance name, bool alive | updates assistant status cache | endpoint paired; not a mode function |

Line-precise offsets remain required for the complete source inventory. Blob + symbol evidence above closes endpoint identity and behavior but is not treated as completion of the all-mode line-enumeration requirement.

## Highest-priority collision groups

1. **`GuiltCheck`:** repeated dot-defined signature bug across TDM, HL2DM, CO-OP, Defense, Crisis Response, Riot, Gang Wars and Pathowogen evidence.
2. **`CanLaunch`:** duplicate/overwritten or unconditional checks allow modes to launch without required points, teams, spawns, dependencies or population.
3. **winner functions:** several modes compute or resample winners in delayed callbacks after authoritative end.
4. **spawn members:** `OverideSpawnPos` spelling and actual consumer remain unresolved; correcting it without tracing the framework could silently disable existing behavior.
5. **internal helpers on `MODE`:** event, wave, possession, fear and extraction helpers are automatically exposed as hook candidates.
6. **inheritance:** CStrike and Fear require base registration before child assembly; unsorted directory enumeration makes callback sets nondeterministic.

## Required completion trace

- Fetch every verified server/shared mode file and enumerate all assignments whose final value is a function, including anonymous assignments and inherited replacements.
- Record exact definition style (`function MODE:X` versus `function MODE.X`), source line/blob, expected arguments, return shape, realm and caller.
- Pair each name with core/project/engine hook emitters and prove whether inactive modes are gated before invocation.
- Mark duplicate definitions and effective last-writer behavior separately from runtime-confirmed behavior.
- Move genuine helpers off the auto-hook surface only during an approved implementation package, after callers and inheritance are complete.
