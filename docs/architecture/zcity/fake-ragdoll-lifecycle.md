# Z-City Fake-Ragdoll Lifecycle and Authority

**Status:** Verified by static inspection of the current executable source. Runtime validation remains required for vehicle, prediction, combat, and rapid-transition behavior.

## Scope

This document records fake-ragdoll creation, identity, authority transfer, player input, get-up, death conversion, vehicles, camera behavior, cleanup, and the compatibility boundary required before refactoring.

Primary source files:

- `lua/homigrad/fake/sv_tier_0.lua`;
- `lua/homigrad/fake/sv_input.lua`;
- `lua/homigrad/fake/cl_fake.lua`;
- organism, player-class, weapon, vehicle, death, and round consumers.

## Current identity model

A fake player can be represented simultaneously by several references:

- the hidden but still alive player entity;
- `ply.FakeRagdoll`;
- `ply:GetNWEntity("FakeRagdoll")`;
- `hg.ragdollFake[ply]`;
- `ragdoll.ply` and `ragdoll:GetNWEntity("ply")`;
- `ply.FakeRagdollOld` / `ply.OldRagdoll` during recovery;
- `ply.RagdollDeath` / `NWEntity("RagdollDeath")` after death;
- the organism table shared or transferred between identities.

There is no explicit fake-state enum, transition generation, or authoritative identity token. Correctness depends on all references being updated in the correct order.

## Creation

`hg.Ragdoll_Create(ply)` duplicates player entity data into a `prop_ragdoll`, copies appearance, body state, model pose, velocity, amputations, and physical mass, then creates an `npc_bullseye` used to preserve NPC hostility toward the represented player.

Creation also:

1. adds the ragdoll to a global PVS-delivery queue;
2. installs collision and removal callbacks;
3. copies player bone transforms into ragdoll physics objects;
4. establishes networked player/ragdoll references;
5. emits `Ragdoll_Create`;
6. applies appearance;
7. performs special vehicle parenting and weld behavior when the player is seated.

The function has many partial-failure points after entity creation. For example, a missing physics object can return before all cleanup ownership is installed.

## Entering fake state

The ordinary user path is the `fake` console command. It checks alive state, cooldown, and frozen state, then calls `hg.Fake` or `hg.FakeUp`.

`hg.Fake`:

1. rejects invalid, dead, already-fake, unsupported movement, and ordinary vehicle cases unless forced;
2. creates or adopts a ragdoll;
3. installs removal ownership;
4. broadcasts `Player Ragdoll`;
5. writes all current fake references;
6. clears previous recovery ragdolls;
7. cancels the named get-up timer;
8. records the active weapon and emits `Fake`;
9. hides the player through rendering/collision/movement changes rather than removing the player entity;
10. disables flashlight use;
11. transfers selected fire presentation to the ragdoll through delayed work.

A zero-delay collision-group callback is explicitly marked as a temporary fix and has no generation check.

## Control and movement

`hg.SetFreemove` changes the hidden player's movement type, hull, view offsets, and fake timing. This means ragdoll control is partly implemented through the still-existing player movement controller.

Control permission is distributed across:

- `CanControlFake` hooks;
- organism stun fields;
- weapon fake/combat code;
- client input/camera code;
- the `hg_ragdollcombat` setting;
- vehicle and recovery state.

The current system does not expose one authoritative control-state object.

## Recovery / get-up

`hg.FakeUp(ply, forced, instant)` performs a broad recovery transaction:

1. validates the current ragdoll and `Should Fake Up` hooks;
2. blocks recovery for velocity, stun, light stun, dissolving, and invalid placement unless forced;
3. removes vehicle weld state and may exit the vehicle;
4. computes a candidate position through recursive trace sampling;
5. emits `Fake Up`;
6. moves the ragdoll into `FakeRagdollOld` / `OldRagdoll` recovery identity;
7. forces duck input temporarily;
8. calls `ply:Spawn()` under the global `OverrideSpawn` flag;
9. restores health, armor, view, weapon, render, movement, collision, and flashlight state;
10. broadcasts the non-fake state;
11. removes the old ragdoll immediately or through `faking_up<EntIndex>` after one second.

Recovery is therefore implemented by respawning the player while manually preserving selected state. Any spawn consumer that does not respect `OverrideSpawn` can mutate inventory, class, team, organism, or mode state during get-up.

The named removal timer is better than anonymous work but remains keyed only by entity index. It has no player lifetime, round, fake-transition, or owner generation.

## Death conversion

`DoPlayerDeath` reuses the existing fake ragdoll or creates one, removes its bullseye, assigns it as `RagdollDeath`, and copies wound NetVars. `PostPlayerDeath` removes the engine-created ragdoll, clears fake references, resets fake timing, and changes view mode.

The fake ragdoll therefore changes role from a live proxy to a corpse without an explicit identity transition. Organism authority, death networking, removal callbacks, and stale delayed work must infer this change from mutable references.

If an owned fake ragdoll is removed unexpectedly, `RemoveRag` can kill the still-alive player. This is intentional failover behavior but makes entity removal a gameplay-authoritative death path.

## Vehicle behavior

Vehicle integration is embedded directly in the core fake file.

Observed behavior includes:

- entering most vehicles schedules `EnterVehicleRag<EntIndex>` and force-fakes the player;
- the ragdoll is parented to the vehicle or parent vehicle entity;
- selected bones are welded to the vehicle;
- weld removal can force vehicle exit and schedule physics-mass restoration;
- seat switching uses shared player flags and a Glide hook;
- leaving a vehicle either gets the player up or ejects the ragdoll based on speed;
- vehicle entry can be blocked while dead bodies are detached;
- client camera input is overridden while seated unless adapter predicates disable it.

