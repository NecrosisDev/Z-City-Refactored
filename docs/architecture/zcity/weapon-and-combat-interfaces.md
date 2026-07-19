# Z-City Weapon and Combat Interfaces

**Status:** Partial, executable-source verified against runtime baseline `429ec928203cec963176dfb6afd086dcdd01c181`. Complete recursive weapon enumeration remains pending because repository code search is currently unavailable.

## Purpose

This document records the weapon-facing contracts already proven to participate in the current character runtime. It does not claim a complete SWEP, ammunition, projectile, armor, explosive, loadout, or networking inventory.

The immediate goal is to preserve known gameplay behavior while replacing implicit cross-system assumptions with explicit capability and lifecycle contracts.

## Verified source boundary

The currently verified source boundary is the server fake-ragdoll controller:

`lua/homigrad/fake/sv_control.lua`

That controller executes every frame for an active fake body, obtains the player's active weapon, interprets legacy weapon fields and methods, consumes player input, and mutates ragdoll physics and organism state.

This is sufficient to prove the interfaces below are live compatibility surfaces. It is not sufficient to identify every publisher.

## 1. Active-ragdoll weapon classification

The controller uses a mixed implicit interface rather than a registered weapon adapter.

| Surface | Observed consumer behavior | Current contract risk |
|---|---|---|
| `ishgweapon(wep)` | Selects firearm posture and input branches | Global classifier definition and complete accepted-base list remain unresolved |
| `wep:IsPistolHoldType()` | Changes torso and arm orientation | Method availability is assumed after classification |
| `wep.IsResting` | Used as a capability-presence check | Field and method identity are conflated |
| `wep:IsResting()` | Selects resting/aim posture | Some branches assume the method remains callable |
| `wep.RagdollFunc` | Suppresses generic arm/grab behavior and is later invoked by the controller | Callback signature, return meaning, mutation ownership, and cleanup are implicit |
| `wep.ismelee` | Selects melee attack/control behavior | Untyped flag overlaps firearm and generic-use classification |
| `wep.ismelee2` | Selects a second melee/control path | Semantics and precedence relative to `ismelee` are undocumented |

These surfaces are public compatibility contracts even when they were not intentionally designed as APIs.

## 2. Validity and type assumptions

Weapon fields and methods are read from the active weapon inside the per-frame fake-body loop. The verified path does not establish a uniform validity/type guard before every access.

Consequences:

- one malformed or partially initialized weapon can break fake-body control;
- hot reload can replace a method while a prior weapon instance remains active;
- weapon removal or switching can occur between related reads and callback execution;
- compatibility guards can silently hide an invalid state rather than identify its publisher.

A future adapter must validate capabilities once per weapon instance/generation rather than scatter conditional checks through body control.

## 3. Input ownership

The fake controller directly consumes player inputs and assigns them to body and weapon behavior.

Observed inputs include:

- `IN_ATTACK`;
- `IN_ATTACK2`;
- `IN_USE`;
- `IN_FORWARD`;
- `IN_BACK`;
- `IN_DUCK`;
- current player view angles.

The same frame can involve:

- firearm posture;
- resting posture;
- weapon-owned `RagdollFunc` behavior;
- generic melee/use behavior;
- arm and torso posing;
- hand-constraint forces;
- stamina use;
- pain feedback;
- wound-driven hand occupation.

Input precedence is therefore gameplay-significant. It cannot be changed safely by replacing only a weapon callback or obstruction trace.

## 4. Organism and movement coupling

Weapon posture and fake-body actions are gated or scaled by mutable organism state.

Known participating state includes:

- body and head movement permission;
- arm injury and dislocation;
- blood and oxygen condition;
- pain and consciousness;
- stamina consumption;
- temporary hand occupation caused by wounds.

The controller owns more than weapon dispatch. It coordinates limbs, constraints, movement power, organism consequences, generic fallback actions, and weapon-specific callbacks in one server-frame transaction.

## 5. Authority and prediction

The verified fake-weapon path is server authoritative. It runs from the server fake-body loop and reads current key state and eye angles directly.

Within the verified boundary, no explicit value was found for:

- input command sequence;
- character representation generation;
- active weapon instance generation;
- callback sequence;
- prediction acknowledgement;
- stale-action rejection.

Client camera, model rendering, and weapon presentation are handled separately. The server action and client presentation therefore lack a documented shared command contract.

## 6. Representation lifecycle

The broader fake-ragdoll baseline establishes that fake entry stores the active weapon and recovery later attempts to preserve/reselect weapon state across a full `Player:Spawn()` call.

The currently verified path does not establish complete preservation of:

