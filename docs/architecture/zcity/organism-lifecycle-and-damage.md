# Z-City Organism Lifecycle and Damage

**Status:** Verified by static inspection of the current executable source, reconciled from the earlier architecture baseline. Runtime load-order, packet-capture, and injury-fixture validation remain required.

## Scope

This document records the current organism system's ownership, initialization, clearing, simulation, damage, incapacitation, fake/death-ragdoll interaction, replication, and cleanup contracts.

Primary source areas:

- `lua/homigrad/organism/tier_0/**`;
- `lua/homigrad/organism/tier_1/**`;
- `lua/homigrad/organism/sv_brainfuck.lua`;
- organism consumers in player, fake-ragdoll, mode, class, weapon, armor, medical, NPC, UI, and spectator code.

The organism is not an isolated health component. It is shared mutable gameplay state that participates in movement, consciousness, death, damage, fake ragdolls, mode outcomes, medical actions, and client presentation.

## Source topology

### Tier 0: attachment, transfer, registry, and geometry

| Area | Current responsibility |
|---|---|
| `tier_0/sv_tier_0.lua` | Create/remove organisms, maintain the global active registry, transfer ownership, attach players/NPCs/ragdolls, and emit the global organism tick. |
| `tier_0/cl_tier_0.lua` | Remove stale client organism references when entities disappear. |
| `tier_0/sh_hitboxorgans.lua` | Build custom model/organ oriented bounding boxes and admin visualization data. |
| `tier_0/sv_hitboxorgans.lua` | Trace penetration and blast interactions through custom organ geometry. |
| `tier_0/sh_hitboxorgans_manual.lua` | Define ValveBiped organs, bones, arteries, and conditional armor regions. |

### Tier 1: schema, simulation, damage, and presentation

| Area | Current responsibility |
|---|---|
| `tier_1/sv_organism.lua` | Reset the organism in place, run physiology modules, decide life/unconscious/fake state, heal, and replicate. |
| `tier_1/sv_input.lua` | Intercept damage, resolve penetration/organ hits, dispatch tissue handlers, create wounds, apply forces/effects, and reduce ordinary engine damage. |
| `tier_1/modules/*.lua` | Blood, pain, pulse, lungs, stamina, metabolism, liver, random events, virus, and related physiology. |
| `tier_1/modules_input/*.lua` | Organ, bone, limb, artery, and tissue damage handlers. |
| `tier_1/cl_statistics.lua` | Receive/merge snapshots and maintain interpolated client state. |
| `tier_1/cl_main.lua` | Render organism-driven audiovisual effects and medical interaction UI. |
| `organism/sv_brainfuck.lua` | Apply brain-damage fencing, spasms, and fake/death-ragdoll physical reactions. |

## Load-order contract

The subsystem depends on recursive filename/directory loading rather than a declared manifest. Tier 1 assumes Tier 0 already created `hg.organism`; module and input files assume their registries exist before callbacks are invoked.

The current directory naming suggests the intended order, but sibling enumeration is not explicitly sorted. A changed filesystem order can therefore turn an organism dependency into a startup failure rather than a controlled unavailable capability.

## Ownership and identity

`hg.organism.Add(ent)` creates one mutable organism table and assigns it to the entity. The table contains:

- `owner`: the entity currently treated as authoritative;
- `ownerX`: the original identity entity;
- lifecycle, physiology, wound, organ, limb, extension, and replication fields.

The same table is inserted into the global organism registry and passed to `Org Add`.

`hg.organism.Clear(ent)` does not replace the organism table. It emits `Org Clear`, and the Tier 1 handler rewrites the existing table to defaults.

### Shared-table transitions

The player, fake ragdoll, and death ragdoll can reference the same organism table:

1. a player receives an organism during initial spawn;
2. ordinary spawn/reset clears it in place;
3. fake-ragdoll creation transfers or shares authority with the ragdoll;
4. getting up preserves the table while removing the fake-ragdoll pointer;
5. death transfers the table to the death ragdoll and sends a final snapshot;
6. entity removal deletes registry ownership when applicable.

