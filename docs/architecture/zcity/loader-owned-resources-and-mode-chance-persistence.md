# Z-City Loader-Owned Resources and Mode-Chance Persistence

**Status:** Verified from `gamemodes/zcity/gamemode/loader.lua`. This is a bounded loader inventory, not a complete stock-mode resource inventory.

## Scope

This document records the resources created directly by the gamemode loader, their current lifetime, trust boundary, persistence behavior, failure behavior, and required migration treatment. It advances the mode-resource inventory without claiming that resources registered inside individual stock modes have been enumerated.

Primary source:

- `gamemodes/zcity/gamemode/loader.lua`

Related documents:

- `mode-and-round-lifecycle.md`
- `mode-method-dispatch-and-hot-reload.md`
- `mode-contract-and-resource-ownership.md`
- `verified-defects.md`
- `../sources/trauma-lifecycle-assessment.md`
- `../../decisions/ADR-0001-EXPLICIT_MODE_LIFECYCLE_OWNERSHIP.md`
- `../../decisions/ADR-0004-DECLARED_MODE_CALLABLES_AND_OWNED_RESOURCES.md`

## 1. Loader-owned resource inventory

| Resource | External identity | Realm | Current lifetime | Current owner | Removal/reconciliation |
|---|---|---|---|---|---|
| projected mode hook dispatcher | `zb_modehook_<function-name>` | shared by included realm | Lua-state/process lifetime | implicit loader singleton | no explicit removal; repeated registration replaces same hook identifier |
| mode callback registry | `zb.modesHooks[mode][function-name]` | shared by included realm | loader generation | implicit global table | table is replaced wholesale when loader executes |
| loaded mode registry | `zb.modes[mode]` | shared by included realm | Lua-state with selected retained field | implicit global table | mode entry is replaced; only prior `saved` table is preserved explicitly |
| persisted chance table | `zb.ModesChances` | server | Lua-state plus DATA-file persistence | implicit loader singleton | table is rebuilt from disk when modes load |
| chance DATA file | `data/zbattle/modeschances.json` | server | map/process persistent | implicit loader singleton | written on first creation, explicit save, and shutdown |
| shutdown save hook | hook `ShutDown`, id `savechances` | server | Lua-state/process lifetime | implicit loader singleton | no explicit removal; same identifier replaces on refresh |
| inspect command | `zb_getmodeschances` | server | Lua-state/process lifetime | implicit loader singleton | no explicit removal/reconciliation |
| mutate command | `zb_setmodechance` | server | Lua-state/process lifetime | implicit loader singleton | no explicit removal/reconciliation |
| save command | `zb_savemodeschances` | server | Lua-state/process lifetime | implicit loader singleton | no explicit removal/reconciliation |
| temporary mode authoring global | `MODE` | current include realm | one top-level load attempt | loader ambient state | set before include and cleared only after `InitMode()` returns |
| accidental inheritance scratch global | `tbl2` | current include realm | Lua-state until overwritten | none | never explicitly cleared |

## 2. Projected hook-dispatcher lifetime

For every direct function found on the final inherited mode table, the loader:

1. stores the function under `zb.modesHooks[MODE.name][hookName]`;
2. calls `hook.Add(hookName, "zb_modehook_" .. hookName, dispatcher)`;
3. resolves the active mode inside the dispatcher at invocation time.

The external hook identity contains only the function name. It does not encode:

- defining mode;
- source path;
- realm;
- loader generation;
- activation generation;
- method classification;
- intended lifetime.

Repeated registration of the same function name replaces the dispatcher under the same hook identifier. This avoids one class of duplicate hook execution, but it also destroys provenance and does not remove dispatchers for function names absent from the new loader generation.

An old dispatcher can therefore remain installed while becoming inert because the rebuilt `zb.modesHooks` table no longer contains its callback. It can become behaviorally active again if the registry is later repopulated under that function name.

## 3. Loader generation is implicit

Executing the loader creates a new effective loader generation, but no generation number or immutable load result exists.

Observed replacement behavior:

- `zb.modesHooks` is always replaced with a new table;
- `zb.modes` is reused when already present;
- each loaded mode entry is replaced;
- the prior mode entry contributes only its `saved` table;
- hook dispatchers are replaced only for names encountered during the new load;
- loader-owned commands and the shutdown hook are re-registered ambiently;
- no commit record states that all required modes loaded successfully.