- weapon entity identity;
- clip and reserve ammunition;
- chamber state;
- fire mode;
- attachments;
- cooldowns;
- reload phase;
- safety or stance;
- per-instance inventory data;
- constraints and callbacks;
- projectiles and physical bullets;
- recoil and delayed effects.

Recovery can therefore appear successful because the same class is reselected while still losing or duplicating hidden weapon state.

## 7. Required explicit capability boundary

The replacement architecture should define a resolved capability record rather than repeatedly inspect arbitrary fields.

```text
WeaponCapability
  classification: firearm | melee | utility | other
  hold_profile: pistol | long_gun | custom
  resting_query
  fake_body_action
  input_ownership
  allowed_representation_states
  limb_and_hand_requirements
  authority_and_prediction_contract
  switch_and_cleanup_contract
  snapshot_and_restore_contract
```

This is a target contract, not a current API.

## 8. Required fire transaction

A future authoritative fire action should carry one event-scoped context containing at least:

- weapon instance identity;
- holder identity;
- character representation generation;
- command/timing identity;
- authoritative origin and direction;
- presentation origin when different;
- obstruction result;
- ammunition mutation;
- projectile or hitscan selection;
- damage context;
- cleanup ownership.

This prevents camera, muzzle, fake body, vehicle, bot, projectile, and damage code from independently deriving incompatible fire events.

## 9. Verified architectural problems

1. Weapon classification is distributed across a global function, methods, callback fields, and boolean flags.
2. Capability availability is checked inconsistently.
3. A weapon callback runs inside the monolithic body controller without a mutation boundary.
4. Input ownership and precedence are implicit.
5. Organism, movement, constraints, and weapon behavior participate in one unversioned transaction.
6. Server actions and client presentation have no verified shared command/generation contract.
7. Respawn-based recovery preserves only a narrow visible subset of weapon state.
8. Per-frame weapon callbacks have no explicit budget or failure isolation.

## 10. Behavior that must be preserved

Until exact publishers and tests are available, preserve:

- current `ishgweapon` classification outcomes;
- pistol versus long-gun fake posture;
- resting posture behavior;
- weapon-specific `RagdollFunc` behavior;
- `ismelee` and `ismelee2` branch precedence;
- organism restrictions and limb scaling;
- generic grab/use/melee fallbacks;
- server authority for fake-body actions;
- current visible get-up weapon restoration outcomes.

## 11. Trauma comparison

The verified current behavior supports the following dispositions:

### Adopt as requirements

- explicit weapon instance identity;
- holder and character-representation generations;
- lifecycle diagnostics;
- stale-action rejection;
- immutable authored definitions with validated overrides.

### Adapt

- bounded weapon capability metadata;
- obstruction concepts after authoritative origin separation;
- shared player/bot capability queries;
- projectile and explosion budgeting concepts.

### Rewrite

- fake-ragdoll weapon ownership;
- weapon snapshot/restore;
- fire transaction authority;
- vehicle integration;
- weapon networking;
- delayed weapon work and cleanup ownership.

### Reject

- permanent shared-SWEP mutation;
- separate upright/fake/vehicle/bot fire authorities;
- anonymous delayed fire or reload work;
- client-authoritative ammunition or firing;
- whole-table weapon replication;
- optional weapon providers bundled into core code.

## 12. Required runtime tests

1. Standard weapon deploy, fire, reload, holster, switch, drop, and pickup.
2. Fake entry and fake-body attack for every supported weapon category.
3. Weapon switch or removal during `RagdollFunc` execution.
4. Get-up during reload, cooldown, recoil, and delayed effects.
5. Death during fake-body weapon action.
6. Disconnect or map cleanup with active constraints/projectiles/tasks.
7. Pistol, long-gun, melee, and unknown weapon classification parity.
8. Resting-state method absence, failure, and hot reload.
9. Limb loss/injury, unconsciousness, and wound-hand occupation.
10. Muzzle, camera, ragdoll, and damage-origin agreement.
11. Latency and packet-loss comparison of server action versus client presentation.
12. Rejection of stale actions after representation or weapon generation changes.
13. Ammo preservation and duplication prevention across fake/get-up/respawn.
14. Bot/NPC consumption of the same capability contract.
15. Optional integration absent, loaded at boot, and loaded after startup.
16. Hot reload without duplicated callbacks, timers, projectiles, or mutated defaults.

## 13. Exact continuation

The next source-enumeration pass must still identify every definition and publisher of:

- `ishgweapon`;
- `RagdollFunc`;
- `IsPistolHoldType`;
- `IsResting`;
- `ismelee`;
- `ismelee2`.

It must then trace switch, drop, pickup, death, fake, get-up, loadout, ammo, reload, projectile, physical-bullet, damage, vehicle, bot, networking, disconnect, and cleanup ownership.

Negative repository-wide claims remain prohibited until recursive source enumeration succeeds.