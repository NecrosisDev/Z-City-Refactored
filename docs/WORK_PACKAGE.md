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

- Project structure, bootstrap/load order, realm routing, mode registration, round lifecycle, shared system/behavior/type contracts, file-manifest boundaries, and public surfaces are documented in the linked architecture/catalog/reference files.
- Every known top-level mode directory has a verified registry identity or explicit unresolved-file boundary:
  - core: `tdm`, `cstrike`, `dm`, `hmcd`, `fear`;
  - team/PvE: `hl2dm`, `coop`, `defense`, `criresp`, `pathowogen`;
  - additional: `riot`, `gwars`, `superfighters`, `scugarena`, `event`.
- `docs/reference/MODE_FUNCTION_MATRIX.md` now classifies all function/member families already verified in fetched mode source, records dispatcher argument behavior, duplicate/overwrite hazards, inheritance coupling, collision groups, realms, and exact completion requirements.
- `docs/reference/PACKET_MATRIX.md` now consolidates all currently known core/admin and mode channels with direction, ordered schema, trust, validation, mismatch, rate/size, duplicate/legacy and endpoint status.
- The two matrices are deliberately marked partial: they distinguish catalog-derived verified rows from the remaining exact source-line enumeration and unresolved auxiliary files.
- `docs/README.md` indexes the matrices as authoritative references; existing grouped catalogs remain the detailed per-mode evidence source.

## High-impact verified findings

### Framework

- Global and gamemode loaders differ in realm/traversal rules; neither explicitly sorts `file.Find` results.
- Mode inheritance requires an already-registered base despite unsorted mode-directory enumeration.
- Every function-valued mode member becomes a hook candidate; dot-defined functions receive shifted arguments.
- Round states are `0`, `1`, `3`; stale comments/listeners use `2`.
- Round administration contains overlapping protocols and duplicate name-keyed registrations; client-supplied tables are weakly validated.

### Cross-mode matrices

- Repeated collision groups are now explicit: `GuiltCheck`, `CanLaunch`, delayed winner callbacks, spawn override members, inheritance callbacks, and internal helpers stored on `MODE`.
- Confirmed packet mismatches include `tdm_start`, `CS_Roundover`, `hl2dm_roundend`, `npc_defense_newwave`, and conditional `HMCD_RoundStart` roster decoding.
- Highest-risk untrusted payloads are admin queue/list tables, TDM purchases, Fear light vectors, Crisis customization, Defense support commands, Event loot edits, and Pathowogen's complex end table.
- Lua-table protocols lack explicit versions/count limits; entity payloads lack consistent disconnect/validity semantics; many client requests lack phase/rate/alive/role checks.
- Fear and Pathowogen are hard-disabled for normal selection but still load function/direct-hook surfaces that require inactive-mode gating audits.

## Current bounded trace

Convert the catalog-derived matrices into exact executable-source inventories and close unresolved auxiliary endpoints before moving into organism/fake-ragdoll/movement.

### Required outputs

1. Fetch every server/shared mode file and enumerate every final function-valued `MODE` assignment with definition style, exact path/blob/line, realm, expected arguments, return contract, caller, class, inheritance and duplicate status.
2. Enumerate every loaded `util.AddNetworkString`, `net.Receive`, `net.Start`, `net.Write*` and `net.Read*`; update the packet matrix with exact source endpoints and every conditional branch.
3. Resolve Defense auxiliary wave/support/highlight files and methods.
4. Resolve Homicide/Fear assistant, police-role, subrole, role-selection and conditional packet endpoints.
5. Resolve Counter-Strike bomb/hostage entities, killfeed/intermission readers and objective payloads.
6. Resolve Pathowogen `derma/` files, end-report consumers and inactive-mode direct hooks.
7. Trace framework consumers for `OverideSpawnPos`/spawn override, `COMMANDS`, map-point fallback, `zb.EndMatch`, round-hook names and mode cleanup.
8. Update the two matrices and existing catalogs/reference files; do not create another branch, PR or duplicate index.

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
- Recursive path enumeration remains incomplete because the connector cannot reliably list directories; repository code search was transiently unavailable during the matrix pass, so source discovery must continue through known paths, indexed results and fetched executable files rather than guesses.
- No dedicated-server smoke-test evidence has been captured.
- Documented defects must not be patched until adjacent contracts and integration boundaries are mapped.

## Dependency-ordered continuation

1. Complete exact function and packet source enumeration and close remaining mode endpoint/file gaps.
2. Complete file/realm/public-surface inventories exposed by those matrices.
3. Trace organism, fake-ragdoll, movement and player-class systems.
4. Trace weapons/combat/explosives, inventory/equipment/appearance, NPC/bots, UI/camera/spectator, persistence/admin/security/integrations.
5. Produce cross-system integration map, regression matrix, verified defect catalog and implementation-ready remediation packages.
6. Begin implementation on justified branches only after research defines boundaries and the user approves transition.

## Exact next action

Continue on `docs/architecture-baseline`: fetch the known server/shared mode files in catalog order, enumerate every function-valued `MODE` assignment into `MODE_FUNCTION_MATRIX.md`, and simultaneously pair each network operation into `PACKET_MATRIX.md`; prioritize Defense auxiliary paths, Homicide/Fear endpoints, Counter-Strike objective entities and Pathowogen derma files, then refresh this handoff and PR #1 without creating another branch or PR.
