# Type Catalog

Shared contracts are recorded only after confirming definitions and multiple consumers where applicable. Fields are classified as registration-required, consumer-assumed, optional, or unresolved rather than inferred into a complete schema.

## `TYPE-HG-BOOTSTRAP` — Global `hg` bootstrap namespace

- **Kind:** table/namespace.
- **Authority/owner:** `SYS-BOOTSTRAP-GLOBAL` initializes the table; loaded subsystems extend it.
- **Definition:** `lua/autorun/loader.lua`.
- **Verified fields:** version/repository metadata and `loaded`.
- **Realm:** independent server/client globals.
- **Invariant:** existing table reused; `loaded` false before main include and true before `HomigradRun`, except ixhl2rp early return.
- **Related:** global bootstrap/realm behavior.
- **Last verified:** blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`, 2026-07-12.

## `TYPE-MODE-REGISTRY` — `zb.modes` and `zb.modesHooks`

- **Kind:** registry.
- **Shape:** `zb.modes[modeName] -> TYPE-MODE-TABLE`; `zb.modesHooks[modeName][hookName] -> function`.
- **Authority:** `SYS-MODE-REGISTRY`; separate realm copies.
- **Invariants:** key is `MODE.name`; modes persist, hook table resets; dispatch fallback main/current/tdm.
- **Compatibility:** IDs/function names are public persistence/transport/hook identifiers.
- **Related:** mode registry/table/dispatch.
- **Last verified:** loader `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `TYPE-MODE-TABLE` — Registered mode definition

- **Kind:** extensible table/object.
- **Required:** `name`; empty table skipped.
- **Managed:** `saved`, inherited members; every function-valued member becomes a hook candidate.
- **Metadata/callbacks:** classified in `reference/MODE_FUNCTION_MATRIX.md`.
- **Realm:** separate server/client definitions; IDs/state networked, not table.
- **Compatibility:** new functions create global hook names; ID/function changes are breaking.
- **Related:** mode/round systems.

## `TYPE-ROUND-STATE` — Round lifecycle state

- **Kind:** signed four-bit integer.
- **Authority:** server, client mirror.
- **Values:** `0` pre-round, `1` active, `3` end; state-2 comments/listeners are stale.
- **Validation:** full cycle, late join, admin end, timeout, CO-OP/changelevel.

## `TYPE-ROUNDINFO-PAYLOAD` — Current round synchronization

- **Channel:** `RoundInfo`.
- **Fields:** string mode ID; int4 state.
- **Authority:** server.
- **Compatibility:** exact order/type/width and client registry ID required.

## `TYPE-ROUND-QUEUE` — Future and legacy queue contracts

- **Kind:** arrays plus packet families.
- **Fields:** active `zb.RoundList`, next mode, legacy `zb.QueuedModes`, force mode.
- **Trust:** admin checks exist, incoming tables lack strong bounds/schema/ID validation.
- **Compatibility:** active and legacy lists are separate server models.

## `TYPE-ORGANISM-STATE` — Authoritative physiological state table

- **Kind:** mutable extensible state table.
- **Authority:** server; one table may be shared by player, fake ragdoll and death ragdoll.
- **Identity:** `owner`, `ownerX`, registry membership.
- **Groups:** lifecycle, consciousness, cardiovascular, respiratory, pain/drugs, movement, organs/bones, limbs, wounds, metabolism, extensions and replication.
- **Lifecycle:** add, reset in place, transfer and ragdoll aliasing.
- **Risks:** no explicit schema/version/extension registry; duplicated defaults/transport/interpolation.
- **Related:** organism system/behavior/snapshot.
- **Last verified:** Tier 0 `1b8a...`, Tier 1 `483050...`, 2026-07-12.

## `TYPE-ORGANISM-SNAPSHOT` — `organism_send`

- **Kind:** unversioned Lua table plus booleans.
- **Fields:** table, force, spectator protection, more info, add/merge.
- **Variants:** owner, observer, developer whole table and partial merge.
- **Cadence:** about one second owner/player, one-to-three seconds observer/non-player, plus events.
- **Risks:** invalid owner ordering, implicit schema, PVS privacy, developer exposure and cost.
- **Related:** organism system/state and packet matrix.

## `TYPE-FAKE-RAGDOLL-STATE` — Player/body ownership and transition state

- **Kind:** distributed entity-reference state machine.
- **Authority:** server; client mirror through NWEntities, packet/index and proxies.
- **Server surfaces:** current/old/death ragdolls, ownership maps, NWEntities, vehicle/constraint/PVS state.
- **Client surfaces:** mirrored references, follow camera, ragdoll identity/organism, render indices/state.
- **Conceptual states:** standing, entering fake, fake, unconscious, getting up, dead; represented implicitly rather than by enum.
- **Invariant:** all references and organism owner identify one generation.
- **Risks:** no generation, packet/NW/proxy order, NULL ambiguity, stale old body, respawn get-up and EntIndex reuse.
- **Related:** fake system/behavior/payload.

## `TYPE-FAKE-RAGDOLL-PAYLOAD` — `Player Ragdoll`

- **Fields:** entity player; entity body/null.
- **Authority:** server fake lifecycle.
- **Client:** uses undefined/custom `net.ReadEntity2()` expecting body plus index; actual ownership primarily follows NWEntity proxies.
- **Risks:** no generation/transition type, helper dependency, PVS/entity-order races and duplicate/NULL ambiguity.

