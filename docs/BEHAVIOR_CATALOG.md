# Behavior Catalog

Externally observable behavior is recorded independently from implementation structure. `Verified` means executable source establishes the behavior; entries remain `partial` when runtime evidence or integration coverage is still missing.

## `BEH-REALM-GLOBAL` — Global addon files are routed by exact prefix/suffix with shared fallback

- **Status:** `partial`.
- **Trigger/result:** Autorun routes exact realm prefixes/suffixes; unmarked files are shared; current-directory files precede children.
- **Edge cases:** unsorted enumeration, marker limits, ixhl2rp early exit and client delivery of unmarked files.
- **Regression:** log include path/realm/order on dedicated server/client.
- **Related:** global bootstrap system/type.

## `BEH-REALM-GAMEMODE` — Gamemode files use substring routing and child-first recursion

- **Status:** `partial`.
- **Trigger/result:** child directories precede files; substring realm matching; unmarked files ignored.
- **Edge cases:** path misclassification, silent unloaded files, unsorted order and mismatch with global loader.
- **Regression:** compare discovered and included realm manifests.
- **Related:** gamemode bootstrap.

## `BEH-MODE-DISPATCH` — Current mode functions are dispatched through shared hook callbacks

- **Status:** `partial` — known source matrix complete; runtime external emissions pending.
- **Trigger/result:** every function-valued mode member becomes a hook candidate; selected mode receives the mode table first.
- **Edge cases:** internal helpers, dot-function argument shift, empty/inherited callbacks and disabled-mode surfaces.
- **Regression:** realm/mode/arguments/returns/fallback/inheritance/hotload and accidental helper calls.
- **Related:** mode registry/types and matrix.

## `BEH-MODE-SELECTION` — Server builds, overrides, and synchronizes future rounds

- **Status:** `partial`.
- **Trigger/result:** chances/eligibility/queue/force actions build and synchronize future/next mode state.
- **Edge cases:** invalid sets, two queue models, unbounded admin tables and random order.
- **Regression:** deterministic selection, persistence and unauthorized/malformed transport.

## `BEH-ROUND-CYCLE` — Rounds progress through pre-round, active, end, and preparation states

- **Status:** `partial`.
- **Trigger/result:** one-second server Think advances `0 -> 1 -> 3 -> 0`, synchronizes clients and invokes mode/reset/equipment/intermission work.
- **Edge cases:** stale state 2, CO-OP/changelevel, fake get-up spawn and external failures.
- **Regression:** full dedicated cycle, late join/disconnect, selection, timeout/admin end and reset.

## `BEH-ORGANISM-LIFECYCLE` — Physiological state follows injury, fake ragdoll, unconsciousness and death

- **Status:** `partial`.
- **Trigger/result:** attach/reset/transfer, 10 Hz physiology, organ damage, fake/get-up/death and snapshot replication.
- **Ownership:** player and ragdolls may share one table while authority moves.
- **Edge cases:** load/module order, unsupported models, extreme values, stale callbacks and unversioned/high-cost transport.
- **Regression:** schema/order/owner fixtures, complete damage/model/armor matrix and population cost/privacy.
- **Related:** organism system/types and fake lifecycle.

## `BEH-FAKE-RAGDOLL-LIFECYCLE` — A living player can become a controllable physical body and return through respawn

- **Status:** `partial`.
- **Entry result:** custom body is created/adopted, identity/organism/appearance/NPC/vehicle state attached, player hidden/noninteractive and ownership replicated.
- **Active result:** per-frame server control drives physics from input, organism, weapon and class state; supports crawl/grab/use/choke/combat/fire and follows the hidden player.
- **Death/get-up:** body is reused on death; get-up checks velocity/stun/space, respawns under override, partially restores state and removes old body.
- **Client result:** NWEntity proxies primarily own fake/death state; custom packet/index overlaps render/camera transition.
- **Edge cases:** partial creation, undefined `ReadEntity2`, ownership reorder, global spawn override, stale timers, unsupported physics/vehicles and per-frame cost.
- **Regression:** one body generation across every transition/failure/latency/PVS path, controls/vehicles and camera/render restoration.
- **Related:** fake system/types and organism behavior.

## `BEH-MOVEMENT-CALC` — Ordinary movement is recomputed from physiology, class, weapon, load, stance, and inertia on both realms

- **Status:** `partial` — source path verified; server/client prediction convergence unproven.
- **Actors/context:** living non-fake player, shared `SetupMove`, organism, current class, active weapon, carried entity, mode hooks and movement convars.
- **Trigger:** every movement command on server and predicting client.
- **Observable result:** the system calculates walk/run/crouch/backward state, load and physiological power; applies class/NW/weapon/mode modifiers; rewrites forward/side movement and maximum speed; sets jump power; processes inertia, carry reach, slipping and dive-fake; updates animation/footstep/stamina state.
- **Fake interaction:** normal movement is suppressed/redirected when a fake body is active; fall/slip/dive and organism state can enter fake.
- **Convar behavior:** disabling `hg_inertia` does not disable the movement system; it primarily removes acceleration interpolation while the hook still owns speed/jump/input and transitions.
- **Edge cases:** realm-local `SysTime`, stale client organism/class/weapon state, prediction replay of mutable fields, input values reused after rewrite, nil matrices/physics/weapon data, zero/extreme modifiers and overlapping ordinary/fake ownership.
- **Regression procedure:** per-command server/client modifier trace under latency/replay; full organism/class/weapon/load/stance matrix; fake/fall/slip/get-up transitions; population cost.
- **Related:** `SYS-MOVEMENT`, `TYPE-MOVEMENT-CONTEXT`, character integration graph.

## `BEH-PLAYER-CLASS-TRANSITION` — A class change can reconfigure identity, equipment, physiology, movement, faction, and presentation

- **Status:** `partial` — registry/transition/transport and representative classes verified; all class hooks/consumers incomplete.
- **Actors/context:** player, old/new shared class definitions, mode/round caller, client mirrors and class-owned integrations.
- **Server trigger/result:** `SetPlayerClass` calls old `Off`, writes class field/NetVar, broadcasts class ID + Lua table, calls new `On` with original args, resets movement NWInts, then emits `PlayerClass`.
- **Client result:** client receives ID/table, writes the class field, calls new `On(data)` and emits `PlayerClass`; old client class `Off` is not called.
- **Death result:** class `PlayerDeath` runs, then ID is cleared and default is broadcast; side-effect cleanup depends on class-specific code.
- **Think result:** class `Think` is invoked through `Org Think`, but one `nextThink` timestamp on the shared class table lets only one same-class player run per interval.
- **Critical trust behavior:** the server accepts the same `playerclass` ID/table payload from any valid client and directly calls `SetPlayerClass`; no legitimate repository client sender or authorization/phase/rate checks were found.
- **Observable class effects:** models/bodygroups/name/role, loadout/armor/inventory, organism/movement/fake modifiers, NPC faction hooks, guilt, sounds, footsteps, phrases, gestures and HUD.
- **Edge cases:** raw server args versus normalized client table, nil `data` indexing, NW multipliers reset after `On`, mixed-case IDs, incomplete/empty `Off`, transition errors without rollback, persistent global hooks/NPC relationships and EntIndex reuse.
- **Regression procedure:** security fuzz/replay, every class-to-class transition while standing/fake/dead/in vehicle, injected failures/rollback, client cleanup, same-class multi-player Think and complete side-effect restoration.
- **Related:** `SYS-PLAYER-CLASS`, class registry/runtime/payload types, character integration graph.
