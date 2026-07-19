# Public Surfaces Inventory

**Work package:** `WP-RESEARCH-001`  
**Scope:** bootstrap, mode/round framework, cataloged modes, organism, fake-ragdoll, movement, player classes, weapon-facing character-runtime interfaces, and their integration  
**Status:** `partial / executable-source verified`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Reviewed:** 2026-07-12

Exact schemas live in [`PACKET_MATRIX.md`](PACKET_MATRIX.md); mode dispatch in [`MODE_FUNCTION_MATRIX.md`](MODE_FUNCTION_MATRIX.md); detailed ownership in the linked architecture documents.

## Core globals and registries

| Surface | Owner | Realm | Contract/risk |
|---|---|---|---|
| `hg` / `hg.loaded` | global loader | server/client | global addon namespace and bootstrap state |
| `zb` | gamemode libraries | server/client | mode/round/points/teams/admin state |
| `zb.modes`, `zb.modesHooks`, temporary `MODE` | mode loader | server/client | mode registry and automatic function-to-hook dispatch |
| `CurrentRound`, `NextRound` | round framework | realm-local/server | broad mode-state consumers |
| `COMMANDS` | unresolved framework | primarily server | owner/dispatcher/collision behavior untraced |
| `zb.RoundList`, `zb.QueuedModes` | active/legacy queue systems | server | distinct queue models |
| `hg.organism`, `.list`, `.module`, `.input_list` | organism | server/client helpers | physiology, ownership, damage and replication registries |
| entity `.organism`, `.new_organism` | organism lifecycle | server/client | shared authoritative table and interpolated copies |
| `hg.ragdollFake`, `hg.queue_ragdolls`, `hg.ragdolls` | fake subsystem | mixed | active body, forced PVS and render registries |
| `player.classList` | player-class registry | shared | case-sensitive shared class-definition tables |
| player `PlayerClassName` | class runtime | server/client mirror | explicit class ID; fallback to default |
| mode/client globals | many systems | mixed | timing/menu/audio/camera/result/extraction state can collide across hotload |

## Core emitted hooks

| Hook | Emitter | Contract/risk |
|---|---|---|
| `HomigradRun` | global loader | post-main-load |
| `ZB_PreRoundStart`, `ZB_StartRound`, `ZB_EndRound`, `TTTPrepareRound` | round framework | lifecycle; stale alternative hook names exist |
| `RoundInfoCalled` | client round receiver | mode ID before assignment |
| dynamic mode function names | mode loader | `func(modeTable, ...)`; dot-defined functions shift arguments |
| `Org Add`, `Org Clear`, `Org Think`, `Org Transfer`, `Org Think Call` | organism | attachment/reset/10 Hz/ownership/immediate update |
| `HG_OnOtrub`, `HG_OnWakeOtrub` | organism | unconscious/wake transitions |
| `PreHomigradDamage`, `HomigradDamage`, wound/amputation hooks | damage | broad custom damage extension surface |
| `Ragdoll_Create`, `Fake`, `Fake Up`, `Should Fake Up`, `CanControlFake` | fake subsystem | body lifecycle and control gates |
| `RagdollEntityCreated`, `RagdollRemove`, `Ragdoll Collide`, `RagdollDeath` | fake/damage | server/client body ownership and injury |
| `PlayerClass` | class transition | class ID/state change |
| class events through `PlayerClassEvent` | class runtime | `On`, `Off`, `Think`, `Damage`, `PlayerDeath`, `Guilt`, `Player Spawn`, equipment and class-specific methods |
| staged `HG_MovementCalc*` | movement | movement modifier pipeline; exact full consumer list incomplete |

## High-impact registrations and cadence

| Hook/cadence | Owner | Risk |
|---|---|---|
| server Think once/sec | round framework | lifecycle latency/order |
| `Think/homigrad-organism` ~10 Hz | organism | all organisms; module/hook order and population cost |
| server `Think/Fake` every frame | fake control | all players, multiple physics bodies, traces/constraints/weapons |
| shared `SetupMove/homigrad-inertia` every command | movement | server/client prediction and mutable modifier state |
| `FinishMove/!homigrad-organism` | stamina | movement feedback into physiology |
| `EntityTakeDamage/homigrad-damage` | organism damage | monolithic geometry/armor/wound/effect/replication path |
| `Org Think/PlayerClass` | class system | shared class-table `nextThink` starves same-class players |
| multiple `PlayerInitialSpawn`, `PlayerSpawn`, `Player Spawn` | round/organism/class/fake | delayed handlers and conflicting spawn override semantics |
| dynamic class NPC hooks | concrete classes | EntIndex-keyed cleanup and relationship scan risk |
| permanent class sound/HUD/gesture hooks | concrete classes | remain installed and branch by class ID |

