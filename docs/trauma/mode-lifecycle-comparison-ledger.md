# Trauma Comparison Ledger: Mode Lifecycle

- **Status:** Evidence review in progress
- **Baseline:** Current/vanilla Z-City behavior
- **Prototype source:** Trauma mode lifecycle manager
- **Decision authority:** ADR-0002
- **Last reviewed:** 2026-07-14

## Scope

This ledger records the first bounded Trauma concept review required by ADR-0002. It does not authorize copying Trauma files. Each row separates the desired behavior from the prototype mechanism so useful ideas can be retained without importing global interception, hidden ownership, or unverified behavioral changes.

## Compatibility baseline

Until runtime parity tests prove otherwise, the refactor must preserve these observable properties:

1. Mode activation does not silently replace unrelated hooks, timers, network receivers, or commands.
2. Leaving a mode removes only resources owned by that mode.
3. Re-entering or reloading a mode does not accumulate duplicate registrations.
4. Existing Z-City mode behavior remains the reference for spawn flow, role setup, round transitions, cleanup, and spectator handling.
5. A failed activation can be rolled back without requiring a server restart.
6. Diagnostics may observe registrations, but production code must not globally intercept `hook.Add`, timer creation, or equivalent engine APIs.

These properties are acceptance targets, not claims that the current implementation already satisfies them.

## Decision matrix

| Concept attempted by Trauma | Problem addressed | Disposition | Refactor rule | Required evidence before implementation |
|---|---|---|---|---|
| Generation guards | Stale callbacks from a previous activation remain callable | **Adopt** | Every activation receives a monotonically increasing generation token. Deferred work must verify that token before mutating state. | Re-entry test; delayed timer test; stale net/callback test |
| Explicit activation and deactivation | Mode setup and cleanup are spread across implicit hooks | **Adapt** | Define a narrow lifecycle contract owned by the mode registry. Activation and deactivation must be idempotent and return structured results. | Current mode transition trace; rollback test; double-deactivate test |
| Ownership records | Resources cannot be attributed reliably during cleanup | **Rewrite** | Store explicit handles returned by project wrappers. Ownership is declared at registration time; it is never inferred by replacing global APIs. | Ownership schema review; cleanup coverage test; foreign-resource preservation test |
| Global `hook.Add`/timer interception | Attempts to discover registrations automatically | **Reject** | Production architecture must not monkey-patch global registration functions. | No implementation work; static audit tooling may remain separate and offline |
| Static registration capture | Finds likely hooks, timers, networking, commands, and ConVars | **Migration-only audit technique** | Use generated repository manifests to seed manual review. Lexical matches are evidence pointers, not proof of runtime ownership. | Manifest freshness; semantic review of each migrated registration |
| Lifecycle diagnostics | Operators need to see active generation, owners, leaks, and failed cleanup | **Adapt** | Expose read-only diagnostics from the registry. Do not expose mutation endpoints to clients. | Server-only access review; redaction review; leak-report acceptance test |
| Spawn contracts | Mode activation depends on spawn/role/loadout behavior | **Defer** | Do not standardize until vanilla spawn and round behavior is documented per supported mode. | Spawn parity documents; role and spectator traces; failure-path tests |
| Self-tests | Trauma includes checks but their authority and categories are inconsistent | **Rewrite** | Tests must distinguish static evidence, isolated unit checks, integration checks, and live runtime parity. A static pass cannot claim gameplay parity. | Test taxonomy; reproducible harness; failure injection cases |

## Proposed project contract

The following interface is a design target, not yet an implementation commitment:

```lua
ModeLifecycle.Activate(modeId, context) -> result
ModeLifecycle.Deactivate(modeId, reason) -> result
ModeLifecycle.GetActive() -> snapshot
ModeLifecycle.GetOwnedResources(modeId) -> snapshot
```

### Activation requirements

- Validate the mode identifier and prerequisites before mutating global state.
- Allocate a new generation and ownership scope.
- Register resources only through explicit project wrappers.
- Record every successful registration immediately.
- On failure, unwind registrations in reverse order.
- Publish the active mode only after all mandatory activation stages succeed.

### Deactivation requirements

- Mark the generation inactive before cleanup begins so delayed callbacks become inert.
- Remove only resources recorded in that ownership scope.
- Continue cleanup after individual failures and return an aggregated error report.
- Clear references that could retain players, entities, functions, or large tables.
- Remain safe when called repeatedly or after partial activation.

## Minimum ownership schema

Each owned resource record should contain:

| Field | Purpose |
|---|---|
| `owner_mode` | Stable project mode identifier |
| `generation` | Activation generation that created the resource |
| `resource_type` | Hook, timer, network receiver, command, ConVar observer, entity, or custom cleanup |
| `resource_name` | Stable registration name or diagnostic label |
| `remove` | Server-held cleanup closure or typed removal descriptor |
| `source` | File and line when available |
| `created_at` | Relative/runtime timestamp for diagnostics |
| `state` | Active, removed, failed, or orphaned |

Cleanup closures must remain server-side and must not be serialized to clients.

## Acceptance tests required before code migration

1. **Clean activation:** a supported vanilla-equivalent mode activates once with no duplicate resources.
2. **Idempotent activation:** activating the already-active mode has a defined no-op or controlled restart result.
3. **Clean transition:** mode A deactivates before mode B becomes authoritative.
4. **Rollback:** a forced failure halfway through activation removes everything created by that attempt.
5. **Generation invalidation:** delayed callbacks from a previous generation perform no mutation.
6. **Foreign-resource preservation:** hooks and timers not owned by the mode remain registered.
7. **Repeated cycle:** 100 activate/deactivate cycles produce stable registration and memory counts.
8. **Player disconnect:** lifecycle cleanup does not retain disconnected player objects.
9. **Entity removal:** owned entities and references are removed without touching map-owned or admin-spawned entities.
10. **Diagnostics security:** lifecycle state is available to authorized server operators without exposing privileged mutation or internal closures to clients.

## Evidence still required

The next review must document current Z-City behavior for:

- initial mode selection and activation;
- round-start and round-end ownership;
- player spawn, role, loadout, and spectator transitions;
- cleanup on map cleanup, Lua refresh, and mode change;
- registrations that currently outlive their intended mode;
- failure behavior when a mode file or dependency is missing.

No spawn-contract rewrite should begin until that baseline exists.

## Implementation boundary

This review justifies a future lifecycle registry and generation guard. It does **not** justify importing Trauma's lifecycle files, public names, global interception, or assumptions about spawn behavior. Implementation should begin only after the vanilla transition trace and registration inventory are linked into this ledger.
