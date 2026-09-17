# Hospital 1 label investigation — decision requested, no policies changed

This is **development analysis of already-exposed labels**, including the former
held-aside split. It is not fresh validation. Jev has been set aside; no model was
called. Original assessment files, H1/H4 rules and policies, engines, frozen audit
outputs and submission.csv remain unchanged (hash checked).

## Short evidence table

| Finding | Verified evidence / what it establishes | Remaining explanations or limits | Hospital 4 transfer / proposed decision | Conditional coverage effect |
|---|---|---|---|---|
| Exclusion endpoints | H1 000847 removes 27,600 at exactly 7 days across invoices; 000211 removes 96,600 at exactly 10 days. Same patient and correct trigger verified. Supports inclusive endpoints for these H1 examples. | Invoice-level totals are not line-level labels, but the exact matching charge and category make the interpretation strong. Does not independently test every window size. | H4 uses the same “within” construction; its §9.1 explicitly adds same-patient/across-invoice scope. Propose **inclusive ≤ N as an explicit H4 interpretation**, subject to approval; H1 already uses it. | Four H4 exact-boundary charges affected; only **1 otherwise-clear invoice**, 000235, would gain a total (1,518,150 cents). The other three still have blockers. |
| Wrong units | All **11** H1 cases reconcile with no monetary change attributed to the unit field after identified other corrections. Seven have isolated financial evidence; four need qualifications detailed below. 000717 is particularly clean. | Unit-label-only corruption is consistent with the data, not proven as a universal mechanism. 000657 has ambiguous service identity; 000369 unknown-service issues; 000552 an invalid date; 000457 a reused ID. No physical conversion factors are supplied. | Propose a **case-evidenced metadata correction path**, never “all mismatches are typos.” For unlabelled H4, price agreement alone is insufficient; require independent quantity evidence or an explicit new convention. H4 dual-unit ambiguity remains separate. | H4 has 11 ordinary unit-mismatch invoices. **5 otherwise-clear candidate invoices** could be reconsidered if their quantities were established; this is not 5 justified new submissions. No automatic recovery of the 100 dual-unit-affected IDs. |
| Cross-invoice duplicates | All **4** labelled later invoices lose an identical one-unit charge; the four earlier invoices are labelled correct. Other named errors explain the remaining deltas. Both rates comply. | Lexical order and invoice chronology agree, so labels do not distinguish those retention criteria. No differing quantities/rates, partial duplicates or competing compliant/noncompliant copies are tested. | H4 §11.3 also forbids repeated service/patient/date billing. Propose retaining the earliest lexical occurrence **only for exact-copy, same-quantity, same-rate, eligible duplicates**; leave conflicts for review. This is an H4 correction convention to approve, not explicit contract text. | Three H4 pairs affect six IDs. The **3 earlier invoices** (000018, 000069, 000084) have no other blockers; the three later invoices still do. |
| Volume discounts | All **8** labelled invoice deltas reconcile with the relevant contract rate changes plus other identified errors. Five focal tier decisions are provable from saved prior bounds; three early decisions remain label-consistent but have unknown prior upper bounds. H1 §7.1 expressly aggregates all patients/whole term. | These examples do not independently test equality at every threshold, every tie ordering, or resolve all uncertain historical matches. Totals alone cannot reveal every line's ground truth. | **Do not transfer population/reset scope.** H4 §§8.3–8.5 share strict prior-line/deepest-tier/order mechanics, but omit the population/reset definition. Obtain a specific H4 decision. | 258 H4 omitted IDs have discount uncertainty; that is affected coverage, **not 258 recoverable rows**. No defensible gain quantified before scope/history decisions. |
| Cap discrepancy | H1 000015 has no other same-patient/day record in either CSV or nested JSONL. Four-test cap yields 1,210,600, label 1,195,825. Broader check: **all four cap-labelled invoices imply below-cap quantities** after named other corrections. | Restoring a hidden pre-error quantity is plausible; additional undisclosed adjustments or label-generation inconsistency are alternatives. The original quantity/generator logic is unavailable. No basis for declaring the label wrong or changing the cap to three. | **Keep caps unchanged; seek adjudication of expected-amount semantics.** H4 §6.1 explicitly excludes excess but does not reveal original delivered quantity. Flag the three currently submitted H4 cap corrections for this methodological risk, without modifying them. | No proposed automatic coverage increase. Detection of a cap breach and knowing the exact corrected total must remain separate. |

