# Z-City Refactor Architecture

## Purpose

This directory contains the source evidence, normative standards, subsystem contracts, and decision ledgers used to build the refactor.

## Required reading order

1. `../BUILD_GUIDE.md`
2. `source-baselines.md`
3. `standards/evidence-and-testing.md`
4. `standards/runtime-ownership-and-generations.md`
5. accepted ADRs under `../decisions/`
6. the relevant `zcity/` subsystem documents
7. `comparison-ledger.md` and relevant `sources/` assessment

## Source model

Use exact terms from `source-baselines.md`:

- upstream vanilla snapshot;
- destination baseline;
- working branch;
- current Trauma prototype;
- historical Trauma prototype.

Earlier bare “vanilla/current Z-City” wording is deprecated.

## Canonical documents

### Standards and build control

- `source-baselines.md`
- `standards/evidence-and-testing.md`
- `standards/runtime-ownership-and-generations.md`
- `comparison-ledger.md`

### Z-City baseline, contracts, and upstream evidence

- `zcity/boot-and-loading.md` — destination loader behavior.
- `zcity/boot-content-and-dependency-contract.md` — destination/upstream/Trauma comparison, target contract, requirements, and tests.
- `zcity/mode-and-round-lifecycle.md`
- `zcity/mode-method-dispatch-and-hot-reload.md`
- `zcity/mode-contract-and-resource-ownership.md`
- `zcity/loader-owned-resources-and-mode-chance-persistence.md`
- `zcity/player-lifecycle.md`
- `zcity/player-class-inventory-equipment-boundary.md`
- `zcity/round-and-spectator-networking.md`
- `zcity/organism-lifecycle-and-damage.md`
- `zcity/fake-ragdoll-lifecycle.md`
- `zcity/weapon-and-combat-interfaces.md`
- `zcity/upstream-delta-429ec92-to-3716789.md`
- `zcity/verified-defects.md`

Unless explicitly stated otherwise, the older Z-City documents are source-verified against destination baseline `429ec92`; they do not establish runtime parity.

### Trauma evidence

- `sources/trauma-clean-inventory.md` — current prototype inventory.
- `sources/trauma-mode-lifecycle-comparison.md` — canonical detailed lifecycle comparison.
- `sources/trauma-lifecycle-assessment.md` — earlier deep implementation assessment; revalidate file-level references against Trauma Clean.
- `sources/trauma-weapon-combat-assessment.md` — preliminary weapon-area assessment; exact graph still required.
- `sources/trauma-inventory.md` — historical snapshot pointer only.

### Machine-readable data

- `data/source-snapshots-2026-07-14.json` — current source registry and Trauma delta.
- `data/trauma-snapshot-2026-07-14.json` — historical Trauma snapshot, superseded for implementation guidance.

### Decisions

- `../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../decisions/ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`
- `../decisions/ADR-0003-EXPLICIT_CHARACTER_REPRESENTATION_STATE.md`
- `../decisions/ADR-0004-DECLARED_MODE_CALLABLES_AND_OWNED_RESOURCES.md`

## Current maturity

Completed enough to guide continued analysis:

- boot and realm loading;
- boot/content/dependency target contract with eight requirements and ten acceptance tests;
- mode/round lifecycle and loader boundaries;
- player admission and round-reset orchestration;
- round/spectator networking baseline;
- organism and fake-ragdoll ownership risks;
- fake-body weapon interface risks;
- 27 stable foundation defects;
- Trauma lifecycle and structural dispositions.

Not yet complete enough for broad replacement:

- executable acceptance harness;
- exhaustive boot listener, realm, and lexical-order inventory;
- exact Trauma Clean dependency-bootstrap side-effect trace;
- exhaustive stock-mode method/resource inventory;
- complete weapon publisher/consumer and fire graph;
- complete network registry and trust-boundary matrix;
- medical item and organism packet consumers;
- map cleanup, disconnect, shutdown, and refresh coverage;
- bot/NPC architecture;
- adapter and vendor separation;
- runtime and performance baselines.

## Implementation rule

Research does not need to be globally complete before any code changes. A bounded work package may begin when it satisfies Gates 0–2 in `../BUILD_GUIDE.md` and cannot create a second authority or untestable rollback.

The first implementation phase is observation and low-risk foundation corrections, not a full loader, organism, fake-ragdoll, or weapon rewrite.
