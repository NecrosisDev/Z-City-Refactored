# Evidence and Testing Standard

- **Status:** Normative
- **Applies to:** All refactor documentation, requirements, tests, and implementation claims

## Purpose

This standard prevents static inspection, comments, prototype tests, or broad “self-test passed” counts from being mistaken for gameplay parity.

## Evidence labels

Use one of these labels for material claims:

| Label | Meaning | May establish runtime parity? |
|---|---|---|
| **TEST-VERIFIED** | Reproducible automated assertion passed against an identified source, environment, and fixture | Yes, within the test scope |
| **RUNTIME-OBSERVED** | Reproduced manually or through captured runtime instrumentation | Not alone |
| **SOURCE-VERIFIED** | Confirmed directly in executable source at an exact commit/archive hash | Structural facts only |
| **INFERRED** | Strong conclusion from several facts, not directly established | No |
| **CLAIMED** | Present only in comments, names, documentation, logs without reproduction, or prototype prose | No |
| **PROPOSED** | Target design or future requirement | No |
| **REJECTED** | Reviewed and intentionally excluded | Not applicable |
| **UNKNOWN** | Not established | No |

Existing documents that use bare **Verified** without qualification must be read as **SOURCE-VERIFIED**, unless they cite a runtime fixture or executable acceptance test.

## Source binding

Every test result or evidence record must include:

- source commit or archive SHA-256;
- branch when applicable;
- server/client realm;
- map and mode;
- player/bot count;
- relevant ConVars and optional dependencies;
- test or reproduction steps;
- expected and actual result;
- captured diagnostics or artifact location.

Evidence without a source binding is advisory only.

## Test classes

### Static audit

Examples:

- syntax and parse checks;
- symbol and registration inventory;
- duplicate literal detection;
- forbidden global/interception patterns;
- realm naming and manifest checks;
- dependency and content references.

Static audits can establish source structure. They cannot establish gameplay parity.

### Load smoke test

Proves that required server/client phases load without unhandled errors and that optional failures are isolated.

Required scenarios:

- clean server startup;
- first client join;
- second client join;
- missing optional dependency;
- Lua refresh when supported;
- map change or controlled restart.

### Behavioral parity test

Records a destination-baseline outcome and compares the implementation candidate under the same fixture.

A parity test must state which outcomes are compared. Visual similarity, no Lua errors, or registration counts are insufficient.

### Integration test

Validates an end-to-end transition across subsystem boundaries, such as:

- round reset through class, inventory, spawn, and equipment;
- player to fake ragdoll to recovery;
- damage through penetration, organism mutation, effects, and replication;
- vehicle entry, free aim, fire, exit, and cleanup.

### Fault-injection test

Forces failure during preparation, commit, delayed work, cleanup, persistence, adapter discovery, or networking. It verifies rollback and foreign-resource preservation.

### Security test

Covers:

- malformed payloads;
- out-of-range enums and counts;
- stale generations and sequences;
- request spam and rate limits;
- unauthorized admin or debug actions;
- client attempts to write server authority;
- oversized strings/tables and expensive requests.

### Performance test

Measures, rather than assumes:

- server tick and Lua time;
- allocations and retained references;
- network bytes and frequency;
- entity/constraint counts;
- client frame cost;
- scaling with players, bots, wounds, projectiles, and effects.

## Acceptance-test contract

Each acceptance test uses a stable `ZC-AT-<AREA>-NNN` identifier and records:

- requirement and defect links;
- fixture setup;
- baseline source;
- expected observable outcome;
- assertions;
- cleanup assertions;
- realm and authority;
- allowed tolerances;
- failure artifact;
- whether it is static, smoke, parity, integration, fault, security, or performance.

## Minimum assertions for lifecycle work

Lifecycle tests must check more than visible outcome. Where applicable, assert:

- current authority and generation;
- resource counts by owner and type;
- no stale callback mutation;
- no retained invalid player/entity references;
- no duplicate hook, timer, receiver, command, entity, or constraint;
- foreign resources preserved;
- legacy compatibility projections match the new authority;
- rollback returns to the previous stable state.

## Test-result states

Use these states:

- **Not implemented** — test definition exists, no harness.
- **Blocked** — prerequisite fixture or instrumentation missing.
- **Failing baseline** — destination baseline does not satisfy the proposed expectation.
- **Baseline captured** — current behavior recorded without judging it correct.
- **Passing candidate** — candidate satisfies assertions.
- **Parity verified** — baseline-preservation assertions pass.
- **Intentional divergence verified** — approved requirement changes the baseline and the new outcome passes.

A failing baseline is useful evidence. Do not rewrite expected results merely to make a test green.

## Trauma test handling

Trauma tests and release documents are **CLAIMED** evidence until:

1. the asserted system and authority are identified;
2. the test is reproducible against `Trauma_Clean.zip`;
3. the same fixture is run against the destination baseline;
4. assertions cover gameplay and cleanup, not only registration;
5. hidden compatibility fallbacks are disabled or documented.

Trauma’s test names and broad pass counts must not be imported as acceptance authority.

## Closure rule

A defect or requirement cannot be marked complete solely from:

- static analysis;
- absence of Lua errors;
- a single happy-path manual test;
- a passing registration/content audit;
- comments stating intended behavior;
- visual inspection without state assertions.

Completion requires the test classes appropriate to the risk and the Definition of Done in `../../BUILD_GUIDE.md`.
