# Z-City Architecture Research

This directory is the working source of truth for the Z-City refactor.

The project uses a three-source comparison model:

1. **Vanilla Z-City** defines observed gameplay behavior and compatibility expectations.
2. **Z-City-Refactored** defines the current repository baseline and migration constraints.
3. **Trauma** is an experimental implementation whose ideas must be independently verified before adoption.

No Trauma feature is accepted solely because it exists. Every candidate change must be classified as one of:

- **Keep vanilla** — existing behavior is correct and sufficiently maintainable.
- **Adopt** — the concept and implementation are both suitable.
- **Adapt** — the implementation is useful but must be integrated behind stable project boundaries.
- **Rewrite** — the intent is valid, but the implementation is unsafe, coupled, incomplete, or unnecessarily complex.
- **Reject** — the change adds no sufficient value or creates unacceptable regressions.

## Documentation order

1. Build a behavior-first inventory of vanilla Z-City.
2. Record subsystem ownership, lifecycle, dependencies, hooks, timers, networking, ConVars, globals, and external integrations.
3. Inventory Trauma's attempted changes without treating them as authoritative.
4. Compare each attempt against vanilla behavior and the new project requirements.
5. Record architectural decisions before implementation.
6. Port only evidence-backed changes with acceptance tests.

## Required evidence for implementation

A change should not enter the new project without:

- a documented problem or requirement;
- the relevant vanilla behavior;
- the Trauma approach, when applicable;
- alternatives considered;
- compatibility and regression risks;
- server/client ownership;
- lifecycle and cleanup requirements;
- acceptance criteria;
- an explicit adoption decision.

## Current status

The documentation foundation is being established before production code is changed. The first completed artifact is the initial Trauma inventory in `sources/trauma-inventory.md`.