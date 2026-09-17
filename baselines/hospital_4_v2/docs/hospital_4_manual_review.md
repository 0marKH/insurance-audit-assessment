# Hospital 4 manual calculation and uncertainty review

Codex-assisted inspection, 17 September 2026. These are contract/source comparisons,
not hidden labels or measured generalisation accuracy. Values below are integer
cents. Every erroneous submission was checked for the specific correction and
invoice delta; correct and uncertain cases were sampled. Full evidence is in
`outputs/hospital_4/line_audit.jsonl`. Replay the independent numerical expectations
with `python3 -m hospital_4.manual_check`.

## Representative calculations

| Line ID | Source and independent calculation | Result |
|---|---|---|
| H4-L00009-03 | Standard Hepatic Infusion Therapy (§3), 3,975 × 1.15 = 4,571.25, rounded to 4,571 (§4.2); delivered 34 > 6 (§5), so all 34 units receive premium: 4,571 × 34. | 155,414, billed correctly. Invoice 000009 is submitted correct. |
| H4-L00003-06 / 07 | Same patient PT-H4-000099 and 2024-01-07. Supervised Rheumatologic Dialysis Session and Specialist Immunologic Consultation: §7 replaces base rates with 13,900 and 91,600; quantities 3 and 2. | 41,700 and 183,200. Both bundle sides checked. |
| H4-L00017-04 | Advanced Orthopaedic Ward Bed Occupancy; six nights × 97,925 (§3), below cap twelve (§6). Original line total 562,550 is arithmetically short. | 587,550; add 25,000. |
| H4-L00165-05 | Extended Hepatic Transfusion Service, 13 billed units (delivery inferred), cap 8 (§6); 8 × 8,450 (§3). | 67,600 instead of 109,850; remove only five units. |
| H4-L00540-02 | Focused Metabolic Biopsy Procedure, 13 units capped at 8; 8 × 15,025. Printed contract number is also wrong, but does not erase the hospital context. | 120,200; reduce by 75,125; flag identity separately. |
| H4-L00554-08 | Elective Gastrointestinal Nursing Observation, 8 days capped at 6; 6 × 58,925. Invoice header also exceeds original line sum by 25,000. | 353,550; cap reduces 117,850 plus 25,000 header correction. |
| H4-L00583-03 / 04 / 05 | Elective Obstetric Transfusion and Intermittent Rheumatologic Dialysis are a §7 pair: 1,250 × 3 and 111,675 × 1. Ambulatory Immunologic Ward Bed rate is 74,700, not billed 130,725; quantity 2. | 3,750; 111,675; 149,400. Combined reduction 127,800. |
| H4-L00645-10 / 11 | Standard Hepatic Infusion: 17 > 6; round 3,975 × 1.15 to 4,571 then ×17. Assisted Paediatric Physiotherapy bundle rate 2,675 ×10, rather than billed 1,337 ×10. | 77,707 and 26,750. Combined increase 23,512. |
| H4-L00719-08 | Intermittent Oncology Home Visit, 3 ×22,050; no price adjustment required. | 66,150 versus billed 65,150; add 1,000. |

All ten erroneous submission totals were checked:

| Invoice suffix (INV-H4-) | Billed | Expected | Evidence for difference |
|---|---:|---:|---|
| 000017 | 4,939,975 | 4,964,975 | Line arithmetic +25,000 |
| 000104 | 763,938 | 763,938 | Wrong printed contract only (§11.1); all five line amounts checked |
| 000165 | 3,413,175 | 3,370,925 | Cap -42,250 |
| 000235 | 1,538,350 | 1,518,150 | Approved inclusive 21-day exclusion -20,200; wrong contract also flagged |
| 000323 | 1,906,175 | 1,905,175 | Header arithmetic -1,000; line sum independently checked |
| 000540 | 2,195,250 | 2,120,125 | Cap -75,125 and wrong contract |
| 000554 | 3,608,010 | 3,465,160 | Cap -117,850; header arithmetic -25,000 |
| 000583 | 947,375 | 819,575 | Bundle/base rate corrections -127,800 |
| 000645 | 2,403,195 | 2,426,707 | Premium and bundle corrections +23,512 |
| 000719 | 2,370,128 | 2,371,128 | Line arithmetic +1,000 |

