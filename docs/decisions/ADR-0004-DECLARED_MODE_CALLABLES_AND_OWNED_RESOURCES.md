# ADR-0004: Declared Mode Callables and Owned Resources

- **Status:** Accepted
- **Date:** 2026-07-14
- **Scope:** New mode architecture and legacy-mode migration

## Context

The current loader places each mode in a temporary global `MODE` table and automatically projects every direct function in the final inherited table into Garry's Mod hooks. Function placement therefore doubles as public registration.

This behavior does not distinguish engine events, round callbacks, policy queries, commands, utilities, or adapter functions. The same logical method may also have direct callers. Direct hooks, timers, receivers, commands, entities, constraints, globals, and delayed work created by mode code are not owned by the projected dispatcher and are not reconciled by the loader's `MODE.saved` hot-reload continuity.

Trauma attempted to improve lifecycle ownership through activation generations, registration capture, cleanup, and diagnostics. Its useful requirements are separable from its rejected implementation techniques, especially temporary global interception and event-name persistence policy.

## Decision

All new modes will use declared callable contracts and explicit resource ownership. Automatic function-to-hook projection is prohibited for new mode definitions.

Each callable must be declared as exactly one primary category:

- engine event;
- round lifecycle callback;
- policy query;
- command;
- utility;
- adapter callback.

A callable reachable through more than one mechanism must declare each route explicitly and prove that duplicate invocation is either impossible or intentional.

Every runtime resource created by a mode must be registered to an owner scope containing:

- mode identifier;
- activation generation;
- source;
- realm;
- lifetime class;
- resource type;
- internal resource identity.

Resources must declare load, activation, round, player/character, request/event, or process lifetime. Process lifetime is exceptional and cannot be inferred from hook or event names.

Mode activation will use resolve, prepare, validate, commit, publish, run, deactivate, cleanup verification, retained-state migration, and rollback phases. Only one activation generation may own gameplay authority.

Delayed and asynchronous work must be cancellable, attributable, generation-checked, and cleaned up. Anonymous delayed work is prohibited in new mode code.

Retained state must have an explicit schema, version, owner, validation rules, migration function, and rollback representation. `MODE.saved` remains a temporary compatibility projection only.

## Legacy compatibility

Existing modes may continue through the current loader while an external manifest classifies methods and audits resources.

The compatibility adapter must preserve:

- current mode names and inheritance outcomes;
- `zb.CROUND_MAIN`, `zb.CROUND`, then `tdm` precedence;
- method-style invocation;
- first-return-value gating;
- multi-return propagation;
- current `MODE.saved` continuity;
- existing hook and packet projections until consumers migrate.

The adapter may observe registrations for audit purposes, but it must not permanently replace global registration APIs.

Unclassified legacy behavior remains supported compatibility behavior, not approved architecture.

## Trauma disposition

### Adopt

- activation-generation requirements;
- stale-work rejection;
- cleanup verification;
- lifecycle diagnostics;
- retained-state schema migration requirements.

### Adapt

- temporary bounded registration capture for migration evidence;
- resource-count and leak reporting;
- structured activation/deactivation phases.

### Rewrite

- owner APIs;
- callable declarations;
- resource registration;
- delayed-task scheduling;
- activation and rollback implementation;
- retained-state storage.

### Reject

- permanent global `hook` or `timer` interception;
- event-name lifetime allowlists;
- automatic publication of all mode-table functions;
- undeclared process-lifetime resources;
- silent continuation after required activation failure;
- concurrent gameplay authority from old and new generations.

## Consequences

### Positive

- Method intent becomes machine-readable.
- Direct calls and hook emissions can be audited together.
- Cleanup and leak reporting can be complete.
- Hot reload can reject stale work and roll back failed activation.
- Optional integrations can remain inert when absent.
- Acceptance tests can target declared contracts rather than ambient names.

### Negative

- Every stock mode requires a method and resource inventory before migration.
- Compatibility manifests add transitional maintenance cost.
- Existing direct registrations cannot be migrated safely without source and runtime tracing.
- Some current implicit behavior will need explicit policy decisions.

## Acceptance criteria

This decision is implemented only when:

1. all stock mode methods are classified;
2. direct callers and hook emitters are enumerated;
3. direct resources and retained state have owners;
4. activation failure rolls back to a valid prior generation;
5. deactivation leaves no activation-lifetime resources;
6. stale delayed work cannot mutate a new generation;
7. inherited and overridden behavior retains parity;
8. server and client mode generations converge;
9. missing optional adapters do not break core activation;
10. legacy return and dispatch behavior remains covered during migration.

## References

- `../architecture/zcity/mode-method-dispatch-and-hot-reload.md`
- `../architecture/zcity/mode-contract-and-resource-ownership.md`
- `../architecture/sources/trauma-lifecycle-assessment.md`
- `ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `ADR-0002-TRAUMA_IS_EVIDENCE_NOT_BASELINE.md`