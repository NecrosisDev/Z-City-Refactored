# Behavior Catalog

Externally observable behavior is recorded independently from implementation structure. `Verified` means executable source establishes the behavior; entries remain `partial` when runtime evidence or integration coverage is still missing.

## `BEH-REALM-GLOBAL` — Global addon files are routed by exact prefix/suffix with shared fallback

- **Status:** `partial` — routing code verified; complete runtime manifest pending.
- **Actors/context:** Server and clients loading files beneath `lua/homigrad` and `lua/initpost` through the global autorun loader.
- **Trigger:** Immediate autorun `Run()` or later `InitPostEntity` callback.
- **Observable result:** `sv_`/`_sv` files execute only on the server; `sh_`/`_sh` files are sent and execute on both; `cl_`/`_cl` files are sent by server and execute on client; unrecognized names are treated as shared. Current-directory files are processed before child directories.
- **Edge cases:** Matching examines only exact first/last three-character markers; unsorted `file.Find` order is not guaranteed; `ixhl2rp` skips the main tree after setting `hg.loaded = false`; unmarked sensitive code is client-delivered.
- **Implementation evidence:** `lua/autorun/loader.lua`: `sides`, `AddFile`, `IncludeDir`, `Run`, `InitPostEntity` hook.
- **Regression procedure:** Instrument include paths in a test-only environment, start dedicated server plus client, and compare actual execution realm/order against a generated expected manifest containing each marker and one unmarked file.
- **Related:** `SYS-BOOTSTRAP-GLOBAL`, `TYPE-HG-BOOTSTRAP`.
- **Last verified:** source blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`, 2026-07-12.

## `BEH-REALM-GAMEMODE` — Gamemode files use substring routing and child-first recursion

- **Status:** `partial` — routing code verified; complete runtime manifest pending.
- **Actors/context:** Server and clients loading `gamemodes/zcity/gamemode/libraries` and mode folders.
- **Trigger:** `init.lua`/`cl_init.lua` includes `loader.lua`; loader calls `LoadFromDir`.
- **Observable result:** Child folders load before current-directory files. Paths containing `sv_` are server-included, `shared.lua` or `sh_` are shared, and `cl_` are client-targeted. Files without a recognized substring are not included by this loader.
- **Edge cases:** A marker anywhere in the full path can classify the file; unmarked files silently remain unloaded; sibling order is unsorted; behavior differs materially from `BEH-REALM-GLOBAL`.
- **Implementation evidence:** `gamemodes/zcity/gamemode/loader.lua`: `IncluderFunc`, `LoadFromDir`.
- **Regression procedure:** Generate actual server/client include logs for libraries and mode folders, flag discovered Lua files with zero includes, duplicate includes, unexpected realm execution, or order dependencies.
- **Related:** `SYS-BOOTSTRAP-GAMEMODE`.
- **Last verified:** source blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `BEH-MODE-DISPATCH` — Current mode functions are dispatched through shared hook callbacks

- **Status:** `partial` — dispatch implementation and known-mode function matrix verified; runtime external hook coverage pending.
- **Actors/context:** Any server/client engine or project hook whose name matches a function key stored on a registered mode.
- **Trigger:** `InitMode` iterates mode functions and calls `addModeHook`; later `hook.Run` invokes the registered dispatcher.
- **Observable result:** Dispatcher selects `zb.CROUND_MAIN`, then `zb.CROUND`, then `tdm`; it invokes the selected function with its mode table as first argument. Up to six values are returned only when the first return value is non-`nil`.
- **Edge cases:** All function-valued mode members are registered, including internal helpers; dot-defined functions receive shifted arguments; empty callbacks can suppress inherited behavior; disabled modes still publish callbacks; multiple modes share one dispatcher identifier per hook name.
- **Implementation evidence:** `gamemodes/zcity/gamemode/loader.lua`; `reference/MODE_FUNCTION_MATRIX.md`.
- **Regression procedure:** Verify selected mode, realm, arguments, `self`, nil/non-nil return forwarding, fallback to `tdm`, inheritance, hotload and accidental helper-name emissions.
- **Related:** `SYS-MODE-REGISTRY`, `TYPE-MODE-TABLE`, `TYPE-MODE-REGISTRY`.
- **Last verified:** source blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `BEH-MODE-SELECTION` — Server builds, overrides, and synchronizes the future round sequence

- **Status:** `partial` — static selection and admin paths verified; probability/runtime validation pending.
- **Actors/context:** Server round manager, registered modes, administrators, and admin UI clients.
- **Trigger:** Empty `zb.RoundList`, explicit reroll/set/queue request, round start, map-size change, force-mode change, or admin request.
- **Observable result:** Available modes pass `CanLaunch` and map-size rules; weighted selection fills 20 future entries, removes the first into `zb.nextround`, and may be overridden by `zb_forcemode` or admin actions. Admin clients receive modes, list, next mode, and force-mode state.
- **Edge cases:** Empty/invalid mode sets, unsorted/random traversal, overlapping admin protocols and unvalidated incoming queue tables require runtime/fuzz validation.
- **Implementation evidence:** `sv_roundsystem.lua`, `loader.lua`, packet/mode matrices.
- **Regression procedure:** Seed deterministic chances, verify eligibility/queue/force behavior, persistence reload, malformed/unauthorized admin input and all-client synchronization.
- **Related:** `SYS-MODE-REGISTRY`, `SYS-ROUND-LIFECYCLE`, `TYPE-ROUND-QUEUE`, `TYPE-MODE-TABLE`.
- **Last verified:** `sv_roundsystem.lua` blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`, 2026-07-12.

