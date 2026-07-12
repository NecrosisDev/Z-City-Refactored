# Bot and NPC System Architecture

**System IDs:** `SYS-BOTDRIVER`, `SYS-BOTFILL`, `SYS-VJ-COMPAT`, `SYS-ZOMBIE-EXTENSIONS`  
**Evidence:** uploaded local archive SHA-256 `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652`  
**Status:** `Verified (local archive) / runtime unverified / player bots shipping-disabled`

## Scope

This document covers the local archive's player-bot controller, population manager, VJ Base compatibility, stock-NPC organism/loot extensions, and zombie-specific extensions. It does not claim these files exist on repository `main`.

## Operational state

Player bots are disabled by `lua/autorun/000_trauma_disable_bots.lua`. The implementation still loads, registers behaviors, commands, convars and optional mode profiles, but execution paths check `hg.BotsDisabled` and bot entities are removed. VJ/stock NPC integrations are not disabled by that switch.

This creates three distinct states that tests and future settings must not conflate:

1. bot code absent;
2. bot code loaded but globally disabled — current archive shipping state;
3. bot code enabled for development or a future release.

## Player-bot ownership model

### Brain registry and lifecycle

`lua/homigrad/botdriver/sv_brain.lua` owns `hg.botdriver.brains[bot]` and an active-bot registry. A brain table persists across lives while per-life fields are cleared by `ResetBrain`.

Lifecycle hooks:

- `PlayerSpawn`: add bot, create/reset brain, schedule decision;
- `PlayerDeath`: reset brain and unschedule decisions;
- `ZB_PreRoundStart`: increment round epoch to invalidate delayed callbacks;
- `PlayerDisconnected`: unschedule, remove registry entry and delete brain;
- Lua refresh: rebuild connected bot state immediately and through a zero-delay retry.

`lifeEpoch` and `roundEpoch` reduce stale delayed-callback risk, but no single bot-generation object owns every timer, claim, path, packet and mode resource.

### Decision scheduling

The expensive decision pass is decoupled from command application.

- A due-time binary heap schedules alive bots.
- Default cadence is approximately 0.15 seconds plus an EntIndex-based stagger.
- `hg_bot_decide_budget` caps full decisions per server tick.
- `hg_bot_decision_scheduler` can revert to a compatibility scan over the active-bot registry.
- `FailSafe` clears movement, attack and gaze intent after an exception and reschedules later.
- Profiling records scheduler, decision, command-control and pathfinding time.

This avoids a full decision for every bot every tick, but deferred work can increase reaction latency under load. Runtime population budgets remain unverified.

## Behavior arbiter

`sv_arbiter.lua` compiles registered behaviors into ordered bands:

1. `REFLEX`
2. `SURVIVAL`
3. `MODE`
4. `ACQUIRE`
5. `COMBAT`
6. `SUPPORT`
7. `IDLE`

Verified default behaviors include deadman handling, survival preemption, downed/dodge fallback, weapon acquisition and looting, grenade/engagement combat, medical/rescue support, objective travel, investigation and roaming. Homicide role behaviors are opt-in mode behaviors.

`RegisterModeProfile` stores declarative profiles in `hg.botdriver.modeBrains`; profiles may add/suppress behaviors and supply objective generators. The arbiter stops on the first behavior that claims ownership and records the owner/band on the brain. Preemption callbacks exist for involuntary ownership loss.

Risks:

- behavior definitions are mutable global tables;
- registration replacement is allowed and only logged;
- profile aliases can point multiple mode IDs at one table;
- mode/profile selection depends on current round globals;
- ownership covers decision output, not every asynchronous resource started by a behavior.

## Command-rate controller

`sv_control.lua` applies brain intent through `StartCommand` every server tick.

Responsibilities include:

- smooth view interpolation based on skill;
- optional physical-muzzle correction derived from worldmodel pose;
- command-rate line-of-sight fire suppression;
- world-space path movement reprojected into view-relative command axes;
- eased forward/side movement;
- sprint key synthesis;
- stationary action locks;
- command/buttons/view output and control profiling.

