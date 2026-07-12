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
- `MODE_FUNCTION_MATRIX.md` classifies the effective callback/helper surface for the complete known registry, including inheritance, dot/colon argument behavior, direct hooks, empty overrides and internal helpers accidentally registered as hooks.
- `PACKET_MATRIX.md` records verified core/admin and mode packet families, ordered schemas, overloaded names, mismatches, trust checks, rate/size limits, persistence crossings and one-sided endpoints.
- Counter-Strike nested Derma readers and bomb entity endpoints are paired.
- Homicide assistant/death-state and role-selection endpoints are paired; `HMCD(SetSubRole)` remains reader-only and `HMCDPoliceRole` registration-only.
- Defense auxiliary ownership and function surfaces are resolved across `sv_defense.lua`, `sv_defense_waves.lua`, `sv_defense_roles.lua`, `sv_defense_support.lua`, `sv_defense_hooks.lua`, and `cl_defense.lua`.
- Remaining Defense channel classifications are closed:
  - `defense_highlight_last_npcs` is paired with `sv_defense_hooks.lua` broadcasting entity-index tables and `cl_defense.lua` outlining valid entities;
  - `defense_commander_points` is registration-only/dormant because commander state uses `NWInt("CommanderPoints")`;
  - `defense_player_role_assigned` is writer-only/redundant because clients use `NWString("PlayerRole")` and role-change polling;
  - `defense_admin_command` is reader-only with an inline admin allowlist but no repository sender, rate/size or active-mode guard.
- The canonical matrices remain `MODE_FUNCTION_MATRIX.md` and `PACKET_MATRIX.md`; no duplicate index is retained.

## High-impact verified findings

### Framework

- Global and gamemode loaders differ in realm/traversal rules; neither explicitly sorts `file.Find` results.
- Mode inheritance requires an already-registered base despite unsorted mode-directory enumeration.
- Every function-valued mode member becomes a hook candidate; dot-defined functions receive shifted arguments.
- Round states are `0`, `1`, `3`; stale comments/listeners use `2`.
- Round administration contains overlapping protocols and duplicate name-keyed registrations; client-supplied tables are weakly validated.

### Function and packet matrices

- Internal services published as hooks include Homicide role/spawn helpers, Fear event/victim helpers, Defense wave/spawn/timer/economy helpers, CO-OP equipment helpers, Event persistence helpers and Pathowogen extraction services.
- Confirmed packet mismatches: base `tdm_start`, `CS_Roundover`, `hl2dm_roundend`, `npc_defense_newwave`, and conditional `HMCD_RoundStart` roster decoding.
- Highest-risk client inputs: admin queue/list tables, TDM purchases, bomb codes, Fear light vectors, Crisis customization, Defense commander purchase/support/admin commands, and Event persistent loot edits.
- Defense globally wraps `SpawnZBaseNPC`, combines per-NPC timers/nav scans/world scans, and performs broad end cleanup across unrelated NPC/addon classes.
- Fear and Pathowogen are hard-disabled for normal selection but still load network receivers, direct hooks and function-dispatch surfaces.
- Multiple systems listen on hook names that differ from verified core emitters: CO-OP uses `ZB_RoundStart`; Defense support uses `RoundEnd`; core emits `ZB_StartRound` and `ZB_EndRound`.

## Current bounded trace

Close core one-sided channels and framework ownership surfaces, then begin organism/fake-ragdoll/movement/player-class ownership using the completed mode matrices as consumers.

### Required outputs

1. Pair core one-sided channels: `FadeScreen`, `updtime`, `ZB_SpectatePlayer`, and legacy admin queue consumers.
2. Trace `COMMANDS` registry owner/dispatcher, spawn-override consumers (`OverrideSpawn`, `OverideSpawnPos`), map-point fallbacks, `zb.EndMatch`, and actual round hook emitters.
3. Complete Pathowogen Derma/end-report and inactive-mode direct-hook audit.
4. Begin organism ownership: initialization, entity/player attachment, state schema, damage/medical lifecycle, replication, fake-ragdoll integration and mode consumers.
5. Continue immediately into fake-ragdoll, movement and player-class boundaries.
6. Update existing matrices/catalogs/reference files only; do not create duplicate indexes, branches or PRs.

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
- Recursive path enumeration remains incomplete because the connector cannot reliably list directories; source discovery continues through known paths, indexed results and fetched executable files.
- Some matrix rows are symbol/blob-complete rather than original line-offset complete.
- No dedicated-server smoke-test evidence has been captured.
- One-sided/dormant packet names must be checked against external addons before removal.
- Documented defects must not be patched until adjacent contracts and integration boundaries are mapped.

## Dependency-ordered continuation

1. Close core one-sided channels and hook-name consumers.
2. Trace `COMMANDS`, spawn override, points, end-match and round-hook ownership.
3. Complete Pathowogen client/inactive-mode boundaries.
4. Trace organism, fake-ragdoll, movement and player classes.
5. Continue through combat/weapons/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator and persistence/admin/security/integrations.
6. Produce the cross-system integration map, regression matrix, verified defect catalog and implementation-ready remediation packages.
7. Begin implementation only after research defines boundaries and the user approves transition.

## Exact next action

Continue on `docs/architecture-baseline`: locate both endpoints and ownership for `FadeScreen`, `updtime`, `ZB_SpectatePlayer`, `RequestGameQueue`, `SendGameQueue`, `QueueEmptiedNotification`, and `QueueModifiedNotification`; update `PACKET_MATRIX.md` and `PUBLIC_SURFACES.md`; then trace `COMMANDS`, spawn overrides, map-point fallback, `zb.EndMatch`, and verified round-hook emitters before beginning the organism initialization/state/replication trace. Do not create another branch or PR.