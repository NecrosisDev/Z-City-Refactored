# Agent Operating Contract

This repository is the canonical workspace for all ZCity Refactored agent work.

## Required workflow

1. Never commit directly to `main`; use a focused branch.
2. Read `docs/INDEX.md` and `docs/WORK_PACKAGE.md` before changing code.
3. Verify behavior from executable code; comments and legacy documentation are claims until confirmed.
4. Keep each individual change within a scope the active agent can safely implement and validate, but do not stop the broader work stream merely because one bounded change is complete.
5. Continue from the next unblocked work package until the requested system is fully integrated or progress is genuinely blocked by missing user input, inaccessible dependencies, or unavailable validation capability.
6. Update the relevant catalog entry when behavior, public APIs, types, load order, networking, configuration, ownership, or integration state changes.
7. Add or update a regression check for every bug fix and contract change where practical.
8. Write implementation documentation at handoff depth: identify exact files, symbols, dependencies, data flow, invariants, edge cases, acceptance criteria, validation steps, and integration order so the next agent performs minimal rediscovery or design inference.
9. Record unresolved assumptions, risks, evidence gaps, and the next concrete action in `docs/WORK_PACKAGE.md` before handoff.
10. Commit messages must explain both what changed and why.
11. End active sessions by arranging the next continuation step unless the requested system is fully integrated or further progress is blocked by required user input.

## Definition of done

"Work complete" means full system integration, not merely completion of a local edit, document, branch, or pull request. The requested system must be implemented across all required layers, validated against its acceptance criteria, documented to implementation-ready depth, checked for regressions, and left with no known unresolved integration gap; otherwise the next work package must be identified and continued.
