# ZC-WP-NNN — Work Package Title

- **State:** Draft
- **Owner:**
- **Created:**
- **Last reviewed:**
- **Target branch:**

## 1. Scope

Define the smallest independently testable implementation slice. State explicit exclusions.

## 2. Source binding

| Source | Identity | Relevant paths |
|---|---|---|
| Destination baseline | Commit | |
| Upstream vanilla snapshot | Commit/archive SHA-256 | |
| Current Trauma prototype | Archive SHA-256 | |
| Working branch | Commit | |

State whether exhaustive symbol and registration search was completed.

## 3. Problem and authority

- **Linked defects:**
- **Linked requirements:**
- **Linked ADRs/standards:**
- **Current authority:**
- **Target authority:**
- **Intentional behavior change:** Yes/No

Describe why the current state is defective or why a new requirement is justified.

## 4. Current compatibility contract

Record observable behavior that must remain stable, including:

- inputs and outputs;
- realm and call order;
- state mutations;
- hooks, packets, fields, globals, and aliases;
- failure and fallback behavior;
- map/mode/player/weapon/adapter variations.

## 5. Upstream and Trauma comparison

### Upstream delta

Describe relevant later upstream changes and disposition.

### Trauma attempt

List exact Trauma paths and dependencies.

- **Disposition:** Keep Z-City / Adopt / Adapt / Rewrite / Reject / Deferred
- **Justification:**
- **Mechanisms explicitly not imported:**

## 6. Design

Describe:

- target API and data model;
- server/client ownership;
- owner type, lifetime, and generation;
- transition prepare/commit/rollback points;
- runtime resources and cleanup;
- compatibility projections;
- network schema, validation, visibility, and rate policy;
- persistence schema/revision/migration when applicable;
- optional adapter boundaries;
- hot-path and memory budget.

## 7. Implementation plan

List ordered, reviewable commits. Each step must leave the branch in a coherent state.

1.
2.
3.

## 8. Acceptance tests

| Test ID | Class | Baseline captured | Candidate expected | Status |
|---|---|---|---|---|
| `ZC-AT-AREA-NNN` | Static/Smoke/Parity/Integration/Fault/Security/Performance | | | Not implemented |

Include cleanup, stale-generation, rollback, and foreign-resource assertions where applicable.

## 9. Rollout

- feature switch or compatibility adapter;
- default state;
- operator diagnostics;
- observation period;
- failure response.

## 10. Rollback

Define how to return to the previous stable authority without losing live or persistent state. State whether restart is required.

## 11. Legacy removal criteria

List every condition required before deleting the old path:

- exhaustive consumer search complete;
- telemetry observation window complete;
- compatibility tests pass without legacy writer;
- downgrade/removal tested;
- migration notes published.

## 12. Risks and unknowns

List unresolved questions. A field that can change correctness, authority, cleanup, security, persistence, or parity blocks **Ready** state.

## 13. Gate checklist

### Gate 0 — Source freeze

- [ ] exact source identities recorded
- [ ] affected graph exhaustively searched
- [ ] upstream drift reviewed

### Gate 1 — Behavioral contract

- [ ] current lifecycle documented
- [ ] compatibility invariants written
- [ ] candidate disposition approved

### Gate 2 — Test harness

- [ ] stable test IDs assigned
- [ ] destination-baseline fixtures captured
- [ ] required failure injection available

### Definition of Done

- [ ] one authoritative state owner
- [ ] resources owned and cleanup verified
- [ ] parity or intentional divergence test-verified
- [ ] security and payload limits reviewed
- [ ] hot reload/cleanup/disconnect/shutdown addressed
- [ ] performance measured where relevant
- [ ] rollback tested
- [ ] ledger, defect register, and traceability updated
- [ ] legacy removal criteria explicit
