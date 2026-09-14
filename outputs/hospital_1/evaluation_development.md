# Hospital 1 evaluation — development

Development descriptions and labels informed implementation. Held-aside labels were reserved until the implementation freeze; all invoice records still supply cross-invoice contractual context. The split is by invoice ID, not an independent hospital or patient cohort.

Duplicate header records are consolidated by ID for label scoring; their amount remains unresolved. Missing predictions count as review. Review is never counted as correct.

| Measure | Result |
|---|---:|
| decision coverage | 55.51% (398/717) |
| known error precision | 100.00% (44/44) |
| known error recall including abstentions | 100.00% (44/44) |
| accuracy on decided invoices | 100.00% (398/398) |
| expected amount coverage | 50.63% (363/717) |
| exact expected amount accuracy when known | 100.00% (363/363) |
| Mean absolute error on known amounts | 0/363 cents |

Amounts are evaluated only where the engine can establish them. Conditional accuracy is not full-dataset accuracy. No numeric confidence scores or calibration claims are made.

## Per-category invoice detection

These rows measure whether an invoice with the given label category has any known violation. They do not claim exact identification of each injected category. Multi-label invoices appear in multiple rows.

| Label category | Invoices | Known error detected | Review only | Incorrectly accepted | Known amounts | Exact amounts |
|---|---:|---:|---:|---:|---:|---:|
| bundle_not_applied | 4 | 4 | 0 | 0 | 2 | 2 |
| contract_number_mismatch | 3 | 3 | 0 | 0 | 2 | 2 |
| cross_invoice_duplicate | 3 | 3 | 0 | 0 | 2 | 2 |
| daily_cap_exceeded | 3 | 3 | 0 | 0 | 0 | 0 |
| duplicate_invoice_id | 5 | 5 | 0 | 0 | 0 | 0 |
| exclusion_window_violation | 3 | 3 | 0 | 0 | 1 | 1 |
| invoice_total_mismatch | 4 | 4 | 0 | 0 | 1 | 1 |
| line_total_arithmetic | 6 | 6 | 0 | 0 | 0 | 0 |
| malformed_service_date | 5 | 5 | 0 | 0 | 0 | 0 |
| premium_incorrectly_applied | 5 | 5 | 0 | 0 | 2 | 2 |
| premium_omitted | 3 | 3 | 0 | 0 | 0 | 0 |
| service_date_after_invoice_date | 3 | 3 | 0 | 0 | 0 | 0 |
| service_date_out_of_window | 2 | 2 | 0 | 0 | 0 | 0 |
| unit_price_mismatch | 8 | 8 | 0 | 0 | 4 | 4 |
| unknown_service | 10 | 10 | 0 | 0 | 0 | 0 |
| volume_discount_incorrectly_applied | 2 | 2 | 0 | 0 | 1 | 1 |
| volume_discount_omitted | 4 | 4 | 0 | 0 | 1 | 1 |
| wrong_unit_basis | 8 | 8 | 0 | 0 | 0 | 0 |

## Grouped category detection

Categories are mapped explicitly in hospital_audit/evaluate.py. Pricing groups bundles/premiums/discounts/rate errors; arithmetic groups line/invoice arithmetic. Unknown-service matching is conservatively reviewed rather than asserted as an uncontracted charge.

| Category group | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---|---|
| pricing | 21 | 0 | 1 | 100.00% (21/21) | 95.45% (21/22) |
| arithmetic | 9 | 5 | 0 | 64.29% (9/14) | 100.00% (9/9) |
| dates | 10 | 5 | 0 | 66.67% (10/15) | 100.00% (10/10) |
| unit_basis | 8 | 1 | 0 | 88.89% (8/9) | 100.00% (8/8) |
| daily_caps | 3 | 0 | 0 | 100.00% (3/3) | 100.00% (3/3) |
| duplicate_service | 3 | 0 | 0 | 100.00% (3/3) | 100.00% (3/3) |
| duplicate_invoice_id | 5 | 0 | 0 | 100.00% (5/5) | 100.00% (5/5) |
| exclusions | 2 | 0 | 1 | 100.00% (2/2) | 66.67% (2/3) |
| contract_identity | 3 | 0 | 0 | 100.00% (3/3) | 100.00% (3/3) |
| uncontracted_service | 0 | 0 | 10 | not measurable | 0.00% (0/10) |

## Systematic limitations and examples

- **Ambiguous descriptions:** service_match_unresolved: 207 invoices (e.g. INV-H1-000003, INV-H1-000012)
- **Uncertain cross-invoice dependencies:** volume_discount_uncertain: 161 invoices (e.g. INV-H1-000036, INV-H1-000037); bundle_eligibility_uncertain: 2 invoices (e.g. INV-H1-000548, INV-H1-000847); exclusion_presence_uncertain: 29 invoices (e.g. INV-H1-000036, INV-H1-000043); premium_eligibility_uncertain: 8 invoices (e.g. INV-H1-000068, INV-H1-000116)
- **Quantity or duplicate conflicts:** contract_quantity_unknown_due_to_unit_mismatch: 9 invoices (e.g. INV-H1-000236, INV-H1-000257); delivered_quantity_or_duplicate_identity_uncertain: 49 invoices (e.g. INV-H1-000036, INV-H1-000067); retention_or_payable_quantity_requires_review: 71 invoices (e.g. INV-H1-000002, INV-H1-000036)
- **Malformed identity/date evidence:** missing_or_ambiguous_invoice_join: 5 invoices (e.g. INV-H1-000068, INV-H1-000152); invalid_date_payability_requires_review: 15 invoices (e.g. INV-H1-000002, INV-H1-000036)

False positive examples: `[]`

Missed known error examples: `[]`

Expected-amount mismatch examples: `[]`

Original billed quantities and money are unchanged. A known violation may coexist with an unknown expected total. Date defects and unit mismatches do not receive invented zero corrections.

## Evaluation provenance

Labels SHA-256: `79e7918337b7836d810b1164ec955684454dd7dcdd805ee7e0a7a980d14302b6`

Unlabelled prediction IDs: []. Missing labelled IDs: [].

See run_manifest.json for implementation, input and output hashes, and evaluation_freeze.json for the held-aside implementation freeze.
