# Extractor interface

The boundary for the Hospital 1 engine is `outputs/hospital_1.rules.json`, schema
version `1.1`. This is an extraction representation, not an implementation of
your calculation engine.

## Rule envelope

| Field | Meaning |
|---|---|
| `id` | Rule identity within this extraction. Clause IDs follow source numbering; table IDs follow source row order. Table IDs may change when rows are inserted. |
| `kind` | Catalogue, premium, discount, bundle, restriction, definition, etc. |
| `applies_to` | Exact service name(s) or the entity being constrained. No inferred invoice aliases. |
| `condition` | Metric, comparison operator, threshold, date predicate or grouping eligibility. |
| `action` | Rate, multiplier, definition, calculation step or violation flag. Money is integer cents; multipliers use integer numerator/denominator. |
| `scope` | Hospital, grouping keys, population, period and counting instructions where relevant. The containing contract supplies identity and dates. |
| `order` | Stage, prerequisites and numbered position for rate/calculation stages. Validation timing is separate and unnumbered. |
| `source` | List of document paths, hashes, sections, line spans and exact quotations supporting the rule. |
| `uncertainty` | `explicit`, `interpretation`, `implementation_convention` or `unresolved`; interpretation, questions and resolution. Applied conventions preserve `contract_ambiguities`, `contract_interpretation` and `policy_references`. No uncalibrated confidence percentage. |
| `ready_for_engine` | False if extraction has any blocking diagnostics or this record has unresolved questions. True is a parsing/review status, not a claim that an engine exists. |

Catalogue rows preserve `service_name`, `unit_basis`, `base_rate_cents`,
`currency` and `daily_cap`. A null cap means no cap is listed for the service;
it does not mean zero. A null condition or correction policy is unspecified,
not permission to choose a default.

`source.line_start` and `source.line_end` are one-based. The current Markdown
parser produces single-line spans for clauses and rows. The whole-document
SHA-256 pins those coordinates to the source bytes. Quotes preserve Markdown,
including table pipes and emphasis. `extractor.profile_sha256` records the
reviewed semantic profile used for the extraction. The top-level
`implementation_policy` includes the separate policy document, its hash, user
prompt path and hash, and all convention values. Contract quotes are never
altered to imply that implementation assumptions came from the contract.

## Consumption rules

Reject the full contract if `status` is `blocked` or diagnostics are nonempty.
Do not execute a record with unresolved fields. The contract-level
`ready_for_engine` is false while any record remains unresolved. Any later
policy resolution should be versioned separately with its rationale and source;
do not disguise an engine assumption as explicit contract language. The default
output applies `hospital_1_user_conventions_v1` and has status
`extracted_with_assumptions`. `--contract-only` (or Python
`extract(policy_path=None)`) omits conventions and retains raw ambiguities.

Readiness covers contract extraction and documented policy resolution. It does
not certify invoice correctness or decide conflicts in actual billing records.
Before processing changed data, run the line-ID validator; `review_required`
means the format/order assumption must be reviewed. Validation is separate from
the contract parser and its report is pinned to dataset hashes.

Some global definition/grouping records explain table rules. Do not apply a
global explanatory record and its concrete service rule as two adjustments.
Use the catalogue for base rates and concrete service rules for adjustments;
use the global records for definitions, grouping, sequencing and validation.

Volume tiers use strict `>` against prior billed units, select one deepest
qualifying discount, and apply that rate to the current line as a whole.
Daily premiums use delivered service/patient/day totals. The prompt 003 policy
specifies that duplicate charges are counted once, with conflicting quantities
left uncertain. A qualifying premium applies to all applicable units. The raw
contract profile is preserved; applied premium rules are marked as an
implementation convention and use `delivered_daily_quantity_excluding_duplicates`.

For exclusion rules, `direction: both` refers to dates either side of the
trigger. It does not make the service exclusion reciprocal. Only the
first-column service is marked not billable. Applied conventions set `operator`
to `<=`, `same_patient` to true, and scope to the same patient across all
invoices. The excluded charge's expected payable amount is zero, not a discount.

## Correction policy handoff

`implementation_policy.decisions.corrections` supplies shared controls:
preserve original lines/amounts, use adjusted contract rates for pricing
compliance, and flag indefensible allocations for review. The indeterminate
expected amount is null, never a forced zero. Concrete cap/duplicate rules
include `action.correction_policy`, with a reference to those shared controls.

Caps allocate earlier eligible units first using lexical line-ID order, retaining
the allowed portion of a partially excess line. Duplicates retain one eligible
occurrence, prioritizing adjusted-rate compliance and then lexical line ID.
If no occurrence complies and the service remains payable, correct the earliest
occurrence's price; other duplicate occurrences receive zero expected payable.
Neither convention restores payability to an excluded service. If conflicting
quantities or evidence prevent defensible correction, stop allocation for review.

Cumulative counting uses original billed quantities including all prior
duplicate/disallowed units. It remains independent of payable corrections.
These structures describe policies consumed by `hospital_audit/engine.py`; the
calculated invoice results are separate in `outputs/hospital_1/`. Do not treat
`expected_payable_cents: 0` in an exclusion action
as unconditional: it applies only when that rule's condition matches.

## Extension policy

To support changed prose, add a reviewed template with an explicit semantic
interpretation and independent tests. To support another layout/hospital, use a
separate profile or parser. Do not regenerate the accepted prose allowlist from
an arbitrary input document: that would remove the change-detection protection.

The source snapshot is immutable assessment input; the development profile is
separate. Invoice descriptions and labels do not participate in extraction.
The engine verifies that the generated reference matches a fresh extraction;
its implementation rejects unsupported changes to core conventions rather than
silently running a different policy.
