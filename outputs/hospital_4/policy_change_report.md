# Hospital 4 approved-policy comparison

Submission: 370 → 374 rows; correct 361 → 364; erroneous 9 → 10. Coverage 44.31% → 44.79%. 461 unique H4 IDs remain omitted.

Added 4; removed 0; changed existing submission rows 0 (including expected cents, categories and confidence). Existing class confidence values remain 0.892297 / 0.581503.

| Added invoice | Flag | Billed cents | Expected cents | Confidence | Evidence |
|---|---:|---:|---:|---:|---|
| INV-H4-000018 | 0 | 1493475 | 1493475 | 0.892297 | Exact copy; retained H4-L00018-07 (§11.3) |
| INV-H4-000069 | 0 | 3522700 | 3522700 | 0.892297 | Exact copy; retained H4-L00069-13 (§11.3) |
| INV-H4-000084 | 0 | 4715550 | 4715550 | 0.892297 | Exact copy; retained H4-L00084-02 (§11.3) |
| INV-H4-000235 | 1 | 1538350 | 1518150 | 0.581503 | H4-L00235-06 inclusive exclusion (§9.1); approved interpretation, not H4 validation |

## Cap estimates retained

Confirmed daily-cap violations are separate from assumption-dependent corrected amounts. Actual delivered quantities are not established. No new confidence penalty; the shared class score is not cap-specific calibration. Already-exposed H1 development evidence suggests below-cap quantities in four cases, with an unproven explanation.

| Invoice | Expected cents | Evidence line | Confidence |
|---|---:|---|---:|
| INV-H4-000165 | 3370925 | H4-L00165-05 | 0.581503 |
| INV-H4-000540 | 2120125 | H4-L00540-02 | 0.581503 |
| INV-H4-000554 | 3465160 | H4-L00554-08 | 0.581503 |

## Changes on still-omitted invoices

Line and invoice changes, including newly determined amounts on omitted invoices, are fully recorded in policy_change_report.json. Endpoint targets 000168, 000473 and 000658 remain blocked by other evidence. Discarded copies on 000309, 000473 and 000693 now have zero payable amounts; other unresolved lines still prevent submission.

## Remaining omissions (overlapping reasons)

| Reason | Unique invoices |
|---|---:|
| bundle_eligibility_uncertain | 45 |
| contract_quantity_unknown_due_to_unit_mismatch | 11 |
| delivered_quantity_or_duplicate_identity_uncertain | 59 |
| exclusion_presence_uncertain | 46 |
| expected_total_unknown | 461 |
| hospital_4_contractual_unit_unresolved | 100 |
| invalid_date_payability_requires_review | 20 |
| invoice_identifier_join_ambiguous | 5 |
| missing_or_ambiguous_invoice_join | 5 |
| missing_patient_context | 5 |
| nonunique_invoice_id | 5 |
| premium_eligibility_uncertain | 19 |
| retention_or_payable_quantity_requires_review | 96 |
| service_match_unresolved | 253 |
| volume_discount_uncertain | 258 |

Approved H4 policies; no H4 label validation. H1 evidence uses already-exposed development analysis. No confidence penalty or matching change.

All baseline files are hash-checked on every run. Original assessment and H1 implementation/evaluation are checked by their existing manifests. Matching aliases and acceptance thresholds are unchanged; Jev remains experimental.
