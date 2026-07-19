# Trauma Lifecycle Assessment

**Source snapshot:** `Trauma.zip`

- SHA-256: `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652`
- Archive size: 4,425,563 bytes
- Extracted Lua files: 1,028
- Extracted Lua source size: approximately 8.62 MB

**Status:** Static assessment. Trauma is evidence and prototype material, not an authoritative implementation.

## 1. Problem Trauma attempts to solve

Vanilla/current Z-City dispatches active mode methods selectively, but mode files can register hooks, timers, network handlers, globals, and other side effects during load. Those side effects are not inherently scoped to the active mode.

Trauma attempts to add:

- deterministic loading;
- active-mode ownership;
- hook/timer teardown on mode change;
- runtime registration tracking;
- generation guards for stale callbacks;
- lifecycle diagnostics;
- explicit activation/deactivation events;
- composed ownership across inherited modes.

The problem is real. The implementation should not be adopted wholesale.

## 2. Primary implementation

Main source:

`gamemodes/trauma/gamemode/libraries/sh_mode_lifecycle.lua`

The lifecycle manager stores:

- mode definitions;
- active mode;
- static hook and timer registrations;
- runtime hook and timer registrations;
- a lifecycle generation counter;
- a list of persistent hook events exempted from active-mode ownership.

It supports:

- `RegisterMode`;
- `Activate`;
- `Deactivate`;
- `CallModeMethod`;
- `RunOwned`;
- composed base/derived definitions;
- a status console command.

## 3. Useful concepts

### 3.1 Generation tokens

Callbacks are associated with a lifecycle generation. A stale callback can check that the active mode and generation still match.

**Disposition:** Adopt the concept.

Generation tokens are simple, cheap, and useful for delayed callbacks, asynchronous completions, and mode transitions.

### 3.2 Explicit activation and deactivation

Trauma creates explicit mode activation/deactivation operations and diagnostics.

**Disposition:** Adapt.

The future system should expose formal phases such as registered, activating, active, deactivating, and inactive. The current Trauma event names and global placement should not define the final API.

### 3.3 Ownership records

Static and runtime hooks/timers are tracked so they can be removed when a mode deactivates.

**Disposition:** Rewrite.

Ownership is required, but it must be declared through project APIs rather than inferred by replacing Garry's Mod globals.

### 3.4 Base/derived composition

Trauma composes registrations from base modes and derived modes, with child entries replacing identical base event/identifier pairs.

**Disposition:** Adapt after verifying current inheritance behavior.

This may be useful, but executable inheritance should be explicit and separately testable from configuration inheritance.

### 3.5 Status diagnostics

The lifecycle status command reports active mode, generation, and owned hook/timer counts.

**Disposition:** Adopt and broaden.

Future diagnostics should also report owner, source path, realm, activation phase, replacement history, and leaked resources.

## 4. Critical implementation flaws

### 4.1 Global API interception

`RunOwned` temporarily replaces:

- `hook.Add`;
- `timer.Create`;
- `timer.Simple`.

This is the most serious flaw.

Risks:

- unrelated code running in the same call stack is attributed to the current mode;
- nested ownership contexts can restore the wrong function if reentrancy is mishandled;
- coroutine or callback boundaries are not represented accurately;
- addons caching the original functions bypass tracking;
- addons inspecting or wrapping the functions observe temporary replacements;
- runtime errors between replacement and restoration are dangerous despite `xpcall`;
- behavior differs from normal Garry's Mod semantics during the wrapped call;
- only selected APIs are intercepted, producing false confidence about ownership.

**Disposition:** Reject.

Global monkey-patching must not be part of the production architecture.

### 4.2 Incomplete ownership surface

The system tracks some hooks and timers but not all resources modes may create, including:

- `net.Receive` handlers;
- concommands;
- entity callbacks;
- global variables;
- file writes;
- cleanup registrations;
- custom registries;
- spawned entities;
- `timer.Adjust`, `timer.Pause`, or external scheduler APIs;
- callbacks registered through cached function references.

