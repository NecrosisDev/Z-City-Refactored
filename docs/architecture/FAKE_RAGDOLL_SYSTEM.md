# Fake-Ragdoll System Architecture

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified; weapon-specific ragdoll combat, all vehicle adapters, and every presentation consumer are not yet exhaustive  
**Reviewed:** 2026-07-12

## Purpose

The fake-ragdoll system replaces the living player body with a controllable physical ragdoll while preserving player identity, organism state, equipment, camera, appearance, NPC targeting, vehicle state, wounds, and combat interactions. It also takes ownership of death-ragdoll creation and smooth get-up behavior.

This is not a cosmetic ragdoll toggle. It is a cross-system state transition that:

- disables the engine's normal player ragdoll;
- creates and configures a custom `prop_ragdoll`;
- hides and repositions the live player entity;
- shares the player's organism table with the ragdoll;
- redirects damage and camera/render ownership;
- drives active-ragdoll physics every server frame;
- allows crawling, grabbing, choking, weapon use, vehicle integration and ragdoll combat;
- respawns the player during get-up while attempting to preserve health, armor, weapon and position;
- converts the same physical body into a death ragdoll when the player dies.

## Source topology

| File | Verified responsibility |
|---|---|
| `fake/sv_tier_0.lua` | custom ragdoll creation, fake/get-up/death lifecycle, ownership maps, networking, PVS, vehicle attachment, get-up positioning and engine-ragdoll replacement |
| `fake/sv_control.lua` | per-frame active-ragdoll control, body shadow control, crawling, grabbing, choking, use/pickup, fire response, stamina and weapon-specific ragdoll actions |
| `fake/sv_input.lua` | player console commands, collision/fall stun and forced fake administration |
| `fake/cl_fake.lua` | camera/input/view, NWEntity proxy handling, client ownership, render override, fake/death follow state and get-up presentation |
| `fake/sh_render.lua` | shared render contract, smooth unragdoll interpolation, ragdoll-combat toggle and body/weapon/armor/gore rendering |
| organism damage/brain files | damage redirection, shared organism ownership, get-up gates, collision injury and posturing/spasm behavior |
| weapons/movement/classes/modes | ragdoll-specific controls, permissions, combat and forced state transitions |

## Engine overrides

### Player ragdoll API

`PLAYER:GetRagdollEntity()` is replaced to prefer the player's networked `RagdollDeath` entity before falling back to the engine method.

`PLAYER:CreateRagdoll()` is replaced with a function that returns `false`, preventing the engine from creating its ordinary death ragdoll. `DoPlayerDeath/Fake` creates or reuses the custom fake ragdoll instead.

These are global metatable overrides. Any addon expecting the default behavior now receives the ZCity fake/death body contract.

### Spawn suppression

The get-up path uses a global `OverrideSpawn` variable plus an `Override Spawn` network message and multiple duplicate `PlayerSpawn`/`Player Spawn` hooks. The intent is to call `ply:Spawn()` without running ordinary spawn/reset behavior.

There are three distinct concepts with similar names:

1. global `OverrideSpawn` used during get-up;
2. mode field `CurrentRound().OverrideSpawn` used by gamemode spawning;
3. client `hg.override[player]` populated by `Override Spawn`.

They are not one shared API and must not be consolidated by name alone.

## Core entity/state model

### Server ownership fields

| Surface | Meaning |
|---|---|
| `ply.FakeRagdoll` | current server-side controllable physical body |
| `ply.FakeRagdollOld` / `ply.OldRagdoll` | previous ragdoll retained during get-up/render interpolation |
| `ply.RagdollDeath` | server reference to custom death body |
| NWEntity `FakeRagdoll` | replicated current fake body |
| NWEntity `FakeRagdollOld` | replicated prior body during get-up |
| NWEntity `RagdollDeath` | replicated death body used by overridden `GetRagdollEntity` |
| `ragdoll.ply` / NWEntity `ply` | owning player reference |
| `hg.ragdollFake[player]` | server active-fake lookup used by control loop |
| `hg.queue_ragdolls[ragdoll]` | PVS-delivery queue for newly created ragdolls |
| `vehicle.rags` | ragdolls attached to vehicle seats/body |
| `ragdoll.welds` | vehicle/body constraints to remove during exit/get-up |
| `ragdoll.bull` | NPC bullseye used to preserve NPC targeting relationships |

