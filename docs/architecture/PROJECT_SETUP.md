# Z-City Refactored Project Setup

**Repository:** `NecrosisDev/Z-City-Refactored`  
**Branch reviewed:** `main`  
**Source commit:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** Initial code-grounded architecture baseline  
**Reviewed:** 2026-07-12

## Purpose

This document establishes the first verified map of how the project is arranged. It describes repository layout, runtime entry points, subsystem boundaries, persistence, bundled integrations, and structural risks.

It is not yet a complete behavioral specification. Organism simulation, fake ragdolls, weapons, inventory, NPCs, networking, UI, and individual modes require dedicated trace documents.

## High-level architecture

Z-City is both:

1. a globally loaded Garry's Mod addon under `lua/`; and
2. a selectable Sandbox-derived gamemode under `gamemodes/zcity/`.

```text
Garry's Mod
├─ Global addon layer
│  └─ lua/autorun/loader.lua
│     ├─ recursively loads lua/homigrad/
│     └─ loads lua/initpost/ during InitPostEntity
│
└─ Z-City gamemode layer
   └─ gamemodes/zcity/
      ├─ zcity.txt
      └─ gamemode/
         ├─ shared.lua
         ├─ init.lua
         ├─ cl_init.lua
         ├─ loader.lua
         ├─ libraries/
         └─ modes/
```

The addon layer supplies most shared gameplay systems, weapons, entities, character simulation, inventory, presentation, and integrations. The gamemode layer supplies round orchestration, mode registration and selection, teams, map points, spectators, scoring, and mode-specific behavior.

## Repository layout

```text
Z-City-Refactored/
├─ .github/
├─ data_static/
│  └─ glide/
├─ docs/
├─ gamemodes/
│  └─ zcity/
├─ lua/
├─ .gitignore
├─ LICENSE
└─ README.md
```

### `lua/`

```text
lua/
├─ autorun/
├─ bin/
├─ effects/
├─ entities/
├─ glide/
├─ homigrad/
├─ includes/modules/
├─ initpost/
├─ weapons/
├─ wos/dynabase/
├─ glide_helicopters_source.txt
├─ glide_source.txt
├─ vfire_source.txt
└─ wos_source.txt
```

The source-attribution files and dedicated Glide, DynaBase, and fire-related paths show that first-party code, adapted code, and bundled third-party systems coexist inside one addon tree.

### `gamemodes/zcity/`

```text
gamemodes/zcity/
├─ entities/
├─ gamemode/
│  ├─ libraries/
│  ├─ modes/
│  ├─ cl_init.lua
│  ├─ init.lua
│  ├─ loader.lua
│  └─ shared.lua
├─ icon24.png
├─ logo.png
└─ zcity.txt
```

The descriptor registers `ZCity` in the `pvp` category and associates it with several map-name patterns, including `hmcd`, `md`, `mu`, `murder`, `zc`, and `zb`.

## Global addon layer

The primary entry point is:

```text
lua/autorun/loader.lua
```

It initializes the `hg` namespace, defines realm-aware loading, recursively loads `lua/homigrad/`, marks `hg.loaded`, runs the `HomigradRun` hook, and later loads `lua/initpost/` from `InitPostEntity`.

The loader skips the project when the active gamemode is `ixhl2rp`. It also warns when ULX/ULib is unavailable and when the game is running in single-player.

The global loader currently reports:

```lua
hg.Version = "Release 1.4.1"
```

The root README reports `1.4.0`; neither value should be treated as canonical until version ownership is formalized.

## Deferred initialization

`lua/initpost/` is loaded after entity initialization and currently contains UI/Derma setup, skins, atlases, and shared/server post-initialization files.

```text
lua/initpost/
├─ menu-n-derma/derma/
├─ cl_atlases.lua
├─ cl_derma_skin.lua
├─ cl_derma_skin_hokmah.lua
├─ sh_initpost.lua
└─ sv_initpost.lua
```

Subsystem documents must state whether their APIs are available during the initial addon load, after `HomigradRun`, or only after `InitPostEntity`.

## Gamemode layer

`gamemodes/zcity/gamemode/shared.lua` derives from Sandbox:

```lua
DeriveGamemode("sandbox")
```

The shared gamemode currently:

- defines custom teams at indices `0`, `1`, and `2`;
- restricts Sandbox spawning to administrators;
- restricts noclip to administrators;
- blocks the spawn menu for ordinary players;
- provides helpers for collecting playing, alive, and team-grouped players.

The server entry point includes `shared.lua` and `loader.lua`, and sends the client files. The client entry point includes the same shared and loader files. Both realms therefore build their mode registries through the gamemode loader.

## Mode architecture

The gamemode loader first loads `gamemode/libraries/`, then scans `gamemode/modes/`.

For each mode it:

1. creates a temporary global `MODE` table;
2. includes the mode's realm files;
3. optionally inherits from a previously registered base mode;
4. stores the mode under `zb.modes[MODE.name]`;
5. registers functions found on the mode table through the mode hook dispatcher;
6. clears the temporary global.

Mode directories generally contain:

```text
modes/<mode>/
├─ cl_<mode>.lua
├─ sh_<mode>.lua
└─ sv_<mode>.lua
```

Current mode directories include:

```text
coop
criresp
defense
dm
eventhandler
gwars
hl2dm
homicide
homicide_fear
pathowogen
riot
scugarena
sfd
tdm
tdm_cstrike
```

Directory presence does not prove that a mode is stable, reachable, or feature-complete.

## Shared gamemode libraries

