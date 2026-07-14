# Refactor Traceability Index

- **Status:** Normative index; implementation rows not yet populated
- **Source registry:** `../architecture/source-baselines.md`
- **Build guide:** `../BUILD_GUIDE.md`

## Purpose

This file prevents requirements, defects, tests, code, and decisions from drifting apart. Every behavior-changing work package must add or update a row before it can be marked **Ready**, and again before it can be marked **Complete**.

## Master table

| Requirement ID | Work package | Defects | ADRs/standards | Acceptance tests | Implementation | State |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | No implementation work packages approved yet |

## Row rules

- One requirement may span multiple work packages only when each slice is independently testable.
- One work package may satisfy several tightly coupled requirements, but scope must remain bounded.
- Every defect closure links at least one acceptance test and implementation commit.
- Every test links a requirement or a defect; orphan tests are diagnostics, not acceptance authority.
- Rejected and deferred requirements remain in the index with their decision and prerequisite.
- Compatibility adapters receive removal criteria and a later removal work package.

## Required evidence links

Each populated row must make it possible to locate:

- exact destination and comparison source identities;
- current behavior document;
- comparison-ledger disposition;
- accepted ADR or standard;
- work-package record;
- test specification and result artifact;
- implementation commit or pull request;
- rollback result;
- defect/legacy status after validation.

## Planned first implementation area

The build guide identifies observation and low-risk foundation corrections as the first implementation phase. No work package is **Ready** until the baseline harness, fixtures, and exact affected call graphs satisfy Gates 0–2.
