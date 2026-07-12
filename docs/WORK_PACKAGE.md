# Active Work Package

> Keep this page limited to the current package. Preserve completed packages in issues, pull requests, or decision records rather than accumulating history here.

## Identity

- **ID:** `WP-DOCS-001`
- **Title:** Establish repository-local agent knowledge and regression contract
- **Branch:** `chore/agent-knowledge-contract`
- **Owner/agent:** OpenAI agent
- **Status:** `validation`

## Desired outcome

Provide a small, durable operating contract that lets future agents resume work from verified repository evidence, keep implementation scope explicit, and leave a reproducible handoff without introducing runtime dependencies.

## Creative and product constraints

- Documentation must remain concise enough to read at the start of every work session.
- Executable code and reproducible runtime evidence outrank inherited documentation and comments.
- The contract must not prescribe gameplay design that has not been verified or approved.
- The structure must work with ordinary Git and Markdown; no generator, service, hook, or external knowledge system is required.

## Scope

### Included

- Root agent operating rules.
- Canonical documentation index.
- Active work-package handoff format.
- System, behavior, and shared-type catalog templates.
- Architectural decision-record template.
- Pull-request regression and handoff checklist.
- Validation of branch scope and runtime non-impact.

### Excluded

- Runtime Lua changes.
- Claims about existing gameplay systems not traced from executable code.
- Full population of catalogs.
- Automated documentation generation or CI enforcement.
- Moving documentation to GitHub Wiki.

## Verified current behavior

- Pull request `#2` targets `main` from `chore/agent-knowledge-contract` and remains a draft.
- Before this update, the branch was eight commits ahead of `main`, zero commits behind, and changed only eight Markdown files.
- The branch introduces no Lua, asset, networking, hook, load-order, or configuration changes.
- Catalogs intentionally contain no project claims until executable code or reproducible runtime evidence is traced.

## Decisions

| Decision | Reason | Evidence/record |
|---|---|---|
| Keep canonical working documentation in the repository | Branches, reviews, and code changes must version documentation atomically; Wiki history cannot enforce that relationship | `AGENTS.md`, `docs/INDEX.md`, PR `#2` |
| Use stable IDs for systems, behaviors, types, and work packages | Agents need compact cross-references that survive file movement and implementation refactors | Catalog templates and PR template |
| Treat inherited documentation and comments as claims | Prevents stale notes from overriding executable behavior | `AGENTS.md`, `docs/INDEX.md` authority order |
| Avoid tooling or runtime dependencies | The first contract should reduce coordination cost without increasing build, server, or maintenance risk | Branch diff and PR scope |

## Changes completed

- Added `AGENTS.md` with required workflow and definition of done.
- Added `docs/INDEX.md` as the canonical documentation entry point.
- Added templates for system, behavior, and shared-type catalogs.
- Added the active work-package handoff format.
- Added lightweight architectural decision records.
- Added a pull-request regression and handoff checklist.
- Replaced the unassigned work-package template state with this active package record.

## Validation

| Check | Result | Evidence |
|---|---|---|
| Branch is based on current `main` | Pass | Comparison before this update: 0 commits behind |
| Changes are documentation/process only | Pass | PR `#2` changed-file list contains only Markdown files |
| Runtime behavior changed | No | No Lua, assets, hooks, net messages, convars, or load-order files changed |
| Catalog claims are evidence-gated | Pass | Each catalog begins empty and requires paths, symbols, validation, commit, and date |
| Handoff has an executable next action | Pass | See next section |
| Runtime smoke test | Not applicable | No executable files changed |

## Risks and unresolved questions

- The contract remains advisory until reviewers consistently require it or later CI checks are deliberately added.
- Stable ID naming conventions may need refinement after the first real system-tracing package.
- Catalog templates may be too broad or too narrow; adjust only from observed use, not speculation.
- The repository currently has no verified subsystem catalog entries, so future work still requires initial code tracing.

## Next concrete action

After this pull request is reviewed and merged, create a focused branch for `WP-TRACE-001` and trace the repository bootstrap/load order from executable Lua. Populate the first `SYS-*` entries with exact paths, realms, include/autorun order, public hooks, dependencies, and a reproducible server-start validation procedure. Do not document gameplay intent during that package unless runtime evidence verifies it.
