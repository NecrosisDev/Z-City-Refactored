# Organism System Architecture

**Work package:** `WP-RESEARCH-001`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Branch:** `docs/architecture-baseline`  
**Status:** executable-source verified; medical-item and every client presentation consumer not yet exhaustive  
**Reviewed:** 2026-07-12

## Purpose

The organism system replaces ordinary health-only damage with a mutable physiological state attached to players, NPCs, fake ragdolls, and death ragdolls. It owns or influences:

- life/death and unconsciousness;
- blood, wounds, arteries and internal bleeding;
- pain, shock, consciousness and immobilization;
- pulse, heart, oxygen, lungs, temperature and carbon monoxide;
- stamina, adrenaline, fear, metabolism and hunger;
- organ, bone, limb, dislocation and amputation damage;
- custom organ hitboxes and penetration;
- fake-ragdoll transitions and post-death physical effects;
- network snapshots used by HUD, spectator, medical and presentation systems.

It is not one isolated module. It is a shared state machine written by damage code, physiology modules, modes, player classes, weapons, medical items, fake-ragdoll code, virus logic and direct hooks.

## Source topology and load assumptions

### Tier 0 — attachment, ownership and geometric tracing

| File | Verified responsibility |
|---|---|
| `organism/tier_0/sv_tier_0.lua` | organism creation/removal, global registry, owner transfer, player/NPC attachment, fake/death-ragdoll sharing and the global 10 Hz `Org Think` loop |
| `organism/tier_0/cl_tier_0.lua` | client entity-removal cleanup |
| `organism/tier_0/sh_hitboxorgans.lua` | model/custom-organ OBB construction and client admin hitbox visualization |
| `organism/tier_0/sv_hitboxorgans.lua` | custom ray/penetration and blast traversal through organ OBBs |
| `organism/tier_0/sh_hitboxorgans_manual.lua` | ValveBiped organ, bone, artery and conditional-armor hitbox definitions |

### Tier 1 — state reset, physiology, damage and presentation

| Area | Verified responsibility |
|---|---|
| `tier_1/sv_organism.lua` | canonical reset schema, module execution order, life/unconscious/fake state, regeneration and replication |
| `tier_1/sv_input.lua` | authoritative damage interception, custom penetration, organ dispatch, wounds, amputation, collision damage and damage hooks |
| `tier_1/modules/*.lua` | pulse, blood, pain, lungs, stamina, metabolism, liver, random events and virus behavior |
| `tier_1/modules_input/*.lua` | organ, bone, limb, artery and tissue-specific damage handlers |
| `tier_1/cl_statistics.lua` | network snapshot receive/merge, client interpolation schema and admin statistics |
| `tier_1/cl_main.lua` | organism-driven screen/audio effects, radial dislocation actions and dream screenshot system |
| `organism/sv_brainfuck.lua` | brain-damage fencing, spasms and fake/death-ragdoll physical reactions |

### Load-order constraint

The global loader recursively includes files before child directories, but neither file nor directory results are explicitly sorted. Tier 1 assumes Tier 0 has already created `hg.organism`, and Tier 1 module files assume `sv_organism.lua` has already created `hg.organism.module` and `hg.organism.input_list` before their initialization callbacks are used.

Static source shows the intended directory naming/order, but runtime instrumentation is required to prove the actual startup order on every platform. A changed enumeration order can make the subsystem fail during load rather than degrade gracefully.

## Ownership model

### Creation

`hg.organism.Add(ent)` creates one mutable table containing at least:

```text
owner  -> current authoritative entity
ownerX -> original/identity entity
```

The table is assigned to `ent.organism`, inserted into `hg.organism.list`, and passed through `hook.Run("Org Add", ent, organism)`.

`hg.organism.Clear(ent)` does not replace the table. It emits `Org Clear`, whose Tier 1 handler resets the table in place to the canonical baseline.

### Player lifecycle

