# Z-City Player Class, Inventory, and Equipment Boundary

**Status:** Partial, executable-source verified against runtime baseline `429ec928203cec963176dfb6afd086dcdd01c181`. This document covers the currently proven orchestration boundary; complete player-class, inventory implementation, and mode-by-mode equipment enumeration remain pending.

## Purpose

This document isolates the order and authority relationships currently visible between team assignment, inventory creation, spawn placement, player-class application, and mode equipment grants.

It exists because these responsibilities are not executed by one lifecycle owner. They are split across `GM:PlayerSpawn`, `PLAYER:SetupTeam`, `zb:KillPlayers`, mode callbacks, and globally loaded libraries.

## Verified source boundary

Primary sources inspected:

- `gamemodes/zcity/gamemode/init.lua`
- `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`
- `gamemodes/zcity/gamemode/loader.lua`

The following remain outside the verified boundary:

- the definition and complete call graph of `hg.CreateInv`;
- the definition and complete call graph of `PLAYER:SetPlayerClass`;
- individual mode `GiveEquipment`, `Intermission`, `DontKillPlayer`, and spawn implementations;
- inventory persistence, drop, pickup, death, disconnect, and hot-reload behavior;
- player-class schema, inheritance, organism presets, appearance, movement modifiers, and networking.

Negative repository-wide claims are prohibited until those publishers and consumers are enumerated.

## 1. Ordinary spawn does not initialize the complete character

`GM:PlayerSpawn` performs a limited normalization path:

1. suppress Sandbox hints;
2. abort all work when global `OverrideSpawn` is truthy;
3. set view mode;
4. leave spectator mode;
5. restore walking movement;
6. process the initial-spawn sentinel path; or
7. when the active mode does not expose `OverrideSpawn`, temporarily assign team `1001`, apply appearance, and assign a balanced team.

The callback does not directly:

- create inventory;
- apply a player class;
- grant equipment;
- select a validated engine spawn entity;
- initialize organism state;
- declare a completed admission state.

A successful engine spawn therefore does not prove that the player has reached a complete playable-character state.

## 2. `PLAYER:SetupTeam` is an implicit admission transaction

The verified implementation performs exactly three operations:

1. `self:SetTeam(team_)`;
2. `hg.CreateInv(self)`;
3. direct position selection and teleport through the local `PlayerSelectSpawn` helper.

This function is broader than its name. It currently combines:

- team authority;
- inventory construction;
- mode-dependent spawn policy;
- direct spatial placement.

It does not apply a player class or grant equipment within the verified body.

### Ordering contract

The observed order is behaviorally relevant:

- team is visible before inventory creation;
- inventory creation occurs before teleportation;
- spawn policy reads the current active mode and current team;
- no result record is returned for any step;
- no rollback path is visible when inventory creation or spawn resolution fails.

### Failure implications

A failure can leave a player:

- on the requested team without a valid inventory;
- with an inventory but without a resolved spawn;
- teleported to fallback or unvalidated coordinates;
- partially admitted without class or equipment completion.

## 3. The engine spawn contract is separated from team setup

`GM:PlayerSelectSpawn` is empty. The local helper with the same name directly calls `SetPos` and is invoked from `PLAYER:SetupTeam`.

Consequences for class/inventory/equipment work:

- inventory construction is tied to direct teleportation rather than an engine spawn selection result;
- a future class or equipment initializer cannot assume normal engine spawn ordering;
- mode spawn policy and inventory construction share one implicit transaction boundary;
- tools cannot inspect a reserved spawn candidate before inventory or class mutation;
- failure attribution cannot distinguish team, inventory, policy, candidate, validation, or placement errors.

## 4. Round reset applies class after kill and respawn

During end-round transition, `zb:KillPlayers()` iterates non-spectators.

For players not preserved by `mode:DontKillPlayer(ply)`, the verified order is:

1. grant random experience;
2. disable flashlight when active;
3. `KillSilent()`;
4. `Spawn()`;
5. `SetPlayerClass()`.

The class assignment therefore occurs after the engine spawn callback has returned.

This creates an important compatibility condition: any code running during `PlayerSpawn` can observe a respawned player before the round-reset class is applied.

