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

- **Status:** `partial` — registry implementation verified; runtime dispatch instrumentation pending.
- **Purpose:** Discovers mode files/folders, builds `MODE` tables, applies base inheritance, preserves hotload state, registers mode functions as hooks, and persists configurable mode chances.
- **Primary paths/symbols:** `gamemodes/zcity/gamemode/loader.lua`; `zb.modes`, `zb.modesHooks`, global temporary `MODE`; local `addModeHook`, `InitMode`, `LoadModes`.
- **Realm:** Registry and dispatch tables exist on both realms; chance persistence and admin commands are server-only.
- **Initialization/load order:** Libraries load first. Top-level mode files are processed before mode folders. Each candidate sets global `MODE = {}`, includes source, finalizes, stores by `MODE.name`, then clears `MODE`. Base lookup uses the already-populated `zb.modes[MODE.base]`.
- **Public surface:** `zb.modes`, `zb.modesHooks`; dynamically registered hooks named by every function key; mode chance commands and `data/zbattle/modeschances.json`.
- **Dispatch contract:** One hook callback per hook name resolves `zb.CROUND_MAIN`, then `zb.CROUND`, then `tdm`; selected function receives the mode table as first argument and forwards up to six returns only when the first is non-`nil`.
- **Inheritance contract:** `table.Inherit(MODE, zb.modes[MODE.base])`, nested table copies, optional `AfterBaseInheritance`; `saved` state survives hotload.
- **Known failure modes/risks:** unsorted base/child discovery; every function becomes a hook candidate; dot-defined argument shift; empty override/inherited surface; disabled modes still register callbacks; duplicate hook identifier per function name by design.
- **Validation:** runtime registration order, server/client parity, callback arguments/returns, hotload and external hook-name emissions.
- **Related:** `BEH-MODE-DISPATCH`, `TYPE-MODE-REGISTRY`, `TYPE-MODE-TABLE`, `reference/MODE_FUNCTION_MATRIX.md`.
- **Evidence:** `loader.lua` blob `b1754dff2d53012a05cb109f26b75eae118b14ce`; reviewed 2026-07-12.

## `SYS-ROUND-LIFECYCLE` — Server-authoritative round state, selection, and client synchronization

- **Status:** `partial` — server/client source path verified; full integrated cycle pending.
- **Purpose:** Resolves current/next modes, progresses pre-round/active/end states, evaluates winners/timeouts, resets players, selects future modes, synchronizes clients/admin tools, and dispatches lifecycle callbacks.
- **Primary paths/symbols:** `sv_roundsystem.lua`, client `cl_init.lua`; `CurrentRound`, `NextRound`, `zb:PreRound`, `RoundThink`, `EndRoundThink`, `RoundStart`, `EndRound`.
- **Realm/state:** Server authoritative; client mirror. Verified states `0` pre-round, `1` active, `3` end; state-2 comments/listeners are stale.
- **Tick/lifecycle:** server Think once/second; `0 -> 1 -> 3 -> 0`; reset/equipment/intermission work spans many subsystems.
- **Public surface:** round globals, `ZB_PreRoundStart`, `ZB_StartRound`, `ZB_EndRound`, `TTTPrepareRound`, force/queue/admin packets, time/spectator synchronization and map-size persistence.
- **Dependencies:** mode registry, player reset/class/organism/fake, map points, achievements, admin UI and optional integrations.
- **Known failure modes/risks:** overlapping queue protocols/lists; unvalidated admin tables; mode callbacks assumed; one-second cadence; stale hook names; spawn/get-up interactions through `OverrideSpawn`.
- **Validation:** dedicated full cycle, late joins, selection, admin end, CO-OP/changelevel, reset/equipment, malformed admin transport and persistence reload.
- **Related:** `BEH-ROUND-CYCLE`, `BEH-MODE-SELECTION`, `TYPE-ROUND-STATE`, `TYPE-ROUNDINFO-PAYLOAD`, `TYPE-ROUND-QUEUE`.
- **Evidence:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; reviewed 2026-07-12.

## `SYS-ORGANISM` — Physiological state, organ geometry, damage and replication

