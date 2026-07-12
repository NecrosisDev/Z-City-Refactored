# ZCity Refactored Knowledge Index

This is the entry point for repository knowledge. Every agent must read the following in order at the start of every session:

1. [`../AGENTS.md`](../AGENTS.md) — immutable operating contract and completion standard.
2. [`WORK_PACKAGE.md`](WORK_PACKAGE.md) — current scope, evidence, validation, blockers, and exact continuation action.
3. The relevant catalogs and decision records linked by the work package.

## Verified catalogs

- [`SYSTEM_CATALOG.md`](SYSTEM_CATALOG.md) — systems, ownership, entry points, dependencies, runtime flow, networking, integration state, and validation.
- [`BEHAVIOR_CATALOG.md`](BEHAVIOR_CATALOG.md) — observable gameplay/runtime behaviors and supporting evidence.
- [`TYPE_CATALOG.md`](TYPE_CATALOG.md) — shared types, registries, identifiers, schemas, and compatibility contracts.

## Decision records

- [`decisions/README.md`](decisions/README.md) — compact architectural decisions that future agents must preserve unless superseded by explicit evidence or user direction.

## Knowledge authority

1. Reproducible tests and runtime evidence.
2. Executable code.
3. Evidence-linked catalogs and decision records.
4. Comments, historical notes, and inherited documentation.

Every claim must be labeled `Verified`, `Inferred`, `Legacy Claim`, or `Planned`. Lower-authority material cannot override higher-authority evidence, and supporting documents cannot override `AGENTS.md`.

## Maintenance rule

Keep this index compact. Add only canonical entry points; detailed implementation and handoff information belongs in the active work package, catalogs, decision records, issues, pull requests, tests, and code references.
