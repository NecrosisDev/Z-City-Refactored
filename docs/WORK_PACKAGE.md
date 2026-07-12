# Active Work Package

> Current bounded package and continuation state. Durable detail belongs in the linked architecture documents, catalogs, matrices, commits, PR discussion, integration records, and validation evidence.

## Identity

- **ID:** `WP-RESEARCH-001`
- **Title:** Build the code-grounded ZCity Refactored architecture and integration baseline
- **Branch:** `docs/architecture-baseline`
- **Pull request:** `#1`
- **Status:** `active research`
- **Repository runtime baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Local archive baseline:** `Trauma.zip`, SHA-256 `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652`
- **Runtime mutation:** none; documentation-only branch

## Non-negotiable rules

- Continue on `docs/architecture-baseline`; PR `#1` is the only active review surface.
- Do not create another branch or PR and do not modify runtime Lua during research.
- Executable code and reproducible runtime evidence outrank comments and inherited documentation.
- Every executable-source claim must identify whether it comes from repository `main` or the hashed local archive.
- Never generalize an archive-only fix or feature to repository `main` without comparison evidence.
- Label claims `Verified`, `Inferred`, `Legacy Claim`, or `Planned`.
- Continue after every bounded trace until integration research is complete or genuinely blocked.

## Completed baseline

- Repository bootstrap/load order, realm routing, mode registration, round lifecycle, known mode directories, mode-function matrix, packet matrix, public surfaces, file-manifest boundaries, organism, fake-ragdoll, movement, player-class, character-runtime and weapon/ballistics architecture are documented.
- Counter-Strike objectives, Homicide/Fear endpoints, Defense auxiliary files, Pathowogen endpoints, queue protocols, time/spectator synchronization and one-sided round channels are classified.
- Core ownership, state, transport, transition, security and validation boundaries exist for organism, fake-ragdoll, movement, player classes, character runtime and weapon-facing contracts.
- The local archive now has an immutable integration baseline covering artifact identity, file counts, deployment roots, Trauma/Z-City identity drift, loader differences, subsystem families, persistence migration and validation gates.
- The local archive bot/NPC system is documented across player-bot brain ownership, due-time scheduling, behavior bands, command-rate control, muzzle steering, perception, navigation, botfill, configuration/debugging, VJ compatibility, stock NPC extensions and zombie extensions.
- The archive's player bots are verified as code-present but shipping-disabled by `lua/autorun/000_trauma_disable_bots.lua`.
- The local archive now has a complete, reproducible 1,040-row file manifest with normalized candidate paths, byte sizes, SHA-256 values and Git blob identities; canonical CSV SHA-256 is `28f6eca648b80d6eca1419ce3e30fc60d2971ab743457d23aeee9d5a261cd4b0`.
- Thirteen representative core paths have exact repository/archive blob comparisons: two are identical and eleven have diverged, proving that integration must remain file- and feature-scoped.

## Verified cross-system findings

### Repository baseline

- `hg.FakeUp` uses process-global `OverrideSpawn`, respawns, and clears the global only on the successful path; the transition is not transactional.
- Ordinary movement, fake control, organism state, class multipliers, weapon state and presentation share mutable state without one per-player authority/generation object.
- Shared movement uses realm-local timing and prediction-mutated player fields; convergence is not established.
- Shared class definitions contain runtime `nextThink`, so same-class players compete for one throttle.
- The server accepts overloaded `playerclass` input without a verified permission, phase or rate contract.
- Vehicle/fake transitions use process-global flags and the fake controller invokes weapon callbacks without a verified mutation or cleanup contract.

### Local archive

