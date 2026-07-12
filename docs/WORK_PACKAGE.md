# Active Work Package

> This file contains only the current package and immediate continuation state. Completed detail belongs in commits, pull requests, architecture documents, catalogs, tests, or decision records.

## Identity

- **ID:** `WP-RESEARCH-001`
- **Title:** Build the code-grounded ZCity Refactored architecture baseline
- **Branch:** `docs/architecture-baseline`
- **Pull request:** `#1`
- **Status:** `active research`
- **Knowledge state:** mixed `Verified` and explicitly labeled `Inferred`; no existing comments or legacy documentation are trusted without code evidence

## Desired outcome

Produce a self-contained, implementation-ready knowledgebase of the current project before refactoring begins. A future agent must be able to understand each system, its runtime behavior, ownership, contracts, dependencies, failure modes, integration surfaces, and validation procedure without repeating broad project discovery.

## User corrections governing this package

- All current research and documentation work belongs on this single branch; do not create per-work-package branches.
- PR `#1` is the single review surface against `main` during the research phase.
- Continue researching after each bounded trace; do not treat branch, document, catalog, or PR completion as a stopping condition.
- Preserve every cumulative rule in root `AGENTS.md`.
- Keep chat output to two-sentence TL;DRs; durable detail belongs in the repository.
- Add only the smallest documentation or regression mechanisms that prevent rediscovery, drift, or regression.

## Verified completed research

- Repository layout, addon/gamemode split, subsystem boundaries, namespaces, persistence locations, dependencies, and structural risks are traced in `docs/architecture/PROJECT_SETUP.md`.
- Global addon bootstrap, gamemode bootstrap, realm routing differences, recursion order, mode assembly, inheritance dependency, hook dispatch, and round startup are traced in `docs/architecture/BOOTSTRAP_AND_LOAD_ORDER.md`.
- Initial system, behavior, and type catalogs now describe global bootstrap, gamemode bootstrap, mode registration/dispatch, round lifecycle, realm behavior, mode selection, round state, `RoundInfo`, queues, and shared registry contracts.
- `docs/reference/FILE_MANIFEST.md` records the verified loader roots, effective realm rules, known library/mode/global-system trees, engine-discovered trees, and runtime instrumentation design.
- `docs/reference/PUBLIC_SURFACES.md` records the currently traced globals, hooks, network channels, convars, commands, persistence paths, trust boundaries, and duplicate-registration hazards.
- PR `#2` was merged only into this research branch, consolidating the previously split agent contract; PR `#1` remains the sole review surface against `main`.
- The duplicate `docs/INDEX.md` was removed; `docs/README.md` is the canonical documentation index.

## High-impact verified findings

- The global and gamemode loaders use materially different realm-selection and traversal rules, and neither explicitly sorts `file.Find` results.
- Unprefixed files under the global loader are shared by default, while unmarked files in the gamemode loader are ignored.
- Mode inheritance requires the base mode to have already been registered, and every function-valued mode member becomes a hook candidate.
- Runtime round-state handling uses `0`, `1`, and `3`; comments claiming state `2` are stale.
- Round state and mode are server-authoritative and mirrored through the ordered `RoundInfo` payload.
- `sv_roundsystem.lua` contains duplicated admin mode/queue network registrations, receivers, a hook identifier, and function definitions; later definitions are expected to override earlier ones.
- The later `AdminSetGameMode` eligibility condition is unreachable after its admin guard, so launchability is not enforced by that branch.
- Admin-supplied queue/list tables are decoded without explicit shape, length, or mode-ID validation; one transmitted `forceUpdate` boolean is read but unused.

## Current bounded trace

Complete the effective admin mode/queue public contract and begin the mode-by-mode registration/dependency inventory without leaving this branch.

### Required outputs

1. Locate every sender and receiver for the round/mode/queue channels already listed in `PUBLIC_SURFACES.md`.
2. Determine effective last-writer behavior for duplicated `net.Receive`, hook, and function registrations.
3. Record exact payload schemas, authorization, validation, UI assumptions, and failure modes.
4. Enumerate actual files and `MODE` metadata for each known mode directory, beginning with base/high-dependency modes.
5. Build the first explicit mode dependency graph: mode ID, base, submodes/types, realms, required callbacks, launch conditions, and consumers.
6. Update living catalogs and reference inventories atomically with verified findings.

## Validation requirements

- Cross-check senders and receivers rather than deriving a payload from one endpoint.
- Distinguish name-keyed overwrite behavior expected from Garry's Mod APIs from runtime evidence still required.
- Verify all client-supplied values are bounded, typed, authorized, and resolved before use.
- Verify server/client mode registries agree on network-visible mode identifiers and lifecycle callbacks.
- Review adjacent UI, persistence, round-selection, map-point, spawn, and team consumers before classifying a mode contract as complete.
- Ensure no runtime Lua, assets, configuration, or `main` changes are introduced during research.

## Risks and evidence gaps

- Source establishes local loader sequences but not the engine-level interleaving between addon autorun, gamemode startup, and all engine callbacks; runtime instrumentation is required for a total order.
- Unsorted `file.Find` enumeration creates implicit ordering dependencies that static inspection can identify but not prove stable across environments.
- Mode functions stored directly on `MODE` mix engine-hook handlers, lifecycle methods, and internal helpers; all functions must be classified.
- Full recursive file enumeration is still incomplete because GitHub directory listing is unavailable through the current connector; known paths must be verified incrementally or through a later repository checkout/runtime manifest.
- Effective overwrite behavior for duplicate hooks, net receivers, and functions is strongly implied by name-keyed APIs but still needs runtime confirmation.
- No runtime smoke-test evidence has yet been captured for the current repository baseline.

## Dependency-ordered continuation

1. Finish the admin mode/queue client-server contract and duplicate-registration analysis.
2. Trace base/high-dependency modes, then all remaining mode directories, into a mode dependency and lifecycle matrix.
3. Extend the exact file/realm manifest and public-surface inventory while tracing those modes.
4. Continue subsystem-by-subsystem through organism/fake-ragdoll/movement, weapons/combat, inventory/equipment, NPC/bots, UI/camera/spectator, persistence/admin/security/integrations.
5. Finish with a cross-system integration map, verified defects/risks, regression matrix, and dependency-ordered implementation work packages.

## Exact next action

Inspect the remaining client mode-selection UI and all server round-system definitions for `RequestGameQueue`, `SendGameQueue`, queue notifications, `AdminEndRound`, `AdminSetGameQueue`, and duplicate receivers; update `PUBLIC_SURFACES.md` with effective contracts, then fetch and trace the actual `tdm` and `homicide` mode files as the first dependency roots.