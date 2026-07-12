# System Catalog

Stable system IDs are cross-references for architecture documents, behaviors, types, defects, validation, and future implementation work. `Verified` below means confirmed in executable source; runtime-only ordering or outcomes remain explicitly unverified.

## `SYS-BOOTSTRAP-GLOBAL` — Global addon bootstrap and recursive loader

- **Status:** `partial` — static source verified; total engine-level startup order and runtime file enumeration remain unverified.
- **Purpose:** Initializes the global `hg` namespace, routes addon Lua files by realm, recursively loads `lua/homigrad`, emits the post-load hook, and later loads `lua/initpost`.
- **Primary paths/symbols:** `lua/autorun/loader.lua`; `AddFile`, `IncludeDir`, `Run` (all local); global `hg`.
- **Realm:** Autorun file executes in server and client realms; routing behavior differs by `SERVER`.
- **Initialization/load order:** Garry's Mod autorun executes the file; `Run()` immediately loads current-directory files before child directories under `homigrad`; `InitPostEntity` later loads `initpost` using the same traversal. No explicit sort is applied to `file.Find` results.
- **Realm contract:** exact `sv_`/`sh_`/`cl_` prefix or `_sv`/`_sh`/`_cl` suffix detection; unrecognized names are sent by the server and included on both realms.
- **Public surface:** `hg.Version`, `hg.GitHub_ReposOwner`, `hg.GitHub_ReposName`, `hg.loaded`; convar `hg_loadcontent`; hook emission `HomigradRun`; hook listener `InitPostEntity`/`zcity`.
- **Dependencies:** Garry's Mod autorun, filesystem, include/AddCSLuaFile, hooks, convars; warns after five seconds when ULX/ULib is unavailable or the game is single-player.
- **Data ownership:** Each realm owns its local `hg` table; `hg_loadcontent` is archive/notify/replicated. Workshop mounting calls are present but commented out.
- **Known failure modes/risks:** implicit sibling order from unsorted `file.Find`; unmarked files execute clientside; any realm marker outside the exact prefix/suffix forms falls through to shared; active gamemode `ixhl2rp` exits after setting `hg.loaded = false`, skips `homigrad`, and does not emit `HomigradRun`; repository/version metadata still names the upstream project.
- **Validation:** Static source trace complete. Runtime validation must log included path, realm, timestamp, and `HomigradRun`/`InitPostEntity` order on dedicated server plus one client without changing persistent behavior.
- **Related:** `BEH-REALM-GLOBAL`, `TYPE-HG-BOOTSTRAP`.
- **Evidence:** `lua/autorun/loader.lua` blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`; reviewed 2026-07-12.

## `SYS-BOOTSTRAP-GAMEMODE` — ZCity gamemode bootstrap and library loader

- **Status:** `partial` — static source verified; runtime interleaving with global autorun remains unverified.
- **Purpose:** Loads shared/client/server gamemode entry points, recursively loads `gamemode/libraries`, then hands control to mode assembly.
- **Primary paths/symbols:** `gamemodes/zcity/gamemode/init.lua`, `cl_init.lua`, `shared.lua`, `loader.lua`; local `IncluderFunc`, `LoadFromDir`.
- **Realm:** Server, client, and shared entry points; loader runs on both realms through `init.lua`/`cl_init.lua`.
- **Initialization/load order:** `shared.lua` precedes `loader.lua`; `LoadFromDir("zcity/gamemode/libraries")` recurses into child folders before current-directory files. No explicit sorting is applied.
- **Realm contract:** substring matching: any path containing `sv_` is server-included; `shared.lua` or `sh_` is shared; `cl_` is sent by server and included by client; unmarked files are ignored by `IncluderFunc`.
- **Public surface:** Loaded libraries define the gamemode's globals, hooks, net receivers, commands, and `zb` APIs; the loader itself exposes no global loader function.
- **Dependencies:** `zb`/`hg` setup from shared/global bootstrap, Garry's Mod filesystem/include/AddCSLuaFile, filename conventions.
- **Data ownership:** Library state is realm-specific unless explicitly networked or stored in shared globals.
- **Known failure modes/risks:** substring routing can misclassify names containing markers away from the prefix; unmarked files silently do not load; child-first recursion differs from `SYS-BOOTSTRAP-GLOBAL`; unsorted enumeration creates implicit dependency order.
- **Validation:** Static routing/traversal trace complete. Runtime validation must compare actual server/client include manifests and detect files found but not included.
- **Related:** `BEH-REALM-GAMEMODE`, `SYS-MODE-REGISTRY`.
- **Evidence:** `gamemodes/zcity/gamemode/loader.lua` blob `b1754dff2d53012a05cb109f26b75eae118b14ce`; reviewed 2026-07-12.

## `SYS-MODE-REGISTRY` — Mode discovery, inheritance, persistence, and hook dispatch

- **Status:** `partial` — registry implementation verified; complete mode inventory and runtime dispatch validation pending.
- **Purpose:** Discovers mode files/folders, builds `MODE` tables, applies base inheritance, preserves hotload state, registers mode functions as hooks, and persists configurable mode chances.
- **Primary paths/symbols:** `gamemodes/zcity/gamemode/loader.lua`; `zb.modes`, `zb.modesHooks`, global temporary `MODE`; local `addModeHook`, `InitMode`, `LoadModes`.
- **Realm:** Registry and dispatch tables exist on both realms; chance persistence and admin commands are server-only.
- **Initialization/load order:** Libraries load first. Top-level mode files are processed before mode folders. Each candidate sets global `MODE = {}`, includes source, finalizes, stores by `MODE.name`, then clears `MODE`. Base lookup uses the already-populated `zb.modes[MODE.base]`.
- **Public surface:** `zb.modes`, `zb.modesHooks`; dynamically registered Garry's Mod hooks named by every function key on every mode; admin commands `zb_getmodeschances`, `zb_setmodechance`, `zb_savemodeschances`; data file `data/zbattle/modeschances.json`.
- **Dispatch contract:** One hook callback per hook name resolves `zb.CROUND_MAIN`, then `zb.CROUND`, then `tdm`; it invokes the selected mode function with the mode table as first argument and forwards up to six return values only when the first is non-`nil`.
- **Inheritance contract:** `table.Inherit(MODE, zb.modes[MODE.base])`, then table-valued members are copied and optional `MODE:AfterBaseInheritance()` runs. Existing `zb.modes[name].saved` survives hotload.
- **Dependencies:** `SYS-BOOTSTRAP-GAMEMODE`, `zb` namespace, mode filename ordering, mode methods such as `SetupChances`.
- **Data ownership:** Each realm owns its registry; server owns `zb.ModesChances` and JSON persistence.
- **Known failure modes/risks:** missing/unregistered base can break inheritance or nested-table access; unsorted mode discovery makes inheritance order implicit; every function on `MODE` is treated as a hook candidate, conflating helpers/lifecycle methods/engine hooks; local `tbl2` is assigned without `local`; duplicate hook identifier `zb_modehook_<hookName>` means all modes share one dispatcher per hook name by design; malformed or partial mode tables may be silently skipped only when completely empty.
- **Validation:** Build a complete mode dependency graph, classify every function key, verify base-before-child order, hotload preservation, chance persistence, and one representative hook return path on server and client.
- **Related:** `BEH-MODE-DISPATCH`, `TYPE-MODE-REGISTRY`, `TYPE-MODE-TABLE`.
- **Evidence:** `gamemodes/zcity/gamemode/loader.lua` blob `b1754dff2d53012a05cb109f26b75eae118b14ce`; reviewed 2026-07-12.

## `SYS-ROUND-LIFECYCLE` — Server-authoritative round state, selection, and client synchronization

- **Status:** `partial` — server/client source path verified; full mode interactions and runtime cycle pending.
- **Purpose:** Resolves current/next modes, progresses pre-round/active/end states, evaluates winners/timeouts, resets players, selects future modes, synchronizes clients/admin tools, and dispatches round lifecycle callbacks.
- **Primary paths/symbols:** server `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`; client `gamemodes/zcity/gamemode/cl_init.lua`; globals/functions `CurrentRound`, `NextRound`; `zb:PreRound`, `zb:RoundThink`, `zb:EndRoundThink`, `zb:RoundStart`, `zb:EndRound`, selection/queue APIs.
- **Realm:** Server authoritative; clients mirror current mode/state/time and invoke client-side mode callbacks.
- **State contract:** `0` pre-round/intermission, `1` active, `3` end period. Client comment claiming state `2` is legacy/mismatched; executable server and client branches use `3`.
- **Tick/lifecycle order:** Server `Think` hook throttles to one execution per second and calls `PreRound`, `RoundThink`, then `EndRoundThink`. State `0` schedules/starts; `RoundStart` sets `1`; end criteria call `EndRound` which sets `3`; end timer returns to `0`, resets players/equipment, and prepares the next mode.
- **Mode resolution/selection:** `CurrentRound` defaults to `hmcd` or forces `coop` when a `trigger_changelevel` exists; submode names resolve through `mode.Types`; available modes require `CanLaunch` and map-size conditions; weighted selection builds a 20-item `zb.RoundList`; convar `zb_forcemode` may override next selection.
- **Public surface:** `zb.ROUND_STATE`, `zb.CROUND`, `zb.CROUND_MAIN`, `zb.nextround`, `zb.RoundList`, `zb.QueuedModes`, `zb.ModesPlaytime`; hooks `ZB_PreRoundStart`, `ZB_StartRound`, `ZB_EndRound`, `TTTPrepareRound`; convar `zb_forcemode`; admin commands including `zb_checkchances` and `zb_rerollchances`; persistence `data/zbattle/mapsizes.json` plus mode chances owned by `SYS-MODE-REGISTRY`.
- **Network surface verified in traced sections:** `FadeScreen`, `RoundInfo`, `ZB_SendModesInfo`, `ZB_SendRoundList`, `ZB_RequestRoundList`, `ZB_UpdateRoundList`, `ZB_NotifyRoundListChange`, `SendAvailableModes`, `AdminSetGameMode`, `AdminEndRound`, `SendGameQueue`, `AdminSetGameQueue`, plus time sync `updtime` consumed by the client.
- **Data ownership/trust:** Server writes round state/mode and broadcasts `RoundInfo` (`mode.name`, signed 4-bit state). Client stores `zb.CROUND`/`zb.ROUND_STATE`, emits `RoundInfoCalled`, and invokes local `RoundStart` or `EndRound`. Admin-originating receivers check `ply:IsAdmin`; `ZB_UpdateRoundList` accepts a decoded table without shape validation and reads `forceUpdate` without using it in the traced body.
- **Dependencies:** `SYS-MODE-REGISTRY`, player reset/class/organism/fake-ragdoll APIs, map points/size, achievements, round-time sync, admin enumeration/UI, optional vFire state.
- **Known failure modes/risks:** state comment drift; mode callback availability assumed at multiple call sites; one-second lifecycle cadence; network table payload lacks explicit schema validation; static source cannot prove global hook ordering; many external subsystem calls make round transitions a high-risk integration boundary.
- **Validation:** Dedicated-server cycle covering `0 -> 1 -> 3 -> 0`, late join synchronization, forced/random/queued selection, submode resolution, end timeout, changelevel/coop path, player reset, client callbacks, malformed/unauthorized admin messages, and persistence reload.
- **Related:** `BEH-ROUND-CYCLE`, `BEH-MODE-SELECTION`, `TYPE-ROUND-STATE`, `TYPE-ROUNDINFO-PAYLOAD`, `TYPE-MODE-TABLE`.
- **Evidence:** `sv_roundsystem.lua` blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; `cl_init.lua` blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; reviewed 2026-07-12.

## `SYS-ORGANISM` — Physiological state, organ geometry, damage and replication

- **Status:** `partial` — authoritative ownership, state, module order, damage path and primary replication are source-verified; every medical/item/client consumer and runtime cost remain incomplete.
- **Purpose:** Attaches a mutable physiological state to players, NPCs and ragdolls; simulates blood, pain, pulse, lungs, stamina, metabolism, organs, limbs and consciousness; resolves custom organ penetration and wounds; drives fake/unconscious/death state; synchronizes clients.
- **Primary paths/symbols:** `lua/homigrad/organism/tier_0/*`, `tier_1/sv_organism.lua`, `tier_1/sv_input.lua`, `tier_1/modules/*`, `tier_1/modules_input/*`, `tier_1/cl_statistics.lua`, `tier_1/cl_main.lua`, `organism/sv_brainfuck.lua`; `hg.organism`, `hg.organism.list`, `hg.organism.module`, `hg.organism.input_list`.
- **Realm:** Server authoritative physiology/damage; shared organ geometry; client snapshot/interpolation/presentation.
- **Ownership contract:** One mutable organism table is attached to an entity and can be shared by player, fake ragdoll and death ragdoll. `owner` is current authoritative entity and `ownerX` preserves identity/origin. Transfers and delayed callbacks must preserve this invariant.
- **Tick contract:** Tier 0 emits `Org Think` at approximately 10 Hz. Core module order is stamina, lungs, liver, blood, pain, metabolism, random events, pulse, followed by other same-hook consumers such as virus and brain-spasm code. Execution order materially changes gameplay values.
- **Damage contract:** `EntityTakeDamage/homigrad-damage` derives weapon/bullet penetration and custom OBB intersections, calls organ/bone/artery handlers, creates wounds, mutates physiology, emits project damage hooks, applies physical/effect output and heavily scales ordinary engine damage. Collision damage enters through separate ragdoll/player physics hooks.
- **Replication contract:** `organism_send` writes a Lua-table snapshot plus four branch booleans. Owner snapshots are roughly one second; PVS snapshots one to three seconds depending on organism type; partial merge packets and wound NetVars overlap the same authority. Developer mode can send the entire organism table.
- **Public surface:** hooks `Org Add`, `Org Clear`, `Org Think`, `Org Transfer`, `Org Think Call`, `HG_OnOtrub`, `HG_OnWakeOtrub`, `Should Fake Up`, `PreHomigradDamage`, `PreHomigradDamageBulletBleedAdd`, `HomigradDamage`, `OnAmputateLimb`, `Ragdoll Collide`, `RagdollDeath`; APIs documented in `architecture/ORGANISM_SYSTEM.md`; commands `hg_fixdislocation`, breath commands; convars for unreliable nets, developer detail, stamina, hunger and presentation.
- **Dependencies:** global loader order, ValveBiped model/bone conventions, fake-ragdoll ownership, physical bullets/weapons, armor, inventory, medical items, player classes, modes, NetVars and UI/effects.
- **Known failure modes/risks:** unsorted Tier 0/Tier 1 load assumption; implicit duplicated schema; mutable player/ragdoll table aliasing; order-dependent physiology; monolithic damage hook; global penetration overrides; nil/uninitialized pre-damage hook fields; inconsistent entity/bone/armor guards; overlapping snapshots/NetVars; unversioned Lua tables; client owner validation after method access; fixed-cadence bandwidth/CPU scaling; dormant `organism_sendply` and readerless `VirusStageUpdate`; model-dependent missing organs; division-by-zero and extreme-value paths.
- **Validation:** startup order instrumentation; canonical reset-schema assertion; deterministic module-order tests; player/NPC/fake/death ownership transitions; every damage type/model/armor combination; penetration/reentrancy/collision/amputation; packet bit/size/cadence capture; private/public field exposure; population performance budgets.
- **Related:** `architecture/ORGANISM_SYSTEM.md`; future `SYS-FAKE-RAGDOLL`, `SYS-MOVEMENT`, `SYS-PLAYER-CLASS`; `TYPE-ORGANISM-STATE`, `TYPE-ORGANISM-SNAPSHOT`; `BEH-ORGANISM-LIFECYCLE`.
- **Evidence:** Tier 0 blob `1b8a72186b295f3542dd90d92374d5985d7d6e62`; Tier 1 core blob `4830503722f005d27373047d8db5c58d4e217559`; damage blob `cce5ff506e9799eb3c1e104ea3146927a8936326`; client snapshot blob `c3c5db65d44125a2acf5df4be1b6fe13d891a86f`; reviewed 2026-07-12.