This avoids state copying but creates a strict identity invariant. Every callback must distinguish original identity, current owner, fake ragdoll, death ragdoll, and stale entity references. The current system has no explicit owner generation or transfer token.

## Canonical reset behavior

`Org Clear` initializes a large implicit schema, including:

| Group | Representative state |
|---|---|
| Lifecycle | owner, original owner, alive, player/fake flags, replication timing |
| Consciousness/control | unconsciousness, fake requests, consciousness, disorientation, stun, movement gates |
| Cardiovascular | blood, bleeding, arteries, heart, pulse, internal bleeding |
| Respiratory | lungs, trachea, pneumothorax, oxygen, carbon monoxide, breath holding |
| Pain/drugs | pain, shock, analgesia, narcotic/antagonist state, immobilization |
| Movement/energy | stamina, adrenaline, recoil multiplier, limb strength, melee speed |
| Organs/bones | brain, skull, spine, chest, pelvis, heart, liver, stomach, intestines |
| Limbs | limb health, dislocations, amputations, head amputation |
| Wounds | wounds, arterial wounds, lodged entities, damage stacks, counters |
| Environment/metabolism | temperature, satiety, hunger, thiamine, fear |
| Extensions | mode/class flags such as superfighter, assimilation, infection, berserk, HEV, godmode |
| Replication | full-send, send cadence, critical/incapacitated flags |

The schema is duplicated across reset logic, modules, client interpolation, networking, and arbitrary consumers. There is no authoritative field registry defining default, type, visibility, persistence, reset policy, or owner.

`Org Clear` also mutates the owning entity by restoring health for living players and clearing selected wound NetVars. It is therefore a state reset plus an entity-side lifecycle operation, not a pure table initialization.

## Simulation order

Tier 0 emits `Org Think(owner, organism, timeValue)` approximately every 0.1 seconds for each registered organism. The main Tier 1 handler runs broad phases in this observed order:

1. player stamina;
2. lungs and oxygen;
3. liver;
4. blood and wounds;
5. pain and consciousness;
6. metabolism;
7. random events;
8. pulse, heart, temperature, and fear;
9. mode/class status extensions;
10. unconscious, fake, and movement decisions;
11. healing, phrases, and death state;
12. replication and wound NetVars.

Additional independent `Org Think` hooks then run for virus effects, sounds, brain fencing/spasms, modes, and integrations.

### Order-sensitive writes

Multiple systems write the same fields:

- pain and lungs both write consciousness;
- blood, pain, pulse, virus, and damage paths can request unconsciousness;
- virus can replace calculated pain after the main pain module;
- modes/classes write extension fields with inconsistent reset ownership;
- medical/damage code mutates oxygen, blood, heart, brain, wounds, and drugs between ticks.

Hook order is therefore gameplay behavior. It is currently implicit.

## Damage pipeline

The principal damage hook performs a monolithic sequence:

1. reject unsupported targets or redirect player/fake-ragdoll damage;
2. resolve the current owner and organism;
3. derive penetration, diameter, ricochet, and multipliers from the inflictor/weapon/bullet;
4. build current organ geometry from model bones;
5. trace bullets, slash/club damage, or blast intersections;
6. dispatch organ, artery, bone, limb, and tissue handlers;
7. add wounds, pain, shock, immobilization, fear, adrenaline, and internal damage;
8. emit project damage hooks;
9. apply forces, effects, continued penetration, and head/limb consequences;
10. heavily scale ordinary engine damage and schedule replication.

Collision/crush handling enters through separate ragdoll/player physics paths and then mutates the same organism state.

### Verified damage hazards

