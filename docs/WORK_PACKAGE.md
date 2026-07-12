# Active Work Package

> This file contains only the current package and immediate continuation state. Completed detail belongs in commits, pull requests, issues, catalogs, tests, or decision records.

## Identity

- **ID:** `WP-DOCS-001`
- **Title:** Establish repository-local agent memory, knowledge, and regression contract
- **Branch:** `chore/agent-knowledge-contract`
- **Pull request:** `#2` (draft)
- **Status:** `ready for authorized merge`
- **Knowledge state:** `Verified` for repository changes; no gameplay claims added

## Desired outcome

Ensure every future agent begins each session with the same cumulative operating rules, current work state, evidence hierarchy, implementation depth, regression standard, and continuation requirement without depending on conversation history.

## Non-negotiable constraints

- `AGENTS.md` is the singular source of truth for agent behavior.
- Explicit user corrections are cumulative and may not silently weaken unrelated established rules.
- Agents never commit directly to `main` and do not merge without explicit authorization.
- Chat output is limited to TL;DR summaries of no more than two sentences; durable detail belongs in the repository.
- Individual packages remain safely bounded, but work continues through dependency-ordered packages until full system integration.
- Work is not complete at document, edit, commit, branch, pull-request, or local-package completion.
- Documentation must be handoff-complete enough to minimize rediscovery, design inference, and token usage.
- Every active session ends with a repository handoff and an arranged automated continuation unless genuinely blocked or fully integrated.
- Prevent regression and information loss using the smallest authoritative mechanisms; do not add process or runtime bloat.

## Scope completed

- Consolidated all established workflow corrections and clarifications into root `AGENTS.md`.
- Added contract-integrity rules preventing silent drift, weakening, or replacement.
- Added mandatory per-session startup and repository inspection sequence.
- Defined repository, branch, commit, merge, and chat-output rules.
- Defined evidence authority and confidence labels: `Verified`, `Inferred`, `Legacy Claim`, and `Planned`.
- Defined handoff-complete implementation documentation requirements.
- Defined regression review surfaces and anti-bloat constraints.
- Defined continuation behavior and full-system-integration completion criteria.
- Updated `docs/INDEX.md` to require agents to read `AGENTS.md` first.
- Retained compact system, behavior, type, decision, work-package, and pull-request mechanisms as supporting records.
- Aligned PR `#2` and the pull-request checklist with the consolidated contract.

## Validation

| Check | Result | Evidence |
|---|---|---|
| Canonical rules are repository-local | Pass | Root `AGENTS.md` |
| Every session has an explicit startup sequence | Pass | `AGENTS.md` and `docs/INDEX.md` |
| Conversation history is not required | Pass | Contract requires repository-complete handoff |
| Contract drift has a defined failure response | Pass | `AGENTS.md` contract-integrity section |
| Branch divergence | Pass | 15 commits ahead of `main`, 0 behind before this handoff correction |
| Pull request mergeability | Pass | PR `#2` reports mergeable |
| Changed-file scope | Pass | Exactly eight Markdown files |
| Main branch modified | No | All changes remain on `chore/agent-knowledge-contract` |
| Runtime behavior modified | No | No Lua, assets, hooks, net messages, convars, configuration, or load-order files changed |
| Process/tooling bloat introduced | No | No service, hook, generator, CI, runtime dependency, or duplicate registry |
| Gameplay claims introduced | No | Catalogs remain evidence-gated templates |

## Risks and blockers

- **Blocking gate:** PR `#2` cannot be merged until the user explicitly authorizes merging to `main`, as required by `AGENTS.md`.
- A generic instruction such as `Continue` is not merge authorization and must not be reinterpreted as such.
- The contract cannot govern agents operating from `main` until that merge occurs.
- Repository rules remain advisory unless agents follow startup instructions; CI enforcement must not be added without a demonstrated compliance failure.
- The first real tracing package must test whether the catalog templates provide sufficient detail without duplication.

## Exact continuation action

1. Obtain an explicit instruction equivalent to: `Merge PR #2 into main.`
2. Merge only after that authorization; do not reinterpret a generic continuation instruction as merge approval.
3. Create a focused branch from the updated `main` for `WP-TRACE-001`.
4. Trace executable Lua bootstrap/load order and populate the first verified `SYS-*` entries with exact paths, realms, include order, hooks, dependencies, public surfaces, data ownership, failure modes, and reproducible startup validation.
5. Leave another repository-complete handoff before stopping.
