# Refactor Implementation Control

- **Status:** Normative process index
- **Build authority:** `../BUILD_GUIDE.md`

## Purpose

This directory contains implementation work packages and the traceability record connecting requirements, defects, ADRs, code changes, and acceptance tests.

Architecture research belongs under `../architecture/`. Decisions belong under `../decisions/`. Implementation records belong here.

## Canonical contents

- `WORK_PACKAGE_TEMPLATE.md` — required template for each bounded implementation slice.
- `TRACEABILITY.md` — master index of requirements, work packages, tests, defects, decisions, and implementation status.
- `work-packages/` — one file per approved work package, named `ZC-WP-NNN-short-title.md`.
- `tests/` — acceptance-test specifications when they are too large for a work package, named by stable test ID.

Create `work-packages/` or `tests/` when the first record is ready; do not add placeholder files solely to create directories.

## Work-package states

| State | Meaning |
|---|---|
| **Draft** | Evidence or design fields remain incomplete. No implementation authorization. |
| **Ready** | Gates 0–2 are satisfied and implementation may begin. |
| **Active** | Code and tests are being implemented. |
| **Blocked** | A named prerequisite prevents progress. |
| **Validation** | Implementation exists and required tests are running. |
| **Complete** | Definition of Done is satisfied and traceability is updated. |
| **Superseded** | Replaced by another work package or decision. |
| **Rejected** | Intentionally not implemented. |

Only **Ready** work packages may introduce behavior-changing code.

## Review rule

A work package must be understandable without chat history. It must link exact source baselines, code paths, requirements, acceptance tests, rollout, rollback, and legacy-removal criteria.