The command-rate LOS gate can clear the live target and firing state between decision updates. This is a useful safety boundary, but it also means target ownership is mutated from both the decision layer and command layer.

The muzzle-steering path is especially sensitive because it consumes `wep.desiredAng`, `LocalMuzzleAng`, obstruction fields, posture and current eye angles. A bad or stale worldmodel transform can bias view increasingly as distance closes. This path requires dedicated aim/muzzle instrumentation before bots are enabled.

## Perception, targeting and combat

The brain includes:

- focused and peripheral vision;
- short visual memory and last-seen investigation;
- gunshot and footstep hearing with occlusion/noise handling;
- near-miss awareness without granting attacker identity;
- damage awareness;
- target-switch hysteresis;
- ballistic lead proxy and bounded aim error;
- melee/ranged weapon classification;
- ammo, reload, sidearm and retreat decisions;
- downed-target finishing with configurable recognition chance;
- grenade, rescue, medical, loot and mode-role behaviors.

Bots use the same player, weapon, organism, movement and fake-ragdoll systems as humans. This improves behavioral parity but tightly couples the driver to mutable weapon flags, inventory schemas, organism fields, round globals and fake-body hooks.

## Navigation and traversal

`sv_nav.lua` runs synchronous A* over the engine navmesh.

Verified characteristics:

- cached nav-area centers, adjacency and area list;
- binary-heap open set and pooled workspaces;
- expansion cap and per-tick path-search budget;
- failed route cache;
- blocked area/edge penalties;
- persisted per-map learning in `DATA/zcity_nav_learning/<map>.json`;
- navmesh fingerprint and score decay/corroboration;
- random roaming that prefers distant, non-terminal areas.

Traversal modules add stuck diagnosis, door discipline, vaulting/edge probes, gait choice, separation and destination deconfliction.

Risks:

- pathfinding remains synchronous;
- persisted path is still under the legacy `zcity_nav_learning` namespace;
- comments describe “machine learning,” but the executable model is a heuristic penalty map, not a learned policy;
- nav generation/availability is an external prerequisite;
- map cleanup, nav rebuild and invalid area identity require runtime tests.

## Botfill population manager

`gamemodes/trauma/gamemode/libraries/sv_botfill.lua` manages population only between rounds.

- It tops up to a configurable floor and removes only bots it created.
- It uses `player.CreateNextBot` directly.
- Per-mode floors and optional `MODE.BotFill` overrides are supported.
- Adds/removes at most one bot per convergence step.
- External/admin-created bots count toward the floor but are not removed.
- When `hg.BotsDisabled` is set, the file replaces `Tick` with a no-op and returns before creating convars/timers/hooks.

Population ownership is therefore cleanly separated from behavior ownership, but current shipping code prevents the manager from operating.

## Bot configuration and diagnostics

### Survival configuration

The bot survival editor uses four network channels and writes `DATA/trauma/bot_survival_config.json`, with legacy read fallback from `DATA/zcity/`.

The server requires superadmin, applies a 0.25-second write cooldown, bounds compressed payloads to 32 KiB, authenticates before decompression, sanitizes the schema, and broadcasts the resulting configuration.

### Debug and profiling

Verified surfaces include:

- `trauma_debug_bots`
- `trauma_botprof`
- `trauma_bot_scheduler_status`
- `trauma_debug_weaponscore`
- client debug overlay commands and `Trauma_BotDebug_*` packets
- survival configuration UI and packets
- performance metrics under `server.bot.*`

The debug overlay captures final movement commands after `StartCommand`, enabling comparison of intended and effective aim/buttons/movement. Access is admin/superadmin gated, but packet size, PVS exposure and high-population cost require runtime measurement.

## VJ Base compatibility

`lua/homigrad/vjbase/` is gated by convars and `ent.IsVJBaseSNPC` flags so it is mostly inert without VJ Base.

Verified integrations:

