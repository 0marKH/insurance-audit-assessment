# Hospital 1 evaluation — held_aside

Development descriptions and labels informed implementation. Held-aside labels were reserved until the implementation freeze; all invoice records still supply cross-invoice contractual context. The split is by invoice ID, not an independent hospital or patient cohort.

Duplicate header records are consolidated by ID for label scoring; their amount remains unresolved. Missing predictions count as review. Review is never counted as correct.

| Measure | Result |
|---|---:|
| decision coverage | 52.55% (103/196) |
| known error precision | 100.00% (12/12) |
| known error recall including abstentions | 85.71% (12/14) |
| accuracy on decided invoices | 100.00% (103/103) |
| expected amount coverage | 47.96% (94/196) |
| exact expected amount accuracy when known | 98.94% (93/94) |
| Mean absolute error on known amounts | 14775/94 cents |

Amounts are evaluated only where the engine can establish them. Conditional accuracy is not full-dataset accuracy. No numeric confidence scores or calibration claims are made.

## Per-category invoice detection

These rows measure whether an invoice with the given label category has any known violation. They do not claim exact identification of each injected category. Multi-label invoices appear in multiple rows.

| Label category | Invoices | Known error detected | Review only | Incorrectly accepted | Known amounts | Exact amounts |
|---|---:|---:|---:|---:|---:|---:|
| bundle_not_applied | 1 | 1 | 0 | 0 | 1 | 1 |
| contract_number_mismatch | 2 | 2 | 0 | 0 | 1 | 1 |
| cross_invoice_duplicate | 1 | 1 | 0 | 0 | 0 | 0 |
| daily_cap_exceeded | 1 | 1 | 0 | 0 | 1 | 0 |
| exclusion_window_violation | 1 | 1 | 0 | 0 | 0 | 0 |
| invoice_total_mismatch | 2 | 2 | 0 | 0 | 1 | 1 |
| malformed_service_date | 1 | 1 | 0 | 0 | 0 | 0 |
| premium_incorrectly_applied | 1 | 1 | 0 | 0 | 1 | 1 |
| service_date_after_invoice_date | 2 | 2 | 0 | 0 | 0 | 0 |
| service_date_out_of_window | 3 | 3 | 0 | 0 | 0 | 0 |
| unit_price_mismatch | 2 | 2 | 0 | 0 | 0 | 0 |
| unknown_service | 2 | 1 | 1 | 0 | 0 | 0 |
| volume_discount_incorrectly_applied | 2 | 2 | 0 | 0 | 0 | 0 |
| wrong_unit_basis | 3 | 2 | 1 | 0 | 0 | 0 |

## Grouped category detection

Categories are mapped explicitly in hospital_audit/evaluate.py. Pricing groups bundles/premiums/discounts/rate errors; arithmetic groups line/invoice arithmetic. Unknown-service matching is conservatively reviewed rather than asserted as an uncontracted charge.

| Category group | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---|---|
| pricing | 4 | 0 | 1 | 100.00% (4/4) | 80.00% (4/5) |
| arithmetic | 2 | 0 | 0 | 100.00% (2/2) | 100.00% (2/2) |
| dates | 5 | 0 | 0 | 100.00% (5/5) | 100.00% (5/5) |
| unit_basis | 2 | 0 | 1 | 100.00% (2/2) | 66.67% (2/3) |
| daily_caps | 1 | 0 | 0 | 100.00% (1/1) | 100.00% (1/1) |
| duplicate_service | 1 | 0 | 0 | 100.00% (1/1) | 100.00% (1/1) |
| duplicate_invoice_id | 0 | 0 | 0 | not measurable | not measurable |
| exclusions | 1 | 0 | 0 | 100.00% (1/1) | 100.00% (1/1) |
| contract_identity | 2 | 0 | 0 | 100.00% (2/2) | 100.00% (2/2) |
| uncontracted_service | 0 | 0 | 2 | not measurable | 0.00% (0/2) |

## Systematic limitations and examples

- **Ambiguous descriptions:** service_match_unresolved: 43 invoices (e.g. INV-H1-000001, INV-H1-000025)
- **Uncertain cross-invoice dependencies:** volume_discount_uncertain: 54 invoices (e.g. INV-H1-000038, INV-H1-000041); exclusion_presence_uncertain: 13 invoices (e.g. INV-H1-000045, INV-H1-000060); premium_eligibility_uncertain: 1 invoices (e.g. INV-H1-000678)
- **Quantity or duplicate conflicts:** contract_quantity_unknown_due_to_unit_mismatch: 2 invoices (e.g. INV-H1-000211, INV-H1-000635); delivered_quantity_or_duplicate_identity_uncertain: 15 invoices (e.g. INV-H1-000148, INV-H1-000149); retention_or_payable_quantity_requires_review: 30 invoices (e.g. INV-H1-000045, INV-H1-000060)
- **Malformed identity/date evidence:** invalid_date_payability_requires_review: 5 invoices (e.g. INV-H1-000148, INV-H1-000219)

False positive examples: `[]`

Missed known error examples: `[{"invoice_id": "INV-H1-000657", "decision": "review", "label_categories": ["wrong_unit_basis"], "violations": []}, {"invoice_id": "INV-H1-000667", "decision": "review", "label_categories": ["unknown_service"], "violations": []}]`

Expected-amount mismatch examples: `[{"invoice_id": "INV-H1-000015", "calculated_cents": 1210600, "label_cents": 1195825, "categories": ["daily_cap_exceeded"]}]`

Original billed quantities and money are unchanged. A known violation may coexist with an unknown expected total. Date defects and unit mismatches do not receive invented zero corrections.

## Evaluation provenance

Labels SHA-256: `79e7918337b7836d810b1164ec955684454dd7dcdd805ee7e0a7a980d14302b6`

Unlabelled prediction IDs: []. Missing labelled IDs: [].

See run_manifest.json for implementation, input and output hashes, and evaluation_freeze.json for the held-aside implementation freeze.