### Client ownership fields

- `ply.FakeRagdoll` is reconstructed by NWVar proxy handling rather than solely by the custom packet.
- `follow` is the local camera-follow entity.
- `ply.OldRagdoll` / `FakeRagdollOld` support smooth get-up rendering.
- `ragdoll.ply` and `ragdoll.organism` are client aliases to player identity/state.
- `hg.ragdolls` tracks client ragdoll render targets.
- `ply.ragdoll_index` / `prevragdoll_index` are used by shared render interpolation.

### Organism ownership

The player and fake ragdoll share the same organism table. The `Ragdoll_Create` organism hook transfers or aliases ownership, while client proxy handling assigns `ragdoll.organism = ply.organism`.

Damage to the living player is redirected to the fake ragdoll. Organism unconsciousness/fake state decides when the body must exist and whether get-up is allowed. On death, the same physical body becomes the death ragdoll rather than being replaced by a fresh engine body.

## Ragdoll creation lifecycle

`hg.Ragdoll_Create(ply)` broadly performs:

1. copy player entity data through duplicator helpers;
2. create `prop_ragdoll` and copy transform, model, appearance and bodygroups;
3. set collision/effect flags and spawn/activate;
4. add ragdoll to PVS queue;
5. replace any prior bullseye and create an `npc_bullseye` linked to player/ragdoll;
6. copy NPC/terminator relationships to the bullseye;
7. add physics-collision callback emitting `Ragdoll Collide`;
8. cache model bone-to-physics-body mapping;
9. copy player bone poses, mass, velocity and queued forces to every ragdoll physics body;
10. remove/amputate configured bones according to organism state;
11. if in a vehicle, parent/weld selected body parts to the vehicle or parent entity;
12. replicate player name/color and owner entities;
13. emit `Ragdoll_Create` and apply appearance rendering.

### Creation hazards

1. A ragdoll and bullseye are spawned before physics body index `10` is checked; failure returns early and can leave a partially initialized body/bullseye.
2. The system assumes ValveBiped bone names, attachments and physics-body mappings.
3. Player bone matrices, ragdoll physics objects and appearance tables are frequently used without uniform validity checks.
4. `duplicator.CopyEntTable`/`DoGeneric` copy broad entity state into the ragdoll without an explicit allowlist.
5. Creation loops every matching NPC/terminator to update relationships, producing global work per fake.
6. Vehicle creation mutates parenting, constraints, collision and player eye angles inside the same routine.
7. Model cache never documents invalidation or model/profile compatibility.
8. Amputation and physical force initialization assume organism exists and has canonical fields.

## Entering fake state

`hg.Fake(ply, suppliedRagdoll, noFreeMove, force)`:

- rejects invalid/dead/already-fake players and ordinary in-vehicle calls unless forced;
- creates or adopts a ragdoll;
- installs removal callback that can kill the living player if the fake body disappears unexpectedly;
- sets fake cooldown and broadcasts ownership;
- stores active weapon and emits `Fake`;
- disables ordinary player rendering/shadow/collision behavior;
- moves player to an invisible/noninteractive collision group while keeping the entity alive;
- disables flashlight;
- transfers fire/vFire effects to the ragdoll;
- registers the body in `hg.ragdollFake` for per-frame control.

### Unexpected ragdoll removal

`RemoveRag` clears `ply.FakeRagdoll`; if the owner is alive, it kills the player. It then calls `NET_Fake2(-1, ply)`, which resolves `Entity(-1)` and depends on undocumented engine/custom behavior. The ordinary get-up path instead broadcasts a NULL ragdoll through `NET_Up`.

## Death lifecycle

`DoPlayerDeath/Fake` reuses the active fake body or creates one, broadcasts ownership, removes its bullseye, assigns `RagdollDeath`, and copies wound/arterial-wound NetVars to the body.

`PostPlayerDeath/Garbage` removes the engine-created fallback ragdoll, clears fake lookup state, resets fake cooldown and sets view mode.

Player disconnect while alive:

- kills the player;
- locates the death ragdoll;
- creates a new organism on that ragdoll and merges player organism data;
- marks it dead and assigns owner;
- attempts `hg.organism.Remove` callback registration and calls `hg.organism.Clear(ply.organism)`.

The final two operations conflict with the verified Tier 0 API shape: `Clear` expects an entity, not the organism table, and `hg.organism.Remove` was not established as the authoritative public removal method. This path requires runtime confirmation and is likely defective.

