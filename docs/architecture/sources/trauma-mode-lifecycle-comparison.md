# Trauma Comparison: Mode Lifecycle

- **Status:** SOURCE-VERIFIED concept review; runtime parity not established
- **Destination baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Prototype:** `Trauma_Clean.zip` (`03d6b1b...`)
- **Decision authority:** ADR-0001, ADR-0002, ADR-0004
- **Standards:** `../standards/runtime-ownership-and-generations.md`, `../standards/evidence-and-testing.md`
- **Supersedes:** `docs/trauma/mode-lifecycle-comparison-ledger.md`

## Scope

This review separates valid lifecycle requirements from Trauma’s implementation mechanisms. It does not authorize copying Trauma lifecycle files or public names.

## Decision matrix

| Trauma concept | Disposition | Build rule |
|---|---|---|
| Generation guards | **Adopt** | Every authoritative activation has a monotonically increasing generation; stale work rejects itself at execution. |
| Explicit activation/deactivation | **Adapt** | Implement prepare, validate, commit, retire, cleanup, verify, and rollback phases under the project registry. |
| Ownership records | **Rewrite** | Ownership is declared through typed project APIs; never inferred through global interception. |
| Global `hook.Add`/timer interception | **Reject** | Allowed only in offline/static migration tooling, never production runtime. |
| Static registration capture | **Migration-only** | Use lexical manifests to seed semantic review; they do not prove runtime ownership. |
| Lifecycle diagnostics | **Adapt** | Read-only authorized diagnostics report owner, generation, source, resources, cleanup, and stale-work rejection. |
| Hard-coded persistent-event allowlists | **Reject** | Lifetime is declared per resource, not guessed from hook name. |
| Retained mode state | **Rewrite** | Versioned retained state has an owner, schema, migration, validation, and cleanup policy. |
| Self-tests | **Rewrite** | Separate static audit, load smoke, parity, integration, fault, security, and performance tests. |
| Spawn contracts embedded in lifecycle | **Defer** | Complete stock-mode admission/spawn fixtures before standardizing topology or fallback. |

## Target project interface

Names remain provisional until implementation ADR/API review:

```lua
ModeRegistry.Prepare(modeId, context) -> transaction
transaction:Validate() -> result
transaction:Commit() -> activation
activation:Deactivate(reason) -> result
ModeRegistry.GetActiveSnapshot() -> snapshot
ModeRegistry.GetResourceSnapshot(filter) -> snapshot
```

The interface must not expose cleanup closures or mutable registry tables to clients.

## Activation contract

1. Resolve the declared mode and inheritance graph deterministically.
2. Validate required capabilities before creating global effects.
3. Allocate a provisional owner and new activation generation.
4. Register resources through typed ownership APIs.
5. Record each resource immediately.
6. Validate mode invariants and required callbacks.
7. Commit active authority at one documented point.
8. Publish legacy `MODE`, `zb`, hooks, and packets only as compatibility projections.
9. On failure, unwind provisional resources in reverse order and preserve the prior committed mode.

## Deactivation contract

1. Mark the generation inactive before cleanup.
2. Stop accepting new work for that activation.
3. Cancel delayed work and remove owned resources.
4. Continue cleanup after individual failures and aggregate results.
5. clear retained player/entity/function/table references whose lifetime ended.
6. Verify foreign resources remain intact.
7. Verify no projected compatibility state still identifies the retired generation.
8. Make repeated deactivation safe.

## Required mode inventory before migration

For every stock mode-table function, record:

- defining source and realm;
- inherited or direct definition;
- classification: engine event, round callback, policy query, command, utility, or adapter callback;
- direct callers;
- matching `hook.Run`/`hook.Call` emitters;
- arguments and return contract;
- global/player/entity mutations;
- hooks, timers, receivers, commands, entities, constraints, and persistence created;
- retained state and cleanup owner;
- behavior when inactive;
- behavior after Lua refresh or partial load failure.

Automatic function-to-hook projection remains a legacy compatibility behavior until this inventory and parity fixtures are complete.

## Required acceptance tests

| ID | Test |
|---|---|
| `ZC-AT-MODE-001` | Clean activation creates one expected resource set. |
| `ZC-AT-MODE-002` | Activating the already-active mode has a defined idempotent result. |
| `ZC-AT-MODE-003` | Mode A retires before mode B becomes authoritative. |
| `ZC-AT-MODE-004` | Forced mid-activation failure rolls back all provisional resources. |
| `ZC-AT-MODE-005` | Delayed work from a retired generation performs no mutation. |
| `ZC-AT-MODE-006` | Foreign hooks/timers/commands/entities remain registered. |
| `ZC-AT-MODE-007` | 100 activation/deactivation cycles keep resource and retained-memory counts stable within defined tolerance. |
| `ZC-AT-MODE-008` | Disconnect and entity removal do not retain invalid objects. |
| `ZC-AT-MODE-009` | Missing optional capability degrades cleanly; missing required capability prevents commit. |
| `ZC-AT-MODE-010` | Diagnostics are authorized, read-only, and redact closures/private state. |
| `ZC-AT-MODE-011` | Lua refresh does not duplicate direct or projected resources. |
| `ZC-AT-MODE-012` | Legacy dispatcher results and multi-return behavior remain compatible during migration. |

## Evidence still required

- exhaustive stock-mode function and direct-resource inventory;
- runtime transition traces for every shipping mode;
- partial include/load failure fixtures;
- map cleanup, shutdown, and Lua-refresh behavior;
- `MODE.saved` consumers and migration requirements;
- mode chance readers/writers and persistence behavior;
- spawn, role, loadout, and spectator outcomes per mode.

## Implementation boundary

This comparison justifies project-owned generations, explicit activation, owned resources, rollback, and diagnostics. It does not justify importing Trauma’s lifecycle runtime, interceptors, spawn assumptions, V1/V2 CustomGM layers, or persistent-event allowlists.
