# Weapon and Ballistics System Architecture

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** firearm base, predicted firing, reload, attachment, inventory, fake-ragdoll integration, and physical-bullet core are executable-source verified; every concrete weapon, ammunition entity, armor interaction, explosive, and one-sided packet branch is not yet exhaustive  
**Reviewed:** 2026-07-12

## Purpose

The weapon runtime is split between two large authorities:

1. `lua/weapons/homigrad_base/**` owns firearm/SWEP state, input, aiming, recoil, reload, magazines, attachments, customization, inventory, animation, prediction, replication, fake-ragdoll weapon control, view/world rendering, and concrete-weapon extension points.
2. `lua/homigrad/sh_luabullets.lua` owns projectile objects, simulation, traces, penetration, ricochet, gravity, suppression/tracers, damage dispatch, PVS replication, and client prediction/reconciliation.

The systems are tightly coupled to organism damage, fake-ragdoll physics, movement, player classes, inventory, armor, ammunition entities, NPCs, modes, camera/rendering, and effects. They cannot be refactored as an isolated SWEP base.

## Source topology

### Firearm framework

| File/area | Verified responsibility |
|---|---|
| `homigrad_base/shared.lua` | base SWEP registration, defaults, network vars, shared includes, helper classification such as `ishgweapon` |
| `sh_bullet.lua` | primary attack, fire validation, clip consumption, recoil/effects, predicted fire request, ballistic payload construction |
| `sh_recoil.lua` | recoil state and view/body reaction |
| `sh_reload.lua`, `sv_reload.lua` | reload state machine, magazine handling, interruption, dropped-magazine entities and ammo transfer |
| `sh_attachment.lua`, `sh_attachment_world.lua` | attachment slots, model/state lookup, modifiers, dropped attachments and rendering |
| `sh_ammo.lua` | cartridge/magazine/ammo metadata and weapon ammo state |
| `sh_weaponsInv.lua`, `sh_inventory.lua` | holstering/stowing/pickup state and inventory integration |
| `sh_fake.lua`, `cl_ragdoll.lua` | fake-ragdoll hand poses, physical weapon control, world model and ragdoll combat behavior |
| `sh_replicate.lua`, `sv_replicate.lua` | generic weapon event replication/replay helpers |
| `sh_customize.lua` | customization state and client/server interaction |
| input/aim/use/view-model/animation files | aiming/resting/safety/hold type, input state, use/drop, TPIK/view/world animation and camera integration |

### Ballistics and ammunition

| File/area | Verified responsibility |
|---|---|
| `lua/homigrad/sh_luabullets.lua` | `ENTITY:FireLuaBullets`, global projectile registry/IDs, server/client simulation, trace/penetration/ricochet/damage, ballistic networking |
| `lua/homigrad/ammostuff/**` | ammunition drop/pickup/entity transfer and ammo-related transport; full client/server matrix remains incomplete |
| `organism/tier_1/sv_input.lua` | consumes ballistic diameter/penetration/damage/force/ammo properties and resolves organ/body injury |
| concrete weapon files | configure cartridge, velocity, penetration, diameter, spread, recoil, magazine, attachments and special callbacks |
| explosives/modes/NPCs | call `FireLuaBullets` directly for shrapnel, sniper enforcement, AI fire and other non-SWEP projectiles |

## Firearm base state

The base defines or assumes broad mutable state across SWEP fields, network variables, owner fields, animation state, attachment tables, magazine/ammo tables, fake-ragdoll state, and client prediction data.

Representative groups include:

- identity and models: class, world/view models, hold type, hand/body offsets;
- fire: clip, chamber/cartridge, fire mode, next attack, safety, underwater restrictions, seed, spread, muzzle and sound state;
- recoil/aim: recoil accumulators, aiming/resting/ready state, view/body recoil, sway and camera offsets;
- reload: staged reload timers, magazine state, chamber state, interrupted reload and dropped magazine references;
- attachments: slots, installed IDs, modifier tables, attachment entities/models and customization state;
- inventory/use: stowed/active/dropped ownership, pickup cooldown and inventory references;
- fake-ragdoll: physical body, hand/weapon constraints, poses, ragdoll callback and world render state;
- replication: event IDs, predicted/replayed state, network-var ownership and client effect state.

There is no single generated weapon-state schema. Concrete weapons and attachment definitions add arbitrary fields and callbacks.

## Fire request and prediction