There is no explicit prepare/validate/commit boundary. Consumers can observe a mixture of old and new state while files are being included and mode entries are being replaced.

## 4. Temporary global cleanup is not exception-safe

For each top-level mode file or folder, the loader assigns `MODE = {}`, includes the source, calls `InitMode()`, and then assigns `MODE = nil`.

The cleanup assignment is not protected by a structured failure boundary. If an include, inheritance operation, setup callback, or hook publication raises an error before control returns, the temporary global may remain populated with a partial mode definition.

The nested-table inheritance copy also assigns `tbl2 = {}` without `local`, producing an unrelated global scratch table that survives the load attempt.

These globals are not acceptable ownership mechanisms in the target architecture. Legacy loading must isolate them inside a compatibility boundary and report incomplete attempts.

## 5. Mode-chance data flow

### 5.1 Read

On the server, `LoadModes()` reads `data/zbattle/modeschances.json` and decodes it with `util.JSONToTable`. Missing, empty, or malformed content falls back to an empty table.

The implementation does not retain a diagnostic distinction between:

- first run;
- missing file;
- empty file;
- malformed JSON;
- valid empty object.

### 5.2 Per-mode initialization

During `InitMode()`:

- `MODE:SetupChances()` is called when present;
- otherwise `zb.ModesChances[name]` keeps its existing value or receives `MODE.Chance`.

This means a mode-defined setup callback can mutate the shared chance registry during load, before a complete loader generation has been validated.

There is no verified schema requiring chance values to be finite, non-negative, bounded, normalized, or associated with a known selectable mode.

### 5.3 Administrative read

`zb_getmodeschances` requires `ply:IsAdmin()` and prints the complete table as JSON through `zChatPrint`.

The command provides no structured version, source revision, validation status, or separation between known and stale keys.

### 5.4 Administrative mutation

`zb_setmodechance` requires `ply:IsAdmin()`, reads a mode key and `tonumber(args[2])`, then writes the value when the key already exists and conversion succeeds.

The command does not visibly reject:

- negative values;
- very large values;
- non-finite numeric values where representable by the runtime;
- modes that exist in persistence but are no longer loadable;
- values that make selection policy degenerate.

Mutation is in memory only until explicit save or shutdown.

### 5.5 Save

The table is serialized with `util.TableToJSON(..., true)` and written directly to the final DATA path:

- when no file exists after mode loading;
- through `zb_savemodeschances`;
- from the `ShutDown` hook.

There is no temporary-file write, validation readback, revision check, backup, or recovery path. A failed or partial write can leave the persistence contract ambiguous on the next load.

## 6. Authority and trust boundary

The chance table is server-authoritative, and all visible console commands require admin status. That is the correct broad authority direction, but the current contract is incomplete.

Required target checks:

- authenticated server-side principal;
- explicit permission capability rather than only a broad admin boolean;
- bounded mode identifier;
- mode existence and selectability validation;
- finite numeric value;
- configured minimum/maximum;
- revision or expected-generation check for concurrent edits;
- structured success or rejection result;
- audit record for mutation and save;
- transactional persistence.

Client code must never authoritatively mutate selection weights.

## 7. Current failure and hot-reload behavior

| Event | Current behavior | Risk |
|---|---|---|
| malformed chance JSON | silently becomes `{}` | valid prior policy can be lost on next save |
| mode include failure | earlier registrations remain; no load result | partial loader generation can become observable |
| `SetupChances` failure | load aborts after prior mutations | shared registry can be partially changed |
| removed mode | stale DATA key can remain | administration and selection diagnostics can disagree with loaded modes |
| added mode | receives prior value or `MODE.Chance` | default provenance is not recorded |
| Lua refresh | tables and registrations are rebuilt ambiently | no generation comparison or cleanup verification |
| shutdown save failure | no verified fallback | latest in-memory policy may be lost |
| concurrent admin edits | last write in memory wins | no revision conflict detection |

## 8. Trauma comparison

Trauma's lifecycle attempt contains useful requirements for registration ownership, generation guards, diagnostics, and cleanup verification. Those requirements apply here, but its broad interception approach is not justified.

