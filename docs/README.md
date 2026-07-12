# Z-City Refactored Documentation

This directory is the maintained, code-grounded knowledgebase for the refactor.

## Documentation authority

Documentation describes the code at a named commit. When documentation and implementation disagree, the implementation is authoritative until the discrepancy is verified and corrected.

Each architecture document should record:

- the commit or branch reviewed;
- the relevant source paths;
- which statements are verified, inferred, or still unverified;
- known mismatches between comments, documentation, and runtime code;
- the next trace work required to complete the subject.

## Current documents

### Architecture

- [`architecture/PROJECT_SETUP.md`](architecture/PROJECT_SETUP.md) — repository layout, addon/gamemode split, namespaces, subsystem boundaries, persistence, dependencies, and structural risks.
- [`architecture/BOOTSTRAP_AND_LOAD_ORDER.md`](architecture/BOOTSTRAP_AND_LOAD_ORDER.md) — global addon bootstrap, gamemode bootstrap, Lua realm routing, recursive load order, mode registration, and round startup.

## Planned documents

The next documentation passes should cover:

1. complete loaded-file and realm manifest;
2. global symbol and public API registry;
3. hooks, network messages, console variables, and commands;
4. round lifecycle and mode catalog;
5. organism, fake-ragdoll, movement, and player-class systems;
6. weapons, physical bullets, armor, ammunition, and explosives;
7. inventory, equipment, appearance, and clothing;
8. NPC and bot architecture;
9. UI, HUD, camera, spectator, and screen effects;
10. persistence, administration, security, and external integrations.

## Suggested long-term structure

```text
docs/
├─ README.md
├─ architecture/
├─ systems/
├─ modes/
├─ integrations/
├─ operations/
└─ reference/
   ├─ FILE_MANIFEST.md
   ├─ GLOBAL_SYMBOLS.md
   ├─ HOOKS.md
   ├─ NETWORK_MESSAGES.md
   ├─ CONVARS_AND_COMMANDS.md
   ├─ DATA_FILES.md
   ├─ WEAPONS.md
   ├─ ENTITIES.md
   ├─ MODES.md
   └─ DEPENDENCIES.md
```

Avoid creating placeholder files before their contents have been verified against the code.