## `BEH-ROUND-CYCLE` — Rounds progress through pre-round, active, end, and preparation states

- **Status:** `partial` — server/client state transitions verified in source; full integrated cycle pending.
- **Actors/context:** Dedicated server, all connected players, current mode, clients, and dependent reset/equipment systems.
- **Trigger:** Server `Think` hook once per second; timers, mode end criteria, admin end request, or pre-round start deadline.
- **Observable result:** State `0` schedules and starts a round; `RoundStart` sets state `1`, broadcasts `RoundInfo`, calls mode start callbacks, and chooses the next mode; end criteria set state `3`, call end callbacks, emit hooks/fade, and start an end timer; expiry returns to `0`, broadcasts state, resets players, and runs intermission/equipment preparation. Late joiners receive current `RoundInfo`.
- **Client result:** Client stores the mode/state, emits `RoundInfoCalled`, and invokes local mode lifecycle callbacks.
- **Edge cases:** Stale state-2 comments/listeners, changelevel-forced CO-OP, external subsystem failures, one-second cadence and realm-separated same-name callbacks.
- **Implementation evidence:** server `sv_roundsystem.lua`; client `cl_init.lua`.
- **Regression procedure:** Dedicated trace for `0 -> 1 -> 3 -> 0`, late join/disconnect, forced/random modes, timeout/mode end, CO-OP transition, reset/equipment calls and packet values.
- **Related:** `SYS-ROUND-LIFECYCLE`, `TYPE-ROUND-STATE`, `TYPE-ROUNDINFO-PAYLOAD`, `TYPE-MODE-TABLE`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; 2026-07-12.

## `BEH-ORGANISM-LIFECYCLE` — Physiological state follows the character through injury, fake ragdoll, unconsciousness and death

- **Status:** `partial` — source behavior verified; deterministic/runtime integration and every medical consumer remain pending.
- **Actors/context:** Living players, supported NPCs, fake ragdolls, death ragdolls, damage sources, modes/classes, medical systems and observing clients.
- **Trigger:** Initial spawn, organism clear/transfer, the global 10 Hz organism loop, damage/collision, fake/get-up, medical mutation, death or entity removal.
- **Observable result:** A mutable organism table is attached and reset; modules update stamina, breathing, blood, pain, metabolism, random events and pulse in fixed order; custom organ hitboxes translate damage into wounds/organ/bone state; physiology determines movement, unconsciousness, fake-ragdoll use and death; clients receive interpolated snapshots and effects.
- **Ownership result:** Player, fake ragdoll and death ragdoll can share the same organism table while `owner` changes. Damage to a faking player is redirected to the ragdoll, and get-up/death preserve physiological state rather than creating a clean copy.
- **Network result:** Owner and nearby observer snapshots use `organism_send` with a Lua table plus branch booleans; partial merges and wound NetVars update overlapping parts of the state.
- **Edge cases:** Unsorted Tier 0/Tier 1 load assumption; shared-table aliasing; module/hook order overwrites; unsupported models/missing bones; global penetration overrides; invalid attacker/inflictor/armor state; extreme/NaN/infinite physiology; delayed callbacks after ownership transfer; unversioned/high-frequency replication; client owner dereference before validity check.
- **Implementation evidence:** `organism/tier_0/*`, `tier_1/sv_organism.lua`, `tier_1/sv_input.lua`, `tier_1/modules/*`, `tier_1/modules_input/*`, `tier_1/cl_statistics.lua`, `organism/sv_brainfuck.lua`; `architecture/ORGANISM_SYSTEM.md`.
- **Regression procedure:** Record startup order and default schema; exercise player/NPC/fake/death ownership transitions; deterministic module-order fixtures; every damage type/model/armor path; collision/penetration/amputation; packet size/cadence/public-private exposure across population levels.
- **Related:** `SYS-ORGANISM`, `TYPE-ORGANISM-STATE`, `TYPE-ORGANISM-SNAPSHOT`; future fake-ragdoll/movement/class behavior entries.
- **Last verified:** Tier 0 blob `1b8a72186b295f3542dd90d92374d5985d7d6e62`; Tier 1 blob `4830503722f005d27373047d8db5c58d4e217559`; damage blob `cce5ff506e9799eb3c1e104ea3146927a8936326`; 2026-07-12.