This architecture explains why vehicle entry, ragdoll creation, aim control, camera behavior, seat switching, and ejection are tightly coupled. Vehicle adapters cannot safely replace only one hook.

## Client camera and prediction

`cl_fake.lua` owns broad mouse and camera behavior for ordinary play, fake state, death, and vehicles. It:

- replaces `InputMouseApply` behavior;
- stores global/local mutable camera angles;
- applies view-punch, weight, consciousness, amputation, lean, and ragdoll-follow effects;
- overrides vehicle angle input in selected vehicles;
- uses ragdoll eye attachments and physics orientation;
- contains several client settings for camera smoothing, first-person ragdoll/death, FOV, GoPro, and third person.

Prediction ownership is implicit. The client derives presentation from mutable globals and replicated entity references rather than a versioned fake-state snapshot. Rapid fake/get-up/death/vehicle transitions can therefore apply camera state from the wrong identity.

## Collision and forced transitions

`sv_input.lua` exposes:

- player collision callbacks that schedule light stun;
- fall-stun logic that can fake or stun players;
- an admin `force_fake` command;
- the ordinary `fake` command.

Collision delayed work is anonymous and captures the player without a transition generation. The administrative command also assumes its target argument resolves to a valid player before dereferencing fake state.

## Cleanup behavior

Current cleanup is distributed across:

- ragdoll `CallOnRemove` handlers;
- `PostPlayerDeath`;
- `PlayerSpawn` and `Player Spawn` hooks;
- `PlayerDisconnected` hooks;
- `PreCleanupMap` forced get-up;
- vehicle leave and weld-removal callbacks;
- organism removal callbacks;
- named and anonymous timers.

Disconnect handling clears registry state and can kill the player to create/transfer a corpse organism. Several networked references, vehicle collections, timers, callbacks, and client camera globals have separate cleanup paths.

## Verified architectural defects

1. Fake identity has several writable authorities and no explicit state generation.
2. Recovery calls full `Spawn()` under a mutable global bypass flag.
3. Vehicle entry intentionally creates a ragdoll for most supported vehicles.
4. Vehicle, fake, camera, seat, and weapon authority are not separated by adapter boundaries.
5. Delayed callbacks can survive fake/get-up/death/vehicle transitions.
6. Unexpected ragdoll removal can kill the represented player.
7. Creation can partially return after spawning entities but before complete ownership setup.
8. Recovery state preservation is an open-coded list rather than a registered transaction.
9. Get-up placement uses shared recursive scratch state and no reservation token.
10. Client prediction uses mutable global camera state and entity references without transition sequencing.

## Trauma comparison

Trauma expands fake, play-dead, combat, rendering, vehicle, organism, and adapter behavior, but it retains overlapping legacy and replacement pathways.

Initial disposition:

- **Adopt:** explicit fake-state generations, transition diagnostics, and adapter capability checks as requirements.
- **Adapt:** useful ragdoll combat, camera, play-dead, and vehicle mechanics only after each is separated into bounded policies.
- **Rewrite:** fake identity, authority transfer, recovery transaction, delayed work, networking, prediction, and vehicle integration.
- **Reject:** broad detours, duplicated fake authorities, global transition flags, and bundling vehicle implementations with the core fake system.
- **Keep Z-City temporarily:** packet names, public hooks, entity references, visual behavior, and current gameplay outcomes until fixtures establish parity.

## Required project boundary

The replacement architecture requires:

1. one server-authoritative fake-state machine with states such as upright, entering, fake-controlled, fake-incapacitated, recovering, corpse, and removed;
2. a monotonically increasing character/representation generation;
3. one identity record for player, active physical representation, organism owner, vehicle/seat, and corpse;
4. an ordered transition transaction with prepare, commit, rollback, and cleanup participants;
5. owned delayed tasks bound to player, round, and representation generations;
6. a recovery API that does not invoke ordinary spawn policy implicitly;
7. a vehicle adapter interface for eligibility, pose, parenting, constraints, camera, weapons, seat changes, exit, and ejection;
8. versioned fake-state replication and client rejection of stale transitions;
9. separated camera presentation from authoritative input and combat state;
10. explicit removal policy distinguishing expected cleanup from gameplay death.

## Required acceptance tests

1. Manual fake and get-up while standing, moving, crouching, airborne, stunned, unconscious, dissolving, and blocked.
2. Repeated fake/get-up commands around cooldown boundaries.
3. Fake during round reset, spawn, death, respawn, disconnect, map cleanup, and Lua refresh.
4. Existing fake ragdoll converted to death ragdoll without duplicate corpse or organism.
5. Unexpected active-ragdoll removal and expected cleanup removal.
6. Recovery preserves exactly the intended health, armor, class, organism, inventory, weapon, ammo, appearance, and team state.
7. Get-up placement in open, crowded, moving, constrained, underwater, and invalid-bone cases.
8. All delayed callbacks rejected after a newer representation generation.
9. Vehicle entry/exit, seat switching, high-speed ejection, vehicle removal, parent removal, weld removal, and adapter absence.
10. Vehicle free aim, ADS, weapon use, camera orientation, and prediction.
11. NPC hostility and bullseye cleanup through fake, get-up, death, and removal.
12. Owner, observer, PVS, spectator, and late-join fake-state replication.
13. Fake-ragdoll combat with weapon drop, pickup, fire, reload, obstruction, and limb impairment.
14. Client prediction under latency, packet reordering, rapid transitions, and stale entity references.
15. Hot reload with active fake players and occupied vehicles.

## Next verification work

- Map player-class, inventory, weapon, and mode consumers of fake transitions.
- Trace fake-ragdoll combat and weapon ownership end to end.
- Compare every Trauma fake/vehicle file against this baseline.
- Build the combined player/organism/fake/movement/class ownership graph.