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
- Historical `chore/agent-knowledge-contract` and closed PRs `#2`/`#3` are obsolete consolidation artifacts; never resume work from them.
- The research branch history was squashed into one intentional baseline commit, then continued with grouped research commits; do not recreate the prior fragmented history.
- Do not treat lack of permission to merge `main` as a research blocker.
- Continue after every bounded trace until the research baseline and subsequent integration work are complete.
- Preserve every cumulative rule in root `AGENTS.md`.
- Keep chat output to two-sentence TL;DRs; durable detail belongs in the repository.
- Add only the smallest authoritative documentation or regression mechanism that prevents rediscovery, drift, or regression.

## Verified completed research

- Project structure, bootstrap/load order, realm routing, mode registration, round lifecycle, shared system/behavior/type contracts, file-manifest boundaries, and core public surfaces are documented in the architecture, living catalog, and reference files linked from `docs/README.md`.
- Core mode catalog: `tdm`, `cstrike`, `dm`, and `hmcd`.
- Team/PvE catalog: `hl2dm`, `coop`, and `defense`.
- Additional standalone catalog: `riot`, `gwars`, `superfighters` (directory `sfd`), and `scugarena` (files named `*_arena.lua`).
- Every catalog entry includes source blobs, lifecycle, public contracts, cross-system dependencies, verified defects, evidence gaps, and validation requirements.
- The canonical documentation index is `docs/README.md`; no duplicate index or per-mode document proliferation is permitted.

## High-impact verified findings

### Bootstrap and round framework

- Global and gamemode loaders use different realm/traversal rules; neither explicitly sorts `file.Find` results.
- Unprefixed global-loader files are shared by default; unmarked gamemode-loader files are ignored.
- Mode inheritance requires an already-registered base, while mode-directory enumeration is unsorted.
- Every function-valued `MODE` member is registered as a hook candidate, including helpers and dot-defined functions whose arguments are shifted by dispatcher-injected `self`.
- Round states are `0`, `1`, and `3`; comments and mode code still reference stale state `2`.
- The round system contains overlapping admin protocols and duplicate receiver/hook/function registrations; later name-keyed definitions are expected effective but need runtime confirmation.
- Admin list/queue tables lack explicit shape, size, duplicate, and registered-ID validation.

### Recurrent mode defects

- Multiple sender/receiver schema mismatches: base TDM start, HL2DM end, Counter-Strike winner encoding, Defense wave countdown and Homicide variable payloads.
- Several launch checks are unconditional or overwritten despite required map points, teams, nav areas, objectives, or spawns.
- Delayed callbacks commonly capture invalidatable players/entities without checks and may resample winners after the authoritative end transition.
- Inventory, organism, appearance, weapon and class APIs are frequently assumed to return initialized/valid state.
- Repeated misspelling `OverideSpawnPos` appears in Riot and Gang Wars; framework consumer is not yet traced.
- Several modes scan all entities repeatedly or perform overbroad cleanup, creating performance and integration risk.
- Many client modes reuse global music/end-menu/state names and remote audio URLs, creating cross-mode state, reliability, licensing, and privacy risks.
- CO-OP listens for `ZB_RoundStart` while the verified core emitter is `ZB_StartRound`.
- Defense depends on unresolved additional files/globals/methods and has client/server channels whose opposite endpoints are not in fetched top-level files.
- Homicide `HMCD_RoundStart` can desynchronize when transmitted traitor count exceeds appearance-backed roster entries.

## Current bounded trace

Finish the remaining mode registry and mode-public-surface baseline, then produce the cross-mode function/payload collision matrix before moving into organism/fake-ragdoll/movement.

### Required outputs

1. Discover exact filenames/registration IDs for unresolved directories (`criresp`, `eventhandler`, `pathowogen`, `homicide_fear`, and any additional mode directories) using executable evidence.
2. Complete all Homicide channel endpoints/type augmentation and Counter-Strike objective entity/client contracts.
3. Enumerate unresolved Defense files and pair support/highlight/wave channels with their senders/receivers.
4. Classify every function-valued mode member as lifecycle, engine hook, project hook, data callback, network helper, or internal helper; identify collisions and argument shifts.
5. Build one cross-mode packet matrix containing channel, writer, reader, ordered schema, authorization, validation, rate/size limits, and duplicate/legacy status.
6. Trace the actual framework consumers for spawn-override flags, `COMMANDS`, map-point fallbacks, `zb.EndMatch`, and emitted round hook names.
7. Update existing grouped catalogs/reference inventories rather than creating per-mode branches or documents.

## Validation requirements

- Cross-check sender and receiver endpoints; never infer payloads from one side.
- Separate expected name-keyed overwrite behavior from runtime-confirmed behavior.
- Verify client-supplied values are bounded, typed, authorized, rate-limited where appropriate, and resolved server-side.
- Verify server/client mode registries agree on network-visible IDs, inherited members, and lifecycle callbacks.
- Review UI, persistence, selection, map points, spawn, team, organism, inventory, appearance, weapon, entity, NPC and cleanup consumers before classifying a mode contract as complete.
- Introduce no runtime Lua, asset, configuration, or `main` changes during research.

## Risks and evidence gaps

- Static source cannot prove total engine startup order, unsorted enumeration order, or effective overwrite behavior; temporary runtime instrumentation is required.
- Full recursive path enumeration remains incomplete because the connector cannot reliably list directories; filename discovery is incremental.
- Physical historical branch deletion is unavailable through the connector; the obsolete branch points to `main` and is explicitly excluded from work.
- No dedicated-server smoke-test evidence has been captured for the current baseline.
- Existing catalog findings identify implementation defects but must not be patched before adjacent contracts and integration boundaries are fully mapped.

## Dependency-ordered continuation

1. Complete every mode, packet, inheritance edge, function classification, and public surface.
2. Complete file/realm and public-surface inventories discovered through those modes.
3. Trace organism, fake-ragdoll, movement, and player-class systems.
4. Trace weapons/combat/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator, persistence/admin/security/integrations.
5. Produce the cross-system integration map, regression matrix, verified defect catalog, and implementation-ready remediation packages.
6. Continue through implementation packages on justified branches only after the research baseline defines their boundaries and the user approves transition from research.

## Exact next action

Continue on `docs/architecture-baseline`: discover and trace the unresolved mode directories using verified filenames, pair the unresolved Homicide/Defense/Counter-Strike network endpoints, and update the existing grouped mode catalogs plus `PUBLIC_SURFACES.md` without creating another branch or PR.