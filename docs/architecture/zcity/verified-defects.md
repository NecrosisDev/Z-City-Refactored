# Verified Foundation Defects

This register contains defects established by direct static inspection of the current repository. It is intentionally limited to specific, actionable findings. Broader architectural concerns belong in subsystem documents.

## ZC-FND-001 — Runtime identity points to upstream

- **Area:** Addon bootstrap
- **Source:** `lua/autorun/loader.lua`
- **Observed:** `hg.GitHub_ReposOwner` and `hg.GitHub_ReposName` identify `uzelezz123/Z-City` rather than this repository.
- **Impact:** Update/status tooling and diagnostics can attribute the running project to the wrong repository.
- **Constraint:** Preserve legacy `hg` fields until consumers are inventoried.
- **Disposition:** Introduce project-owned immutable metadata and retain compatibility aliases.

## ZC-FND-002 — Workshop setting has no effective action

- **Area:** Content delivery
- **Source:** `lua/autorun/loader.lua`
- **Observed:** `hg_loadcontent` defaults to enabled, but all guarded `resource.AddWorkshop` calls are commented out.
- **Impact:** Administrators are presented with a control that does not perform its stated function.
- **Disposition:** Replace with an explicit content manifest or remove/deprecate the setting.

## ZC-FND-003 — Unknown addon filenames default to shared execution

- **Area:** Realm loading
- **Source:** `lua/autorun/loader.lua`
- **Observed:** Files without recognized `sv_`, `sh_`, `cl_`, `_sv`, `_sh`, or `_cl` markers are sent to clients and included in both realms.
- **Impact:** A naming error can expose server implementation or execute code in an unsupported realm.
- **Disposition:** Audit unmarked files; migrate to explicit realm declarations; eventually reject unknown realm.

## ZC-FND-004 — Gamemode realm detection uses substring matching

- **Area:** Gamemode loader
- **Source:** `gamemodes/zcity/gamemode/loader.lua`
- **Observed:** Realm markers are searched across the path rather than parsed from a strict filename convention.
- **Impact:** Directory names or unrelated substrings can change how descendant files load.
- **Disposition:** Replace with anchored filename parsing behind a compatibility audit.

## ZC-FND-005 — Library and mode ordering is not explicitly sorted

- **Area:** Gamemode loader
- **Source:** `gamemodes/zcity/gamemode/loader.lua`
- **Observed:** The loader processes child folders before files but does not explicitly sort sibling results.
- **Impact:** Inheritance and hidden global dependencies can depend on engine enumeration order.
- **Disposition:** First record actual required ordering; then add deterministic phases and dependency declarations.

## ZC-FND-006 — Global `MODE` bootstrap state

- **Area:** Mode registration
- **Source:** `gamemodes/zcity/gamemode/loader.lua`
- **Observed:** Each mode is authored by mutating a temporary global `MODE` table.
- **Impact:** Errors, reentrancy, nested loading, and tooling can observe or leave invalid ambient state.
- **Disposition:** Add explicit registration for new modes and a legacy loader adapter for existing modes.

## ZC-FND-007 — Mode inheritance leaks `tbl2` globally

- **Area:** Mode inheritance
- **Source:** `gamemodes/zcity/gamemode/loader.lua`
- **Observed:** The nested-table copy loop assigns `tbl2 = {}` without `local`.
- **Impact:** A global variable is created/overwritten during mode loading, allowing accidental cross-file coupling and stale data visibility.
- **Disposition:** Correct locally when code changes begin; add a static global-leak test.

## ZC-FND-008 — Direct mode registrations are not lifecycle-owned

- **Area:** Hooks and timers
- **Source:** Mode files under `gamemodes/zcity/gamemode/modes/**`
- **Observed:** The mode-table dispatcher scopes mode methods, but direct `hook.Add`, `timer.Create`, receivers, commands, globals, and other side effects remain global.
- **Impact:** Inactive modes can retain callbacks and state; hot reload can duplicate resources.
- **Disposition:** Inventory direct registrations, then migrate through explicit owner APIs. Global interception is prohibited.

## ZC-FND-009 — Round-state comments conflict with runtime state

- **Area:** Round state
- **Sources:** `gamemodes/zcity/gamemode/init.lua`, `cl_init.lua`, `libraries/sv_roundsystem.lua`
- **Observed:** Comments describe state `2` as end-round, while the server round system uses state `3`.
- **Impact:** New consumers can implement incorrect transitions or UI behavior.
- **Disposition:** Audit all numeric state consumers, define a compatibility enum, and test wire values before changing them.

## ZC-FND-010 — `CurrentRound()` repeatedly scans for changelevel entities

