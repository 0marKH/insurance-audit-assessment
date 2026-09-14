# Extraction evaluation — Hospital 1

This records the extraction milestone. The subsequent invoice-audit evaluation
is documented in [Hospital 1 engine results](hospital_1_engine.md). This document
reports structural extraction checks, not label-derived accuracy or calibration.

## Observed baseline

| Measure | Result |
|---|---:|
| Source nonempty lines recognized | 206 / 206 |
| Exact service catalogue entries | 108 |
| Daily threshold premiums | 9 |
| Weekend uplifts | 7 |
| Discount tiers | 11 |
| Daily caps | 7 |
| Bundle pairs | 3 |
| Exclusion windows | 6 |
| Other scope/definition/calculation/grouping/invoicing rules | 23 |
| Total rule records | 174 |
| Contract-only records with unresolved questions | 27 |
| Unresolved policy questions after user conventions | 0 |
| Blocking parse diagnostics on baseline | 0 |

All rule records have exact source quotations and document hashes. Structural
coverage includes recognized headings and table headers; it is not proof that
every interpretation is correct. The prose profile and reference expectations
were created during this development session, not independently adjudicated by
an external reviewer.

## Validation

Run `python3 -m unittest discover -s tests -v` and
`python3 -m contract_extractor --check`. Also run
`python3 -m contract_extractor.validate_line_ids --check`.

The extraction/policy subset contains **35 passing tests**; the complete suite
now has 63. Identifier validation covers 61,211 CSV
IDs and the matching 61,211 JSONL IDs across all five hospitals. Every ID matches
the fixed-width pattern; no duplicate IDs, format exceptions or ordering
disagreements were found. The detailed report includes input hashes.

The suite checks the baseline inventory, unusual billing units, exact cents,
every discount tier and bundle price, all cap values, cross-invoice grouping,
strict boundaries, counting order, calculation conventions and evidence spans.
It verifies source file hashes and deterministic reproduction of both outputs.

Mutation tests change contract values to verify live extraction. They also
introduce changed comparison words, changed definitions, missing clauses,
unknown services, inconsistent units, duplicate table rows, broken tables,
conflicting caps, conflicting dates and an unsupported hospital. These must
surface diagnostics and block every record from engine use. CLI tests verify
exit codes for completed, unresolved and blocked extraction. Added tests check
the convention overlay, unchanged contract evidence, retained ambiguity history,
inclusive patient-scoped exclusions, original billed usage, partial cap policy,
duplicate pricing priorities and conflict-review controls. Identifier tests
inject bad padding, wrong hospital prefixes, duplicates, ordering disagreement
and mismatched CSV/JSONL identifiers to verify review behavior.

These tests inspect extraction semantics and failure behavior. They do not
execute invoice calculations; that is the next milestone.

## Failure types and limits

1. **Unsupported language/layout.** Replacing “exceeds” with “is at least”
   requires reviewed semantics; the parser blocks rather than guessing. Even
   meaning-preserving prose rewrites may require a profile update.
2. **Incomplete or inconsistent source.** Missing required clauses or mismatched
   caps block. A removed unreferenced catalogue row cannot be detected by table
   structure alone. Snapshot hashes and baseline counts detect that regression
   for the pinned assessment, but are not a general completeness oracle.
3. **Underspecified meaning.** Exclusion endpoint/patient scope, identifier
   comparison, disallowed usage history and correction allocation are resolved
   by explicit user conventions. The original contract ambiguities remain
   recorded. Conflicting evidence in actual invoices must still be reviewed;
   policy resolution is not evidence that every correction can be determined.
4. **Unimplemented invoice grounding.** Free-text billing descriptions still
   need service matching. The extractor keeps exact contractual names and does
   not learn aliases from invoices or labels. Invoice accuracy remains untested.
