# Movement System Architecture

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified for the core movement directory; traversal, weapon stance, vehicle and every external movement-hook consumer remain incomplete  
**Reviewed:** 2026-07-12

## Purpose

The movement system replaces ordinary sandbox movement calculation with a shared server/client pipeline that derives speed, jump power, inertia, crouch behavior, slipping, animation and footsteps from:

- organism state;
- fake-ragdoll state;
- player class fields and replicated class multipliers;
- active weapon stance and weight;
- armor/inventory/carried-object mass;
- view direction and player input;
- walking/sprinting/crouching/ground state;
- custom movement hooks and convars.

It runs in both realms for prediction, but several calculations use realm-local time/state and broad mutable fields, so deterministic movement depends on identical load order, class state, organism snapshots, weapon interfaces and convars.

## Source topology

| File | Responsibility |
|---|---|
| `movement/sh_inertia.lua` | authoritative/predicted `SetupMove` calculation, speed, jump, inertia, physiology/class/weapon modifiers, carry reach, slip/dive-fake and custom movement hooks |
| `movement/sh_anims.lua` | `CalcMainActivity`/`UpdateAnimation`, sequence/gesture selection, velocity pose parameters and custom animation hooks |
| `movement/sh_footsteps.lua` | custom footsteps, volume/pitch/material variants, class hook and server/client sound emission |
| `movement/sh_movedata.lua` | helper state such as walking/sprinting/backward predicates and movement-direction utilities |
| fake control/input | active-ragdoll movement replaces ordinary player movement while fake |
| organism stamina/lungs/pain | movement energy, oxygen, pain, limbs, spine, consciousness and immobilization |
| player classes | direct Lua multipliers, replicated NW multipliers, run speed/jump power, fall function and class-specific movement hooks |
| weapons | speed, aiming/resting/hold-type and fake-ragdoll callbacks |

## Core `SetupMove` pipeline

The shared `SetupMove/homigrad-inertia` hook broadly executes:

1. calculate realm-local delta time from `SysTime()` and a player field;
2. reject missing organism/brain state;
3. handle noclip and emit custom movement hook stages;
4. suppress normal movement while fake unless ragdoll-combat rules permit it;
5. determine walking/running/crouching/backward state;
6. calculate weight from armor, inventory, active weapon and carried physics entities;
7. calculate organism power from legs, spine, pain, blood, oxygen, stamina, shock, disorientation, immobilization and other fields;
8. apply class and NWInt movement multipliers;
9. apply active weapon/aim/resting/hold-type restrictions;
10. apply direction, crouch, backward and in-air modifiers;
11. calculate target speed and optional inertia interpolation;
12. rewrite command movement values and maximum speed;
13. set jump power and process jump/dive/slip behavior;
14. limit carried-object reach and force dropping when overextended;
15. emit custom staged movement hooks for modes/classes/weapons/integrations;
16. update player movement bookkeeping used by animations, footsteps and organism stamina.

The system therefore remains active even when `hg_inertia` is disabled. That convar primarily changes interpolation/acceleration behavior; the hook still owns speed caps, jump power, fake input suppression, physiology, class/weapon restrictions, slipping and extension hooks.

## Input/state helpers

Verified player helpers include walking, sprinting and backward predicates. These are consumed by movement, footsteps, fake control, classes and weapons.

Movement state is distributed across:

- engine buttons/command movement;
- player fields such as `CurrentSpeed`, velocity/history, jump/crouch timers and carried entity state;
- organism nested tables and scalar modifiers;
- class Lua fields (`JumpPowerMul`, `SpeedGainClassMul`, `StaminaExhaustMul`, etc.);
- class/mode NWInts (`SpeedMul`, `JumpMul`, and other project-defined multipliers);
- weapon fields/methods;
- global/current-round state and custom hooks.

There is no explicit movement-context object or schema.

## Organism coupling

Movement reads or writes at least:

- `brain`, `spine1..3`, legs and leg dislocations/amputations;
- `pain`, `blood`, `o2`, `consciousness`, `shock`, `immobilization`, `stun`, `lightstun`;
- stamina current/max/regen/exhaustion and adrenaline;
- `canmove`, `canmovehead`, `legstrength`, `recoilmul` and mode/class extensions.

The stamina module also installs `FinishMove` and updates energy from movement state. Movement and organism therefore form a feedback loop:

```text
input + movement modifiers
    -> velocity/sprint/jump
    -> stamina/O2/pain effects
    -> next movement calculation
```

