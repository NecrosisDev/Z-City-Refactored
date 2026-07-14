# Source Baselines and Terminology

- **Status:** Normative source registry
- **Captured:** 2026-07-14

## Purpose

Earlier documents used “vanilla/current Z-City” too loosely. The project now has four distinct sources. Every factual claim, test fixture, diff, or migration decision must identify which one it describes.

## Canonical terms

| Term | Meaning |
|---|---|
| **Upstream vanilla snapshot** | The uploaded `Z-City.zip` source at upstream commit `3716789311f726174e1255f8b93fe1b28e619f6d` |
| **Destination baseline** | `NecrosisDev/Z-City-Refactored` commit `429ec928203cec963176dfb6afd086dcdd01c181`, the base of the working branch |
| **Working branch** | `fix/repo-foundation-hardening` and its successors |
| **Current Trauma prototype** | The uploaded `Trauma_Clean.zip` archive |
| **Historical Trauma prototype** | The earlier uploaded `Trauma.zip` archive, retained only for delta/history evidence |

Do not use bare “current Z-City” in new documents.

## Upstream vanilla snapshot

| Field | Value |
|---|---|
| Archive | `Z-City.zip` |
| SHA-256 | `8b67e8b362a7c07563a6e957632de1f2727a170fb65336ec4c5d18930d700487` |
| Archive bytes | `9,842,319` |
| Extracted root | `Z-City` |
| Git commit | `3716789311f726174e1255f8b93fe1b28e619f6d` |
| Lua files | `899` |
| Lua source bytes | `6,894,163` |
| Non-`.git` files | `931` |

The archive contains `.git`. Its working tree reports widespread modifications caused by line-ending conversion during copying. With end-of-line differences ignored, the only content difference from the recorded commit is a missing non-runtime bug-report template. Runtime source is therefore treated as equivalent to commit `3716789` for this audit.

## Destination baseline

| Field | Value |
|---|---|
| Repository | `NecrosisDev/Z-City-Refactored` |
| Base commit | `429ec928203cec963176dfb6afd086dcdd01c181` |
| Relationship | Ancestor of upstream snapshot commit `3716789` |

Most existing `architecture/zcity/` documents were inspected against this destination baseline. Unless a document explicitly states otherwise, its bare “Verified” findings mean **SOURCE-VERIFIED against `429ec92`**, not runtime parity and not the later upstream snapshot.

## Upstream drift after the destination baseline

The uploaded upstream snapshot contains three commits after `429ec92`. The executable diff is limited to:

- `lua/autorun/loader.lua` — re-enables five `resource.AddWorkshop` calls;
- `lua/homigrad/sh_luabullets.lua` — bounds an organism penetration loop with 50 attempts.

These changes are tracked in `zcity/upstream-delta-429ec92-to-3716789.md`. They are evidence, not automatic cherry-picks.

## Current Trauma prototype

| Field | Value |
|---|---|
| Archive | `Trauma_Clean.zip` |
| SHA-256 | `03d6b1b917ebd33ba0a472dbc7ecf09118eb743aaadbbdd8dab1505476dc13f8` |
| Archive bytes | `7,133,204` |
| Extracted root | `Trauma_Clean` |
| Files | `1,289` |
| Lua files | `1,035` |
| Lua source bytes | `8,850,553` |

`Trauma_Clean.zip` is the only Trauma archive used for new file-level findings. Documentation inside it remains **CLAIMED** evidence until verified against executable source and runtime behavior.

## Historical Trauma prototype

| Field | Value |
|---|---|
| Archive | `Trauma.zip` |
| SHA-256 | `0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652` |
| Archive bytes | `4,425,563` |
| Extracted root | `TMod` |
| Lua files | `1,028` |

This snapshot is superseded for implementation guidance. It remains useful only for identifying what changed between Trauma iterations.

## Inheritance rule for existing documents

Until each subsystem document receives an explicit header:

- `architecture/zcity/**` inherits the **destination baseline**;
- `architecture/sources/trauma-*.md` written before this registry inherits the **historical Trauma prototype**;
- accepted ADRs remain decisions, but their source evidence must be rechecked if based on the historical Trauma archive;
- no existing static document establishes runtime parity.

## Required source header for new or revised documents

Every new or materially revised subsystem document must state:

- evidence status;
- source baseline name;
- exact commit or archive SHA-256;
- realm and relevant paths;
- last reviewed date;
- whether exhaustive repository search was completed;
- runtime/test status;
- superseded documents, if any.