## Getting up

`hg.FakeUp(ply, forced, instant)`:

1. validates current fake body;
2. removes/handles vehicle state and constraints;
3. unless forced, rejects dead players or any non-nil `Should Fake Up` result;
4. locates pelvis position and calculates a safe player hull position through recursive traces;
5. emits `Fake Up`;
6. preserves old ragdoll references for rendering;
7. clears active fake pointer and forces a temporary duck command;
8. removes fire/vehicle welds;
9. sets global `OverrideSpawn`;
10. saves health, armor, eye angles and active weapon;
11. broadcasts `Override Spawn` and calls `ply:Spawn()`;
12. restores health/armor/angles/weapon, velocity, position and rendering;
13. broadcasts NULL fake-ragdoll state;
14. removes old ragdoll immediately or after a one-second timer;
15. restores collision, move type, shadow and flashlight behavior.

### Get-up gates

`Should Fake Up/speedhuy` rejects get-up when:

- ragdoll velocity exceeds 200;
- organism stun or light-stun is still active;
- ragdoll is dissolving.

Organism brain/spasm and other external hooks can also return non-nil to block get-up.

### Get-up hazards

1. `Should Fake Up` treats any non-nil result—including `true`—as denial rather than checking specifically for `false`.
2. Pelvis/spine bones and matrices are dereferenced without complete guards.
3. Get-up respawns the player, traversing global spawn hooks and relying on global/network override coordination to preserve state.
4. Global `OverrideSpawn` is not protected by `xpcall`/finally semantics; an error can leave spawn suppression active.
5. The delayed `faking_up<EntIndex>` callback uses the player after one second without uniformly validating it.
6. Timer names based on EntIndex can collide after reconnect/hotload.
7. `NET_Up` can be sent in multiple branches; packet order relative to NWEntity changes is not explicit.
8. Old ragdoll aliases and client proxies can observe transient contradictory states.
9. `hg.GetUpPos` uses module-level shared `poses`/recursive state and requires a separate concurrency/reentrancy audit.
10. Health/armor/weapon restoration does not prove inventory, class, ammo, movement modifiers, organism owner or other spawn-reset state remained unchanged.

## Networking and replication

### `Player Ragdoll`

Server writes:

1. player entity;
2. ragdoll entity or NULL.

Client reads:

```lua
local ply, ragdoll, ragdoll_index = net.ReadEntity(), net.ReadEntity2()
if not ragdoll_index then return end
ply.ragdoll_index = ragdoll_index
```

No definition or other use of `net.ReadEntity2()` was found in the repository. The reader therefore depends on an external/runtime extension returning both entity and index. If it behaves like ordinary `ReadEntity`, `ragdoll_index` is nil and the packet is ignored.

The packet only assigns an index. Actual client fake ownership is primarily reconstructed through NWEntity proxies.

### NWEntity proxy path

Client installs proxies for `RagdollDeath` and `FakeRagdoll` on initial spawn and `InitPostEntity`. Proxy changes emit `RagdollEntityCreated`, whose handler:

- updates `ply.FakeRagdoll`;
- assigns render override;
- selects camera `follow` for the local player;
- transfers decals/model instance;
- aliases player/organism to ragdoll;
- emits client `Fake` or `FakeUp`;
- manages old ragdoll/get-up state.

### `Override Spawn`

Server writes player entity before get-up spawn. Client stores `hg.override[player]`; two duplicate `Player Spawn` hooks consume the marker and return `false`.

### Network hazards

1. Custom packet and NWEntity proxy are two overlapping state channels with no sequence/generation number.
2. `Player Ragdoll` relies on undefined `net.ReadEntity2` behavior.
3. Server sends both explicit packet and NWEntity updates; order under latency/PVS/entity creation is not formalized.
4. Client proxy may receive a ragdoll before its render/organism dependencies are initialized.
5. Packet has no lifecycle discriminator for fake, get-up, death or adopted body beyond NULL/entity state.
6. Ownership is inferred through replicated entity pointers and equality rather than a stable generation token.
7. PVS hooks forcibly add every queued ragdoll origin for every human until counted, potentially expanding visibility/network cost.
8. Queue completion uses `#hg.humans_cached` and per-player table keys; joins/leaves can make completion counts stale.

