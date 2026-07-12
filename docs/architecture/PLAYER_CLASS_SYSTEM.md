# Player-Class System Architecture

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** registry/lifecycle/transport and representative concrete classes verified; every class method/global hook and external consumer is not yet exhaustive  
**Reviewed:** 2026-07-12

## Purpose

The player-class system is a project-specific registry and event dispatcher layered over Garry's Mod players. A class can change far more than identity or appearance. Concrete classes may control:

- model, bodygroups, materials, color, name, role and accessories;
- weapons, ammunition, armor and inventory;
- organism fields, movement multipliers, fall behavior and fake-ragdoll transitions;
- NPC relationships and dynamically registered world hooks;
- guilt/friendly-fire behavior;
- phrases, gestures, footsteps, HUD overlays and sound sets;
- class-specific Think/Damage/PlayerDeath/Spawn behavior;
- mode-specific subclasses and equipment.

Class state is distributed across a shared class table, mutable player fields, NWVars/NWInts, organism extensions, equipment, appearance, global hooks and an unversioned network table.

## Source topology

| File/area | Responsibility |
|---|---|
| `playerclass/sh_tier_0.lua` | class registry, lookup, generic class event dispatch and client class-change receiver |
| `playerclass/sv_tier_0.lua` | server class transition, network broadcast/receiver, death reset, damage/guilt/spawn/Think hooks |
| `playerclass/classes/**` | concrete class definitions and permanent global hooks |
| modes | assign class/subclass/role/equipment and assume class-specific behavior |
| movement | reads class Lua fields and NW multipliers |
| organism | class Think and direct class mutations influence physiology/fake/death |
| fake-ragdoll | class fall behavior, forced transformations, phrases/gestures/footsteps and active-ragdoll behavior |
| NPC/appearance/inventory/armor/weapons/UI | major class producers/consumers |

## Registry contract

`player.classList` maps a case-sensitive string ID to one shared class table.

`player.RegClass(name)` returns the existing table or creates/stores a new one. Repeated registration extends/mutates the same table rather than rejecting duplicates or declaring ownership.

Verified IDs discovered in executable class files:

| ID | Source | Verified role/surface summary |
|---|---|---|
| `default` | `classes/sh_default.lua` | applies ordinary appearance; allows default phrases, random sounds and gestures |
| `Slugcat` | `classes/sh_slugcat.lua` | custom model/state, movement speed/run/jump settings, creature sounds/footsteps and zero guilt |
| `police` | `classes/sh_police.lua` | ranked police identity/model/color and Homicide force guilt behavior |
| `terrorist` | `classes/sh_terrorist.lua` | appearance masks/band, team/hostage guilt and layered footsteps |
| `swat` | `classes/sh_swat.lua` | SWAT appearance/armor and movement/organism modifiers with military sound behavior |
| `nationalguard` | `classes/sh_nationalguard.lua` | ranked military identity/models, guilt and military footsteps |
| `groove` | `classes/sh_groove.lua` | gang identity/model/color/bodygroups and sling inventory |
| `bloodz` | `classes/sh_bloodz.lua` | gang identity/model/color/bodygroups and sling inventory |
| `gordon` | `classes/sh_gordon.lua` | Gordon/HEV transformation, loadout/armor, organism HEV state and suit feedback |
| `Combine` | `classes/sh_combine.lua` | Combine subclasses/loadouts/armor, callsigns/squads, organism recoil/pulse state, NPC relationships, sounds/HUD |
| `Metrocop` | `classes/sh_metrocop.lua` | Metrocop loadout/armor/callsign, organism recoil/pulse state, NPC relationships, phrases/footsteps/HUD |
| `Refugee` | `classes/sh_refuge.lua` | campaign/Defense survivor role, subclass equipment, NPC relationships and appearance |
| `Rebel` | `classes/sh_rebel.lua` | Rebel subclasses/loadouts/armor, NPC relationships, role, appearance and sound behavior |
| `commanderforces` | `classes/sh_commanderforces.lua` | Pathowogen Delta force appearance, guilt and military footsteps |
| `headcrabzombie` | `classes/sh_headcrabzombie.lua` | zombie model/body/health, organism brain state, faction relationships, sounds and guilt |
| `furry` | `classes/furry/sh_furry.lua` | Pathowogen creature transformation, infection/assimilation, movement/combat/organism and custom sounds/animations |

