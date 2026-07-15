# Trauma Pathowogen Adapter Decision

## Scope

This decision covers only Trauma's attempted Pathowogen compatibility adapter and the patching strategy exposed by its runtime failure. It does not approve or reject Pathowogen gameplay features themselves.

## Verified evidence

The observed Trauma runtime reported:

```text
[Trauma CustomGM V2] Pathowogen adapter failed: canonical stock hash mismatch for pathowogen: 3242346582 != 4050429017
```

The adapter therefore expected one exact representation of a third-party or stock implementation and refused to activate when the loaded implementation produced a different hash.

The current `main` branch remains the verified vanilla Z-City implementation baseline. No Pathowogen dependency, pinned Pathowogen source, or verified Pathowogen owner file is present in the repository evidence inspected for this decision.

## Comparison against vanilla behavior

Vanilla Z-City does not need this adapter to establish core startup or gameplay ownership. Leaving the adapter absent preserves the current behavior.

Trauma's attempted approach provides one useful safety property: it avoids blindly patching code whose expected body has changed. However, exact source hashing is not a durable integration boundary. Harmless upstream edits, formatting changes, distribution differences, or a legitimate newer implementation can disable the adapter even when the required behavior and API remain compatible. Conversely, a matching hash proves only that the compared text matches; it does not prove that the surrounding runtime state, load order, dependencies, or hooks are safe.

## Decision

Reject exact canonical-source hashing as the activation mechanism for optional gameplay integration.

A future Pathowogen integration is justified only when an exact gameplay need and inspectable provider source are available. It must then:

- detect the specific functions, hooks, entities, or data contracts it consumes;
- avoid replacing provider functions when a hook or adapter boundary can express the behavior;
- remain inert when the provider is absent or incompatible;
- preserve vanilla Z-City behavior when inactive;
- report one actionable incompatibility diagnostic without repeated log spam;
- pin compatibility to explicit provider versions only when capability detection is insufficient;
- include live tests for provider absent, supported, unsupported, and Lua-refresh states.

If a provider function must be wrapped, the wrapper must retain the original callable, be idempotent, verify that it still owns the installed wrapper before restoring it, and fail closed without leaving a partial patch.

## Production impact

None. No Pathowogen code, hashes, hooks, wrappers, network messages, dependencies, or gameplay behavior were added to the current branch.

## Status

Trauma's attempted compatibility goal remains eligible for later evaluation. Its hash-gated monkey-patch strategy is explicitly rejected. Missing provider source is not permission to invent an integration surface.