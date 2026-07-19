# Boot, Content, and Dependency Contract

- **Status:** SOURCE-VERIFIED comparison; runtime fixtures not yet executed
- **Destination baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Upstream vanilla snapshot:** `3716789311f726174e1255f8b93fe1b28e619f6d`
- **Current Trauma prototype:** `Trauma_Clean.zip` (`03d6b1b917ebd33ba0a472dbc7ecf09118eb743aaadbbdd8dab1505476dc13f8`)
- **Realm:** server bootstrap with shared/client distribution effects
- **Last reviewed:** 2026-07-14
- **Exhaustive search:** complete for the recorded destination/upstream loader delta; structural only for Trauma Clean dependency attempts
- **Runtime status:** not tested

## Purpose

This document defines the smallest justified boot/content/dependency contract that may enter the refactor. It separates verified vanilla behavior from Trauma attempts and prevents a third bootstrap implementation from being introduced without ownership, failure, and rollback rules.

## Verified destination behavior

At the destination baseline, `lua/autorun/loader.lua`:

1. creates the legacy `hg` namespace and upstream identity metadata;
2. creates the replicated, enabled-by-default `hg_loadcontent` ConVar;
3. contains five guarded `resource.AddWorkshop` calls, but all five are commented out;
4. recursively includes the `homigrad` tree using filename-derived realms;
5. sets `hg.loaded`, emits `HomigradRun`, and later loads `initpost` files;
6. prints repeated ULX/ULib warnings after a delay when the dependency is absent;
7. has no declared module manifest, capability registry, transactional rollback, or structured dependency report.

Therefore, the destination setting claims to control content while producing no Workshop registrations.

## Verified later upstream behavior

Upstream vanilla commit `3716789` re-enables the same five Workshop registrations:

- `3657285193`;
- `3657897364`;
- `3657294321`;
- `3544105055`;
- `3257937532`.

This repairs the immediate destination mismatch but does not establish final architecture. The IDs remain embedded in the loader, dependency ownership is not declared, and the loader still cannot report which gameplay capabilities are unavailable when content is missing.

**Disposition:** preserve as a vanilla compatibility fixture only. Do not blindly cherry-pick as the project content system.

## Trauma Clean attempts

Structural inventory of Trauma Clean identifies:

- a newly added `lua/autorun/00_trauma_dependencies.lua`;
- additional compatibility and restoration autoruns;
- project identity, disk logging, dependency checks, feature controls, live-test guidance, and broad readiness reporting;
- multiple autoruns/loaders that can overlap in authority;
- dependency and vendor code mixed with project behavior;
- optional Glide, vFire, DynaBase/wOS, VJ, and Pathowogen integrations.

The current archive contains 1,035 Lua files, 240 server ConVar creation calls, 121 client ConVar creation calls, and 207 console command registrations. These lexical counts establish review scale, not runtime correctness.

The exact semantics and all call sites of `00_trauma_dependencies.lua` have not yet been re-traced against the clean archive. Trauma documentation remains claimed evidence.

**Disposition:** adapt the requirements for capability detection and actionable reporting; rewrite implementation. Reject multiple competing boot authorities, hash-pinned silent fallbacks, and bundled vendor code as the dependency model.

## Target authority

One project-owned bootstrap service is authoritative for:

- immutable project identity;
- module manifest loading;
- explicit realm declarations;
- required and optional capability detection;
- content manifest selection;
- initialization phase state;
- structured health and dependency reports;
- compatibility publication through `hg.loaded` and `HomigradRun`.

Legacy loader surfaces remain compatibility projections until their consumers are inventoried. They must not independently load a second module graph.

## Dependency classes

| Class | Missing behavior | Example |
|---|---|---|
| Required foundation | Abort the affected initialization phase and report one actionable error | core manifest or ownership service |
| Required feature capability | Disable the feature explicitly; do not partially activate it | a mandatory asset pack for an enabled mode |
| Optional adapter | Remain inert and report unavailable capability | Glide, VJ Base, StormFox, GAS |
| Administrative integration | Preserve gameplay; disable only administration extension | ULX/ULib-backed commands |
| Development tooling | Never affect release gameplay authority | live-test guides and probes |

A provider may satisfy a capability without becoming the project authority. Capability detection must not mutate vendor internals.

## Content-manifest rules

