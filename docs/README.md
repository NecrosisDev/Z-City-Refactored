# Z-City Refactor Documentation

## Purpose

This directory is the working specification for the Z-City Refactor. It separates verified behavior from proposed design and prevents Trauma experiments, comments, or inherited assumptions from being treated as authoritative.

## Authority order

When documents disagree, use this order:

1. **Verified Z-City behavior** under `architecture/zcity/`.
2. **Accepted architectural decisions** under `decisions/`.
3. **Comparison ledger** under `architecture/comparison-ledger.md`.
4. **Source inventories** under `architecture/sources/`.
5. Planning and migration documents.
6. Legacy or transitional documents.

Runtime code remains the ultimate evidence until a behavior has an executable acceptance test.

## Canonical document tree

- `00_REFACTOR_METHOD.md` — investigation and migration rules.
- `architecture/README.md` — architecture documentation index.
- `architecture/zcity/` — verified current and vanilla-derived behavior.
- `architecture/sources/` — inventories of source material, including Trauma.
- `architecture/comparison-ledger.md` — per-concept disposition ledger.
- `decisions/` — architectural decision records.
- `architecture/data/` — machine-readable audit snapshots.

## Transitional duplicates

The following early files overlap with the canonical architecture tree and are retained temporarily only to avoid losing work during consolidation:

- `zcity/BOOT_AND_LOAD_LIFECYCLE.md`
- `trauma/ATTEMPT_INVENTORY.md`

They are not independent sources of truth. Material from them must be reconciled into `architecture/zcity/`, `architecture/sources/`, or an ADR before implementation work relies on it. They should be removed after reconciliation is verified.

## Evidence labels

Every substantive claim should be identifiable as one of:

- **Verified** — confirmed against executable code or a reproducible test.
- **Observed** — found by static inspection but not runtime-tested.
- **Inferred** — a reasoned conclusion from observed behavior.
- **Proposed** — a future design.
- **Rejected** — reviewed and intentionally not selected.

## Change rule

No Trauma subsystem is ported merely because it is newer or more modular. A change must document:

- the vanilla/current behavior it affects;
- the defect or requirement being addressed;
- the Trauma concept, if any, being considered;
- the selected disposition: adopt, adapt, rewrite, reject, or keep current behavior;
- compatibility and rollback strategy;
- acceptance tests.