## Round/mode/admin surfaces

- Active and legacy queue protocols and all mode packet schemas are in `PACKET_MATRIX.md`.
- Confirmed mismatches: base TDM start, CStrike winner bool, HL2DM end, Defense new-wave and Homicide roster count.
- High-risk mode inputs: admin tables, TDM purchases, bomb code, Fear light vector, Crisis customization, Defense commander/admin and Event persistent loot.
- Core spawn uses global `OverrideSpawn` and mode-table `CurrentRound().OverrideSpawn` as separate contracts.
- `zb:EndRound()` is verified; `zb.EndMatch` remains unresolved.

## Organism APIs and transport

| Surface | Contract/risk |
|---|---|
| `hg.organism.Add/Clear`, entity Add/Del/HasOrganism | attach/reset ownership |
| `Trace`, `BlastTrace`, `ShootMatrix`, `GetHitBoxOrgans` | custom ValveBiped OBB damage geometry |
| `input_list.*`, wound/amputation/oxygen/adrenaline helpers | physiology mutation |
| `hg.send_organism`, `hg.send_bareinfo` | owner/PVS/partial Lua-table snapshots |
| `organism_send` | unversioned table + booleans; owner validity order and cost/privacy issues |
| `organism_sendply`, `VirusStageUpdate`, `pulse` | dormant or one-sided protocols |
| blood-effect channels and wound NetVars | overlapping effect/state transport |
| dislocation/breath commands | parsing/range and self-state trust boundaries |

Organism schema groups and extension fields are documented in `ORGANISM_SYSTEM.md` and `TYPE_CATALOG.md`.

## Fake-ragdoll APIs, state, and transport

| Surface | Contract/risk |
|---|---|
| `hg.Ragdoll_Create`, `hg.Fake`, `hg.FakeUp` | custom body enter/get-up/death lifecycle; no transaction/rollback |
| `hg.GetCurrentCharacter`, `hg.RagdollOwner`, `hg.GetUpPos` | identity/position helpers |
| `hg.SavePoses`, `hg.ApplyPoses`, `hg.ShadowControl` | body pose and per-frame physics control |
| overridden `PLAYER:GetRagdollEntity`, `CreateRagdoll` | global compatibility change |
| player fields/NWEntities `FakeRagdoll`, old body, `RagdollDeath` | distributed ownership without generation |
| `Player Ragdoll` | player + body/null packet; client relies on undefined/custom `net.ReadEntity2` |
| `Override Spawn` plus global `OverrideSpawn` | respawn-based get-up suppression; not transactional |
| fake/control/render commands/convars | voluntary/admin fake, ragdoll combat, stamina and camera modes |
| vehicle/NPC bullseye/constraint maps | external integrations embedded in core lifecycle |

## Movement surfaces

| Surface | Contract/risk |
|---|---|
| `SetupMove/homigrad-inertia` | shared server/client movement authority; active even when inertia disabled |
| staged `HG_MovementCalc*` | mode/class/weapon extension stages; full order/consumers incomplete |
| walking/sprinting/backward helpers | shared predicates used by movement/fake/footsteps/classes/weapons |
| movement player fields | current/target speed, timing/history, jump/crouch/carry and prediction state; no schema |
| `hg_inertia` and movement convars | replicated/archived behavior but do not disable whole system |
| `CalcMainActivity`, `UpdateAnimation` | animation/pose from mutable movement/model/weapon state |
| `PlayerFootstep`, `PlayerStepSoundTime`, `HG_PlayerFootstep` | permanent class/movement sound pipeline |
| global Sandbox `AntiDuckSpam` mutation | spawn-time compatibility side effect |

Movement consumes organism state, class fields/NWInts, active weapon interfaces, armor/inventory/carried mass, mode hooks and fake ownership. Realm-local `SysTime` and replayed player fields make prediction a public behavior boundary.

## Weapon-facing character-runtime surfaces

The first executable-source weapon trace is the server `Think/Fake` consumer in `lua/homigrad/fake/sv_control.lua` blob `22c87ad4148716ff1173c104e7df943043b09ce5`.

| Surface | Contract/risk |
|---|---|
| `ishgweapon(wep)` | implicit global firearm classifier; definition and accepted bases unresolved |
| `wep:IsPistolHoldType()` | hold-profile query used for body orientation; method assumed for classified weapons |
| `wep.IsResting` / `wep:IsResting()` | resting/aim posture query with inconsistent existence guarding |
| `wep.RagdollFunc` | weapon-owned callback inside the monolithic per-frame fake controller; signature, publishers, cleanup and mutation limits unresolved |
| `wep.ismelee`, `wep.ismelee2` | ad-hoc capability flags sharing attack/use input with generic fake control |
| active weapon across `hg.Fake` / `hg.FakeUp` | selected class is preserved around respawn, but complete instance/clip/ammo/reload/attachment/cooldown state restoration is unproven |

