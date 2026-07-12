# Public Surfaces Inventory

**Work package:** `WP-RESEARCH-001`  
**Scope:** bootstrap, mode/round framework, admin mode UI, all cataloged modes, and organism ownership/damage/replication  
**Status:** `partial / executable-source verified`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Reviewed:** 2026-07-12

This inventory tracks refactor-sensitive globals, hooks, network channels, convars, commands, persistence and trust boundaries. Exact packet schemas are canonical in [`PACKET_MATRIX.md`](PACKET_MATRIX.md); mode function dispatch is canonical in [`MODE_FUNCTION_MATRIX.md`](MODE_FUNCTION_MATRIX.md); organism architecture is canonical in [`../architecture/ORGANISM_SYSTEM.md`](../architecture/ORGANISM_SYSTEM.md).

## Core globals and registries

| Surface | Owner | Realm | Contract/risk |
|---|---|---|---|
| `hg` / `hg.loaded` | global loader | server/client | global addon namespace and bootstrap state |
| `zb` | gamemode/bootstrap libraries | server/client | mode registry, round state, points, teams, admin UI and subsystem globals |
| `zb.modes` | mode loader | server/client | mode name -> table; realm registries must agree |
| `zb.modesHooks` | mode loader | server/client | mode -> function key -> callback |
| `MODE` | loader/mode files | temporary global | every function-valued member becomes a hook candidate |
| `CurrentRound()` / `NextRound()` | round system/client | realm-local | broad mode-state consumer surface |
| `COMMANDS` | unresolved command framework | primarily server | owner/dispatcher/collision behavior still untraced; round system publishes four entries |
| `zb.RoundList` | current round queue | server/admin clients | active queue model synchronized through `ZB_*` packets |
| `zb.QueuedModes` | legacy queue generation | server | separate legacy queue model synchronized through writer-only `SendGameQueue` |
| `hg.organism` | organism Tier 0/Tier 1 | primarily server, client helpers | registry, module/input tables, geometry, damage and replication APIs |
| `hg.organism.list` | Tier 0 server | server | entity-keyed set iterated at 10 Hz; player/NPC/ragdoll ownership surface |
| `hg.organism.module` | Tier 1 core/modules | server | ordered initializer/tick pairs; module ordering changes gameplay |
| `hg.organism.input_list` | Tier 1 damage inputs | server | organ/bone/limb damage handler registry |
| entity `.organism` / `.new_organism` | organism lifecycle | server/client | authoritative server table; interpolated client copies; can be shared by player/ragdolls |
| mode/client globals | individual modes | mixed | repeated timing, menu, winner, zone, extraction and audio globals collide across hotload |

## Core hook contract

### Emitted

| Hook | Emitter | Contract |
|---|---|---|
| `HomigradRun` | global loader | no args after main addon load |
| `ZB_PreRoundStart` | round lifecycle | state `3 -> 0` preparation |
| `TTTPrepareRound` | same path | compatibility preparation emission |
| `ZB_StartRound` | round start | after mode start and next-mode selection |
| `ZB_EndRound` | round end | after mode `EndRound` |
| `RoundInfoCalled` | client round receiver | mode name before local assignment |
| `ZB_TraitorWinOrNot` | Homicide | traitor entity + winner identifier |
| dynamic mode function names | mode loader | invokes `func(modeTable, ...)`; dot-defined methods shift arguments |
| `Org Add` | Tier 0 organism | entity, newly attached organism table |
| `Org Clear` | Tier 0 organism | entity, organism table; Tier 1 resets in place |
| `Org Think` | Tier 0 10 Hz loop | current owner, organism, time delta |
| `Org Transfer` | organism/fake ownership | old owner, new owner, organism |
| `Org Think Call` | damage/immediate update paths | owner, organism |
| `HG_OnOtrub` / `HG_OnWakeOtrub` | organism core | unconscious/wake player transition |
| `PreHomigradDamage` | organism damage | target, DamageInfo and provisional hit data; some trace locals are not yet initialized at call site |
| `PreHomigradDamageBulletBleedAdd` | damage pipeline | pre-wound extension point |
| `HomigradDamage` | damage/collision pipeline | normalized project damage result and organ-hit data |
| `OnAmputateLimb` | organism damage | organism, entity, limb identifier |
| `Ragdoll Collide` / `RagdollDeath` | ragdoll/damage systems | collision or death-ragdoll integration |
| `HG_OrganismChanged` | client snapshot merge | old client organism, incoming partial organism |