1. `PlayerInitialSpawn` schedules `Add` + `Clear`.
2. Spawn/reset hooks clear wounds and reinitialize state unless `OverrideSpawn` is active.
3. The global organism loop runs approximately every 0.1 seconds.
4. Player death transfers the same organism table to the death ragdoll and sends a final snapshot.
5. Entity removal deletes its registry entry and emits client cleanup where applicable.

### Fake ragdoll

When a player fakes:

- the fake ragdoll and player share the **same organism table**;
- `owner`/`ownerX` and transfer hooks determine which entity is currently authoritative;
- player damage is forwarded to the fake ragdoll;
- getting up removes the ragdoll pointer but preserves the organism table;
- death-ragdoll, spasm, amputation and medical systems continue to read/write the same state.

This shared-table design avoids explicit state copying but creates a strict identity/ownership invariant: every delayed callback and consumer must know whether `owner`, `ownerX`, the player, fake ragdoll, or death ragdoll is currently valid and authoritative.

## Canonical reset schema

The `Org Clear/Main` handler initializes the primary state. Major groups are below; this is a contract summary, not every temporary field.

| Group | Representative fields |
|---|---|
| Identity/lifecycle | `owner`, `ownerX`, `entindex`, `alive`, `isPly`, `fakePlayer`, `ownerFake` |
| Consciousness/control | `otrub`, `needotrub`, `fake`, `needfake`, `consciousness`, `disorientation`, `canmove`, `canmovehead`, `stun`, `lightstun` |
| Cardiovascular | `blood`, `bloodtype`, `bleed`, `internalBleed`, `arteria`, limb arteries, `heart`, `heartstop`, `pulse`, `heartbeat` |
| Respiratory | `lungsL`, `lungsR`, `trachea`, `pneumothorax`, `o2`, `CO`, `lungsfunction`, `holdingbreath` |
| Pain/drugs | `pain`, `painadd`, `avgpain`, `shock`, `hurt`, `analgesia`, `painkiller`, `naloxone`, `tranquilizer`, `immobilization` |
| Movement/energy | `stamina`, `adrenaline`, `adrenalineStorage`, `recoilmul`, `legstrength`, `meleespeed` |
| Bones/organs | `brain`, `skull`, `jaw`, `spine1..3`, `chest`, `pelvis`, `heart`, `liver`, `stomach`, `intestines` |
| Limbs | `lleg`, `rleg`, `larm`, `rarm`, dislocation booleans, amputation booleans, `headamputated` |
| Wounds | `wounds`, `arterialwounds`, `dmgstack`, `LodgedEntities`, wound counters |
| Environment/metabolism | `temperature`, `satiety`, `hungry`, `thiamine`, `fear`, `fearadd` |
| Mode/class extensions | `superfighter`, `assimilated`, `furryinfected`, `berserk`, `noradrenaline`, `HEV`, `godmode` |
| Replication | owner `fullsend`, `sendPlyTime`, `timeValue`, `critical`, `incapacitated` |

`Org Clear` also mutates the owner by setting health to 100 for a living player and clearing replicated wounds/arterial wounds and selected NetVars.

## Authoritative tick model

Tier 0 emits `Org Think(owner, org, timeValue)` for every registered organism on the global loop. The Tier 1 `Org Think/Main` callback executes physiology in this verified order:

1. stamina — players only;
2. lungs/oxygen — players or fake-player organisms;
3. liver — players only;
4. blood/wounds;
5. pain/consciousness;
6. metabolism — players only;
7. random events — players only;
8. pulse/heart/temperature/fear;
9. assimilation, berserk and noradrenaline state;
10. unconscious/fake/movement decisions;
11. healing, class/status phrases and death state;
12. replication and wound NetVars.

Other `Org Think` hooks then participate in the same global event, including virus effects, random virus/temperature sounds, brain fencing/spasm processing and mode/integration behavior. Hook registration order therefore changes gameplay because later callbacks can overwrite values produced by the core modules.

### Observable overwrite examples