## `TYPE-FAKE-CONTROL-STATE` — Active-ragdoll physics/control data

- **Kind:** transient distributed control state.
- **Authority:** server frame loop sourced from input/view, organism, weapon, constraints and physics.
- **Fields:** power/time, hand constraints/cooldowns, stamina/choking/fire/weld state, player fake/jump/freemove/weapon state and organism movement fields.
- **Risks:** no fixed-step budget, frame coupling, shared temporaries, invalid physics/weapon assumptions and embedded class logic.

## `TYPE-MOVEMENT-CONTEXT` — Effective ordinary-player movement calculation

- **Kind:** implicit transient context assembled during shared `SetupMove`.
- **Authority:** server for game state, with client prediction executing a realm-local copy.
- **Inputs:** command buttons/view/move values; player velocity/ground/crouch/carry state; organism limbs/pain/blood/O2/stamina/consciousness; class Lua fields and NWInts; weapon stance/weight; armor/inventory/carried mass; mode/project hook modifiers; movement convars.
- **Outputs:** rewritten command movement, maximum speed, jump power, inertia/current-speed fields, carry reach/drop decisions, slip/dive/fake transitions and animation/footstep bookkeeping.
- **Current representation:** no table/schema exists; values are local variables plus mutable player/organism/class/weapon fields.
- **Invariants:** server/client modifier order and inputs must converge; only one ordinary/fake controller should be authoritative.
- **Risks:** realm-local `SysTime`, prediction replay of mutable fields, stage hooks, overlapping modifier mechanisms, nil/zero/extreme values and input reuse after mutation.
- **Compatibility:** future explicit context must preserve existing stage order and hook behavior until consumers migrate.
- **Validation:** per-command server/client trace with deterministic modifier breakdown and rollback tests.
- **Related:** `SYS-MOVEMENT`, `BEH-MOVEMENT-CALC`, character integration graph.

## `TYPE-CLASS-REGISTRY` — `player.classList`

- **Kind:** case-sensitive string -> shared class-definition table registry.
- **Authority:** shared source definitions; server owns assignment authority by intent.
- **Registration:** `player.RegClass(name)` returns existing or creates a table; duplicate files extend/overwrite the same object.
- **Verified IDs:** `default`, `Slugcat`, `police`, `terrorist`, `swat`, `nationalguard`, `groove`, `bloodz`, `gordon`, `Combine`, `Metrocop`, `Refugee`, `Rebel`, `commanderforces`, `headcrabzombie`, `furry`.
- **Definition fields:** lifecycle/event methods, capability flags, movement/combat multipliers and class-specific shared data.
- **Critical invariant:** class definitions should be immutable; current code stores shared runtime `nextThink` on them.
- **Risks:** mixed-case IDs, no duplicate-owner diagnostics, permanent global hooks outside definition lifecycle, arbitrary methods with unresolved callers.
- **Validation:** realm registry parity, duplicate ownership, full method/global-hook consumer map and same-class multi-player tests.
- **Related:** `SYS-PLAYER-CLASS`, `TYPE-CLASS-RUNTIME`, class transition behavior.

## `TYPE-CLASS-RUNTIME` — Per-player class assignment and effects

- **Kind:** distributed runtime state currently spread across player fields, NetVars/NWInts, organism, equipment, appearance, hooks and world relationships.
- **Identity:** `PlayerClassName` Lua field and NetVar; `GetPlayerClass()` falls back to `default`.
- **Transition:** old `Off`, write ID, broadcast payload, new `On`, reset movement NWInts, emit `PlayerClass`.
- **Effects:** appearance/model/bodygroups/color/name/role; equipment/armor/inventory; organism/movement/fake; NPC relationships; guilt/phrases/gestures/footsteps/HUD.
- **Risks:** no transaction/rollback, client does not call old `Off`, server/client data divergence, incomplete cleanup, EntIndex-keyed hooks and class side effects surviving death/exit.
- **Planned compatibility:** separate immutable definition and per-player runtime state with lifecycle-owned resources.
- **Related:** `SYS-PLAYER-CLASS`, `TYPE-PLAYERCLASS-PAYLOAD`, character integration graph.

## `TYPE-PLAYERCLASS-PAYLOAD` — Overloaded `playerclass` transition message

- **Kind:** bidirectional ordered payload.
- **Fields:** string class ID (`"nil"` clears); Lua table data.
- **Server -> clients:** authoritative transition broadcast; client sets ID, calls new `On(data)`, emits `PlayerClass`; old client class `Off` is not called.
- **Client -> server:** same payload is accepted and passed to `SetPlayerClass` with only sender validity check; no legitimate repository sender was found.
- **Trust defect:** any client can request any registered class and arbitrary table data unless an external layer blocks the channel.
- **Schema risks:** no raw/table depth/count/type/version bounds; server `On` receives original raw args while client receives normalized table.
- **Compatibility:** server-only transition authority and versioned/bounded intent payload are required before deployment.
- **Validation:** unauthorized/fuzz/replay tests, mode/role/phase checks, realm effect parity and rollback.
- **Related:** class registry/runtime, packet matrix and class transition behavior.
