# Z-City Boot and Loading

> Status: verified against the current `lua/autorun/loader.lua` on the repository default branch. This document describes observed behavior, not desired architecture.

## Purpose

The current loader establishes the global `hg` namespace, declares repository/version metadata, optionally queues Workshop content, recursively includes the `homigrad` source tree, loads `initpost` files after entity initialization, and emits completion hooks and warnings.

## Current identity

The loader currently identifies the project as:

- version: `Release 1.4.1`;
- GitHub owner: `uzelezz123`;
- GitHub repository: `Z-City`;
- global root: `hg`;
- primary source root: `homigrad`;
- completion hook: `HomigradRun`.

This means the repository name `Z-City-Refactored` is not reflected in runtime identity. Existing `hg` compatibility must be preserved during migration, but new project identity should not depend on upstream metadata.

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
- The default should eventually become rejection or explicit declaration, not shared execution.

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

Observed sequence:

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

## Failure behavior

Includes are not protected by `pcall` or an equivalent error collector.

A load error may therefore:

- stop the recursive traversal;
- prevent `hg.loaded` from becoming true;
- prevent `HomigradRun` from firing;
- leave earlier files active;
- produce a partially initialized addon with no rollback.

Protected loading alone is not a sufficient fix because silently continuing after a foundational failure can be worse. The desired design needs explicit phases, required/optional modules, and fail-closed behavior for critical components.

## Workshop content

The loader creates an enabled-by-default replicated ConVar named `hg_loadcontent`. However, all five `resource.AddWorkshop` calls inside its conditional block are commented out.

Current effective behavior: the setting does not load content.

This must be corrected in one of two ways:

- remove/deprecate the setting until content ownership is defined; or
- populate an explicit content manifest and make the setting truthfully control it.

## ULX/ULib dependency

After five seconds, the server prints repeated warnings when `ulx` is not a table. The warning states that Z-City will not work properly without ULX and ULib.

Current limitations:

- no capability registry records what becomes unavailable;
- startup is not blocked;
- no adapter boundary isolates ULX-dependent behavior;
- six repeated warning lines add noise without actionable detail.

The dependency must be classified per subsystem rather than globally assumed.

## Compatibility constraints

A replacement boot system must initially preserve:

- the global `hg` table;
- legacy file availability;
- existing realm conventions long enough to migrate callers;
- `HomigradRun` for existing listeners;
- the current exclusion of `ixhl2rp`, unless intentionally changed;
- `initpost` semantics where behavior depends on initialized map entities.

## Desired migration direction

The loader should eventually become a small compatibility bootstrap that delegates to a project-owned lifecycle:

1. establish immutable project metadata;
2. establish compatibility aliases;
3. load a manifest;
4. validate realm and dependency declarations;
5. load foundation modules;
6. load shared gameplay services;
7. load server/client modules by explicit realm;
8. initialize optional adapters after capability detection;
9. run post-entity modules;
10. publish structured health and self-test results.

This migration should be incremental. Replacing the loader before documenting hidden load-order dependencies would produce widespread regressions.

## Open questions

- Which files rely on lexical load order?
- Which files are unmarked but genuinely realm-specific?
- Which listeners depend on `HomigradRun` timing?
- Which `initpost` modules can become explicit post-entity components?
- Which ULX calls are essential versus administrative conveniences?
- Which Workshop packages are actually required for current content?
- Does hot reload invoke the loader multiple times, and which registrations survive duplication?