- Pain and lungs both write `consciousness`.
- Blood, pain, pulse, virus and damage code can request or directly set `otrub`.
- Virus writes `organism.pain` after core physiology, replacing the pain module's calculated value for that tick.
- Modes write persistent extensions such as `superfighter` and `recoilmul`; reset coverage is inconsistent outside `Org Clear`.
- Damage and medical code can mutate `o2`, `blood`, `heart`, `brain`, wounds and drugs between organism ticks.

## Physiology modules

| Module | Initialization / tick responsibility | Important integration risks |
|---|---|---|
| Blood | blood volume/type, wounds, arterial wounds, internal bleeding, coagulation, critical/incapacitated state | multiple wound loops; bleed is recalculated in stages; divide-by-zero/infinite time estimates; bone matrices/effects assumed valid |
| Pain | pain, shock, analgesia, drugs, disorientation, consciousness and fake/unconscious requests | competes with lung/virus/consciousness writers; thresholds are spread across modules |
| Pulse | heart damage, pulse/heartbeat, temperature, fear, cardiac arrest and agonal effects | broad cross-dependencies on blood/O2/brain/drugs/environment |
| Lungs | lungs, trachea, pneumothorax, oxygen, CO, holding breath and drowning/gas-mask behavior | uses current-character bones; breath commands and partial snapshots; writes consciousness |
| Stamina | sprint/movement drain, weight, adrenaline and max/regen | direct `FinishMove` hook; depends on armor, lungs, chest, hunger and player-class state |
| Metabolism | hunger, satiety, blood/health regeneration and starvation organ effects | directly changes entity health; disabled by default convar but schema remains active |
| Liver | initializes liver | tick is effectively empty and checks misspelled `hearstop` |
| Random events | sneeze/cough/burp/fart and virus/temperature sounds | many delayed callbacks capture players without complete validity/state checks |
| Virus | separate `ply.Virus` staged infection state, lung/brain/internal-bleed/O2/pain effects | not stored in organism; client stage packet has no located reader; assumes organism survives delayed callbacks |

## Custom organ geometry

`GetHitBoxOrgans(model, ent)` selects a female table for a fixed set of known female models and otherwise returns the male/default ValveBiped definition.

The definition maps bones to OBB records:

```text
{ organKey, protection/penetration value, localPosition, localAngle,
  halfExtents, debugColor [, requiresArmor] [, bodygroup/armor metadata] }
```

Verified organ regions include brain, skull, jaw, neck/spine, trachea, carotid and limb arteries, chest/ribs, lungs, heart, liver, stomach, intestines, pelvis and limb bones. Conditional pseudo-organs model armor such as HEV/combine/helmet coverage.

`ShootMatrix()` combines normal model hitboxes and custom organ OBBs for the current pose. `Trace()` steps a ray through those OBBs to determine hit order, penetration distance and input/output wounds. `BlastTrace()` applies a distance-based callback to every custom box.

### Geometric risks

- Only known ValveBiped-compatible skeletons are modeled; unknown models silently use the male/default layout.
- Missing bones/matrices are frequently skipped, producing model-dependent invulnerability or missing organs.
- Shared organ tables are mutated by adding conditional armor entries, making definition ownership/order important.
- `BlastTrace` divides damage by distance; an organ center at the blast origin can produce division-by-zero/infinite values.
- Penetration tracing uses capped distance/attempt counts and mutable shared vectors, requiring deterministic regression tests.

## Damage pipeline

The authoritative `EntityTakeDamage/homigrad-damage` hook in `sv_input.lua` performs the following broad flow:

1. Ignore unsupported targets/damage or redirect bullseye/fake-ragdoll damage.
2. Resolve player/ragdoll owner and organism.
3. Derive weapon/bullet penetration, diameter, ricochet and effect multipliers.
4. Build current custom organ OBBs.
5. Trace bullet/slash/club damage or blast intersections.
6. Invoke organ/bone/artery handlers from `hg.organism.input_list`.
7. Add wounds, pain, shock, immobilization, fear, adrenaline and internal damage.
8. Emit project hooks such as `PreHomigradDamage`, `PreHomigradDamageBulletBleedAdd` and `HomigradDamage`.
9. Apply physics forces, blood effects, possible continued bullet penetration and head/limb effects.
10. Scale ordinary engine damage heavily and schedule organism snapshots.

