# Hospital 4 contract review and scope

## Selection, before implementation

| Contract | Additional work / unresolved assumptions | Decision |
|---|---|---|
| 2 | Prose catalogue; 07:00–06:59 service day rather than calendar day; episode definitions; a dual billing unit. Requires new temporal context and more parsing. | Defer. |
| 3 | Base agreement, appendix and amendment; service-date rate versions, seven changed rates and two added services; document precedence and a dual billing unit. | Defer. |
| 4 | One structured document; existing arithmetic, bundle, premium, cap, discount and exclusion types; uniform facility/plan rates, empty weekend schedule. Calendar service days. Some interpretation gaps, handled by abstention. | Selected and explained in conversation before implementation. |
| 5 | Service-specific facility/plan multipliers, facility-location evidence discrepancy, dual billing unit and usage/exclusion ambiguities. | Defer. |

Selection compares incremental implementation and interpretation cost, not measured
accuracy or label performance. Hospital 4 has more catalogue rows than some alternatives,
but needs fewer new calculation types.

## Reviewed reference

Source: `data/assessment/contracts/hospital_4/conditional_reimbursement_agreement.md`,
SHA-256 `715c7db32ff8c6fcd28bb7c9bcba7c2b14137d473305197950e901a08df73ec3`.
Calderwood University Teaching Hospital; contract INS-H4-2024-2049; GBP;
1 January 2024 through 31 December 2025.

The source-pinned extractor represents 31 numbered clauses and 160 table rows:
98 catalogue services, 18 premiums, 18 caps, 7 bundle pairs, 4 discount tiers and
15 directional exclusions. Its 192 rule records retain applies-to, condition,
action, scope, order, source and uncertainty. Sources include exact text, clause,
line and file hash. Structural coverage is not a semantic accuracy estimate.
Changes to the contract hash require review before extraction proceeds.

Reviewed order (§4): substitute bundle rates, facility multiplier, plan multiplier,
premiums, deepest qualifying discount, then quantity; round half away from zero
after each applicable step. All rates and totals use integer cents with exact
rational intermediates. §2.2 makes both multipliers one. §10 has no weekend rates.
Premiums use strict greater-than and apply to all eligible units that day (§5.1).
§6.1 explicitly makes excess units nonpayable. §7 is same patient/calendar day.
§9 explicitly specifies same patient, both date directions and cross-invoice
search; only the first service's charge is excluded. §11 forbids duplicate
service/patient/date charges and repeated invoice identifiers.

## Independent Hospital 4 policies

Machine-readable policy: `policies/hospital_4.json`; alias review:
`policies/hospital_4_aliases.json`. Hospital 1 policies are not loaded.

- **Discount population/reset:** §§8.3–8.5 define prior usage, strict thresholds,
  deepest tier, no splitting the crossing line, and date/line ordering. They do
  not define whose utilisation accumulates or a reset horizon. Use zero as a
  lower bound and original billed contract-term quantities as a working upper
  bound; price only when all scopes inside those bounds agree. This assumes the
  supplied contract-term records bound relevant usage; outside-term carry-in is
  not evidenced. Unknown prior units/dates can make the upper bound unbounded.
  Do not infer scope from billed prices. Correction quantities never lower usage.
- **Dual unit:** `Intermittent Urologic Telemetry Monitoring` has “per hour, per
  item” at 7,275 cents. Preserve that text. It is unclear whether the supplied
  quantity is hours, items or their product. Recognize the description but withhold
  quantity/rate calculation. Keep it as a possible exclusion trigger for the
  neurological laboratory panel. No inferred conversion.
- **Exact exclusion endpoints:** approved `≤ N` under prompt 008. Preserve same
  patient, both temporal directions, cross-invoice search and exclusion of the
  first-column service only. Analogous H1 wording and labelled 000847/000211
  support this interpretation; this is not direct H4 validation.
- **Duplicate correction:** retain the earliest eligible lexical line ID only for
  exact copies of service, patient, date, quantity, billing unit, unit rate and
  line charge, including multi-unit copies. Require known, consistent eligibility
  and adjusted rates. Reject other payable copies; keep original records/history.
  Conflicting quantities, rates, eligibility or uncertain related occurrences
  remain unresolved. H1's broader price-aware selection is not adopted.
- **Cap correction:** §6.1 establishes the cap violation, but not actual delivery.
  Use min(inferred delivered quantity, cap) on the retained eligible occurrence
  as an approved **assumption-dependent estimate**. Keep otherwise-defensible
  rows. Separate `confirmed_violations` from `amount_dependent_violations`, and
  `amount_assumptions` from blocking `uncertainty`. The invoice and submission
  evidence carry `expected_amount_status=assumption_dependent`. H1 development
  analysis of already-exposed labels implies below-cap quantities in four cases;
  three are conditional residual reconstructions. The cause remains unproven.