Because the movement hook runs every predicted command and organism runs on the server global tick, client movement can temporarily use stale physiological snapshots.

## Fake-ragdoll coupling

When `FakeRagdoll` is valid, normal player movement is suppressed or redirected according to ragdoll-combat mode and custom hooks. The hidden player entity is repositioned by fake control rather than ordinary movement.

Ordinary movement also triggers fake transitions:

- high-speed falls/light stuns;
- dive-fake behavior;
- slips and loss of balance;
- class-specific fall handlers;
- organism unconsciousness/fake state;
- vehicle/fall/collision conditions.

Movement and fake control are therefore mutually exclusive only by convention and state checks, not through a single owner token.

## Class coupling

Classes modify movement through several incompatible mechanisms:

1. direct engine setters such as `SetRunSpeed`;
2. direct Lua fields such as `JumpPowerMul`, `SpeedGainClassMul`, `StaminaExhaustMul`, `MeleeDamageMul`;
3. NWInts reset in `SetPlayerClass` (`JumpMul`, `RunMul`, `SpeedMul`);
4. class methods such as `Move`, `FallDmgFunc` and `Think`;
5. global hooks such as `HG_MovementCalc_2`, footsteps and input hooks;
6. organism mutations that indirectly change movement.

Cleanup is class-specific and inconsistent. Some `Off` methods restore fields; many are empty.

## Weight and carried-object behavior

Movement derives load from armor/inventory/weapon state and a carried entity. Carried ragdolls/physics objects can contribute mass and alter reach.

The carry path:

- reads model/bone matrices and physics object mass;
- calculates a reach distance from the hands weapon definition;
- clamps player movement and drops the entity when the hand/target distance exceeds a threshold;
- shares state with fake-ragdoll hand control and weapon pickup/use systems.

This path assumes valid matrices, physics objects and `weapon_hands_sh` storage.

## Jump, crouch, slipping and dive behavior

The movement hook owns jump power and may:

- reduce or remove jump based on organism, stance, carry weight and class multipliers;
- swap or distort controls under brain damage/disorientation;
- force crouch behavior while airborne;
- detect fast direction changes/low friction and trigger slipping or fake state;
- apply dive impulses and then enter fake-ragdoll state;
- add view punch and landing effects.

A global `GM.PlayerSpawn` override also mutates `BaseClass.AntiDuckSpam` on every spawn, affecting Sandbox behavior globally rather than only this movement system.

## Inertia and prediction

`hg_inertia` is a replicated/archived convar. When active, current speed approaches target speed instead of immediately matching it; direction input can be rewritten to preserve momentum and acceleration.

### Determinism risks

1. The shared hook uses `SysTime()` deltas stored on each realm; server/client deltas are not guaranteed identical.
2. Client organism/class/weapon state may lag server authority.
3. Player fields are mutated during prediction and can be replayed.
4. Movement commands are rewritten in stages; later stages can use already-modified forward/side values.
5. Custom hooks can mutate multipliers/tables differently by realm or return early.
6. Random/oscillatory effects tied to brain state and ordinary time functions require deterministic review.
7. The hook uses global/current-round/player state beyond the `mv`/`cmd` inputs.
8. Convar replication/order and class-change packets can create one-frame or longer divergence.

## Animation pipeline

`sh_anims.lua` replaces/extends `CalcMainActivity` and `UpdateAnimation` behavior. It selects activities/sequences from:

- movement speed/direction;
- ground/air/crouch state;
- active weapon hold type;
- fake/death/vehicle state;
- class/model sequences;
- custom hooks and gesture state.

It writes pose parameters and animation rates from velocity, including backward/side movement. It depends on model sequence availability and current movement fields.

### Animation risks

- Missing sequences/activities produce model-dependent fallback behavior.
- Animation speed derives from movement state that may differ between realms.
- Global hooks/classes/weapons can override activities without one priority contract.
- Player model/class changes can leave sequence/gesture state from the previous class.
- Fake-ragdoll rendering and smooth get-up write bones independently of normal animation.

## Footstep pipeline

`sh_footsteps.lua` intercepts footsteps and emits custom sounds based on:

- material/surface sound;
- walking/sprinting/crouching state;
- current character (player or fake body);
- organism/class conditions;
- custom `HG_PlayerFootstep` hook responses.

Class files add military, terrorist, Combine/Metrocop, zombie and other footstep layers. Some class hooks return `true` to suppress default handling; others add sounds without a consistent ownership convention.