Collision damage is separately handled through `Ragdoll Collide`, player physics callbacks and `velocityDamage`, then feeds the same organ/bone state and damage hooks.

### Organ/bone input ownership

- `modules_input/sv_organs.lua`: heart, liver, stomach, intestines, brain, lungs, trachea and arteries.
- `modules_input/sv_bone.lua`: limbs, spine, jaw, skull/chest/pelvis, fracture/dislocation and crush amputation behavior.
- Other input files extend tissue, armor or special damage contracts and remain to be fully enumerated.

### Verified damage defects and hazards

1. Global `PenetrationGlobal` and `MaxPenLenGlobal` override one damage event and are then cleared; nested/reentrant damage can consume the wrong override.
2. The pre-damage hook call occurs before some local trace variables are initialized in the fetched lexical sequence, so consumers can receive nil/global values rather than final hit results.
3. `attacker.harm` is assigned/reset on entities that may be world/NPC/invalid without a normalized attacker-state contract.
4. Armor, inflictor, weapon, bullet, bone, matrix and current-character fields are repeatedly dereferenced without uniform guards.
5. Player damage is redirected to fake ragdolls, making duplicate or recursive damage suppression dependent on hook return semantics and entity identity.
6. `DMG_CRUSH` is returned early from the primary handler while collision damage is handled elsewhere; ordinary crush sources can bypass expected physiology depending on path.
7. Continued bullets mutate and reuse the original bullet table, then fire from an exit wound with modified filters and penetration counters.
8. Delayed wound/effect/replication timers capture entities and organism tables after owner transfer or removal.
9. Damage-type tests combine constants with arithmetic addition; behavior depends on non-overlapping bit flags and is difficult to audit.
10. Several handlers contain unreachable code or disabled behavior, including an unconditional return in trachea damage.
11. Liver damage calculates attacker harm before updating liver, producing zero harm from the current hit.
12. Bone handlers assume inflictor fields such as `RubberBullets`, `BreakBoneMul` and `Penetration` exist on a valid entity.
13. Break-neck/amputation paths assume translated bones and physics objects are valid before constraint operations.
14. Duplicate local calculations and commented alternatives make the effective damage equation hard to verify and easy to regress.

## Unconsciousness, fake and death

Core physiology calculates `needotrub` and `needfake`, then commits them to `otrub` and `fake` at the end of the tick.

Key gates include:

- blood thresholds;
- consciousness and pain/shock thresholds;
- spine/limb damage;
- oxygen/pulse/brain/heart state;
- stun and movement ability;
- amputation and mode/class extensions.

Transitions emit `HG_OnOtrub`, `HG_OnWakeOtrub` and `PlayerDropWeapon`. When fake/unconscious, `hg.Fake()` creates or retains the shared-state ragdoll. Organism death disables lungs, stops the heart and kills the owner when appropriate.

`sv_brainfuck.lua` adds fencing/spasm physics to the fake/death ragdoll for brain/skull/head damage and blocks get-up during active posturing.

## Replication contract

### `organism_send`

Server writes:

1. Lua table snapshot;
2. `bool force` (`owner.fullsend`);
3. `bool spectatorProtection`;
4. `bool moreInfo`;
5. `bool add/merge`.

The normal snapshot still contains dozens of scalar and nested fields, including owner entity, stamina, O2, wounds-relevant state, organs, limbs, drugs, temperature, movement and mode extensions. When `hg_developer` is enabled, the entire organism table is sent.

Two principal paths exist:

- owner/full information: approximately once per second for living players;
- PVS/bare information: approximately once per second for players and every three seconds for non-player/fake organisms, excluding the owner.

