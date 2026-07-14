# Z-City Refactor Documentation

## Start here

`BUILD_GUIDE.md` is the normative entry point for writing the new code.

The documentation separates four concerns:

1. exact source baselines and evidence;
2. accepted target architecture;
3. ordered implementation and test gates;
4. prototype ideas that may or may not be retained.

## Authority

### Existing behavior

Use the evidence hierarchy in `architecture/standards/evidence-and-testing.md` and the exact source registry in `architecture/source-baselines.md`.

### Target design

Use this order:

1. accepted ADRs under `decisions/`;
2. normative standards under `architecture/standards/`;
3. `BUILD_GUIDE.md` and approved work packages;
4. subsystem architecture documents;
5. `architecture/comparison-ledger.md`;
6. source inventories and prototype documentation.

Runtime code is the ultimate source fact until behavior is tied to a reproducible test. An ADR can change the target; it cannot change what the baseline code did.

## Canonical tree

- `BUILD_GUIDE.md` — implementation phases, gates, work-package requirements, and Definition of Done.
- `00_REFACTOR_METHOD.md` — investigation and decision process.
- `architecture/source-baselines.md` — exact meaning and identity of vanilla, destination, working, and Trauma sources.
- `architecture/standards/` — cross-cutting normative rules.
- `architecture/zcity/` — source-verified baseline behavior and upstream drift.
- `architecture/zcity/verified-defects.md` — stable evidence-backed defects.
- `architecture/sources/` — source inventories and bounded Trauma comparisons.
- `architecture/comparison-ledger.md` — concept-level dispositions.
- `architecture/data/` — machine-readable snapshots.
- `decisions/` — accepted architectural decisions.

Do not create additional top-level documentation trees for Trauma, modes, tests, or migration work. Add them under the canonical paths above.

## Evidence vocabulary

Use:

- **TEST-VERIFIED**;
- **RUNTIME-OBSERVED**;
- **SOURCE-VERIFIED**;
- **INFERRED**;
- **CLAIMED**;
- **PROPOSED**;
- **REJECTED**;
- **UNKNOWN**.

Bare “Verified” in older documents means source-verified unless a runtime fixture or acceptance-test result is linked.

## Change rule

No Trauma subsystem, upstream commit, or apparent fix enters the new project merely because it is newer or more modular. Every implementation must identify:

- exact source baseline;
- defect or requirement;
- current compatibility contract;
- selected disposition;
- authority and lifecycle owner;
- test IDs;
- rollout and rollback path;
- legacy removal criteria.
