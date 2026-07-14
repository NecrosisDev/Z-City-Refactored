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
- `zcity/player-lifecycle.md`
- `zcity/round-and-spectator-networking.md`
- `zcity/organism-lifecycle-and-damage.md`
- `zcity/fake-ragdoll-lifecycle.md`
- `zcity/verified-defects.md`

### Trauma evidence

- `sources/trauma-inventory.md`
- `sources/trauma-lifecycle-assessment.md`
- `data/trauma-snapshot-2026-07-14.json`

### Decisions and migration control

- `comparison-ledger.md`
- `../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`

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
- gamemode-level player spawn, death, spectator, and respawn behavior;
- core round and spectator packet schemas, direction, authority, and late-join risks;
- organism ownership, schema reset, simulation order, damage, incapacitation, replication, and cleanup contracts;
- fake-ragdoll creation, identity, control, recovery, death conversion, vehicles, prediction, and cleanup contracts;
- a specific foundation defect register;
- a structural Trauma inventory with reproducible snapshot identity;
- a deep assessment of Trauma's lifecycle ownership attempt;
- organism- and fake-level dispositions for Trauma medical, networking, ownership, presentation, vehicle, and combat concepts;
- a formal decision that Trauma is evidence rather than baseline;
- concept-level dispositions in the comparison ledger;
- removal of duplicate documentation trees.

## Next behavioral spine

Work should proceed in this order:

1. player-class, movement, inventory, equipment, and mode-specific player lifecycle branches;
2. fake-ragdoll combat and weapon ownership consumers;
3. remaining medical-item and organism packet/NetVar consumers;
4. weapon deploy, input, ADS, obstruction, firing, projectile/bullet, and damage dispatch;
5. map cleanup, shutdown, disconnect, and hot reload;
6. complete network ownership and payload registry beyond the core round/spectator baseline;
7. direct mode-resource inventory;
8. CustomGM requirement extraction;
9. adapter and vendor-boundary inventory.

Production refactoring remains blocked until the relevant compatibility path has acceptance tests.