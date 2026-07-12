# Active Work Package

> This file contains only the current package and immediate continuation state. Completed detail belongs in commits, pull requests, architecture documents, catalogs, tests, or decision records.

## Identity

- **ID:** `WP-RESEARCH-001`
- **Title:** Build the code-grounded ZCity Refactored architecture baseline
- **Branch:** `docs/architecture-baseline`
- **Pull request:** `#1`
- **Status:** `active research`
- **Knowledge state:** mixed `Verified` and explicitly labeled `Inferred`; comments and inherited documentation remain claims until confirmed in executable code or runtime evidence

## Desired outcome

Produce a self-contained, implementation-ready knowledgebase of the current project before refactoring begins. A future agent must be able to understand each system, its runtime behavior, ownership, contracts, dependencies, failure modes, integration surfaces, and validation procedure without repeating broad project discovery.

## Non-negotiable branch and session rules

- Continue all current research and documentation on `docs/architecture-baseline`; do not create a branch per work package.
- PR `#1` is the single active review surface against `main` during research.
- Historical `chore/agent-knowledge-contract` and closed PR `#2` are obsolete consolidation artifacts; never resume work from them.
- Do not treat lack of permission to merge `main` as a research blocker.
- Continue after every bounded trace until the research baseline and subsequent integration work are complete.
- Preserve every cumulative rule in root `AGENTS.md`.
- Keep chat output to two-sentence TL;DRs; durable detail belongs in the repository.
- Add only the smallest authoritative documentation or regression mechanism that prevents rediscovery, drift, or regression.

## Verified completed research

- Repository layout, addon/gamemode split, subsystem boundaries, namespaces, persistence locations, dependencies, and structural risks: `docs/architecture/PROJECT_SETUP.md`.
- Global addon bootstrap, gamemode bootstrap, realm routing, recursion order, mode assembly, inheritance, hook dispatch, and round startup: `docs/architecture/BOOTSTRAP_AND_LOAD_ORDER.md`.
- Initial system, behavior, and type contracts for bootstrap, mode registration/dispatch, round lifecycle, realm routing, selection, state, `RoundInfo`, queues, and registries: living catalogs.
- Loader roots, effective realms, known runtime trees, engine-discovered trees, and validation instrumentation design: `docs/reference/FILE_MANIFEST.md`.
- Traced globals, hooks, network channels, convars, commands, persistence, trust boundaries, and overlapping admin protocols: `docs/reference/PUBLIC_SURFACES.md`.
- Mode identities, inheritance, lifecycle, contracts, defects, dependencies, and validation for `tdm`, `cstrike`, `dm`, and `hmcd`: `docs/modes/MODE_CATALOG.md`.
- The repository-local agent contract is consolidated into this branch; `docs/README.md` is the single documentation index.

## High-impact verified findings

### Bootstrap and round framework

- Global and gamemode loaders use different realm and traversal rules; neither explicitly sorts `file.Find` results.
- Unprefixed global-loader files are shared by default; unmarked gamemode-loader files are ignored.
- Mode inheritance requires an already-registered base, while mode-directory enumeration is unsorted.
- Every function-valued `MODE` member is registered as a hook candidate.
- Round states are `0`, `1`, and `3`; comments and mode code still reference stale state `2`.
- The round system contains overlapping admin protocols and duplicate receiver/hook/function registrations; later name-keyed definitions are expected effective but need runtime confirmation.
- Admin list/queue tables lack explicit shape, size, duplicate, and registered-ID validation.

### Modes traced

- Base TDM broadcasts `tdm_start` without a payload while its client reads a string; Counter-Strike inherits the receiver and writes the expected string.
- TDM accepts arbitrary client-requested attachment IDs and does not enforce `TeamBased` buy metadata.
- Counter-Strike's map-point `CanLaunch` validator is overwritten by a later unconditional definition; objective spawning can call `math.random(0)` on empty teams.
- Counter-Strike writes numeric winner IDs through `net.WriteBool`, collapsing team identity.
- Deathmatch divides its zone center by zero with no participants and scans all entities every 0.5 seconds while the zone is active.
- Homicide role selection is hard-disabled, its requested-main-traitor consumer is commented out, and its reset hook waits for stale state `2`.
- Homicide police equipment uses an undefined `gun` variable before declaration, combined with `if math.random(0,1)` conditions that are always truthy in Lua.
- Homicide reinforcement can compare nil `afkTime2` against a number, and its variable network payload lacks a version discriminator.

## Current bounded trace

Complete the mode registry and mode-public-surface baseline before moving into organism/fake-ragdoll/movement.

### Required outputs

1. Finish every Homicide sender/receiver pair, conditional `HMCD_RoundStart` branch, and server `MODE.Types` definition.
2. Discover the exact files and registration key for `homicide_fear`; do not infer names from its directory.
3. Trace all remaining known mode directories into the dependency/lifecycle matrix.
4. Classify every function-valued mode member as lifecycle, engine hook, project hook, data callback, network helper, or internal helper; identify collisions and argument shifts.
5. Finish unresolved Counter-Strike client receivers and bomb/hostage entity contracts.
6. Resolve whether legacy admin queue channels have live clients, external consumers, or no consumers.
7. Update catalogs and inventories atomically with each verified trace.

## Validation requirements

- Cross-check sender and receiver endpoints; never infer payloads from one side.
- Separate expected name-keyed overwrite behavior from runtime-confirmed behavior.
- Verify client-supplied values are bounded, typed, authorized, rate-limited where appropriate, and resolved server-side.
- Verify server/client mode registries agree on network-visible IDs, inherited members, and lifecycle callbacks.
- Review UI, persistence, selection, map points, spawn, team, organism, inventory, appearance, weapon, and entity consumers before classifying a mode contract as complete.
- Introduce no runtime Lua, asset, configuration, or `main` changes during research.

## Risks and evidence gaps

- Static source cannot prove total engine startup order or actual unsorted enumeration order; temporary runtime instrumentation is required.
- Full recursive path enumeration is incomplete because the current connector cannot list directories reliably.
- Effective overwrite behavior for duplicate hooks, receivers, and functions still needs runtime evidence.
- The physical historical branch cannot be deleted through the available connector; it is explicitly obsolete and must not be used.
- No dedicated-server smoke-test evidence has been captured for the current baseline.

## Dependency-ordered continuation

1. Complete every mode, mode payload, inheritance edge, and function classification.
2. Complete the file/realm and public-surface inventories discovered through those modes.
3. Trace organism, fake-ragdoll, movement, and player-class systems.
4. Trace weapons/combat/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator, persistence/admin/security/integrations.
5. Produce the cross-system integration map, regression matrix, verified defect catalog, and implementation-ready remediation packages.
6. Continue through implementation packages on appropriately justified branches only after the research baseline defines their boundaries and the user approves the transition.

## Exact next action

Continue on `docs/architecture-baseline`: finish the remaining Homicide source ranges and payload schemas, discover `homicide_fear` through verified repository evidence, then trace the next unresolved mode without creating another branch or PR.