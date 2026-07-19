# Mode Function Dispatch Matrix

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified; auxiliary UI-only panel methods excluded  
**Reviewed:** 2026-07-12

## Purpose

The mode loader registers **every top-level function-valued `MODE` member** as a global hook candidate. This document distinguishes intended lifecycle/hooks from internal services that are accidentally published through `hook.Add`.

Nested functions stored inside data tables such as `MODE.Types.*.PoliceEquipment`, `MODE.SubRoles.*.SpawnFunction`, and local helpers are not registered by the mode loader. Direct `hook.Add` registrations are listed separately because they bypass mode-table dispatch and must gate themselves.

## Dispatcher contract

`gamemodes/zcity/gamemode/loader.lua` builds a realm-local `zb.modesHooks[modeName][functionName]` table and installs one global dispatcher per function name:

```text
hook event arguments
    -> dispatcher resolves zb.CROUND_MAIN / zb.CROUND / "tdm"
    -> selected mode callback receives MODE table as first argument
    -> up to six results are returned only when result #1 is non-nil
```

Consequences:

1. Colon-defined methods receive the expected `self`.
2. Dot-defined functions written without a `self` parameter receive shifted arguments.
3. Internal helpers become globally callable hook names.
4. Empty callbacks can suppress or replace inherited behavior.
5. Same-name functions across modes intentionally share one dispatcher, but same-name functions within one assembled mode are last-writer dependent.
6. Server and client registries are separate; the same callback name can have different implementations and contracts by realm.
7. Inheritance copies base functions before registration, so a child publishes inherited helpers and callbacks unless it overrides them.

## Classification legend

| Class | Meaning |
|---|---|
| `Lifecycle` | Called by the round/mode framework intentionally. |
| `Engine hook` | Matches a Garry's Mod hook and is intentionally dispatched. |
| `Project hook` | Matches a project-defined hook and is intentionally dispatched. |
| `Data callback` | Queried as mode data/behavior rather than emitted as a hook. |
| `Internal helper` | Intended for direct calls from the same subsystem; accidental hook surface. |
| `Empty override` | Function exists but has no behavior; can hide inherited/default behavior. |
| `Direct hook` | Registered with `hook.Add`, outside the mode dispatcher. |

## Registry summary

| Mode | Base | Effective risk summary |
|---|---|---|
| `tdm` | none | Small lifecycle plus buy/equipment surface; dot-defined guilt callback is shifted. |
| `cstrike` | `tdm` | Inherits the complete TDM hook set and adds series/objective helpers; duplicate `CanLaunch` leaves the unconditional version effective. |
| `dm` | none | Publishes zone helper as a hook and also owns two direct `Think` hooks. |
| `hmcd` | none | Large helper surface: role selection, spawning, reinforcement, equipment, status packets, and tracing all become hook names. |
| `fear` | `hmcd` | Inherits Homicide, overwrites selected lifecycle/render callbacks, and adds event/timer/victim-selection services as hooks despite `CanLaunch=false`. |
| `hl2dm` | none | Lifecycle plus role-reset helper; airstrike behavior is implemented through direct hooks/network receivers. |
| `coop` | none | Lifecycle plus loot/default-equipment services; possession is mostly direct-hook/local-helper driven. |
| `defense` | none | Largest accidental surface: wave orchestration, spawn search, timers, roles, economy, and NPC targeting are all hook candidates. |
| `criresp` | none | Mostly lifecycle; team assignment is an internal helper published as a hook. |
| `pathowogen` | none | Large scenario service surface including extraction, vehicles, dialogue, setup, and timers; normally disabled by `CanLaunch=false`. |
| `riot` | none | Conventional team-mode lifecycle with shifted dot-defined guilt callback. |
| `gwars` | none | Conventional team lifecycle plus `BoringRoundFunction`; shifted guilt callback. |
| `superfighters` | none | FFA lifecycle; shared attack gate plus client render callbacks. |
| `scugarena` | none | FFA lifecycle; shared attack hook and client render callbacks. |
| `event` | none | Admin event lifecycle plus persistence/loot-editor helpers exposed as hooks. |

