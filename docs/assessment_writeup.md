# Contract-grounded invoice auditing

Final Hospitals 2-5 submission | 17 September 2026 | Hospital 1 evaluation frozen

## Scope, sequence and delivery

I chose a simple deterministic rules engine, supplied its architecture and rule format, and approved the uncertainty and correction policies. I started with Hospital 1, approved Hospital 4 after Codex recommended its simpler contract, then expanded the scope to Hospitals 2, 3 and 5. Codex built the extractors, matcher, engine adapters, tests, evaluation and submission tooling, and drafted documentation. All 49,796 target lines and 3,968 headers were processed; unsupported financial decisions remain unresolved.

| Hospital | Submitted / unique IDs | Correct / erroneous | Coverage |
|---|---|---|---|
| 2 | 492 / 1,125 | 481 / 11 | 43.73% |
| 3 | 425 / 932 | 417 / 8 | 45.60% |
| 4 | 374 / 835 | 364 / 10 | 44.79% |
| 5 | 466 / 1,050 | 456 / 10 | 44.38% |
| Total | 1,757 / 3,942 | 1,718 / 39 | 44.57% |

The exact six-column submission contains both correct and erroneous opinions. The 2,185 omitted IDs retain overlapping reasons in outputs/final/omitted_invoices.csv. H4's previous 374 rows are unchanged; H2/3/5 add 1,383 rows. No target-hospital labels exist, so coverage is not accuracy. H1 is not submitted.

## AI assistance and exploratory classification

Codex inspected contracts and data and performed the source-based manual calculation checks, then implemented their scripted replay. These checks were not independent human adjudication. I initiated a TypeSafe Jev trial and later stopped that work. Codex tested jev-1.13.0 on 12 clear controls and 23 unresolved descriptions: all controls agreed with Codex-assisted references; unresolved cases yielded 16 abstentions and seven unsupported proposals. No new mappings were accepted. The trial was exploratory, not validated accuracy. Its working files were removed during cleanup; prompt 006 and Git history preserve disclosure and evidence.

## Grounding and calculation

Source-pinned references retain applicability, conditions, actions, scope, order, exact source text and uncertainty. H2 has 76 prose service clauses with embedded rules; reciprocal bundle rates are cross-checked. H3 has 118 original services, seven amended rates and two additions effective by service date from 2025-01-01. H5 has 84 services with separate facility and plan multiplier schedules. H4 retains its reviewed 98-service reference. Description matching uses inspected abbreviations and hospital-specific suffix removal; prices and billed units never choose a service. Acceptance thresholds are unchanged; no runtime model or experimental mappings are used.

Cross-invoice context precedes pricing. Original billed history, inferred delivered quantities and payable quantities remain separate. Rates follow bundle substitution, facility, plan, premiums/weekend uplifts, then deepest qualifying discount. Exact rational arithmetic rounds half away from zero to integer cents after each rate step, before quantity multiplication. H2/3/5 expressly define whole-term/all-patient volume scope; uncertain prior records widen bounds rather than disappear. H3 selects amended rates by service date, not invoice date. H5 applies and rounds facility and plan multipliers separately.

## Assumptions and limits

I approved H2's recorded service date as its Service Day because 07:00-boundary timestamps are absent, and H5's header facility code as line context because line-level codes are absent. These assumptions appear in evidence. H4 keeps approved inclusive same-patient bidirectional exclusions and earliest eligible lexical retention of exact copies; conflicting copies remain unresolved. H4 population/reset scope stays uncertain. Its three cap-corrected rows (000165/000540/000554) are explicitly assumption-dependent estimates, separated from confirmed cap violations.

H2/3/5 do not inherit H4's cap correction or duplicate allocation convention: affected amounts are withheld. H2 exclusions explicitly specify same patient and both directions; exact endpoints remain uncertain. H3/H5 positive exclusion cases are withheld because population/direction/endpoints are not explicit; same-patient candidate searching is a documented limitation. Wrong units and all dual-unit ambiguities remain unresolved. Operational compliance involving clinical records, actual submission timestamps, settlement or waivers cannot be established from invoice tables. H2's 60-day submission clause is screened without fabricating a submission date or automatic rejection.

