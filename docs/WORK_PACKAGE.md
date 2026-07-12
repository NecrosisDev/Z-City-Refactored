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
- `SYS-ORGANISM`, `SYS-FAKE-RAGDOLL`, `SYS-MOVEMENT`, `SYS-PLAYER-CLASS`, and the initial `SYS-CHARACTER-RUNTIME` authority graph now document core ownership, state, transport, transition behavior, integration risks, and validation boundaries.
- Movement research covers predicted calculation, inertia, physiology/class/weapon/load modifiers, fake suppression/entry, animation, footsteps, and determinism hazards.
- Player-class research covers registry/dispatch, transition order, transport, class side effects, shared-table Think throttling, cleanup gaps, and the unvalidated client-to-server `playerclass` assignment surface.

## Verified cross-system findings

- `hg.FakeUp` uses process-global `OverrideSpawn`, calls `hg.OverrideSpawn(ply)`, respawns, then clears the global only on the successful path; the transition is not transactional.
- Ordinary movement, fake-body control, organism state, class multipliers, weapon state, and presentation hooks share mutable state without one explicit per-player authority/generation object.
- Shared movement uses realm-local timing and prediction-mutated player fields; server/client convergence is not established.
- Class definitions are shared mutable tables. `class.nextThink` therefore throttles all players using the same class through one timestamp.
- The server accepts the overloaded `playerclass` payload from a valid client and applies the supplied class/data without a verified permission, phase, or rate contract.
- Vehicle/fake transitions still use process-global `hg.leaveveh` and `hg.fallfromveh`, creating concurrent-player interference risk.

## Still-open framework inventory

- The `COMMANDS` registry initializer/parser/dispatcher, generic permission/cooldown semantics, collision behavior, realm exposure, and complete publisher list remain unresolved. Confirmed publisher: `COMMANDS.bigmap = {handler, 0}` in `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`.
- Global `OverrideSpawn` is verified in `GM:PlayerSpawn` and fake get-up; all assignments/readers still require exact source enumeration.
- `MODE.OverrideSpawn` is a distinct mode-table gate that suppresses default team/appearance assignment only.
- `hg.OverrideSpawn(ply)` remains a third distinct surface; its definition and complete caller set are unresolved.
- `OverideSpawnPos` remains unresolved; repository-wide absence is not proven.
- `zb:EndRound()` is the verified termination API. No `zb.EndMatch` reference exists in fetched core/fake/movement/class files, but repository-wide absence is not proven.
- Point-system storage/editor APIs and all objective/extraction/UI consumers remain incomplete.
- Connector code search is repeatedly timing out and no directory/tree listing action is exposed. Direct exact-path fetching remains available but cannot support repository-wide negative claims until the recursive manifest is completed.

## Current bounded trace

Close command/spawn/point/lifecycle symbol ownership while continuing the character runtime integration trace into weapons, vehicles, appearance, inventory/armor, camera/spectator, death, and combat.

### Required outputs

1. Locate the `COMMANDS` initializer, parser, dispatcher, permission/cooldown behavior, realm exposure, overwrite/collision semantics, and every `COMMANDS.*` publisher.
2. Enumerate every global `OverrideSpawn` assignment/read, every `MODE.OverrideSpawn`, and the definition/callers of `hg.OverrideSpawn`.
3. Locate every `OverideSpawnPos` spelling or prove absence from an exact recursive file manifest.
4. Trace map-point persistence/editor APIs plus every spawn, objective, extraction, world-size, mode, entity, and UI consumer.
5. Locate every `zb.EndMatch` definition/call or prove absence from an exact recursive file manifest; keep it distinct from `zb:EndRound()`.
6. Extend the CharacterRuntime authority graph through weapon ownership/stance/ragdoll callbacks, vehicles, appearance/bodygroups/armor, inventory/equipment, camera/spectator, and death/disconnect cleanup.
7. Update existing catalogs/reference files and this handoff only; do not create duplicate indexes.

## Validation requirements

- Instrument get-up with failure injection around `OverrideSpawn`, `hg.OverrideSpawn`, `Spawn`, position restore, body removal, timers, death, and disconnect; assert cleanup in every exit.
- Exercise simultaneous fake/get-up, class change, movement prediction, and vehicle transitions for multiple players.
- Assert one character/body/organism/class/controller generation across player, fake body, death body, disconnect conversion, delayed callbacks, packets, and NWEntity reordering.
- Capture per-command server/client movement inputs, ordered modifiers, final speed/jump/input, prediction replay, latency, and stale physiology/class/weapon state.
- Fuzz/replay `playerclass`; verify authorization, payload limits, transition rollback, old-class cleanup, same-class multi-player Think, and client/server parity.
- Runtime-confirm loader order, duplicate hook/net/command registration, command collision behavior, and public-surface parity.
- Do not patch documented defects before adjacent contracts and regression boundaries are complete.

## Dependency-ordered continuation

1. Complete the recursive exact-path manifest for `lua/homigrad/zchat`, `adminsystem`, `admintools`, gamemode `libraries/!core`, fake/spawn/movement/playerclass, and mappoint/editor trees; close `COMMANDS`, spawn symbols, `OverideSpawnPos`, and `zb.EndMatch`.
2. Trace weapons and physical bullets, including movement/stance interfaces, fake-ragdoll callbacks, carry/grab state, damage ownership, ammo/loadout restoration, and prediction/networking.
3. Trace vehicles/Glide/simfphys and complete concurrent fake/enter/exit/ejection/get-up ownership.
4. Trace inventory/equipment/armor/appearance and their class/fake/death restoration contracts.
5. Trace UI/HUD/camera/spectator, NPC/bots, persistence/admin/security, and external integrations.
6. Produce the cross-system integration map, regression matrix, verified defect catalog, and implementation-ready remediation packages.

## Exact next action

Continue on `docs/architecture-baseline`: use exact-path fetching from the manifest and known loader/catalog references to close the `COMMANDS`, global/mode/hg spawn-override, `OverideSpawnPos`, map-point, and `zb.EndMatch` inventories; update `PUBLIC_SURFACES.md`, `FILE_MANIFEST.md`, `SYSTEM_CATALOG.md`, affected matrices/catalogs, and this handoff; then trace weapon/combat interfaces against the existing organism/fake/movement/player-class CharacterRuntime graph. Do not create another branch or PR. If connector search remains unavailable, record only fetched-file evidence and avoid repository-wide absence claims until an exact recursive manifest exists.