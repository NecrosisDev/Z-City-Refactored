# Z-City Round and Spectator Networking

**Status:** Verified by static inspection of the current branch. Runtime packet capture is still required.

## Scope

This document records the currently verified network contracts used by the core round and spectator flow. It is intentionally limited to channels visible in:

- `gamemodes/zcity/gamemode/init.lua`;
- `gamemodes/zcity/gamemode/cl_init.lua`;
- `gamemodes/zcity/gamemode/libraries/sv_roundsystem.lua`.

It does not claim to inventory the full addon network surface.

## Authority model

The server is authoritative for:

- selected mode;
- numeric round state;
- round timing values;
- spectator admission;
- spectator target selection;
- spectator view mode;
- fade initiation.

The client currently sends spectator input requests and reconstructs client presentation from server messages plus replicated networked variables.

## Channel registry

| Channel | Direction | Payload | Sender | Receiver | Current purpose |
|---|---|---|---|---|---|
| `RoundInfo` | Server to client | mode string, signed 4-bit round state | round lifecycle and initial-spawn sync | client gamemode | Select local mode and invoke client round callbacks. |
| `updtime` | Server to all clients | three floats | `hg.UpdateRoundTime` | client gamemode | Replicate duration, start time, and begin time. |
| `FadeScreen` | Server to all clients | no explicit payload | `zb.AddFade` | receiver outside inspected core files | Initiate round-transition fade. |
| `ZB_ChooseSpecPly` | Client to server | signed 32-bit input constant | dead-player camera input | server gamemode | Request next target, previous target, or view-mode change. |
| `ZB_SpectatePlayer` | Server to one client | current entity, adjacent entity, signed 4-bit view mode | spectator request receiver | client gamemode | Update immediate spectator presentation state. |
| `ZB_SpecMode` | Client to server | boolean | spectator UI/input path | server gamemode | Join or leave spectator team. |

## `RoundInfo`

### Server writes

The server writes:

1. `mode.name` or `"hmcd"` as a string;
2. `zb.ROUND_STATE` as a signed 4-bit integer.

It sends this packet:

- when `zb:EndRound()` enters state `3`;
- when the end delay returns the system to state `0` and selects the next mode;
- to a joining player when `zb.CROUND` already exists.

### Client reads

The client:

1. reads the mode string;
2. emits `RoundInfoCalled` before assigning the new mode;
3. stops dynamic music when the mode changes;
4. assigns `zb.CROUND`;
5. reads the signed 4-bit state into `zb.ROUND_STATE`;
6. starts a local fade when state is `0`;
7. invokes the selected mode's client `EndRound()` when state is `3`;
8. invokes the selected mode's client `RoundStart()` when state is `1`.

### Contract risks

- The wire representation is numeric and inherits the documented state-`2` versus runtime-state-`3` inconsistency.
- The message has no protocol version.
- The packet identifies `mode.name`, while server authority also distinguishes `zb.CROUND`, `zb.CROUND_MAIN`, aliases, types, and submodes. The transmitted value may not preserve every semantic distinction.
- Client callbacks are invoked directly from network reception. A malformed local mode registry or partially loaded client can fail inside a transition receiver.
- Initial synchronization is conditional on `zb.CROUND`; there is no explicit complete snapshot acknowledgement.
- Mode and state are not coupled to timing values in one atomic packet.

## `updtime`

### Payload

`hg.UpdateRoundTime` updates server globals and broadcasts:

1. `zb.ROUND_TIME`;
2. `zb.ROUND_START`;
3. `zb.ROUND_BEGIN`.

All three values are written as floats.

### Contract risks

- Field names and units are implicit.
- There is no mode, state, sequence, or round-generation identifier.
- `RoundInfo` and `updtime` can be observed independently, allowing temporary mixed-generation client state.
- A late join relies on other synchronization paths to receive timing data; the inspected `PlayerInitialSpawn` hook sends `RoundInfo` and invokes `ply:SyncVars()`, but does not directly call `hg.UpdateRoundTime` for that player.
- Float timestamps depend on compatible server/client interpretation of engine time.

## Spectator input request

The dead client sends `ZB_ChooseSpecPly` once per detected key press:

- `IN_ATTACK` for the next target;
- `IN_ATTACK2` for the previous target;
- `IN_RELOAD` to cycle view mode.

The server rejects the request when the player is alive, reads a signed 32-bit integer, and compares only against the three expected constants.

### Server behavior

The server:

- obtains the current alive-player list;
- normalizes `ply.chosenspect` and `ply.viewmode`;
- changes the selected index or view mode;
- sends `ZB_SpectatePlayer` to the requesting player;
- updates `ply.chosenSpectEntity` and `ply.lastSpectTarget`.

### Contract risks