- **Area:** Active-mode lookup
- **Source:** `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`
- **Observed:** `ents.FindByClass("trigger_changelevel")` is evaluated in `CurrentRound()` and `NextRound()` paths.
- **Impact:** A frequently used getter performs repeated entity scans.
- **Disposition:** Introduce an event-invalidated map capability cache without making the getter mutate lifecycle state.

## ZC-FND-011 — Round reset is a hidden multi-system transaction

- **Area:** Round transition
- **Source:** `zb:KillPlayers()` and surrounding round flow
- **Observed:** The operation grants experience, handles preserved players, clears organism state, forces fake-up, controls flashlights, kills, respawns, and assigns classes.
- **Impact:** Reordering or replacing the apparent “kill players” helper can break unrelated systems.
- **Disposition:** Document and test ordering, then expose an explicit round-reset transaction with ordered participants.

## ZC-FND-012 — Dependency warnings do not define capabilities

- **Area:** Optional/required dependencies
- **Source:** Addon bootstrap and integrations
- **Observed:** ULX/ULib absence causes repeated warnings while startup continues; unavailable features are not enumerated.
- **Impact:** Server operators cannot determine supported degraded behavior.
- **Disposition:** Build a capability registry with required/optional classification and one actionable health report.

## ZC-FND-013 — Include failures leave partial state

- **Area:** Loading
- **Sources:** Addon and gamemode recursive loaders
- **Observed:** Includes are executed directly without phase-level failure accounting or rollback.
- **Impact:** Earlier files remain registered after later foundational failures, producing a partially initialized addon.
- **Disposition:** Do not merely wrap every include and continue. Define required phases, fail-closed critical modules, optional module isolation, and structured diagnostics.

## ZC-FND-014 — First-player admission terminates the round and creates a bot

- **Area:** Player admission
- **Source:** `GM:PlayerInitialSpawn` in `gamemodes/zcity/gamemode/init.lua`
- **Observed:** The first connected player causes the server to execute `bot`, set a global bootstrap flag, and call `zb:EndRound()`.
- **Impact:** Connection handling unexpectedly mutates population and round state, complicating empty-server startup and late initialization.
- **Disposition:** Preserve until runtime-tested; then move temporary population/bootstrap policy into an explicit server lifecycle service.

## ZC-FND-015 — Engine spawn selection is bypassed

- **Area:** Spawn lifecycle
- **Source:** `gamemodes/zcity/gamemode/init.lua`
- **Observed:** `GM:PlayerSelectSpawn` is empty while a separate local function directly calls `SetPos` during `PLAYER:SetupTeam`.
- **Impact:** Team assignment, inventory creation, spawn policy, and teleportation are tightly coupled and bypass the normal spawn-selection contract.
- **Disposition:** Record mode parity, then introduce explicit resolve/validate/reserve/place phases behind compatibility wrappers.

## ZC-FND-016 — Random-spawn fallback can select unsuitable positions

- **Area:** Spawn validation
- **Source:** `zb:FurthestFromEveryone` in `gamemodes/zcity/gamemode/init.lua`
- **Observed:** Candidate checks consider only distance from alive players; after tolerance passes fail, the function returns a random candidate without validating it.
- **Impact:** Crowded, blocked, hazardous, or otherwise invalid positions can still be selected.
- **Disposition:** Preserve fallback behavior until mode tests exist; add structured validation reasons and a deterministic emergency policy.

## ZC-FND-017 — Death uses uncancellable anonymous delayed work

- **Area:** Death and spectating
- **Source:** `GM:PlayerDeath` in `gamemodes/zcity/gamemode/init.lua`
- **Observed:** A `timer.Simple(0.1, ...)` callback selects a spectator target after death.
- **Impact:** The task cannot be enumerated, cancelled, or attributed during rapid respawn, disconnect, mode changes, or hot reload.
- **Disposition:** Replace through an owned delayed-task API with player and round-generation guards.

## ZC-FND-018 — Spectator exit restores a hard-coded team

- **Area:** Spectator state
- **Source:** `ZB_SpecMode` receiver in `gamemodes/zcity/gamemode/init.lua`
- **Observed:** Leaving spectator mode assigns team `1` rather than consulting the active mode or team-balancing policy.
- **Impact:** Team-based, asymmetric, or mode-specific admission can be bypassed or temporarily corrupted.
- **Disposition:** Route spectator exit through an authoritative mode admission policy while preserving current behavior until tests exist.

## Verification policy

A defect can be closed only when:

1. the implementation change is linked;
2. compatibility behavior is documented;
3. an automated static, smoke, or behavioral test covers the defect;
4. hot reload and map cleanup are considered where applicable;
5. rollback behavior is defined.