Counts above are a **static blocker inventory plus explicitly conditional case
arithmetic**, not a rerun under changed policies. Inclusive endpoints plus the
narrow duplicate convention would make four disjoint H4 invoice totals otherwise
resolvable: 370 → **374/835 (44.79%)**, conditional on approval and a subsequent
verified implementation. Unit opportunities are not included in that figure.
No interpretation has been adopted and actual coverage remains **370/835**.

## 1. Verified exclusion examples

| Excluded / triggering lines | Patient | Dates | Billed invoice | Label expected | Reduction |
|---|---|---|---:|---:|---:|
| H1-L00847-17 / H1-L00830-09 | PT-H1-000229 | 2025-10-19 / 2025-10-26 | 3,988,200 | 3,960,600 | 27,600 |
| H1-L00211-08 / H1-L00211-04 | PT-H1-000199 | 2024-06-14 / 2024-06-24 | 1,567,925 | 1,471,325 | 96,600 |

The first charge is Advanced Metabolic Anaesthesia Administration (3 × 9,200),
triggered by Standard Endocrine Endoscopic Procedure. The second is Standard
Paediatric Biopsy Procedure (6 × 16,100), triggered by Advanced Infectious Critical
Care Occupancy. The wrong-unit error in each invoice is on a different line.

H1 §10 table says “Not billable within”; §10.1 specifies either date direction.
H4 §9.1 says “within the stated number of days” and explicitly specifies the same
patient, both directions and separate invoices. This makes consistent inclusive
interpretation reasonable, but H1 labels are not H4 labels. H4's four observed
boundary charges are H4-L00168-14 (10 days, 37,100 cents), H4-L00235-06 (21 days,
20,200), H4-L00473-08 (7 days, 470,475) and H4-L00658-19 (7 days, 940,950).
Only 000235 has no other amount blockers; its wrong-contract violation remains.

## 2. All eleven wrong-unit-labelled invoices

`Reduction` below is billed total minus labelled expected total. Negative values
mean the corrected invoice increases. Every listed mismatched line is arithmetically
consistent with its original quantity and billed rate. That is supporting evidence,
not a general permission to equate incompatible units.

| H1 invoice | Mismatched line | Billed → contract unit; original quantity | Reduction explained elsewhere | Strength and remaining limitation |
|---|---|---|---:|---|
| 000211 | H1-L00211-05 | unit dispensed → item; 5 | 96,600 exclusion | Strong isolated evidence: 5 × 25,300 = 126,500 is retained after the excluded charge is removed. |
| 000257 | H1-L00257-11 | procedure → day; 3 | 7,500 line arithmetic | Strong isolated evidence: 3 × 87,250 = 261,750 retained. No day/procedure conversion is needed to reconcile this label. |
| 000369 | H1-L00369-12 | test → item; 9 | 0 | 9 × 17,675 = 159,075 matches the discounted rate, but unknown-service and ambiguous-description lines prevent isolating all contributions. Billed equals labelled expected at 5,369,613. |
| 000457 | H1-L00483-02 | unit dispensed → item; 4 | 0 on the second nested record | Nested JSONL ties this line to PT-H1-000104 and the 1,922,972-cent record; label equals that record. 4 × 8,585 = 34,340 retained. A separate 3,516,982-cent record shares the invoice ID: no unique invoice-level correction is authorized. |
| 000552 | H1-L00552-15 | item → night; 4 | −7,500 line arithmetic | 4 × 59,700 = 238,800 fits unchanged, but another line has a malformed date. Reconciliation assumes that date error has no monetary effect; there is no independent delivery evidence. |
| 000635 | H1-L00635-01 | item → procedure; 1 | −38,178 pricing | Strong isolated evidence: 243,150 unchanged; another imaging line increases from 38,172 to 76,350. |
| 000657 | H1-L00657-02 | night → procedure; 2 | 0 | Total remains 4,217,639, but “Procedure Immun Endosc” fits two services. Both require per-procedure, so a unit violation can be recognized without choosing a service. Do not use the 121,580 rate to force the match. |
| 000677 | H1-L00677-12 | night → day; 4 | 704,175 = 616,875 pricing + 87,300 duplicate | Strong isolated unit evidence: 4 × 127,369 = 509,476 is retained. The adjusted rate is the deepest cumulative tier. |
| 000703 | H1-L00703-01 | hour → visit; 2 | −7,500 line arithmetic | Strong isolated evidence: 2 × 12,105 = 24,210 retained. |
| 000717 | H1-L00717-10 | hour → unit dispensed; 1 | 0 | Strongest simple example: the only labelled error is unit basis; all other lines reconcile; total remains 2,651,162 and this line remains 5,325. |
| 000847 | H1-L00847-02 | unit dispensed → item; 10 | 27,600 exclusion | Strong isolated unit/bundle evidence: 10 × bundled 19,150 = 191,500 retained; its clearly described counterpart is present same patient/day. Current unit uncertainty also blocks that counterpart. |

