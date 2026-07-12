# Active Work Package

> Current bounded package and continuation state. Durable detail belongs in the linked architecture documents, catalogs, matrices, commits, PR discussion, and validation records.

## Identity

- **ID:** `WP-RESEARCH-001`
- **Title:** Build the code-grounded ZCity Refactored architecture baseline
- **Branch:** `docs/architecture-baseline`
- **Pull request:** `#1`
- **Status:** `active research`
- **Runtime baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`; documentation-only branch

## Non-negotiable rules

- Continue on `docs/architecture-baseline`; PR `#1` is the only active review surface.
- Do not create another branch or PR and do not modify runtime Lua during research.
- Executable code and reproducible runtime evidence outrank comments and inherited documentation.
- Label claims `Verified`, `Inferred`, `Legacy Claim`, or `Planned`.
- Continue after every bounded trace until integration research is complete or genuinely blocked.

## Completed baseline

- Bootstrap/load order, realm routing, mode registration, round lifecycle, all known mode directories, mode-function matrix, packet matrix, public surfaces, file-manifest boundaries, organism architecture, and core fake-ragdoll architecture are documented.
- Counter-Strike objective entities, Homicide/Fear endpoints, Defense auxiliary files, Pathowogen endpoints, active/legacy queue protocols, time/spectator synchronization, and one-sided round channels are classified.
- `SYS-ORGANISM` and `SYS-FAKE-RAGDOLL` now record ownership, state, damage, replication, fake creation/control, death reuse, get-up, camera/render, transport, validation, and major risks.

## Newly verified fake-ragdoll/get-up ownership

Source: `lua/homigrad/fake/sv_tier_0.lua` blob `0fa522db3f0562eaf1816d6452fa082aef81d2bb`.

- `hg.FakeUp` sets the undeclared global `OverrideSpawn = true`, calls `hg.OverrideSpawn(ply)`, invokes `ply:Spawn()`, then clears the global with `OverrideSpawn = nil`.
- The global lifetime is therefore synchronous only on the successful get-up path, but it is process-global rather than player- or mode-scoped. Any error between assignment and cleanup can leak spawn suppression to unrelated players and rounds.
- Get-up preserves health, armor, eye angles, active-weapon class, selected rope weapon, ragdoll velocity, fire state, flashlight permission, and selected movement/render/collision state, but restoration is not transactional.
- The spawn call occurs before the player is moved to the resolved get-up position. Normal `GM:PlayerSpawn` work is suppressed by the global gate, while `hg.OverrideSpawn(ply)` is a separate pre-spawn restoration hook/API and must not be conflated with either the global or `MODE.OverrideSpawn`.
- Delayed cleanup uses `timer.Create("faking_up" .. EntIndex, ...)`; body removal, `FakeRagdoll` NWEntity clearing, movement/collision restoration, and `hg.ragdollFake` cleanup can therefore be interrupted by disconnect, death, replacement body creation, or timer-name reuse.
- `PlayerDisconnected/hg-killniers` creates a new organism on the death ragdoll, merges the player organism, changes `owner`, then calls `hg.organism.Clear(ply.organism)`. This is copy/merge semantics rather than the normal shared-table transfer contract and requires direct validation for alias loss, duplicated delayed writers, and invalid API arguments.
- `hg.RagdollOwner` only returns an owner when `ply.FakeRagdoll == ragdoll`; death bodies and stale/replaced generations intentionally fail this lookup.
- Vehicle transitions branch through global `hg.leaveveh` / `hg.fallfromveh`, delayed fake entry, seat-switch timers, welds, parents, and forced get-up. These globals are not player-scoped and are high-risk under concurrent players.

## Still-open framework inventory

- The `COMMANDS` registry initializer/parser/dispatcher, generic permission/cooldown semantics, collision behavior, realm exposure, and complete publisher list remain unresolved. Confirmed publisher: `COMMANDS.bigmap = {handler, 0}` in `libraries/sv_roundsystem.lua`.
- Global `OverrideSpawn` is now verified in `GM:PlayerSpawn` and fake get-up. All additional assignments/readers still require source enumeration.
- `MODE.OverrideSpawn` is a distinct mode-table gate that suppresses only default team/appearance assignment.
- `OverideSpawnPos` remains unresolved; repository-wide absence is not proven.
- `zb:EndRound()` is the verified termination API. No `zb.EndMatch` reference exists in fetched core/fake files, but repository-wide absence is not yet proven.
- Point-system storage/editor APIs and all objective/extraction/UI consumers remain incomplete.

