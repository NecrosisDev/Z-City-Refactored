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
- **Definition paths:** all `gamemodes/zcity/gamemode/modes/**`; registration/consumers traced in `loader.lua`, `sv_roundsystem.lua`, and `cl_init.lua`. Complete per-mode inventory pending.
- **Registration-required:** `name: string` is used as the registry key and network-visible current mode identifier. A completely empty table is skipped.
- **Registry-managed:** `saved: table` is preserved across hotload and reset during round preparation; inherited tables may be copied; every function-valued member is added to mode-hook dispatch.
- **Verified optional metadata:** `base: mode name`; `PrintName`; `Description`; `Types: table`; `Type`; `Chance`; `ForBigMaps`; `SubModes`; timing values such as `start_time`/`end_time`; `shouldfreeze`.
- **Verified optional callbacks:** `AfterBaseInheritance`, `SetupChances`, `CanLaunch`, `ChanceFunction`, `RoundStart`, `RoundStartPost`, `RoundThink`, `ShouldRoundEnd`, `BoringRoundFunction`, `EndRound`, `Intermission`, `GiveEquipment`, `DontKillPlayer`. Some call sites assume selected modes implement specific lifecycle methods; defaults/inheritance must be traced before classifying them as universally required.
- **Realm/transport:** Separate tables execute in their routed realms; only the mode name/state and selected supporting data are networked, not the table itself.
- **Invariants:** Base mode must already be registered before inheritance; server/client definitions for a mode name must be compatible; function names participate in global hook dispatch even when intended as helpers.
- **Compatibility rules:** Additive data fields are generally safe if names do not collide with hook names; function additions can create new hook registrations; renaming/removing lifecycle functions or mode IDs is breaking; nested inherited tables require copy/ownership review.
- **Validation:** Generate a per-mode schema matrix from all sources and consumers, detect absent consumer-assumed callbacks, unresolved bases, server/client differences, duplicate names, function/hook collisions, and mutable table aliasing.
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
- **Ordered fields:** `1. modeName: string` written from `mode.name or "hmcd"`; `2. roundState: signed 4-bit integer` from `TYPE-ROUND-STATE`.
- **Send conditions:** round start, round end, end-to-pre-round transition, and `PlayerInitialSpawn` when `zb.CROUND` exists.
- **Client effects:** emits `hook.Run("RoundInfoCalled", modeName)` before assigning mode; stops dynamic music when mode changes; stores `zb.CROUND` and `zb.ROUND_STATE`; applies fade for `0`; invokes local mode `RoundStart` for `1` or `EndRound` for `3` when the mode exists.
- **Invariants:** Field order and bit width must match exactly; mode names must exist in the client `TYPE-MODE-REGISTRY`; server remains authoritative.
- **Compatibility rules:** Any field insertion/reordering/type/width change is breaking unless both sender and receiver migrate atomically; unknown mode handling must remain safe.
- **Validation:** Packet capture/log wrapper comparing writes/reads, late-join state, unknown mode name, each valid state, and repeated identical broadcasts.
- **Related:** `SYS-ROUND-LIFECYCLE`, `BEH-ROUND-CYCLE`, `TYPE-MODE-REGISTRY`, `TYPE-ROUND-STATE`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`; client blob `fa61811ef802529d54abe2cf1cc72a936ba15590`; 2026-07-12.

## `TYPE-ROUND-QUEUE` — Future mode list and forced-mode admin contract

- **Kind:** registry/list plus network payload family.
- **Authority/owner:** Server `SYS-ROUND-LIFECYCLE`.
- **Definition paths:** `sv_roundsystem.lua`; client/admin consumers not yet fully traced.
- **Server fields:** `zb.RoundList: array<string>`; `zb.nextround: string|nil`; `zb.QueuedModes: array<string>`; `zb_forcemode: string convar` using `random` as disabled state.
- **Verified messages:** server-to-admin `ZB_SendRoundList` writes table, next-round string, force-mode string; client-to-server `ZB_UpdateRoundList` reads table then boolean; request/notification and additional queue/mode admin messages are registered/consumed in the round system.
- **Invariants:** List entries should resolve through the mode registry or submode mapping; setting a non-empty new list removes its first entry into `zb.nextround`; empty input rerolls; forced mode overrides random choice.
- **Trust/validation:** Receivers require `ply:IsAdmin`, but the traced update path does not validate table shape/length/IDs and reads `forceUpdate` without using it.
- **Compatibility rules:** Validate and bound all client-supplied tables before future expansion; preserve mode IDs across persistence/UI; migrate all admin clients with payload changes.
- **Validation:** Trace client definitions, fuzz authorized payload shape/size/unknown IDs, verify unauthorized rejection, deterministic queue order, force reset, and synchronization to all admins.
- **Related:** `SYS-ROUND-LIFECYCLE`, `BEH-MODE-SELECTION`, `TYPE-MODE-REGISTRY`.
- **Last verified:** server blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`, 2026-07-12.