## Uncertainty inspection

- **Exact endpoints (approved):** H4-L00168-14 / H4-L00168-07 are ten days
  apart; H4-L00235-06 / H4-L00235-03 are 21 days apart; H4-L00473-08 /
  H4-L00084-14 and H4-L00658-19 / H4-L00217-01 are seven-day cross-invoice
  pairs. Each pair has the same patient. The first-column services now pay zero
  under approved inclusive endpoints; the trigger is not automatically excluded.
  Invoice 000235 becomes submissible at 1,518,150 cents; the others retain
  independent unit/matching/bundle blockers. This interpretation is supported by
  H1 examples, not validated with H4 labels.
- **Exact multi-unit copies:** H4-L00018-07 / H4-L00693-16 bill the same service,
  patient and date, 40 units ×3,575 =143,000. Keep the earlier ID, reject the later
  charge; inferred daily delivery is 40, while original billed history retains
  both. H4-L00069-13 / H4-L00309-14 similarly bill 5 nights ×162,775 =813,875.
  H4-L00084-02 / H4-L00473-07 bill 2 procedures ×365,675 =731,350. All fields
  required by the exact-copy policy agree. Earlier invoices are now correct at
  1,493,475; 3,522,700; and 4,715,550 respectively. Later invoices remain omitted
  due to other unresolved lines. Conflicting copies are tested and withheld.
- **Cap amounts are estimates:** 000165, 000540 and 000554 have confirmed billed
  cap violations. Their payable quantities 8, 8 and 6 and totals above are
  assumption-dependent estimates, not established actual delivered quantities.
  Already-exposed H1 labels imply below-cap quantities in four investigated cases;
  the reason is unproven, and three reconstructions contain unrelated unresolved
  lines. Submission retains these three estimates by explicit approval. The
  unchanged 0.581503 class heuristic is not a calibrated cap-amount confidence.
- **Dual unit:** H4-L00002-15 is recognizably Intermittent Urologic Telemetry
  Monitoring, billed as `per_hour_per_item`, quantity 25. A matching billed rate
  (7,275) does not establish what 25 measures. Review and propagate possible
  exclusion presence; do not multiply by an assumed valid quantity.
- **Cumulative uncertainty:** H4-L00051-01 is Standard Oncology Ward Bed
  Occupancy. Exact matched prior quantities give a contract-wide scenario of 12,
  but uncertain prior records make the upper bound unknown. The population/reset
  issue also remains. Neither zero usage nor a certain discount is justified.
- **Propagation:** H4-L00053-15 has an otherwise clear service/rate, but records
  H4-L00053-01 and 07 cannot be grounded to the catalogue. Their candidate fallback
  includes the exclusion trigger. The affected charge stays unknown instead of
  treating those records as absent. This broad fallback sacrifices coverage.

No strictly-inside-window exclusion or applied cross-invoice bundle was found.
The four exact-endpoint exclusions above now apply under the approved interpretation. Those paths were therefore checked with explicit
synthetic fixtures (both date directions, unrelated patient, inclusive endpoints,
and separate invoice headers); they are not presented as observed successes.
Discount threshold invariance and crossing-line behaviour are likewise tested
with fixtures because actual uncertain prior records dominate the live examples.

The frozen v1 review and artifacts remain under `baselines/hospital_4_v1/`; this updated review reflects prompt 008. Twenty line calculations, ten erroneous invoice deltas, all three added correct invoices, four endpoint pairs and the three submitted cap estimates are replayed independently.