### High-impact registrations

| Hook | Identifier/owner | Risk |
|---|---|---|
| `Think/zb-think` | round system | core lifecycle once/sec |
| `Think/homigrad-organism` | Tier 0 organism | all organisms at 10 Hz; population cost |
| `EntityTakeDamage/homigrad-damage` | organism damage | monolithic organ/weapon/armor/wound/effect/replication path |
| `FinishMove/!homigrad-organism` | stamina | direct movement-state mutation |
| `PlayerInitialSpawn` | round/admin/organism | multiple delayed handlers; organism attachment callback lacks complete disconnect guard |
| `RoundStateChange` | Homicide reset | waits for stale state `2` |
| `ZB_RoundStart` | CO-OP reset | core emits `ZB_StartRound` |
| `RoundEnd` | Defense support cleanup | core emits `ZB_EndRound` |
| direct `Org Think` extensions | virus/random events/brain effects | execute after/beside core modules and can overwrite state |
| dynamic Fear hooks | Fear events/environment | cleanup and identifier reuse risks |
| `SetupOutlines` / `radialOptions` | Defense/client organism | direct integrations outside mode dispatch |

## Round/admin and mode transport highlights

- Core round, queue, mode and spectator channels are fully recorded in `PACKET_MATRIX.md`.
- Active `ZB_*` queue state and legacy `AdminSetGameQueue`/`SendGameQueue` use different server lists.
- Confirmed mismatches include base `tdm_start`, `CS_Roundover`, `hl2dm_roundend`, `npc_defense_newwave` and conditional `HMCD_RoundStart`.
- Highest-risk mode client inputs include admin queue tables, TDM purchases, bomb codes, Fear light vectors, Crisis customization, Defense commander/admin tables and Event persistent loot edits.

## Organism public APIs

| API | Owner | Contract/risk |
|---|---|---|
| `hg.organism.Add(ent)` | Tier 0 | creates/attaches table and emits `Org Add` |
| `hg.organism.Clear(ent)` | Tier 0/Tier 1 | emits reset in place; default schema duplicated across consumers |
| `Entity:AddOrganism`, `DelOrganism`, `HasOrganism` | Tier 0 | entity convenience methods |
| `hg.organism.Trace`, `BlastTrace`, `ShootMatrix`, `GetHitBoxOrgans` | hitbox system | ValveBiped/custom OBB penetration and blast geometry |
| `hg.organism.input_list.*` | modules_input | organ/bone/artery/limb mutation callbacks |
| `hg.organism.AmputateLimb` | damage | state, effects, NetVars and partial snapshot |
| wound APIs | damage/blood | wound arrays, timers, blood particles and NetVars |
| `hg.send_organism` / `hg.send_bareinfo` | Tier 1 core | full/PVS/partial Lua-table replication |
| `hg.organism.OxygenateBlood`, breath controls | lungs | O2 and holding-breath state |
| `Entity:AddNaturalAdrenaline` | stamina/pulse | physiology modifier |
| `hg.BreakNeck`, `hg.ExplodeHead` | damage | death/physics effects; bone/physics validity assumptions |
| fake-ragdoll ownership APIs | fake subsystem | organism table transfer/sharing; next trace |

## Organism packet and command surfaces

| Surface | Direction/input | Contract/risk |
|---|---|---|
| `organism_send` | S -> C | unversioned Lua table + four booleans; owner/PVS/partial/developer variants; client dereferences owner before validity check |
| `organism_sendply` | unresolved | server registration and commented client receiver; dormant until external audit |
| `VirusStageUpdate` | S -> infected C | int8 stage; no repository reader |
| `pulse` | S -> owner C | no payload; function has no located caller or receiver |
| blood effect channels | S -> C | entity/bone/matrix/vector effects; several writers/readers still one-sided |
| wound/arterial wound NetVars | S -> C | overlap snapshot authority using Lua-table values |
| `hg_fixdislocation` | console command | limb group + self/eye-trace target; missing numeric args can error; no explicit other-target distance cap |
| breath commands | console commands | self-targeted organism/alive/stamina/O2/cooldown checks |

