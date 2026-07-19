# Source Assessments

- **Status:** Normative index for source-derived evidence
- **Source registry:** `../source-baselines.md`

## Authority rule

Source inventories and assessments identify evidence and candidate requirements. They do not override accepted ADRs, normative standards, destination-baseline behavior, or executable acceptance results.

## Current Trauma authority

Use these for new work:

1. `trauma-clean-inventory.md` — current structural inventory and archive delta.
2. `trauma-mode-lifecycle-comparison.md` — current canonical bounded lifecycle comparison.
3. `trauma-networking-assessment.md` — current structural network attempt families, dispositions, trust risks, and unresolved endpoint evidence.
4. `../comparison-ledger.md` — concept disposition.
5. accepted ADRs and an approved work package — implementation authority.

## Historical assessments

The following were written from the historical `Trauma.zip` snapshot:

- `trauma-lifecycle-assessment.md`;
- `trauma-weapon-combat-assessment.md`;
- `trauma-inventory.md`.

Their concept-level conclusions remain useful where they agree with accepted ADRs and the current comparison ledger. Their exact paths, counts, hashes, and implementation claims are **not current build evidence** until revalidated against `Trauma_Clean.zip`.

## Revalidation rule

Before a historical assessment supports a **Ready** work package:

- locate the equivalent path in Trauma Clean;
- record whether it is unchanged, changed, replaced, or removed;
- re-run exhaustive symbol and registration search;
- verify dependencies and load order;
- update security, cleanup, networking, and performance implications;
- link the current source evidence in the work package.

If no equivalent path exists, retain only the extracted requirement or reject the concept. Do not recreate an obsolete Trauma implementation merely to match the historical assessment.
