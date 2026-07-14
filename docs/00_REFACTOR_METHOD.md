# Z-City Refactor Method

- **Status:** Normative investigation and decision method
- **Implementation guide:** `BUILD_GUIDE.md`
- **Source registry:** `architecture/source-baselines.md`

## Purpose

The refactor compares distinct bodies of work without conflating them:

1. the upstream vanilla snapshot;
2. the destination baseline and working branch;
3. the current Trauma prototype;
4. historical Trauma material and prior experiments.

Exact definitions and hashes are maintained in `architecture/source-baselines.md`.

Trauma is not an authoritative replacement for Z-City. Upstream commits are not automatic cherry-picks. The new project may retain behavior, adapt a concept, or intentionally diverge only through documented requirements and tests.

## Decision hierarchy

1. Establish existing behavior using the evidence standard.
2. Preserve verified compatibility unless an intentional change is approved.
3. Apply accepted ADRs and cross-cutting standards.
4. Prefer explicit authority, ownership, realm boundaries, lifecycle, and rollback.
5. Reject abstractions whose operational risk exceeds their benefit.
6. Require acceptance tests before behavior-changing migration.

## Evidence

Use the labels and test classes in `architecture/standards/evidence-and-testing.md`.

Important interpretation rule:

> Direct source inspection can verify code structure and possible execution paths. It does not by itself verify runtime outcome or gameplay parity.

Comments, file names, Trauma documentation, release claims, and self-test summaries are evidence leads, not authority.

## Per-system workflow

Process each subsystem in this order:

1. Bind the review to exact source snapshots.
2. Enumerate all files, entry points, publishers, consumers, hooks, timers, messages, commands, ConVars, globals, entities, constraints, persistence, and external dependencies.
3. Reconstruct actual destination-baseline lifecycle and ordering.
4. Compare later upstream vanilla changes separately.
5. Inventory corresponding Trauma attempts and their dependencies.
6. Identify authority, realm, lifetime, cleanup, failure, security, and performance characteristics.
7. Record compatibility invariants and ambiguity.
8. Classify each candidate:
   - **Keep Z-City**;
   - **Adopt**;
   - **Adapt**;
   - **Rewrite**;
   - **Reject**;
   - **Deferred**.
9. Write or update an ADR for material architecture decisions.
10. Assign requirement and acceptance-test IDs.
11. Create a work package satisfying `BUILD_GUIDE.md`.
12. Implement in a small compatibility-preserving slice.
13. Run parity, fault, security, cleanup, and performance tests appropriate to the risk.
14. Update the ledger, defect status, and removal criteria.

## Required subsystem documentation

A mature subsystem document includes:

- source baseline, hash/commit, paths, realm, and review date;
- evidence and runtime/test status;
- purpose and current authority;
- entry points and lifecycle;
- public and internal interfaces;
- data model and persistent state;
- hook, timer, network, command, ConVar, entity, and constraint registries;
- ordering and hot-path behavior;
- dependencies and optional adapters;
- destination-baseline compatibility contracts;
- later upstream delta;
- Trauma attempts and disposition;
- known defects and unknowns;
- security and performance implications;
- target authority and migration boundary;
- stable requirements and acceptance-test IDs;
- compatibility, rollout, rollback, and legacy removal criteria.

## Migration constraints

- Legacy `hg` and `zb` surfaces remain compatibility projections until callers are inventoried and migrated.
- New runtime resources follow `architecture/standards/runtime-ownership-and-generations.md`.
- Global registration functions are not replaced to infer ownership.
- Optional integrations fail isolated and leave core gameplay operational.
- Load order is explicit where behavior depends on order.
- Shared files do not silently become server-only or client-only.
- Client-delivered code and client-originated payloads are untrusted.
- Hot reload support does not weaken clean-start correctness.
- Critical initialization does not continue silently after partial failure.
- Runtime and persistent state changes have rollback and downgrade behavior.
- Compatibility layers have telemetry and removal criteria.

## Work order

Follow the phases in `BUILD_GUIDE.md` rather than extending research indefinitely. Analysis for a subsystem is complete enough to implement when Gates 0–2 are satisfied, not when every possible source file in the project has been described.

This file governs investigation. `BUILD_GUIDE.md` governs implementation.