Seven cases can isolate the financial consequence with the other contract
calculations (211, 257, 635, 677, 703, 717, 847). The remaining four have the
specific caveats above; the nested source adds useful record-level evidence for
457. **No example demonstrates a necessary numerical conversion.** Neither do
these labels supply conversion factors for new invoices. Retaining quantities
is defensible as a labelled-case reconstruction in the isolated cases; it is not
independently established for an unlabelled mismatched H4 record merely because
its billed rate looks right.

A separate, nonfinancial improvement could flag the unit mismatch in 657 because
both plausible services have the same contractual unit. The exact service and
expected amount would remain unresolved. No analogous additional H4 case was
found in this static candidate-unit check.

H4's five ordinary-unit opportunities are 000003, 000095, 000196 and 000541
(other lines already resolved), plus 000504 (its only additional blocker is a
bundle partner dependent on the unit-mismatched line). This is a review queue,
not a prescription to keep their quantities. The compound contractual unit
“per hour, per item” has no H1 counterpart here and is not a simple wrong-unit
label; keep its quantity question separate.

## 3. All four cross-invoice duplicate labels

| Later H1 invoice / line | Earlier line | Identical repeated charge | Additional reduction | Labelled invoice reduction |
|---|---|---:|---:|---:|
| 000231 / H1-L00231-07 | H1-L00079-05 | 134,725 | 0 | 134,725 |
| 000675 / H1-L00675-07 | H1-L00450-04 | 8,225 | 70,070 pricing | 78,295 |
| 000677 / H1-L00677-18 | H1-L00346-03 | 87,300 | 616,875 pricing | 704,175 |
| 000852 / H1-L00852-18 | H1-L00246-02 | 243,150 | 0 | 243,150 |

All pairs have identical descriptions, dates, quantities, units, rates and line
totals; patient IDs agree. All quantities are one. Earlier invoice labels are
correct. The unit-price errors on 675 and 677 affect other lines, not either
copy. Invoice 852 also has an out-of-term service date on another line; its label
does not subtract that line's 27,025 cents. This does not authorize invalid-date
payability generally.

These cases support later-copy removal in an exact-copy tie. They do **not**
validate a general price-aware preference for a later compliant record over an
earlier mispriced one, or how to allocate differing quantities. Lexical line
order and invoice-date chronology agree in every pair.

H4 has three exact-copy groups, with quantities 40, 5 and 2 respectively. Rates
are compliant on both copies. If an exact-copy retention convention is approved,
the earlier invoices' conditional totals are: 000018 = 1,493,475; 000069 =
3,522,700; 000084 = 4,715,550 (all equal their billed totals). Later invoices
000693, 000309 and 000473 retain other blockers. Applying this convention to
multi-unit copies is a separately stated H4 implementation choice, not something
the four one-unit H1 labels directly prove.

## 4. All eight volume-discount-labelled invoices

All arithmetic is in cents. “Other reduction” includes separate pricing,
arithmetic or invoice-header errors; a negative volume reduction raises payable.
The corrected rates below are contract-derived candidates checked against the
label delta, not rates chosen to define a service match.

| H1 invoice / focal line | Billed rate → contract rate; quantity | Volume reduction | Other reduction | Label expected |
|---|---|---:|---:|---:|
| 000004 / H1-L00004-01 | 8,585 → 10,100; 3 | −4,545 | 340,743 | 924,200 |
| 000102 / H1-L00102-07 | 121,580 → 151,975; 1 | −30,395 | 103,331 | 2,663,314 |
| 000186 / H1-L00186-01 | 12,105 → 13,450; 3 | −4,035 | 25,000 | 1,959,233 |
| 000219 / H1-L00219-06 | 12,105 → 13,450; 2 | −2,690 | 0 | 2,761,823 |
| 000304 / H1-L00304-08 | 25,250 → 17,675; 7 | 53,025 | 32,382 | 1,792,655 |
| 000458 / H1-L00458-03 | 112,825 → 101,543; 6 | 67,692 | 0 | 1,831,611 |
| 000811 / H1-L00811-02 | 169,825 → 127,369; 2 | 84,912 | 0 | 3,629,745 |
| 000820 / H1-L00820-12 | 151,975 → 121,580; 1 | 30,395 | 1,000 | 2,850,137 |

- 000004 has exactly zero prior usage for the focal service, so no discount is
  due. Its two independent unit-price corrections total 340,743.
