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

## Rejected approaches

The following are not justified for the refactor:

- porting Trauma folders or systems wholesale;
- making ULX/ULib, Glide, Dynabase, workshop assets, or a database mandatory for core startup;
- registering optional entities or animation sources before validating their complete dependencies;
- replacing vanilla behavior merely because Trauma contains a larger implementation;
- expanding audits or documentation without a named subsystem migration that consumes the result;
- enabling vehicle injury tuning before live server validation.

## Next bounded migration candidate

The strongest justified candidate is **optional integration hardening** because current Trauma runtime evidence shows concrete startup failures and dependency leakage. A future work order should select exactly one adapter, preserve vanilla behavior, define the complete required API surface, add inert fallback behavior, and test startup both with and without that dependency.

No production Lua behavior was changed by this document.