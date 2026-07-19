# Z-City Network Contract and Trust Boundaries

- **Status:** SOURCE-VERIFIED baseline and PROPOSED target contract
- **Destination baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Later upstream vanilla snapshot:** `3716789311f726174e1255f8b93fe1b28e619f6d`
- **Current Trauma prototype:** `Trauma_Clean.zip` (`03d6b1b...`)
- **Runtime packet capture:** Not performed
- **Registry completeness:** Incomplete; this document defines the contract that the exhaustive registry must satisfy

## Purpose

This document converts the verified round/spectator packet behavior and the structurally inventoried Trauma network surface into one target contract for the refactor. It does not authorize a network rewrite by itself and does not claim that every legacy channel has been enumerated.

The migration unit is a declared endpoint or bounded snapshot contributor, not a Lua file and not a bulk copy of Trauma networking.

## Verified destination behavior

The destination baseline has a server-authoritative round and spectator flow, but state is distributed across dedicated packets, NWVars, globals, and subsystem-specific synchronization.

The currently verified core channels are:

| Channel | Direction | Verified role | Principal concern |
|---|---|---|---|
| `RoundInfo` | server to client | mode name and numeric round state | no version, sequence, timing, or complete mode identity |
| `updtime` | server to all clients | round duration/start/begin floats | can arrive independently from `RoundInfo` |
| `FadeScreen` | server to all clients | transition presentation trigger | no explicit payload or generation |
| `ZB_ChooseSpecPly` | client to server | next/previous/view-mode request | raw input constant, no explicit rate policy |
| `ZB_SpectatePlayer` | server to one client | immediate target/adjacent target/view response | duplicates persistent spectator NWVars |
| `ZB_SpecMode` | client to server | join/leave spectator request | can kill or re-team the player without expected-state metadata |

Additional verified characteristics:

- `RoundInfo` and `updtime` are broadcast separately during round transition.
- initial synchronization sends `RoundInfo` only when `zb.CROUND` exists and separately invokes `ply:SyncVars()` when available;
- spectator target and view mode are represented both by a dedicated response and by `NWEntity("spect")` / `NWInt("viewmode")`;
- spectator observation can invoke organism synchronization approximately once per second;
- client presentation applies delayed local hull/movement changes without a sequence or representation generation;
- client-originated spectator requests rely on receiver-local checks rather than a shared request policy.

See `round-and-spectator-networking.md` for the exact source trace and packet fields.

## Later upstream vanilla comparison

The later upstream vanilla snapshot is three commits ahead of the destination baseline. The compared files are limited to:

- `lua/autorun/loader.lua`;
- `lua/homigrad/sh_luabullets.lua`.

None of the surveyed core round/spectator source files changed in that delta. The later upstream snapshot therefore does not supply a newer network architecture for these contracts; destination behavior remains the relevant vanilla behavior for this analysis.

This conclusion is limited to the surveyed source files. It does not prove that no indirect loader-order effect can alter packet registration or receiver replacement at runtime.

## Trauma Clean comparison

Static inventory of the current Trauma prototype found:

| Surface | Lexical count |
|---|---:|
| `util.AddNetworkString` | 327 |
| `net.Receive` | 340 |
| `net.Start` | 467 |
| duplicate declaration literal groups | 5 |
| duplicate receiver literal groups | 30 |

The current archive has the same declaration and receiver counts as the historical Trauma archive and two additional sends. This means the clean archive did not resolve network ownership by materially shrinking or replacing the packet surface.

Trauma attempts or claims concepts in these groups:

- broader late-join and custom-system synchronization;
- mode, editor, role, class, weapon, organism, medical, bot, minimap, map-tool, and administration packets;
- lifecycle generations and stale-work protection in selected paths;
- diagnostics, health reports, readiness checks, and payload/rate guardrails in later experiments;
- compatibility messages layered over stock channels and networked variables;
- optional-provider and bundled-vendor integration traffic.

These are concept families, not approved implementations. Exact channel-level migration remains blocked until the current Trauma Clean declaration, sender, receiver, realm, payload, permission, visibility, and lifecycle graph is generated and reviewed.

## Core problem statement

The legacy and Trauma surfaces do not provide one enforceable answer to the following questions:

1. Who owns the endpoint?
2. Which realm may send it?
3. Which principal is authorized to request or observe it?
4. What exact fields, widths, bounds, and semantic units are on the wire?
5. Which round, player, representation, mode, or data revision does it belong to?
6. What happens when it is duplicated, reordered, delayed, replayed, or received after a transition?
7. What is the maximum sender rate, payload size, decode work, and fan-out?
8. Which legacy projection remains during migration, and when can it be removed?

The new project must answer these before a behavior-changing endpoint is accepted.

## Target endpoint registry

Every project-owned endpoint must have one registry record with at least:

| Field | Required meaning |
|---|---|
| `id` | stable project endpoint identifier |
| `wire_name` | current network-string literal |
| `owner` | one subsystem owner |
| `direction` | `s2c`, `c2s`, or explicitly justified `shared` |
| `sender_realm` | realm allowed to originate the message |
| `receiver_realm` | realm allowed to receive it |
| `kind` | snapshot, delta, event, request, command result, or compatibility projection |
| `schema_version` | explicit protocol version |
| `payload` | ordered field schema, widths, units, enum domains, and optionality |
| `max_bits` | hard encoded-payload ceiling |
| `decode_budget` | bounded validation/processing expectations |
| `authorization` | permission and gameplay-state predicate |
| `visibility` | who may observe the data and why |
| `rate_policy` | burst, sustained rate, cooldown, and rejection behavior |
| `generations` | round/player/representation/mode/data revisions carried or resolved |
| `lifetime` | boot, session, mode, round, player, entity, or request scope |
| `compatibility` | legacy channel/NWVar projection and removal criteria |
| `diagnostics` | accepted/rejected/stale/oversize counters without private payload logging |

A registration without these fields is an audit observation, not an approved project endpoint.

## Endpoint kinds

### Snapshots

Snapshots establish a complete authoritative state for a declared scope. A snapshot must include:

- protocol version;
- snapshot scope and owner;
- sequence or revision;
- applicable generations;
- contributor presence/version information;
- bounded payload size;
- completion semantics;
- explicit behavior for unknown contributors.

The round late-join snapshot should include mode identity, round state, timing, round generation, and the minimum spectator/admission context needed by the client. Organism, inventory, editor, and other private or large data remain separate contributors with their own visibility and size limits.

### Deltas

A delta must identify the base revision it expects. The receiver rejects or requests resynchronization when the base is absent, stale, or mismatched.

### Events

Events represent non-authoritative presentation or notification facts. They must not silently become persistent gameplay state. Replaying an event must not duplicate gameplay mutation.

### Client requests

Client requests express intent, never authority. Each request must define:

- a bounded action enum rather than raw engine constants where practical;
- expected current state or generation;
- target identity and eligibility rules;
- permission and gameplay-state checks;
- per-player rate policy;
- bounded payload and decode work;
- deterministic rejection result or intentionally silent rejection policy.

### Command results

Administrative/editor requests receive an explicit result containing a request identifier, success/failure code, safe message, and resulting revision when applicable. A UI timeout is not proof that the command failed.

## Serialization rules

New project endpoints must not use unrestricted `net.WriteTable` / `net.ReadTable` as their contract.

Approved serialization requires:

- fixed ordered fields or a bounded project codec;
- explicit maximum lengths for strings, arrays, maps, compressed data, and chunks;
- allowlisted identifiers and enums;
- finite numeric ranges and semantic units;
- no arbitrary entity/table/function/userdata serialization;
- no client-authored whole-object replacement;
- rejection before expensive persistence, decompression, or graph traversal;
- chunk transfer identifiers, counts, byte totals, expiry, and duplicate handling where chunking is justified.

Compression does not replace a decompressed-size limit.

## Authority and visibility

The server remains authoritative for gameplay state. Client-authored data is limited to validated intent, preferences that do not affect authority, and explicitly permitted editor/admin commands.

Visibility must be declared independently from authority. Examples:

- public round phase may be visible to all clients;
- full organism state is private and must not be broadcast merely because the server owns it;
- spectator visibility is derived from the observed target, selected view, mode policy, and data sensitivity;
- admin/editor visibility requires explicit permissions and must not reuse ordinary-player snapshots;
- diagnostic counters may be visible while payload contents remain private.

