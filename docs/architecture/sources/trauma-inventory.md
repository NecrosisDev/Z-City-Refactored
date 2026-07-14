# Trauma Source Inventory

> Status: initial structural inventory. Counts are lexical and require semantic verification.

## Scope

The supplied `Trauma.zip` contains a Garry's Mod addon rooted at `TMod` with both a large `lua/homigrad` tree and a `gamemodes/trauma` implementation.

Initial scan:

| Metric | Count |
|---|---:|
| Lua files scanned | 1,009 |
| `hook.Add` calls | 1,144 |
| Distinct hook event names | 256 |
| `util.AddNetworkString` calls | 321 |
| `net.Receive` calls | 333 |
| ConVar creation calls | 351 |
| Timer creation/adjustment calls | 642 |
| Global table initializer patterns | 195 |

These counts demonstrate scale, not correctness. Dynamic registration, aliases, commented code, generated names, and wrappers require deeper review.

## Major implementation areas

### Shared addon systems

The `lua/homigrad` tree includes:

- achievements;
- administration and admin tools;
- bot driving;
- clothes and appearance;
- combatant logic;
- dynamic animation utilities;
- multiple music systems;
- explosives;
- fake-ragdoll behavior;
- HUD;
- inventory;
- movement;
- organism and medical behavior;
- Pathowogen integration;
- physical bullets;
- player classes;
- postmortem behavior;
- self-tests;
- VJ Base support;
- chat;
- manipulation and zombie systems.

### Gamemode systems

`gamemodes/trauma/gamemode` contains:

- core libraries;
- custom gamemode infrastructure;
- experience and guilt systems;
- map points and map tools;
- minimap;
- onboarding;
- RTV;
- spawn management;
- weapon balance;
- mode lifecycle and mode base layers;
- many game modes, including DM, TDM, HL2DM, Homicide, Defense, Riot, COOP, and Pathowogen-derived modes.

### Bundled or copied integrations

The archive includes substantial external or optional-system content, including:

- Glide entity bases and vehicle entities;
- vFire entities;
- wOS DynaBase content;
- VJ Base-facing code;
- Pathowogen-facing code;
- several adapter/loader files.

These must be separated into four categories during review:

1. original project code;
2. copied third-party code;
3. compatibility adapters;
4. modifications applied directly to vendor code.

Bundling and modifying optional dependencies directly is a major maintenance and conflict risk.

## Early lifecycle findings

The most frequently registered events include:

| Event | Registrations |
|---|---:|
| `Think` | 73 |
| `InitPostEntity` | 60 |
| `HUDPaint` | 48 |
| `PlayerDeath` | 31 |
| `PostCleanupMap` | 31 |
| `OnEntityCreated` | 30 |
| `Player Spawn` | 28 |
| `Org Think` | 28 |
| `Player_Death` | 26 |
| `radialOptions` | 25 |
| `PlayerInitialSpawn` | 23 |
| `Org Clear` | 22 |
| `Player Think` | 20 |
| `RenderScreenspaceEffects` | 19 |
| `PlayerSpawn` | 18 |
| `EntityTakeDamage` | 17 |
| `PlayerDisconnected` | 16 |
| `OnNetVarSet` | 16 |
| `ZB_PreRoundStart` | 16 |

The simultaneous use of names such as `PlayerSpawn`, `Player Spawn`, `Player_Death`, `PlayerDeath`, and project-specific event variants suggests multiple lifecycle dialects. Some may be intentional internal events; others may represent legacy duplication or compatibility layers. They must be traced before consolidation.

## Early networking findings

The lexical scan found network strings declared more than once, including:

- `projectileFarSound`;
- `select_mode`;
- `send_tourniquets`;
- `updtime`;
- `defense_commander_notification`.

Duplicate declarations are not automatically runtime failures in Garry's Mod, but they are evidence of unclear ownership. Each network message needs one documented owner, schema, direction, validation policy, and rate expectation.

The count mismatch between 321 declarations and 333 receivers also requires investigation. Potential explanations include engine-provided messages, conditional declarations, duplicate receivers, dynamic names, or missing declarations.

## Early architectural concerns

The archive appears to combine several generations of architecture:

- stock-style global `hg` systems;
- a custom Trauma gamemode layer;
- lifecycle ownership mechanisms;
- self-test systems;
- adapters;
- direct vendor copies;
- compatibility patches;
- legacy modes and newer replacements.

This can create the appearance of modularity while retaining hidden global coupling underneath.

Specific risks to verify:

1. Multiple loaders or initialization paths loading overlapping files.
2. Numeric or filename-based ordering substituting for declared dependencies.
3. Hook and timer ownership implemented by intercepting global APIs.
4. Legacy and replacement systems both remaining active.
5. Cleanup paths failing during round changes, map cleanup, hot reload, or disconnect.
6. Client files receiving server implementation details unnecessarily.
7. Network receivers trusting client-provided entities, identifiers, amounts, or state.
8. Optional integrations becoming hard dependencies because vendor code is bundled.
9. Self-tests validating registration rather than actual gameplay behavior.
10. Compatibility guards suppressing symptoms while leaving lifecycle defects unresolved.

## Concepts worth evaluating

The following Trauma concepts may be useful after comparison with vanilla:

- explicit mode lifecycle;
- registries with ownership metadata;
- deterministic mode discovery;
- cleanup-aware hook and timer ownership;
- optional adapters;
- spawn contracts;
- self-tests;
- onboarding and map tooling;
- network and dependency audits.

None are approved yet. Each needs a behavior comparison and an architectural decision record.

## Next analysis targets

1. Vanilla loader and initialization lifecycle.
2. Trauma loader and all secondary loaders.
3. Round/mode lifecycle from selection through cleanup.
4. Player spawn, death, fake death, spectating, and respawn flow.
5. Organism initialization and clearing.
6. Hook/timer ownership implementation.
7. Network registry and validation.
8. Third-party/vendor boundary inventory.