Immediate partial merge packets are also used for events such as holding breath and amputation.

### Client receive

`cl_statistics.lua` reads the table and booleans, stores `organism` and `new_organism`, merges partial updates, and mirrors both tables onto the fake ragdoll. Client UI then interpolates a large hard-coded field list.

### Replication defects and trust/performance risks

1. The client calls `ply:IsNPC()` before validating `org.owner`; malformed/stale entity references can error.
2. The client copies `ply.organism` before proving it exists and then assigns the copy back.
3. Schema is implicit Lua-table serialization with no version or field-count contract.
4. Developer mode can serialize the whole organism, including fields/entities/tables that are not safe or useful to clients.
5. PVS snapshots reveal physiological state of nearby entities without an explicit visibility/authorization model.
6. Server and client both maintain mutable old/new copies, creating aliasing and fake-ragdoll synchronization risks.
7. Large nested Lua tables are sent on fixed cadence per organism; bandwidth and encode/decode cost scale with players, NPC organisms and ragdolls.
8. `organism_sendply` is registered but its client reader is commented out.
9. Virus uses a separate `VirusStageUpdate` int8 packet; no client receiver was located in repository search.
10. Wounds and arterial wounds are also replicated through NetVars, creating overlapping state channels.

## Client presentation and local persistence

`cl_main.lua` uses organism state for unconsciousness DSP/sound fading, post-processing, blood/pain/oxygen effects and radial dislocation actions.

It also records periodic low-quality screenshots into client `data/dreams`, maintains an in-memory screen list, and deletes those images on local spawn, initialization and disconnect events. This behavior is presentation-only but is a persistent local-data side effect that should be documented and made optional before release.

The dislocation radial UI invokes the server console command:

```text
hg_fixdislocation <limb-group 1..3> <target-self-or-eye-trace 0|1>
```

The server checks alive/conscious/movement/pain/cooldown state, but target-other selection trusts the server eye trace without an explicit distance/line-of-sight cap beyond that trace, and numeric parsing can error when arguments are absent/non-numeric before `math.Round`.

Holding-breath commands are self-targeted and enforce organism/alive/stamina/O2/cooldown checks.

## Public hooks and APIs

### Core lifecycle hooks

- `Org Add(ent, org)`
- `Org Clear(ent, org)` / Tier 1 callback currently declares only one parameter and relies on actual emitted shape needing runtime confirmation
- `Org Think(owner, org, timeValue)`
- `Org Transfer(oldOwner, newOwner, org)`
- `Org Think Call(owner, org)`
- `HG_OnOtrub(player)`
- `HG_OnWakeOtrub(player)`
- `Should Fake Up(player)`
- `HomigradDamage(...)`
- `PreHomigradDamage(...)`
- `PreHomigradDamageBulletBleedAdd(...)`
- `OnAmputateLimb(org, ent, limb)`
- `Ragdoll Collide(ragdoll, data)`
- `RagdollDeath(player, ragdoll)`

### APIs

- `hg.organism.Add`, `Clear`, `Trace`, `BlastTrace`, `ShootMatrix`, `GetHitBoxOrgans`
- `hg.organism.input_list.*`
- `hg.organism.AmputateLimb`, wound APIs, oxygen/adrenaline helpers
- entity methods `AddOrganism`, `DelOrganism`, `HasOrganism`, `AddNaturalAdrenaline`
- `hg.send_organism`, `hg.send_bareinfo`
- `hg.BreakNeck`, `hg.ExplodeHead`

## Cross-system dependencies

| Consumer/producer | Coupling |
|---|---|
| Fake ragdoll | shared organism table, damage redirection, get-up gates, collision damage and post-death physics |
| Modes | `superfighter`, recoil, incapacitation/alive checks, role/loadout mutations, winner logic |
| Player classes | physiology modifiers, class conversion/assimilation, movement and random-event behavior |
| Weapons/bullets | penetration/diameter/multipliers, continued bullets, damage types and inflictor extensions |
| Armor | conditional organ hitboxes, gas protection, helmet/bone modifiers and dropped armor |
| Inventory/medical | wound/drug/organ state mutations and equipment assumptions |
| NPC/bots | organism attachment, fake-player behavior, damage and death handling |
| UI/spectator | replicated organism snapshots, health/status statistics and effects |
| Persistence/integrations | virus/class state, NetVars, client dream images and external hook consumers |

