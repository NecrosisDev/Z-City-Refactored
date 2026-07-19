# Z-City Player Lifecycle

**Status:** Observed from the current `main` implementation. Runtime verification and mode-by-mode comparison are still required.

## Scope

This document records the current player lifecycle from initial connection through spawn, round reset, death, spectating, spectator opt-in, and respawn eligibility.

Primary source paths:

- `gamemodes/zcity/gamemode/init.lua`
- `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`
- mode implementations under `gamemodes/zcity/gamemode/modes/**`

Fake-ragdoll internals, organism initialization, player-class construction, inventory construction, and mode-specific spawn overrides remain separate follow-up analyses.

## 1. Initial connection

`GM:PlayerInitialSpawn(ply)` sets `ply.initialspawn = true`.

The same callback also contains population-management behavior:

1. When the joining player is the only connected player, the server runs the `bot` console command.
2. It sets `hg.addbot = true`.
3. It forces `zb:EndRound()`.
4. When more than one human is present and the temporary bot flag is set, all players returned by `player.GetListByName("bot")` are kicked and the flag is cleared.

### Consequences

- First-player admission is coupled to bot creation and round termination.
- A connection callback mutates round state before the new player has completed the first spawn path.
- The code assumes every player returned by the name query is the disposable bootstrap bot.
- The reason for the temporary bot is not represented as a capability or lifecycle participant.

**Disposition:** Preserve behavior until runtime-tested, then separate server-population bootstrap from player admission.

## 2. Late-join round synchronization

A separate `PlayerInitialSpawn` hook sends `RoundInfo` when `zb.CROUND` already exists. The payload contains:

- resolved mode name;
- current round-state integer.

It then calls `ply:SyncVars()` when available.

### Limitations

- The late joiner receives a round summary, not an explicitly versioned complete player/round snapshot.
- Round timing is synchronized through a separate channel and may not be sent by this path.
- Mode-specific state, spectator target, organism state, inventory state, and player-class state are synchronized elsewhere or implicitly.

**Requirement:** Define one late-join snapshot contract with ordered subsystem contributions and explicit versioning.

## 3. First spawn sentinel path

`GM:PlayerSpawn(ply)` performs hint suppression, then exits immediately when the global `OverrideSpawn` is truthy.

For the first spawn after connection:

1. `ply.viewmode` becomes `3`.
2. The player is unspectated.
3. Movement becomes `MOVETYPE_WALK`.
4. `ply:KillSilent()` is called.
5. Team becomes `1001`.
6. `ply.initialspawn` is cleared.
7. The callback returns.

This deliberately converts the first engine spawn into a dead/spectating state instead of admitting the player directly into active gameplay.

### Risks

- Team `1001` is an implicit sentinel rather than a named contract.
- The first spawn performs death-state mutation while death/spectator hooks may also execute.
- A global `OverrideSpawn` can suppress all initialization in this callback, including movement and spectator normalization.
- The callback does not document whether `KillSilent()` is expected to trigger every ordinary death-side effect.

**Disposition:** Keep behavior for compatibility; replace magic team/state values with named states after mode tests exist.

## 4. Ordinary spawn path

For later spawns, the callback:

1. suppresses Sandbox hints;
2. sets view mode `3`;
3. calls `UnSpectate()`;
4. sets walking movement;
5. unless the active mode exposes `OverrideSpawn`, temporarily assigns team `1001`;
6. calls `ApplyAppearance(ply, nil, nil, nil, true)`;
7. assigns a balanced team through `zb:BalancedChoice(0, 1)`.

### Important exclusions

The callback does not itself:

- select a physical spawn point;
- create inventory;
- apply a player class;
- initialize or clear organism state;
- grant equipment;
- define loadout order.

Those responsibilities are distributed across `PLAYER:SetupTeam`, round-reset code, mode callbacks, player-class code, and other subsystems.

## 5. Spawn-point discovery

At startup and `InitPostEntity`, `getRandSpawn()` rebuilds a cached array.

Selection order:

1. Use map points named `Spawnpoint` when at least one exists.
2. Otherwise add `info_player_start` entities.
3. Then add positions from a broad hard-coded list of spawn entity classes.

Navmesh-derived spawns exist only as commented code.

### Observed concerns

- The broad fallback can mix semantically incompatible team or gamemode spawn entities.
- Duplicate positions are not removed.
- The cache rebuild does not run on `PostCleanupMap` in this file.
- Entity validity is converted immediately to positions, so later removal is not represented.
- There is no spawn-source metadata for diagnostics.

## 6. Random spawn selection

`zb:GetRandomSpawn()` delegates to `zb:FurthestFromEveryone()`.

The suitability function rejects a candidate when an alive player's position is within a tolerance-scaled distance. The search relaxes tolerance across five passes, then falls back to `table.Random`.

### Verified defect

The helper accepts a `target` parameter but does not use it. The restriction set defaults to all players, including the player being positioned when that player is already alive.

