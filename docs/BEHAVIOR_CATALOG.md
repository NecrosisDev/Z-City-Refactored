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

- **Status:** `partial` — dispatch implementation verified; complete function classification and runtime hook coverage pending.
- **Actors/context:** Any server/client engine or project hook whose name matches a function key stored on a registered mode.
- **Trigger:** `InitMode` iterates mode functions and calls `addModeHook`; later `hook.Run` invokes the registered dispatcher.
- **Observable result:** Dispatcher selects `zb.CROUND_MAIN`, then `zb.CROUND`, then `tdm`; it invokes the selected function with its mode table as first argument. Up to six values are returned only when the first return value is non-`nil`.
- **Edge cases:** All function-valued mode members are registered as hook candidates, including possible helpers and lifecycle methods; missing current mode/hook is ignored; multiple modes share one dispatcher identifier per hook name; base-mode registration order affects inherited functions.
- **Implementation evidence:** `gamemodes/zcity/gamemode/loader.lua`: `addModeHook`, `InitMode`, `zb.modesHooks`, `zb.modes`.
- **Regression procedure:** For representative engine hooks, verify selected mode, arguments, `self`, nil/non-nil return forwarding, fallback to `tdm`, hotload behavior, and that internal helper names do not accidentally collide with emitted hooks.
- **Related:** `SYS-MODE-REGISTRY`, `TYPE-MODE-TABLE`, `TYPE-MODE-REGISTRY`.
- **Last verified:** source blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `BEH-MODE-SELECTION` — Server builds, overrides, and synchronizes the future round sequence

- **Status:** `partial` — static selection and admin paths verified; probability/runtime validation pending.
- **Actors/context:** Server round manager, registered modes, administrators, and admin UI clients.
- **Trigger:** Empty `zb.RoundList`, explicit reroll/set/queue request, round start, map-size change, force-mode change, or admin request.
- **Observable result:** Available modes pass `CanLaunch` and map-size rules; weighted selection fills 20 future entries, removes the first into `zb.nextround`, and may be overridden by `zb_forcemode` or admin actions. Admin clients receive modes, list, next mode, and force-mode state.
- **Edge cases:** Weight calculation multiplies chances by 100 and passes the total to `math.random`; empty/invalid mode sets need runtime validation; `RandomPairs` affects traversal; `forceUpdate` is read from `ZB_UpdateRoundList` but unused in the traced receiver; incoming list table has no explicit shape validation beyond admin authorization.
- **Implementation evidence:** `sv_roundsystem.lua`: `GetAvailableModes`, `GetChance`, `GetModesChances`, `WeightedChanceMode`, `RerollChances`, `SetRoundList`, admin net receivers and commands; `loader.lua` chance persistence.
- **Regression procedure:** Seed deterministic test chances, run large selection sample, verify eligibility filtering, queue order, force-mode override/reset, submode selection, persistence reload, unauthorized rejection, malformed admin payload handling, and client synchronization.
- **Related:** `SYS-MODE-REGISTRY`, `SYS-ROUND-LIFECYCLE`, `TYPE-ROUND-QUEUE`, `TYPE-MODE-TABLE`.
- **Last verified:** `sv_roundsystem.lua` blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`, 2026-07-12.

## `BEH-ROUND-CYCLE` — Rounds progress through pre-round, active, end, and preparation states

- **Status:** `partial` — server/client state transitions verified in source; full integrated cycle pending.
- **Actors/context:** Dedicated server, all connected players, current mode, clients, and dependent reset/equipment systems.
- **Trigger:** Server `Think` hook once per second; timers, mode end criteria, admin end request, or pre-round start deadline.
- **Observable result:** State `0` schedules and starts a round; `RoundStart` sets state `1`, broadcasts `RoundInfo`, calls mode start callbacks, and chooses the next mode; end criteria set state `3`, call end callbacks, emit hooks/fade, and start an end timer; expiry returns to `0`, broadcasts state, resets players, and runs intermission/equipment preparation. Late joiners receive current `RoundInfo`.
- **Client result:** Client stores the broadcast mode and signed 4-bit state, emits `RoundInfoCalled`, and calls local mode `RoundStart` for `1` or `EndRound` for `3`; state `0` activates fade handling.
- **Edge cases:** Client comment incorrectly names `2` as end state; current mode defaults to `hmcd` and changelevel maps force `coop`; multiple external subsystem calls can abort transitions; lifecycle polling is one-second cadence; client callbacks repeat server-named methods in a separate realm and must remain side-safe.
- **Implementation evidence:** server `sv_roundsystem.lua`: `CurrentRound`, `PreRound`, `RoundStart`, `RoundThink`, `ShouldRoundEnd`, `EndRound`, `EndRoundThink`, `Think`; client `cl_init.lua`: `RoundInfo` receiver.
- **Regression procedure:** Capture a dedicated-server trace for `0 -> 1 -> 3 -> 0`, including one late join, one disconnect, forced and random modes, timeout and mode-defined end, coop changelevel path, player reset/equipment calls, client callback counts, and network payload values.
- **Related:** `SYS-ROUND-LIFECYCLE`, `TYPE-ROUND-STATE`, `TYPE-ROUNDINFO-PAYLOAD`, `TYPE-MODE-TABLE`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; 2026-07-12.