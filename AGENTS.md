# Agent Operating Contract

This repository is the canonical workspace for all ZCity Refactored agent work.

## Required workflow

1. Never commit directly to `main`; use a focused branch.
2. Read `docs/INDEX.md` and `docs/WORK_PACKAGE.md` before changing code.
3. Verify behavior from executable code; comments and legacy documentation are claims until confirmed.
4. Keep changes scoped to the active work package. Do not perform opportunistic rewrites.
5. Update the relevant catalog entry when behavior, public APIs, types, load order, networking, configuration, or ownership changes.
6. Add or update a regression check for every bug fix where practical.
7. Record unresolved assumptions, risks, and the next concrete action in `docs/WORK_PACKAGE.md` before handoff.
8. Commit messages must explain both what changed and why.

## Definition of done

A work package is complete only when implementation, validation, documentation impact, known limitations, and handoff state agree. If any item is unknown, mark it explicitly rather than guessing.