### Adopt as requirements

- explicit loader and activation generations;
- owner/source/realm metadata;
- stale-generation rejection;
- resource and persistence diagnostics;
- cleanup verification;
- versioned retained schemas.

### Adapt

- registration observations as temporary migration tooling;
- resource-count and leak reports;
- structured lifecycle phase records;
- validated configuration snapshots.

### Rewrite

- loader result and atomic publication;
- mode-chance schema and mutation API;
- transactional persistence;
- command authorization and result reporting;
- hook/command ownership registration;
- legacy `MODE` isolation and failure cleanup.

### Reject

- permanent replacement of global hook, timer, command, or file APIs;
- silent continuation after required mode-load failure;
- event-name allowlists as ownership policy;
- unversioned shared configuration tables;
- client-authoritative chance mutation;
- whole-table replication as a configuration protocol.

### Keep Z-City temporarily

- DATA path `zbattle/modeschances.json`;
- current mode keys and effective chance values;
- current admin-only access direction;
- `SetupChances` and `MODE.Chance` outcomes;
- save-on-shutdown behavior;
- projected hook names and dispatcher return behavior.

Compatibility retention does not endorse the current implementation. It prevents migration from changing mode selection before fixtures exist.

## 9. Target loader resource contract

A replacement loader must produce an immutable result containing at least:

- loader generation;
- source revision;
- realm;
- discovered mode definitions;
- resolved inheritance graph;
- validation results;
- proposed resources;
- retained-state migration results;
- chance-config snapshot and schema version;
- diagnostics;
- commit or rollback result.

Publication must be atomic from the perspective of gameplay consumers. No mode becomes authoritative until required definitions, inheritance, capabilities, and configuration validate.

Loader-owned resources must be registered through an explicit process-lifetime owner scope. Mode gameplay resources must use activation or round lifetime and cannot be owned by the loader singleton merely because they were discovered during loading.

## 10. Target chance-config contract

The configuration should retain compatibility values while moving to a versioned schema, for example:

```text
schema_version
revision
updated_at
updated_by
modes[mode_id].weight
modes[mode_id].enabled
modes[mode_id].source_default
modes[mode_id].validation_status
```

Required operations:

1. load and parse into a candidate snapshot;
2. validate schema and values;
3. reconcile loaded modes and stale keys without destructive silent deletion;
4. publish one immutable in-memory revision;
5. mutate through validated commands with expected revision;
6. write to a temporary path;
7. read back and validate;
8. atomically replace the final file where the platform permits;
9. retain a recoverable previous valid revision;
10. report save and recovery status.

## 11. Acceptance requirements

Before replacing the loader-owned resource path, tests must prove:

1. cold load produces one complete loader result;
2. missing, empty, malformed, and valid chance files are distinguishable;
3. all loaded modes receive the same effective weights as the compatibility path;
4. stale keys are reported without silently affecting selectable modes;
5. invalid numeric values are rejected;
6. non-authorized callers cannot inspect or mutate protected configuration;
7. failed mode preparation leaves the prior generation authoritative;
8. failed chance mutation does not change the published revision;
9. failed persistence retains a recoverable valid file;
10. shutdown save reports failure without corrupting the last valid revision;
11. Lua refresh does not leave stale projected hooks, commands, or globals;
12. removed function names do not leave unattributed dispatchers;
13. the temporary legacy `MODE` value is cleared after success and failure;
14. no inheritance scratch globals are created;
15. server and client loader generations identify the same compatible mode definitions;
16. ownership diagnostics attribute every loader-owned resource;
17. stock mode selection outcomes remain unchanged under recorded fixtures.

## 12. Remaining evidence work

Still required:

- enumerate every stock mode and its `SetupChances` or `Chance` behavior;
- identify the selection algorithm consuming `zb.ModesChances`;
- enumerate all direct writers/readers of `zb.ModesChances`;
- verify console-command behavior for server console or invalid player objects;
- verify DATA write semantics and failure signals in the target runtime;
- enumerate all stale projected hook identifiers after a controlled reload;
- complete individual stock-mode direct-resource inventories.

Repository-wide code search remained unavailable during this pass. No exhaustive absence claim is made.