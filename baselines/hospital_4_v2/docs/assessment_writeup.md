# Contract-grounded invoice auditing

Hospital 1 evaluation preserved; Hospital 4 approved-policy update | 17 September 2026

## Scope and sequencing

Selected Hospital 4 after inspecting Contracts 2-5. It needs the existing rule types: one structured document, calendar service days, uniform facility/plan rates and no weekend uplift. Hospital 2 adds shifted service days and episode context; Hospital 3 adds amendment precedence and effective-date rates; Hospital 5 adds service-specific facility/plan multipliers. This is a comparison of implementation cost, not accuracy. Work stops at one carefully bounded unlabelled hospital. Prior human time is unavailable, so no total-hours or remaining-budget claim is made.

## Grounding and calculation

H4 contract INS-H4-2024-2049 covers 2024-01-01 to 2025-12-31 in GBP. A source-pinned extractor reviews 31 numbered clauses and 160 table rows: 98 services, 18 premiums, 18 caps, 7 bundles, 4 discount tiers and 15 exclusions. The 192 reference rules retain applicability, condition, action, scope, order, source quotes/lines and uncertainty. Structural coverage is not semantic accuracy. Reviewed H4 aliases match descriptions without using prices or units to choose a service; uncertain candidates remain relevant to other invoices.

The frozen engine supplies exact rational arithmetic, integer cents, half-away-from-zero rounding after each step and cross-invoice context. H4 uses its own catalogue, policies and initializer. Order is bundle, facility/plan, premium, deepest discount, then payable quantity. Original billed, delivered and payable quantities are separate. Source invoices are never edited; wrong printed contract numbers do not hide related charges. A tested private adapter bridges the base engine's single H1 header check and restores H4 originals in all public evidence.

## Independent interpretations and abstentions

H4 makes excess daily quantities nonpayable (section 6.1). Cap violations can therefore be confirmed, but min(quantity, cap) is an approved assumption-dependent correction, not established actual delivery. Keep otherwise-eligible cap estimates with separate amount-assumption evidence. Premiums apply to all units above strict thresholds (section 5.1). For exact duplicate copies, retain the earliest eligible lexical line ID, including multi-unit copies; service, patient, date, quantity, unit and charge must agree. Conflicting quantities, rates or eligibility remain unresolved. H1's broader price-aware retention is not transferred.

Exclusions search the same patient in both date directions across invoices; exclude only the first-column service. Prompt 008 approves inclusive N-day endpoints, supported by analogous H1 wording and labelled examples, not direct H4 validation. Cumulative population/reset scope remains unspecified: bound usage from zero to original billed contract-term quantities and accept only invariant rates. This assumes supplied term records bound usage; carry-in is not evidenced. Unknown prior units/dates can make the upper bound unbounded. Wrong units need individual quantity evidence; prices cannot establish quantities. The dual unit "per hour, per item" remains unresolved. Uncertainty propagates through dependent rules.

## Submission changes and manual review

Submission increases from 370 to 374 H4 rows: 364 correct, 10 erroneous. Coverage is 374/835 distinct H4 IDs (44.79%); 461 IDs / 466 header records remain omitted. Overall H2-5 coverage is 374/3,942 (9.49%). There are no removals and no changes to existing submitted amounts, categories or confidence. Newly correct invoices 000018, 000069 and 000084 retain exact-copy charges of 143,000, 813,875 and 731,350 cents; their totals are 1,493,475, 3,522,700 and 4,715,550. Invoice 000235 now excludes 20,200 cents at the 21-day endpoint: expected 1,518,150 versus billed 1,538,350, with its wrong-contract flag retained.

Ten previously unknown line amounts become determined under the approved policies. Other affected invoices remain omitted: endpoint targets 000168/000473/000658 and discarded copies on 000309/000473/000693 still have independent blockers. Omission reasons overlap: 258 IDs have uncertain discounts, 253 unresolved matching, 100 dual-unit uncertainty, 46 uncertain exclusions and 11 ordinary unit mismatches. Matching thresholds and aliases are unchanged. Jev remains experimental with no accepted mappings or runtime dependency. H1 is excluded from submission; H2/3/5 remain unaudited.

Manual checks replay all ten erroneous invoice deltas, 20 line calculations, four endpoint pairs, three added correct invoices and three submitted cap estimates. Example: round 3,975 x 1.15 to 4,571, then multiply by 34 =155,414 cents. Cap rows 000165/000540/000554 retain estimated totals 3,370,925 / 2,120,125 / 3,465,160 cents. Their violations are confirmed; corrected amounts are assumption-dependent. Source records and the v1 baseline remain intact. Detailed evidence: hospital_4_manual_review.md and policy_change_report.json.

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

Matching abstentions: unresolved descriptions can prevent detecting a specific violation (INV-H1-000657, wrong unit; 000667, unknown service). Context propagation: one uncertain record can block later discounts or exclusions (000038, 000045), reducing coverage. Ambiguous records: repeated headers and invalid dates prevent defensible joins or quantities (000068, 000148); other violations may still be known. Correction interpretation: cap invoice 000015 was detected, but expected 1,210,600 differed from labelled 1,195,825 by 14,775 cents. Development analysis of all four exposed-label cap cases implies below-cap quantities; three residual reconstructions involve other unresolved lines. No same-patient/day records explain the discrepancy. Latent original quantities are a hypothesis, not proven; the frozen engine is not retuned.

## Proposed numerical confidence

Use already-exposed H1 rows passing the strict submission gate: unique ID, known total, decisive flag and no uncertainty. Joint success requires both flag and exact expected cents. Correct predictions have 445/445 successes; erroneous predictions have 11/12. Per predicted class use 0.90 x the Wilson 95% lower bound (z=1.96), rounded to six decimals: 0.892297 for correct and 0.581503 for erroneous H4 rows. The sample includes the frozen cap mismatch. Cap estimates keep this class score with no invented penalty; it is not cap-specific confidence in the corrected amount. The 0.90 transfer factor is a declared heuristic, not fitted calibration. Correlated invoices limit interval interpretation; categories are not separately calibrated. No H4 labels exist, so these scores are unvalidated and no H4 accuracy is claimed.

## Verification and delivery

Fifteen H4 tests and 71 existing tests pass. Checks cover threshold/rounding boundaries, cross-invoice context, identical multi-unit copies, conflicting eligibility, cap amount assumptions, unit uncertainty, H4 identity, and submission tampering. Run python3 -m hospital_4, python3 -m hospital_4.manual_check, then python3 -m hospital_4 --check. Python 3.9+ standard library is sufficient. Byte comparisons verify all H4 evidence and submission; source/H1 hashes protect preserved work. scripts/check_hospital_4_baseline.py reproduces the archived v1 pipeline separately. Validation enforces the exact template, unique IDs, original billed cents, integer expected line sums, defensible flags, approved cap estimates and finite confidence. No network or runtime AI is used.

README documents all commands. Outputs include submission.csv, rules, audit evidence, omissions, confidence, before/after comparison and manifests. submission_evidence.jsonl separates confirmed violations, amount-dependent comparisons and correction assumptions. Prompts 001-008 disclose requests and AI-assisted development; policies and the decision log record approvals. The optional PDF builder has a pinned dependency. Unfinished work: resolve contract gaps and omitted records, audit H2/3/5, and validate confidence on new labels. Prioritize clarification before expanding coverage.