## 5. Preserved players bypass the class and equipment-equivalent reset path

When a live player is preserved by `mode:DontKillPlayer(ply)`, the verified path:

1. clears organism state;
2. forces fake-ragdoll recovery;
3. skips kill;
4. skips respawn;
5. skips `SetPlayerClass()` in `zb:KillPlayers()`.

The preserved branch does not prove that class, inventory, appearance, equipment, movement modifiers, or weapon state are refreshed to the next round's requirements.

This is not automatically a defect for every mode. It is a required mode-specific compatibility question.

## 6. Mode equipment is granted after all player resets and balancing

When the end delay expires, the round system performs:

1. transition to round state `0`;
2. run pre-round hooks;
3. select the next mode;
4. broadcast round state and timing;
5. call `zb:KillPlayers()`;
6. call `zb:AutoBalance()`;
7. reset mode saved state;
8. call mode `Intermission()`;
9. call mode `GiveEquipment()`.

Equipment is therefore granted after:

- ordinary respawn;
- round-reset class application;
- global auto-balance;
- the mode's intermission callback.

A replacement must preserve this order until mode fixtures prove which dependencies are intentional.

## 7. Empty base equipment method is not the active mode contract

`PLAYER:GiveEquipment(team_)` exists as an empty player metatable method in `init.lua`.

The verified round transition does not call this method. It calls `CurrentRound():GiveEquipment()`.

This creates two similarly named surfaces with different owners:

- player method: empty in the inspected source;
- mode method: lifecycle-significant round equipment authority.

Any refactor that searches by name alone can attach behavior to the wrong layer.

## 8. Mode method dispatch expands equipment authority into global hooks

The loader registers every function found on a mode table through `addModeHook`.

For each function key, it creates a global hook named after that key and dispatches to the active mode.

Implications:

- a mode's `GiveEquipment` can be both directly called by the round system and registered as a hook handler for a hook named `GiveEquipment`;
- the exact impact depends on whether any code calls `hook.Run("GiveEquipment", ...)`;
- duplicate semantic entry points are possible even when the direct round call is the intended path;
- method names are public lifecycle surfaces, not private implementation details.

Complete hook-run enumeration is still required before classifying duplicate execution as present or absent.

## 9. Global loader order participates in class and inventory availability

The gamemode loader recursively loads all child directories under `zcity/gamemode/libraries` before files in each directory, without explicit sibling sorting or dependency declarations.

`GM:PlayerSpawn`, `PLAYER:SetupTeam`, and round reset assume these globals and methods are already available:

- `hg.CreateInv`;
- `ApplyAppearance`;
- `PLAYER:SetPlayerClass`;
- `hg.organism.Clear`;
- `hg.FakeUp`;
- mode registration and dispatch;
- team balancing.

The current orchestration therefore relies on successful ambient library loading rather than an explicit character-runtime readiness capability.

## 10. Current authority map

| Responsibility | Current visible owner | Proven trigger |
|---|---|---|
| Basic spawn normalization | `GM:PlayerSpawn` | Engine spawn |
| Initial dead/spectator sentinel | `GM:PlayerSpawn` | First engine spawn |
| Appearance application | `GM:PlayerSpawn` | Ordinary spawn when mode does not override |
| Balanced team assignment | `GM:PlayerSpawn` | Ordinary spawn when mode does not override |
| Explicit team assignment | `PLAYER:SetupTeam` | Caller-defined |
| Inventory creation | `PLAYER:SetupTeam` via `hg.CreateInv` | Caller-defined |
| Direct spawn placement | local `PlayerSelectSpawn` | `PLAYER:SetupTeam` |
| Round-reset class application | `zb:KillPlayers` via `SetPlayerClass` | Non-preserved round reset |
| Preserved-player organism/fake reset | `zb:KillPlayers` | `DontKillPlayer` branch |
| Team balancing | `zb:AutoBalance` | After all round resets |
| Mode intermission mutation | active mode | After balancing |
| Equipment grant | active mode `GiveEquipment` | After intermission |

No single owner currently publishes a complete character-admission result.

## 11. Verified architectural problems