---

## `tdm`

### Server — `modes/tdm/sv_tdm.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `GuiltCheck` | Project hook | Dot-defined; dispatcher inserts mode table before `Attacker`, shifting every argument. |
| `CanLaunch` | Data callback | Currently unconditional. |
| `Intermission` | Lifecycle | Cleans map, resets teams/economy, sends start packet. |
| `CheckAlivePlayers` | Internal helper | Winner helper accidentally published as a hook. |
| `ShouldRoundEnd` | Lifecycle | Uses team winner helper. |
| `RoundStart` | Lifecycle | Opening state transition. |
| `GetPlySpawn` | Empty override | No behavior. |
| `GiveEquipment` | Lifecycle | Applies classes, roles, inventory and loadout. |
| `RoundThink` | Empty override | Published every round tick despite no behavior. |
| `GetTeamSpawn` | Data callback | Returns T/CT point vectors. |
| `CanSpawn` | Empty override | No behavior. |
| `EndRound` | Lifecycle | Determines rewards and sends end packet. |
| `PlayerDeath` | Empty override | Engine-hook name with no behavior. |
| `ShowSpare1` | Engine hook | Opens buy menu for eligible player. |

### Client — `modes/tdm/cl_tdm.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `RenderScreenspaceEffects` | Engine hook | Opening fade. |
| `HUDPaint` | Engine hook | Intro/buy HUD. |
| `AddHudPaint` | Empty/internal extension | Child-mode extension point also registered as a global hook. |
| `RoundStart` | Lifecycle | Clears end/buy UI state. |

**Direct hook:** `StartCommand/TDM_DisallowMoveOrShoting` removes movement/attack input during opening lock.

## `cstrike` (`base = tdm`)

### Own server functions — `modes/tdm_cstrike/sv_cstrike.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `ChanceFunction` | Data callback | Selection weight helper; published as a hook. |
| `DontKillPlayer` | Internal/data callback | Series transition helper. |
| `CanLaunch` | Data callback | Defined twice; later unconditional definition replaces point validator. |
| `OverrideBalance` | Data callback | Team-balance behavior. |
| `RoundStartPost` | Project/lifecycle hook | Queues the next series round. |
| `Intermission` | Lifecycle | Chooses objective and sends objective/start packets. |
| `EndRound` | Lifecycle | Computes objective/team winner and series state. |
| `ShouldRoundEnd` | Lifecycle | Checks bomb/hostage/team outcome. |
| `RoundThink` | Empty override | Replaces inherited empty callback. |

### Effective inherited functions

`GuiltCheck`, `CheckAlivePlayers`, `RoundStart`, `GetPlySpawn`, `GiveEquipment`, `GetTeamSpawn`, `CanSpawn`, `PlayerDeath`, and `ShowSpare1` are inherited from TDM unless replaced above. The inherited dot-defined `GuiltCheck` remains argument-shifted.

### Client

`AddHudPaint` overrides TDM's empty extension. `RenderScreenspaceEffects`, `HUDPaint`, and `RoundStart` are inherited from TDM. Nested Derma receivers are not mode callbacks.

**Direct hook:** `HarmDone/CS_PlayerDeath` emits the custom killfeed and pays damage-derived money.

## `dm`

### Shared — `modes/dm/sh_dm.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `GetZoneRadius` | Internal/data helper | Dot-defined, globally published; uses global zone state. |
| `HG_MovementCalc_2` | Project hook | Removes attacks/selects hands during opening lock. |
| `PlayerCanLegAttack` | Project hook | Denies leg attack during opening lock. |

### Server — `modes/dm/sv_dm.lua`