**Disposition:** Rewrite around explicit resource scopes.

### 4.3 `timer.Simple` is guarded, not owned

A simple timer has no caller-provided name, so Trauma wraps its callback with an active-generation check. The timer still exists until execution.

Consequences:

- deactivation does not cancel the scheduled work;
- captured objects remain referenced until the timer fires;
- diagnostics cannot enumerate or remove it;
- high churn can accumulate dormant callbacks.

**Disposition:** Replace with an owned delayed-task API that assigns internal IDs and supports cancellation.

### 4.4 Identifier collision can remove unrelated resources

Activation and deactivation remove hooks by event and identifier and timers by name. If another subsystem uses the same pair/name, the lifecycle manager can remove or replace it.

**Disposition:** Require namespaced identifiers generated from owner plus local ID, with explicit replacement rules.

### 4.5 Persistent-hook allowlist is too broad and implicit

Bootstrap and cleanup events are exempted globally through a hard-coded list. A mode registration on one of those events remains global even if it is mode-specific.

**Disposition:** Reject implicit event-based persistence. Persistence must be declared per registration and reviewed.

### 4.6 Static capture changes load semantics

The loader captures mode registrations rather than allowing all direct registrations to behave normally. This can delay registration, suppress initialization side effects, or change replacement order.

**Disposition:** Use capture only as a temporary audit/migration tool, never as the final runtime mechanism.

### 4.7 Two dispatch models coexist

Trauma retains the legacy `zb.modesHooks` active-mode dispatcher while adding lifecycle-managed direct hook ownership. These models overlap and can create:

- duplicate callbacks;
- unclear precedence;
- mismatched return propagation;
- difficult hot-reload behavior;
- mode methods being both utility methods and hook handlers.

**Disposition:** Do not run both as permanent architecture. Build a compatibility bridge with one authoritative dispatcher.

### 4.8 Trauma-specific global naming

Events and commands use names such as `TraumaModeActivated` and `trauma_mode_lifecycle_status` inside a project intended to become Z-City Refactored.

**Disposition:** Rename only after behavior is verified; do not bake prototype naming into the public API.

## 5. Related Trauma lifecycle concepts

### Active registry

`lua/homigrad/libraries/core/sh_active_registry.lua` implements dense registries using an array plus reverse-position map, swap-removal, validation, pruning, metrics, and entity auto-removal.

Strengths:

- efficient dense iteration;
- constant-time membership and removal;
- explicit count;
- optional validation;
- useful diagnostics integration.

Risks:

- swap-removal destroys ordering;
- returning the live item array allows external mutation;
- an existing registry silently wins when created again with different options;
- entity auto-removal policy is global and may not fit every owner;
- lifecycle ownership is not inherent despite the comments.

**Disposition:** Adapt into a generic collection utility, not a universal lifecycle manager.

### Spawn contracts

Trauma introduces shared spawn contracts and server validation.

Strengths:

- makes spawn topology explicit;
- attempts to validate team, FFA, solo, named-group, and nav requirements;
- closes modes that previously skipped validation;
- adds diagnostics and cached results.

Risks:

- some paths fail open when the resolver is unavailable;
- cache keys omit map revision, configuration hash, mode implementation hash, and validation version;
- caching an invalid result can persist after map-point edits;
- team validation can perform many LOS checks and random attempts;
- random validation makes results non-reproducible;
- fallback behavior may differ from vanilla and can reject previously playable maps;
- duplicated nodegraph detection indicates missing shared capability APIs.

**Disposition:** Rewrite after documenting vanilla spawn selection and map-point behavior.

### Self-test framework

Trauma adds shared/server/client self-test files and performance reporting.

Strengths:

- establishes a place for automated diagnostics;
- checks integrations, content, modes, and performance concepts;
- exposes command-driven verification.

Risks:

