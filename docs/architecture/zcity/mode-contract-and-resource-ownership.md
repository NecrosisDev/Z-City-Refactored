# Z-City Mode Contract and Resource Ownership Boundary

**Status:** Verified loader behavior plus proposed migration contract. Stock-mode method and direct-resource enumeration remains incomplete.

## Scope

This document converts the verified behavior of `gamemodes/zcity/gamemode/loader.lua` into a bounded migration contract. It does not claim that stock modes already satisfy the contract. It defines the evidence that must be collected before a mode, lifecycle callback, hook, timer, receiver, command, or retained state can move into the new project.

Related documents:

- `mode-and-round-lifecycle.md`
- `mode-method-dispatch-and-hot-reload.md`
- `player-class-inventory-equipment-boundary.md`
- `verified-defects.md`
- `../sources/trauma-lifecycle-assessment.md`
- `../../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`

## 1. Verified current publication behavior

The current loader creates a temporary global `MODE` table for each top-level mode file or directory. After inclusion and optional inheritance, it stores that table under `zb.modes[MODE.name]`.

Every direct function value in the resulting mode table is then published through the global hook system. Publication is automatic and does not distinguish intent. A function may represent:

- an engine hook;
- a round lifecycle callback;
- a policy query;
- a direct coordinator entry point;
- an administrative operation;
- a utility;
- an internal helper.

The hook identifier is based only on the function name. The dispatcher selects the active mode at call time through `zb.CROUND_MAIN`, then `zb.CROUND`, then the `tdm` fallback.

The current loader also preserves only `MODE.saved` explicitly across reload. Direct resources created while including a mode file are outside this retained-state mechanism.

## 2. Why a method inventory is not enough

A mode can affect runtime behavior through at least four independent surfaces:

1. **Projected methods** — direct functions stored on `MODE` and automatically exposed as hook handlers.
2. **Direct resources** — hooks, timers, receivers, commands, globals, entities, constraints, files, or other registrations created during include or later callbacks.
3. **Direct callers** — round, player, spawn, inventory, equipment, networking, or administrative code calling mode methods without `hook.Run`.
4. **Retained state** — `MODE.saved` plus any undeclared state retained in globals, entities, registries, timers, closures, files, or external addons.

A safe migration requires all four surfaces to be recorded together. Classifying only the method name cannot establish invocation count, active lifetime, authority, cleanup, or rollback behavior.

## 3. Required stock-mode inventory record

Each stock mode must receive one inventory record with the following fields.

### 3.1 Identity

- stable mode identifier;
- source file or directory;
- realm or realms;
- base mode, if any;
- inheritance depth;
- registration order;
- active aliases or compatibility names;
- whether it can be selected as main, submode, override, or fallback.

### 3.2 Method record

Every function present after inheritance must record:

- function name;
- defining source;
- inherited or overridden status;
- intended classification;
- projected hook name;
- direct callers;
- matching `hook.Run` or engine emitter;
- argument contract;
- return contract;
- nil/non-nil return significance;
- server/client/shared realm;
- authority level;
- mutation targets;
- resources created;
- cleanup responsibility;
- activation assumptions;
- required ordering;
- compatibility tests.

### 3.3 Direct resource record

Every directly registered resource must record:

- resource type;
- external identifier;
- owner mode;
- source path and line;
- realm;
- registration phase;
- active lifetime;
- replacement behavior;
- cleanup action;
- cleanup trigger;
- hot-reload behavior;
- stale-generation behavior;
- failure behavior;
- diagnostic visibility.

### 3.4 Retained-state record

Every retained value must record:

- schema name and version;
- storage location;
- writer and readers;
- owner lifetime;
- migration function;
- default construction;
- validation rules;
- rollback representation;
- whether clients may observe it;
- whether it survives mode deactivation, Lua refresh, map cleanup, or shutdown.

## 4. Method classification

New modes must declare each callable under one of the following categories.

### 4.1 Engine event

A Garry's Mod hook with a documented emitter and return contract.

Requirements:

- explicit event name;
- explicit realm;
- declared priority/order policy;
- bounded return semantics;
- no hidden direct invocation unless separately declared.

### 4.2 Round lifecycle callback

A callback invoked by the round coordinator, such as prepare, start, think, finish, cleanup, intermission, or equipment phases.

Requirements:

- one declared coordinator owner;
- activation-generation check;
- defined reentrancy behavior;
- idempotent cleanup or an explicit single-use guarantee;
- result and failure record.

### 4.3 Policy query

A side-effect-free decision function used for spawn, team, class, preservation, equipment, damage, victory, or eligibility decisions.

Requirements:

- deterministic inputs;
- no registration or entity mutation;
- bounded return schema;
- explicit fallback when absent or invalid.

### 4.4 Command

An operation intentionally requested by another subsystem.

Requirements:

- explicit caller;
- permission and expected-state checks where client- or admin-originated;
- transactional result;
- no automatic hook publication.

### 4.5 Utility

A pure or bounded helper that is not part of the public mode lifecycle.

Requirements:

- not projected into hooks;
- not callable by ambient name;
- source-local by default;
- exported only through an explicit private/public interface.

### 4.6 Adapter callback

A capability integration with an optional provider such as Glide, VJ Base, DynaBase, vFire, ULX, or another addon.

Requirements:

- capability detection;
- inert behavior when absent;
- provider-specific code outside core mode authority;
- independent cleanup and diagnostics;
- no bundled vendor implementation inside the mode contract.

## 5. Explicit owner scope

Every new-mode resource must be attached to an owner scope containing at least:

- project subsystem;
- mode identifier;
- activation generation;
- source path;
- realm;
- lifetime;
- resource type;
- internal resource ID.

Recommended logical identity:

```text
mode:<mode-id>:generation:<n>:<resource-type>:<internal-id>
```

External hook, timer, command, or network names may remain compatible during migration, but the ownership registry must retain the complete logical identity.

## 6. Lifetime classes

Resources must declare exactly one lifetime.

### Load lifetime

Exists while the mode definition is loaded, even when inactive. Suitable only for immutable metadata and bounded compatibility adapters.

### Activation lifetime

Exists only while the mode activation generation is current. This is the default for gameplay hooks, timers, entities, constraints, and asynchronous work.

### Round lifetime

Exists for one round generation inside an active mode generation.

### Player/character lifetime

Exists for one player admission or character-representation generation.

### Request/event lifetime

Exists for one command, fire transaction, damage event, snapshot, or asynchronous completion.

### Process lifetime

Exists until shutdown. This must be exceptional and cannot be inferred from an event-name allowlist.

## 7. Prepare, commit, deactivate, and rollback

A new mode activation must use these phases.

1. **Resolve** the requested mode and inheritance graph.
2. **Prepare** immutable definitions and proposed resources without publishing gameplay authority.
3. **Validate** required methods, schemas, capabilities, realms, dependencies, and conflicts.
4. **Commit** one activation generation atomically.
5. **Publish** compatibility projections after the generation is current.
6. **Run** only generation-valid callbacks and tasks.
7. **Deactivate** by preventing new work, cancelling owned tasks, removing resources, and releasing entities/constraints.
8. **Verify cleanup** against the ownership registry.
9. **Migrate retained state** only through declared schema functions.
10. **Rollback** to the prior valid generation when prepare or commit fails.

The old and new activation generations must not both own gameplay authority.

## 8. Delayed and asynchronous work

`timer.Simple`-style anonymous work is not acceptable for new mode code.

Every delayed task requires:

- an internal cancellable ID;
- owner mode and activation generation;
- optional round, player, representation, weapon, or request generation;
- deadline and creation source;
- completion, cancellation, and timeout paths;
- stale-generation rejection before mutation;
- cleanup on mode deactivation and shutdown.

This preserves Trauma's useful generation-guard requirement while rejecting global interception and anonymous ownership.

## 9. Compatibility adapter for legacy modes

Legacy modes may continue to load through the current `MODE` table and projected dispatcher temporarily.

The adapter must:

- snapshot the final inherited mode table;
- classify known methods through an external manifest;
- report unclassified functions;
- report direct resources discovered by static or runtime audit;
- attach observational generation metadata without changing outcomes;
- preserve active-mode precedence and `tdm` fallback;
- preserve method-style invocation and multi-return behavior;
- preserve `MODE.saved` until a versioned migration exists;
- never permanently replace global registration APIs.

Unclassified legacy methods remain compatibility behavior, not approved new architecture.

## 10. Trauma disposition

### Adopt as requirements

- activation generations;
- stale-work rejection;
- lifecycle diagnostics;
- explicit cleanup verification;
- schema-versioned retained-state migration.

### Adapt

- bounded registration capture as temporary audit tooling;
- resource counts and leak reports;
- structured activation/deactivation phases;
- compatibility manifests for legacy modes.

### Rewrite

- ownership APIs;
- method declaration and classification;
- resource registration;
- delayed-task scheduling;
- retained-state storage;
- activation, rollback, and cleanup.

### Reject

- permanent replacement of global `hook.Add`, `timer.Create`, or `timer.Simple`;
- event-name allowlists as lifetime policy;
- automatic hook publication for new mode-table functions;
- undeclared process-lifetime resources;
- parallel old/new mode authority;
- silent continuation after required activation failure.

### Keep Z-City temporarily

- current mode names and inheritance outcomes;
- active-mode precedence;
- `tdm` fallback;
- method-style callback invocation;
- first-return-value gating and multi-return propagation;
- `MODE.saved` compatibility;
- existing packet and hook projections until consumers migrate.

## 11. Acceptance requirements

Before replacing the legacy dispatcher, tests must prove:

1. every stock mode method is classified;
2. inherited and overridden methods resolve identically;
3. direct callers and hook emitters do not cause unintended duplicate execution;
4. return values match current behavior;
5. inactive modes cannot mutate gameplay through activation-lifetime resources;
6. deactivation removes all owned hooks, timers, receivers, commands, entities, and constraints;
7. delayed work from an old generation cannot mutate a new generation;
8. failed activation leaves the prior valid mode authoritative;
9. retained state migrates or rolls back deterministically;
10. hot reload does not duplicate direct resources;
11. server/client mode generations converge;
12. missing optional adapters do not prevent core mode activation;
13. required dependency failures are explicit and fail closed;
14. legacy compatibility projections remain available during migration;
15. ownership diagnostics report zero leaked activation resources after cleanup;
16. map cleanup and shutdown release all non-process resources.

## 12. Remaining evidence work

The following work is still required before production implementation:

- enumerate every stock mode file and inherited method;
- locate every direct caller and matching hook emitter;
- enumerate direct hooks, timers, receivers, commands, globals, entities, and constraints;
- identify all `MODE.saved` schemas and undeclared retained state;
- record mode-specific spawn, class, inventory, equipment, preservation, victory, and cleanup behavior;
- build fixtures for each stock mode and inheritance branch;
- verify runtime load order and duplicate invocation behavior.

Repository-wide code search was unavailable during this pass. This document therefore defines the verified loader boundary and required evidence schema without claiming exhaustive stock-mode coverage.