- harm profiles for human, creature and zombie classes;
- VJ melee `DMG_CRUSH` remapping to `DMG_CLUB` for organism compatibility;
- optional lightweight living organism on humanoid VJ NPCs;
- organism transfer or creation on humanoid VJ corpses;
- bleeding over time;
- temporary ragdoll knockdown from qualifying damage;
- downed/playing-dead relationship handling and configurable finishing chance;
- faction/perception integration;
- path and spawn compatibility;
- vFire damage-data adjustment.

Ownership remains split: VJ retains AI, flinch and death behavior while Homigrad may own organism wounds, bleedout, corpse state, temporary ragdoll and relationship changes. That boundary needs failure and cleanup tests.

## Stock NPC and zombie extensions

The archive also contains general NPC and zombie behavior outside the VJ layer:

- stock NPC organism/corpse/loot setup;
- player/NPC relationship adaptation;
- forced server ragdolls and corpse inventory/name metadata;
- optional NPC health/playback modifications;
- zombie limb-loss behavior;
- headcrab release/latch behavior with population convars;
- combatant-aware helpers for future NPC-inclusive win conditions.

These paths overlap engine NPC damage, organism damage, corpse creation, inventory, fake-ragdoll and mode cleanup. Their exact precedence with VJ NPCs and other NPC bases is not yet runtime verified.

## Critical defects and integration risks

1. Player bots are fully implemented but globally disabled, making static completeness a poor proxy for release readiness.
2. Bot aim is authored through eye angles while shots follow physical weapon pose; muzzle correction can become a feedback source.
3. Decision, command, fake-ragdoll, movement and weapon systems all mutate shared player/brain/weapon state at different cadences.
4. Behavior ownership does not automatically own delayed timers, claims or external entity state.
5. Navigation persistence still uses a legacy Z-City data path.
6. Bot/NPC relations depend on mode teams, classes, organism downed state and external NPC disposition APIs.
7. VJ living organism, VJ death handling and Homigrad kill paths can compete if configuration or entity classification is wrong.
8. Multiple `Think`, damage, spawn and entity-created hooks scale with bots/NPCs and need a combined budget.
9. Debug/config surfaces expand network and permission attack surface.
10. No dedicated runtime evidence exists for enabled bots in the uploaded archive.

## Required validation

- run a bot-disabled shipping smoke test and confirm no player bots survive any join path;
- run a separate enabled development build with 1, 4, 8, 16 and 32 bots;
- capture desired eye aim, physical muzzle transform, corrected command view, shot trace and target distance;
- test close-range approach to detect vertical aim feedback;
- profile decision queue depth, deferred decisions, path searches, traces and command cost;
- exercise every behavior band and preemption path;
- test death/respawn/round transitions for stale targets, claims, paths and callbacks;
- test navmesh absent, partial, regenerated and cleanup states;
- test botfill joins/leaves around round boundaries and full servers;
- fuzz survival/debug packets and verify permission/rate/size limits;
- test VJ humanoid/nonhumanoid/tank classes with compatibility convars on/off;
- verify organism transfer, knockdown recovery, bleedout, corpse creation and relationship restoration;
- test stock and VJ zombies for duplicate headcrab/limb/corpse processing.

## Planned architecture boundary

A stable integration should separate:

- `BotPopulationService` — creates/removes managed bots;
- `BotRuntime` — per-bot generation, brain and owned resources;
- `BehaviorRegistry` and immutable mode profiles;
- `PerceptionService` — observations rather than live target leakage;
- `NavigationService` — budgeted requests and versioned map learning;
- `CommandController` — one output owner with aim/muzzle diagnostics;
- `NPCAdapter` — explicit stock/VJ/ZBase capability adapters;
- `NPCPhysiologyAdapter` — organism and corpse ownership contracts;
- `BotDebugService` — development-only, bounded and permissioned.

Compatibility adapters should preserve current hooks/convars during migration, but the shipping bot-disabled policy must remain explicit until enabled-bot acceptance tests pass.