IDs are case-sensitive and use inconsistent casing. Consumers must use exactly `Slugcat`, `Combine`, `Metrocop`, `Refugee`, `Rebel`, while several other IDs are lowercase. Normalizing case without an alias/migration layer is breaking.

## Generic event dispatch

`PLAYER:PlayerClassEvent(name, ...)`:

1. resolves the player's current class table;
2. selects `class[name]` when present;
3. otherwise falls back to `player.classList.default[name]`;
4. invokes the function with the player as first argument;
5. forwards its returns.

This is not an automatic engine-hook registry. Only explicitly called class events run. Verified generic dispatch paths include:

- `On`, `Off` during transitions;
- `Damage` from `HomigradDamage`;
- `PlayerDeath` and death reset;
- `Think` from `Org Think`;
- `Guilt` from guilt logic;
- `Player Spawn` from a project hook;
- nested class-driven `GiveEquipment` calls.

Methods such as `Move` and `PlayerDraw` exist on classes, but no `PlayerClassEvent("Move")` or `PlayerClassEvent("PlayerDraw")` caller was located in repository search. They may be stale, externally consumed or directly called elsewhere; they must not be assumed functional without further evidence.

Concrete class files also install ordinary global hooks directly. Those hooks remain registered regardless of the current player class and branch on `PlayerClassName` at runtime.

## Server transition contract

`PLAYER:SetPlayerClass(name, args)` broadly:

1. validates server realm;
2. if clearing class: calls old `Off`, clears field/NetVar, broadcasts string `"nil"` plus empty table, then calls default `On` through fallback;
3. if assigning: resolves class table, calls current class `Off`, sets `PlayerClassName` and NetVar;
4. serializes `Data = args` only when `args` is a table, otherwise serializes `{}`;
5. broadcasts class string + Lua table to every client;
6. calls new `On` with the **original** `args`, not normalized `Data`;
7. resets NWInts `JumpMul`, `RunMul`, and `SpeedMul` to `1`;
8. emits `PlayerClass`.

### Transition defects

1. Server `On` receives raw nil/boolean/non-table input while clients receive `{}`. Realm behavior diverges.
2. Several concrete `On(self, data)` methods index `data.bNoEquipment` without guarding nil, so ordinary `SetPlayerClass("Class")` calls can error after state already changed.
3. NW movement multipliers are reset **after** `On`, silently overwriting any values assigned during class initialization.
4. There is no transaction/rollback if `Off`, network serialization, `On`, appearance, equipment or integration code errors.
5. Reassigning the same class still performs `Off` then `On`, potentially stripping/regranting equipment and resetting global hooks/state.
6. Client transition does not call the old class `Off`; client-only class cleanup must be global/event-based or leaks.
7. Server broadcasts every class change to every client rather than using ordinary entity-local replicated state only.
8. Class data has no schema, version, size cap or per-class validator.

## Network contract and critical trust boundary

Channel `playerclass` is registered server-side.

### Server -> clients

Ordered fields:

1. `string className` (`"nil"` means default/no explicit class);
2. Lua table `data`.

Client stores `PlayerClassName`, invokes `On(data)`, and emits `PlayerClass`.

### Client -> server

The server also registers a receiver for the same channel and reads:

1. `string className`;
2. Lua table `data`;
3. calls `ply:SetPlayerClass(className, data)`.

The only verified check is `IsValid(ply)`. No legitimate repository client sender was found.

This means a client can directly request any registered class and arbitrary class-data table unless another external layer blocks the message. Consequences can include model/loadout/armor/organism/relationship/fake/role changes and class-specific world hooks.

Required controls:

- remove client-to-server transition authority or restrict it to an explicit server-issued token/request flow;
- cap raw length/table depth/count and reject unexpected types;
- resolve an allowlisted server-side transition intent rather than accepting class IDs/data;
- validate active mode, role, admin permission and lifecycle phase;
- rate-limit and audit changes.

