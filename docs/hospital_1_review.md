# Hospital 1 contract review

Northgate Regional Medical Centre, contract **INS-H1-2024-0417**, reimbursed by
Meridian Health Assurance Group. Term: **1 January 2024–31 December 2025**.
Currency: **GBP**, represented in integer cents. Main Campus (`F-MAIN`) has
no facility differential. BRONZE, SILVER and GOLD use the same rates.

This review summarizes the [original contract](../data/assessment/contracts/hospital_1/provider_services_agreement.md).
All 174 rules, including every exact service name and rate, are in the
[generated rule register](../outputs/hospital_1.rules.md) and
[JSON artifact](../outputs/hospital_1.rules.json).

| Requested area | Extracted result | Evidence |
|---|---|---|
| Contract scope | Provider, payer, contract number, dates, currency, facility and plan treatment | Preamble; §§1.1–1.3 |
| Service catalogue | 108 exact names, billing bases and integer-cent rates; 7 caps cross-checked against §8 | §4; §2.3 |
| Definitions | Calendar service day; business day excludes Saturday/Sunday; cumulative billed units exclude the current line | §§2.1–2.4 |
| Adjustments | 9 strict daily-quantity premiums; 7 weekend uplifts; 11 discount tiers for 7 services | §§5–7 |
| Grouping | Premiums and caps: service/patient/day. Discounts: service/all patients/whole term. Bundles: patient/day/pair | §5.1; §§7.1–7.2; §8; §9.1 |
| Bundles | 3 pairs; replace each component's unit rate before adjustments; same patient/day, including across invoices | §9; §3.2 |
| Restrictions | 7 daily caps; 6 exclusion windows; required contract number; required unique invoice identifiers; valid service dates; duplicate-service prohibition | §§8, 10, 11 |
| Calculation | Bundle → facility → plan → premium/uplift → volume discount → quantity → invoice sum; half-up rounding at each step | §§3.1–3.3 |
| Boundaries | “Exceeds” is `>`; at equality no threshold adjustment; usage excludes the current line; same-date lines use ascending line ID; deepest qualifying discount only | Table headers in §§5, 7; §§2.4, 7.2 |
| Evidence and uncertainty | Exact contract evidence for every rule; user conventions and resolved contract ambiguities recorded separately | Every generated rule; `policies/hospital_1.json` |

## Worked extraction: pulmonary volume discount

This is the extracted meaning, not a calculated invoice:

- **Applies to:** Ambulatory Pulmonary Recovery Room Occupancy; base rate 112825 cents per night of occupancy.
- **Condition:** Prior cumulative billed usage **exceeds 60 nights**. At exactly 60, the discount is not triggered.
- **Action:** Reduce the effective unit rate by **10%**, using the exact multiplier `90/100`. Apply to the whole current line; do not split the line at the threshold.
- **Scope:** This service, all patients, across the whole contract term. Exclude the current line from usage; sort by service date and then ascending line identifier.
- **Order:** After bundle substitution, facility/plan multipliers and any applicable premium. Round to cents after the discount, then multiply quantity.
- **Source:** §4 rate row; §7 discount row; §§2.4, 7.1, 7.2, 3.1 and 3.2.
- **Assumptions:** Use lexical line-ID ordering and include all prior billed units, including duplicates and disallowed units. These user-approved conventions resolve ambiguity in the contract; corrections never reduce cumulative billed history.

## Bundle rates

| Service A | Service B | Replacement A, cents | Replacement B, cents |
|---|---|---:|---:|
| Advanced Cardiac Recovery Room Occupancy | Routine Cardiac Specimen Analysis | 16400 | 19150 |
| Extended Palliative Laboratory Panel | Inpatient Ophthalmic Radiotherapy Fraction | 15175 | 21500 |
| Inpatient Hepatic Physiotherapy Session | Specialist Otolaryngologic Theatre Time | 37500 | 7050 |

Both services must occur for the same patient/day. Each retains its own
contractual billing unit. These are replacement unit rates, not a single price
for a combined bundle. Evidence: §9 and §9.1.

## Resolved implementation decisions

These choices were approved by the user and are versioned in
[the policy file](../policies/hospital_1.json). They are implementation conventions;
the original ambiguities and contract quotations remain intact.

1. **Exclusions:** Use an inclusive boundary (`≤ N`), the same patient, and all
   invoices. Check trigger dates before and after the excluded service. Only
   the first-column service's charge becomes non-payable, with expected amount
   zero; the trigger is not automatically excluded. Section 10 does not
   explicitly establish the inclusive endpoint or patient scope.
2. **Line ordering:** Use ascending lexical text comparison. All 61,211 IDs
   across five hospitals, in both CSV and JSONL, have fixed-width, zero-padded
   numeric components. Lexical and natural sorting agree with no exceptions.
   Revalidate changed datasets and revisit the convention only on exceptions.
3. **Cumulative usage:** Include all prior original billed quantities for the
   service, including duplicates and disallowed units. Never subtract expected
   payable corrections from utilisation.
4. **Daily caps:** Retain earlier eligible units in ascending lexical line-ID
   order within patient/service/day groups. Exclude the latest excess units;
   a partially excess line retains its allowed payable quantity.
5. **Duplicates:** Retain one eligible payable occurrence. Prefer compliance
   with the applicable adjusted contract rate, including bundles, premiums and
   discounts; break ties by lexical line ID. If none comply and the service
   remains payable, retain the earliest and correct its price. Other duplicate
   occurrences receive zero expected payable amount.

Original invoice lines and billed amounts stay unchanged. Violations are
flagged; corrections affect calculated expected payables only. If differing
quantities or conflicting evidence prevent a defensible correction, flag the
ambiguity for review rather than force an allocation or assume zero.

All 27 previously unresolved rule records now have documented resolutions.
The full extraction passes its policy-readiness gate. That does not mean invoice
calculations have been implemented or case-specific conflicts cannot occur.
Term endpoints remain an inclusive interpretation. `--contract-only` preserves
the original extraction without these conventions for comparison.

The subsequent [Hospital 1 engine milestone](hospital_1_engine.md) implements
matching, calculations and label evaluation. Its additional approved decisions
exclude duplicate charges from delivered premium quantities, preserve separate
quantity tracks and propagate uncertainty. Those applied premium rules are
labelled implementation conventions; the original contract evidence is intact.
