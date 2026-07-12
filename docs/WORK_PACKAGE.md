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
- Verified round emitters are `ZB_PreRoundStart`, `TTTPrepareRound`, `ZB_StartRound`, and `ZB_EndRound` in `libraries/sv_roundsystem.lua`.
- Organism initialization, attachment, major state groups, module order, primary damage flow and `organism_send` replication are source-traced in `docs/architecture/ORGANISM_SYSTEM.md` and the catalogs.

## Newly verified framework ownership

### Spawn selection and overrides

- `gamemodes/zcity/gamemode/init.lua:getRandSpawn` rebuilds a realm-local `spawners` array at load and `InitPostEntity`.
- Map points named `Spawnpoint` are authoritative when at least one exists. Only when none exist does the code collect `info_player_start` plus the broad `default_spawns` class list.
- `zb:GetRandomSpawn` and `zb:FurthestFromEveryone` fall back to the cached `spawners` table when no explicit choices are supplied.
- `GM:PlayerSpawn` checks the undeclared global `OverrideSpawn` first and returns immediately when truthy. This suppresses all normal view/spectate/movement/team/appearance handling in that function.
- The separate mode member `CurrentRound().OverrideSpawn` only suppresses the default team and appearance reassignment block; it does not return from `GM:PlayerSpawn`.
- These names therefore represent two distinct contracts despite sharing the same spelling. The global is not mode-scoped and must be traced across fake-ragdoll/respawn callers for leakage and cleanup.
- The requested misspelling `OverideSpawnPos` remains unresolved and must be searched across every known source path before absence can be claimed.

### Map-point consumers

- `Spawnpoint` points feed the primary random-spawn cache.
- `RandomSpawns` points feed `zb.GetWorldSize`; the function computes the maximum squared pairwise point distance and returns its square root. With fewer than two useful points it returns zero, affecting `ForBigMaps` mode availability.
- Team spawning calls `CurrentRound():GetTeamSpawn()` and substitutes one random spawn for either empty team list.
- Objective/extraction point APIs remain to be enumerated from the point-system owner and all mode/entity consumers.

### Round termination

- `zb:EndRound()` in `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua` is the verified core termination entry. It sets state `3`, increments round count, broadcasts `RoundInfo`, invokes the current mode's `EndRound`, emits `ZB_EndRound`, sends `FadeScreen`, and saves achievements.
- `GM:PlayerInitialSpawn` calls `zb:EndRound()` after creating a temporary bot when the first player joins.
- No `zb.EndMatch` definition or call exists in the two verified core ownership files (`gamemode/init.lua` and `libraries/sv_roundsystem.lua`). Repository-wide absence is not yet proven because connector code search is timing out; mode/entity files must still be checked directly.

### COMMANDS publisher evidence

- `libraries/sv_roundsystem.lua` publishes `COMMANDS.bigmap = {handler, 0}` without initializing `COMMANDS` locally.
- The handler performs its own `ply:IsAdmin()` check, parses `args[1]` with `tonumber`, mutates `ZBATTLE_BIGMAP`, rerolls chances, and persists `data/zbattle/mapsizes.json`.
- A missing/non-numeric argument can assign `nil`, then string concatenation and later comparisons can fail. The trailing `0` is an unresolved framework field until the registry/dispatcher owner is located.
- Registry initialization, chat/console parser, dispatch semantics, generic permission/cooldown enforcement, realm exposure, collision behavior and all additional publishers remain unresolved.

## High-impact verified findings

### Framework

- Global and gamemode loaders differ in realm/traversal rules; neither explicitly sorts `file.Find` results.
- Mode inheritance requires an already-registered base despite unsorted mode-directory enumeration.
- Every function-valued mode member becomes a hook candidate; dot-defined functions receive shifted arguments.
- Round states are `0`, `1`, `3`; stale comments/listeners use `2`.
- Round administration contains overlapping protocols, duplicate name-keyed registrations, weak client-table validation and two divergent queue-state tables.
- `FadeScreen` is currently an unconsumed writer, while end-round fading is also implemented through `RoundInfo` client state and server `Player:ScreenFade` calls.
- `GM:PlayerInitialSpawn` can spawn a temporary bot and force `zb:EndRound()` when the first player joins, coupling population bootstrap to lifecycle transitions.
- Spawn behavior is controlled by both an undeclared global `OverrideSpawn` and a mode-table member of the same name with materially different effects.
- Big-map eligibility depends on `RandomSpawns` map-point coverage rather than BSP/world bounds.