- **Status:** `partial` — authoritative ownership, state, module order, damage path and primary replication are source-verified; every medical/item/client consumer and runtime cost remain incomplete.
- **Purpose:** Attaches mutable physiology to players, NPCs and ragdolls; simulates blood, pain, pulse, lungs, stamina, metabolism, organs, limbs and consciousness; resolves penetration/wounds; drives fake/unconscious/death state; synchronizes clients.
- **Primary paths/symbols:** `organism/tier_0/*`, `tier_1/sv_organism.lua`, `sv_input.lua`, `modules/*`, `modules_input/*`, `cl_statistics.lua`, `cl_main.lua`, `sv_brainfuck.lua`; `hg.organism`, registries/modules/inputs.
- **Realm:** Server authoritative physiology/damage; shared geometry; client snapshots/interpolation/effects.
- **Ownership:** one mutable table may be shared by player, fake ragdoll and death ragdoll; `owner` changes and `ownerX` preserves identity.
- **Tick:** Tier 0 emits ~10 Hz `Org Think`; core order stamina, lungs, liver, blood, pain, metabolism, random events, pulse, then additional hook consumers.
- **Damage:** monolithic `EntityTakeDamage/homigrad-damage` handles bullet/armor/OBB/organ/wound/effects/physics/replication; collisions enter separate hooks.
- **Replication:** `organism_send` unversioned Lua table + four booleans; owner/PVS/partial/developer variants plus wound NetVars.
- **Public surface:** organism lifecycle/damage/amputation/ragdoll hooks; geometry/damage/replication APIs; dislocation/breath commands.
- **Known failure modes/risks:** load-order assumption; implicit schema; shared-table aliasing; order-dependent modules; global penetration overrides; nil trace/entity assumptions; overlapping transport; client owner dereference before validity; fixed-cadence CPU/bandwidth; model assumptions/extreme values.
- **Validation:** startup/schema, deterministic simulation, owner transitions, damage/model/armor/penetration/collision/amputation, packet cost/privacy and population budgets.
- **Related:** `architecture/ORGANISM_SYSTEM.md`, `SYS-FAKE-RAGDOLL`, future `SYS-MOVEMENT`, `SYS-PLAYER-CLASS`; organism types/behavior.
- **Evidence:** Tier 0 `1b8a72186b295f3542dd90d92374d5985d7d6e62`; core `4830503722f005d27373047d8db5c58d4e217559`; damage `cce5ff506e9799eb3c1e104ea3146927a8936326`; client snapshot `c3c5db65d44125a2acf5df4be1b6fe13d891a86f`; reviewed 2026-07-12.

## `SYS-FAKE-RAGDOLL` — Living-body replacement, active physics control, death and get-up

- **Status:** `partial` — core creation, ownership, controls, networking, camera/render, death and get-up are source-verified; every weapon/vehicle/class integration and runtime performance remain incomplete.
- **Purpose:** Replaces the visible/colliding living player with a custom controllable physical ragdoll while preserving identity, organism, appearance, equipment, camera, NPC targeting, vehicle state and death-body continuity.
- **Primary paths/symbols:** `lua/homigrad/fake/sv_tier_0.lua`, `sv_control.lua`, `sv_input.lua`, `cl_fake.lua`, `sh_render.lua`; `hg.Ragdoll_Create`, `hg.Fake`, `hg.FakeUp`, `hg.GetCurrentCharacter`, `hg.RagdollOwner`, `hg.ragdollFake`, NWEntities and lifecycle hooks.
- **Realm:** Server authoritative body creation/physics/transition; client reconstructs ownership through NWVar proxies, controls camera/render and smooth get-up.
- **Ownership contract:** server fields/maps, NWEntity `FakeRagdoll`/`RagdollDeath`, custom `Player Ragdoll` packet/index, client proxy state and shared organism table must all refer to one current body generation.
- **Entry/death:** custom `prop_ragdoll`, appearance/pose/physics/bullseye/PVS/vehicle setup; player hidden/noninteractive; death reuses body and suppresses engine ragdoll.
- **Get-up:** validates state/velocity/stun/space, emits hooks, sets global/network spawn override, respawns player, restores partial state, removes body and restores rendering/collision/movement.
- **Control:** per-frame all-player Think drives physics bodies, crawling, grabbing, choking, weapon callbacks, use/pickup, stamina, pain, fire and player position from organism/input state.
- **Replication:** `Player Ragdoll` writes player + body/null but client depends on undefined external `net.ReadEntity2()` dual return; actual ownership primarily follows NWEntity proxies. `Override Spawn` coordinates get-up spawn suppression.
- **Public surface:** `Ragdoll_Create`, `Fake`, `Fake Up`, `Should Fake Up`, `CanControlFake`, `RagdollEntityCreated`, `RagdollRemove`, `Ragdoll Collide`, decal/prediction/collision hooks; fake/control/render APIs; fake/force_fake commands and camera/control convars.
- **Dependencies:** organism, movement, player classes, weapons, appearance/armor/gore, NPC relationships, vehicles/Glide/simfphys, round spawn, spectator/camera and fire integrations.
- **Known failure modes/risks:** overlapping ownership channels without generation; no transactional rollback; respawn-based get-up/global `OverrideSpawn`; undefined `ReadEntity2`; partial body/bullseye creation; hard-coded ValveBiped physics map; per-frame multi-body cost; invalid physics/bone/weapon assumptions; inverted/ambiguous hook semantics; stale timers/constraints; vehicle core branching; client camera/render global leaks; disconnect organism API misuse.
- **Validation:** lifecycle failure injection, owner-generation assertions, packet/NW order/PVS/late join, model/physics compatibility, per-frame scale tests, grabbing/choking/combat/fire, get-up spawn preservation, vehicle adapters and camera/render restoration.
- **Related:** `architecture/FAKE_RAGDOLL_SYSTEM.md`, `SYS-ORGANISM`, future `SYS-MOVEMENT`, `SYS-PLAYER-CLASS`; fake state/payload types and behavior.
- **Evidence:** server Tier 0 blob `0fa522db3f0562eaf1816d6452fa082aef81d2bb`; control blob `22c87ad4148716ff1173c104e7df943043b09ce5`; input blob `545f7b292c6bdb4610766700251cc741072a5e2e`; client blob `bdd7e6a215da568a2070bd9b33e29244f1970f90`; render blob `ddf5584d6ab0e51fdbb8fa802e87a40ec2c80ffe`; reviewed 2026-07-12.