`SWEP:PrimaryAttack` performs broad shared validation and predicted effects, including:

- owner/weapon validity and active ownership;
- safety, reload and cooldown state;
- underwater and movement/organism constraints;
- clip/ammo/chamber availability;
- recoil, sound, animation and muzzle effects;
- construction of a Lua-bullet payload passed to `owner:FireLuaBullets`.

### `hgwep shoot`

The channel is used in both directions.

**Client -> server verified fields:**

1. weapon entity;
2. signed 32-bit random/prediction seed.

The server verifies that the weapon belongs to the sender and checks the seed against the expected shared random state/tolerance before invoking `PrimaryAttack(true, seed)`. If the authoritative fire state changes, it broadcasts the weapon to relevant clients for remote effects/replay.

**Server -> client:** the verified branch identifies the weapon and replays remote firing/effects through the shared attack path. Exact conditional effect fields beyond the weapon identity remain source-range dependent and must be packet-captured before migration.

### Prediction risks

1. The client initiates an authoritative action with a seed and local predicted state rather than sending a bounded intent independent of simulation internals.
2. Fire validation is distributed across shared code, owner/organism state, reload state, weapon fields and server receiver checks.
3. Client/server random state, command prediction and mutable weapon fields must remain synchronized.
4. Replayed `PrimaryAttack(true, seed)` can execute shared side effects unless every effect branch is correctly realm/prediction gated.
5. The server trusts the weapon entity reference after ownership checks but still depends on its class/state being fully initialized.
6. Concrete weapons can override attack/fire callbacks and weaken base validation.
7. Fire rate and replay protection depend on mutable next-fire state rather than a stable shot sequence number.
8. No versioned shot-intent protocol exists.

## Ballistic payload contract

`FireLuaBullets` accepts a mutable table with fields such as:

- `Attacker`, `Inflictor`;
- `Src`, `Dir`, `Spread`, `Num`;
- `Damage`, `Force`, `Distance`;
- velocity/speed and gravity behavior;
- `AmmoType`, `Tracer` and tracer/effect settings;
- `Penetration`, `Diameter`, ricochet/penetration counters and limits;
- damage type and lag-compensation options;
- filters, callbacks and state used by continuation/reconciliation.

Concrete weapons, NPCs, modes and explosives do not necessarily populate the same subset. The function normalizes/defaults the table and adds runtime projectile identity/state.

This table is a de facto public API. Field names, units and default behavior are not defined by an explicit schema or version.

## Physical-bullet lifecycle

`ENTITY:FireLuaBullets(bullet, bullet_but)` broadly:

1. validates/normalizes the ballistic table;
2. assigns a global bullet ID and stores a projectile object in `hg.luabullets`;
3. derives direction/spread, initial velocity, distance, attacker/inflictor, damage and penetration state;
4. simulates projectile movement over time on server and client;
5. traces the segment, resolves world/entity hit, material response, penetration and ricochet;
6. emits tracers/suppression/impact effects;
7. applies server-authoritative damage and passes ballistic metadata to the organism pipeline;
8. can continue the projectile from an exit point with reduced energy/penetration state;
9. removes or reconciles the projectile at termination.

### Ballistic networking

The shared file registers `hg luabullets`, `hg luabullets 2`, and `hg luabullets 3`. Verified source establishes separate initialization/reconciliation/update/removal branches and selected-table replication to relevant clients, but the exact ordered field schema for every conditional branch remains incomplete due to the large shared source and must not be inferred from registration names.

The server writes selected ballistic values through project table-network helpers rather than sending arbitrary callbacks/functions. Clients reconcile predicted bullets through IDs and weapon bullet state.

Until every branch is line-paired, these channels are classified as `partial/overloaded ballistic state`, not as three fully documented stable protocols.

### Ballistic risks

1. Global bullet IDs and mutable registries exist independently on server and clients.
2. Prediction/reconciliation depends on IDs, weapon state and transport ordering without a documented generation/epoch.
3. Projectiles are simulated in both realms using local frame/tick timing.
4. Ballistic tables are mutable and reused for penetration/continued shots.
5. Attacker, inflictor, filter entities and callbacks can become invalid during flight.
6. Penetration and ricochet can loop through multiple traces/materials/entities per projectile.
7. Organism damage can fire nested damage/bullet behavior while global penetration overrides and mutable tables are active.
8. PVS replication and tracer/effect work scale with projectiles and observers.
9. Concrete weapons, NPCs and explosives can supply malformed or extreme velocity, penetration, diameter, damage, spread or distance values.
10. World geometry/material assumptions and zero-length/extreme vectors require deterministic guards.
11. Client prediction can expose authoritative-looking visual hits that the server rejects or resolves differently.
12. No projectile simulation budget, maximum active count, or graceful degradation policy is documented.