### Risks

- Suitability checks only player distance, not hull clearance, world bounds, hazards, line of sight, objective constraints, or map-specific rules.
- Final fallback can select a known-bad position.
- Empty-cache behavior can return `nil` and is not handled consistently by every caller.

**Trauma comparison:** Trauma's spawn contracts and validation address valid requirements, but its implementation remains deferred until each stock mode's spawn policy is mapped. The future API should preserve source metadata, validation reasons, and deterministic fallback policy.

## 7. Team spawn selection

`zb:GetTeamSpawn(ply)` asks the active mode for two spawn collections.

When either collection is missing or empty, it substitutes one random spawn. The first player for each team receives a random anchor. Later players are offset around that anchor through `hg.tpPlayer`, using entity index to choose one of twenty-four slots.

`ZB_PreRoundStart` clears the two team anchors.

### Risks

- Team identity is assumed to be `0` versus any non-zero team.
- The error path after the two branch returns is unreachable.
- The mode's spawn-table return shape is implicit.
- Anchor placement and offset safety are delegated without validation here.
- The team anchor is global round state rather than an owned spawn-session object.

## 8. `PlayerSelectSpawn` behavior

The engine-facing `GM:PlayerSelectSpawn` method is empty.

A separate local function named `PlayerSelectSpawn` directly teleports the player:

- random spawn when `CurrentRound().randomSpawns` is true;
- otherwise team spawn;
- random fallback when team spawn resolution fails.

`PLAYER:SetupTeam(team_)` sets the team, creates inventory, then calls this local teleporter.

### Consequences

- The normal engine spawn-selection contract is bypassed.
- A local function shares the engine hook's name but has different semantics and visibility.
- Teleporting during team setup couples team assignment, inventory creation, and spatial placement.
- Spawn-point entities are not returned to the engine.

**Disposition:** Preserve until mode parity tests exist. The replacement should expose explicit phases: choose policy, resolve candidate, validate, reserve, position, initialize inventory/class, and release reservation.

## 9. Round reset transaction

At the transition from end delay to intermission, `zb:EndRoundThink()` calls:

1. `self:KillPlayers()`;
2. `self:AutoBalance()`;
3. mode `Intermission()`;
4. mode `GiveEquipment()`.

`zb:KillPlayers()` is broader than its name suggests. For every non-spectator it:

- grants random experience;
- allows `mode:DontKillPlayer(ply)` to preserve an alive player;
- when preserved, clears organism state and forces fake-ragdoll recovery;
- otherwise turns off the flashlight;
- silently kills;
- immediately spawns;
- assigns a player class.

### Ordering contracts

The observed order is behaviorally significant:

1. experience before preservation decision;
2. organism clear and fake-up only on the preservation branch;
3. kill before spawn;
4. player class after spawn;
5. auto-balance after every player has been reset;
6. mode equipment after intermission callback.

### Risks

- `KillPlayers` is an undocumented multi-subsystem transaction.
- Failure in any step can leave a partially reset player.
- Random experience gain is coupled to lifecycle reset.
- Preserved players do not run the same class, inventory, appearance, or equipment path as respawned players.
- The reset has no per-player result record or rollback/repair mechanism.

**Requirement:** Replace with an explicit round-reset coordinator only after acceptance tests capture the current ordering and mode exceptions.

## 10. Death transition

`GM:PlayerDeath(ply)`:

1. clears cached spectator targets;
2. enters roaming spectator mode;
3. shrinks standing and duck hulls to a one-unit cube;
4. initializes spectator index and view mode;
5. schedules an anonymous delayed callback after 0.1 seconds;
6. the callback selects the first alive player when the dead player remains valid and dead.

### Risks

- Hull replacement is not paired with an explicit restoration in this callback.
- Spectator target selection depends on ordering from `zb:CheckAlive()`.
- The anonymous timer cannot be cancelled or diagnosed.
- A rapid respawn, disconnect, team change, or mode transition leaves the timer alive until execution, though validity/death guards suppress most effects.

**Trauma comparison:** Generation guards are justified for this class of delayed work, but the final implementation should use cancellable owned delayed tasks rather than anonymous `timer.Simple` wrappers.

## 11. Respawn eligibility

`PLAYER:CanSpawn()` returns true when either:

- the active mode defines `CanSpawn` and returns truthy for the player; or
- the round state equals `0`.

`GM:PlayerDeathThink(ply)` returns `false` only when `CanSpawn()` is false.

### Semantics to preserve

- A mode can permit respawn during an active round.
- Intermission permits respawn by default.
- A mode callback returning false falls through to the round-state check because the expression uses `or`.

That final point is potentially surprising: a mode cannot explicitly deny spawn during state `0` through `CanSpawn`; state `0` still permits it.

## 12. Spectator selection and movement

Dead players submit `ZB_ChooseSpecPly` with an input key.

Server behavior:

- ignores requests from alive players;
- obtains the current alive-player list;
- cycles forward on attack;
- cycles backward on secondary attack;
- cycles view mode on reload;
- sends current and adjacent target entities plus view mode;
- stores the chosen target on the player.

A `PlayerDeathThink` hook then:

- publishes target and view mode through networked variables;
- sends organism state once per second for first-person spectating;
- moves the spectator entity near the target for non-roaming modes;
- enables noclip and roaming observer mode for view mode `3`;
- restores walking movement when leaving roaming mode.

`SetupPlayerVisibility` adds the target position to the spectator's PVS when needed.

### Trust and correctness concerns

- The client controls the key value, though the server constrains recognized actions.
- Target lists are recomputed and indexed without stable identities across list changes.
- Spectators are physically teleported near targets in non-roaming modes.
- Organism replication is driven from spectator polling rather than a documented observation subscription.
- Movement mode and hull state are manipulated across multiple callbacks.

## 13. Spectator opt-in/out

`ZB_SpecMode` accepts a client boolean.

The server calls `hook.Run("ZB_JoinSpectators", ply)` and enables the requested transition when that hook does not return truthy.

When joining spectators:

- an alive player is killed;
- team becomes `TEAM_SPECTATOR`;
- a global chat message is printed.

When leaving spectators:

- any player whose team is not `1` is assigned to team `1`;
- a global chat message is printed.

### Risks

- The boolean requests state, but the leave path uses hard-coded team `1` rather than mode/team policy.
- Joining spectators uses ordinary `Kill()`, not the round-reset path.
- Permission and round-policy semantics are delegated to an ambiguously inverted hook result.
- No rate limit is visible in this receiver.

## 14. Disconnect behavior

`GM:PlayerDisconnected()` is empty.

Cleanup therefore depends on subsystem hooks elsewhere.

### Requirement

Inventory, fake-ragdoll, organism, spectator, timers, ownership records, mode state, bot state, and network subscriptions must each be traced for disconnect cleanup. An empty gamemode callback does not prove cleanup is absent, but it provides no central contract.

## 15. Verified architectural problems

1. Initial admission, population bootstrap, and round termination are coupled.
2. Magic team values represent lifecycle states.
3. Engine spawn selection is bypassed by direct teleportation.
4. Team, inventory, spawn position, appearance, class, and equipment initialization are split across unrelated paths.
5. Round reset is a broad non-transactional operation hidden behind `KillPlayers`.
6. Preserved and respawned players follow materially different reset paths.
7. Anonymous delayed death work has no explicit owner or cancellation.
8. Spectator state is distributed across network receivers, death callbacks, polling hooks, movement type, hulls, and networked values.
9. Late-join synchronization is fragmented.
10. Disconnect cleanup has no central lifecycle contract.
11. Spawn candidate validation is too narrow and fallback can knowingly select unsuitable positions.
12. Client-requested spectator changes lack visible rate limiting and use hard-coded team restoration.

## 16. Behavior to preserve during refactor

- first engine spawn does not immediately enter active play;
- mode `OverrideSpawn` and global `OverrideSpawn` compatibility surfaces;
- intermission respawn permission;
- mode-specific active-round respawn permission;
- current team-balancing point in the round transition;
- `DontKillPlayer` preservation behavior and its organism/fake-up cleanup;
- player-class assignment after forced round respawn;
- spectator view-mode cycling and PVS support;
- late-join receipt of current mode and round state;
- team and random spawn mode behavior;
- existing map-point preference over entity-class fallback.

## 17. Required acceptance tests

1. first human joins an empty server;
2. temporary bootstrap bot creation and removal;
3. late join during states `0`, `1`, and `3`;
4. first spawn sentinel transition;
5. ordinary spawn with and without global override;
6. ordinary spawn with and without mode override;
7. random versus team spawn policies;
8. no map points and no valid spawn entities;
9. crowded spawn relaxation and final fallback;
10. every stock mode's team-spawn return shape;
11. `DontKillPlayer` true and false paths;
12. preserved fake-ragdoll player during round reset;
13. class, appearance, inventory, and equipment ordering;
14. death followed by immediate respawn before the delayed spectator callback;
15. disconnect during the delayed death callback;
16. spectator target disappearing while selected;
17. spectator switching among all three view modes;
18. joining and leaving spectators during each round state;
19. mode `CanSpawn` true, false, and nil during each round state;
20. cleanup and Lua refresh while players are alive, dead, fake, or spectating.

## 18. Refactor boundary

The next implementation target is not a replacement spawn or player-state engine. It is an observational lifecycle trace that records, per player:

- lifecycle phase;
- initiating event;
- mode and round generation;
- team before/after;
- alive/fake/spectator state before/after;
- selected spawn policy and candidate source;
- class, inventory, appearance, organism, and equipment operations;
- delayed tasks and cleanup ownership;
- failures and partial completion.

The existing implementation remains authoritative until these traces and acceptance tests demonstrate parity.