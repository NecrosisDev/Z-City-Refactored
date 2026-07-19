# ADR-0002: Trauma Is Evidence, Not the Refactor Baseline

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Z-City Refactor maintainers
- **Source scope:** All Trauma snapshots; current source selected by `../architecture/source-baselines.md`

## Context

The Trauma prototypes contain a large collection of modifications, rewrites, adapters, diagnostics, mode extensions, bot systems, medical changes, performance tooling, and compatibility patches built on top of Z-City.

They also contain overlapping generations of systems, duplicated registrations, broad patches, prototype naming, bundled vendor code, implicit assumptions, and behavior changes that have not been proven against the destination baseline or upstream vanilla behavior.

The historical `Trauma.zip` snapshot has been superseded for implementation guidance by `Trauma_Clean.zip`. The newer archive changes hundreds of files and adds further diagnostics, restoration code, documentation, assets, and vendor material. A newer Trauma iteration does not become authoritative merely because it is cleaner or more complete.

Using any Trauma snapshot directly as the new baseline would import both useful ideas and regressions. Ignoring Trauma would discard substantial design exploration and prototypes.

## Decision

Trauma is treated as **non-authoritative evidence and prototype material**.

The destination baseline and explicitly selected upstream vanilla behavior remain the compatibility references until a deliberate architectural decision and acceptance tests authorize a change.

Every Trauma attempt receives one of these dispositions:

- **Adopt** — implementation and behavior are suitable with minimal changes.
- **Adapt** — retain a bounded implementation pattern behind project APIs.
- **Rewrite** — retain the requirement while replacing the implementation.
- **Reject** — do not carry the concept forward.
- **Keep Z-City** — existing behavior remains preferable.
- **Deferred** — prerequisite evidence, contracts, or tests are missing.

No Trauma file is merged solely because it is newer, more feature-rich, documented as fixed, or present in the clean snapshot.

## Required evidence for adoption

A Trauma concept may advance into implementation only when the comparison ledger and work package record:

1. exact source identities and paths;
2. destination-baseline behavior;
3. relevant later upstream vanilla behavior;
4. the actual defect or new requirement;
5. the Trauma implementation and dependencies;
6. known regressions and failure modes;
7. server/client authority, lifecycle, cleanup, and persistence;
8. security, networking, and performance effects;
9. selected disposition;
10. compatibility, rollout, rollback, and legacy-removal strategy;
11. stable acceptance-test IDs and fixtures.

The work package must satisfy the gates in `../BUILD_GUIDE.md`.

## Consequences

### Positive

- Proven gameplay behavior is not accidentally lost.
- Useful Trauma concepts remain available.
- Architectural decisions become traceable.
- Prototype mistakes do not become permanent public APIs.
- Work can be cherry-picked at requirement or mechanic level rather than ZIP/file level.
- The future project can be cleaner than both sources.
- Changes between Trauma iterations can be evaluated rather than silently inherited.

### Negative

- Migration is slower than copying Trauma.
- Baseline behavior must be documented and tested deeply.
- Some Trauma systems will be reimplemented despite existing code.
- Temporary compatibility layers will be necessary.
- More test and observability infrastructure is required before large rewrites.

## Rejected alternatives

### Use Trauma Clean as the baseline and fix regressions later

Rejected because overlapping systems, vendor modifications, hidden fallbacks, and regressions are not fully enumerated. Starting from Trauma would obscure whether behavior came from Z-City, an intentional redesign, a compatibility patch, or an accidental breakage.

### Ignore Trauma and refactor only from vanilla

Rejected because Trauma contains useful experiments in lifecycle ownership, generations, registries, adapters, self-tests, spawning, bots, medical simulation, configuration, UI, and tooling.

### Merge individual Trauma files opportunistically

Rejected because most files depend on surrounding globals, load order, vendor code, duplicate systems, or implicit behavior. File-level copying is not a safe migration unit.

### Trust Trauma documentation and release evidence as proof

Rejected because internal documentation and passing self-test counts are claims until verified against executable source, runtime fixtures, cleanup, authority, and parity assertions.

## Enforcement

- The comparison ledger is required for every Trauma-derived implementation.
- The current Trauma source is selected only by `architecture/source-baselines.md`.
- New public APIs use project naming, not Trauma prototype naming.
- Trauma-specific compatibility names may exist only behind adapters with removal criteria.
- Production architecture must not infer ownership by replacing global registration functions.
- Comments and internal documents in either source are claims, not proof.
- Static inspection must be followed by the test classes appropriate to the risk.
- Bundled vendor code is not adopted as the default dependency architecture.

## Initial application

The first reviewed concept was Trauma’s mode lifecycle manager.

Decision summary:

- generation guards: adopt;
- explicit activation/deactivation: adapt;
- ownership records: rewrite;
- global `hook.Add`/timer interception: reject;
- static capture: migration-only audit technique;
- lifecycle diagnostics: adapt;
- spawn contracts: defer pending stock-mode parity documentation;
- self-tests: rewrite under the project evidence taxonomy.

The canonical detailed comparison is `../architecture/sources/trauma-mode-lifecycle-comparison.md`.
