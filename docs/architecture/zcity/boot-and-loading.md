# Z-City Boot and Loading

- **Status:** SOURCE-VERIFIED current-behavior map
- **Source baseline:** destination baseline
- **Commit:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Primary path:** `lua/autorun/loader.lua`
- **Realm:** server bootstrap with shared/client distribution effects
- **Last reviewed:** 2026-07-14
- **Exhaustive repository search:** incomplete for all listeners, globals, and lexical-order dependencies
- **Runtime verification:** not performed

## Purpose

The destination loader establishes the global `hg` namespace, declares repository/version metadata, exposes an inert Workshop-content control, recursively includes the `homigrad` source tree, loads `initpost` files after entity initialization, and emits completion hooks and warnings.

This document describes existing destination-baseline behavior. The target contract and comparison with later vanilla and Trauma Clean are defined in `boot-content-and-dependency-contract.md`.

## Current identity

The loader identifies the project as:

- version: `Release 1.4.1`;
- GitHub owner: `uzelezz123`;
- GitHub repository: `Z-City`;
- global root: `hg`;
- primary source root: `homigrad`;
- completion hook: `HomigradRun`.

The repository name `Z-City-Refactored` is not reflected in runtime identity. Existing `hg` compatibility must be preserved during migration, but new project identity must not depend on mutable upstream metadata.

## Realm inference

The loader derives file realm from the first or last three characters of a Lua filename:

- `sv_` or `_sv`: server;
- `sh_` or `_sh`: shared;
- `cl_` or `_cl`: client.

Files with no recognized marker are treated as shared: the server sends them with `AddCSLuaFile`, and both realms include them.

### Consequences

- Realm ownership is implicit.
- A naming error can expose server code or execute code in an unsupported realm.
- Unmarked files cannot be assumed safe merely because they currently work.
- The target default is explicit declaration; grandfathered unmarked files require an audited compatibility list.

## Directory traversal

`IncludeDir` recursively calls `file.Find` for every directory under `homigrad`, includes all `.lua` files, and then recurses into child directories.

No manifest or dependency graph is present.

### Consequences

- Ordering is derived from filesystem enumeration and names.
- Dependencies are hidden in globals and naming conventions.
- A subsystem cannot be loaded or tested independently.
- There is no authoritative list of modules.
- Errors can leave partially initialized global state.

## Runtime sequence

Source-observed sequence:

1. The loader file executes.
2. `Run()` is called immediately.
3. `Run()` sets `hg.loaded = false`.
4. Loading is skipped only for the `ixhl2rp` gamemode.
5. The entire `homigrad` tree is recursively included.
6. `hg.loaded = true` is assigned.
7. `HomigradRun` is emitted.
8. On `InitPostEntity`, the separate `initpost` tree is recursively included.
9. After five seconds, warnings are printed for missing ULX/ULib or single-player use.

The `initpost` boolean check preceding the immediate `Run()` call does not delay normal loading; it is false until the later hook fires.

This sequence is source-derived and must not be labeled runtime parity until executable fixtures verify ordering and refresh behavior.

## Failure behavior

Includes are not protected by `pcall` or an equivalent error collector.

A load error may therefore:

- stop recursive traversal;
- prevent `hg.loaded` from becoming true;
- prevent `HomigradRun` from firing;
- leave earlier files active;
- produce a partially initialized addon with no rollback.

Protected loading alone is not a sufficient fix. Silently continuing after a foundational failure can be worse. The target requires explicit phases, required/optional module classification, owned resources, and fail-closed behavior for critical components.

## Workshop content

The destination loader creates an enabled-by-default replicated ConVar named `hg_loadcontent`. All five `resource.AddWorkshop` calls inside its conditional block are commented out.

Destination effective behavior: the setting does not load content.

Later upstream vanilla commit `3716789` re-enables these five IDs. That delta is documented in `upstream-delta-429ec92-to-3716789.md`; it repairs the immediate mismatch but does not establish the final content architecture.

The target requirement is a validated, revisioned content manifest. The ConVar must truthfully select no manifest or one manifest, and duplicate registrations must be prevented.

## ULX/ULib dependency

After five seconds, the server prints repeated warnings when `ulx` is not a table. The warning states that Z-City will not work properly without ULX and ULib.

Current limitations:

- no capability registry records what becomes unavailable;
- startup is not blocked;
- no adapter boundary isolates ULX-dependent behavior;
- six repeated warning lines add noise without actionable detail;
- gameplay and administrative dependence are not distinguished.

ULX/ULib usage must be classified per capability. Missing administration integration must not automatically invalidate unrelated gameplay.

## Compatibility constraints

A replacement boot system must initially preserve:

- the global `hg` table;
- legacy file availability;
- existing realm conventions long enough to migrate callers;
- `HomigradRun` for existing listeners;
- the current exclusion of `ixhl2rp`, unless intentionally changed;
- `initpost` semantics where behavior depends on initialized map entities;
- the destination load order until parity fixtures authorize migration.

Compatibility surfaces are projections. They must not become a second loader authority.

## Desired migration direction

The loader should become a small compatibility bootstrap that delegates to one project-owned lifecycle:

1. establish immutable project metadata;
2. establish compatibility aliases;
3. validate a module and content manifest;
4. validate realm and dependency declarations;
5. load foundation modules;
6. load shared gameplay services;
7. load server/client modules by explicit realm;
8. initialize optional adapters after capability detection;
9. run post-entity modules;
10. publish structured health and acceptance-test results.

Migration must be incremental. Replacing the loader before documenting hidden load-order dependencies would produce widespread regressions.

## Required next evidence

Before a loader implementation work package can become Ready:

- enumerate all `HomigradRun` listeners;
- enumerate all `hg.loaded` readers and writers;
- index unmarked Lua files and classify their true realms;
- identify files that rely on lexical or filesystem enumeration order;
- enumerate `initpost` modules and required entity-state assumptions;
- classify all ULX/ULib usage by capability;
- map Workshop/content consumers and missing-content failure modes;
- execute boot, partial-failure, disconnect, shutdown, map-cleanup, and Lua-refresh fixtures;
- trace Trauma Clean dependency/bootstrap paths against the current archive.

## Related requirements and tests

The normative requirement and acceptance-test IDs are defined in `boot-content-and-dependency-contract.md`:

- `ZC-REQ-BOOT-001` through `ZC-REQ-BOOT-008`;
- `ZC-AT-BOOT-001` through `ZC-AT-BOOT-010`.

## Related documents

- `boot-content-and-dependency-contract.md`
- `upstream-delta-429ec92-to-3716789.md`
- `../source-baselines.md`
- `../sources/trauma-clean-inventory.md`
- `../standards/evidence-and-testing.md`
- `../standards/runtime-ownership-and-generations.md`
