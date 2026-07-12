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
- `SYS-ORGANISM`, `SYS-FAKE-RAGDOLL`, `SYS-MOVEMENT`, `SYS-PLAYER-CLASS`, and `SYS-CHARACTER-RUNTIME` document core ownership, state, transport, transition behavior, integration risks, and validation boundaries.
- The initial `SYS-WEAPON-COMBAT` trace now documents the executable fake-controller consumer contract for `ishgweapon`, `IsPistolHoldType`, `IsResting`, `RagdollFunc`, `ismelee`, and `ismelee2`.
- Movement research covers predicted calculation, inertia, physiology/class/weapon/load modifiers, fake suppression/entry, animation, footsteps, and determinism hazards.
- Player-class research covers registry/dispatch, transition order, transport, class side effects, shared-table Think throttling, cleanup gaps, and the unvalidated client-to-server `playerclass` assignment surface.

## Verified cross-system findings

- `hg.FakeUp` uses process-global `OverrideSpawn`, calls `hg.OverrideSpawn(ply)`, respawns, then clears the global only on the successful path; the transition is not transactional.
- Ordinary movement, fake-body control, organism state, class multipliers, weapon state, and presentation hooks share mutable state without one explicit per-player authority/generation object.
- Shared movement uses realm-local timing and prediction-mutated player fields; server/client convergence is not established.
- Class definitions are shared mutable tables. `class.nextThink` therefore throttles all players using the same class through one timestamp.
- The server accepts the overloaded `playerclass` payload from a valid client and applies the supplied class/data without a verified permission, phase, or rate contract.
- Vehicle/fake transitions still use process-global `hg.leaveveh` and `hg.fallfromveh`, creating concurrent-player interference risk.
- Server `Think/Fake` reads the active weapon every frame and combines implicit weapon capability fields/methods with generic limb, constraint, organism, and input ownership.
- `RagdollFunc` executes inside the monolithic fake-body loop without a verified signature, mutation boundary, cleanup contract, command number, or body-generation token.
- Respawn-based get-up reselects a saved active weapon but does not prove preservation of weapon instances, clips, reserve ammunition, chamber/reload state, attachments, cooldowns, pending projectiles, or callback resources.

## Still-open framework inventory

- The `COMMANDS` registry initializer/parser/dispatcher, generic permission/cooldown semantics, collision behavior, realm exposure, and complete publisher list remain unresolved. Confirmed publisher: `COMMANDS.bigmap = {handler, 0}` in `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`.
- Global `OverrideSpawn` is verified in `GM:PlayerSpawn` and fake get-up; all assignments/readers still require exact source enumeration.
- `MODE.OverrideSpawn` is a distinct mode-table gate that suppresses default team/appearance assignment only.
- `hg.OverrideSpawn(ply)` remains a third distinct surface; its definition and complete caller set are unresolved.
- `OverideSpawnPos` remains unresolved; repository-wide absence is not proven.
- `zb:EndRound()` is the verified termination API. No `zb.EndMatch` reference exists in fetched core/fake/movement/class files, but repository-wide absence is not proven.
- Point-system storage/editor APIs and all objective/extraction/UI consumers remain incomplete.
- Connector code search continues to time out and no recursive directory/tree listing action is exposed. Direct exact-path fetching is available, so negative claims must remain bounded to fetched files.

## Current bounded trace

Complete the exact weapon capability/publisher and combat-lifecycle inventory while continuing exact-path attempts for unresolved command/spawn/point/lifecycle symbols.

### Required outputs

1. Enumerate the definition and every use of `ishgweapon`.
2. Enumerate every publisher/consumer of `RagdollFunc`, `IsPistolHoldType`, `IsResting`, `ismelee`, and `ismelee2` across engine-loaded SWEPs and global files.
3. Trace switch, drop, pickup, fake, get-up, death, disconnect, class/mode loadout, ammo/reload, projectile, physical-bullet, damage, armor, and cleanup ownership.
4. Pair server weapon action with client animation, rendering, camera, recoil, sound, and networking.
5. Continue exact-path enumeration of `COMMANDS`, global/MODE/hg spawn overrides, `OverideSpawnPos`, map points, and `zb.EndMatch` without overstating repository-wide absence.
6. Extend the CharacterRuntime graph through weapon state snapshots, callbacks, body generation, prediction, networking, and cleanup.
7. Update existing catalogs/reference files and this handoff; avoid duplicate indexes.

## Validation requirements

- Instrument get-up with failure injection around `OverrideSpawn`, `hg.OverrideSpawn`, `Spawn`, weapon snapshot/restore, position restore, body removal, timers, death, and disconnect; assert cleanup in every exit.
- Exercise simultaneous fake/get-up, class change, weapon switch/reload/fire, movement prediction, and vehicle transitions for multiple players.
- Assert one character/body/organism/class/controller/weapon generation across player, fake body, death body, disconnect conversion, delayed callbacks, packets, projectiles, and NWEntity reordering.
- Capture command number, active weapon class/instance, capability branch, callback, input bits, view, resulting forces, ammo/clip/reload state, and client presentation timing.
- Fuzz/replay `playerclass`; verify authorization, payload limits, transition rollback, old-class cleanup, same-class multi-player Think, and client/server parity.
- Runtime-confirm loader order, duplicate hook/net/command registration, command collision behavior, weapon publisher collisions, and public-surface parity.
- Do not patch documented defects before adjacent contracts and regression boundaries are complete.

## Dependency-ordered continuation

1. Complete exact weapon capability and lifecycle enumeration, then physical bullets, ammunition, projectiles, armor, explosives, damage ownership, and client presentation.
2. Continue the recursive exact-path manifest for command/chat/admin, fake/spawn, point/editor, SWEP, entity, and mode trees; close unresolved symbols only when evidence supports it.
3. Trace vehicles/Glide/simfphys and complete concurrent fake/enter/exit/ejection/get-up ownership.
4. Trace inventory/equipment/armor/appearance and their class/fake/death restoration contracts.
5. Trace UI/HUD/camera/spectator, NPC/bots, persistence/admin/security, and external integrations.
6. Produce the cross-system integration map, regression matrix, verified defect catalog, and implementation-ready remediation packages.

## Exact next action

Continue on `docs/architecture-baseline`: fetch exact SWEP/base files referenced by known weapon classifiers, class loadouts, fake control, movement and mode catalogs; enumerate `ishgweapon`, `RagdollFunc`, hold/resting/melee capability publishers and weapon lifecycle/transport; update `WEAPON_COMBAT_INTERFACES.md`, `PUBLIC_SURFACES.md`, `FILE_MANIFEST.md`, `SYSTEM_CATALOG.md`, affected matrices/catalogs, `CHARACTER_RUNTIME_INTEGRATION.md`, and this handoff. In parallel, preserve exact-path attempts for `COMMANDS`, spawn overrides, map points, `OverideSpawnPos`, and `zb.EndMatch`. Do not create another branch or PR. If recursive access remains unavailable, record only fetched-file evidence and preserve bounded negative claims.
