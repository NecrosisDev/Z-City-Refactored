# Weapon and Combat Interface Trace

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

## Purpose

This document records the weapon-facing contracts already consumed by the character runtime before weapon implementations are enumerated. It does not yet claim a complete SWEP, ammunition, physical-bullet, armor, explosive, or loadout inventory.

## Verified source boundary

The initial trace is grounded in `lua/homigrad/fake/sv_control.lua` blob `22c87ad4148716ff1173c104e7df943043b09ce5`, which is a server-only, every-frame consumer of the active weapon while a player owns a fake ragdoll.

## Active-ragdoll weapon contract

The fake controller obtains `ply:GetActiveWeapon()` and branches on a mixed implicit interface rather than one registered adapter.

| Surface | Consumer behavior | Contract/risk |
|---|---|---|
| `ishgweapon(wep)` | selects firearm posture and input branches | global classifier definition and accepted bases remain unresolved |
| `wep:IsPistolHoldType()` | changes torso/arm orientation | called after `ishgweapon`; method availability is assumed for classified weapons |
| `wep.IsResting` and `wep:IsResting()` | enters resting/aim posture | field existence is checked in one branch, but other calls assume method availability |
| `wep.RagdollFunc` | suppresses generic arm/grab handling when present; invoked later by the controller | callback signature, return semantics, mutation ownership, and complete publisher list remain unresolved |
| `wep.ismelee` / `wep.ismelee2` | selects attack/use arm-control branches | untyped ad-hoc capability flags overlap firearm classification |
| active-weapon validity | weapon fields are read during the per-frame body loop | no uniform `IsValid(wep)` guard precedes all field/method access |

## Input ownership

The fake controller directly maps player input to body and weapon behavior:

- `IN_ATTACK`, `IN_ATTACK2`, and `IN_USE` select arm posing, generic melee/use behavior, firearm resting posture, or weapon-owned ragdoll behavior;
- `IN_FORWARD` and `IN_BACK` apply forces through active hand constraints and feed organism pain/stamina;
- `IN_DUCK` changes torso/head posture;
- view angles drive head, torso, and weapon orientation;
- ragdoll-combat mode can force the same control path even without an ordinary weapon action.

This means the active weapon, fake-body controller, organism simulation, input state, and constraints participate in one server-frame transaction without an explicit command context or rollback boundary.

## Organism and movement coupling

Weapon posture and fake actions are gated or scaled by mutable organism state:

- `canmove` and `canmovehead` gate torso/head/arm control;
- arm injury/dislocation modifies force and adds pain;
- blood, oxygen, pain, and consciousness determine ragdoll control power;
- hand-force movement writes stamina consumption;
- wound location can temporarily occupy hands and suppress attack inputs.

The fake controller therefore does not merely call a weapon callback. It owns generic weapon posture, limb authority, hand constraints, stamina/pain feedback, and fallback melee/use behavior around that callback.

## Prediction and networking boundary

The verified active-ragdoll weapon path is server authoritative and executes from the server `Think/Fake` loop. It reads current key state and eye angles directly rather than a versioned/predicted weapon command. Client presentation is handled separately by fake render/camera code and weapon world rendering. No sequence number, body generation, command number, or callback result replication was found in this bounded source.

Required runtime evidence:

1. record command number, active weapon class, body generation, input bits, view angles, callback selected, and resulting forces/state;
2. compare server weapon action with client animation/render timing under latency and packet loss;
3. verify stale callbacks cannot act on an old fake body after weapon switch, get-up, death, disconnect, or entity removal;
4. measure per-frame callback cost and enforce a weapon/body budget.

## Lifecycle and restoration boundary

`hg.Fake` stores the active weapon and `hg.FakeUp` preserves/restores a selected active weapon around `ply:Spawn()`, but the current trace does not establish complete preservation of:

- weapon instances and per-instance state;
- clips, reserve ammunition, chamber state, fire mode, attachments, cooldowns, reload state, safety/stance, or carried inventory;
- callbacks, constraints, projectiles, timers, recoil, or pending physical bullets;
- class/mode-granted loadout ownership and duplicate-grant prevention.

The respawn-based get-up path therefore remains a high-risk weapon transaction even when the same active class is reselected.

## Public integration surface

The current minimum compatibility adapter for a weapon consumed by fake control must explicitly define:

```text
WeaponCapability
  classification: firearm / melee / other
  hold-profile: pistol / long gun / custom
  resting-state query
  fake-body action callback
  input ownership and allowed states
  limb/hand requirements
  server authority and prediction contract
  cleanup on switch/get-up/death/disconnect
  state snapshot/restore contract
```

These are planned architectural requirements, not current implemented APIs.

## Verified risks

1. Implicit capability detection through globals, methods, fields, and flags can classify the same weapon inconsistently.
2. Missing validity/type guards can break the entire per-frame fake loop for one weapon.
3. A weapon callback executes inside the monolithic body controller and can mutate body, organism, constraints, projectiles, or global state without ownership limits.
4. Input is shared among generic grab/use/melee/firearm posture and weapon-specific logic, so precedence changes can silently alter gameplay.
5. Respawn-based get-up restores only a narrow visible subset of weapon state.
6. Server-frame weapon actions and client render/camera state have no verified command/body generation contract.
7. Per-frame weapon callbacks add unbudgeted cost to the existing fake physics loop.

## Exact continuation

1. Enumerate the definition and all uses of `ishgweapon`.
2. Enumerate every `RagdollFunc`, `IsPistolHoldType`, `IsResting`, `ismelee`, and `ismelee2` publisher across engine-loaded SWEPs and global addon files.
3. Trace weapon switch, drop, pickup, death, fake, get-up, class/mode loadout, ammo, reload, projectile, physical-bullet, and cleanup ownership.
4. Pair weapon server actions with client rendering, animation, camera, recoil, sound, and networking.
5. Extend the CharacterRuntime graph and public-surface inventory only after exact source enumeration; preserve unresolved negative claims while recursive tree access remains unavailable.
