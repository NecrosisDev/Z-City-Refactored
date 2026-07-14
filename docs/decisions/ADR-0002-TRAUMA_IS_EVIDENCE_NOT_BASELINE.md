# ADR-0002: Trauma Is Evidence, Not the Refactor Baseline

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Z-City Refactor maintainers

## Context

`Trauma.zip` contains a large collection of modifications, rewrites, adapters, diagnostics, mode extensions, bot systems, medical changes, performance tooling, and compatibility patches built on top of Z-City.

It also contains overlapping generations of systems, duplicated registrations, broad patches, prototype naming, implicit assumptions, and behavior changes that have not been proven against vanilla Z-City.

Using Trauma directly as the new baseline would import both its useful ideas and its regressions. Ignoring Trauma would discard substantial design exploration and working prototypes.

The project therefore requires a clear rule for how Trauma influences the refactor.

## Decision

Trauma is treated as **non-authoritative evidence and prototype material**.

Vanilla/current Z-City behavior remains the compatibility reference until a deliberate architectural decision and acceptance tests replace it.

Every Trauma attempt must receive one of these dispositions:

- **Adopt** — implementation and behavior are both suitable with minimal changes.
- **Adapt** — retain the implementation pattern but integrate it through project conventions.
- **Rewrite** — retain the intent while replacing the implementation.
- **Reject** — do not carry the concept forward.
- **Keep Z-City** — current behavior is preferable or Trauma does not justify a change.
- **Defer** — insufficient evidence or prerequisite documentation.

No Trauma file is merged solely because it is newer, more feature-rich, or labeled as a fix.

## Required evidence for adoption

A Trauma concept may advance into implementation only when the comparison ledger records:

1. the current Z-City behavior;
2. the actual problem or new requirement;
3. the relevant Trauma implementation;
4. known regressions and failure modes;
5. security, realm, networking, and performance effects;
6. the selected disposition;
7. rollback and compatibility strategy;
8. acceptance tests.

## Consequences

### Positive

- Proven gameplay behavior is not accidentally lost.
- Useful Trauma concepts remain available.
- Architectural decisions become traceable.
- Prototype mistakes do not become permanent public APIs.
- Work can be cherry-picked at concept level rather than ZIP/file level.
- The future project can be cleaner than both sources.

### Negative

- Migration is slower than copying Trauma.
- Vanilla behavior must be documented deeply.
- Some Trauma systems will be reimplemented despite existing code.
- Temporary compatibility layers will be necessary.
- More test infrastructure is required before large rewrites.

## Rejected alternatives

### Use Trauma as the baseline and fix regressions later

Rejected because regressions and overlapping systems are not fully enumerated. Starting from Trauma would make it difficult to distinguish inherited behavior, intentional redesign, and accidental breakage.

### Ignore Trauma and refactor only from vanilla

Rejected because Trauma contains useful experiments in lifecycle ownership, registries, adapters, self-tests, spawning, bots, medical simulation, configuration, and tooling.

### Merge individual Trauma files opportunistically

Rejected because most files depend on surrounding globals, load order, duplicate systems, or implicit behavior. File-level copying is not a safe unit of architectural migration.

## Enforcement

- The comparison ledger is required for every Trauma-derived implementation.
- New public APIs use Z-City project naming, not Trauma prototype naming.
- A Trauma-specific compatibility name may exist only behind an adapter and with a removal plan.
- Global function interception is prohibited in production architecture unless a later ADR explicitly overrides this rule.
- Documentation comments in either source are claims, not proof.
- Static inspection must be followed by runtime tests before declaring parity.

## Initial application

The first reviewed concept is Trauma's mode lifecycle manager.

Decision summary:

- generation guards: adopt;
- explicit activation/deactivation: adapt;
- ownership records: rewrite;
- global `hook.Add`/timer interception: reject;
- static capture: migration-only audit technique;
- lifecycle diagnostics: adapt;
- spawn contracts: defer pending spawn parity documentation;
- self-tests: rewrite under stricter evidence categories.