## Current bounded trace

Close the remaining command/spawn/point/lifecycle symbols, then continue fake-ragdoll integration into movement, player classes, weapons, vehicles, appearance, spectator/camera, and organism consumers.

### Required outputs

1. Locate the `COMMANDS` initializer, parser, dispatcher, permission/cooldown behavior, realm exposure, overwrite/collision semantics, and every `COMMANDS.*` publisher.
2. Enumerate every global `OverrideSpawn` assignment/read and every `MODE.OverrideSpawn`; prove setup/reset lifetime and failure leakage.
3. Locate every `OverideSpawnPos` spelling or prove absence from an exact recursive file manifest.
4. Trace map-point persistence/editor APIs plus every spawn, objective, extraction, world-size, mode, entity, and UI consumer.
5. Locate every `zb.EndMatch` definition/call or prove absence from an exact recursive file manifest; keep it distinct from `zb:EndRound()`.
6. Trace `hg.OverrideSpawn(ply)` definition and all publishers/consumers; classify it separately from both `OverrideSpawn` gates.
7. Trace fake-ragdoll transition consumers in movement, player classes, weapons, vehicles, appearance, camera/spectator, death, and disconnect paths.
8. Update existing catalogs/reference files and this handoff only; do not create duplicate indexes.

## Validation requirements

- Instrument get-up with failure injection around `OverrideSpawn` assignment, `hg.OverrideSpawn`, `Spawn`, position restore, body removal, timers, death, and disconnect; assert global cleanup in every exit.
- Exercise simultaneous fake/get-up and vehicle transitions for multiple players to expose process-global `OverrideSpawn`, `hg.leaveveh`, and `hg.fallfromveh` interference.
- Assert one organism owner generation across player, fake body, death body, disconnect conversion, delayed callbacks, and packet/NWEntity reordering.
- Capture `Player Ragdoll`, `Override Spawn`, organism snapshots, NWEntity changes, late join, PVS changes, and undefined `net.ReadEntity2()` behavior.
- Runtime-confirm loader order, duplicate hook/net registration, command collision behavior, and server/client public-surface parity.
- Do not patch documented defects before adjacent contracts and regression boundaries are complete.

## Evidence gaps and blockers

- Connector code search is repeatedly timing out and directory-listing is unavailable, so repository-wide negative claims cannot yet be made from search alone.
- Direct file fetching remains available and is the required fallback: use known manifests, source references, loader paths, mode catalogs, and exact include paths to enumerate files.
- No dedicated-server runtime evidence has been captured.
- External-addon readers for one-sided channels remain unknown.

## Dependency-ordered continuation

1. Fetch likely command/chat/admin files under `lua/homigrad/zchat`, `adminsystem`, `admintools`, gamemode `libraries/!core`, and every known publisher path; close `COMMANDS` ownership.
2. Fetch all fake/spawn/movement/player-class files; close `OverrideSpawn`, `hg.OverrideSpawn`, `OverideSpawnPos`, get-up, disconnect, death, and concurrent-player state.
3. Fetch `libraries/mappoints/**`, point editor/UI files, objective entities, extraction modes, and world-size consumers.
4. Prove or locate `zb.EndMatch` through the exact file manifest.
5. Continue weapons/physical bullets/armor/explosives, inventory/equipment/appearance, NPC/bots, UI/HUD/camera/spectator, persistence/admin/security, and external integrations.
6. Produce the cross-system integration map, regression matrix, verified defect catalog, and implementation-ready remediation packages.

## Exact next action

Continue on `docs/architecture-baseline`: fetch the known command/chat/admin library files directly and close the `COMMANDS` registry; fetch the definition and every call of `hg.OverrideSpawn`, all remaining fake/spawn/movement/player-class files, and exact point-system/editor paths; enumerate `OverrideSpawn`, `OverideSpawnPos`, and `zb.EndMatch` repository-wide from the resulting manifest; update `PUBLIC_SURFACES.md`, `SYSTEM_CATALOG.md`, affected mode catalogs/matrices, and this handoff; then continue fake-ragdoll integration into movement, player classes, weapons, vehicles, appearance, camera/spectator, death, and combat without creating another branch or PR.