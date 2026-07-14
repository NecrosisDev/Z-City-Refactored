# Trauma Weapon and Combat Assessment

**Status:** Preliminary disposition based on the reproducible Trauma structural inventory and the verified Z-City organism/fake-ragdoll boundaries. File-level semantic adjudication remains blocked until the complete current weapon source graph is enumerated.

## Purpose

This document prevents Trauma's weapon-related work from being treated as a single portable subsystem. It separates the requirements already supported by verified Z-City behavior from concepts that remain unverified or architecturally unsafe.

## Evidence currently available

Verified Z-City documents establish that weapon behavior crosses at least these authority boundaries:

- upright player representation;
- fake-ragdoll representation and ragdoll combat;
- vehicle entry, seated control, camera, and free aim;
- organism damage geometry, penetration, wounds, and death;
- player spawn, round reset, inventory restoration, death, and recovery;
- client input/camera presentation;
- delayed work and representation generations.

The Trauma inventory confirms attempted work in:

- physical bullets;
- weapon-balance schemas and editors;
- fake-ragdoll combat;
- vehicle integration;
- bot behavior and aiming;
- explosives and an explosion manager;
- additional damage, organism, medical, and networking integrations.

These areas are not one lifecycle. They must be reviewed as cooperating owners with explicit contracts.

## Required current-Z-City map before implementation

The next verified source pass must enumerate, by definition and every consumer:

1. weapon classification and capability flags;
2. deploy, holster, switch, drop, pickup, strip, and restore paths;
3. ordinary and fake-ragdoll weapon ownership;
4. primary/secondary attack and reload authority;
5. ADS, free aim, hold type, low/high ready, sprint, and obstruction state;
6. muzzle, eye, barrel, and side-obstruction traces;
7. hitscan, physical bullet, projectile, penetration, ricochet, suppression, and impact effects;
8. ammo ownership and synchronization;
9. death, fake, get-up, vehicle, disconnect, round reset, and map-cleanup behavior;
10. bot/NPC publication and consumption of weapon state;
11. client-only presentation versus server-authoritative fire decisions;
12. hooks, timers, network messages, globals, and mutable SWEP-table writes.

The audit must specifically trace legacy compatibility surfaces already identified in repository work, including `ishgweapon`, `RagdollFunc`, `IsPistolHoldType`, `IsResting`, `ismelee`, and `ismelee2`.

## Preliminary Trauma dispositions

### Weapon balance schema/editor

**Decision: Rewrite from requirements.**

Runtime-editable balance data is useful, but the final design must not irreversibly mutate shared stock SWEP tables or make authored defaults indistinguishable from active overrides.

Required boundary:

- immutable authored definition;
- validated project override layer;
- per-instance resolved values;
- versioned migration;
- server authority;
- explicit client projection;
- rollback to canonical values;
- change diagnostics and acceptance tests.

### Weapon obstruction

**Decision: Deferred pending exact current behavior map.**

Barrel/muzzle and side-obstruction checks are plausible improvements, but obstruction is coupled to ADS, hip fire, ready stance, sprint transitions, vehicle free aim, camera origin, fake-ragdoll weapons, bots, and projectile origin. A local trace replacement can create visual/fire-authority disagreement.

No Trauma obstruction implementation should be ported before the authoritative fire origin and presentation origins are separated.

### Fake-ragdoll combat

**Decision: Rewrite around the explicit character representation state.**

Useful mechanics may be preserved, but weapon ownership must attach to the authoritative representation generation. Delayed fire, reload, drop, pickup, and animation work must be rejected after a newer generation.

The fake system must not become a second weapon authority.

### Vehicle weapon integration

**Decision: Rewrite behind the vehicle adapter boundary.**

Vehicle eligibility, seated pose, free aim, ADS, muzzle origin, obstruction, fire permission, camera, seat switching, exit, and ejection must be adapter capabilities. Core weapon code must remain functional when no supported vehicle addon is loaded.

Bundled vehicle implementations remain rejected.

### Physical bullets and projectiles

**Decision: Deferred pending damage-dispatch mapping.**

The requirement may be valid, but projectile simulation cannot be selected independently of organism penetration, engine damage, impact effects, networking, prediction, lag compensation, and cleanup.

A future projectile service must expose one event-scoped damage context rather than global penetration or inflictor overrides.

### Explosion manager

**Decision: Deferred pending projectile and damage ownership.**

Centralized explosion processing is potentially useful for blast, fragments, effects, sound, suppression, and budgets. It must not become a second damage authority or bypass organism and entity damage contracts.

### Bot and NPC weapon behavior

**Decision: Deferred pending player weapon contract.**

Bots should consume the same bounded weapon capability model as players where behavior is shared. Bot-only muzzle, obstruction, aim, reload, or fire pathways must be justified as adapters rather than silent forks.

### Weapon networking

**Decision: Rewrite.**

Any new weapon messages require owner, direction, schema version, permission, expected representation generation, rate policy, payload limits, and stale-update rejection. Additional messages must not compensate for unclear weapon authority.

## Rejected architecture patterns

The following are rejected regardless of individual feature quality:

- broad detours around unknown weapon bases;
- permanent mutation of global/shared SWEP definitions;
- separate upright, ragdoll, vehicle, and bot fire authorities;
- client-authoritative fire or ammo state;
- fire origin inferred differently by damage and presentation code without an explicit contract;
- anonymous delayed fire/reload/drop work;
- optional addon code bundled into the core weapon subsystem;
- whole-table weapon state replication;
- compatibility guards that silently convert invalid weapon state into no-op behavior.

## Required target boundary

The refined project should converge on:

1. a server-authoritative weapon instance identity;
2. explicit holder and representation generation;
3. immutable authored weapon data plus validated override layers;
4. a capability interface for aim, fire, reload, obstruction, melee, drop, and fake use;
5. one fire transaction carrying origin, direction, weapon instance, holder generation, timing, ammo mutation, and damage context;
6. separate server authority from client camera/animation presentation;
7. owned resources for timers, hooks, projectiles, effects, and cleanup;
8. adapter interfaces for vehicles, bots/NPCs, weapon bases, and optional projectile systems;
9. versioned networking with stale-generation rejection;
10. behavioral fixtures before changing legacy public flags or hook names.

## Acceptance evidence required before a port

At minimum:

- ordinary deploy/fire/reload/holster/drop/pickup;
- fake, get-up, death, respawn, disconnect, and round-reset transitions;
- ADS and hip fire through obstruction, sprint, low/high ready, and vehicles;
- muzzle versus camera-origin agreement;
- melee and pistol classifications;
- physical bullet/projectile cleanup and stale-generation rejection;
- ammo preservation and duplication prevention;
- bot/NPC use of the same capability contract;
- optional addon absence and late availability;
- hot reload without duplicated hooks, timers, receivers, or mutated defaults.

## Current conclusion

Trauma demonstrates valuable weapon-related requirements, but no complete weapon implementation is accepted at this stage. The next source pass must produce the verified current-Z-City weapon graph; only then can individual Trauma files be classified as adopt, adapt, rewrite, reject, or keep current behavior.