## Structural findings

1. **No explicit schema object:** state fields, default values, replication and client interpolation are duplicated across code.
2. **Shared mutable ownership:** player and ragdolls can point to one table without a formal owner-generation/token contract.
3. **Order-dependent physiology:** module/hook ordering materially changes values.
4. **Monolithic damage hook:** geometry, weapon penetration, organ damage, blood effects, physics, armor, headcrab logic and replication are combined.
5. **Overlapping replication:** snapshots, partial merges, NetVars and separate subsystem packets duplicate authority.
6. **Implicit extension fields:** modes/classes/weapons add arbitrary organism fields with inconsistent reset/cleanup.
7. **Unbudgeted cadence:** 10 Hz simulation plus per-organism Lua-table networking, effects and scans scale globally.
8. **Model assumptions:** ValveBiped and known model tables are treated as universal.
9. **Hook-shape ambiguity:** some callback signatures do not match Tier 0 emitter arguments by inspection and need runtime instrumentation.
10. **Failure is non-local:** one nil field or load-order error can break damage, fake ragdoll, movement and mode winner logic simultaneously.

## Required validation

### Startup and schema

- Record actual recursive load order on Windows/Linux dedicated servers.
- Assert Tier 0/Tier 1/module/input dependencies before hook registration.
- Generate and compare canonical default-field schema on every `Org Clear`.
- Verify player, NPC, fake ragdoll and death-ragdoll ownership transitions with disconnect/removal/hotload.

### Simulation

- Deterministic tests for module order and all death/unconscious/fake thresholds.
- Zero/max/extreme/NaN/infinite values for blood, bleed, O2, pulse, temperature and damage.
- Class/mode extensions through clear, spawn, fake, get-up, death and mode switch.

### Damage

- Every damage type against player, fake ragdoll, death ragdoll and supported NPC.
- Missing bones, non-ValveBiped models, armor combinations and invalid inflictors/attackers.
- Penetration/ricochet/reentrant damage and global override isolation.
- Bullet continuation and wound entry/exit correctness.
- Collision/crush path parity and duplicate damage suppression.
- Amputation, dislocation, break-neck and head explosion with missing physics objects.

### Replication

- Measure bytes/sec and encode/decode time across player/NPC/ragdoll populations.
- Capture every snapshot branch and partial merge; reject invalid owner/table shapes clientside.
- Version the schema and distinguish owner/private from observer/public fields.
- Verify PVS/spectator information exposure.
- Resolve/remove dormant `organism_sendply` and `VirusStageUpdate` protocols after external-consumer audit.

## Implementation boundary

Do not patch individual symptoms until the organism/fake-ragdoll/movement/player-class ownership map is complete. The eventual refactor should preserve gameplay behavior through an adapter while introducing:

1. one explicit schema/default registry;
2. one owner-generation/transfer contract;
3. deterministic module phases and priorities;
4. separated damage geometry, physiological mutation, effects and replication stages;
5. versioned delta replication with public/private field sets;
6. explicit extension registration for modes/classes/items;
7. performance budgets and instrumentation;
8. model-profile validation/fallbacks;
9. regression fixtures for every injury and lifecycle transition.

## Next trace

1. Finish remaining organism input/medical/client packet consumers and exact hook signatures.
2. Trace fake-ragdoll creation, ownership transfer, networking, input, get-up and combat.
3. Trace movement consumers of organism state and fake/unconscious transitions.
4. Trace player-class modifiers and reset contracts.
5. Produce the combined organism/fake-ragdoll/movement/class integration graph before implementation planning.
