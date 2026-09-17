# Hospitals 2, 3 and 5: final contract and calculation review

Source-pinned extraction uses the original Markdown contracts. Hospital 4 stays
frozen at its approved v2 result; Hospital 1's engine/evaluation remain unchanged.
This is engineering review of unlabelled hospitals, not measured accuracy.

| Hospital | Implemented contract features | Reference |
|---|---|---|
| 2 | 76 prose catalogue clauses; 9 daily premiums, 8 weekend uplifts, 8 caps, 3 reciprocal bundles, 12 discount tiers, 6 exclusions. | `outputs/hospital_2/rules.json` |
| 3 | 118 original services plus 2 additions; 7 amended rates by service date from 2025-01-01; 14 premiums, 12 weekend uplifts, 12 caps, 5 bundles, 19 discount tiers, 10 exclusions. | `outputs/hospital_3/rules.json` |
| 5 | 84 services, each with three facility and three plan multipliers; 10 premiums, 9 weekend uplifts, 9 caps, 3 bundles, 15 discount tiers, 7 exclusions. | `outputs/hospital_5/rules.json` |

Every pricing rule retains source text, document hash and line/clause reference.
H2's clause inventory distinguishes machine-used pricing/invoice clauses from
administrative or documentary clauses not testable with this dataset. Reciprocal
bundle prose is deduplicated only after confirming the two rates agree. H3 checks
amended old rates and units against Appendix B before accepting replacements.
H5 independently applies facility, then plan, rounding each step before premiums
and discounts. Abbreviation tokens and SA/RM/PH numeric suffixes were inspected
against observed descriptions and the hospital's own catalogue. Price and billed
unit never select a service; matching acceptance thresholds remain unchanged.
All unique descriptions and decisions are saved in each description_review.json.

## Documented boundaries

The user explicitly approved using H2's recorded service date as its Service Day
because timestamps are absent, and H5's header facility code for each invoice
line because line-level facility codes are absent. Context assumptions appear in
line/invoice evidence and the final submission sidecar. Neither is direct validation.

H2 service clauses, H3 §6.1 and H5 §8.1 explicitly establish whole-term/all-patient
volume scope. H2/H3 explicitly exclude the current line; H5's “subsequent units”
is read as prior-line eligibility. Billed history includes rejected quantities;
unknown prior records widen intervals. If the known lower bound already exceeds
the deepest tier, an unknown upper bound cannot change the rate. H4's different
scope uncertainty is preserved and not overwritten.

H2 expressly provides same-patient exclusions and both temporal directions;
strictly inside the window can resolve, while exact endpoints remain uncertain.
H3/H5 do not expressly resolve exclusion population/direction/endpoints. Same-
patient cross-invoice candidates are collected; positive cases are withheld rather
than silently importing H4's approved inclusion policy. This still uses patient
identity as the clinically relevant search scope; broader population interpretations
are not evaluated and remain a limitation.

No H1/H4 duplicate-retention or cap-correction convention is imported into H2/3/5.
Cap violations are flagged, but positive corrected amounts remain unknown. Repeated
service/patient/date groups are withheld. H2 has no equivalent explicit duplicate
prohibition located: its repeat group is an identity/quantity uncertainty rather
than a confirmed contractual duplicate violation. Nonpayable services can still
establish delivery; original history is not reduced. Dual units and ordinary wrong
units remain unresolved without independent evidence.

H3's amendment explicitly makes the two new services nonbillable before 2025-01-01;
that specific case can produce zero. Invalid dates/units do not otherwise imply
zero. Already-settled-invoice protection cannot be checked because settlement data
is absent. H2's submission-within-60-days clause is screened using issue/discharge
dates only; a late issue or missing date is reviewed, not automatically rejected.
Actual submission timestamps, waivers, clinical records and other administrative
compliance cannot be established from invoice tables. Service-date-after-invoice
checks are treated as data validity checks on all hospitals; H2 does not separately
state that restriction. No episode-based price adjustment was found.

## Independent representative checks

Replay: `python3 -m assessment_audit.manual_check`. Constants below were read from
contracts and original records, not obtained by calling the pricing functions.

| Evidence | Calculation in cents | Expected |
|---|---|---:|
| H2-L00325-08 / 09, clauses 14.2 / 16.4 | Bundle 73,625 ×2 and 27,275 ×6 | 147,250 / 163,650 |
| H2-L00607-07 | Prior lower bound 484 >300; 18,475 ×.75 rounded | 13,856 |
| H2-L00625-03 | Prior lower bound 1,664 >300; round 10,050 ×.75 to 7,538, then ×12 | 90,456 |
| H3-L00020-03 / H3-L00461-07 | Same amended service: 2024 rate 182,625 ×2; 2025 rate 208,200 ×2 | 365,250 / 416,400 |
| H3-L00516-06 / 08 | Weekday rate 26,375 ×7; deepest discount 34,775 ×.75 rounded | 184,625 / 26,081 |
| H3-L00716-02 | 30,600 ×2; no weekend uplift contracted for this service | 61,200 |
| H3-L00788-07 / 08 | Bundle 235,000 ×2 and 12,025 ×2 | 470,000 / 24,050 |
| H5-L00015-10 | 284,175 ×1 ×.92 ×1.12, rounded per step, then ×2 | 585,628 |
| H5-L00015-12 / 13 | Round 6,675 ×.90 to 6,008, ×1.25 then ×20; second service 550,750 ×.90, prior 6 below threshold | 150,200 / 495,675 |
| H5-L00132-04 | Round 431,375 ×1.05 to 452,944; ×.90 rounded | 407,650 |
| H5-L00298-01 | 3,750 ×1.10 →4,125; ×.95 →3,919; ×.75 →2,939; ×30 | 88,170 |

Nine independent invoice deltas are checked. Nine sampled review cases confirm
that dual-unit, cap and discount uncertainty stays unresolved across all three
new hospitals. Seventeen focused tests cover effective dates, added services,
rounding, multipliers, bundles, thresholds, exclusions, duplicate/cap safeguards,
unknown units and output tampering. All target records are processed, but only
1,757/3,942 unique invoice IDs pass submission selection. This is not exhaustive
human review or calibration on unlabelled hospitals.
