# ZCity Refactored Agent Contract

This file is the singular source of truth for how every agent works in this repository. Read it in full at the start of every session and before selecting, planning, reviewing, or implementing any work package.

## Contract integrity

- Preserve every rule in this file across all work packages and sessions.
- User corrections and clarifications are cumulative and supersede only the specific earlier statement they correct; never silently reinterpret, weaken, omit, or replace unrelated rules.
- Do not edit this contract for convenience, local optimization, or agent preference. Change it only to record an explicit user correction or clarification, preserving prior intent and documenting why.
- If this contract is missing, materially contradictory, or known to have drifted from the user's established instructions, stop implementation and report that the canonical workflow must be reconstructed; do not invent a replacement.
- The repository is durable memory. Chat history may provide context, but no agent may depend on unavailable conversation history to resume work.

## Mandatory session startup

1. Read this file.
2. Read `docs/README.md` and `docs/WORK_PACKAGE.md`.
3. Inspect the active branch, latest relevant commits, open pull request, validation state, and unresolved handoff items.
4. State the current work package and ask only questions necessary to resolve the user's desired outcome or creative vision.
5. Continue from verified repository state without restarting completed analysis or relying on undocumented assumptions.

## Repository workflow

- `NecrosisDev/Z-City-Refactored` is the canonical workspace for all agent output.
- Never commit directly to `main`.
- During the current project-research and documentation-baseline phase, use `docs/architecture-baseline` as the single continuous working branch and PR `#1` as the single review surface. Do not create a branch per work package.
- Create another branch only when the user explicitly requests it or when implementation/experimentation must be independently reviewed, validated, reverted, or shipped; first confirm that no existing active branch already covers the work.
- Keep each work package within a scope the current agent can safely complete and validate, but record and continue the next dependency-ordered package on the same research branch until the research baseline is complete.
- Commit messages must describe both what changed and why it was necessary.
- Store detailed work, evidence, implementation guidance, decisions, validation, and handoff state in the repository. Chat responses must be TL;DR summaries of no more than two sentences.
- Do not merge to `main` unless the user explicitly requests or authorizes it. Lack of merge authorization is not a blocker to continued research on the active branch.

## Evidence and knowledge rules

- Reproducible runtime evidence and tests outrank executable code; executable code outranks catalogs and decision records; verified repository documentation outranks comments, historical notes, and inherited documentation.
- Comments and legacy documentation are claims until verified against executable code or reproducible behavior.
- Mark knowledge as `Verified`, `Inferred`, `Legacy Claim`, or `Planned`; never present inference or intent as current behavior.
- Maintain lightweight living indexes of systems, behaviors, shared types, ownership, dependencies, initialization order, runtime flow, public contracts, networking, configuration, and integration state.
- Update affected catalogs and decision records atomically with research or implementation changes. Do not create speculative entries merely to fill documentation.
- Prefer compact Markdown and existing repository mechanisms. Add automation, CI, generators, hooks, or runtime systems only when they prevent a demonstrated regression or coordination failure and their maintenance cost is justified.

## Implementation and handoff depth

Documentation must be handoff-complete: another capable agent with no chat history must be able to implement or continue the work with minimal rediscovery and minimal design inference. Where applicable, record:

- exact files, paths, symbols, realms, owners, and entry points;
- verified current behavior and evidence;
- desired behavior and approved design rationale;
- prerequisites, dependencies, integration order, and migration constraints;
- public interfaces, data contracts, invariants, preconditions, and postconditions;
- control flow, data flow, lifecycle, networking, replication, trust boundaries, persistence, and configuration;
- edge cases, failure modes, compatibility constraints, security concerns, and performance implications;
- independently executable implementation steps;
- automated and manual validation procedures with expected results;
- regression risks, acceptance criteria, known limitations, unresolved evidence gaps, and the exact next action.

## Regression prevention

- Add or update a regression check for every bug fix and contract change where practical.
- Before handoff, review adjacent callers, consumers, hooks, network payloads, shared state, load order, persistence, UI, permissions, and compatibility surfaces affected by the change.
- Do not treat a local pass as integration success. Validation must cover the required layers and interactions for the requested system.
- Do not bloat the project with duplicate abstractions, reports, registries, indexes, or tooling. Extend the smallest authoritative mechanism that closes the demonstrated gap.

## Continuation and completion

- Work may span multiple responses and sessions. Continue for as long as practical, then leave a repository-complete handoff and arrange the next automated continuation step.
- Do not stop because a document, edit, commit, branch, pull request, or bounded work package is locally complete. Select the next unblocked dependency-ordered package and continue.
- Stop only when required user input, inaccessible dependencies, unavailable validation capability, or a safety constraint genuinely blocks further progress; document the blocker and the exact decision or resource needed.
- `Work complete` means full system integration: all required layers are implemented, validated against explicit acceptance criteria, documented at handoff depth, regression-reviewed, and free of known unresolved integration gaps.
- Until full integration is achieved, `docs/WORK_PACKAGE.md` must identify the active or next work package, evidence state, risks, dependencies, validation status, and exact continuation action.