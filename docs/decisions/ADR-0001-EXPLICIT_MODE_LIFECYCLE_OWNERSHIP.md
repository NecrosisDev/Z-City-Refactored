# ADR-0001: Explicit Mode Lifecycle Ownership

- **Status:** Accepted as architectural direction
- **Implementation status:** Not yet implemented
- **Scope:** Mode-owned hooks, timers, delayed callbacks, and cleanup

## Context

The current Z-City mode loader registers every function on a mode table through a shared dispatcher. This successfully prevents ordinary mode methods from becoming one independent Garry's Mod hook per mode.

However, mode files can also directly call:

- `hook.Add`
- `timer.Create`
- `timer.Simple`
- `net.Receive`
- `concommand.Add`
- other global registration APIs

Those registrations are not owned by the mode lifecycle and can remain active while another mode is selected.

Trauma attempts to correct this by temporarily replacing global registration functions while mode files load and while mode callbacks execute. It records the resulting hooks and timers, then activates or removes them when the selected mode changes.

## Vanilla behavior

### Useful behavior to preserve

- Mode-table methods are dispatched through one hook per method name.
- Inactive mode-table methods are not independently registered as hooks.
- Hook return values propagate to Garry's Mod callers.
- Base modes and subtype aliases remain compatible.
- Mode `saved` data may survive Lua refresh.

### Defect to correct

Direct registrations made by mode files are process-global and have no reliable owner.

## Trauma alternative

Trauma provides:

- Static registration capture during mode loading.
- Runtime registration capture during mode callback execution.
- Activation and deactivation of captured hooks and timers.
- Generation checks that suppress delayed callbacks from an inactive mode.
- Base-mode definition chaining.

## Rejected mechanism

The project will not infer ownership by replacing global `hook` and `timer` functions.

### Reasons

1. **Global side effects** — unrelated code called in the capture window observes modified APIs.
2. **Attribution ambiguity** — registrations created by shared libraries may be assigned to the invoking mode.
3. **Bypass risk** — cached references to the original functions are invisible to capture.
4. **Reentrancy complexity** — nested calls and cross-mode execution are difficult to define safely.
5. **Exception sensitivity** — every failure path must restore global functions perfectly.
6. **Incomplete ownership** — the pattern does not naturally cover every registration API.
7. **Behavioral uncertainty** — execution can differ based on call path rather than explicit declaration.

## Decision

Mode-owned runtime resources will use explicit ownership APIs.

The future mode context will conceptually provide operations such as:

```lua
context:Hook(eventName, identifier, callback)
context:Timer(name, delay, repetitions, callback)
context:Delay(delay, callback)
context:Cleanup(identifier, callback)
context:NetHandler(messageName, callback)
```

The final names and signatures remain subject to design review.

Each active mode receives an ownership context with a unique generation. Deactivation disposes all resources registered through that context.

## Compatibility strategy

Migration will be incremental:

1. Keep the current mode-method dispatcher.
2. Inventory direct registrations in each vanilla mode.
3. Migrate direct registrations to explicit context APIs one mode at a time.
4. Add diagnostics for unmanaged registrations where practical.
5. Do not globally intercept registration APIs.
6. Preserve persistent process-level hooks outside mode contexts.

Legacy mode files remain loadable during migration, but their unmanaged registrations are documented as technical debt until converted.

## Delayed callback rule

A delayed callback owned by a mode must not execute after that ownership context is disposed.

Preferred behavior:

- Named timers are removed during disposal.
- One-shot delays use generated names or another cancellable registry.
- A generation check remains as a secondary safety guard, not the primary cleanup mechanism.

## Activation rule

Pure lookup functions such as `CurrentRound()` must not activate or deactivate a mode.

Mode lifecycle transitions must occur through explicit round-state transition functions. This keeps getters free of side effects and makes activation ordering testable.

## Consequences

### Positive

- Deterministic ownership
- Clear cleanup behavior
- Easier hot-reload reasoning
- No temporary replacement of global APIs
- Better diagnostics
- Easier unit and acceptance testing
- Extensible to network handlers and other registrations

### Negative

- Existing mode files require deliberate migration.
- Some shared helper libraries may need owner-aware variants.
- Mixed managed and unmanaged behavior will exist during transition.
- The system cannot automatically capture arbitrary third-party side effects.

These costs are accepted because explicit ownership is safer than invisible interception.

## Acceptance criteria

1. Switching modes removes all managed hooks and timers from the previous mode.
2. A delayed callback from the previous mode cannot mutate the new round.
3. Persistent global hooks remain registered across mode changes.
4. Hook return propagation matches current Z-City behavior.
5. Base-mode resources activate before derived-mode overrides.
6. Derived registrations with the same event and identifier replace the inherited registration predictably.
7. An exception in a mode callback does not corrupt global registration functions.
8. `CurrentRound()` performs no lifecycle mutation.
9. Lua refresh does not duplicate managed registrations.
10. Diagnostics can identify remaining unmanaged mode registrations during development.