### Footstep risks

- Server/client emission can duplicate sounds if suppression/realm rules disagree.
- Global `lply`/local-player and organism assumptions appear in client paths.
- Sound-path duration checks and fallback behavior run at event time.
- `PlayerStepSoundTime` behavior is broadly overridden rather than scoped.
- Class hooks remain registered after class exit and must check class strings every event.

## Public hooks and extension stages

Verified movement-related hooks include:

- `SetupMove/homigrad-inertia`;
- staged `HG_MovementCalc*` project hooks, including mode/class consumers such as `HG_MovementCalc_2`;
- `FinishMove/!homigrad-organism`;
- `OnPlayerHitGround` fake/class handling;
- `CalcMainActivity`, `UpdateAnimation` and custom animation hooks;
- `PlayerFootstep`, `PlayerStepSoundTime`, `HG_PlayerFootstep`;
- fake control `CanControlFake` and class `FallDmgFunc` dispatch.

The exact complete stage ordering and all external emitters/consumers remain to be cataloged.

## Verified defects and hazards

1. Global variable leakage: calculations assign generic names such as `k` without `local` in the movement path.
2. Several expressions mix `and`/`or` and nested state without parentheses, making nil access and unintended precedence likely.
3. Limb formula checks are asymmetric and depend on canonical organism fields always existing.
4. Weight/carry code assumes valid bone matrices, physics objects and stored hands weapon metadata.
5. Speed/inertia calculations can divide by target/current speed values and require zero/extreme validation.
6. Input rewriting uses already-mutated movement components in later calculations, which can distort direction.
7. Shared `SetupMove` uses realm-local time, mutable state and hook results, risking prediction mismatch.
8. Engine run speed, Lua multipliers and NW multipliers overlap without one reset/priority model.
9. Movement remains active and authoritative when inertia is disabled, despite the convar name suggesting the subsystem is off.
10. Brain/disorientation logic modifies player inputs directly and must be prediction-deterministic.
11. Fake and ordinary movement ownership is inferred from entity validity and convars rather than an explicit controller state.
12. Dive/slip/fall paths can create fake-ragdoll transitions from predicted/shared movement and server-only physics state.
13. Base Sandbox crouch-spam behavior is mutated globally during player spawn.
14. Animation and footsteps are separate hook systems reading the same mutable movement state without an explicit snapshot.
15. Class hooks remain globally registered and repeatedly branch on class identity rather than being installed/uninstalled transactionally.
16. No per-player diagnostic output explains which modifier produced final speed/jump/input values.

## Required validation

### Prediction and authority

- Log server/client inputs, modifiers and final velocity/max-speed/jump power per command.
- Replay identical commands with inertia on/off, latency, packet loss and class/organism changes.
- Verify prediction rollback does not accumulate player-field state.
- Define authoritative versus presentation-only movement values.

### Modifier matrix

- Every organism injury/drug/stamina/O2/blood state.
- Every class multiplier mechanism and class transition.
- Every weapon stance/hold/resting/speed interface.
- Armor/inventory/carried-object mass and invalid entities.
- Forward/back/side/crouch/walk/sprint/air/noclip/fake/vehicle combinations.

### Transitions

- Fall, slip, dive, fake, unconsciousness, get-up and respawn.
- Class/mode/weapon changes during prediction and movement.
- Missing bones/models/physics objects and external hook failures.

### Performance

- Per-command cost across full player counts.
- Hook consumer count and animation/footstep sound cost.
- Diagnostic breakdown without changing prediction.

## Implementation boundary

Do not rewrite movement independently from organism, fake ragdoll and player classes. The eventual architecture should introduce:

1. an explicit movement-context schema created from authoritative inputs;
2. deterministic ordered modifier phases;
3. one class/mode/weapon modifier registration API;
4. clear ordinary-player versus active-ragdoll controller ownership;
5. fixed/prediction-safe timing;
6. separate authoritative movement, animation and footstep presentation stages;
7. centralized default/reset behavior;
8. instrumentation explaining final speed/jump/inertia decisions;
9. regression fixtures for every modifier and transition.

## Next trace

1. Complete the player-class registry and concrete class matrix.
2. Locate every movement stage hook emitter/consumer and class `Move` invocation.
3. Build the combined organism/fake/movement/class integration graph.
4. Then trace weapon movement and ragdoll interfaces as the next dependency.
