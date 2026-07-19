# Z-City Mode Method Dispatch and Hot-Reload Boundary

**Status:** Observed from the current repository implementation. Runtime verification and complete mode-method enumeration remain required.

## Scope

This document isolates the registration boundary created by `gamemodes/zcity/gamemode/loader.lua`. It distinguishes:

- mode-table methods projected into Garry's Mod hooks;
- direct side effects registered by mode files;
- data intentionally retained across Lua refreshes;
- dispatch state rebuilt during reload;
- lifecycle behavior that Trauma attempted to formalize;
- requirements for a replacement that preserves current gameplay without adopting Trauma as the baseline.

Primary source:

- `gamemodes/zcity/gamemode/loader.lua`

Related baselines:

- `mode-and-round-lifecycle.md`
- `player-class-inventory-equipment-boundary.md`
- `verified-defects.md`
- `../sources/trauma-lifecycle-assessment.md`
- `../../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`

## 1. Loader phases relevant to lifecycle ownership

The current loader executes these phases in order:

1. recursively include `zcity/gamemode/libraries`;
2. reset `zb.modesHooks` to a new empty table;
3. preserve `zb.modes` when it already exists;
4. define one global dispatcher registration helper;
5. read persisted mode chances on the server;
6. load each top-level mode file using a temporary global `MODE` table;
7. load each top-level mode directory using the same temporary global;
8. register the resulting mode table;
9. project every directly stored function into the hook system;
10. write initial chance persistence when absent.

This is both a bootstrap path and an implicit hot-reload path. It does not declare a separate unload, deactivate, refresh, or rollback phase.

## 2. Dispatch registry

`addModeHook(MODE, hookName, func)` stores callbacks under:

```text
zb.modesHooks[modeName][hookName]
```

It then calls:

```text
hook.Add(hookName, "zb_modehook_" .. hookName, dispatcher)
```

The hook identifier depends only on the function/event name, not on:

- mode name;
- load generation;
- source file;
- realm;
- activation generation;
- owner lifetime.

Repeated registration of the same hook name replaces the same dispatcher identifier rather than creating one dispatcher per mode. The replacement dispatcher consults the rebuilt `zb.modesHooks` table at call time.

## 3. Active callback resolution

When a projected hook runs, the dispatcher selects:

1. `zb.CROUND_MAIN` when present;
2. otherwise `zb.CROUND`;
3. otherwise the hard-coded fallback `tdm`.

It then finds the callback for the selected mode and hook name, retrieves the current mode table, invokes the callback with that table as the first argument, and returns up to six values only when the first value is non-`nil`.

### Compatibility requirements

A replacement must preserve until migrated and tested:

- active-mode precedence;
- the `tdm` fallback;
- method-style invocation with the mode table as `self`;
- first-return-value gating;
- propagation of multiple return values;
- inactive modes not receiving projected callbacks.

## 4. Automatic method projection

`InitMode()` iterates every direct key/value pair in `MODE`. Every value for which `isfunction(value)` is true is sent to `addModeHook`.

There is no declaration separating:

- Garry's Mod engine hooks;
- Z-City lifecycle callbacks;
- round coordinator entry points;
- mode utilities;
- data transformation helpers;
- administrative helpers;
- internal implementation functions.

Therefore function placement in the mode table is itself the hook-publication mechanism.

### Consequences

- A utility named like an engine event becomes globally callable through `hook.Run`.
- A lifecycle method can be invoked both directly by Z-City code and indirectly through the hook system.
- Renaming a helper can change global dispatch behavior.
- Adding a function to mode data is a runtime registration change even when the author intended only local reuse.
- Tooling cannot classify intent from the table shape alone.
- Complete parity work requires enumerating method names and all direct calls plus matching `hook.Run` sites.

## 5. Duplicate invocation risk

The loader does not prove that a projected method is intended to run only through the global hook dispatcher.

Methods such as round lifecycle, equipment, spawn, and intermission functions can also be called directly by round or player orchestration. When another system emits a hook with the same name, the same logical operation may be reachable through both paths.

This document does not claim that every method is currently double-executed. It establishes that the architecture permits duplicate reachability and lacks metadata to prove or prevent it.

Required audit tuple for each mode function:

```text
mode
method name
source path
realm
direct callers
matching hook emitters
return contract
side effects
expected lifetime
idempotence
```

## 6. Hot-reload state retention

Before replacing a mode table, `InitMode()` reads:

```text
zb.modes[name].saved
```

when a previous mode exists. The old `saved` table is then attached to the newly loaded mode table.

This is the only explicit mode-local hot-reload preservation contract visible in the loader.

### Preserved