Developer mode does not authorize whole-table replication.

## Generations and stale-message handling

Endpoints that can outlive a transition must carry or resolve the applicable generation set. Depending on scope, this may include:

- server session generation;
- mode generation;
- round generation;
- player admission/life generation;
- character representation generation;
- weapon-instance generation;
- entity generation;
- configuration/data revision;
- request identifier.

A receiver must reject stale state before invoking subsystem callbacks. Compatibility projections may omit new fields only when their owner can safely derive current state and when tests prove that stale legacy delivery cannot restore obsolete authority.

## Late-join contract

Late join is a transaction, not an incidental collection of broadcasts.

The target sequence is:

1. establish protocol compatibility;
2. allocate a join snapshot revision;
3. send core round/mode/timing state;
4. send authorized subsystem contributors;
5. apply contributors in declared dependency order;
6. acknowledge or locally mark completion;
7. release presentation/input gates that require a coherent state;
8. switch to ordered deltas/events.

A missing optional contributor is reported as absent, not silently replaced by stale local state.

## Compatibility migration

Legacy channel names and NWVars may remain temporarily as projections, but they cannot remain parallel writable authorities.

For each compatibility projection:

- project state is written once by the new owner;
- the projection is derived from that state;
- legacy sender and receiver behavior is covered by fixtures;
- projection usage is observable;
- removal criteria identify supported client/addon versions and zero-use evidence;
- rollback restores the old path without leaving both writers active.

For the core round/spectator flow, `RoundInfo`, `updtime`, `ZB_SpectatePlayer`, `NWEntity("spect")`, and `NWInt("viewmode")` require an explicit projection plan before replacement.

## Rate, cost, and abuse policy

Every client-originated endpoint must set both a rate policy and a work policy.

The policy must bound:

- packets per burst and sustained interval;
- decoded bytes and collection entries;
- entity lookups and world queries;
- persistence writes and broadcasts;
- decompression and JSON work;
- failed-attempt logging;
- per-player and global queue occupancy.

Permission checks alone are insufficient. An authorized administrator can still send accidental or maliciously large, rapid, or structurally invalid requests.

## Observability

The network layer should expose aggregate diagnostics by endpoint:

- sent and received count;
- accepted and rejected client requests;
- rejection reasons;
- stale-generation drops;
- oversize and decode failures;
- rate-limit drops;
- average and maximum encoded bytes;
- average and maximum handler time;
- current compatibility-projection use;
- duplicate registration and receiver replacement history.

Do not log private medical state, credentials, chat content, or full editor payloads by default.

## Trauma dispositions

| Trauma concept | Decision | Refined use |
|---|---|---|
| lifecycle generations | Adopt | required metadata for asynchronous state and requests |
| broader late-join synchronization | Rewrite | one ordered core snapshot with bounded contributors |
| packet ownership/schema metadata | Adapt | implement one project registry, not per-subsystem conventions |
| diagnostics and payload/rate reporting | Adapt | aggregate endpoint telemetry with privacy limits |
| editor/admin request channels | Rewrite | bounded commands, revisions, permissions, rate/cost limits, explicit results |
| organism/medical replication | Rewrite | typed visibility sets and deltas; no whole-table authority |
| compatibility channels | Adapt temporarily | one-way projections with measured removal criteria |
| additional ad hoc sync messages | Reject | cannot compensate for missing snapshot or ownership design |
| unrestricted table serialization | Reject for new endpoints | fixed/bounded codecs only |
| bundled-provider network coupling | Reject | provider adapters translate through project contracts |

## Stable requirements

