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

## Milestone 3 — Hospital 4 submission, 17 September 2026

Hospital 1 and the original assessment remain frozen. This section is an
independent H4 decision record; detailed evidence is in `hospital_4_review.md`
and `hospital_4_manual_review.md`. Prompt: `prompts/005_hospital_4_submission.md`.

| Question | H4 decision and basis |
|---|---|
| Hospital choice | Choose H4 after inspecting 2–5: existing rule types, one structured source, calendar days, uniform facility/plan rates, no weekend schedule. Defer H2 service-day/episode handling, H3 amendments and H5 multipliers. |
| Grounding | Source-pinned extraction of 31 clauses/160 table rows; reviewed H4 aliases and CW suffix. Match by descriptions only; preserve possible candidates and source evidence. |
| Premium/cap | §5.1: strict `>` premium, all units; §6.1 explicitly excludes excess. One unambiguous line pays min(quantity, cap). Rounding after each step (§4.2). |
| Duplicate correction | H4 forbids duplicates but lacks an allocation convention. Flag group, withhold amounts; equal quantities count once for delivered context, conflicts remain unknown. Do not inherit H1 retention. |
| Cumulative usage | H4 leaves population/reset unspecified. Bounds 0 to original billed contract-term usage; only invariant prices accepted. Unknown units/dates broaden bounds. Contract-term data bounds usage as an explicit working interpretation, no inferred carry-in. |
| Exclusions | Same patient, both date directions and cross-invoice search are explicit (§9.1). Exact N-day endpoints unresolved; only strictly-inside matches certain. First service excluded, not both. |
| Dual billing unit | Preserve “per hour, per item”; quantity and dependent calculations remain unresolved. Never infer validity from price agreement. |
| Identity/dates | Use H4 assessment context and flag printed contract errors independently. Inclusive term dates interpreted; invalid dates/units/joins never automatically zero. |
| Confidence | Existing exposed H1 strict rows: 445/445 correct-class joint successes, 11/12 erroneous. 0.90 × Wilson95 lower bound = 0.892297 / 0.581503. Transfer factor is heuristic; no H4 validation/calibration claim. No H1 retuning. |
| Submission | Exact template, H4 only, unique IDs, known totals, no uncertainty. 370/835 IDs: 361 correct, 9 erroneous. Omit 465 IDs. Overall H2–5 coverage 370/3,942. |
| Verification | 12 new tests plus 71 existing tests; independent review of all 9 erroneous row deltas, 13 line calculations, 3 real endpoint pairs and other review cases. Byte-reproduction check and original/H1 hashes. |
| Scope/time | Complete one conservative hospital pipeline. H2/3/5 engines and adjudication deferred. Prior human time unavailable; do not invent remaining assessment hours. AI assistance disclosed; no runtime AI. |

## Milestone 4 — Jev description-matching pilot, 17 September 2026

Prompt 006 authorizes an exploratory TypeSafe Jev trial; the user subsequently
provided a local .env credential. Synthetic source-data status was verified.
Only description text, reviewed abbreviation definitions and catalogue names were
sent; no prices, billed units, quantities, invoice/patient identifiers or labels.
The key is ignored by Git and never logged. The baseline submission is unchanged.

Pin jev-1.13.0; use all 98 H4 services plus explicit outside-catalogue and
insufficient-information options. Independently preserve ambiguous contractual
units: they are not a description-classification problem. Pre-response reference
judgments are Codex-assisted, not independent human labels. Do not report H1's
exposed holdout as new validation or equate model confidence with invoice confidence.

35 cached responses: 12/12 clear controls agree with review. Of 23 unresolved
strings (194 lines), 16 abstain; seven propose specific services despite missing
qualifiers. None is accepted. All 13 unsupported service combinations receive
insufficient-information rather than outside-catalogue, so this trial provides
no accepted evidence to narrow their dependency context. See the experimental
report for proposal details, exact distributions, cost estimate and limitations.
No thresholds were tuned, no invoice replay was promoted, and no coverage gain is
claimed. A second classifier cannot supply missing evidence; compare alternatives
on reviewed recoverable cases if a further experiment is warranted.

## Milestone 5 — Approved Hospital 4 revisions, 17 September 2026

