# Type Catalog

Shared contracts are recorded only after confirming definitions and multiple consumers where applicable. Fields are classified as registration-required, consumer-assumed, optional, or unresolved rather than inferred into a complete schema.

## `TYPE-HG-BOOTSTRAP` — Global `hg` bootstrap namespace

- **Kind:** table/namespace.
- **Authority/owner:** `SYS-BOOTSTRAP-GLOBAL` initializes the table; loaded subsystems extend it.
- **Definition paths:** `lua/autorun/loader.lua` initializes `hg = hg or {}` and writes bootstrap metadata/state.
- **Verified bootstrap fields:** `Version: string`; `GitHub_ReposOwner: string`; `GitHub_ReposName: string`; `loaded: boolean` during/after the main load path.
- **Consumers:** All addon/gamemode systems using the global `hg` namespace; complete consumer inventory pending.
- **Realm/transport:** Independent server/client global tables; no automatic table replication. Individual fields/services may network separately.
- **Invariants:** Existing table is reused; `loaded` is set false before the main recursive include and true before `HomigradRun`, except the `ixhl2rp` early-return path leaves it false.
- **Compatibility rules:** Additive names must avoid collisions; code must not assume the entire namespace exists before `HomigradRun`; realm-specific members require guards.
- **Validation:** Runtime snapshot immediately before loader, during includes, at `HomigradRun`, and at `InitPostEntity` on server/client.
- **Related:** `SYS-BOOTSTRAP-GLOBAL`, `BEH-REALM-GLOBAL`.
- **Last verified:** `lua/autorun/loader.lua` blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`, 2026-07-12.

## `TYPE-MODE-REGISTRY` — `zb.modes` and `zb.modesHooks`

- **Kind:** registry.
- **Authority/owner:** `SYS-MODE-REGISTRY`.
- **Definition paths:** `gamemodes/zcity/gamemode/loader.lua` initializes and writes both registries.
- **Shape:** `zb.modes[modeName] -> TYPE-MODE-TABLE`; `zb.modesHooks[modeName][hookName] -> function`.
- **Consumers:** Mode loader/dispatcher, server round resolver/selection, client `CurrentRound`, UI/admin mode inventory, and all mode-dependent systems.
- **Realm/transport:** Separate server/client registries assembled from realm-routed source; registry tables are not directly networked.
- **Invariants:** Mode key is `MODE.name`; `zb.modes` survives loader hotloads when already present; `zb.modesHooks` is reset each loader execution; selected mode lookup falls back through `zb.CROUND_MAIN`, `zb.CROUND`, then `tdm` in dispatch.
- **Compatibility rules:** Mode names and hook/member names are public identifiers; renaming breaks saved chances, round lists, commands, net/UI references, and dispatch. Server/client mode registration must remain compatible for `RoundInfo` names.
- **Validation:** Compare server/client key sets and selected function sets after startup and hotload; report missing/extra modes and hooks.
- **Related:** `SYS-MODE-REGISTRY`, `BEH-MODE-DISPATCH`, `TYPE-MODE-TABLE`.
- **Last verified:** `loader.lua` blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `TYPE-MODE-TABLE` — Registered mode definition

- **Kind:** extensible table/object contract.
- **Authority/owner:** Each mode source populates temporary global `MODE`; `SYS-MODE-REGISTRY` finalizes and stores it.
- **Definition paths:** all `gamemodes/zcity/gamemode/modes/**`; registration/consumers traced in `loader.lua`, `sv_roundsystem.lua`, and `cl_init.lua`.
- **Registration-required:** `name: string` is used as the registry key and network-visible current mode identifier. A completely empty table is skipped.
- **Registry-managed:** `saved: table` is preserved across hotload and reset during round preparation; inherited tables may be copied; every function-valued member is added to mode-hook dispatch.
- **Verified optional metadata:** `base: mode name`; `PrintName`; `Description`; `Types: table`; `Type`; `Chance`; `ForBigMaps`; `SubModes`; timing values such as `start_time`/`end_time`; `shouldfreeze`.
- **Verified optional callbacks:** `AfterBaseInheritance`, `SetupChances`, `CanLaunch`, `ChanceFunction`, `RoundStart`, `RoundStartPost`, `RoundThink`, `ShouldRoundEnd`, `BoringRoundFunction`, `EndRound`, `Intermission`, `GiveEquipment`, `DontKillPlayer`. The complete known function surface is now classified in `reference/MODE_FUNCTION_MATRIX.md`.
- **Realm/transport:** Separate tables execute in their routed realms; only the mode name/state and selected supporting data are networked, not the table itself.
- **Invariants:** Base mode must already be registered before inheritance; server/client definitions for a mode name must be compatible; function names participate in global hook dispatch even when intended as helpers.
- **Compatibility rules:** Additive data fields are generally safe if names do not collide with hook names; function additions can create new hook registrations; renaming/removing lifecycle functions or mode IDs is breaking; nested inherited tables require copy/ownership review.
- **Validation:** Compare registry schemas, absent consumer-assumed callbacks, unresolved bases, server/client differences, duplicate names, function/hook collisions and mutable table aliasing.
- **Related:** `SYS-MODE-REGISTRY`, `SYS-ROUND-LIFECYCLE`, `BEH-MODE-DISPATCH`, `BEH-MODE-SELECTION`.
- **Last verified:** loader blob `b1754dff2d53012a05cb109f26b75eae118b14ce`; round blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; 2026-07-12.

## `TYPE-ROUND-STATE` — Round lifecycle state identifier

- **Kind:** integer identifier/state machine.
- **Authority/owner:** Server `SYS-ROUND-LIFECYCLE`; clients mirror it.
- **Definition paths:** server `sv_roundsystem.lua`; client `cl_init.lua`.
- **Verified values:** `0 = pre-round/intermission`, `1 = active round`, `3 = end-round period`.
- **Transport:** `RoundInfo` sends the value with `net.WriteInt(value, 4)`; client reads `net.ReadInt(4)` into `zb.ROUND_STATE`.
- **Consumers:** Server lifecycle gates, chat-listening rule, mode callbacks, client fade/presentation and client-side mode callbacks.
- **Invariants:** Server is authoritative; state transitions traced are `0 -> 1 -> 3 -> 0`; clients must not infer authority from local callbacks.
- **Legacy claim:** Client comment states `2 = endround`; executable source uses `3` on both server and client branches.
- **Compatibility rules:** Reassigning numeric values is network- and behavior-breaking; adding states requires auditing all equality checks, payload width/sign semantics, hooks, UI, and mode code.
- **Validation:** Record server transitions and every client-received payload through a full cycle, late join, admin end, timeout, and changelevel/coop path.
- **Related:** `SYS-ROUND-LIFECYCLE`, `BEH-ROUND-CYCLE`, `TYPE-ROUNDINFO-PAYLOAD`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; 2026-07-12.

## `TYPE-ROUNDINFO-PAYLOAD` — Current round synchronization message

- **Kind:** ordered network payload.
- **Authority/owner:** Server `SYS-ROUND-LIFECYCLE` writes; client round receiver reads.
- **Definition paths:** server `sv_roundsystem.lua`; client `cl_init.lua`.
- **Channel:** `RoundInfo` registered server-side with `util.AddNetworkString`.
- **Ordered fields:** `1. modeName: string`; `2. roundState: signed 4-bit integer`.
- **Send conditions:** round start, round end, end-to-pre-round transition, and `PlayerInitialSpawn` when `zb.CROUND` exists.
- **Client effects:** emits `RoundInfoCalled`, updates local mode/state, applies fade and invokes local mode lifecycle callbacks.
- **Invariants:** Field order and bit width must match exactly; mode names must exist clientside; server remains authoritative.
- **Compatibility rules:** Any field insertion/reordering/type/width change is breaking unless both sender and receiver migrate atomically.
- **Validation:** Packet capture/log wrapper comparing writes/reads, late join state, unknown mode name, each valid state and repeated broadcasts.
- **Related:** `SYS-ROUND-LIFECYCLE`, `BEH-ROUND-CYCLE`, `TYPE-MODE-REGISTRY`, `TYPE-ROUND-STATE`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; 2026-07-12.

## `TYPE-ROUND-QUEUE` — Future mode list and forced-mode admin contract

- **Kind:** registry/list plus network payload family.
- **Authority/owner:** Server `SYS-ROUND-LIFECYCLE`.
- **Definition paths:** `sv_roundsystem.lua`; client/admin consumers partially traced.
- **Server fields:** `zb.RoundList: array<string>`; `zb.nextround: string|nil`; `zb.QueuedModes: array<string>`; `zb_forcemode: string convar` using `random` as disabled state.
- **Verified messages:** server-to-admin `ZB_SendRoundList` writes table, next-round string, force-mode string; client-to-server `ZB_UpdateRoundList` reads table then boolean; overlapping legacy queue protocols remain.
- **Invariants:** Entries should resolve through mode/submode registries; non-empty replacement removes its first entry into `zb.nextround`; empty input rerolls; force mode overrides random selection.
- **Trust/validation:** Admin checks exist, but client tables lack shape/length/ID/duplicate bounds and overlapping receivers make effective behavior runtime-dependent.
- **Compatibility rules:** Validate/bound tables, preserve mode IDs, and migrate every admin client atomically.
- **Validation:** Fuzz payloads, verify unauthorized rejection, deterministic order, force reset and synchronization.
- **Related:** `SYS-ROUND-LIFECYCLE`, `BEH-MODE-SELECTION`, `TYPE-MODE-REGISTRY`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`, 2026-07-12.

## `TYPE-ORGANISM-STATE` — Authoritative physiological state table

- **Kind:** mutable extensible table/state machine.
- **Authority/owner:** Server `SYS-ORGANISM`; one table may be shared by player, fake ragdoll and death ragdoll.
- **Definition paths:** `organism/tier_0/sv_tier_0.lua` creates identity fields; `tier_1/sv_organism.lua` resets canonical fields; modules, damage, modes, classes, weapons and medical systems extend/mutate it.
- **Required identity:** `owner: Entity`, `ownerX: Entity`; registry ownership through `hg.organism.list[entity]`.
- **Verified state groups:** lifecycle; consciousness/control; cardiovascular; respiratory; pain/drugs; movement/energy; bones/organs; limbs/dislocations/amputations; wounds; environment/metabolism; mode/class extensions; replication timing.
- **Nested structures:** stamina table; O2 table; left/right lung tables; wound/arterial-wound arrays; damage stack; lodged entities; optional mode/integration tables.
- **Lifecycle:** `Add` creates/attaches; `Org Clear` resets in place; `Org Transfer` changes owner; fake/death ragdolls can alias the same table; entity removal clears registry entry.
- **Invariants:** exactly one authoritative owner generation should exist; `owner.organism` must reference the table; required module fields must exist before the 10 Hz tick; client copies are non-authoritative.
- **Current compatibility issue:** There is no explicit schema/version/extension registry. Fields are duplicated across reset, replication, client interpolation and external consumers.
- **Validation:** Generate runtime schemas after clear and during each owner transition; reject missing/wrong-type fields; compare mode/class extensions; test aliasing and delayed callbacks.
- **Related:** `SYS-ORGANISM`, `BEH-ORGANISM-LIFECYCLE`, `TYPE-ORGANISM-SNAPSHOT`.
- **Last verified:** Tier 0 blob `1b8a72186b295f3542dd90d92374d5985d7d6e62`; Tier 1 blob `4830503722f005d27373047d8db5c58d4e217559`; 2026-07-12.

## `TYPE-ORGANISM-SNAPSHOT` — `organism_send` replication payload

- **Kind:** ordered header plus unversioned Lua-table payload.
- **Authority/owner:** Server `SYS-ORGANISM`; client receiver in `tier_1/cl_statistics.lua`.
- **Channel:** `organism_send`.
- **Ordered fields:** `1. table snapshot`; `2. bool force`; `3. bool spectatorProtection`; `4. bool moreInfo`; `5. bool add/merge`.
- **Snapshot variants:** owner/full-field whitelist; PVS/bare whitelist; developer-mode entire organism table; immediate partial merge tables.
- **Send cadence:** generally one second for living players/owner snapshots and one to three seconds for nearby observer snapshots, plus damage/event-triggered sends.
- **Client behavior:** reads owner from table, creates/merges old/new state, optionally replaces on `force`, and mirrors copies to fake ragdoll for interpolation/presentation.
- **Trust/privacy:** Server authoritative but table shape/version is implicit; PVS observers receive sensitive physiology fields; developer mode can expose arbitrary extension data.
- **Known defects:** client method call on owner before `IsValid`; copies existing state before confirming it exists; Lua-table cost scales with organism count; partial/full semantics are represented by booleans rather than explicit message variants; wounds also travel through NetVars.
- **Compatibility rules:** Any field/type/branch change can break interpolation/UI; future migration requires versioned payload and public/private field sets.
- **Validation:** Packet capture for every branch, invalid owner/table tests, size/cadence population tests, PVS/spectator exposure and compatibility replay.
- **Related:** `SYS-ORGANISM`, `TYPE-ORGANISM-STATE`, `reference/PACKET_MATRIX.md`.
- **Last verified:** server blob `4830503722f005d27373047d8db5c58d4e217559`; client blob `c3c5db65d44125a2acf5df4be1b6fe13d891a86f`; 2026-07-12.