## Organism damage integration

The ballistic engine ultimately feeds `EntityTakeDamage/homigrad-damage` with weapon/ammunition metadata. The organism pipeline reads penetration, diameter, damage, force, ammo type, ricochet state and inflictor-specific modifiers to trace custom organ OBBs, create wounds and continue bullets.

This creates a feedback chain:

```text
weapon PrimaryAttack
  -> FireLuaBullets projectile
  -> world/entity trace
  -> organism custom penetration and organ damage
  -> optional exit wound / continued projectile
  -> physical effects, wounds and replication
```

The ballistic and organism penetration models must be tested as one system. Refactoring either side independently risks double penetration, incorrect energy loss, duplicate damage, or broken wound entry/exit state.

## Reload and magazine lifecycle

Reload is a staged state machine shared across server/client weapon code, with server-only physical magazine/ammunition operations.

Verified responsibilities include:

- start/cancel/finish reload state;
- chamber and magazine transitions;
- animation/timer sequencing;
- tactical versus empty reload behavior;
- magazine/ammo data transfer;
- dropped magazine entity creation;
- interruption by fake, weapon switch, attack, invalid ownership or other state;
- replicated reload-stop/effect notifications.

### `hgwep reload`

The server sends the relevant owner/entity state when authoritative reload stops or changes. Shared/client code consumes the channel to synchronize local reload animation/state. The exact conditional schema beyond the verified entity reference remains to be packet-captured and is intentionally not generalized.

### Reload hazards

1. Timers and state are spread across shared/server files and weapon fields.
2. Reload can be executed/predicted in both realms, requiring side-effect gating.
3. Magazine entities and ammo transfer can duplicate or lose rounds under interruption, owner change, fake/get-up, death or weapon removal.
4. Dropped entities are created and configured without one transactional inventory/ammo operation.
5. Concrete weapons can override capacity/chamber/reload timing and animation assumptions.
6. Reload state can conflict with attachments, customization and fake-ragdoll control.
7. Owner/weapon validity is not uniformly guarded in delayed callbacks.
8. No explicit magazine unique ID or transfer ledger prevents replay/duplication.

## Attachments and customization

Attachments are table-driven and can change models, slots, weapon properties, ballistic values, recoil, sights, sound, handling and rendering.

The base owns:

- slot definitions and installed attachment IDs;
- lookup/validation and model creation;
- attachment modifier application;
- world/view/fake-ragdoll rendering;
- dropping/removing attachments;
- customization UI/state and client/server transport.

Verified channels include `hgwep att drop` and `hgwep customize`. Endpoint owners are located, but every conditional field/table branch is not yet fully paired; they remain explicit partial trust boundaries.

### Attachment/customization risks

1. Attachment IDs and slot compatibility are public identifiers with no versioned registry.
2. TDM purchase already demonstrates arbitrary client attachment IDs reaching force-apply code outside this base.
3. Modifier application mutates weapon fields and can stack or fail to restore defaults.
4. Attachment models/entities require cleanup across weapon removal, inventory, fake, death and hotload.
5. Client customization state can request server mutation; exact authorization, ownership, phase, rate and size checks must be line-audited.
6. Concrete weapons can define incompatible slot layouts or assume required attachments.
7. World/view/ragdoll render paths must agree on installed state.
8. Dropped attachments cross weapon, inventory, entity and persistence boundaries without one transaction.

## Weapon inventory/use integration

`sh_weaponsInv.lua` and related files let weapons move between active world/SWEP state and project inventory/holster state.

Verified channels:

- `hgwep inv`;
- `hgwep inv pickup`.

Client requests include weapon entity references; the server verifies ownership/current state before toggling or picking up. The server then replicates resulting inventory/effect state.

### Inventory/use risks

1. Entity-reference authorization must remain server-side and include distance, alive/fake/dead state and ownership generation.
2. Weapon entity can be removed or transferred during request processing.
3. Inventory state, active weapon, fake-ragdoll held weapon and world model can disagree.
4. Class/mode equipment grants and round reset can race stow/pickup operations.
5. Ammo/magazine/attachment state must move atomically with the weapon.
6. The transport lacks an explicit transaction ID or expected prior state.