`CanLaunch` (`Data callback`), `Intermission`, `ShouldRoundEnd`, `RoundStart`, `EndRound` (`Lifecycle`), `CheckAlivePlayers` (`Internal helper`), `PlayerDeath` (`Engine hook`), plus empty overrides `GiveWeapons`, `GiveEquipment`, `RoundThink`, and `CanSpawn`.

**Direct hook:** `Think/bober` performs the zone entity sweep and gates itself by current mode.

### Client — `modes/dm/cl_dm.lua`

`PostDrawTranslucentRenderables`, `RenderScreenspaceEffects`, and `HUDPaint` are engine/render hooks; `RoundStart` clears result flags/UI.

**Direct hook:** `Think/ZoneSoundThink`; its guard falls through when `CurrentRound()` is nil.

## `hmcd`

### Shared — `modes/homicide/sh_homicide.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `GetPlayerTraceToOther` | Internal helper | Dot-defined; receives shifted arguments when emitted as a hook. |

Nested subrole/profession/type callbacks remain data-table functions and are not individually registered.

### Server — `modes/homicide/sv_homicide.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `SetupChances` | Internal bootstrap helper | Published as global hook name. |
| `GetPlySpawn` | Empty override | No behavior. |
| `SubModes` | Data callback | Returns registered Homicide submode IDs. |
| `Intermission` | Lifecycle | Selects subtype, traitors, words and pre-round state. |
| `CheckAlivePlayers` | Internal helper | Builds innocent/traitor alive arrays. |
| `GetActivePlayers` | Internal helper | Finds dead non-spectator reinforcement candidates. |
| `RoundThink` | Lifecycle | Police/SWAT/National Guard deployment. |
| `SpawnForce` | Internal helper | Converts dead players into reinforcement roles. |
| `EquipSWAT` | Internal helper | Reinforcement equipment service. |
| `EquipNationalGuard` | Internal helper | Reinforcement equipment service. |
| `StartPlayersRoleSelection` | Internal workflow | Dot-defined and argument-shifted; currently unreachable. |
| `SendTraitorDeathState` | Network helper | Sends appearance-name/alive state. |
| `ShouldStartRoleRound` | Data callback | Dot-defined; hard-returns false. |
| `ShouldRoundEnd` | Lifecycle | Role-selection transition or winner check. |
| `RoundStart` | Lifecycle | Resets reinforcement state and calls spawning workflow. |
| `GiveEquipment` | Empty override | No behavior. |
| `CanSpawn` | Empty override | No behavior. |
| `EndRound` | Lifecycle | Rewards, cleanup and end packets. |
| `CanLaunch` | Data callback | Unconditional. |
| `SpawnPlayers` | Internal workflow | Dot-defined and argument-shifted; large player/loadout/network operation. |

**Direct hooks:** traitor death/spawn tracking, duplicate radio pickup, project `Player_Death` rewards, stale `RoundStateChange`, and assistant-list refresh hooks.

### Client — `modes/homicide/cl_homicide.lua`, `cl_hud.lua`

| Function | Class | Effective contract / risk |
|---|---|---|
| `RenderScreenspaceEffects` | Engine hook | Dynamic role-intro fade. |
| `HUDPaint` | Engine hook | Role/subrole/profession/objective presentation. |
| `RoundStart` | Empty lifecycle override | Does not currently clear prior end menu. |

`cl_hud.lua` uses direct `HUDPaint` and `PlayerButtonDown` hooks rather than top-level mode functions.

## `fear` (`base = hmcd`, `CanLaunch=false`)

### Shared — `modes/homicide_fear/core/sh_fear.lua`

`CreateTimer`, `AddEvent`, `StartEvent`, `DoEventThink`, and `StopEvent` are internal event/timer services but become hook names. `ShouldCollide` is an intended engine hook. The registered event objects have their own methods and are not mode-hook entries.

### Server — `core/sv_fear.lua`