## Organism state/extension surfaces

- Canonical groups: identity/lifecycle, consciousness/control, cardiovascular, respiratory, pain/drugs, stamina/adrenaline, bones/organs, limbs, wounds, metabolism/environment, replication timing.
- Modes and classes add noncanonical fields including `superfighter`, `recoilmul`, `assimilated`, `berserk`, `noradrenaline`, `HEV` and other flags.
- Virus state is stored separately on `player.Virus`, then writes into organism during `Org Think`.
- Player/fake/death ragdoll can alias one table while `owner` changes; delayed callbacks must not assume the original entity remains authoritative.
- Client maintains `organism` and `new_organism` copies and mirrors both to fake ragdoll.

## Defense function/public-service surface

- Core owns voting, preparation, wave state, fallback spawning and timers.
- Wave extension owns nav/visibility search, spawn queues, NPC targeting/death tracking and globally wraps `SpawnZBaseNPC`.
- Role extension owns role assignment, equipment, commander economy and wave rewards.
- Support extension owns support/menu/purchase receivers, airdrops and reinforcements; generic `RoundEnd` cleanup likely misses core emitter.
- Hooks extension owns last-NPC highlights and admin commands.
- Large waves combine per-NPC timers, nav enumeration, tracked scans and world scans without a budget.

## Spawn, point and lifecycle surfaces

- `gamemode/init.lua` builds default spawns from map points, then engine spawn entities/classes.
- `GM:PlayerSpawn` has global `OverrideSpawn` and distinct mode-table `CurrentRound().OverrideSpawn` gates.
- Team spawn calls mode `GetTeamSpawn()` and falls back to random spawn when either side is empty.
- `zb:EndRound()` is the verified core termination entry; `zb.EndMatch` remains unresolved.
- First-player initial spawn can end the current round after creating a temporary bot.

## Pathowogen and Fear surfaces

Pathowogen exposes briefing/dialogue/extraction/end-report packets, global simfphys convar changes, fake-ragdoll weld extraction, timers, audio and render state without a complete restore contract. Fear inherits Homicide and remains hard-disabled yet loads hooks, receivers, event registries, light sampling and presentation state.

## Persistence and local-data surfaces

| Surface | Owner | Contract/risk |
|---|---|---|
| mode chances/mapsizes JSON | registry/round | weak decode/type guards |
| Homicide PData | Homicide | integer-like counters |
| Event loot JSON | Event | unversioned persistent client-authored data |
| CO-OP SQLite/persistence | CO-OP | partial optional integration |
| client `data/dreams` screenshots | organism client | periodic low-quality captures while alive; deleted on spawn/init/disconnect; local persistence should be optional/documented |
| simfphys fuel convars | Pathowogen | global mutation without restore |

## Cross-system regression rules

1. Do not change packets before every writer, reader and branch is listed.
2. Record size, shape, ownership and compatibility before replacing Lua-table payloads.
3. Runtime-confirm duplicate/hook order before consolidation.
4. Validate every client table/string/vector/command for type, bounds, ID, phase, permission, distance and rate.
5. Freeze authoritative outcomes before delayed presentation.
6. Centralize timers/hooks/audio/render/convar state and prove cleanup.
7. Treat organism module order and owner transfer as public behavior.
8. Do not separate organism/fake/movement/class code before mapping every shared state writer.

## Next trace

1. Finish remaining organism input/medical/effect writers and exact hook signatures.
2. Trace fake-ragdoll creation, ownership transfer, input, networking, get-up, death and combat.
3. Trace movement and player-class consumers of organism/fake state.
4. Resolve `COMMANDS`, `zb.EndMatch`, remaining spawn-override spellings and external one-sided channels.
