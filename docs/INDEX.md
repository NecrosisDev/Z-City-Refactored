# ZCity Refactored Knowledge Index

This index is the entry point for verified project knowledge. Keep pages concise and link to code, tests, issues, or commits that support important claims.

## Current work

- [`WORK_PACKAGE.md`](WORK_PACKAGE.md) — active scope, decisions, validation, risks, and next action.

## Verified catalogs

- [`SYSTEM_CATALOG.md`](SYSTEM_CATALOG.md) — systems, ownership, entry points, dependencies, networking, and validation.
- [`BEHAVIOR_CATALOG.md`](BEHAVIOR_CATALOG.md) — observable gameplay/runtime behaviors and their evidence.
- [`TYPE_CATALOG.md`](TYPE_CATALOG.md) — shared types, registries, identifiers, schemas, and compatibility contracts.

## Decision records

- [`decisions/README.md`](decisions/README.md) — small records for architectural decisions that future agents must not repeatedly rediscover.

## Authority order

1. Tests and reproducible runtime evidence.
2. Executable code.
3. Catalogs and decision records linked to evidence.
4. Comments, historical notes, and inherited documentation.

A lower-authority source must not override a higher-authority source without new evidence.