- The request schema accepts any 32-bit value and silently ignores unknown values rather than validating a small enum.
- There is no explicit rate limiter. The client attempts edge-triggering, but a modified client can send arbitrary request frequency.
- Selection is index-based against a newly generated alive-player list. Population changes can alter index meaning between requests.
- The response's second entity is adjacent selection context, but its semantic name is undocumented.
- View mode is encoded as a signed 4-bit integer even though only values `1` through `3` are expected.

## Spectator presentation response

The client receives `ZB_SpectatePlayer` and stores three globals:

- `spect`;
- `prevspect`;
- `viewmode`.

It then schedules an anonymous `timer.Simple(0.1)` callback that changes the local hull and may set noclip movement.

Separately, the server's `PlayerDeathThink` hook continuously publishes:

- `NWEntity("spect")`;
- `NWInt("viewmode")`.

The client camera reads these networked variables during `HG_CalcView`.

### Split-authority consequence

Immediate response state and persistent spectator state travel through two mechanisms:

1. a dedicated net message;
2. legacy networked variables updated during death think.

This creates duplicate state paths with different update cadence and failure behavior.

### Contract risks

- Client movement and hull changes occur in an uncancellable anonymous delayed callback.
- The server mutates spectator position and movement mode during `PlayerDeathThink`, while the client also mutates local movement and position for camera presentation.
- No sequence number prevents an older response or delayed callback from applying after respawn or target change.
- `PlayerDeathThink` can transmit the observed target's organism approximately once per second through another subsystem-specific channel, coupling spectator flow to medical replication.

## Spectator admission request

The client sends `ZB_SpecMode` with one boolean. The server computes:

`enable = not hook.Run("ZB_JoinSpectators", ply)`

When allowed:

- `true` kills a living player, assigns `TEAM_SPECTATOR`, and broadcasts a chat message;
- the other branch assigns hard-coded team `1` and broadcasts a chat message.

### Contract risks

- The boolean expresses intent but not expected current state, mode, or generation.
- No explicit rate limiting or transition lock is visible.
- Leaving spectators bypasses mode-specific admission and balancing authority.
- The hook's inverted return convention is implicit.
- The request can kill the player as a side effect of a UI/network action.

## Fade channel

`FadeScreen` is registered and broadcast with no explicit payload when `zb:EndRound()` executes. The core receiver was not found in the three inspected files and must be located before the channel is changed.

The absence of payload means presentation duration and semantics are determined elsewhere or are fixed by the receiver.

## Late-join consistency

The inspected initial-spawn hook sends `RoundInfo` only when `zb.CROUND` exists and then calls `ply:SyncVars()` when available.

A complete late-join state currently appears to be assembled from several independent mechanisms:

- `RoundInfo`;
- generic synced variables;
- timing state from `updtime` or another path;
- networked spectator variables;
- subsystem-specific synchronization such as organism replication.

This is not an atomic snapshot and has no visible completion marker.

## Verified design requirements

A replacement network layer must provide:

1. one declared owner per channel;
2. explicit direction and authorization;
3. versioned payload schemas;
4. bounded enums rather than raw input constants where practical;
5. rate policies for client-originated requests;
6. round and player generation identifiers for asynchronous state;
7. one authoritative spectator-state representation;
8. atomic or sequenced round snapshot delivery;
9. a late-join completion contract;
10. compatibility bridges for existing channel names during migration.

## Initial disposition against Trauma

- **Adopt:** explicit packet ownership metadata, schema metadata, and generation identifiers as requirements.
- **Adapt:** Trauma's broader synchronization concepts into a small versioned snapshot with subsystem contributors.
- **Rewrite:** client request handling, rate control, validation, and lifecycle ownership behind project APIs.
- **Reject:** adding more ad hoc channels to compensate for incomplete snapshots.
- **Keep temporarily:** current channel names and payloads until compatibility tests and receivers are fully inventoried.

## Required acceptance tests

1. Join during intermission, active round, and end delay.
2. Join before `zb.CROUND` is initialized.
3. Verify mode alias/type/submode identity on the client.
4. Deliver `RoundInfo` and `updtime` in both possible orders.
5. Change rounds while a client is loading mode files.
6. Spam each spectator request and verify bounded server work.
7. Send unknown spectator input values.
8. Change alive-player population between target requests.
9. Respawn before the delayed spectator callback fires.
10. Disconnect while a spectator request or response is pending.
11. Toggle spectator admission during every round state.
12. Verify team restoration for asymmetric and team-based modes.
13. Verify spectator state after map cleanup and Lua refresh.
14. Verify organism observation begins and stops with target/view changes.
15. Confirm legacy clients receive compatible packets during migration.

## Next verification work

- Locate every declaration, receiver, and sender for these six channels.
- Locate the `FadeScreen` client receiver.
- Trace `ply:SyncVars()` and enumerate which state it contributes.
- Determine whether late joiners receive current `updtime` through another hook.
- Inventory all round and spectator networked variables.
- Extend the registry to fake-ragdoll, organism, inventory, player-class, and mode-specific packets.