| Class | Functions |
|---|---|
| Lifecycle/data overrides | `AfterBaseInheritance`, `CanLaunch`, `SubModes`, `Intermission`, `ShouldRoundEnd`, `EndRound`, `RoundThink`, `PlayerSilentDeath`, `PlayerDeath`, `Ragdoll_Create`, `HG_PlayerCanHearPlayersVoice`, `HG_PlayerCanSeePlayersChat` |
| Internal helpers accidentally dispatched | `IsDoor`, `RandomStuff`, `SkipVictim`, `CheckInAGroup`, `CheckInDarkness`, `SelectTheBestVictim`, `ReturnToRealmOfLiving`, `Disappear`, `PropKill`, `ResetNetworkVars` |

### Client — `core/cl_fear.lua`

`PreDrawPlayer2`, `RenderScreenspaceEffects`, `Player_Death`, `RoundStart`, `EndRound`, and `EntityEmitSound` are intentional render/project/lifecycle callbacks. Client `CheckInDarkness` is a data helper published as a hook and has a different contract than the server method of the same name.

**Inactive-mode risk:** direct hooks and network receivers load even though normal launch is disabled; every direct registration requires explicit selected-mode gating.

## `hl2dm`

### Server — `modes/hl2dm/sv_hl2dm.lua`

| Class | Functions |
|---|---|
| Lifecycle/data | `Intermission`, `ShouldRoundEnd`, `RoundStart`, `GiveEquipment`, `EndRound`, `CanLaunch`, `GetTeamSpawn` |
| Engine/project callbacks | `PlayerDeath` |
| Internal/data helpers accidentally dispatched | `ClearPlayerRoles`, `CheckAlivePlayers` |
| Empty overrides | `GetPlySpawn`, `RoundThink`, `CanSpawn` |
| Shifted dot function | `GuiltCheck` |

Client publishes `RenderScreenspaceEffects`, `HUDPaint`, and `RoundStart`. Airstrike UI/reset behavior uses direct `radialOptions` and `PostCleanupMap` hooks; the request is handled by a direct network receiver.

## `coop`

### Server — `modes/coop/sv_coop.lua`

| Class | Functions |
|---|---|
| Lifecycle/data | `Intermission`, `ShouldRoundEnd`, `RoundStart`, `GetPlySpawn`, `GetTeamSpawn`, `GiveEquipment`, `EndRound`, `CanLaunch` |
| Internal/data helpers accidentally dispatched | `GetLootTable`, `GiveDefaultEquipment` |
| Empty overrides | `CheckAlivePlayers`, `ZB_OnEntCreated`, `RoundThink`, `CanSpawn` |
| Shifted dot function | `GuiltCheck` |

Client publishes `RenderScreenspaceEffects`, `HUDPaint`, and `RoundStart`.

**Direct hooks:** friendly-fire `EntityTakeDamage`, possession `PlayerButtonDown`, mismatched `ZB_RoundStart`, `PostCleanupMap`, and Alyx weapon replacement `OnEntityCreated`. Possession validators/converters are local functions and therefore not hook-dispatched.

## `defense`

### Core server — `modes/defense/sv_defense.lua`