- Global penetration override variables can be consumed by nested or reentrant damage.
- Some pre-damage hook arguments are emitted before final local trace values exist.
- Invalid/world/NPC attackers and optional inflictor fields are not normalized consistently.
- Fake-ragdoll redirection depends on identity and hook-return semantics to avoid recursion or duplicate damage.
- Ordinary `DMG_CRUSH` can bypass the main path while collision damage is handled elsewhere.
- Continued bullets mutate and reuse the original bullet table.
- Delayed wounds, effects, and snapshots capture entities and organism tables after transfer/removal.
- Several handlers contain unreachable, misspelled, disabled, or incorrectly ordered calculations.
- Bone/amputation paths assume bones, matrices, translated indices, constraints, and physics objects remain valid.
- Damage-type combinations use arithmetic addition rather than an explicit bitmask helper.

## Incapacitation, fake state, and death

Physiology computes requested unconscious/fake state (`needotrub`, `needfake`) and commits it near the end of the tick.

Inputs include blood, oxygen, pulse, brain/heart condition, pain/shock, spine/limb damage, stun, movement ability, amputation, and mode/class extensions.

Transitions emit compatibility hooks such as `HG_OnOtrub`, `HG_OnWakeOtrub`, and `PlayerDropWeapon`. Fake/unconscious state invokes the fake-ragdoll system while preserving the shared organism table. Organism death stops heart/lung behavior and kills the owner when the current identity path permits it.

`sv_brainfuck.lua` separately blocks get-up and adds spasm/fencing physics based on head/brain damage. This means incapacitation authority is distributed across physiology, fake-ragdoll code, brain effects, damage handlers, modes, and player state.

## Replication

### Current snapshot

`organism_send` writes:

1. a serialized Lua table;
2. full-send flag;
3. spectator-protection flag;
4. additional-information flag;
5. add/merge flag.

Normal owner snapshots are sent approximately once per second. Bare/PVS snapshots are sent approximately once per second for players and every three seconds for non-player/fake organisms. Immediate partial merge packets are also used for actions such as breath holding and amputation.

The client stores mutable current/new copies, merges partial updates, mirrors state to fake ragdolls, and interpolates a hard-coded field list.

### Replication defects

- The payload is an implicit unversioned Lua-table schema.
- Client validation can dereference owner/state before proving validity.
- Developer mode can serialize the entire organism table.
- Public/PVS, spectator, and owner-private visibility are not defined as explicit field sets.
- Large nested snapshots scale with players, NPC organisms, and ragdolls.
- Mutable old/new copies can alias or diverge during owner transfer.
- Wounds also travel through NetVars, creating overlapping authorities.
- `organism_sendply` is registered while its located client reader is commented out.
- Virus stage uses a separate packet whose client receiver was not located in the earlier repository-wide trace.

## Client-side side effects

Organism presentation drives DSP, sound fades, post-processing, pain/blood/oxygen effects, and radial medical interactions.

The current client also records low-quality dream screenshots under client data storage and removes them during selected lifecycle events. This persistent local-data behavior is not required for physiological authority and should become explicit, optional presentation policy.

The dislocation console command validates several organism conditions but relies on argument parsing and eye-trace target selection without a separately declared interaction-distance contract.

## Public compatibility surfaces

Important hooks include:

- `Org Add`, `Org Clear`, `Org Think`, `Org Transfer`, `Org Think Call`;
- `HG_OnOtrub`, `HG_OnWakeOtrub`, `Should Fake Up`;
- `PreHomigradDamage`, `PreHomigradDamageBulletBleedAdd`, `HomigradDamage`;
- `OnAmputateLimb`, `Ragdoll Collide`, `RagdollDeath`.

Important APIs include:

- `hg.organism.Add`, `Clear`, `Trace`, `BlastTrace`, `ShootMatrix`, `GetHitBoxOrgans`;
- `hg.organism.input_list.*` and wound/amputation helpers;
- entity organism attachment/query methods;
- `hg.send_organism`, `hg.send_bareinfo`;
- `hg.BreakNeck`, `hg.ExplodeHead`.

