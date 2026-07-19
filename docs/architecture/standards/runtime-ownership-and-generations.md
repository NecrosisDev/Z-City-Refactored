# Runtime Ownership and Generation Standard

- **Status:** Normative
- **Applies to:** Modes, players, representations, organisms, weapons, adapters, networking, delayed work, persistence, and diagnostics

## Purpose

Z-City currently relies heavily on globals, engine registries, shared mutable tables, entity back-references, and anonymous delayed work. The refactor must make authority, lifetime, cleanup, and stale-work rejection explicit without creating a second parallel runtime.

## Core rule

Every authoritative state object and every removable runtime resource has exactly one owner record.

Compatibility fields, hooks, NWVars, packets, and aliases may project that state. They are not allowed to become independent writers.

## Owner record

The minimum owner record is:

| Field | Requirement |
|---|---|
| `owner_id` | Stable identity within its owner type |
| `owner_type` | Project, loader, mode, round, player, representation, organism, weapon, adapter, or subsystem |
| `generation` | Monotonically increasing incarnation number |
| `realm` | Server, client, or explicitly shared definition |
| `lifetime` | Process, map, mode activation, round, player session, representation, weapon instance, request, or shorter |
| `source` | Registration/creation source when available |
| `state` | Preparing, active, deactivating, removed, failed, or orphaned |
| `created_at` | Runtime timestamp or sequence for diagnostics |
| `parent_owner` | Optional enclosing ownership scope |

A generation identifies an incarnation, not an arbitrary function call. It changes when old delayed work must no longer be allowed to mutate the new state.

## Resource record

Owned resources include:

- hooks;
- named and delayed timers;
- network receivers or request handlers;
- console commands and admin actions;
- ConVar change callbacks;
- entities and constraints;
- file watchers or persistence transactions;
- retained player/entity/function/table references;
- adapter subscriptions;
- custom cleanup callbacks.

Each record includes owner identity, generation, resource type, stable diagnostic name, handle/removal descriptor, source, state, and cleanup result.

## Registration rules

New code must register through typed project APIs that return a handle or owned record.

Required behavior:

1. validate owner and lifetime before registration;
2. prevent accidental duplicate identity within the same owner generation;
3. record successful registration immediately;
4. expose read-only diagnostics;
5. remove in reverse creation order when ordering matters;
6. continue cleanup after individual removal failures;
7. aggregate cleanup failures;
8. make repeated cleanup safe.

Project wrappers must call engine APIs; they must not permanently replace engine globals.

## Delayed work

Direct anonymous `timer.Simple` use is prohibited in new authoritative code.

Use an owned scheduler that records:

- owner and generation;
- stable task name or internal ID;
- scheduled and execution time;
- cancellation handle;
- expected state;
- completion and failure result.

At execution, the task must reject itself when its owner, generation, entity identity, representation, round, weapon instance, or request is no longer current.

Cancellation is still required. Generation checks are a final safety barrier, not a substitute for cleanup.

## Transition protocol

State transitions use explicit phases:

1. **Prepare** — validate inputs and prerequisites without publishing new authority.
2. **Allocate** — create a new generation and provisional ownership scope.
3. **Apply** — create resources and mutate provisional state.
4. **Validate** — check invariants and required outcomes.
5. **Commit** — publish the new authority atomically or at one documented commit point.
6. **Project** — update legacy aliases, packets, NWVars, hooks, or fields from the committed authority.
7. **Retire** — mark the old generation inactive before cleanup.
8. **Cleanup** — remove owned resources and references.
9. **Verify** — assert no duplicate authority, leaks, or stale mutation.

If preparation or application fails, unwind provisional work and preserve the previous committed authority.

## Entity and player identity

Garry’s Mod entity indexes and Lua entity objects are not sufficient long-lived identity by themselves.

Delayed or replicated work involving an entity must include the relevant owner generation and, where needed:

- player session identity;
- representation identity;
- organism owner identity;
- weapon-instance identity;
- round generation;
- adapter/provider generation.

Never assume that a valid entity reference still represents the same logical owner that scheduled the work.

## Network rules

Authoritative snapshots and client requests should include, as applicable:

- schema version;
- owner identity;
- authoritative generation;
- monotonic sequence;
- expected prior generation/state for mutations;
- bounded action enum;
- payload limits;
- visibility classification;
- rate policy;
- rejection reason for diagnostics.

The server rejects stale, malformed, unauthorized, oversized, or state-incompatible requests before expensive work.

Legacy packets may be emitted as compatibility projections. They must be generated from the same committed state and must not update authority independently.

## Persistence rules

Persistent state requires:

- schema and revision;
- validated immutable input snapshot;
- temporary write;
- readback or parse validation;
- atomic replacement where supported;
- backup/recovery policy;
- stale revision rejection;
- migration and downgrade behavior.

Runtime generation and persistent revision are different concepts and must not be conflated.

## Adapter rules

An optional adapter owns only its integration resources. It does not own core player, representation, organism, weapon, or mode state.

Adapters must:

- capability-detect the provider;
- remain inert when absent;
- expose one bounded project-facing interface;
- avoid modifying bundled vendor internals;
- clean up when the provider disappears or reloads;
- reject stale provider generations;
- report degraded capability once, not spam warnings.

## Compatibility rules

During migration:

- legacy globals and methods call or read the new authority;
- legacy fields are updated from one projection point;
- old and new code do not both perform the same side effect;
- telemetry records legacy surface use;
- removal criteria and an observation window are defined.

## Prohibited patterns

New production code must not:

- monkey-patch global registration APIs to infer ownership;
- create unnamed delayed gameplay tasks;
- use a getter to activate or mutate lifecycle state;
- serialize cleanup closures or arbitrary Lua tables to clients;
- let compatibility projections write back into authority;
- retain entities or players beyond owner lifetime without generation checks;
- hide critical failure by silently continuing with partial state;
- make an optional dependency a core authority;
- use event-name allowlists to guess persistence lifetime.

## Required diagnostics

Authorized server diagnostics must be able to report:

- current owners and generations;
- resources by owner/type/state;
- creation source and replacement history;
- stale callback rejections;
- cleanup failures and orphaned resources;
- duplicate authority/projection mismatches;
- adapter capability state;
- retained invalid entity/player references.

Diagnostics are read-only by default and must not expose closures, private organism data, inventories, secrets, or privileged mutation to clients.
