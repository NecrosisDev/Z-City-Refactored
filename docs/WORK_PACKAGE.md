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

Produce a self-contained, implementation-ready knowledgebase of the current project before refactoring begins. A future agent must be able to understand each system, runtime behavior, ownership, contracts, dependencies, failure modes, integration surfaces, and validation procedure without repeating broad discovery.

## Non-negotiable branch and session rules

- Continue all current research and documentation on `docs/architecture-baseline`; do not create a branch per work package.
- PR `#1` is the single active review surface against `main` during research.
- Historical `chore/agent-knowledge-contract` and closed PRs `#2`/`#3` are obsolete consolidation artifacts; never resume work from them.
- The research branch was squashed into one intentional baseline commit and continues through grouped research commits; do not recreate fragmented history.
- Lack of merge permission is not a research blocker.
- Continue after every bounded trace until research and subsequent integration are complete.
- Preserve every cumulative rule in root `AGENTS.md`.
- Keep chat output to two-sentence TL;DRs; durable detail belongs in the repository.
- Add only the smallest authoritative mechanism that prevents rediscovery, drift, or regression.

## Verified completed research

- Project structure, bootstrap/load order, realm routing, mode registration, round lifecycle, shared system/behavior/type contracts, file-manifest boundaries, and public surfaces are documented in the linked architecture/catalog/reference files.
- Every known top-level mode directory now has a verified registry identity or explicit unresolved-file boundary in the grouped catalogs:
  - core: `tdm`, `cstrike`, `dm`, `hmcd`, `fear`;
  - team/PvE: `hl2dm`, `coop`, `defense`, `criresp`, `pathowogen`;
  - additional: `riot`, `gwars`, `superfighters` (`sfd`), `scugarena`, `event` (`eventhandler`).
- Fear inheritance and event framework are traced from `core/sh_fear.lua`, `core/sv_fear.lua`, `core/cl_fear.lua`, and `sv_scary_black_guy.lua`.
- Pathowogen identity, extraction/assimilation flow, network channels, vehicle/fake-ragdoll integrations and major failure modes are traced from `sh_uwu.lua`, `sv_uwu.lua`, `cl_uwu.lua`, and `sv_dialogue.lua`.
- `PUBLIC_SURFACES.md` now includes core/admin, competitive, Homicide/Fear, team/PvE and Pathowogen channel/state/trust summaries.
- Every catalog entry names source blobs, lifecycle, dependencies, defects, evidence gaps and validation requirements.

## High-impact verified findings

### Framework

- Global and gamemode loaders differ in realm/traversal rules; neither explicitly sorts `file.Find` results.
- Mode inheritance requires an already-registered base despite unsorted mode-directory enumeration.
- Every function-valued mode member becomes a hook candidate; dot-defined functions receive shifted arguments.
- Round states are `0`, `1`, `3`; stale comments/listeners use `2`.
- Round administration contains overlapping protocols and duplicate name-keyed registrations; client-supplied tables are weakly validated.

### Cross-mode

- Sender/receiver schema mismatches exist in TDM, HL2DM, Counter-Strike, Defense and Homicide-family packets.
- Required launch prerequisites are frequently absent, disabled, or overwritten.
- Delayed callbacks capture invalidatable players/entities and often resample winners after authoritative end.
- Inventory, organism, appearance, weapon, entity, class and integration APIs are assumed valid.
- Multiple modes use expensive entity scans, overbroad cleanup, unnamespaced timers/hooks and shared client globals/audio state.
- Fear and Pathowogen are hard-disabled for normal selection but still load function/direct-hook surfaces that require inactive-mode gating audits.
- Fear accepts client-authored light samples, contains event/timer cleanup defects, a misspelled victim variable and unsafe entity/sound paths.
- Pathowogen can recurse indefinitely when spawns are exhausted, mutates global fuel convars without restoration, duplicates broadcasts, assumes vehicle/weld validity and can leak `cam.IgnoreZ(true)` clientside.

## Current bounded trace

The directory-level mode identity pass is complete. Convert it into two implementation-grade cross-mode matrices and close remaining endpoint/file gaps before moving into organism/fake-ragdoll/movement.

### Required outputs

1. **Mode function matrix:** every function-valued mode member classified as lifecycle, engine hook, project hook, data callback, network helper, internal helper, or unresolved; include expected arguments, dispatcher behavior, collisions and realm.
2. **Packet matrix:** every channel with writer, reader, ordered schema, conditional branches, authority, validation, phase, rate/size limits, duplicates and legacy status.
3. Resolve remaining Homicide/Fear endpoints and conditional packet branches.
4. Resolve Defense auxiliary wave/support/highlight files and endpoints.
5. Resolve Counter-Strike bomb/hostage entities and client receivers.
6. Complete Pathowogen derma/end-report endpoints and inactive-mode direct-hook audit.
7. Trace framework consumers for `OverideSpawnPos`/spawn override, `COMMANDS`, map-point fallback, `zb.EndMatch`, round-hook names and mode cleanup.
8. Update existing catalogs/reference files; do not create branches or per-mode documents.

## Validation requirements

- Cross-check both packet endpoints and every conditional branch.
- Separate expected name-keyed overwrite behavior from runtime-confirmed behavior.
- Verify all client values are typed, bounded, authorized, phase-checked, rate-limited and server-resolved where applicable.
- Verify server/client mode registries agree on IDs, inheritance and callback sets.
- Review UI, persistence, selection, points, spawn, team, organism, inventory, appearance, weapons, entities, NPCs, vehicles, audio/render state and cleanup consumers.
- Introduce no runtime Lua, assets, configuration or `main` changes during research.

## Risks and evidence gaps

- Static source cannot prove total startup order, unsorted enumeration order, inactive-hook execution or effective duplicate overwrite behavior; temporary runtime instrumentation is required.
- Recursive path enumeration remains incomplete because the connector cannot reliably list directories; discovery is incremental and upstream search is used only to locate paths before fetching current-repo files.
- No dedicated-server smoke-test evidence has been captured.
- Documented defects must not be patched until adjacent contracts and integration boundaries are mapped.

## Dependency-ordered continuation

1. Build the complete function and packet matrices; close remaining mode endpoint/file gaps.
2. Complete file/realm/public-surface inventories discovered through those matrices.
3. Trace organism, fake-ragdoll, movement and player-class systems.
4. Trace weapons/combat/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator, persistence/admin/security/integrations.
5. Produce cross-system integration map, regression matrix, verified defect catalog and implementation-ready remediation packages.
6. Begin implementation on justified branches only after research defines boundaries and the user approves transition.

## Exact next action

Continue on `docs/architecture-baseline`: inventory all function-valued members from the fetched mode files into the mode-function matrix, then inventory their network channels into the packet matrix; while doing so, fetch the unresolved Defense, Homicide/Fear, Counter-Strike and Pathowogen endpoint files and update existing references without creating another branch or PR.