# Decision log — milestone 1

Date: 14 September 2026. Scope: Hospital 1 contract extraction only.

| Decision or ambiguity | Reading / action | Evidence |
|---|---|---|
| Start with a narrow deterministic baseline | Parse Markdown tables and exact reviewed prose. No runtime AI, OCR or external lookup. Unknown language blocks extraction. | User instruction; supplied Markdown |
| Preserve input and provenance | Clone upstream; copy its assessment files unchanged into this repo; record commit and file hashes. Retain this repo's original remote. | `data/assessment/SOURCE.json` |
| Units may look unusual | Preserve the exact unit basis; do not infer it from a service name. | §2.3; §4 |
| Strict boundaries and prior usage | Use `>`, exclude the current line, never split a line at a volume threshold, select the deepest eligible tier without stacking. | §2.4; §7 headers; §7.2 |
| Daily grouping versus duplicate restriction | Preserve both: aggregate service/patient/day quantities for premiums/caps, and independently flag duplicate billing. | §5.1; §8; §11.4 |
| Term endpoints | Record inclusive effective/expiry dates as an interpretation. Invoice dates themselves are not constrained to the term. | §1.1; §11.3 |
| Weekend definition | Saturday/Sunday only; no additional holiday calendar. | §2.2 |
| Exclusion endpoints and patient scope | User-approved assumptions: `≤ N`, same patient across all invoices. Original ambiguity remains recorded. Excluded charge receives zero expected payable amount. | §10; §10.1; prompt 002 |
| Exclusion direction | Both temporal directions; only first-column service excluded, not reciprocal exclusion of the pair. | §10 table; §10.1 |
| Ascending line identifiers | Use lexical text order. Validated all 61,211 IDs in each of CSV and JSONL across five hospitals: fixed widths, identical identifier sets, no duplicates or format exceptions, lexical/natural agreement. Revisit only on exceptions. | §7.2; prompt 002; `outputs/line_id_validation.json` |
| Invalid billed usage | Include all prior original billed quantities, including duplicate and disallowed units. Do not subtract rejected quantities or calculated corrections. | §2.4; §7.1; prompt 002 |
| Daily cap allocation | Retain earlier eligible units by ascending lexical line ID; remove latest excess; reduce partially excess lines' payable quantity. | §8; user convention in prompt 002 |
| Duplicate retention | Prefer an eligible occurrence compliant with adjusted contract pricing; break ties lexically. If none comply but service remains payable, retain earliest and correct price. Other duplicates receive zero expected payable amount. | §11.4; user convention in prompt 002 |
| Pricing and uncertainty | Compliance includes applicable bundles, premiums and discounts. If differing quantities or conflicting evidence prevent a defensible correction, flag review without forcing an allocation. | §§3–9; prompt 002 |
| Preserve originals | Never modify invoice lines or billed amounts. Violations remain flagged; corrections apply only to calculated expected payable fields. | Prompt 002 |
| Report evidence honestly | 206/206 recognized nonempty lines is structural coverage. No invoice precision/recall or semantic-accuracy percentage yet. | Extraction output; tests |
| AI assistance | Codex assisted development and initial clause interpretation; no AI is called by the extractor. User prompt is preserved. | `prompts/001_hospital_1_extraction.md` |

User decisions are versioned separately in `policies/hospital_1.json`, with
prompt provenance. The original 27 unresolved records remain available through
`--contract-only`; the default output applies documented assumptions and passes
the policy-readiness gate. Case-specific conflicts still require review.

The above records milestone 1. Milestone 2 is recorded below.

## Milestone 2 — Hospital 1 engine, 15 September 2026

| Decision | Implementation | Authority |
|---|---|---|
| Unit mismatch | Flag it and leave compatible quantity/expected amount unresolved. No conversions or price-based inference. | Prompt 003, decision 1 |
| Delivered premium quantity | Equal-quantity duplicates count once; conflicting records leave delivered quantity and premium eligibility unknown. A qualifying premium applies to all units. | Prompt 003, decisions 2 and 7 |
| Three quantities | Keep original billed, delivered and expected payable quantities separately. Non-payable services may still establish delivery. | Prompt 003, decision 3 |
| Processing | Match and validate; gather global context and exclusions; establish delivered quantities; calculate rates; select retained duplicates; apply caps; calculate amounts. | Prompt 003, decision 3 |
| Applicable contract | Audit/group under the Hospital 1 assessment context; separately flag a wrong printed contract number. | Prompt 003, decision 4 |
| Propagation | Preserve candidate service sets; use possible presence for bundles/exclusions and lower/upper billed-usage bounds for discounts. Unknown quantities are not zero. | Prompt 003, decision 5 |
| Violations versus amounts | Known violations can yield an erroneous decision with an unknown total. Invalid dates and uncertain units are not zeroed. Wrong contract numbers do not erase pricing context. | Prompt 003, decision 6 |
| Matching | Inspected development descriptions; reviewed abbreviation expansions; accept only one supported catalogue candidate. Ignore NG suffixes and word order; never use prices/units to choose a service. | Prompt 003; `hospital_1_aliases.json` |
| Duplicate attribution | Keep group evidence on all occurrences. Once retention is defensible, attribute duplicate-charge violations to discarded occurrences; retain other violations on the chosen one. If retention is ambiguous, flag all involved records for review. | Approved retention policy; development failure analysis |
| Unknown inputs | Malformed/reused joins and uncertain identifiers remain reviewable. Record validation failures without guessing a header or quantity. | Prompt 003 evidence requirement |
| Held-aside protocol | Reserve invoice IDs where the first 8 SHA-256 hex digits modulo 5 equal zero. Inspect only development descriptions/labels before freezing. All records still provide mandatory cross-invoice context. | Validation scope |
| Confidence | Output null confidence; measured precision/recall do not imply probability calibration. | User instruction |

Development inspection found that attributing a duplicate-charge violation to
the retained, otherwise valid occurrence produced two false-positive invoices.
The attribution was corrected and tested before the implementation freeze.
No alias/price adjustments were made from held-aside labels. The frozen
evaluation remains unchanged after observing its two review-only errors and
one expected-amount mismatch.

Completed: working Hospital 1 pipeline, 63 tests, generated evidence and separate
development/held-aside evaluations. Unresolved records are in the review log;
they are not falsely accepted. Hospitals 2–5, runtime AI and final submissions
remain outside scope. See `docs/hospital_1_engine.md` for the measured limits.