These are compatibility surfaces until all callers are mapped.

## Cross-system coupling

| System | Organism dependency |
|---|---|
| Fake ragdoll | shared table, owner transfer, damage redirection, collision damage, get-up gates |
| Modes | alive/incapacitated winner logic, recoil and class/status extensions |
| Player classes | physiology modifiers, assimilation/conversion, movement and event behavior |
| Weapons/ballistics | penetration, diameter, damage multipliers, continued bullets, inflictor fields |
| Armor | conditional organ geometry, gas protection, helmet/bone modifiers |
| Medical/inventory | wounds, drugs, organ state, equipment assumptions |
| NPC/bots | organism attachment, fake-player behavior, damage and death |
| UI/spectator | private and observed organism snapshots and presentation |
| Persistence/integrations | virus/class state, NetVars, local dream images, external hooks |

## Required project design

The replacement boundary must preserve observed gameplay through compatibility adapters while introducing:

1. one explicit organism schema registry with type, default, owner, reset, visibility, and persistence metadata;
2. one identity/owner-generation transfer contract for player, fake ragdoll, death ragdoll, NPC, and removal;
3. deterministic simulation phases and declared module priorities;
4. separated geometry, damage-resolution, physiological mutation, effects, and replication stages;
5. per-damage-event context instead of global penetration overrides;
6. explicit extension registration for modes, classes, items, diseases, and integrations;
7. versioned delta replication with owner-private, authorized medical, spectator, and public field sets;
8. cadence and bandwidth budgets with instrumentation;
9. validated model profiles and safe unsupported-model fallback;
10. injury and lifecycle regression fixtures.

## Initial disposition against Trauma

- **Adopt:** explicit schema metadata, delta concepts, owner generations, and subsystem diagnostics as requirements.
- **Adapt:** Trauma's medical, narcotic, infection, and health-presentation concepts only as individually registered modules behind the Z-City organism contract.
- **Rewrite:** organism networking, ownership transfer, extension fields, damage-event context, and lifecycle scheduling.
- **Reject:** monolithic HUD/medical implementations, whole-table developer replication, broad detours, and parallel organism authority.
- **Keep Z-City temporarily:** current field names, hooks, table-sharing behavior, damage outcomes, and snapshot compatibility until fixtures establish parity.

## Required acceptance tests

1. Cold boot and hot reload with recorded Tier 0/Tier 1/module/input order.
2. Add/clear/remove for player, NPC, fake ragdoll, and death ragdoll.
3. Fake/get-up/death/disconnect/removal during delayed damage and replication work.
4. Canonical schema equality after every clear path.
5. Mode/class extension reset across spawn, round reset, fake, death, and mode switch.
6. Deterministic module-order tests for consciousness, blood, oxygen, pulse, pain, and temperature.
7. Zero, extreme, NaN, and infinite values for major physiological fields.
8. Every damage type against player, fake ragdoll, death ragdoll, and supported NPC.
9. Reentrant penetration and continued-bullet isolation.
10. Collision/crush parity and duplicate-damage suppression.
11. Missing bones, unsupported models, invalid inflictors/attackers, and removed physics objects.
12. Amputation, dislocation, break-neck, and head explosion failure paths.
13. Owner/private versus observer/spectator/medical replication authorization.
14. Snapshot/delta packet schema rejection and stale owner-generation handling.
15. Bandwidth and encode/decode measurements at representative player/NPC/ragdoll counts.
16. Organism interaction with late join, spectator target changes, round reset, map cleanup, and Lua refresh.

## Next verification work

- Trace exact fake-ragdoll creation, transfer, input, combat, get-up, vehicle, and removal behavior.
- Trace movement and player-class consumers of organism state.
- Inventory every medical item and every organism packet/NetVar consumer.
- Build the combined organism/fake-ragdoll/movement/class ownership graph before production refactoring.
