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

The first foundation pass now includes:

- documentation authority and evidence rules;
- current addon boot/load behavior;
- current mode registration and round lifecycle;
- a specific foundation defect register;
- a structural Trauma inventory with reproducible snapshot identity;
- a deep assessment of Trauma's lifecycle ownership attempt;
- a formal decision that Trauma is evidence rather than baseline;
- initial concept-level dispositions in the comparison ledger;
- removal of duplicate documentation trees.

## Next behavioral spine

Work should proceed in this order:

1. player initial spawn, spawn selection, round reset, death, fake death, spectating, and respawn;
2. organism initialization, damage, incapacitation, clearing, and death;
3. weapon deploy, input, ADS, obstruction, firing, projectile/bullet, and damage dispatch;
4. map cleanup, shutdown, disconnect, and hot reload;
5. network ownership and payload registry;
6. direct mode-resource inventory;
7. CustomGM requirement extraction;
8. adapter and vendor-boundary inventory.

Production refactoring remains blocked until the relevant compatibility path has acceptance tests.