## Lifecycle hooks

### Damage

`HomigradDamage/playerclass` calls class `Damage`. Class methods can mutate or return damage behavior after organism damage processing. Exact return contract and ordering relative to other damage hooks require completion.

### Death/reset

`PlayerDeath/playerclass` calls class `PlayerDeath`, then `PlayerClassName` is cleared and the server broadcasts `"nil"` + empty table. It does not guarantee every class-owned Lua field, NWVar, hook, armor, appearance, inventory or organism extension is restored.

### Think

`Org Think/PlayerClass` obtains the class table, checks `class.nextThink`, sets `class.nextThink = time + 1`, then calls class `Think`.

Because the timestamp is stored on the **shared class table**, all players using the same class share one throttle. At most the first eligible player of that class receives the once-per-second Think callback during each interval; other same-class players return early.

This is a verified cross-player state bug. The throttle must be per player or the class Think method must receive a batch intentionally.

### Spawn

`Player Spawn/playerclass` calls the class event. Concrete classes also perform their main mutation through `On`, which modes frequently call independently of ordinary spawn.

### Guilt

`Guilt ClassSystem` forwards guilt decisions to the current class. Several classes implement team/faction logic, while `default` returns no decision and some creature classes return zero.

## Concrete class integration patterns

### Appearance/identity

Most classes call `ApplyAppearance` or random appearance helpers, then mutate model, materials, bodygroups, color, name, accessories and role. Common defects include:

- misspelled appearance fields such as `AColthes` and `AAttachmets`;
- assigning undefined lowercase `appearance` instead of the local `Appearance`;
- delayed timers capturing the player/class without validity/current-class checks;
- class exit methods that do not restore original name/model/material/bodygroups;
- model maps that assume a specific appearance key/case.

### Equipment/armor/inventory

Classes may strip all weapons, give subclass loadouts, ammo, medical items, grenades, armor and inventory entries. The class transition therefore overlaps mode `GiveEquipment`, round reset, inventory and role systems.

Common risks:

- failed `Give` results dereferenced for ammo/attachments;
- class data `bNoEquipment` is inconsistent between boolean/table/nil callers;
- equipment can be granted both by mode and class;
- `Off` rarely reverses loadout/armor/inventory;
- class transition can occur while fake/dead/in vehicle.

### Organism/movement/fake

Classes write fields such as recoil, pulse-check restrictions, HEV/brain state, movement multipliers, jump/run speed, melee power, stamina/fall behavior and infection/assimilation state.

`Combine`, `Metrocop`, furry and other transformation classes can force `hg.FakeUp` before changing model/body state. Cleanup often restores only a subset of organism fields.

### NPC/faction relationships

Combine/Metrocop/Rebel/Refugee and related classes:

- scan every `npc_*` entity on entry/exit;
- mutate relationships and clear enemy memory;
- install per-player `OnEntityCreated` hooks keyed by EntIndex;
- remove those hooks in selected `Off`/death paths.

This makes class changes O(number of NPCs), mutates global AI behavior, and can leave hooks/relationships stale after errors, disconnect, EntIndex reuse or incomplete `Off` execution.

### Global presentation hooks

Class files register permanent hooks for footsteps, phrases, gestures, HUD overlays, animations and sounds. These hooks remain loaded for the whole session and branch on class name.

There is no registry tying these hooks to the class lifecycle, so removal/renaming/refactoring must inventory them separately from class table methods.

## Class matrix: verified high-impact fields/methods

| Class group | High-impact behavior |
|---|---|
| default | appearance and default phrase/sound/gesture capability flags |
| police/terrorist/nationalguard/gangs/commanderforces | appearance/identity, faction/team guilt, class footsteps, inventory additions |
| SWAT | appearance/armor and direct movement/organism/combat multipliers |
| Gordon | HEV/model/loadout/armor transformation, organism HEV state and suit feedback |
| Combine/Metrocop | subclasses/loadouts, forced fake-up, armor, organism fields, callsigns/roles, NPC relationships, dynamic hooks and HUD/sounds |
| Rebel/Refugee | mode/subclass equipment, armor/appearance, NPC relationships and dynamic hooks |
| Slugcat | custom model/health/scale, direct run speed and movement/fall/creature presentation |
| Headcrab zombie | zombie model/body/health, brain/faction/sound behavior and creature guilt |
| Furry | large transformation/infection/assimilation system coupled to fake, organism, movement, damage, animations and Pathowogen |

