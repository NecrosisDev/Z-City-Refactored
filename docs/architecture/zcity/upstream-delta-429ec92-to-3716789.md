# Upstream Delta: `429ec92` to `3716789`

- **Status:** SOURCE-VERIFIED
- **Destination baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`
- **Upstream vanilla snapshot:** `3716789311f726174e1255f8b93fe1b28e619f6d`
- **Runtime verification:** Not yet performed

## Scope

The working refactor branch was created from `429ec92`. The uploaded upstream vanilla repository is three commits later at `3716789`. This document prevents later upstream changes from being mistaken for either existing destination behavior or Trauma-derived work.

## Changed executable files

Only two executable files differ between the commits.

### `lua/autorun/loader.lua`

Upstream re-enables five Workshop resources guarded by `hg_loadcontent`:

- `3657285193`;
- `3657897364`;
- `3657294321`;
- `3544105055`;
- `3257937532`.

#### Effect on existing documentation

`ZC-FND-002` is true for the destination baseline: the ConVar is enabled while its guarded actions are commented out. It is not true in the same form for upstream `3716789`.

#### Disposition

**Rewrite, do not cherry-pick blindly.** The future project requires a truthful, project-owned content/dependency manifest. Re-enabling upstream IDs may be useful for a vanilla compatibility fixture, but it is not the final content architecture and may conflict with the project’s intended consolidated Workshop dependency.

#### Required tests

- disabled ConVar adds no Workshop resources;
- enabled compatibility fixture adds the expected exact resources once;
- missing optional content produces one actionable capability report;
- project content manifest and legacy compatibility mode cannot both double-register the same dependency.

### `lua/homigrad/sh_luabullets.lua`

Upstream adds a `tries = 50` bound to a loop that continues while a traced entity is valid and has an organism.

#### Problem addressed

The destination-baseline loop has no explicit iteration bound. A trace sequence that repeatedly resolves to organism-bearing entities can keep the loop active longer than intended or indefinitely under pathological behavior.

#### Disposition

**Adapt as a high-priority safety requirement.** Preserve intended penetration behavior, but move the bound into the future event-scoped bullet/damage transaction with diagnostics for budget exhaustion. The literal value `50` is provisional until fixtures establish a safe and sufficient limit.

#### Required tests

- normal penetration chains retain destination-baseline damage outcomes;
- pathological repeated organism traces terminate;
- budget exhaustion emits bounded server diagnostics without spamming clients;
- the trace cannot repeatedly damage the same logical owner unintentionally;
- cost remains bounded across many simultaneous bullets;
- the implementation does not hide an underlying unchanged-trace bug.

## Build rule

Before implementing a subsystem, compare the destination baseline against the upstream vanilla snapshot for that subsystem. Classify later upstream work as:

- required compatibility change;
- safety fix to adapt;
- feature change requiring an explicit requirement;
- rejected or superseded by project architecture.

Upstream commits are evidence. They do not bypass the work-package gates in `../../BUILD_GUIDE.md`.
