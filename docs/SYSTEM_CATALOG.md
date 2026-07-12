# System Catalog

Stable system IDs are cross-references for architecture documents, behaviors, types, defects, validation, and future implementation work. `Verified` means confirmed in executable source; runtime-only ordering or outcomes remain explicitly unverified.

## `SYS-BOOTSTRAP-GLOBAL` — Global addon bootstrap and recursive loader

- **Status:** `partial` — static source verified; runtime startup order remains unverified.
- **Purpose:** Initializes `hg`, recursively realm-routes `lua/homigrad`, emits `HomigradRun`, and loads `lua/initpost` after `InitPostEntity`.
- **Primary source:** `lua/autorun/loader.lua` blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`.
- **Realm/order:** current-directory files before child directories; exact prefix/suffix routing; unmarked files are shared; `file.Find` results are unsorted.
- **Risks:** implicit load order, client delivery of unmarked files, ixhl2rp early return, upstream metadata drift.
- **Validation:** log path, realm, timestamp, and lifecycle hooks on dedicated server/client.
- **Related:** `BEH-REALM-GLOBAL`, `TYPE-HG-BOOTSTRAP`.

## `SYS-BOOTSTRAP-GAMEMODE` — ZCity gamemode bootstrap and library loader

- **Status:** `partial`.
- **Purpose:** Loads shared/server/client entry points and recursively loads gamemode libraries and modes.
- **Primary source:** `gamemodes/zcity/gamemode/loader.lua` blob `b1754dff2d53012a05cb109f26b75eae118b14ce`.
- **Realm/order:** child directories before current-directory files; substring realm matching; unmarked files ignored; unsorted enumeration.
- **Risks:** routing differs from global loader, silent unloaded files, path-substring misclassification, implicit dependencies.
- **Validation:** compare discovered versus included server/client manifests.
- **Related:** `BEH-REALM-GAMEMODE`, `SYS-MODE-REGISTRY`.

## `SYS-MODE-REGISTRY` — Mode discovery, inheritance, persistence, and hook dispatch

- **Status:** `partial` — source matrix complete; runtime dispatch instrumentation pending.
- **Purpose:** Builds `MODE` tables, applies base inheritance, preserves `saved`, registers every function-valued member as a hook candidate, and persists mode chances.
- **Primary source/symbols:** gamemode loader; `zb.modes`, `zb.modesHooks`, temporary global `MODE`.
- **Dispatch:** selects main/current/`tdm`, invokes `func(modeTable, ...)`, forwards returns only when return #1 is non-nil.
- **Risks:** unsorted base/child registration, dot-defined argument shift, internal helper exposure, empty/inherited callbacks, disabled-mode hooks.
- **Validation:** registration order, realm parity, arguments/returns, hotload and external helper-name emissions.
- **Related:** `reference/MODE_FUNCTION_MATRIX.md`, `BEH-MODE-DISPATCH`, mode registry/table types.

## `SYS-ROUND-LIFECYCLE` — Server-authoritative round state, selection, and client synchronization

- **Status:** `partial` — source verified; integrated runtime cycle pending.
- **Purpose:** Runs `0 -> 1 -> 3 -> 0`, chooses modes, resets/equips players, synchronizes clients/admins, and emits lifecycle hooks.
- **Primary sources:** `sv_roundsystem.lua` blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client `cl_init.lua` blob `fa61811ef802529d54abe2cf1cc72a936ba15590`.
- **Risks:** active/legacy queue protocols, weak admin table validation, stale state/hook names, one-second cadence, broad cross-system calls, fake get-up spawn interaction.
- **Validation:** dedicated full cycle, late join, selection, admin end, CO-OP/changelevel, persistence and malformed transport.
- **Related:** round behavior/state/payload/queue types.

## `SYS-ORGANISM` — Physiological state, organ geometry, damage and replication

- **Status:** `partial` — ownership, state, order, damage and primary replication verified; all medical/item consumers and runtime budgets incomplete.
- **Purpose:** Simulates physiology and custom organ damage; drives movement, unconsciousness, fake/death state; synchronizes clients.
- **Sources:** Tier 0 `1b8a72186b295f3542dd90d92374d5985d7d6e62`; core `4830503722f005d27373047d8db5c58d4e217559`; damage `cce5ff506e9799eb3c1e104ea3146927a8936326`; client snapshot `c3c5db65d44125a2acf5df4be1b6fe13d891a86f`.
- **Ownership/order:** one mutable table may be shared by player/fake/death body; ~10 Hz module order is stamina, lungs, liver, blood, pain, metabolism, random events, pulse, then extension hooks.
- **Risks:** implicit schema, owner aliasing, order-dependent writes, monolithic/reentrant damage, model assumptions, overlapping unversioned transport and population cost.
- **Validation:** startup/schema, deterministic simulation, owner transfer, all damage/model/armor paths, packet size/privacy/performance.
- **Related:** `architecture/ORGANISM_SYSTEM.md`, organism behavior/state/snapshot types.

## `SYS-FAKE-RAGDOLL` — Living-body replacement, active physics control, death and get-up

- **Status:** `partial` — core lifecycle/control/transport/render verified; all weapon/vehicle/class integrations and performance incomplete.
- **Purpose:** Replaces the living body with a controllable custom ragdoll while preserving identity, organism, appearance, equipment, camera, NPC and vehicle behavior.
- **Sources:** server `0fa522db3f0562eaf1816d6452fa082aef81d2bb`; control `22c87ad4148716ff1173c104e7df943043b09ce5`; input `545f7b292c6bdb4610766700251cc741072a5e2e`; client `bdd7e6a215da568a2070bd9b33e29244f1970f90`; render `ddf5584d6ab0e51fdbb8fa802e87a40ec2c80ffe`.
- **Ownership:** server fields/maps, NWEntities, `Player Ragdoll` packet/index, client proxies and organism owner must converge on one body generation.
- **Risks:** no generation/transaction, respawn-based get-up/global override, undefined `net.ReadEntity2`, per-frame multi-body cost, skeleton/weapon/vehicle assumptions, stale constraints/timers and camera/render leaks.
- **Validation:** lifecycle failure injection, generation assertions, latency/PVS/late join, model/control/vehicle matrix and camera/render restoration.
- **Related:** `architecture/FAKE_RAGDOLL_SYSTEM.md`, fake behavior/state/payload/control types.

## `SYS-MOVEMENT` — Shared predicted movement, inertia, animation, and footsteps

- **Status:** `partial` — core movement directory verified; all weapon/mode hook consumers and runtime prediction evidence pending.
- **Purpose:** Calculates ordinary player speed, jump, input rewriting, inertia, carry reach, slip/dive-fake, animation and footsteps from organism, class, weapon, mass, stance and mode state.
- **Primary paths/sources:** `movement/sh_inertia.lua` blob `c7cd8553...`; `sh_movedata.lua` `f9a526...`; `sh_anims.lua` `aa303b...`; `sh_footsteps.lua` `63768f...`.
- **Realm:** shared server/client `SetupMove`; server/client prediction must converge despite realm-local timing and mutable state.
- **Authority:** ordinary movement remains active even when inertia is disabled; fake-body movement is separately owned by `SYS-FAKE-RAGDOLL`.
- **Dependencies:** organism limbs/pain/blood/O2/stamina, class Lua/NW modifiers, weapon stance/weight, carried entities, round/mode hooks, animation and sound.
- **Public surface:** `SetupMove/homigrad-inertia`, staged `HG_MovementCalc*`, `FinishMove`, landing/fake transitions, animation/footstep hooks, movement helper predicates and convars.
- **Known risks:** `SysTime` prediction divergence, replayed mutable player fields, modifier ownership overlap, nil/precedence/global-variable errors, hard model/physics/hands assumptions, fake/standing controller ambiguity, global Sandbox anti-duck mutation, no diagnostics/budget.
- **Validation:** per-command server/client traces, latency/replay, full modifier matrix, transition matrix, missing entities and population cost.
- **Related:** `architecture/MOVEMENT_SYSTEM.md`, `BEH-MOVEMENT-CALC`, movement context type, character integration graph.

## `SYS-PLAYER-CLASS` — Class registry, transition lifecycle, modifiers, and class-owned integrations

- **Status:** `partial` — registry/transport/lifecycle and sixteen concrete IDs verified; every global class hook/consumer incomplete.
- **Purpose:** Assigns class identity and dispatches class behavior that may change appearance, loadout, armor, organism, movement, fake state, NPC relationships, guilt, sounds, gestures and HUD.
- **Primary sources:** `playerclass/sh_tier_0.lua` blob `6415ce34...`; `sv_tier_0.lua` blob `d5f50151...`; `playerclass/classes/**`.
- **Registry/API:** `player.classList`, `player.RegClass`, `GetPlayerClass`, `SetPlayerClass`, `PlayerClassEvent`; case-sensitive mixed-case IDs.
- **Transport:** overloaded `playerclass` string + Lua table. Server broadcasts transitions, but also accepts the same payload C -> S with only `IsValid(ply)`; no repository legitimate client sender was found.
- **Runtime defect:** `class.nextThink` is stored on the shared class-definition table, so same-class players compete for one once-per-second Think slot.
- **Dependencies:** modes/rounds, appearance, inventory/equipment/armor, organism, movement, fake, NPC factions, weapons, phrases/gestures/footsteps/HUD.
- **Known risks:** arbitrary client class/data assignment, unbounded table, raw-server/normalized-client data divergence, no old-client `Off`, NW movement reset after `On`, no transaction/rollback, empty/incomplete `Off`, permanent/dynamic global hooks, NPC scans, case-sensitive IDs and partial death cleanup.
- **Validation:** transport fuzz/security, every class transition in all lifecycle states, failure rollback, multi-player same-class Think, resource/hook/relationship cleanup and realm parity.
- **Related:** `architecture/PLAYER_CLASS_SYSTEM.md`, class registry/payload/runtime types, class transition behavior.

## `SYS-CHARACTER-RUNTIME` — Cross-system player/body/class/movement/physiology ownership

- **Status:** `partial` — four-system authority graph verified; weapons, inventory, appearance, armor, NPC and vehicle boundaries remain incomplete.
- **Purpose:** Records the actual lifecycle authority across `SYS-ORGANISM`, `SYS-FAKE-RAGDOLL`, `SYS-MOVEMENT`, and `SYS-PLAYER-CLASS` so they are not refactored independently.
- **Authority problem:** class, body, organism, controller, equipment and presentation state are distributed across player fields, ragdolls, shared tables, NWVars, packets, hooks and modes without one generation/transaction owner.
- **Highest-impact defects:** arbitrary client class assignment; no body/organism generation; respawn-based get-up; shared class Think throttle; prediction-unsafe movement context; order-dependent physiology; overlapping fake transport; no transactional class/fake transitions; unbudgeted combined cadence.
- **Validation:** stable lifecycle generation tracing, transition matrix, one-owner/controller invariants, stale-callback detection and combined performance budgets.
- **Planned boundary:** per-player CharacterRuntime, explicit PhysiologyState, PhysicalBodyController, MovementContext, immutable ClassDefinition plus per-player ClassRuntime, and adapters for appearance/equipment/armor/weapons/NPCs/vehicles.
- **Related:** `architecture/CHARACTER_RUNTIME_INTEGRATION.md` and all four subsystem documents.
