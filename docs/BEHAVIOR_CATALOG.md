# Behavior Catalog

Externally observable behavior is recorded independently from implementation structure. `Verified` means executable source establishes the behavior; entries remain `partial` when runtime evidence or integration coverage is still missing.

## `BEH-REALM-GLOBAL` — Global addon files are routed by exact prefix/suffix with shared fallback

- **Status:** `partial` — routing code verified; complete runtime manifest pending.
- **Actors/context:** Server and clients loading `lua/homigrad` and `lua/initpost`.
- **Trigger/result:** Autorun loader; exact realm prefixes/suffixes, unmarked shared fallback, current-directory files before children.
- **Edge cases:** unsorted enumeration, exact-marker limits, ixhl2rp early exit and client delivery of unmarked files.
- **Regression:** instrument include path/realm/order on dedicated server/client.
- **Related:** `SYS-BOOTSTRAP-GLOBAL`, `TYPE-HG-BOOTSTRAP`.
- **Last verified:** loader blob `c250ed9129cfc61ef43c1ee0bb6c0fde0a0d53e5`, 2026-07-12.

## `BEH-REALM-GAMEMODE` — Gamemode files use substring routing and child-first recursion

- **Status:** `partial`.
- **Trigger/result:** gamemode loader recurses children before files; substring `sv_`/`sh_`/`cl_`; unmarked files ignored.
- **Edge cases:** substring misclassification, silent unloaded files, unsorted order and difference from global loader.
- **Regression:** compare discovered and actually included server/client manifests.
- **Related:** `SYS-BOOTSTRAP-GAMEMODE`.
- **Last verified:** loader blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `BEH-MODE-DISPATCH` — Current mode functions are dispatched through shared hook callbacks

- **Status:** `partial` — complete known source matrix; runtime external hook coverage pending.
- **Trigger/result:** every function-valued mode member becomes a hook candidate; dispatcher selects main/current/tdm and calls with mode table first.
- **Edge cases:** internal helpers exposed, dot-function argument shift, empty overrides, disabled-mode callbacks and inherited surfaces.
- **Regression:** selected realm/mode, self/arguments, nil/multiple returns, fallback, inheritance, hotload and accidental helper emission.
- **Related:** mode registry/types and `MODE_FUNCTION_MATRIX.md`.
- **Last verified:** loader blob `b1754dff2d53012a05cb109f26b75eae118b14ce`, 2026-07-12.

## `BEH-MODE-SELECTION` — Server builds, overrides, and synchronizes the future round sequence

- **Status:** `partial`.
- **Trigger/result:** eligibility/chances/queue/force actions build a 20-entry list and synchronized next/force state.
- **Edge cases:** invalid/empty sets, two queue models, unbounded admin tables and randomness/order.
- **Regression:** deterministic chances, eligibility, force/queue/persistence and unauthorized/malformed transport.
- **Related:** mode/round systems and queue type.
- **Last verified:** round blob `324491c8ad470d0aae1c24b768b9dc607b38c4e7`, 2026-07-12.

## `BEH-ROUND-CYCLE` — Rounds progress through pre-round, active, end, and preparation states

- **Status:** `partial`.
- **Trigger/result:** server one-second Think advances `0 -> 1 -> 3 -> 0`, synchronizes clients and invokes mode/reset/equipment/intermission work.
- **Edge cases:** stale state 2, CO-OP/changelevel, spawn/fake get-up, external failure and realm-local same-name callbacks.
- **Regression:** dedicated full cycle, late join/disconnect, force/random, timeout/admin end, player reset and packet values.
- **Related:** round system/state/payload.
- **Last verified:** server `324491...`, client `fa6181...`, 2026-07-12.

## `BEH-ORGANISM-LIFECYCLE` — Physiological state follows the character through injury, fake ragdoll, unconsciousness and death

- **Status:** `partial` — source verified; deterministic/runtime integration incomplete.
- **Actors/context:** players, supported NPCs, fake/death ragdolls, damage, modes/classes, medical systems and observing clients.
- **Trigger/result:** organism attachment/clear/transfer, 10 Hz modules, organ damage, fake/get-up/death; shared state determines control/life and is replicated/interpolated.
- **Ownership:** player and ragdolls may share one table while owner changes.
- **Edge cases:** load order, module overwrites, unsupported models, extreme values, delayed owner transfer and unversioned/high-cost transport.
- **Regression:** schema/order/owner fixtures, every damage/model/armor/collision/amputation path and population network cost/privacy.
- **Related:** organism system/types and fake lifecycle.
- **Last verified:** Tier 0 `1b8a...`, core `483050...`, damage `cce5ff...`, 2026-07-12.

## `BEH-FAKE-RAGDOLL-LIFECYCLE` — A living player can transition into a controllable physical body and return through respawn

- **Status:** `partial` — core source behavior verified; runtime ordering, every integration and performance limits pending.
- **Actors/context:** living/dead player, current/old/death ragdolls, organism, weapons, vehicles, NPCs, camera/render clients and spawn/round systems.
- **Entry trigger:** voluntary `fake` command, organism unconscious/fake request, fall/collision/class behavior, vehicle hook, mode/item/admin force.
- **Entry result:** custom ragdoll is created/adopted, posed and physically initialized; appearance/organism/identity/NPC bullseye/vehicle state are attached; player is hidden and moved to noninteractive collision while remaining alive; fake ownership is replicated.
- **Active result:** server per-frame control drives body physics from player buttons/view, organism power and weapon/class state; supports pose, crawl, grab, use/pickup, choke, combat, stamina, pain, fire and vehicle behavior; player entity follows the ragdoll.
- **Death result:** active body is reused as death ragdoll, wounds/identity remain, engine ragdoll is suppressed, camera/render follow changes.
- **Get-up trigger/result:** velocity/stun/organism/external hooks and safe hull position are checked; player is respawned under spawn-override state, health/armor/weapon/position are partially restored, old body is removed and rendering/collision/movement return.
- **Client result:** NWEntity proxies primarily reconstruct fake/death ownership; custom packet supplies ragdoll index; render/camera follow and smooth bone interpolation run through transition.
- **Edge cases:** partial creation, ragdoll removal kills living owner, undefined `ReadEntity2`, packet/NW/proxy reorder, shared organism stale callbacks, global spawn override errors, timer/EntIndex reuse, unsupported skeleton/physics, vehicle destruction, per-frame cost and camera/render leaks.
- **Implementation evidence:** `fake/sv_tier_0.lua`, `sv_control.lua`, `sv_input.lua`, `cl_fake.lua`, `sh_render.lua`; `architecture/FAKE_RAGDOLL_SYSTEM.md`.
- **Regression procedure:** assert one body generation across every server/client reference; failure injection for create/fake/get-up/death/disconnect; latency/PVS/late join; controls/combat/constraints/fire; model/vehicle matrix; performance and camera/render restoration.
- **Related:** `SYS-FAKE-RAGDOLL`, `TYPE-FAKE-RAGDOLL-STATE`, `TYPE-FAKE-RAGDOLL-PAYLOAD`, `TYPE-FAKE-CONTROL-STATE`, organism behavior.
- **Last verified:** server `0fa522db3f0562eaf1816d6452fa082aef81d2bb`; control `22c87ad4148716ff1173c104e7df943043b09ce5`; client `bdd7e6a215da568a2070bd9b33e29244f1970f90`; 2026-07-12.