| Class | Functions |
|---|---|
| Lifecycle/data | `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `RoundThink`, `EndRound`, `PlayerDeath` |
| Wave workflow helpers accidentally dispatched | `IsBossWave`, `GetCurrentWaveDefinition`, `IsWaveActive`, `StartWave`, `EndWave`, `StartVoting`, `EndVoting`, `StartPrepPhase` |
| Spawn helpers accidentally dispatched | `GetGroundedPlayerSpawn`, `GetUsualPlayerSpawnPoints`, `GetDefenseAnchorPoints` |
| Timer services accidentally dispatched | `CreateTimer`, `RemoveTimer`, `ClearAllTimers` |
| Shifted dot function | `GuiltCheck` |

### Wave extension — `sv_defense_waves.lua`

`IsSpawnVisibleToAnyPlayer`, `FindValidSpawnPoint`, `IsValidNavMeshSpawn`, `FindNavMeshSpawnPoint`, and `AssignNPCTarget` are internal services exposed as hooks. `StartNewWave` and `SpawnWave` are workflow helpers exposed as hooks. `OnNPCKilled` is an intended engine callback.

### Role extension — `sv_defense_roles.lua`

`ClearPlayerRoles`, `AddCommanderPoints`, `OnWaveComplete`, and `AssignPlayerRoles` are internal workflow/economy helpers exposed as hooks. `GetPlySpawn` and `GiveEquipment` are framework callbacks.

### Support extension — `sv_defense_support.lua`

Support placement, airdrop, reinforcement, and item lookup functions are local and not mode-dispatched. Their network receivers call the published timer/spawn services directly.

### Client — `cl_defense.lua`

`RenderScreenspaceEffects`, `HUDPaint`, and `RoundStart` are top-level mode callbacks. Outline, radial-options, voting, commander UI, music, and panel logic use direct hooks/receivers or local functions.

## `criresp`

### Server — `modes/criresp/sv_criresp.lua`

| Class | Functions |
|---|---|
| Lifecycle/data | `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `GetTeamSpawn`, `EndRound`, `PlayerDeath` |
| Internal helper accidentally dispatched | `AssignTeams`, `CheckAlivePlayers` |
| Empty overrides | `GiveEquipment`, `RoundThink`, `CanSpawn` |
| Shifted dot function | `GuiltCheck` |

Client publishes `RenderScreenspaceEffects` and `HUDPaint`; input locks are direct hooks.

## `pathowogen`

### Shared/server — `modes/pathowogen/sh_uwu.lua`, `sv_uwu.lua`

| Class | Functions |
|---|---|
| Lifecycle/data/project callbacks | `CanLaunch`, `PlayerInitialSpawn`, `CanSpawn`, `EndRound`, `Intermission`, `RoundStart`, `ShouldRoundEnd`, `CanPlayerSuicide`, `CanPlayerEnterVehicle`, `PlayerDeath`, `ZB_LootMultiplier`, `HG_OnAssimilation`, `Think`, `ZB_JoinSpectators` |
| Internal services accidentally dispatched | `CreateTimer`, `FigureOutConsequences`, `SpawnInterests`, `GetRandomSpawn`, `SetupFur`, `SetupTraitor`, `SetupSurvivor`, `BroadcastCommander`, `BroadcastContractor`, `SpawnDeltaSquad`, `SpawnSquadHelicopter`, `InitiateCQExtraction`, `InitiateTraitorExtraction`, `SpawnGlideHelicopter` |
| Empty override | `GiveEquipment` |
| Shifted dot function | `GuiltCheck` |

Client publishes `Think`, `RoundStart`, `PostDrawTranslucentRenderables`, and `HUDPaint`. Nested Derma/dialogue methods are not mode callbacks.

**Inactive-mode risk:** `CanLaunch=false` does not prevent registration of the complete callback set.

## `riot`

Server publishes shifted `GuiltCheck`; lifecycle/data functions `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `GiveEquipment`, `GetTeamSpawn`, `EndRound`, and `PlayerDeath`; internal `CheckAlivePlayers`; and empty `CanSpawn`. Client publishes its intro render/HUD and round-state callbacks. Spectator-inclusive assignment is implemented inside lifecycle code, not a separate mode helper.

## `gwars`

Server publishes shifted `GuiltCheck`; lifecycle/data functions `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `GiveEquipment`, `RoundThink`, `GetTeamSpawn`, `EndRound`, and `PlayerDeath`; internal `CheckAlivePlayers` and `BoringRoundFunction`; and empty `GetPlySpawn`/`CanSpawn`. Client publishes `RenderScreenspaceEffects` and `HUDPaint`.

## `superfighters`