## Fake-ragdoll weapon integration

`sh_fake.lua` and related rendering/control files make firearms usable or physically represented while the owner is fake.

The system can:

- position the weapon against ragdoll hands/body;
- drive one/two-hand physics and pose state;
- invoke weapon-specific `RagdollFunc` from the fake controller;
- preserve/restore active weapon through fake/get-up;
- render attachments, magazines and world models on the ragdoll;
- apply recoil/forces to body/weapon physics;
- allow pickup/use/drop interactions from fake controls.

### Fake-weapon risks

1. Active weapon, fake body, hand physics, constraints and organism state can become invalid independently.
2. Per-frame weapon callbacks execute inside the already expensive fake control loop.
3. Weapon-specific callbacks are not declared through one capability/interface registry.
4. Standing and fake firing share SWEP state/prediction but have different muzzle/source/owner physics.
5. Get-up respawns the player and restores only selected active-weapon state.
6. Dropped/stowed/held weapon identity can conflict with inventory and death cleanup.
7. Model/bone/attachment assumptions are ValveBiped and weapon-specific.

## Generic weapon event replication

`sh_replicate.lua`/`sv_replicate.lua` provide generic event-call/replay helpers for weapon behavior. These utilities serialize event identity and arguments/state, then invoke weapon methods remotely.

This is a broad extension surface: adding or renaming weapon event methods changes network-visible behavior even when no dedicated channel is added.

Risks:

- event names/methods are implicit public identifiers;
- argument schemas are not centrally registered/versioned;
- replay can execute methods with side effects unless realm-gated;
- weapon entity ownership/lifetime and event ordering are mutable;
- generic replication can bypass the validation rigor of dedicated endpoints.

## Other verified weapon channels

The weapon base registers or consumes additional channels including:

- `hgwep angle`;
- `hgwep dwr sound`;
- generic replicated-event channels in `sh_replicate.lua`;
- reload/inventory/attachment/customization/fire channels described above.

Some are one-sided or branch-heavy in current evidence. They remain listed as unresolved packet rows until both writer and reader schemas are line-paired.

## Concrete weapon inheritance surface

Concrete firearms inherit from `homigrad` and commonly configure:

- models, hold type and offsets;
- cartridge/ammo type, velocity, damage, penetration and diameter;
- clip/magazine/chamber behavior;
- fire modes, fire rate, spread and recoil;
- sights and attachment slots;
- sound/muzzle/tracer/effects;
- animation and fake-ragdoll behavior;
- special callbacks for fire, reload, damage or projectiles.

A complete concrete-weapon manifest remains required. The base cannot be stabilized without verifying every override/capability used by shipped weapons.

## Ammunition entities and transfer

`lua/homigrad/ammostuff/**` owns project ammo drop/pickup/entity behavior outside ordinary engine ammo counts. Server code creates/transfers ammo entities and uses network channels for client presentation/interaction. The exact full endpoint/schema matrix remains a current trace item.

Ammunition ownership overlaps:

- engine ammo counts;
- weapon clip/chamber/magazine state;
- dropped magazine entities;
- inventory templates/items;
- loot tables and mode equipment;
- physical bullet `AmmoType` metadata.

No single ammo ledger currently guarantees conservation across reload, drop, pickup, death, inventory and round cleanup.

## Public APIs and hooks

### Firearm APIs

- `ishgweapon(entity)` and weapon-base identification helpers;
- `SWEP:PrimaryAttack`, `FireBullet`, reload and attachment methods;
- inventory/stow/pickup methods;
- attachment lookup/apply/drop/customization APIs;
- fake-ragdoll pose/control/render callbacks;
- generic event replication methods.

### Ballistic APIs

- `ENTITY:FireLuaBullets(bullet, bullet_but)`;
- global `hg.luabullets` registry and projectile IDs;
- ballistic trace/penetration/ricochet helpers;
- project table-network helpers used for bullet state;
- damage/effect callbacks and continued-projectile behavior.

### Hooks/integration points

- weapon/owner input and movement hooks;
- fake `RagdollFunc` and render hooks;
- organism `PreHomigradDamage`/`HomigradDamage` and wound callbacks;
- muzzle/tracer/impact/suppression/effect hooks;
- inventory, attachment, reload and weapon event hooks;
- mode/class equipment and restrictions.

