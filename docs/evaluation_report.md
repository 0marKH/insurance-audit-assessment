# Evaluation and error analysis

Hospital 1 is the only labelled hospital. Its original implementation and results
remain frozen: 717 development IDs and 196 originally held-aside IDs. All labels
are now exposed; no final-stage retuning or fresh-holdout claim is made.

Development: 44/44 erroneous invoices detected, zero invoice-level false positives;
398/717 decisions (55.51%); known expected totals exact in 363/363 cases (amount
coverage 50.63%). These conditional results do not imply full-dataset accuracy.
Historical held-aside: 12/14 errors detected, zero invoice-level false positives;
103/196 decisions; 93/94 known totals exact. Two errors stayed under review.

## Per-category performance on development data

Grouped categories follow the frozen evaluator's explicit label mapping. Counts
are TP / FP / FN for category identification, not merely any error on the invoice.
Category false positives may occur on an already-erroneous invoice.

| Category | TP / FP / FN | Precision | Recall |
|---|---|---:|---:|
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

Full per-label counts, mappings and original split results are in
`outputs/hospital_1/evaluation_development.{md,json}` and
`outputs/hospital_1/evaluation_held_aside.{md,json}`. The comparison script joins
saved predictions and labels without changing the engine.

## Four systematic failure types

1. **Insufficient description evidence.** Missing qualifiers cannot reliably
   distinguish contracted or uncontracted services. H1-000657 remains uncertain
   despite a wrong-unit label; 000667 illustrates an unidentified unknown service.
   No amount/price-based service choice is made. These are exposed-label examples.
2. **Uncertainty propagates through shared context.** An uncertain prior record
   can block later volume discounts or exclusion decisions (H1-000038/000045).
   Ignoring it would raise coverage by silently assuming zero usage. In H2/3/5,
   explicit scope permits some deepest-tier invariant results despite unknown
   upper bounds; H4's scope remains unresolved.
3. **Identity, dates and quantity conflicts.** Repeated headers, malformed dates
   and incompatible units prevent defensible joins or conversions (H1-000068/
   000148). Known violations and unknown totals are separate outcomes, not zero
   reimbursements or accepted correct invoices.
4. **Violation does not establish the correction.** H1-000015 is a detected cap
   violation, but the cap-based 1,210,600 cents differs from labelled 1,195,825 by
   14,775. Exposed-label investigation of four cap cases suggests lower underlying
   quantities; that explanation is unproven. H4's three estimates remain explicitly
   approved assumptions; new hospitals' cap corrections are withheld.

## Target coverage and confidence

Final submission: H2 492/1,125, H3 425/932, H4 374/835, H5 466/1,050; total
1,757/3,942 (44.57%), with 1,718 correct and 39 erroneous predictions. All target
records are processed, but 2,185 IDs are omitted. No labels exist for these
hospitals, so manual review and tests do not establish target accuracy.

Confidence preserves the existing class heuristic from exposed H1 strict rows:
445/445 correct-class and 11/12 erroneous-class joint flag/exact-amount successes.
`0.90 × Wilson95 lower bound`, z=1.96, gives 0.892297 / 0.581503. The transfer factor
is heuristic, invoices are correlated, and neither target hospitals nor cap amounts
are calibrated. No new numerical penalty is invented. See the final confidence
method and submission-evidence sidecar for assumptions and limitations.
