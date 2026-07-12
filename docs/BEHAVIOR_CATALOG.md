# Behavior Catalog

Record externally observable behavior independently from implementation structure. Stable behavior IDs let code changes, tests, issues, and design discussions reference the same contract.

## Entry template

### `BEH-<stable-id>` — Behavior name

- **Status:** `verified | partial | broken | planned`
- **Actors/context:** Who or what performs the behavior and under which mode/state.
- **Trigger:** Input, hook, event, timer, command, or state transition.
- **Expected result:** Observable outcome.
- **Important edge cases:** Boundaries, invalid states, disconnects, death, round changes, map cleanup, lag, or missing integrations.
- **Implementation evidence:** Paths and symbols responsible for the behavior.
- **Regression coverage:** Automated check or reproducible manual procedure.
- **Related systems/types:** Stable catalog IDs.
- **Last verified:** Commit SHA and date.

## Catalog

No behaviors have been verified for this refactored baseline yet. Intended behavior must be labeled `planned` until implementation or runtime evidence confirms it.