## Active-ragdoll control

`sv_control.lua` installs a server `Think/Fake` hook that runs every frame and iterates all players. For each active fake body it:

- updates bullseye position;
- evaluates `CanControlFake`;
- calculates frame-scaled ragdoll delta time;
- computes control power from organism pain, blood, oxygen and consciousness;
- synchronizes or drives multiple physics bodies through `ComputeShadowControl`;
- keeps the hidden player near the ragdoll/head;
- updates eye target and pose from player view;
- handles weapon/resting/melee poses;
- drives arms, legs, crawling and jump forces;
- creates/removes hand weld constraints;
- lets the ragdoll use entities and pick up weapons;
- supports grabbing other bodies, choking and furry assimilation;
- consumes stamina and adds pain for damaged/dislocated limbs;
- handles burning roll/extinguish actions;
- invokes weapon-specific `RagdollFunc`;
- cooperates with global ragdoll-combat mode.

### Control input mapping observed

| Input/state | Ragdoll behavior |
|---|---|
| attack/attack2/use | arm posing, weapon/melee actions, grabbing or resting behavior depending on weapon |
| forward/back | pull/push body through hand constraints |
| walk | hand use/grab, weapon pickup and choke/assimilation interaction |
| duck | leg/body pose and crawl/kick posture |
| move left/right while burning | roll body and probabilistically remove fire entities |
| jump in ragdoll-combat | apply upward force across controlled bodies |
| view angles | head/torso/weapon orientation and eye target |

### Control hazards and performance

1. Every server frame iterates all players and may iterate every physics object on each active body.
2. It performs repeated traces, bone lookups, matrix/attachment reads, constraint checks and shadow controls per fake.
3. Shared mutable tables (`shadowparams`, trace tables, angle/vector locals) assume no reentrancy.
4. Many physics objects, bones, attachments, organism nested fields and weapon methods are used without validity/type guards.
5. Boolean expressions mixing `and`/`or` lack parentheses in several control gates and can execute weapon/member access under unintended conditions.
6. The active weapon may be invalid, yet fields such as `RagdollFunc`, `ismelee`, `ismelee2`, weight/resting methods and hold-type methods are accessed.
7. Per-frame control directly mutates organism stamina, pain, choking, stun and assimilation, coupling simulation order to server frame rate despite partial delta-time scaling.
8. `hook.Run("PlayerUse", ply, ent)` is treated as authorization only when truthy; ordinary Garry's Mod use-hook semantics often use `false` to deny and nil to allow, so behavior may be inverted or overly restrictive.
9. Hand constraints can weld to world/entities/other ragdolls and retain callbacks/state through owner removal.
10. Choking calls `HomigradDamage` directly rather than entering the full damage pipeline, producing a distinct damage contract.
11. Furry assimilation is embedded in generic hand-control code through player-class string checks.
12. Fire handling assumes `ragdoll.fires` exists when burning.
13. Movement power uses `org.o2[1]`, pain, blood, consciousness and limbs without a fallback schema.
14. Model compatibility depends on the same hard-coded ValveBiped physical-body map as creation/damage.
15. No explicit per-frame/per-ragdoll performance budget or degradation policy exists.

## Collision and fall transitions

`sv_input.lua` adds a physics callback to every player and emits `PlayerCollide`. Heavy/fast physics impacts schedule `hg.LightStunPlayer`.

`OnPlayerHitGround/fallStun`:

- ignores players already fake;
- delegates to player-class `FallDmgFunc` when present;
- can drop/light-stun a player struck beneath another falling player;
- light-stuns the falling player above speed 600.

Risks include repeated invalid physics-object dereferences, class-specific bypasses, trace entity assumptions and separate collision/organism damage paths.

## Vehicle integration

The fake system can force players into fake bodies after entering vehicles, parent/weld ragdoll bones to vehicles, remove bodies before entry, restrict seat switching, and use vehicle parent/model-specific offsets.

Verified external surfaces include:

- `Glide_CanSwitchSeat` cooldown;
- `CanPlayerEnterVehicle` cleanup and velocity checks;
- `PlayerEnteredVehicle` delayed forced `hg.Fake`;
- `HG_OnOtrub` vehicle behavior;
- Glide/simfphys helpers and vehicle model/class conditions;
- `vehicle.rags`, ragdoll welds and seat/parent ownership.