- `TMod/` contains 1,040 files, including 1,028 Lua files; it is a full deployment tree rather than a patch.
- Project identity is `Trauma` / `trauma` with legacy `Z-City` / `zcity` compatibility.
- The local gamemode loader sorts paths and captures mode-owned hooks/timers through `zb.modeLifecycle`, unlike the repository baseline.
- Player-bot decisions run on a budgeted due-time heap while `StartCommand` applies intent every tick.
- Physical-muzzle correction consumes weapon worldmodel pose and can feed back into commanded eye aim; close-range vertical drift requires instrumentation.
- Bot navigation is synchronous A* with per-tick budget, pooled workspaces and persisted heuristic penalties under a legacy `zcity_nav_learning` path.
- Bot survival configuration has superadmin, cooldown and payload bounds; bot debug/config surfaces still require runtime cost and transport review.
- VJ compatibility intentionally splits AI/death ownership from organism/bleeding/corpse/knockdown ownership.

## Still-open inventory and evidence gaps

- The local archive manifest is complete and reproducible, but a recursive repository path/hash manifest is unavailable through the current connector.
- Repository-only, archive-only, renamed, modified, bundled dependency and excluded paths therefore cannot yet be classified repository-wide.
- The `COMMANDS` registry, all spawn override surfaces, point-system APIs and complete objective/editor consumers remain unresolved on the repository baseline.
- Complete weapon publisher/consumer and lifecycle enumeration remains incomplete across both sources.
- Inventory/equipment/appearance/clothing restoration contracts remain incomplete.
- UI/HUD/camera/spectator, persistence/admin/security and external integrations remain incomplete.
- No dedicated-server smoke test or enabled-bot runtime evidence has been captured for the local archive.
- Connector code search does not provide reliable recursive repository enumeration; negative repository claims must remain bounded.

## Current bounded trace

Complete the repository side of the integration comparison needed before runtime import while continuing source-qualified subsystem documentation.

### Required outputs

1. Preserve and verify the complete local archive manifest and its deterministic generator.
2. Obtain or construct a complete repository `main` path/hash manifest.
3. Join both manifests and classify every path as identical, modified, archive-only, repository-only, rename, generated, bundled dependency or excluded.
4. Map each changed path to subsystem owner, realm, public surfaces, persistence and validation.
5. Update `FILE_MANIFEST`, `PUBLIC_SURFACES`, system/behavior/type catalogs and packet coverage for local bot/NPC surfaces.
6. Continue weapon lifecycle and capability enumeration without mixing repository and archive evidence.
7. Define dependency-ordered runtime import packages, but do not execute them on this branch.

## Validation requirements

- Confirm archive SHA and normalized path manifest are reproducible.
- Runtime-trace server/client include order for repository and archive builds.
- Boot a clean dedicated server with only declared dependencies.
- Verify bot-disabled shipping behavior, then separately test enabled bots at 1/4/8/16/32 population.
- Capture desired aim, physical muzzle, corrected command view and shot result across target distance and posture.
- Profile bot scheduler, decision, command, navigation and trace budgets.
- Fuzz client-to-server class, bot configuration, debug, admin and mode inputs.
- Exercise fake/get-up, class, weapon, vehicle, NPC, organism and round transitions with stale callback/resource assertions.
- Test VJ/stock/ZBase NPC classification, organism ownership, knockdown, corpse transfer and cleanup.
- Do not patch documented defects before adjacent contracts and regression boundaries are complete.

## Dependency-ordered continuation

1. Obtain the recursive repository manifest, then complete the repository-versus-archive path/hash delta and import classification.
2. Weapon lifecycle, bullets, ammunition, projectiles, armor, explosives, damage and presentation.
3. Inventory/equipment/appearance/clothing ownership and restoration.
4. Complete bot/NPC public surfaces, types, packets and runtime evidence.
5. UI/HUD/camera/spectator and screen effects.
6. Persistence, administration, security and external integrations.
7. Cross-system regression matrix, verified defect catalog and implementation-ready import/remediation packages.

## Exact next action

Continue on `docs/architecture-baseline`: obtain a recursive repository tree/archive for baseline commit `429ec928203cec963176dfb6afd086dcdd01c181`, generate its path/hash manifest, join it against the pinned 1,040-row local manifest, and produce complete path and subsystem dispositions. Until recursive repository evidence is available, continue exact-path weapon/inventory/UI/security traces and preserve bounded negative claims. Do not modify runtime Lua, create another branch, or merge PR `#1` without explicit authorization.