### Function and packet matrices

- Internal services published as hooks include Homicide role/spawn helpers, Fear event/victim helpers, Defense wave/spawn/timer/economy helpers, CO-OP equipment helpers, Event persistence helpers and Pathowogen extraction services.
- Confirmed packet mismatches remain base `tdm_start`, `CS_Roundover`, `hl2dm_roundend`, `npc_defense_newwave`, and conditional `HMCD_RoundStart` roster decoding.
- Highest-risk client inputs remain admin queue/list tables, TDM purchases, bomb codes, Fear light vectors, Crisis customization, Defense commander support/purchase/admin commands, and Event persistent loot edits.
- Fear and Pathowogen are hard-disabled for normal selection but still load receivers, direct hooks and dispatch surfaces.
- Multiple systems listen on names that differ from verified core emitters: CO-OP uses `ZB_RoundStart`; Defense support uses `RoundEnd`; core emits `ZB_StartRound` and `ZB_EndRound`.

## Current bounded trace

Close the unresolved framework command registry and remaining spawn/point/lifecycle symbols, then continue organism-to-fake-ragdoll ownership integration.

### Required outputs

1. Locate the `COMMANDS` registry initializer, parser, dispatcher, permission/cooldown semantics and every publisher; classify collisions and realm exposure.
2. Enumerate every global `OverrideSpawn` assignment/read and every mode-table `OverrideSpawn`; establish setup/reset lifetime and cross-round leakage.
3. Locate every `OverideSpawnPos` spelling or prove repository-wide absence from fetched sources.
4. Trace map-point storage/load/edit APIs and every spawn, objective, extraction, world-size and UI consumer.
5. Locate every `zb.EndMatch` definition/call or prove repository-wide absence; distinguish all call sites from `zb:EndRound()`.
6. Finish organism input/medical/effect writers, then trace fake-ragdoll creation, ownership transfer, input, networking, get-up, death and combat.
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
- GitHub code search timed out repeatedly during this trace, so repository-wide negative claims for `COMMANDS`, `OverideSpawnPos`, `zb.EndMatch` and override publishers remain open.
- Some matrix rows are symbol/blob-complete rather than original line-offset complete.
- No dedicated-server smoke-test evidence has been captured.
- One-sided/dormant packet names must be checked against external addons before removal.
- Documented defects must not be patched until adjacent contracts and integration boundaries are mapped.

## Dependency-ordered continuation

1. Fetch likely command/chat framework files and all known command-publishing mode files directly; close `COMMANDS` ownership without relying on code search.
2. Fetch fake-ragdoll and round/spawn files to enumerate global `OverrideSpawn` lifetime and organism transfer.
3. Fetch point-system/editor files and each objective/extraction consumer.
4. Complete Pathowogen client/inactive-mode boundaries.
5. Continue through fake-ragdoll, movement and player classes, then combat/weapons/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator and persistence/admin/security/integrations.
6. Produce the cross-system integration map, regression matrix, verified defect catalog and implementation-ready remediation packages.
7. Begin implementation only after research defines boundaries and the user approves transition.

## Exact next action

Continue on `docs/architecture-baseline`: inspect the file manifest and likely chat/admin library paths to locate the `COMMANDS` initializer and dispatcher; fetch every file publishing `COMMANDS.*`; enumerate all global/mode `OverrideSpawn` and `OverideSpawnPos` symbols, point-system APIs/consumers and `zb.EndMatch` references; update `PUBLIC_SURFACES.md`, `SYSTEM_CATALOG.md`, affected mode catalogs and this handoff; then continue the organism/fake-ragdoll ownership and replication trace without creating another branch or PR.