Vehicle behavior is embedded in the core creation/get-up routines rather than isolated behind an adapter. Missing addon APIs, invalid vehicle parents/seats, delayed disconnects and constraint removal can leave player, ragdoll and vehicle state inconsistent.

## Rendering and camera

Client fake code owns or modifies:

- `CreateMove`, `InputMouseApply`, custom `HG.InputMouseApply`;
- player view angles and camera follow;
- fake/death first-person/third-person/GoPro modes;
- weapon view influence, consciousness/limb effects and vehicle camera behavior;
- render overrides for player/ragdoll, TPIK, armor, bandages, tourniquets, gore, projectiles and headcrabs;
- head bone scaling to avoid first-person self-obstruction;
- smooth ragdoll-to-player bone interpolation during get-up.

`sh_render.lua` defines `hg.RagdollCombatInUse()` from replicated convar `hg_ragdollcombat`. Shared render behavior therefore depends on client/server convar agreement and the same fake ownership state.

### Client hazards

1. Camera code uses numerous globals (`follow`, `realangle`, lerp/view state) shared with other camera systems.
2. It assumes valid local player, active weapon fields, organism limbs/consciousness, attachments and bones in many paths.
3. Render ownership can be assigned through both network entity creation and NWVar proxy callbacks.
4. The client `Player Ragdoll` packet appears partially inert; render behavior relies on proxies and replicated indices.
5. Smooth get-up writes bone matrices on both ragdoll and player every frame during transition.
6. First-person head scaling and other render mutations require guaranteed restoration across mode switch, death, entity removal and hotload.
7. Vehicle camera code can overwrite a parent vehicle's `MovePlayerView` function globally.

## Public hooks and APIs

### Lifecycle hooks

- `Ragdoll_Create(player, ragdoll)`
- `Fake(player, ragdoll [, armor/list data])`
- `Fake Up(player, ragdoll)`
- client `FakeUp` and `Player Getup` variants also exist; naming/spacing/case requires exact inventory
- `Should Fake Up(player)`
- `CanControlFake(player, ragdoll)`
- `RagdollEntityCreated(player, ragdoll, NWVarName)`
- `RagdollRemove(player, ragdoll)`
- `Ragdoll Collide(ragdoll, collisionData)`
- `ServerRagdollTransferDecals(player, ragdoll)`
- `RagdollPerdiction(ragdoll, player)`
- `PlayerCollide(player, entity, collisionData)`

### APIs

- `hg.Ragdoll_Create`
- `hg.Fake`, `hg.FakeUp`
- `hg.GetCurrentCharacter`
- `hg.RagdollOwner`
- `hg.GetUpPos`
- `hg.SavePoses`, `hg.ApplyPoses`
- `hg.RemoveDeadBodies`
- `hg.cacheModel`, `hg.realPhysNum`
- `hg.ShadowControl`
- `hg.RagdollCombatInUse`
- `hg.SmoothUnfake`
- `DrawPlayerRagdoll`

### Commands and convars

| Surface | Contract / risk |
|---|---|
| `fake` | alive/not-frozen toggle; cooldown check exists but assignment in command is commented; organism/hook gates occur downstream |
| `force_fake` | admin/server-console target by player index; missing/non-numeric/invalid target is not safely rejected before field access |
| `hg_ragdollcombat` | replicated active-ragdoll combat/walking toggle |
| `hg_fake_stamina` | server active-ragdoll stamina toggle |
| `hg_shitty_fake` | replicated control/render behavior; mirrored to GlobalBool |
| camera convars | first-person death/ragdoll, third-person, GoPro, FOV, camera smoothing; ownership overlaps other camera systems |

## Cross-system dependencies

| System | Coupling |
|---|---|
| Organism | shared state, fake/unconscious decision, damage redirection, stamina/pain/O2/pulse, wounds, amputation and get-up gates |
| Movement | hidden-player movement, player position following, inertia, jump/fall and control inputs |
| Player classes | fall function, furry assimilation, class-specific fake permissions/modifiers |
| Weapons | active weapon preservation, world rendering, resting/hold-type interfaces, ragdoll-specific callbacks and pickup/use |
| Armor/appearance | copied appearance/bodygroups, armor rendering and wound effects |
| NPC/bots | bullseye targeting, relationships, NPC organism and fake-body combat |
| Vehicles | forced fake seating, parent/weld state, seat switching and external Glide/simfphys behavior |
| Round/spawn | `OverrideSpawn`, player respawn/reset, death cleanup and spectator/death body |
| Camera/UI | follow entity, first-person head suppression, spectator/death camera and view mode |
| Fire/gore | vFire transfer, fire rolling, bandages/tourniquets/gore and body removal |

