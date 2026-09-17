# Contract-grounded invoice auditing

Hospital 1 evaluation preserved; Hospital 4 submitted | 17 September 2026

## Scope and sequencing

Selected Hospital 4 after inspecting Contracts 2-5. It needs the existing rule types: one structured document, calendar service days, uniform facility/plan rates and no weekend uplift. Hospital 2 adds shifted service days and episode context; Hospital 3 adds amendment precedence and effective-date rates; Hospital 5 adds service-specific facility/plan multipliers. This is a comparison of implementation cost, not accuracy. Work stops at one carefully bounded unlabelled hospital. Prior human time is unavailable, so no total-hours or remaining-budget claim is made.

## Grounding and calculation

H4 contract INS-H4-2024-2049 covers 2024-01-01 to 2025-12-31 in GBP. A source-pinned extractor reviews 31 numbered clauses and 160 table rows: 98 services, 18 premiums, 18 caps, 7 bundles, 4 discount tiers and 15 exclusions. The 192 reference rules retain applicability, condition, action, scope, order, source quotes/lines and uncertainty. Structural coverage is not semantic accuracy. Reviewed H4 aliases match descriptions without using prices or units to choose a service; uncertain candidates remain relevant to other invoices.

The frozen engine supplies exact rational arithmetic, integer cents, half-away-from-zero rounding after each step and cross-invoice context. H4 uses its own catalogue, policies and initializer. Order is bundle, facility/plan, premium, deepest discount, then payable quantity. Original billed, delivered and payable quantities are separate. Source invoices are never edited; wrong printed contract numbers do not hide related charges. A tested private adapter bridges the base engine's single H1 header check and restores H4 originals in all public evidence.

## Independent interpretations and abstentions

H4 explicitly makes excess daily quantities nonpayable (section 6.1), supporting partial single-line caps. Qualifying premiums apply to all units with strict greater-than thresholds (section 5.1). Duplicate-group corrections are withheld: H4 has no approved retention convention. Equal duplicate quantities count once for delivered context; conflicting quantities remain unknown. H1's price-aware retention is not transferred.

Exclusions explicitly search the same patient in both date directions across invoices (section 9.1); only the first service is excluded. Exact N-day endpoints remain unresolved. Cumulative population/reset scope is absent: bound usage from zero to original billed contract-term quantities, accepting only invariant rates. This assumes supplied term data bounds usage; carry-in is not evidenced. Unknown units or dates can make the upper bound unbounded. The dual unit "per hour, per item" is not converted. Uncertainty propagates to bundles, exclusions, premiums and discounts; invalid dates or units never imply zero.

## Submission and review

Submission contains 370 H4 rows: 361 correct and 9 erroneous. Coverage is 370/835 distinct H4 IDs (44.31%); 465 IDs, represented by 470 header records, are omitted. Across all H2-5 target IDs coverage is 370/3,942 (9.39%). Omission reasons overlap: 258 IDs have uncertain discounts, 253 unresolved service matching, 100 dual-unit uncertainty, and 50 uncertain exclusions. H2, H3 and H5 are unaudited; H1 is never submitted.

Manual review checks all nine erroneous invoice deltas, 13 line calculations and three real endpoint pairs. Example: 3,975 x 1.15 rounds to 4,571 before multiplying by 34, giving 155,414 cents. A 13-unit transfusion line capped at eight pays 8 x 8,450 = 67,600. A wrong-contract invoice remains flagged while its expected 763,938 cents equals billed. Actual seven-, ten- and 21-day exclusion pairs stay unresolved. Cross-invoice bundle and strictly-inside exclusion paths use synthetic fixtures because no certain applied example was found in this H4 run. Detailed evidence: docs/hospital_4_manual_review.md.

<!-- pagebreak -->

# Evaluation, confidence and reproducibility

## Frozen Hospital 1 evidence

