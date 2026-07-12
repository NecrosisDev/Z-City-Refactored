## What changed and why

Describe the verified problem or approved requirement, the change, and why this approach was chosen.

## Scope and evidence

- Work package: `WP-...`
- Branch: `...`
- Related systems/behaviors/types: `SYS-...`, `BEH-...`, `TYPE-...`
- Knowledge labels used: `Verified`, `Inferred`, `Legacy Claim`, `Planned`
- Exact evidence: files, symbols, tests, runtime reproduction, issues, or decisions

## Integration and validation

Describe affected layers, callers, consumers, data/control flow, networking, persistence, permissions, UI, load order, compatibility, performance, automated checks, manual checks, expected results, and actual results.

## Regression and handoff checklist

- [ ] I read `AGENTS.md`, `docs/README.md`, and `docs/WORK_PACKAGE.md` before working.
- [ ] Research stayed on `docs/architecture-baseline`, or a separate branch has an explicit justified reason.
- [ ] This change does not commit directly to `main` and contains no unrelated cleanup.
- [ ] Commit messages explain both what changed and why.
- [ ] Current behavior is evidence-backed; assumptions and plans are explicitly labeled.
- [ ] Bug fixes and changed contracts include regression checks where practical.
- [ ] Adjacent callers, consumers, hooks, shared state, network payloads, trust boundaries, load order, persistence, UI, permissions, compatibility, and performance were reviewed as applicable.
- [ ] Relevant architecture documents, catalogs, and decision records were updated atomically, or marked not applicable with a reason.
- [ ] Documentation names exact files, symbols, dependencies, invariants, edge cases, implementation order, acceptance criteria, and validation steps needed by the next agent.
- [ ] `docs/WORK_PACKAGE.md` records status, evidence, risks, blockers, dependencies, validation, and the exact continuation action.
- [ ] No duplicate process, abstraction, registry, report, index, generator, service, CI, hook, or runtime dependency was added without a demonstrated need.
- [ ] Local completion is not represented as full integration; remaining work is dependency-ordered and explicitly handed off.
- [ ] The change was not merged to `main` without explicit user authorization.