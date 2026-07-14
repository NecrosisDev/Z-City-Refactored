# Z-City Refactor Method

## Purpose

This repository is being developed by comparing three bodies of work:

1. **Vanilla Z-City** — the behavioral reference.
2. **The current Refactored repository** — the integration and deployment baseline.
3. **Trauma** — an experimental implementation containing both useful concepts and substantial technical debt.

Trauma is not an authoritative replacement for vanilla Z-City. No Trauma implementation is accepted merely because it is newer or more modular in appearance.

## Decision hierarchy

When implementations disagree, use this order:

1. Preserve verified vanilla gameplay behavior unless a change is intentional and documented.
2. Preserve compatibility required by existing servers, maps, weapons, entities, and addons.
3. Prefer explicit APIs, deterministic lifecycle ownership, and clear realm boundaries.
4. Reject abstractions whose operational risk exceeds their benefit.
5. Require an acceptance test for every behavior-changing migration.

## Evidence levels

Every claim in this documentation must use one of these labels:

- **Verified:** Directly confirmed in executable source.
- **Observed:** Seen in runtime output, logs, or reproducible behavior.
- **Inferred:** Strongly implied by several code paths but not yet runtime-tested.
- **Claimed:** Present only in comments, names, documentation, or design intent.
- **Unknown:** Not yet established.

Comments are evidence of intent, not evidence of behavior.

## Per-system workflow

Each subsystem is processed through the following sequence:

1. Locate all entry points and owners.
2. Reconstruct the actual vanilla lifecycle.
3. Record hooks, timers, network messages, ConVars, commands, globals, files, and external dependencies.
4. Identify implicit contracts and ordering assumptions.
5. Inventory the corresponding Trauma changes.
6. Compare behavior and failure modes.
7. Classify each Trauma attempt as:
   - **Adopt** — concept and implementation are suitable.
   - **Adapt** — implementation needs limited integration work.
   - **Rewrite** — intent is useful, implementation is unsafe or overly coupled.
   - **Reject** — no adequate benefit or unacceptable regression risk.
   - **Keep Vanilla** — existing behavior is preferable.
8. Write an ADR for material decisions.
9. Define acceptance tests before implementation.
10. Migrate in small, reviewable commits.

## Required system documentation

Each mature subsystem document must include:

- Purpose and ownership
- Entry points and lifecycle
- Public and internal interfaces
- Data model and persistent state
- Realm behavior
- Hook registry
- Timer registry
- Network registry and trust boundaries
- ConVar and command registry
- Dependencies and adapters
- Vanilla behavioral contracts
- Trauma attempts
- Known defects and ambiguity
- Performance characteristics
- Migration decision
- Acceptance tests

## Migration constraints

- The legacy `hg` and `zb` namespaces remain compatibility surfaces until callers are inventoried and migrated.
- Global registration functions must not be replaced to infer ownership.
- Mode or subsystem ownership must be explicit at registration time.
- Optional integrations must fail closed and leave core gameplay operational.
- Load order must be explicit where behavior depends on order.
- Shared files must not silently become server-only or client-only.
- Client-delivered code and network handlers must be treated as untrusted surfaces.
- Hot reload support must not weaken ordinary startup correctness.

## Initial work order

1. Boot, realm loading, and deferred initialization
2. Gamemode and round lifecycle
3. Player spawn, death, fake-ragdoll, and organism reset
4. Damage, organism, blood, pain, and death
5. Weapons, aiming, obstruction, and vehicles
6. Networking and client trust boundaries
7. NPCs and bots
8. UI, administration, persistence, and external adapters

This file is the governing method for the documentation and refactor branch.