The fake controller also owns limb gates, generic arm poses, hand constraints, organism pain/stamina feedback, and input precedence around weapon callbacks. The path is server authoritative, per frame, and has no verified command number/body generation or callback-result replication contract. Detailed findings are in `architecture/WEAPON_COMBAT_INTERFACES.md`.

## Player-class APIs, registry, and trust boundary

| Surface | Contract/risk |
|---|---|
| `player.classList`, `player.RegClass` | case-sensitive shared definitions; duplicate files extend/overwrite tables |
| `PLAYER:GetPlayerClass`, `SetPlayerClass`, `PlayerClassEvent`, `ResetPlayerClass` | class lookup/transition/event API |
| `PlayerClassName` field/NetVar | distributed identity |
| `playerclass` S -> C | class string + unversioned Lua table; client does not call old `Off` |
| `playerclass` C -> S | **critical:** server accepts arbitrary class/table from any valid client with no authorization/phase/rate/size/allowlist checks |
| class `nextThink` | incorrectly stored on shared definition; same-class players share one throttle |
| class Lua fields/NWInts | movement/combat/organism modifiers with overlapping reset ownership |
| concrete class global hooks | NPC relationships, sounds, HUD, gestures, footsteps and world behavior outside lifecycle ownership |
| class appearance/equipment/armor/inventory calls | overlap mode/round ownership and frequently lack rollback |

Verified IDs are mixed-case and include `default`, `Slugcat`, `Combine`, `Metrocop`, `Refugee`, `Rebel`, and lower-case role/creature classes. Case normalization is breaking without aliases.

## Character-runtime ownership surfaces

The current runtime has no single owner for class, body, organism, ordinary/fake controller, equipment or presentation. These are distributed across player/ragdoll fields, organism aliases, shared class tables, movement fields, NWVars, packets, modes and hooks.

Critical invariants to instrument:

- one authoritative body generation;
- one organism owner generation;
- one ordinary or fake movement controller;
- per-player class runtime, not shared definition state;
- converged server/client class/body IDs;
- no stale timer/hook/constraint mutation after transition;
- global spawn override false outside active get-up transaction.

## Defense and mode-specific service surfaces

Defense owns wave/vote/timer/spawn/role/economy/support/admin extensions, globally wraps `SpawnZBaseNPC`, and combines per-NPC timers/nav/world scans. Pathowogen/Fear remain hard-disabled or unavailable but load hooks/receivers/global state. Full mode details remain in grouped catalogs and packet/function matrices.

## Persistence and local-data surfaces

| Surface | Owner | Risk |
|---|---|---|
| mode chances/mapsizes JSON | registry/round | weak validation |
| Homicide PData | Homicide | integer-like counters |
| Event loot JSON | Event | persistent weakly validated client-authored data |
| CO-OP SQLite/persistence | CO-OP | optional/partial integration |
| client dream screenshots | organism client | periodic local captures; should be optional/documented |
| simfphys fuel convars | Pathowogen | global mutation without restore |

## Cross-system regression rules

1. Do not change packet/hook/API names before all writers/readers/callers are listed.
2. Treat class and body transitions as security/lifecycle transactions, not field assignments.
3. Record table shape, ownership, size and compatibility before replacing Lua-table transport.
4. Runtime-confirm hook/order/duplicate behavior before consolidation.
5. Validate every client table/string/vector/command for permission, phase, type, bounds, ID, distance and rate.
6. Centralize timers/hooks/constraints/audio/render/convar resources and prove cleanup.
7. Treat organism order, movement prediction and fake ownership as public behavior.
8. Do not migrate organism/fake/movement/class independently; use the character integration graph.
9. Do not formalize a weapon adapter until every current capability publisher and consumer is enumerated.

## Next trace

1. Enumerate `ishgweapon`, every `RagdollFunc`, hold/resting/melee capability publisher, and weapon switch/drop/pickup cleanup.
2. Trace physical bullets, ammunition, reload/chamber state, projectiles, armor and explosives.
3. Close the still-unresolved `COMMANDS`, spawn override, point-system, `OverideSpawnPos`, and `zb.EndMatch` inventories only from exact fetched paths; do not overstate repository-wide absence.
4. Trace inventory/equipment/appearance ownership across round/class/fake transitions.
5. Update the combined character-runtime graph with those boundaries before implementation planning.