- **Wrong units:** no new H4 case-specific quantity evidence was provided. All
  ordinary mismatches and the dual-unit ambiguity remain unresolved; neither H1
  labels nor price agreement establish a conversion or a harmless typo.
- **Identity/dates:** applicable agreement comes from the H4 dataset; flag an
  incorrect printed contract number separately. Inclusive term endpoints are a
  documented interpretation. Invalid dates, joins and units remain review cases;
  they do not imply zero reimbursement. All source records remain unchanged.
- **Matching:** case/word-order normalization, independently inspected abbreviation
  tokens and CW suffix removal. Require one supported candidate; never use prices
  or units to decide the service. Unresolved candidates propagate into context.

## Reuse boundary and limitations

`hospital_4.engine.Hospital4Engine` reuses the frozen calculation passes and exact
arithmetic with a separate H4 initializer, catalogue, policies and matcher. The
base class contains one H1 hospital-header check: a private copied header maps a
verified H4 identity to that check, then the original H4 header is restored in
all public evidence. Wrong-hospital headers still fail. No printed contract or
patient grouping is translated. Tests cover this compatibility adapter.

The adapter accepts the shared engine's duplicate result only where identical
original and adjusted rates make its choice necessarily equal the approved
lexical choice. For conflicting groups, provisional payable amounts, retention
keys and final amount steps are removed; dependent financial flags are withdrawn.
Confirmed duplicate violations remain. Presence never depends on payability.
Hospital 1 files, hashes and evaluation remain unchanged.

The run includes 10,560 lines and 840 headers (835 distinct IDs). Submission is
374 rows, 364 correct and 10 erroneous, 44.79% of H4 IDs. Omitted: 461 distinct
IDs / 466 headers. Overall H2–5 coverage is 374/3,942 (9.49%). No H1 IDs are
submitted; H2/3/5 remain unaudited and H4 accuracy is unknown without labels.

The v1 baseline is archived with hashes in `baselines/hospital_4_v1/`. The
reproducible `outputs/hospital_4/policy_change_report.{md,json}` identifies four
additions (000018, 000069, 000084, 000235), zero removals and zero changes to
previously submitted rows. All ten changed line amounts were previously unknown;
other blockers keep 000168/000309/000473/000658/000693 omitted. Cap evidence is
updated without changing amounts for 000165/000540/000554. The historical H1
investigation remains unchanged under `analysis/hospital_1_label_investigation/`.

## Confidence proposal

The original H1 holdout is already exposed. Its frozen results remain evaluation
history, not fresh validation. Use the existing H1 rows that pass the same strict
submission gate: unique ID, known amount, decisive classification, no uncertainty.
A joint success means both the flag and exact expected cents match the label.
The correct class has 445/445 joint successes; the erroneous class has 11/12.

For each predicted class use `0.90 × Wilson95Lower(successes, n)`, z=1.96, rounded
to six decimals. This yields **0.892297** for correct rows and **0.581503** for
erroneous rows. The lower value for errors reflects the small sample and known
H1 cap-amount mismatch. The 0.90 transfer factor is explicitly a conservative
heuristic, not an estimated adjustment or validated confidence calibration.
Correlated invoices weaken interval interpretation. Categories and individual
rule types are not separately calibrated. H4 labels are unavailable; do not
interpret these scores as established H4 probabilities. Counts, formula and
limitations are reproduced in `outputs/hospital_4/confidence_method.json`.

The cap rows keep the existing erroneous-class score, with **no invented penalty**.
That score is not cap-specific calibration or evidence that the estimated amount
is correct. `submission_evidence.jsonl` separates the amount status, assumptions,
confirmed violations, amount-dependent comparisons and numerical-score basis.
Only the explicitly approved cap assumption can pass the otherwise strict gate;
unresolved scope, unit, matching or duplicate conflicts still block submission.

## Time and next work

Scope stopped at one unlabelled hospital. The assessment cap is six to eight
hours; previous human working time is unavailable in this session, so no remaining
budget or total-hours claim is made. Runtime AI, H2/3/5 engines, adjudication of
omitted records and confidence validation on new labels are unfinished/outside
this bounded deliverable. Clarify the remaining scope, unit and quantity gaps before expanding
coverage; then choose H3 if amendment support is worth the remaining budget.