Shared publishes `PlayerCanLegAttack`; opening attack suppression also uses a direct `StartCommand` hook. Server publishes `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `RoundThink`, `EndRound`, `PlayerDeath`, `CanSpawn`, internal `CheckAlivePlayers`, and empty `GiveWeapons`/`GiveEquipment`. Client publishes `PostDrawTranslucentRenderables`, `RenderScreenspaceEffects`, and `HUDPaint`.

## `scugarena`

Shared attack suppression is a direct `StartCommand` hook. Server publishes `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `EndRound`, internal `CheckAlivePlayers`, and empty `GiveWeapons`/`GiveEquipment`. Client publishes `RenderScreenspaceEffects` and `HUDPaint`.

## `event`

### Server — `modes/eventhandler/sv_event.lua`

| Class | Functions |
|---|---|
| Lifecycle/data | `CanLaunch`, `Intermission`, `ShouldRoundEnd`, `RoundStart`, `RoundThink`, `EndRound`, `PlayerDeath`, `CanSpawn` |
| Internal/persistence/network helpers accidentally dispatched | `CheckAlivePlayers`, `GetLootTable`, `SaveLootTable`, `LoadLootTable` |
| Empty overrides | `GiveWeapons`, `GiveEquipment` |

Client publishes `RenderScreenspaceEffects`, `HUDPaint`, and `RoundStart`. Loot editor/panel functions are local/global UI functions, not mode-dispatched.

## Cross-mode collision and regression matrix

| Pattern | Affected examples | Risk |
|---|---|---|
| Dot-defined function without explicit `self` | TDM/CStrike `GuiltCheck`, DM `GetZoneRadius`, Homicide `GetPlayerTraceToOther`, `ShouldStartRoleRound`, `SpawnPlayers`, Pathowogen `GuiltCheck` | Dispatcher shifts arguments and can silently change authorization/target selection. |
| Generic helper name becomes hook | `CreateTimer`, `CheckAlivePlayers`, `GetActivePlayers`, `GetLootTable`, `SaveLootTable`, `AssignTeams`, `SpawnWave` | Unrelated `hook.Run` calls can execute internal workflows on the active mode. |
| Empty callback | `CanSpawn`, `RoundThink`, `GetPlySpawn`, `GiveEquipment`, `PlayerDeath` | Can suppress inheritance or imply a supported contract that does nothing. |
| Child publishes inherited surface | CStrike from TDM; Fear from Homicide | Child behavior depends on registration/inheritance order and carries base defects. |
| Same callback differs by realm | `RoundStart`, `CheckInDarkness`, `Think` | Server/client semantics cannot be inferred from function name alone. |
| Direct hook beside mode-dispatched callback | DM zone Think, Defense radial/outline/support hooks, CO-OP possession hooks | Direct hook remains loaded regardless of selection unless it gates itself. |
| Disabled mode still loads | Fear, Pathowogen, Event/Slug Arena by zero chance | Network receivers/direct hooks/global mutations can remain active. |
| Broad framework callback names used as helpers | Defense `StartWave`, `EndWave`, `OnWaveComplete`; Homicide `StartPlayersRoleSelection` | Future systems can accidentally emit the same hook name. |

## Required implementation boundary

The loader must eventually register only an explicit callback allowlist or explicit per-mode callback declaration. Until that implementation package is authorized, regression work must:

1. preserve existing function lookup for direct `MODE:` callers;
2. record which callbacks are actually emitted by core/project code;
3. add runtime instrumentation for every dispatched function name and selected mode;
4. verify inherited registration order;
5. determine whether any external addon intentionally emits the accidental helper names;
6. add tests for dot/colon argument shape and multi-return propagation;
7. avoid renaming/removing helper functions until direct callers and external integrations are mapped.

## Remaining evidence gaps

- Runtime startup instrumentation is required to prove effective mode registration order and duplicate last-writer behavior.
- External addons may emit project hook names not discoverable in this repository.
- Some very large client files contain local UI functions and direct hooks not relevant to the top-level mode dispatcher; these remain tracked in the packet/public-surface inventories rather than this matrix.
- The packet matrix is the authority for network receiver activation independent of selected mode.
