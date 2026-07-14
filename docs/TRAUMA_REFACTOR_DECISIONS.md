# Trauma-to-ZCity Refactor Decision Register

Baseline: Z-City `main` at `429ec928203cec963176dfb6afd086dcdd01c181`.

Purpose: record only decisions that are supported by inspected source artifacts or observed Trauma runtime output. This is not a feature backlog and does not authorize broad ports.

## Decision rule

A Trauma change is retained only when it provides a specific benefit over vanilla Z-City and can be reimplemented without replacing working vanilla ownership. Otherwise, vanilla behavior remains authoritative.

## Verified decisions

### TZ-001 — Optional integration boundaries

**Trauma intent:** integrate external systems such as Glide, ULX/ULib, Dynabase, and other addons.

**Observed problem:** Trauma emits repeated dependency warnings and can load partial vendor surfaces when required APIs, models, or server-side workshop content are absent. Runtime output includes missing Glide APIs, a Dynabase nil-model failure, repeated ULX/ULib warnings, and entity bases refusing to load.

**Vanilla baseline:** vanilla Z-City does not require these integrations to establish its core damage/control behavior.

**Decision:** retain the integration goal, reject hard coupling. Every external integration must:

- detect the complete API surface it actually uses;
- remain inert when unavailable;
- avoid registering broken derived entities or animation sources;
- expose one ZCity-owned adapter boundary;
- never become a prerequisite for core ZCity startup.

**Status:** approved concept; implementation must be adapter-specific and separately tested.

### TZ-002 — Asset and model validation before registration

**Trauma intent:** expand character models, animation sources, particles, and effects.

**Observed problem:** runtime output reports missing player models, missing particle collections, a missing Dynabase pointer model, invalid studio headers, and fake-ragdoll code receiving a model without a usable head physics object.

**Vanilla baseline:** vanilla behavior assumes its shipped/default asset set and should remain usable without Trauma-only assets.

**Decision:** retain expanded content support only behind validation. Registration must verify models, particles, entity bases, and required physics bones before activation. Invalid optional content is skipped with one actionable diagnostic; it must not poison the base system.

**Status:** approved concept; no asset is approved for import by this decision.

### TZ-003 — Vehicle-to-organism impact context

**Trauma intent:** connect vehicle damage/crashes to organism and medical behavior.

**Evidence from prior implementation work:** the useful portion can be represented as occupant-aware impact context, with gameplay wounds disabled until live tuning is validated. The prior bridge design also identified a need for stale occupant/damage cleanup and seatbelt-aware scaling.

**Vanilla baseline:** preserve vanilla vehicle entry, exit, damage, and organism behavior until a ZCity-owned bridge is proven.

**Decision:** retain the gameplay concept, not the prior architecture. The eventual implementation should observe canonical ZCity vehicle events, produce a bounded impact record, and pass that record to the organism system. It must not directly depend on Glide internals and must default to non-invasive diagnostics until live acceptance succeeds.

**Status:** approved design concept; not approved for gameplay activation.

### TZ-004 — Database-backed progression and achievements

**Trauma intent:** persist achievements and other server data.

**Observed behavior:** Trauma establishes database connections during startup.

**Vanilla baseline:** core Z-City gameplay must not depend on an external database.

**Decision:** persistence may be retained as an optional service, but round flow, spawning, organism state, and core gameplay must remain functional when persistence is disabled or unavailable. Startup failures must degrade to non-persistent operation.

**Status:** approved constraint; specific schemas and progression behavior remain unreviewed.

### TZ-005 — Network inventory as a migration guardrail

**Trauma intent:** synchronize expanded gameplay and integration state.

**Risk:** copying Trauma networking wholesale would also copy duplicate ownership, stale state paths, and vendor-specific protocol surfaces.

**Vanilla baseline:** existing vanilla messages remain authoritative until a specific subsystem is migrated.

**Decision:** maintain an offline inventory of network strings, receivers, and networked variables only to support a named migration. It is not an independent workstream. Each migrated subsystem must identify authority, sender validation, rate limits, lifecycle cleanup, late-join behavior, and compatibility requirements before changing its protocol.

**Status:** approved guardrail; broad network tooling expansion is explicitly out of scope.

### TZ-006 — Current repository is the vanilla implementation baseline

**Verified current branch state:** `README.md` identifies the connected repository as Z-City 1.4.0 and describes the stock addon/gamemode. The prior refactor artifact set references a separate `lua/zcity/systems/...` architecture, including a singular vehicle facade and medical vehicle-trauma bridge, but representative files from that architecture are absent from the connected `main` branch.

**Trauma/refactor evidence available:** previous generated artifacts document intended systems such as `zb.Vehicle`, canonical vehicle runtime hooks, optional Glide compatibility, and a diagnostic-first vehicle medical bridge. Those artifacts are evidence of attempted design work, not proof that the implementation exists in this repository.

**Vanilla baseline:** the code presently on `main` remains the only verified executable baseline in the repository. Documentation must not claim that artifact-only systems are implemented, tested, or available here.

**Decision:** treat prior refactor artifacts as a concept inventory only. Before refining any concept into production code:

- identify the exact vanilla files that own the behavior;
- identify the exact Trauma change being considered;
- verify whether any equivalent implementation already exists on the current branch;
- define a bounded destination inside the current repository structure;
- add the smallest implementation that preserves vanilla behavior;
- distinguish static validation from live Garry's Mod testing.

Do not recreate the previous broad facade/registry architecture merely because it appears in archived diffs or handoff files. Each architectural element must independently justify its cost against a concrete migration.

**Status:** verified repository boundary; supersedes any prior implication that the archived refactor implementation is already present on `main`.

## Rejected approaches

The following are not justified for the refactor:

- porting Trauma folders or systems wholesale;
- making ULX/ULib, Glide, Dynabase, workshop assets, or a database mandatory for core startup;
- registering optional entities or animation sources before validating their complete dependencies;
- replacing vanilla behavior merely because Trauma contains a larger implementation;
- expanding audits or documentation without a named subsystem migration that consumes the result;
- enabling vehicle injury tuning before live server validation;
- treating archived generated diffs, ZIP handoffs, or guidestones as current repository implementation;
- rebuilding the entire prior refactor scaffolding before a concrete gameplay migration requires it.

## Next bounded migration candidate

The next implementation must begin from one verified vanilla owner file on the current branch. The strongest candidate remains optional integration hardening, but no adapter should be written until its actual vanilla interaction point and Trauma counterpart are both identified. The deliverable should be one dependency-safe adapter or one explicit rejection decision—not another general inventory framework.

No production Lua behavior has been changed by this decision register.