The gamemode library layer includes infrastructure for:

- round orchestration;
- team setup and balancing;
- map-point definitions and lookup;
- map voting and RTV;
- roles;
- experience;
- guilt;
- loot spawning;
- mode-selection UI;
- admin commands and tools.

Current paths include:

```text
gamemodes/zcity/gamemode/libraries/
├─ !core/
├─ experience/
├─ guilt/
├─ mappoints/
├─ rtv/
├─ cl_modeselect_menu.lua
├─ cl_scrappersfonts.lua
├─ sh_giverole.lua
├─ sh_pluvis.lua
├─ sh_simplex.lua
├─ sh_ulxcommands.lua
├─ sv_admin_tools.lua
├─ sv_antiafk.lua
├─ sv_lootspawn.lua
├─ sv_roundsystem.lua
└─ sv_teamsetup.lua
```

## Global gameplay systems

Major `lua/homigrad/` directories include:

```text
abnormalty_detection
achievements
adminsystem
admintools
clothes
dynamic_anims_util
dynamic_music_v2
dynmusic
explosives
fake
gunposmenu
headgib
hud
libraries
liquidystuff
movement
new_appearance
new_inventory
optionsmenu
organism
pathowogen
phys_bullets
phys_silk
playerclass
playermodel_selector
pluvtown
roleplus
synthesizer
z_box_systems
zchat
zmanip
```

For documentation purposes, these should be grouped by responsibility rather than preserving the current folder layout as the architecture model.

### Character simulation

- organism;
- fake ragdolls;
- movement;
- player classes;
- appearance and clothes;
- head and bone handling.

### Combat

- physical bullets;
- explosives;
- armor and ammunition;
- attachments;
- weapon bases;
- damage integration.

### Inventory and equipment

- new inventory;
- legacy/shared inventory code;
- equipment rendering;
- armor, ammunition, and attachment entities.

### Presentation

- HUD;
- camera and TPIK;
- screen effects;
- dynamic music;
- UI and options;
- notifications and chat.

### Administration and services

- admin systems and tools;
- achievements;
- roles;
- abnormality detection;
- persistence and database helpers.

### AI and world integration

- NPC utilities;
- pathowogen;
- vehicle systems;
- Glide;
- fire/vFire-derived code;
- DynaBase.

## Weapons and entities

Large content registries exist under:

```text
lua/entities/
lua/weapons/
```

Important bases include:

```text
lua/weapons/homigrad_base/
lua/weapons/weapon_base/
lua/entities/ammo_base/
lua/entities/armor_base/
lua/entities/attachment_base/
lua/entities/ent_throwable/
```

A later content manifest should classify each registered class as a base, concrete item, compatibility adapter, third-party component, mode-specific object, utility, deprecated class, or clientside helper.

## Bundled and external components

The repository visibly contains or references:

- Glide and related GTA V vehicle/helicopter content;
- wOS DynaBase;
- vFire-derived or adapted fire code;
- the compiled `eightbit` server module;
- optional Discord Rich Presence modules;
- ULX/ULib integration.

Compiled modules currently include:

```text
lua/bin/gmsv_eightbit_linux.dll
lua/bin/gmsv_eightbit_win32.dll
lua/bin/gmsv_eightbit_win64.dll
```

Dependency documentation must distinguish bundled code, modified third-party code, required addons, optional addons, binary modules, Workshop content, and features that silently degrade when a dependency is absent.

## Namespaces and global state

Primary globals include:

| Symbol | Current responsibility |
|---|---|
| `hg` | Homigrad/Z-City systems and shared APIs |
| `zb` | Gamemode, mode registry, and round state |
| `MODE` | Temporary mode assembly table |
| `GM` | Garry's Mod gamemode table |
| `CurrentRound()` | Current-mode resolver |
| `NextRound()` | Future-mode selector |

A global-symbol registry is required because ownership, initialization order, and mutation sites are not consistently visible from names alone.

## Persistence

Confirmed runtime data paths include:

```text
data/zbattle/modeschances.json
data/zbattle/mapsizes.json
```

The packaged `data_static/` directory is distinct from Garry's Mod's writable runtime `DATA` realm. A full persistence audit must inventory file writes, SQL calls, serialized player data, achievement storage, configuration, and cleanup behavior.

## Confirmed structural risks

1. **Two loaders with different rules.** Moving a file between addon and gamemode trees can change its realm and execution order.
2. **Implicit load order.** Neither loader explicitly sorts `file.Find` results.
3. **Shared-by-default addon files.** Unmarked Lua files under `lua/homigrad/` execute as shared code.
4. **Temporary global mode assembly.** `MODE` is mutable global scratch state.
5. **Mode functions become hook candidates.** Helper methods and engine hook handlers share one table.
6. **Stale round-state comments.** Comments describe end state `2`, while runtime code uses `3`.
7. **Version mismatch.** The loader and README disagree.
8. **Mixed code ownership.** First-party, adapted, bundled, and external systems are not separated by a formal manifest.
9. **Large entry files.** `gamemode/init.lua` and especially `cl_init.lua` contain behavior beyond bootstrap responsibilities.

## Next trace work

The next pass should produce:

1. a complete loaded-file and effective-realm manifest;
2. explicit initialization phases and load-order dependencies;
3. global symbol definitions and mutation sites;
4. all startup hooks and network strings;
5. required and optional dependencies;
6. a verified round lifecycle;
7. a mode-by-mode catalog;
8. subsystem documents built on the resulting bootstrap baseline.
