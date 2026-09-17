# Hospital 1 — labels versus audit (all)

Compared 913 labelled invoices with 918 audit records (913 distinct invoice IDs).

## Decision comparison

| Outcome | Invoices |
|---|---:|
| true_positive | 56 |
| true_negative | 445 |
| false_positive | 0 |
| false_negative | 0 |
| review_label_erroneous | 2 |
| review_label_correct | 410 |
| missing_audit | 0 |
| missing_label | 0 |

Review is an abstention, not a correct result or an explicit false negative. Recall still counts review-only erroneous labels as undetected. A known violation can coexist with an unresolved amount.

## Expected-amount comparison

| Outcome | Invoices |
|---|---:|
| audit_amount_unresolved | 456 |
| exact | 456 |
| mismatch | 1 |

All amounts and differences are integer cents. Difference = audit expected total − label expected total. Blank amounts and differences are unknown, not zero. Reused audit invoice IDs are scored once, with expected amounts left unresolved.

## Development and held-aside results

| Split | Decision coverage | Error precision | Error recall | Amount coverage | Exact known amounts |
|---|---|---|---|---|---|
| development | 55.51% (398/717) | 100.00% (44/44) | 100.00% (44/44) | 50.63% (363/717) | 100.00% (363/363) |
| held_aside | 52.55% (103/196) | 100.00% (12/12) | 85.71% (12/14) | 47.96% (94/196) | 98.94% (93/94) |

This script compares already-produced outputs. It does not retune the engine, create a new holdout, or claim confidence calibration. Category names are shown side by side; they are not assumed to be identical vocabularies. Existing grouped/per-label category metrics are retained in summary.json.

## Wrong decisions and amount mismatches

| Invoice | Decision comparison | Label cents | Audit cents | Difference cents |
|---|---|---:|---:|---:|
| INV-H1-000015 | true_positive | 1195825 | 1210600 | 14775 |

## Labelled errors sent to review

- INV-H1-000657: wrong_unit_basis; service_match_unresolved
- INV-H1-000667: unknown_service; delivered_quantity_or_duplicate_identity_uncertain|retention_or_payable_quantity_requires_review|service_match_unresolved

## Files

- `invoice_comparison.csv`: every labelled or predicted invoice, joined by ID.
- `differences.csv`: wrong decisions, differing known amounts, and missing IDs only.
- `review_cases.csv`: cases still requiring review, including known violations with unknown totals.
- `summary.json`: counts, category metrics, split metrics and input hashes.

Missing audit IDs: []. Unlabelled audit IDs: [].