## Structural findings

1. **Three overlapping ownership channels:** server fields/maps, NWEntities/proxies and custom packet/index state.
2. **No transition transaction:** entering fake, death and get-up mutate many systems without a rollback/finally boundary.
3. **Respawn-based get-up:** the player is respawned rather than restored in place, making every spawn hook part of fake behavior.
4. **Shared mutable organism alias:** simple and efficient, but no generation/ownership token prevents stale callbacks from mutating a transferred body.
5. **Monolithic creation routine:** appearance, physics, NPC targeting, vehicles, networking and amputation are combined.
6. **Per-frame monolithic control:** active ragdoll movement, combat, use, stamina, pain, fire and class behavior share one Think loop.
7. **Hard-coded skeleton profile:** creation, control, damage and render all assume ValveBiped naming/physics mapping.
8. **Global compatibility overrides:** player metatable methods, spawn flags/hooks, vehicle behavior and render/camera functions affect unrelated addons.
9. **Hook-name inconsistency:** `Fake Up`, `FakeUp`, `Player Getup`, `Player Spawn` and `PlayerSpawn` coexist.
10. **No explicit performance budget:** PVS expansion, all-player per-frame control, all-NPC relationship updates and multi-body shadow control scale globally.

## Required validation

### Ownership and lifecycle

- Enter fake, voluntary get-up, forced get-up, unconscious fake, death while fake, death while normal, ragdoll removal, disconnect and reconnect.
- Assert one owner generation across server fields, NWEntities, custom packet, client proxies, organism owner and camera follow.
- Inject failure at every creation/get-up step and prove rollback/cleanup.
- Verify `OverrideSpawn` is cleared after errors and all spawn hooks preserve intended state.

### Physics/control

- Every supported model and missing bone/attachment/physics object.
- Per-frame cost with increasing active fake players and ragdoll-combat mode.
- Grabbing world/entities/weapons/players, choking, crawling, jumping, burning and damaged/amputated limbs.
- Constraint/entity removal, player disconnect and mode switch during every interaction.
- Frame-rate/time-scale determinism for stamina, pain, movement and force.

### Networking/client

- Determine runtime definition/behavior of `net.ReadEntity2`; remove or formalize dependency.
- Packet/NWEntity order under latency, entity dormancy/PVS, late join and reconnect.
- Verify proxies install for all players before first state change.
- Validate NULL/adopted/death/get-up transitions and duplicate packet handling.
- Measure forced-PVS cost and queue completion under joins/leaves.
- Restore camera, head scaling, render overrides and globals after every transition.

### Vehicles/integrations

- Native vehicles, prisoner pod, airboat, Glide and simfphys with missing addon APIs.
- Seat switching, high-speed entry, unconsciousness, exit/get-up and vehicle destruction.
- Weld cleanup, parent removal and dead-body ejection.
- NPC targeting and bullseye cleanup across map cleanup and entity removal.

## Implementation boundary

Do not rewrite fake-ragdoll behavior independently from organism, movement, player classes, weapons and vehicles. The eventual refactor should preserve current gameplay through an adapter while introducing:

1. explicit state machine (`Standing`, `EnteringFake`, `Fake`, `Unconscious`, `GettingUp`, `Dead`);
2. stable ownership generation/token shared by player, body and organism;
3. one authoritative replicated transition protocol;
4. transactional enter/get-up/death operations with rollback and finally cleanup;
5. model/skeleton profile validation;
6. separated body creation, appearance, NPC targeting, vehicle attachment and control services;
7. fixed-timestep/budgeted active-ragdoll control;
8. explicit weapon/class interaction interfaces;
9. vehicle adapters instead of core branching;
10. lifecycle and performance regression fixtures.

## Next trace

1. Finish weapon-specific ragdoll callbacks and remaining vehicle/control hooks.
2. Trace movement ownership and its interaction with hidden-player/fake state.
3. Trace player-class fake permissions/modifiers and organism extensions.
4. Build the combined organism/fake/movement/class integration graph.
5. Only then produce implementation-ready subsystem boundaries.
