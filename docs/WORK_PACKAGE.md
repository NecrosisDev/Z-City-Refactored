# Active Work Package

> This file contains only the current package and immediate continuation state. Completed detail belongs in commits, pull requests, issues, catalogs, tests, or decision records.

## Identity

- **ID:** `WP-DOCS-001`
- **Title:** Establish repository-local agent memory, knowledge, and regression contract
- **Branch:** `chore/agent-knowledge-contract`
- **Pull request:** `#2` (draft)
- **Status:** `validation`
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

## Validation

| Check | Result | Evidence |
|---|---|---|
| Canonical rules are repository-local | Pass | Root `AGENTS.md` |
| Every session has an explicit startup sequence | Pass | `AGENTS.md` and `docs/INDEX.md` |
| Conversation history is not required | Pass | Contract requires repository-complete handoff |
| Contract drift has a defined failure response | Pass | `AGENTS.md` contract-integrity section |
| Main branch modified | No | All changes remain on `chore/agent-knowledge-contract` |
| Runtime behavior modified | No | Markdown-only branch |
| Process/tooling bloat introduced | No | No service, hook, generator, CI, runtime dependency, or duplicate registry |
| Gameplay claims introduced | No | Catalogs remain evidence-gated templates |

## Risks and blockers

- The contract cannot govern agents operating from `main` until PR `#2` is reviewed and merged by an authorized user.
- Repository rules are advisory unless the agent follows startup instructions; later CI enforcement should be added only after a demonstrated compliance failure justifies it.
- The first real tracing package must test whether catalog templates provide sufficient detail without duplication.

## Exact continuation action

1. Finish aligning the pull-request checklist and PR `#2` description with the consolidated contract.
2. Re-compare the branch against `main` and verify all changes are Markdown-only and internally consistent.
3. Leave PR `#2` as a draft for user review; do not merge.
4. After authorized merge, branch from updated `main` for `WP-TRACE-001` and trace executable Lua bootstrap/load order, populating the first verified system entries with exact paths, realms, include order, hooks, dependencies, failure modes, and reproducible startup validation.