1. Workshop IDs are data, not loader control flow.
2. Each entry declares purpose, requirement class, affected capabilities, and source authority.
3. The compatibility manifest may reproduce the five upstream vanilla IDs exactly.
4. A consolidated project Workshop package may supersede individual IDs only through an explicit manifest revision.
5. Duplicate registrations are deduplicated before `resource.AddWorkshop` is called.
6. Disabling content loading produces zero Workshop registrations from this project.
7. Missing optional content does not block unrelated systems.
8. Missing required content fails closed for the affected feature and reports the exact remediation.

## Initialization phases

The target bootstrap uses explicit phases:

1. identity and compatibility namespace;
2. manifest and schema validation;
3. foundation services;
4. shared gameplay services;
5. realm-specific modules;
6. optional adapter discovery;
7. post-entity modules;
8. health publication and compatibility completion hooks.

Every phase records `not_started`, `preparing`, `active`, `failed`, or `rolled_back`. Required-phase failure prevents later dependent phases from reporting active.

## Requirements

| ID | Requirement |
|---|---|
| `ZC-REQ-BOOT-001` | The project shall expose one authoritative bootstrap phase state while preserving `hg.loaded` and `HomigradRun` as compatibility projections. |
| `ZC-REQ-BOOT-002` | The project shall load Workshop content from a validated, revisioned manifest rather than hard-coded loader branches. |
| `ZC-REQ-BOOT-003` | The content control shall be truthful: disabled means no registrations; enabled means the selected manifest is registered once. |
| `ZC-REQ-BOOT-004` | Dependencies shall be classified as required foundation, required feature capability, optional adapter, administrative integration, or development tooling. |
| `ZC-REQ-BOOT-005` | Missing dependencies shall produce one structured, actionable report and shall not leave an affected feature partially authoritative. |
| `ZC-REQ-BOOT-006` | Optional providers shall be absent-safe and shall integrate only through project-owned capability adapters. |
| `ZC-REQ-BOOT-007` | Required initialization failures shall fail closed and roll back resources created by the failed phase. |
| `ZC-REQ-BOOT-008` | Re-running or hot-reloading bootstrap shall not duplicate hooks, timers, commands, receivers, Workshop registrations, or completion events. |

## Acceptance tests

| ID | Fixture and expected result |
|---|---|
| `ZC-AT-BOOT-001` | Start with content loading disabled; observe zero project Workshop registrations and a truthful disabled status. |
| `ZC-AT-BOOT-002` | Start with the vanilla compatibility manifest; observe the five exact upstream IDs, each registered once. |
| `ZC-AT-BOOT-003` | Start with a duplicate manifest entry; observe one registration and one bounded validation diagnostic. |
| `ZC-AT-BOOT-004` | Remove an optional adapter provider; unrelated boot phases remain active and the adapter reports unavailable without errors. |
| `ZC-AT-BOOT-005` | Remove a required foundation module; dependent phases do not activate, created resources are released, and one actionable failure is published. |
| `ZC-AT-BOOT-006` | Remove ULX/ULib; core gameplay boot remains valid while only ULX-backed administration capabilities report unavailable. |
| `ZC-AT-BOOT-007` | Execute bootstrap twice and through Lua refresh; registrations and completion publication remain idempotent. |
| `ZC-AT-BOOT-008` | Inject a failure during each initialization phase; no later dependent phase reports active and rollback diagnostics identify released resources. |
| `ZC-AT-BOOT-009` | Load with a consolidated project content manifest; legacy and project manifests cannot both register overlapping content. |
| `ZC-AT-BOOT-010` | Verify client distribution: server-only files are never sent, shared/client files are declared explicitly, and unmarked files are rejected or grandfathered by an audited compatibility list. |

## Implementation boundary

This contract does **not** authorize replacing the loader yet. A work package may become Ready only after:

- all `HomigradRun` listeners are enumerated;
- all `hg.loaded` readers/writers are enumerated;
- unmarked Lua files and lexical-order dependencies are indexed;
- existing Workshop/content consumers are mapped;
- ULX/ULib usage is classified by capability;
- Trauma Clean dependency paths and side effects are traced exactly;
- acceptance fixtures above are runnable against the destination baseline.

The first implementation slice should be observational: manifest validation, dependency classification, and structured reporting with no change to gameplay load order. Loader replacement remains a later controlled migration.

## Related documents

- `boot-and-loading.md`
- `upstream-delta-429ec92-to-3716789.md`
- `../source-baselines.md`
- `../sources/trauma-clean-inventory.md`
- `../standards/evidence-and-testing.md`
- `../standards/runtime-ownership-and-generations.md`
- `../../BUILD_GUIDE.md`
