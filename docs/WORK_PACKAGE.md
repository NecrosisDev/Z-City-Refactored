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
- Lack of merge permission is not a research blocker.
- Continue after every bounded trace until research and subsequent integration are complete.
- Preserve every cumulative rule in root `AGENTS.md`.
- Keep chat output to two-sentence TL;DRs; durable detail belongs in the repository.
- Add only the smallest authoritative mechanism that prevents rediscovery, drift, or regression.

## Verified completed research

- Project structure, bootstrap/load order, realm routing, mode registration, round lifecycle, shared system/behavior/type contracts, file-manifest boundaries, and public surfaces are documented.
- Every known top-level mode directory has a verified registry identity.
- `MODE_FUNCTION_MATRIX.md` classifies the effective callback/helper surface for the complete known registry.
- `PACKET_MATRIX.md` records verified core/admin and mode packet families, schemas, mismatches, trust checks, duplicate generations and dormant endpoints.
- Counter-Strike objective entities, Homicide assistant/death-state/role-selection, and Defense auxiliary function/packet surfaces are traced.
- Core synchronization ownership is now closed:
  - `updtime` is paired from `gamemode/init.lua:hg.UpdateRoundTime` to `cl_init.lua`;
  - `ZB_SpectatePlayer` is paired from dead-player `ZB_ChooseSpecPly` handling in `init.lua` to `cl_init.lua`;
  - `FadeScreen` is writer-only from `sv_roundsystem.lua:zb.AddFade`, with no repository receiver and overlapping `RoundInfo`/`ScreenFade` presentation;
  - `RequestGameQueue` is registration-only;
  - `SendGameQueue`, `QueueEmptiedNotification`, and `QueueModifiedNotification` are legacy writer-only channels with no current manager receivers.
- The active `ZB_*` round-list protocol uses `zb.RoundList`; the legacy queue generation uses separate `zb.QueuedModes`, duplicate handlers and duplicate synchronization functions.
- Initial spawn and fallback ownership is partially source-located in `gamemode/init.lua`: map `Spawnpoint` records precede broad entity-class fallback; global `OverrideSpawn` and mode `CurrentRound().OverrideSpawn` are separate gates.
- Verified round emitters are `ZB_PreRoundStart`, `TTTPrepareRound`, `ZB_StartRound`, and `ZB_EndRound` in `libraries/sv_roundsystem.lua`.

## High-impact verified findings

### Framework

- Global and gamemode loaders differ in realm/traversal rules; neither explicitly sorts `file.Find` results.
- Mode inheritance requires an already-registered base despite unsorted mode-directory enumeration.
- Every function-valued mode member becomes a hook candidate; dot-defined functions receive shifted arguments.
- Round states are `0`, `1`, `3`; stale comments/listeners use `2`.
- Round administration contains overlapping protocols, duplicate name-keyed registrations, weak client-table validation and two divergent queue-state tables.
- `FadeScreen` is currently an unconsumed writer, while end-round fading is also implemented through `RoundInfo` client state and server `Player:ScreenFade` calls.
- `GM:PlayerInitialSpawn` can spawn a temporary bot and force `zb:EndRound()` when the first player joins, coupling population bootstrap to lifecycle transitions.

### Function and packet matrices

- Internal services published as hooks include Homicide role/spawn helpers, Fear event/victim helpers, Defense wave/spawn/timer/economy helpers, CO-OP equipment helpers, Event persistence helpers and Pathowogen extraction services.
- Confirmed packet mismatches remain base `tdm_start`, `CS_Roundover`, `hl2dm_roundend`, `npc_defense_newwave`, and conditional `HMCD_RoundStart` roster decoding.
- Highest-risk client inputs remain admin queue/list tables, TDM purchases, bomb codes, Fear light vectors, Crisis customization, Defense commander support/purchase/admin commands, and Event persistent loot edits.
- Fear and Pathowogen are hard-disabled for normal selection but still load receivers, direct hooks and dispatch surfaces.
- Multiple systems listen on names that differ from verified core emitters: CO-OP uses `ZB_RoundStart`; Defense support uses `RoundEnd`; core emits `ZB_StartRound` and `ZB_EndRound`.

## Current bounded trace

Finish framework command, spawn, point and lifecycle ownership, then begin organism initialization/state/replication using the completed mode and packet matrices as consumer maps.

### Required outputs

1. Locate the `COMMANDS` registry initializer, parser, dispatcher, permission/cooldown semantics and all publishers; classify collisions and realm exposure.
2. Trace every `OverrideSpawn` and misspelled `OverideSpawnPos` producer/consumer, including whether globals leak between modes or rounds.
3. Trace map-point storage/load APIs and every fallback path used by spawn, objective and extraction systems.
4. Locate every `zb.EndMatch` definition/call or prove it absent; distinguish it from verified `zb:EndRound()`.
5. Complete Pathowogen Derma/end-report and inactive-mode direct-hook audit.
6. Begin organism ownership: initialization, entity/player attachment, state schema, damage/medical lifecycle, replication, fake-ragdoll integration and mode consumers.
7. Update existing catalogs/reference files only; do not create duplicate indexes, branches or PRs.

## Validation requirements

- Cross-check both packet endpoints and every conditional branch; never infer a schema from one side.
- Separate expected name-keyed overwrite behavior from runtime-confirmed behavior.
- Verify all client values are typed, bounded, authorized, phase-checked, rate-limited and server-resolved where applicable.
- Verify server/client mode registries agree on IDs, inheritance and callback sets.
- Verify every function classification against actual callers and dynamic hook emitters, including inactive modes.
- Review UI, persistence, selection, points, spawn, team, organism, inventory, appearance, weapons, entities, NPCs, vehicles, audio/render state and cleanup consumers.
- Introduce no runtime Lua, assets, configuration or `main` changes during research.

## Risks and evidence gaps

- Static source cannot prove total startup order, unsorted enumeration order, inactive-hook execution or effective duplicate overwrite behavior; temporary runtime instrumentation is required later.
- Recursive path enumeration remains incomplete because connector code search and directory listing are unreliable; discovery continues through known paths, indexed results and fetched executable files.
- Some matrix rows are symbol/blob-complete rather than original line-offset complete.
- No dedicated-server smoke-test evidence has been captured.
- One-sided/dormant packet names must be checked against external addons before removal.
- `FadeScreen` receiver absence is repository-complete for the traced baseline, not proof that no workshop addon consumes the channel.
- Documented defects must not be patched until adjacent contracts and integration boundaries are mapped.

## Dependency-ordered continuation

1. Trace `COMMANDS`, spawn overrides, map points, `zb.EndMatch` and lifecycle consumers.
2. Complete Pathowogen client/inactive-mode boundaries.
3. Trace organism, fake-ragdoll, movement and player classes.
4. Continue through combat/weapons/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator and persistence/admin/security/integrations.
5. Produce the cross-system integration map, regression matrix, verified defect catalog and implementation-ready remediation packages.
6. Begin implementation only after research defines boundaries and the user approves transition.

## Exact next action

Continue on `docs/architecture-baseline`: locate the `COMMANDS` registry owner/dispatcher and all command publishers; enumerate all `OverrideSpawn`/`OverideSpawnPos`, map-point and `zb.EndMatch` definitions/callers; update `PUBLIC_SURFACES.md`, `SYSTEM_CATALOG.md`, affected mode catalogs and this handoff; then begin organism initialization, attachment and replication tracing without creating another branch or PR.