- **NET-REQ-001:** Every project endpoint has exactly one owner and one registry record.
- **NET-REQ-002:** Every endpoint declares direction, sender realm, receiver realm, kind, and lifetime.
- **NET-REQ-003:** Every payload has a versioned bounded schema and encoded-size ceiling.
- **NET-REQ-004:** Every client request has authorization, expected-state validation, and rate/cost policy.
- **NET-REQ-005:** Asynchronous state carries or resolves applicable generations and rejects stale delivery.
- **NET-REQ-006:** Late join uses a sequenced core snapshot with declared subsystem contributors and completion state.
- **NET-REQ-007:** Round mode, phase, timing, and round generation become one coherent authoritative snapshot.
- **NET-REQ-008:** Spectator target/view/admission have one authoritative representation.
- **NET-REQ-009:** Private organism, medical, inventory, and administrative data have explicit visibility policies.
- **NET-REQ-010:** New endpoints do not use unrestricted table serialization.
- **NET-REQ-011:** Chunked transfers have byte totals, chunk bounds, expiry, duplicate handling, and decompressed-size limits.
- **NET-REQ-012:** Legacy channels and NWVars are compatibility projections, not parallel writers.
- **NET-REQ-013:** Endpoint telemetry reports failures and abuse without logging private payloads.
- **NET-REQ-014:** Optional-provider adapters remain absent-safe and cannot register a competing project authority.

## Acceptance-test specifications

- **NET-AT-001:** Generate the endpoint registry from source and fail on undeclared project-owned declarations, receivers, or sends.
- **NET-AT-002:** Fail when two active project owners register the same wire name or replace a receiver without an approved compatibility record.
- **NET-AT-003:** Fuzz each client request with unknown enums, invalid entities, stale generations, missing permissions, and malformed lengths.
- **NET-AT-004:** Burst and sustain each client request above policy and verify bounded server work and deterministic rejection counters.
- **NET-AT-005:** Join during boot, intermission, active round, end delay, cleanup, and mode change; verify one coherent completed snapshot.
- **NET-AT-006:** Reorder, duplicate, delay, and drop round snapshot chunks/deltas; verify no mixed-generation state is committed.
- **NET-AT-007:** Deliver legacy `RoundInfo` and `updtime` in both orders during compatibility mode and verify the projection cannot overwrite newer state.
- **NET-AT-008:** Change spectator target, view mode, life state, and representation before delayed responses apply; verify stale work is rejected.
- **NET-AT-009:** Spam spectator admission and target requests while alive, dead, respawning, disconnected, and across mode generations.
- **NET-AT-010:** Verify spectator visibility for public state, private organism state, restricted roles, and administrator-only data.
- **NET-AT-011:** Attempt maximum and over-maximum strings, arrays, maps, compressed payloads, and chunk counts for every variable-size schema.
- **NET-AT-012:** Send compressed data with a small encoded size and excessive decompressed size; verify rejection before allocation/parse escalation.
- **NET-AT-013:** Disconnect sender or receiver during a chunked transfer and verify owned buffers expire without leaks.
- **NET-AT-014:** Lua-refresh or replace a receiver and verify registration history, active owner, and stale callbacks are observable.
- **NET-AT-015:** Remove each optional provider and verify core endpoints register and function without errors or substitute vendor authority.
- **NET-AT-016:** Exercise editor/admin saves concurrently and verify revision conflict handling, atomic persistence, explicit results, and bounded broadcasts.
- **NET-AT-017:** Capture bandwidth and handler-time baselines for representative 1, 16, 32, and 64-player cases.
- **NET-AT-018:** Disable compatibility projections only after fixtures show no required legacy consumer and rollback restores exactly one writer.

## Implementation boundary

No broad network replacement is approved yet.

A bounded observation or correction work package may proceed only when it:

- identifies exact affected endpoints and consumers;
- preserves legacy wire behavior unless the work package includes compatibility fixtures;
- does not create a second snapshot or spectator authority;
- adds registry records and tests before behavior changes;
- has a rollback that restores one known authority;
- satisfies Gates 0–2 in `../../BUILD_GUIDE.md`.

The first acceptable implementation work is an offline/generated registry plus passive runtime registration telemetry. It must not intercept, rewrite, or suppress packets.

## Remaining evidence work

1. Generate the complete destination declaration/sender/receiver/NWVar inventory at `429ec92`.
2. Generate the same inventory for upstream `3716789` and prove the exact network delta.
3. Generate the complete current Trauma Clean endpoint graph with vendor/project classification.
4. Resolve all duplicate declaration and receiver groups by realm, load order, and active owner.
5. Trace `ply:SyncVars()`, organism observation packets, editor/admin packets, weapon/projectile packets, and mode-specific channels.
6. Record packet captures and bandwidth/handler-time baselines in a dedicated server fixture.