- 000102, 000186 and 000219 have definite prior lower bounds 50, 91 and 111,
  respectively, below their first thresholds (80, 120 and 120). Their upper
  bounds are unknown because uncertain prior records could count. Restoring the
  base rate exactly reconciles each label delta, but does not independently
  verify all historic membership. Other uncertain/date/unknown-service lines are
  implicitly left financially unchanged in this reconciliation.
- 000304, 000458, 000811 and 000820 have known prior lower bounds 499, 497, 924
  and 300; each already exceeds its deepest threshold. Further unknown usage
  cannot change the selected tier. Known prior same-patient quantities are only
  2, 0, 3 and 2, respectively (not exact totals of every uncertain record).
  Together with H1 §7.1, these support contract-wide, cross-patient counting.
- 000458 verifies rate-level half-up rounding: 112,825 × 0.90 = 101,542.5 →
  101,543, then ×6 = 609,258. Rounding only the final line would give 609,255.
- 000811 uses 25%, not stacked 10% and 25%. 169,825 ×0.75 rounds to 127,369.
  000820 likewise uses the deepest 20% tier without stacking 12%.

The contract, rather than these eight examples alone, establishes strict `>`,
excluding the current line, whole-term/all-patient scope and lexical same-date
ordering (§§2.4, 7.1, 7.2). These focal histories were independently counted for
known matched, compatible-unit records. The frozen engine has complete expected
invoice totals for only 000004 and 000820; the other six remain unknown for
context/record reasons despite this numerical reconciliation.

H4 §§8.3–8.5 specify strict prior-line thresholds, deeper tiers and date/line
order, but contain no equivalent of H1 §7.1's population and horizon definition.
Discount mechanics can be reused; population/reset cannot be inferred from H1
labels. No proposed H4 scope change is implemented here.

## 5. Cap investigation and the broader pattern

For 000015, CSV and nested JSONL agree on patient PT-H1-000172 and 2024-01-20.
That patient has three invoices and 33 lines in the supplied data. The capped
line is the **only record of any service on that date**. The other matching lab
panel for this patient is on 2024-11-16, which does not consume a January daily
cap. The original invoice header equals its line sum; all other priced lines
reconcile. No bundle, premium, discount or exclusion applies to this lab service.
Thus no supplied same-patient/day record explains the extra 14,775-cent reduction.

The broader cap-label check yields:

| H1 invoice | Billed quantity | Contract cap | Other named corrections | Quantity implied by label residual | Literal cap total | Label total |
|---|---:|---:|---:|---:|---:|---:|
| 000015 | 9 | 4 | 0 | 3 | 1,210,600 | 1,195,825 |
| 000049 | 15 | 12 | 108,750 premium removal | 9 | 2,732,035 | 2,706,610 |
| 000227 | 14 | 12 | 100,000 invoice-header correction | 3 | 5,375,775 | 5,299,500 |
| 000725 | 11 | 8 | 0 | 3 | 1,812,750 | 1,624,750 |

There are no additional same-patient/day candidate records for the capped service
in these four cases. The last three whole-invoice reconstructions are conditional
on unrelated unresolved lines retaining their billed amounts; only 000015 has a
fully resolved frozen expected total. They reveal a consistent numerical pattern,
not proof of a hidden generation mechanism.

One plausible explanation is that labels restore pre-injection quantities (3, 9,
3, 3), rather than merely trimming erroneous billed quantities to the maximum.
The supplied data does not expose those original quantities or the generation
logic. An extra unrecorded adjustment or label-generation inconsistency cannot
be ruled out. We should ask which expected-total semantics the assessment intends;
we should neither substitute a cap of three nor assert that the label is wrong.

H4 explicitly states that excess is nonpayable (§6.1), which supports the existing
maximum-based calculation under the billed-delivery assumption. It still cannot
reconstruct a lower true delivered quantity from a corrupted bill. The three
submitted H4 cap cases (000165, 000540, 000554) therefore carry this assessment-
semantics risk. They remain unchanged pending your decision.

## Reproduction and preserved baseline

Run from the repository root:

```bash
python3 analysis/hospital_1_label_investigation/inspect_evidence.py
python3 analysis/hospital_1_label_investigation/analyse.py
```

`selected_evidence.json` preserves the selected saved line/invoice evidence.
`findings.json` contains verified examples and H4 blocker details.
`baseline_sha256.json` protects original data, engines, policies, H1/H4 outputs
and submission. The scripts never call the engine with changed rules, never
change original records and never overwrite an existing differing baseline
snapshot. Reconciliation constants are explicitly case-specific hypotheses, not
rules added to the production engine. Sources are the local original H1/H4
contracts, invoice CSV/JSONL, H1 labels and frozen audit outputs.