- broad self-tests can encode incorrect assumptions as requirements;
- runtime checks and static claims are mixed;
- passing counts can conceal skipped or shallow tests;
- tests are embedded in the addon rather than divided into safe production diagnostics and development-only suites.

**Disposition:** Adopt the concept, rewrite test taxonomy and evidence rules.

## 6. Static snapshot findings

The Trauma snapshot contains approximately:

| Registration type | Count |
|---|---:|
| `hook.Add` calls | 1,150 |
| `timer.Create` calls | 90 |
| `timer.Simple` calls | 546 |
| `util.AddNetworkString` calls | 327 |
| `net.Receive` calls | 340 |
| `net.Start` calls | 465 |
| `CreateConVar` calls | 236 |
| `CreateClientConVar` calls | 119 |
| `concommand.Add` calls | 200 |
| `file.Write` calls | 42 |

Literal-name analysis found:

- 5 duplicated network-string declarations;
- 30 duplicated literal receiver names;
- 9 duplicated literal hook event/identifier pairs;
- 30 duplicated literal ConVar names;
- 4 duplicated literal timer names.

Some duplicates are valid shared/server-client patterns. Others are replacement hazards or evidence of overlapping implementations. Every duplicate requires realm-aware classification before being called a bug.

## 7. Selected disposition table

| Trauma attempt | Decision | Reason |
|---|---|---|
| Deterministic sorted loading | Adapt | Good goal; must preserve verified dependency order. |
| Explicit mode registration | Adopt concept | Removes ambient `MODE` dependence. |
| Mode activation/deactivation | Adopt concept | Required for ownership and cleanup. |
| Generation guards | Adopt | Low-cost stale-callback protection. |
| Global hook/timer interception | Reject | Invasive and incomplete. |
| Static registration capture | Migration-only | Useful for auditing, unsafe as permanent runtime behavior. |
| Explicit owned hook API | Rewrite | Must be opt-in and namespaced. |
| Explicit owned timer API | Rewrite | Must include cancellable delayed tasks. |
| Persistent event allowlist | Reject | Persistence should be declared per resource. |
| Lifecycle status command | Adapt | Expand diagnostics and permissions. |
| Active registry utility | Adapt | Useful data structure with stricter encapsulation. |
| Spawn contracts | Rewrite later | Requires verified spawn parity first. |
| Self-test framework | Rewrite | Keep evidence discipline and separate test classes. |

## 8. Proposed target shape

The future compatibility layer should expose explicit APIs similar to:

```lua
ZCity.Systems.Register({
    id = "rounds",
    realm = "shared",
    depends = { "players", "modes" },
    start = function(context) end,
    stop = function(context) end,
})

ZCity.Hooks.Add(owner, "PlayerSpawn", "apply-mode-spawn", callback)
ZCity.Timers.Create(owner, "round-think", 1, 0, callback)
ZCity.Tasks.Delay(owner, 0.1, callback)
ZCity.Modes.Register(definition)
```

Properties required:

- no replacement of global Garry's Mod functions;
- owner and local ID produce a collision-resistant runtime ID;
- every registration has source, realm, lifetime, and replacement metadata;
- delayed tasks are cancellable;
- deactivation is idempotent;
- cleanup order is deterministic;
- legacy mode files can operate through a compatibility adapter;
- diagnostics can detect registrations bypassing project APIs without claiming ownership of them.

## 9. Acceptance criteria before implementation

1. Current mode and round behavior has executable parity tests.
2. Hook return semantics match Garry's Mod and the legacy dispatcher.
3. Base/derived mode replacement order is documented and tested.
4. Hot reload does not duplicate or remove unrelated registrations.
5. Delayed callbacks from inactive generations cannot mutate active state.
6. Cleanup is idempotent after normal exit, error, map cleanup, and shutdown.
7. Legacy mode files remain functional during staged migration.
8. Diagnostics distinguish owned, legacy, unknown, and leaked resources.
9. No global API is monkey-patched.
10. Performance overhead is measured under real hook/timer counts.
