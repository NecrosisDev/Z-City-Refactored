# Z-City Architecture Research

This directory is the canonical working source of truth for the Z-City refactor.

## Comparison model

1. **Vanilla/current Z-City** defines observed gameplay behavior and compatibility expectations.
2. **Z-City-Refactored** defines the repository baseline and migration constraints.
3. **Trauma** is an experimental implementation whose ideas must be independently verified before adoption.

No Trauma feature is accepted solely because it exists.

## Decision vocabulary

- **Keep Z-City** — existing behavior remains preferred.
- **Adopt** — concept and implementation are suitable with minimal integration work.
- **Adapt** — retain a bounded implementation pattern behind stable project APIs.
- **Rewrite** — retain the requirement while replacing the implementation.
- **Reject** — the concept is harmful, unnecessary, or outside scope.
- **Deferred** — prerequisite behavior or evidence is missing.

## Canonical documents

### Verified Z-City behavior

- `zcity/boot-and-loading.md`
- `zcity/mode-and-round-lifecycle.md`
- `zcity/mode-method-dispatch-and-hot-reload.md`
- `zcity/mode-contract-and-resource-ownership.md`
- `zcity/player-lifecycle.md`
- `zcity/player-class-inventory-equipment-boundary.md`
- `zcity/round-and-spectator-networking.md`
- `zcity/organism-lifecycle-and-damage.md`
- `zcity/fake-ragdoll-lifecycle.md`
- `zcity/weapon-and-combat-interfaces.md`
- `zcity/verified-defects.md`

### Trauma evidence

- `sources/trauma-inventory.md`
- `sources/trauma-lifecycle-assessment.md`
- `sources/trauma-weapon-combat-assessment.md`
- `data/trauma-snapshot-2026-07-14.json`

### Decisions and migration control

- `comparison-ledger.md`
- `../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`
- `../decisions/ADR-0003-EXPLICIT_CHARACTER_REPRESENTATION_STATE.md`

## Required evidence for implementation

A change should not enter the new project without:

- a documented problem or requirement;
- verified current behavior;
- the Trauma approach, when applicable;
- alternatives considered;
- compatibility and regression risks;
- server/client ownership;
- lifecycle and cleanup requirements;
- security and networking effects;
- performance implications;
- acceptance criteria;
- an explicit disposition.

## Current completed scope

The foundation research now includes:

- documentation authority and evidence rules;
- current addon boot/load behavior;
- current mode registration and round lifecycle;
- the loader-level mode method projection, dispatcher replacement, retained-state, partial-load, and hot-reload boundary;
- an explicit mode method-classification, resource-ownership, lifetime, activation, rollback, retained-state, legacy-adapter, and acceptance-test contract;
- gamemode-level player spawn, death, spectator, and respawn behavior;
- the verified orchestration boundary between team assignment, inventory creation, direct spawn placement, round-reset class application, balancing, intermission, and mode equipment grants;
- core round and spectator packet schemas, direction, authority, and late-join risks;
- organism ownership, schema reset, simulation order, damage, incapacitation, replication, and cleanup contracts;
- fake-ragdoll creation, identity, control, recovery, death conversion, vehicles, prediction, and cleanup contracts;
- verified fake-body weapon capability, input, organism, prediction, restoration, and authority interfaces;
- a specific foundation defect register;
- a structural Trauma inventory with reproducible snapshot identity;
- a deep assessment of Trauma's lifecycle ownership attempt;
- a weapon/combat assessment that separates weapon balance, obstruction, ragdoll combat, vehicles, projectiles, explosions, bots, and networking into independent decision areas;
- organism-, fake-, weapon-, character-admission-, and mode-lifecycle-boundary dispositions for Trauma concepts;
- formal decisions that Trauma is evidence rather than baseline and that character representation requires explicit authority;
- concept-level dispositions in the comparison ledger;
- removal of duplicate documentation trees.

## Next behavioral spine

Work should proceed in this order:

1. complete current-Z-City weapon publisher enumeration for `ishgweapon`, `RagdollFunc`, `IsPistolHoldType`, `IsResting`, `ismelee`, and `ismelee2`;
2. apply the new inventory schema to every stock mode-table function, direct caller, matching `hook.Run` emitter, realm, return contract, direct resource, and retained-state owner;
3. enumerate every caller and implementation participating in `SetupTeam`, `CreateInv`, `SetPlayerClass`, mode `GiveEquipment`, `Intermission`, `DontKillPlayer`, `OverrideSpawn`, and `GetTeamSpawn`;
4. complete movement and mode-specific player lifecycle branches;
5. weapon switch, drop, pickup, loadout, ammo, reload, and restoration ownership;
6. ADS, ready stance, obstruction, authoritative fire origin, and vehicle free aim;
7. hitscan, physical bullets, projectiles, penetration, damage dispatch, effects, and explosives;
8. bot/NPC weapon capability publication and consumption;
9. remaining medical-item and organism packet/NetVar consumers;
10. map cleanup, shutdown, disconnect, and hot reload beyond the loader-level baseline;
11. complete network ownership and payload registry beyond the core round/spectator baseline;
12. direct mode-resource, CustomGM requirement, adapter, and vendor-boundary inventories.

Production refactoring remains blocked until the relevant compatibility path has acceptance tests.