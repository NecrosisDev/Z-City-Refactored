# System Catalog

Use one section per independently understandable runtime system. Prefer links and compact facts over prose.

## Entry template

### `SYS-<stable-id>` — System name

- **Status:** `verified | partial | legacy | planned`
- **Purpose:** What responsibility this system owns.
- **Primary paths:** Source entry points.
- **Realm:** `server | client | shared`
- **Initialization/load order:** Hooks, autoruns, includes, registration, or startup dependencies.
- **Public surface:** Commands, hooks, net messages, globals, registries, entities, convars, or exported functions.
- **Dependencies:** Required systems and optional integrations.
- **Data ownership:** Authoritative state and replication direction.
- **Failure modes:** Known ways the system can regress.
- **Validation:** Tests, self-test commands, reproducible checks, or runtime evidence.
- **Related behaviors/types:** Stable catalog IDs.
- **Last verified:** Commit SHA and date.

## Catalog

No systems have been verified for this refactored baseline yet. Add entries only after tracing executable code.