1. `PLAYER:SetupTeam` combines team, inventory, spawn policy, and teleportation without a transaction result.
2. Round-reset class assignment occurs after `PlayerSpawn`, exposing a partially initialized interval.
3. Preserved players bypass the ordinary class assignment path.
4. Equipment authority belongs to the active mode and runs after balance/intermission, while a similarly named empty player method also exists.
5. Mode functions are automatically projected into global hooks, making method names part of the public dispatch surface.
6. Character initialization depends on ambient loader success and unversioned globals.
7. No verified completion marker identifies when team, spawn, inventory, class, organism, appearance, and equipment are coherent.

## 12. Target character-admission boundary

A replacement should expose an ordered server-authoritative transaction:

```text
CharacterAdmission
  identity
  admission_generation
  round_generation
  mode_identity
  requested_team
  resolved_team
  spawn_policy
  spawn_candidate
  inventory_plan
  class_plan
  appearance_plan
  organism_plan
  equipment_plan
  prepare_results
  commit_results
  rollback_or_repair_results
  completion_state
```

Required phases:

1. resolve mode admission policy;
2. resolve team;
3. resolve and validate spawn candidate;
4. build inventory/class/appearance/organism/equipment plans without mutation;
5. commit representation and placement;
6. commit inventory and class;
7. apply appearance and organism state;
8. grant equipment;
9. validate invariants;
10. publish completion or a structured partial-failure record.

This is a target contract, not current behavior.

## 13. Trauma comparison

### Adapt

- explicit per-player lifecycle phase tracing;
- structured admission diagnostics;
- data-driven class, inventory, and equipment plans;
- mode capability declarations;
- generation-bound initialization work.

### Rewrite

- player admission coordination;
- class and inventory ownership;
- preserved-player reset semantics;
- equipment grant orchestration;
- hot-reload and failure recovery;
- mode method-to-hook projection for new modes.

### Reject

- parallel character authorities for spawn, class, inventory, or equipment;
- silent fallback after critical inventory/class initialization failure;
- broad global interception of team, spawn, hook, or timer APIs;
- class or equipment state authored through irreversible shared-table mutation;
- client-authoritative loadout, inventory, class, or team decisions.

### Keep Z-City temporarily

- current `SetupTeam` ordering;
- current round-reset ordering;
- current `DontKillPlayer` branch behavior;
- class-after-respawn behavior;
- auto-balance before intermission/equipment;
- mode-owned `GiveEquipment` outcomes.

These remain compatibility requirements until each stock mode has executable fixtures.

## 14. Required source enumeration

The next pass for this boundary must identify:

- every call to `PLAYER:SetupTeam`;
- the definition and every call to `hg.CreateInv`;
- the definition and every call to `PLAYER:SetPlayerClass`;
- every mode `GiveEquipment`, `Intermission`, `DontKillPlayer`, `OverrideSpawn`, and `GetTeamSpawn` implementation;
- every direct `SetTeam`, `Spawn`, `StripWeapons`, `Give`, inventory reset, class reset, and loadout mutation in mode code;
- disconnect, death, cleanup, map cleanup, and hot-reload ownership;
- client-visible class, inventory, team, and equipment replication.

## 15. Required runtime tests

1. First join through spectator admission and first playable spawn.
2. Ordinary respawn with final team, position, inventory, class, organism, appearance, and equipment assertions.
3. Round reset for a non-preserved player.
4. Round reset for every `DontKillPlayer` mode branch.
5. Failure or absence of inventory creation.
6. Failure or absence of class application.
7. Invalid or empty spawn candidates.
8. Team rebalance after class and inventory initialization.
9. Equipment grant before and after mode intermission mutations.
10. Late join during intermission and active round.
11. Death or fake transition during admission.
12. Disconnect during admission.
13. Mode change or hot reload during admission.
14. Duplicate `GiveEquipment` execution detection.
15. State loss or duplication across kill, spawn, class, and equipment phases.
16. Optional integrations absent and present.

## 16. Exact continuation

Complete recursive weapon publisher enumeration remains the highest-priority blocked source audit. While repository code search is unavailable, the next non-duplicative pass should enumerate exact mode/player-class/inventory paths through known loader and mode entry points, without converting unresolved absence into verified claims.