- the previous mode's `saved` table reference or value;
- `zb.modes` as a registry object when it already exists;
- mode chance state loaded from disk or retained elsewhere.

### Rebuilt or replaced

- `zb.modesHooks`, which is assigned a new empty table on loader execution;
- each loaded mode table stored at `zb.modes[name]`;
- projected hook dispatchers for function names encountered during the current load;
- chance setup performed by the current mode definition.

### Not explicitly reconciled

- direct hooks registered inside mode files;
- named timers created by mode files;
- anonymous delayed callbacks;
- net receivers;
- console commands;
- convars;
- entity callbacks;
- globals;
- cached player/entity references;
- constraints or spawned entities;
- files or persisted data outside `mode.saved`;
- callbacks removed from a newer mode definition.

## 7. Stale projected hook names

`zb.modesHooks` is reset, so an old dispatcher whose method name is not encountered during the new load remains registered in Garry's Mod's hook table unless explicitly removed elsewhere.

Its closure reads the current `zb.modesHooks`. Because the rebuilt table lacks the removed method, the dispatcher normally becomes inert. It is nevertheless still a globally registered resource with no declared owner, source, or unload event.

This distinction matters:

- stale projected dispatchers may not execute mode code;
- they still remain untracked global registrations;
- diagnostics cannot distinguish current, inert, replaced, or leaked dispatchers;
- an unrelated later mutation of `zb.modesHooks` can make an old hook name active again.

## 8. Partial-load behavior

Mode files execute directly against a temporary global `MODE`. `InitMode()` has no protected phase transaction.

If inclusion or initialization fails after earlier side effects:

- already registered direct resources remain;
- the previous mode table may remain or be partially replaced depending on failure location;
- the temporary global can retain invalid state until surrounding execution unwinds;
- `zb.modesHooks` may already have been reset;
- some projected dispatchers may point at the new registry while others have not yet been registered;
- `saved` state has no schema/version validation.

A future loader must not treat `pcall` plus continuation as sufficient. Critical mode activation requires prepare, validate, commit, and rollback phases.

## 9. Realm duplication

The loader runs in both server and client realms. Shared mode files can therefore publish same-named projected hooks independently in each realm.

Ownership records must include realm. A hook existing on both sides is not one shared resource; it is two independent registrations with different call sites, state, failure modes, and cleanup requirements.

## 10. Persistence boundary

The loader currently contains two distinct persistence mechanisms:

### Mode-local transient persistence

`MODE.saved` carries data between hotloads in memory.

### Server data persistence

`zb.ModesChances` is read from and written to:

```text
data/zbattle/modeschances.json
```

These mechanisms have no shared schema, version, migration, atomic write, ownership, or validation contract.

The replacement architecture should distinguish:

- hot-reload continuity data;
- round-persistent data;
- map-persistent data;
- server-persistent configuration;
- derived caches that should be discarded;
- runtime resources that must never be serialized.

## 11. Trauma comparison

Trauma attempted to add explicit lifecycle generations, activation/deactivation phases, registration capture, timer/hook ownership, and diagnostics.

### Justified concepts

- explicit activation generation;
- owner/source/realm metadata;
- declared resource lifetime;
- activation and deactivation diagnostics;
- stale-generation rejection;
- structured mode validation before activation;
- bounded migration tooling that reports legacy direct registrations.

### Concepts requiring adaptation

- registration capture can be useful as temporary audit tooling, but should not remain the authority;
- legacy mode methods can be classified and bridged through a compatibility adapter;
- retained state should be schema-versioned and explicitly migrated;
- hook dispatch should use a declared callback manifest rather than table-wide function scanning.

### Rejected concepts

- replacing global `hook.Add` or timer APIs to infer ownership;
- deciding persistent lifetime from hard-coded event-name allowlists;
- allowing captured resources to substitute for explicit registration;
- carrying Trauma's mode implementation forward as the new baseline;
- keeping anonymous delayed work merely because a generation check suppresses its eventual effect.

## 12. Target mode contract

A new mode definition should separate data and executable surfaces:

```text
identity
inheritance/dependencies
capabilities
configuration schema
engine hooks
round lifecycle callbacks
player lifecycle callbacks
spawn policy
equipment policy
network contributors
owned resources
persistent state schema
migration functions
acceptance tests
```

Each callback declaration should include:

```text
name
category
realm
priority/order
return contract
idempotence
allowed side effects
owner lifetime
required capabilities
```

## 13. Activation transaction

Required phases:

1. **Discover** — locate candidate definitions without activating them.
2. **Parse** — build an isolated definition object.
3. **Resolve** — resolve inheritance and dependencies deterministically.
4. **Validate** — validate schemas, callback declarations, realms, and capabilities.
5. **Prepare** — create an inactive owner scope and migration plan.
6. **Commit** — publish the new active generation atomically.
7. **Deactivate previous** — stop new work and release its owned resources.
8. **Migrate retained state** — transfer only declared versioned state.
9. **Verify** — run invariants and report degraded/failed capability state.
10. **Rollback** — restore the previous generation when commit verification fails.

The exact ordering of deactivation versus commit may vary by resource class, but clients and gameplay code must never observe two writable active authorities.

## 14. Compatibility adapter

Legacy modes can remain functional through an adapter that:

- loads the existing global `MODE` shape in an isolated compatibility context;
- classifies known callback names through a maintained manifest;
- records unknown functions without automatically publishing them in new modes;
- preserves existing dispatcher return semantics;
- exposes `CurrentRound()` and current mode tables temporarily;
- projects compatibility hooks only for verified consumers;
- attributes direct legacy registrations as unowned migration debt;
- refuses activation when required base modes or critical callbacks are absent.

The adapter is transitional. New modes should never depend on ambient global capture or automatic publication of every function.

## 15. Required diagnostics

At minimum:

- active mode identity and generation;
- definition source and schema version;
- resolved base/dependencies;
- declared callbacks by category and realm;
- legacy projected callbacks;
- direct unowned registrations detected during migration audits;
- active hooks, timers, delayed tasks, receivers, commands, entities, and constraints by owner;
- retained-state schema and migration result;
- activation/deactivation duration;
- rollback reason;
- stale callback/task rejection counts;
- inert legacy dispatcher count;
- duplicate direct-plus-hook reachability findings.

Diagnostics must not expose private player, inventory, organism, or administrative data to unauthorized clients.

## 16. Acceptance tests

### Dispatch parity

1. Active-mode precedence remains `CROUND_MAIN`, then `CROUND`, then `tdm` during compatibility operation.
2. Inactive modes do not receive projected callbacks.
3. The mode table remains the first callback argument.
4. Multiple return values and first-value gating match current behavior.
5. Server and client callback registries remain realm-separated.

### Classification

6. Every stock mode function is classified as engine hook, lifecycle callback, policy, utility, or legacy unknown.
7. Every direct call and matching `hook.Run` site is linked.
8. A callback reachable through direct and hook paths has an explicit duplicate-execution test.
9. Unknown new-mode functions are not automatically published.

### Reload

10. Reloading an unchanged mode does not increase owned resource counts.
11. Removing a callback leaves no active owned dispatcher.
12. Direct legacy resources are reported and do not silently multiply.
13. Retained state migrates only through declared schema versions.
14. Invalid retained state fails with a structured diagnostic and rollback/fallback policy.
15. A failed candidate load leaves the previous active generation usable.
16. No callback from the failed or previous generation can mutate current state after deactivation.

### Persistence

17. Chance configuration survives valid restart and rejects malformed values predictably.
18. Hot-reload state, round state, map state, and server configuration are stored in distinct declared lifetimes.
19. Atomic-write or recoverable-write behavior is tested for server-persistent mode configuration.

### Ownership

20. Every new-mode hook, timer, delayed task, receiver, command, entity, and constraint has one owner, realm, source, lifetime, and generation.
21. Deactivation releases every owned resource or records a bounded compatibility exception.
22. Diagnostics identify inert legacy dispatchers and direct unowned registrations.

## 17. Current disposition

- **Keep Z-City temporarily:** existing mode tables, active-mode precedence, dispatcher return behavior, `CurrentRound()` compatibility, and `MODE.saved` continuity.
- **Adopt as requirements:** generation identity, explicit ownership metadata, stale-work rejection, validation, diagnostics, and rollback capability.
- **Adapt:** Trauma lifecycle concepts, legacy registration capture as audit tooling, and versioned retained-state migration.
- **Rewrite:** mode registration, method classification, hook publication, activation/deactivation, hot reload, persistence boundaries, and cleanup.
- **Reject:** permanent global API interception, implicit persistence allowlists, automatic function-table publication for new modes, and anonymous unowned delayed work.

## 18. Remaining evidence required

This document establishes loader-level behavior only. The following remain unresolved:

- complete stock mode method inventory;
- every direct caller of each mode method;
- every matching `hook.Run` emitter;
- direct hooks, timers, receivers, commands, globals, entities, and constraints registered by each mode;
- runtime behavior during `lua_refresh` and partial load failure;
- retained `saved` table schemas and consumers;
- client/server differences in mode definitions;
- exact duplicated invocation cases;
- CustomGM and optional adapter interactions.

No production refactor should replace the compatibility dispatcher until this enumeration and its acceptance fixtures are complete.