<!-- pagebreak -->

# Evaluation and reproducibility

## Frozen Hospital 1 evidence

Original development: 717 IDs, 44/44 errors detected, zero invoice-level false positives, 398/717 decisions and 363/363 known expected totals exact. Historical held-aside: 196 IDs, 12/14 errors detected, zero false positives, 103/196 decisions and 93/94 known totals exact. Two errors remained under review. Labels are now exposed; no fresh-holdout claim or final-stage rule tuning is made. The grouped development category results below measure category identification; category false positives can occur on already-erroneous invoices.

| Category | Development TP / FP / FN | Precision | Recall |
|---|---|---|---|
| Pricing | 21 / 0 / 1 | 100% | 95.45% |
| Arithmetic | 9 / 5 / 0 | 64.29% | 100% |
| Dates | 10 / 5 / 0 | 66.67% | 100% |
| Billing unit | 8 / 1 / 0 | 88.89% | 100% |
| Daily caps | 3 / 0 / 0 | 100% | 100% |
| Duplicate service | 3 / 0 / 0 | 100% | 100% |
| Duplicate invoice ID | 5 / 0 / 0 | 100% | 100% |
| Exclusions | 2 / 0 / 1 | 100% | 66.67% |
| Contract identity | 3 / 0 / 0 | 100% | 100% |
| Uncontracted service | 0 / 0 / 10 | Not measurable | 0% |

## Four systematic failure types

Insufficient descriptions: missing qualifiers prevent defensible matching or unknown-service identification (H1-000657/000667). Shared uncertainty: unknown prior records affect later discounts and exclusions (000038/000045). Ambiguous records: repeated headers, malformed dates or wrong units block identity/quantity correction (000068/000148). Correction uncertainty: cap invoice 000015 was detected, but calculated 1,210,600 differs from labelled 1,195,825 by 14,775 cents. Exposed-label investigation of four cap cases suggests below-cap quantities; three residual reconstructions involve other unresolved lines, and the explanation is unproven. H4's estimates are approved, not validated; new hospitals' cap corrections remain withheld.

## Numerical confidence

Keep the existing exposed-H1 class heuristic. Strict unique-ID rows with known amounts give 445/445 correct-class and 11/12 erroneous-class joint flag/exact-amount successes. Use 0.90 times the Wilson 95% lower bound, z=1.96: 0.892297 for correct and 0.581503 for erroneous rows. The 0.90 transfer factor is a declared heuristic. Correlated invoices, new contract interpretations and category errors limit interpretation. No target-hospital or cap-specific calibration, validated probability, or invented extra penalty is claimed. Submission evidence distinguishes context assumptions and H4 cap estimates from confirmed violations.

## Verification and handover

103 tests cover extraction, original H1 behavior, amendment dates, new services, multipliers, per-step rounding, thresholds, cross-invoice bundles/exclusions, duplicate/cap safeguards, unit propagation and submission tampering. Codex's H2/3/5 checks replay 16 source-based line calculations, nine invoice deltas and nine uncertain cases; H4's existing 20 line calculations, ten erroneous deltas and boundary/cap checks are preserved. Example: H5-L00132-04 rounds 431,375 x1.05 to 452,944, then x.90 to 407,650 cents. These checks are not hidden-label validation.

Run python3 -m assessment_audit, then python3 scripts/verify_assessment.py. Python 3.9+ standard library suffices; PDF-only dependencies are pinned separately. Reproduction checks exact columns, identifiers, original billed cents, integer expected line sums, flags, confidence and output hashes. Source data and H1 remain hash-protected; previous H4 snapshots remain in Git history. Versioned prompts disclose AI assistance and my approvals. README links the evaluation report, decision log, evidence and omissions. Unresolved evidence and target confidence validation remain open.

## What I would do with another week.

I tried to keep this auditing as simple as possible for the time constraints and the limited clarity around it, if i had more time i will try to research a possibly of training a ML models or deploying ones to help the engine, as I said the results clearly favors the uncertainty more, but that was the objective that we can met in this time.