The original split remains unchanged: 717 development IDs and 196 held-aside IDs. Development detected 44/44 erroneous invoices, with zero invoice-level false positives; decisive coverage was 398/717 and known expected amounts were exact in 363/363 cases. Held-aside detected 12/14 erroneous invoices, with zero false positives; decisive coverage was 103/196 and 93/94 known amounts were exact. Two errors were review-only, not accepted as correct. The held-aside labels are now exposed: no retuning or fresh-holdout claim is made.

Grouped category results below are TP / FP / FN against existing label mappings. Multiple categories overlap; category false positives on already-erroneous invoices do not imply invoice-level false positives. Full per-label counts, precision, recall and examples remain in outputs/hospital_1/evaluation_*.json and .md.

| Category | Development TP / FP / FN | Held-aside TP / FP / FN |
|---|---|---|
| Pricing | 21 / 0 / 1 | 4 / 0 / 1 |
| Arithmetic | 9 / 5 / 0 | 2 / 0 / 0 |
| Dates | 10 / 5 / 0 | 5 / 0 / 0 |
| Billing unit | 8 / 1 / 0 | 2 / 0 / 1 |
| Daily caps | 3 / 0 / 0 | 1 / 0 / 0 |
| Duplicate service | 3 / 0 / 0 | 1 / 0 / 0 |
| Duplicate invoice ID | 5 / 0 / 0 | 0 / 0 / 0 |
| Exclusions | 2 / 0 / 1 | 1 / 0 / 0 |
| Contract identity | 3 / 0 / 0 | 2 / 0 / 0 |
| Uncontracted service | 0 / 0 / 10 | 0 / 0 / 2 |

## Systematic failure types

Matching abstentions: unresolved descriptions can prevent detecting a specific violation (INV-H1-000657, wrong unit; 000667, unknown service). Context propagation: one uncertain record can block later discounts or exclusions (000038, 000045), reducing coverage. Ambiguous records: repeated headers and invalid dates prevent defensible joins or quantities (000068, 000148); other violations may still be known. Correction interpretation: cap invoice 000015 was detected, but expected 1,210,600 differed from labelled 1,195,825 by 14,775 cents. This remains an acknowledged frozen mismatch, not a target for post-holdout tuning.

## Proposed numerical confidence

Use already-exposed H1 rows passing the strict submission gate: unique ID, known total, decisive flag and no uncertainty. Joint success requires both flag and exact expected cents. Correct predictions have 445/445 successes; erroneous predictions have 11/12. Per predicted class use 0.90 x the Wilson 95% lower bound (z=1.96), rounded to six decimals: 0.892297 for correct and 0.581503 for erroneous H4 rows. This explicitly incorporates the small error sample and cap mismatch. The 0.90 transfer factor is a declared heuristic, not fitted calibration. Correlated invoices limit interval interpretation; categories are not separately calibrated. No H4 labels exist, so these scores are unvalidated and no H4 accuracy is claimed.

## Verification and delivery

Twelve H4 tests and 71 existing tests pass. Checks cover threshold/rounding boundaries, cross-invoice context, duplicate interactions, caps, unit uncertainty, H4 identity, and submission tampering. Run python3 -m hospital_4, python3 -m hospital_4.manual_check, then python3 -m hospital_4 --check. Python 3.9+ standard library is sufficient. Byte comparisons verify the submission and all generated H4 evidence; source/H1 hashes protect preserved work. Validation enforces the exact template, unique IDs, original billed cents, integer expected line sums, defensible flags and finite confidence. No network or runtime AI is used.

README documents all commands. Outputs include submission.csv, rules, audit evidence, omissions, confidence and manifests. Prompts 001-005 disclose AI-assisted development; H4 policy/review and the decision log record assumptions separately. The optional PDF builder has a pinned dependency. Unfinished work: resolve contract gaps and omitted records, audit H2/3/5, and validate confidence on new labels. Prioritize clarification before expanding coverage.
