# Type Catalog

Shared contracts are recorded only after confirming definitions and multiple consumers where applicable. Fields are classified as registration-required, consumer-assumed, optional, or unresolved rather than inferred into a complete schema.

## `TYPE-HG-BOOTSTRAP` — Global `hg` bootstrap namespace

- **Kind:** table/namespace.
- **Authority/owner:** `SYS-BOOTSTRAP-GLOBAL` initializes the table; loaded subsystems extend it.
- **Definition paths:** `lua/autorun/loader.lua`.
- **Verified bootstrap fields:** `Version`, repository owner/name, `loaded`.
- **Realm/transport:** independent server/client globals.
- **Invariants:** existing table reused; `loaded` false before main include and true before `HomigradRun`, except ixhl2rp early return.
- **Compatibility/validation:** additive names must avoid collisions; runtime snapshots at bootstrap phases.
- **Related:** `SYS-BOOTSTRAP-GLOBAL`, `BEH-REALM-GLOBAL`.
- **Last verified:** blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`, 2026-07-12.

## `TYPE-MODE-REGISTRY` — `zb.modes` and `zb.modesHooks`

- **Kind:** registry.
- **Authority/owner:** `SYS-MODE-REGISTRY`.
- **Shape:** `zb.modes[modeName] -> TYPE-MODE-TABLE`; `zb.modesHooks[modeName][hookName] -> function`.
- **Realm:** separate server/client registries.
- **Invariants:** key is `MODE.name`; modes persist across hotload, hook table resets; dispatch fallback main/current/tdm.
- **Compatibility:** IDs and function names are public identifiers used by persistence, packets, UI and hooks.
- **Validation:** compare realm key/callback sets after startup/hotload.
- **Related:** `SYS-MODE-REGISTRY`, `TYPE-MODE-TABLE`, `BEH-MODE-DISPATCH`.
- **Last verified:** loader blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `TYPE-MODE-TABLE` — Registered mode definition

- **Kind:** extensible table/object contract.
- **Authority/owner:** mode source populates temporary `MODE`; registry finalizes/stores it.
- **Registration-required:** `name`; empty table skipped.
- **Registry-managed:** `saved`; inherited tables; every function-valued member is hook-dispatched.
- **Verified metadata/callbacks:** IDs, base, display/description, Types/Type, chances/map size, timing/freezing and lifecycle/data/helper functions classified in `reference/MODE_FUNCTION_MATRIX.md`.
- **Realm:** separate tables; mode ID/state and selected data networked, not table.
- **Compatibility:** function additions create global hook names; renames/removals break dispatch/persistence/transport.
- **Validation:** realm schema parity, bases, duplicate names, collisions and mutable aliases.
- **Related:** mode/round systems and behavior.
- **Last verified:** loader/round/client blobs in matrix, 2026-07-12.

## `TYPE-ROUND-STATE` — Round lifecycle state identifier

- **Kind:** signed four-bit integer/state machine.
- **Authority:** server; client mirror through `RoundInfo`.
- **Values:** `0` pre-round, `1` active, `3` end.
- **Legacy claim:** comments/listeners using `2` are stale.
- **Compatibility:** numeric reassignment/addition is breaking.
- **Validation:** full cycle, late join, admin end, timeout and CO-OP/changelevel.
- **Related:** `SYS-ROUND-LIFECYCLE`, `TYPE-ROUNDINFO-PAYLOAD`.
- **Last verified:** server `324491...`, client `fa6181...`, 2026-07-12.

## `TYPE-ROUNDINFO-PAYLOAD` — Current round synchronization

- **Kind:** ordered network payload.
- **Channel:** `RoundInfo`.
- **Fields:** `string modeName`; `int4 roundState`.
- **Authority:** server; client stores state and invokes local transitions.
- **Compatibility:** field order/type/width and client mode ID must match.
- **Validation:** packet capture and unknown mode/state handling.
- **Related:** round system/behavior/types.
- **Last verified:** server/client round blobs, 2026-07-12.

## `TYPE-ROUND-QUEUE` — Future and legacy queue contracts

- **Kind:** arrays plus network payload families.
- **Authority:** server.
- **Fields:** active `zb.RoundList`; next mode; legacy `zb.QueuedModes`; force-mode convar.
- **Transport:** active `ZB_SendRoundList`/`ZB_UpdateRoundList`; overlapping legacy admin queue family.
- **Invariants:** IDs should resolve; active and legacy lists are distinct models.
- **Trust:** admin checks exist; incoming tables lack strong bounds/schema/ID validation.
- **Validation:** fuzz, permission, deterministic order and synchronized migration.
- **Related:** round selection and packet matrix.
- **Last verified:** round blob `324491...`, 2026-07-12.

## `TYPE-ORGANISM-STATE` — Authoritative physiological state table

- **Kind:** mutable extensible table/state machine.
- **Authority:** server `SYS-ORGANISM`; one table may be shared by player, fake ragdoll and death ragdoll.
- **Required identity:** `owner`, `ownerX`; registry through `hg.organism.list`.
- **State groups:** lifecycle; consciousness/control; cardiovascular; respiratory; pain/drugs; movement/energy; bones/organs; limbs; wounds; metabolism/environment; mode/class extensions; replication timing.
- **Nested structures:** stamina, O2, lungs, wounds, damage stack, lodged entities and optional extensions.
- **Lifecycle:** Add, clear in place, owner transfer and ragdoll aliasing.
- **Invariants:** one authoritative owner generation; required fields before 10 Hz tick; client copies non-authoritative.
- **Compatibility issue:** no explicit schema/version/extension registry; duplicated across reset/replication/interpolation/consumers.
- **Validation:** runtime schema and owner-transition assertions.
- **Related:** `SYS-ORGANISM`, organism behavior/snapshot.
- **Last verified:** Tier 0 `1b8a...`, Tier 1 `483050...`, 2026-07-12.

## `TYPE-ORGANISM-SNAPSHOT` — `organism_send`

- **Kind:** unversioned Lua table plus ordered branch booleans.
- **Authority:** server; client reader `cl_statistics.lua`.
- **Fields:** table; force; spectator protection; more info; add/merge.
- **Variants:** owner whitelist, observer whitelist, developer whole table and partial merge.
- **Cadence:** about one second owner/player and one-to-three seconds observer/non-player, plus event sends.
- **Client behavior:** replaces/merges old/new state and mirrors to fake ragdoll.
- **Risks:** invalid owner ordering, implicit schema, PVS privacy, developer exposure and population cost.
- **Compatibility:** future versioned public/private deltas required.
- **Validation:** capture every branch, invalid shapes, cadence/size/privacy/replay.
- **Related:** organism system/state and packet matrix.
- **Last verified:** server `483050...`, client `c3c5db...`, 2026-07-12.

## `TYPE-FAKE-RAGDOLL-STATE` — Player/body ownership and transition state

- **Kind:** distributed entity-reference state machine.
- **Authority:** server `SYS-FAKE-RAGDOLL`; clients reconstruct a mirror through NWEntities, custom packet/index and proxies.
- **Server surfaces:** `ply.FakeRagdoll`, `FakeRagdollOld`, `OldRagdoll`, `RagdollDeath`; `hg.ragdollFake[player]`; `ragdoll.ply`; NWEntities `FakeRagdoll`, `FakeRagdollOld`, `RagdollDeath`, ragdoll NWEntity `ply`; PVS/vehicle/constraint maps.
- **Client surfaces:** mirrored player fields, camera `follow`, ragdoll `ply`/`organism`, `ragdoll_index`/`prevragdoll_index`, `hg.ragdolls`, render/camera transition state.
- **Conceptual states:** standing, entering fake, active fake, unconscious fake, getting up, dead/death-ragdoll. Current code represents these implicitly through entity validity, organism booleans, timers and transient globals rather than one enum.
- **Ownership invariant:** all references and organism owner must identify one body generation; the player and current body may share one organism table.
- **Transition writers:** `hg.Fake`, `hg.FakeUp`, death hooks, ragdoll removal, disconnect, vehicle hooks, organism fake/unconscious logic and client NWVar proxies.
- **Known conflicts:** no generation/token; packet/NW/proxy order; NULL versus removed/adopted/death body ambiguity; old body aliases; respawn-based get-up; timer/entity-index reuse.
- **Compatibility:** changing a field/hook/NWEntity requires atomically migrating server physics, organism, camera, render, spectator, weapons, vehicles and death behavior.
- **Validation:** state-machine trace with generation assertions across every lifecycle/failure/latency path.
- **Related:** `SYS-FAKE-RAGDOLL`, `BEH-FAKE-RAGDOLL-LIFECYCLE`, `TYPE-FAKE-RAGDOLL-PAYLOAD`.
- **Last verified:** server Tier 0 `0fa522db3f0562eaf1816d6452fa082aef81d2bb`; client `bdd7e6a215da568a2070bd9b33e29244f1970f90`; 2026-07-12.

## `TYPE-FAKE-RAGDOLL-PAYLOAD` — `Player Ragdoll`

- **Kind:** ordered network payload with external reader dependency.
- **Authority:** server fake lifecycle.
- **Ordered fields:** `entity player`; `entity ragdollOrNull`.
- **Writers:** fake enter/adoption/get-up/death/removal helpers broadcast through `NET_Fake`, `NET_Fake2` and `NET_Up`.
- **Client reader:** calls `net.ReadEntity()` then custom/undefined `net.ReadEntity2()` and expects it to return both entity and numeric index; only the index is stored.
- **Primary ownership transport:** NWEntity proxies for `FakeRagdoll`/`RagdollDeath` perform actual client ownership/render/camera changes, making this packet an overlapping index/presentation path.
- **Risks:** no sequence/generation/transition type; undefined helper behavior; order relative to entity creation/PVS/NW updates; duplicate sends; NULL ambiguity.
- **Compatibility:** either formalize `ReadEntity2` and version/generate transitions or remove packet only after proving proxies/indices cover all consumers.
- **Validation:** bit/return behavior, latency/reorder/late join/PVS, duplicate/NULL/adopted/death/get-up transitions.
- **Related:** fake state, system and packet matrix.
- **Last verified:** server `0fa522db3f0562eaf1816d6452fa082aef81d2bb`; client `bdd7e6a215da568a2070bd9b33e29244f1970f90`; 2026-07-12.

## `TYPE-FAKE-CONTROL-STATE` — Active-ragdoll physics/control data

- **Kind:** transient distributed control state.
- **Authority:** server Think loop, sourced from player buttons/view, organism, weapon, constraints and ragdoll physics.
- **Representative fields:** ragdoll `power`, `dtime`, hand constraints/cooldowns, stamina modifiers, choking/fire/weld state, bullseye; player last-fake/jump/freemove/weapon state; organism movement/pain/O2/blood/consciousness/limbs.
- **Execution:** every server frame for every active fake; drives multiple physical bodies through shadow control and direct forces.
- **Invariants:** supported bone/physics map, valid organism schema, valid active weapon interface and cleanup of constraints/callbacks.
- **Risks:** no fixed-step budget; frame-rate coupling; shared temporary tables; invalid physics/weapon assumptions; class/gameplay logic embedded in generic controls.
- **Compatibility:** weapon/class integrations must use explicit interfaces before control separation.
- **Validation:** deterministic input fixtures, frame/time-scale variance and population performance.
- **Related:** fake system/behavior, organism state and future movement/class contracts.
- **Last verified:** control blob `22c87ad4148716ff1173c104e7df943043b09ce5`; 2026-07-12.
