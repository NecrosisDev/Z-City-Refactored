# Vanilla–Trauma Comparison Ledger

This ledger controls what enters the new project. It is intentionally decision-oriented rather than file-oriented.

## Decision states

| State | Meaning |
|---|---|
| Unreviewed | Attempt identified but not traced. |
| Keep vanilla | Vanilla behavior remains the preferred implementation. |
| Adopt | Trauma's concept and implementation are suitable with minimal integration work. |
| Adapt | A bounded portion can be integrated behind project APIs. |
| Rewrite | The requirement is valid but the implementation should not be carried forward. |
| Reject | The attempt is unnecessary, harmful, or outside project scope. |
| Blocked | More behavioral evidence or testing is required. |

## Review requirements

Each row must eventually link to:

- vanilla behavior documentation;
- current repository behavior;
- Trauma implementation evidence;
- observed defect or requirement;
- lifecycle and cleanup analysis;
- realm and networking analysis;
- performance implications;
- acceptance tests;
- an ADR when the decision is architecturally significant.

## Initial ledger

| Area | Trauma attempt | Preliminary concern | State |
|---|---|---|---|
| Boot/loading | Additional loaders and compatibility bootstraps | Overlapping initialization paths may load or register systems twice. | Unreviewed |
| Mode lifecycle | Explicit mode base and lifecycle ownership | Useful intent; implementation may intercept global hook/timer APIs and hide dependencies. | Rewrite candidate |
| Mode discovery | Structured mode directories and selection | Must preserve vanilla round behavior and avoid filename-order coupling. | Adapt candidate |
| Hook ownership | Associate registrations with active modes | Needed for cleanup, but global interception is high risk. | Rewrite candidate |
| Timer ownership | Cleanup mode timers on transition | Needed; anonymous `timer.Simple` ownership and delayed callbacks require explicit cancellation tokens. | Rewrite candidate |
| Registries | Active registry and subsystem registration | Must avoid becoming another mutable global table without validation or ownership. | Adapt candidate |
| Self-tests | Shared/server/client self-test modules | Registration checks are useful but cannot substitute for behavioral tests. | Adapt candidate |
| Spawn management | Spawn contracts and centralized spawn library | Must be compared against every vanilla mode's spawn/death/spectator flow. | Blocked |
| Organism | Expanded medical and organism behavior | High regression risk; vanilla damage semantics must be mapped first. | Blocked |
| Fake ragdoll | Extended fake/death/combat behavior | Core identity feature; preserve vanilla interaction and prediction before refactoring. | Blocked |
| Bots | Bot driver and mode behavior additions | Existing reports indicate immobility, aim, crouch, and objective-flow defects. | Rewrite candidate |
| Networking | Hundreds of messages and receivers | Ownership, validation, schema, and rate limits are not centralized. | Rewrite candidate |
| Optional adapters | Glide, VJ Base, Pathowogen, DynaBase, others | Adapters should detect capabilities and remain inert when dependencies are absent. Bundled vendor code should be separated. | Rewrite candidate |
| Minimap | Custom minimap libraries | Must prove gameplay value and stable cleanup; avoid mode-specific globals. | Unreviewed |
| Onboarding | Structured onboarding library | Concept is useful if content is data-driven and reflects actual mechanics. | Adapt candidate |
| Map tools | Mappoint and traitor/map compatibility tooling | Useful project goal; needs clear server authority and persistent schema. | Adapt candidate |
| Weapon balance | Centralized balance layer | Avoid runtime mutation of stock SWEP tables without ownership and deterministic reset. | Unreviewed |
| Client performance | Potato-PC and render-effect toggles | Useful where defaults remain visually correct and settings fail safely. | Adapt candidate |
| Content loading | Configurable Workshop loading | Current repository setting is ineffective; replace with a truthful content manifest. | Rewrite candidate |

## First decision boundary

No gameplay subsystem will be ported until the following vanilla flows are documented:

1. addon boot and load order;
2. gamemode selection and round lifecycle;
3. player initial spawn, spawn, death, fake death, spectating, and respawn;
4. organism initialization, damage, clearing, and death;
5. weapon deployment, aiming, obstruction, firing, and damage dispatch;
6. map cleanup and hot-reload behavior.

These flows form the behavioral spine. Porting higher-level features before them would reproduce Trauma's layering problems.