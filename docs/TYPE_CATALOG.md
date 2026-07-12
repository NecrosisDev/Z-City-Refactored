# Type Catalog

Document shared contracts that multiple files or systems depend on. This includes Lua table shapes, registries, enum-like strings, network payloads, entity metadata, configuration schemas, and stable identifiers.

## Entry template

### `TYPE-<stable-id>` — Type or contract name

- **Kind:** `table | registry | identifier | payload | config | entity metadata | other`
- **Authority/owner:** System that defines and validates the contract.
- **Definition paths:** Source locations.
- **Consumers:** Systems or files that read/write it.
- **Required fields/values:** Names, value types, defaults, and invariants.
- **Realm/transport:** Where it exists and how it crosses client/server boundaries.
- **Compatibility rules:** Safe extension and breaking-change conditions.
- **Validation:** Parser, guard, test, assertion, or reproducible check.
- **Related systems/behaviors:** Stable catalog IDs.
- **Last verified:** Commit SHA and date.

## Catalog

No shared types have been verified for this refactored baseline yet. Do not infer a schema from a single call site.