## Public APIs and data

- `player.classList`
- `player.RegClass(name)`
- `PLAYER:GetPlayerClass()`
- `PLAYER:SetPlayerClass(name, data)`
- `PLAYER:PlayerClassEvent(name, ...)`
- `PLAYER:ResetPlayerClass()` server helper
- player field/NetVar `PlayerClassName`
- network channel `playerclass`
- hook `PlayerClass`
- class tables and arbitrary class data/method names

## Verified structural defects and hazards

1. Client-authoritative class-change receiver with arbitrary ID/data and no permission/phase/rate validation.
2. Unbounded/unversioned Lua-table class data.
3. Server/client data divergence because server passes raw args while client receives normalized table.
4. Client never calls old class `Off` during network transition.
5. Shared class-table `nextThink` throttles all same-class players together.
6. NW movement multipliers reset after class `On`.
7. Case-sensitive mixed-case identifiers create fragile comparisons and migrations.
8. No transactional transition/rollback; partial model/equipment/organism/hook state remains after errors.
9. `Off` is empty or incomplete for many classes.
10. Concrete classes install permanent global hooks outside the registry lifecycle.
11. Per-player world hooks are keyed by EntIndex and depend on correct cleanup.
12. Class changes repeatedly scan/mutate all NPC relationships.
13. Appearance/equipment/class-data APIs use inconsistent field names and nil assumptions.
14. Mode and class equipment/role/appearance ownership overlap.
15. Class organism/movement fields lack an extension/default/reset registry.
16. Methods such as `Move`/`PlayerDraw` have no located generic dispatcher and may be dead/external contracts.
17. Class table registration is additive/overwrite-prone with no duplicate owner diagnostics.
18. Death reset clears the class ID but cannot prove all class side effects are removed.

## Required validation

### Registry and transport

- Enumerate every class, method, field, global hook and consumer.
- Fuzz `playerclass` with unauthorized IDs, large/deep tables, wrong phases and rapid replay.
- Remove or lock C -> S authority before public deployment.
- Verify realm class-table parity and case-sensitive IDs.

### Lifecycle

- Transition every class to every other class while alive, fake, unconscious, dead, in vehicle and during mode/round changes.
- Inject failure into `Off`, appearance, equipment, organism, NPC and `On` stages; assert rollback.
- Verify client cleanup and old-class effects.
- Run multiple players of the same class and prove per-player Think behavior.

### Integration

- Appearance/model/bodygroup/material restoration.
- Equipment/armor/inventory duplication and failure.
- Organism/movement/fake field reset.
- NPC relationship/hook cleanup under disconnect/EntIndex reuse.
- Footstep/phrase/HUD/gesture behavior across class changes.
- Mode subclass and `bNoEquipment` call shapes.

## Implementation boundary

Do not migrate classes into a new system until organism/fake/movement and mode ownership are mapped. The eventual architecture should provide:

1. immutable class definition records with explicit IDs and aliases;
2. server-authoritative transition requests only;
3. versioned, bounded class state rather than arbitrary tables;
4. transactional `Exit -> Apply -> Enter` with rollback/finally cleanup;
5. explicit modifier/equipment/appearance/NPC/presentation interfaces;
6. per-player runtime state separate from shared class definitions;
7. registered extension fields/defaults for organism/movement;
8. lifecycle-owned hook handles rather than permanent global hooks;
9. deterministic per-player Think scheduling;
10. compatibility adapters for existing class IDs and mode calls.

## Next trace

1. Complete all concrete class method/global-hook inventories.
2. Locate unresolved class `Move`/`PlayerDraw` and movement-stage consumers.
3. Build the combined organism/fake/movement/class integration graph.
4. Trace weapon interfaces consumed by movement and active ragdoll control.