## Highest-impact verified defects and risks

1. Client-seeded predicted firing is coupled to mutable shared random/weapon state and method replay.
2. No stable shot sequence/generation protocol.
3. Physical bullet packet branches are implicit and only partially line-paired.
4. Ballistic simulation runs on both realms with mutable tables and local timing.
5. No global projectile count/work budget or degradation policy.
6. Ballistic and organism penetration are separate coupled models with reentrant/global-state hazards.
7. Reload/ammo/magazine transfer is not transactional and has no conservation ledger.
8. Attachments mutate weapon fields without a generated defaults/rollback schema.
9. Customization/attachment/inventory endpoints require complete ownership/phase/rate/size auditing.
10. Generic event replication exposes method names/arguments without a central schema.
11. Fake-ragdoll weapon callbacks add per-frame physics and validity dependencies.
12. Standing/fake/world/inventory weapon identities can diverge during transitions.
13. Concrete weapon overrides can bypass base validation or assume unavailable fields.
14. One-sided angle/sound/effect channels remain unresolved.
15. Ammo state is split among engine counts, clip/chamber, magazines, inventory and entities.
16. PVS/tracer/suppression/effect work scales with projectiles and observers.
17. Invalid attacker/inflictor/filter/weapon entities can persist across projectile flight.
18. Extreme/invalid ballistic numbers can produce excessive traces, damage, force or lifetime.

## Required validation

### Fire and prediction

- Log client intent, server acceptance, seed, shot ID, clip/chamber, next-fire and effect replay.
- Test latency, loss, duplicate/reordered requests, prediction rollback and rapid weapon switching.
- Fuzz invalid weapon entities, owner mismatch, seed extremes, cooldown and dead/fake/incapacitated states.
- Verify every concrete weapon override preserves server authority.

### Ballistics

- Deterministic trajectory/penetration/ricochet fixtures across materials, entities and organs.
- Zero/extreme/NaN velocity, spread, distance, penetration, diameter, damage and force.
- Attacker/inflictor/filter removal during flight.
- Reentrant damage and continued projectile behavior.
- Population tests for active bullets, PVS clients, tracers and effects.
- Packet capture for all three `hg luabullets*` channels and prediction reconciliation.

### Reload/ammo/inventory

- Ammo conservation across tactical/empty reload, interruption, fake/get-up, drop/pickup, death, class/mode switch and cleanup.
- Duplicate/replay/disconnect tests for magazine and inventory operations.
- Invalid/removed entity and missing ammo metadata.

### Attachments/customization

- Every weapon/slot/attachment compatibility combination.
- Server-side ID/ownership/phase/rate/table bounds.
- Modifier rollback and model/entity cleanup.
- Realm render/state parity in standing, fake and inventory states.

### Integration

- Organism penetration/wounds and armor.
- Movement/aim/recoil/stamina.
- Fake-ragdoll muzzle/hand/weapon physics.
- NPC/mode/explosive direct `FireLuaBullets` callers.
- Class/round equipment and inventory transitions.

## Planned architectural boundaries

These are `Planned`, not implemented changes.

1. `WeaponDefinition`: immutable concrete weapon/ammo/attachment capabilities and defaults.
2. `WeaponRuntime`: per-entity authoritative state with explicit sequence numbers.
3. `FireIntent`: bounded client request independent of random/internal state.
4. `ShotRecord`: server-issued shot ID, muzzle, seed, cartridge and authoritative outcome references.
5. `BallisticProjectile`: validated schema and fixed/budgeted simulation.
6. `MagazineLedger`: atomic ammo/magazine/entity/inventory transfer.
7. `AttachmentRuntime`: explicit slot compatibility and reversible modifiers.
8. `WeaponBodyAdapter`: standing/fake/world/inventory representation and ownership generation.
9. Versioned packet schemas and dedicated event IDs instead of generic method replay.
10. Instrumentation and budgets for shots, traces, penetration, PVS and effects.

## Next trace

1. Pair every weapon and `hg luabullets*` packet branch exactly.
2. Enumerate concrete weapons and override/capability differences.
3. Complete ammunition drop/pickup and conservation ownership.
4. Trace armor and physical-bullet/organism penetration integration.
5. Trace explosives and shrapnel direct callers.
6. Update the character-runtime graph with weapon-body and movement interfaces.