Prompt: `prompts/008_hospital_4_approved_policy_update.md`. Prior H4 milestones
remain historical; v1 code, policies, results, submission and write-up are archived
in `baselines/hospital_4_v1/` with SHA-256 checks. Original data and H1 freeze remain
unchanged. The preceding investigation (prompt 007) is development analysis of
already-exposed labels, not fresh held-out validation.

| Decision | Implemented policy and limitation |
|---|---|
| Inclusive exclusions | `≤ N`, same patient across invoices, both date directions, first-column service only. Explicit user approval supported by analogous H1 wording and 000847/000211 labels; not direct H4 validation. |
| Exact copies | Earliest eligible lexical ID, including multi-unit copies, only if service/patient/date/quantity/unit/rate/charge agree and eligibility/adjusted rates are consistent and known. Other copies zero; original billing history unchanged. Conflicts remain reviewable. No H1 price-aware policy transfer. |
| Caps | Preserve contractual-cap calculations and otherwise-eligible submission rows, explicitly marked assumption-dependent estimates. Confirm cap violation separately from amount comparisons; no assertion that the cap equals actual delivery. |
| Cap evidence/confidence | H1's four exposed-label cap cases imply below-cap quantities (three conditional residual reconstructions); underlying cause unproven. Keep existing class confidence, add no penalty, claim no cap-specific calibration. Submission sidecar and audit carry assumptions and amount status. |
| Volume | Keep population/reset uncertainty and zero-to-original-billed-term bounds, with term-data upper-bound assumption explicit. Unknown records are not absent. No H1 scope transfer. |
| Units | No new H4 quantity evidence; mismatches and dual unit remain unresolved. No price-derived conversion or blanket typo interpretation. |
| Matching/Jev | No aliases, thresholds, model dependencies or accepted Jev matches changed. Experimental status preserved. |
| Outcome | 370 → 374 rows: +000018/+000069/+000084 correct; +000235 erroneous at 1,518,150 cents. Zero removed rows; zero changed existing amounts/categories/confidence. Three cap estimates retained. 461 H4 IDs omitted. |
| Evidence | Ten formerly unknown line amounts become determined under approved policies; nine invoice evidence records change, four become submissible. Full deterministic comparison in outputs/hospital_4/policy_change_report.json and .md. |
| Verification | Focused endpoint, multi-unit duplicate, conflict/eligibility, cap amount-status and original-history tests; template/source cents/ID/confidence/sum validation; current and archived baseline byte reproduction; manual checks. |

Approved cap amount assumptions are nonblocking only when all other evidence is
sufficient. Unknown or unapproved assumptions cannot pass the submission gate.
No new contract interpretation was needed; remaining scope/unit/quantity questions
are deferred for explicit judgment rather than guessed.

## Milestone 6 — Final all-target-hospital pass, 17 September 2026

Prompt 009 expands the runnable audit to H2–5 and requests final cleanup/deliverables.
User separately approved H2 recorded-date Service Day and H5 invoice-header facility
context. These are recorded as assumptions, not validated facts. H4 v2 is archived
and byte-preserved, including all 374 submission rows; H1 remains frozen.

H2 prose extraction, H3 amendment versions and H5 per-service multiplier schedules
were added through isolated adapters. H2/3/5 discount scope is established by their
own contracts. No H4 cap estimate/duplicate-retention/endpoints convention is
silently transferred. Missing administrative evidence and uncertain exclusion
interpretations are documented in target_hospitals_review.md.

All 49,796 target lines/3,968 headers processed. Submission grows to 1,757 rows
(1,718 correct, 39 erroneous); 2,185 unique IDs omitted. H4 unchanged. Seventeen
new focused tests plus 86 existing tests; 16 new manual line calculations, nine
invoice deltas and nine uncertain cases supplement H4's manual checks. No new
label tuning, Jev acceptance, model calls or calibration claims.

The root README now leads with final reproducible commands. The required short
evaluation and one-page decision log accompany the updated two-page write-up.
History, prompts, baselines and experimental evidence are retained; scratch/cache
artifacts are removed/ignored, and local credentials remain excluded. Prior human
working time is unknown; the assessment time-cap limitation is disclosed.
