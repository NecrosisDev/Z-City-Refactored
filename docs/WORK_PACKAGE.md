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
- The global and gamemode loaders use materially different realm-selection and traversal rules.
- Neither loader explicitly sorts `file.Find` output.
- Unprefixed files under the global `lua/homigrad` loader are shared by default, while unmarked files in the gamemode loader are not included by its routing function.
- Mode inheritance requires the base mode to have already been registered.
- Runtime round-state handling uses state `3` for the end period despite conflicting comments that mention state `2`.
- The cumulative agent contract and handoff rules were consolidated into this branch; the duplicate documentation index was removed and `docs/README.md` is canonical.

## Current bounded trace

Populate the living catalogs from already verified bootstrap and round-system evidence, then extend the trace into a complete loaded-file/realm manifest and public-surface inventory.

### Required outputs

1. `docs/SYSTEM_CATALOG.md` entries for global bootstrap, gamemode bootstrap, mode registry/dispatch, and round lifecycle.
2. `docs/BEHAVIOR_CATALOG.md` entries for realm routing, mode selection/dispatch, and round-state progression where observable behavior is established.
3. `docs/TYPE_CATALOG.md` entries for mode tables/registries and round-state identifiers/contracts.
4. Exact source paths and symbols for each claim.
5. Explicit evidence gaps where runtime ordering or behavior cannot be proven from static source alone.
6. Reproducible server-start and round-cycle validation procedures.

## Validation requirements

- Cross-check catalog entries against executable source, not only architecture prose.
- Confirm realm, initialization order, public globals, hooks, commands, convars, network messages, persistence paths, and authoritative data ownership.
- Distinguish static-source verification from runtime verification still required.
- Review adjacent consumers before declaring any contract complete.
- Ensure no runtime Lua, assets, configuration, or `main` changes are introduced during research.

## Risks and evidence gaps

- Source establishes local loader sequences but not the engine-level interleaving between addon autorun, gamemode startup, and all engine callbacks; runtime instrumentation is required for a total order.
- Unsorted `file.Find` enumeration creates implicit ordering dependencies that static inspection can identify but not prove stable across environments.
- Mode functions stored directly on `MODE` may mix engine-hook handlers, lifecycle methods, and internal helpers; consumers must be classified before documenting the public contract.
- The full set of loaded files, globals, hooks, net messages, commands, convars, and data files is not yet inventoried.
- No runtime smoke-test evidence has yet been captured for the current repository baseline.

## Dependency-ordered continuation

1. Verify the source files cited by the two architecture documents and populate the initial system/behavior/type catalog entries.
2. Build the complete loaded-file and realm manifest from both loader trees.
3. Inventory globals, public APIs, hooks, network messages, console variables, console commands, persistence files, and external dependencies.
4. Trace round lifecycle and every registered mode, including inheritance, availability, selection, hooks, state transitions, and cleanup.
5. Continue subsystem-by-subsystem through organism/fake-ragdoll/movement, weapons/combat, inventory/equipment, NPC/bots, UI/camera/spectator, persistence/admin/security/integrations.
6. Finish with a cross-system integration map, verified defects/risks, regression matrix, and dependency-ordered implementation work packages.

## Exact next action

Read the executable loader and round-system sources on this branch, update the three living catalogs with evidence-backed entries, update PR `#1` with the consolidated research scope, then continue into the file/realm manifest without creating another branch.