# Hospital 1 invoice-audit engine

The Hospital 1 pipeline runs end to end and preserves the original assessment
files. It uses the existing rule register and user-approved policies, with
reviewed text abbreviations and no runtime AI. The current limit is evidence
coverage: about half of labelled invoices can receive a complete automatic
decision, and roughly half have a defensible expected total.

## Reproduce

```sh
python3 -m contract_extractor
python3 -m unittest discover -s tests -v
python3 -m hospital_audit
python3 -m hospital_audit.evaluate --split development
python3 -m hospital_audit.evaluate --freeze
python3 -m hospital_audit.evaluate --split held_aside
python3 -m hospital_audit --check
```

Python 3.9+; no third-party dependencies. All 63 tests pass. The included freeze
and hashes identify the evaluated implementation. Changing code requires a new
versioned evaluation; the existing held-aside labels have now been inspected
and must not be described as untouched for future tuning.

## What runs

1. **Validate and join.** Keep raw headers and lines, require an unambiguous
   invoice join, validate dates, identifiers, quantities and monetary fields.
   Group using the applicable Hospital 1 contract, including invoices with an
   incorrect printed number. Missing/reused header identifiers do not select a
   header by convenience; their affected quantities/amounts remain uncertain.
2. **Match descriptions.** Expand the reviewed abbreviations, ignore word order
   and `/NG-...` suffixes, and compare textual tokens to catalogue names. Require
   a unique supported candidate. Prices and billed units are not matcher inputs.
   All 108 contractual names remain exact in evidence. A description with no
   supported candidate is conservatively potentially relevant to any service.
3. **Gather context.** Find related services across all invoices for the patient
   and date/window. An unresolved candidate, patient, date or necessary quantity
   can make a relation uncertain. A known non-payable charge still supports
   delivery; it is not deleted from context.
4. **Separate quantities.** Keep original billed quantity for cumulative
   history. Equal-quantity duplicates establish one delivered occurrence for
   premiums; differing quantities remain uncertain. Determine payable quantity
   only after selecting the retained occurrence and applying any cap.
5. **Price in order.** Bundle replacement, facility multiplier, plan multiplier,
   premium/uplift, deepest eligible volume discount, quantity multiplication,
   invoice sum. Use integer cents and exact fractions; round half up after each
   step. A threshold premium applies to all units. Cumulative thresholds are
   strict and use history before the current line, sorted by date then lexical ID.
6. **Retain and cap.** Prefer a duplicate occurrence compliant with its applicable
   adjusted unit rate; break ties lexically. If none comply and the service is
   payable, correct the earliest occurrence's price. Then retain earlier eligible
   units under the cap, including a partial line. Conflicts go to review.
7. **Decide separately from money.** A known violation can make an invoice
   erroneous even when its amount is unknown. An unresolved line prevents a
   correct decision. Incorrect printed numbers are flagged without suppressing
   contract pricing. Invalid dates and unsupported unit conversions are not
   assigned zero. Excluded charges and defensibly discarded duplicates are zero.

The implementation is Hospital 1-specific. It does not infer an arbitrary rule
language from prose. Shared definition records explain concrete service rules;
they are not applied as duplicate adjustments. In Hospital 1, multiple equal
service/patient/day charge lines are duplicate occurrences, so a defensible
duplicate group normally yields one retained line before the cap allocator.

## Evidence and outputs

All development artifacts are in `outputs/hospital_1/`:

| Artifact | Contents |
|---|---|
| `line_audit.jsonl` | 11,415 original line records plus match/candidates, rule IDs, source sections, original/delivered/payable quantities, rate steps, violations and uncertainty |
| `invoice_audit.jsonl` | 918 original header records, expected/billed totals, decision, known-violation and review states, linked line keys, null confidence |
| `invoice_audit.csv` | Concise development review table; blank expected totals are unresolved, not zero |
| `review_log.jsonl` | Unresolved line/invoice evidence and affected dependencies |
| `summary.json` | Matching, amount and decision coverage |
| `run_manifest.json` | Code, policies, input and artifact hashes; records that labels are not engine inputs |
| `evaluation_development.*` | Development metrics and examples |
| `evaluation_held_aside.*` | Frozen held-aside metrics and examples |
| `evaluation_freeze.json` | Implementation hashes recorded before scoring held-aside labels |

There are 913 unique invoice IDs. Reused header identifiers are consolidated by
ID for scoring, with their expected amount left unresolved. All 913 label IDs
are present in predictions; none is silently dropped. Original files are checked
against the source hash manifest in the extraction tests.

Exact quotes and document hashes are available by following each line's rule ID
into `outputs/hospital_1.rules.json`. Line `source_clauses` is a compact section
index. Dependency lists include counts and at most 20 sample record keys; this
limit is explicit, and full contexts can be reproduced from the original inputs.
`delivered_quantity` is a shared patient/service/day value, not an additive value
to sum across duplicate line records. `rate_is_provisional` indicates invalid
identity/date evidence; a provisional rate does not establish a payable charge.

## Measured results

| Measure | Development | Held aside |
|---|---:|---:|
| Labelled invoices | 717 | 196 |
| Erroneous labels | 44 | 14 |
| Detected erroneous invoices | 44 | 12 |
| False-positive invoices | 0 | 0 |
| Review-only invoices | 319 | 93 |
| Automatic decision coverage | 55.51% | 52.55% |
| Known-error precision | 44/44 | 12/12 |
| Known-error recall, counting review as not detected | 44/44 | 12/14 |
| Expected totals established | 363/717 | 94/196 |
| Exact expected totals among established amounts | 363/363 | 93/94 |

Overall, 11,131/11,415 descriptions are uniquely matched, 10,551 line expected
amounts are known, and 457 header expected totals are known. These counts are
not all the same denominator: the dataset has repeated invoice headers, and an
invoice needs all its lines resolved to establish its total.

The held-aside error-amount difference totals **14775 cents** over the 94 known
amounts; the exact mean absolute error is `14775/94` cents. No invoice with a
labelled error was accepted as correct: the two undetected errors were sent for
review. That does not make recall 100%; known-error recall is 85.71%.

See [development category metrics](../outputs/hospital_1/evaluation_development.md)
and [held-aside category metrics](../outputs/hospital_1/evaluation_held_aside.md).
They distinguish detecting any error on an invoice with a category from detecting
the category itself. Pricing categories are grouped because several different
adjustment defects can explain a rate mismatch. Multi-label invoices count in
multiple category rows. There is no numerical confidence score or calibration.

## Evaluation protocol and tuning

The first eight hexadecimal digits of SHA-256(invoice ID), modulo five, assign
zero to held-aside and the rest to development. Descriptions were inspected only
on the development subset; a common abbreviation map was then fixed. No service
was selected by matching its price. Development label inspection found two false
positives caused by attributing duplicate-charge violations to retained valid
occurrences. The implementation now preserves the group evidence but attributes
the rejected duplicate charge to discarded lines. This was tested before freeze.

The freeze precedes the held-aside report. All invoices necessarily supply
cross-invoice bundles, exclusions and billed usage, including records whose
labels were held aside. Thus this measures performance on held-aside targets
within the same synthetic contract population, not an independent clinical,
patient, hospital or future-time sample. Held-aside labels were used afterwards
only for scoring and the following failure analysis; no code or aliases were
changed to improve those results.

## Systematic limitations

1. **Descriptions can omit the identifying information.** `Visit Amb Hm` on
   `INV-H1-000001` could be either ambulatory cardiac or infectious home visit.
   `Procedure Immun Endosc` on `INV-H1-000657` leaves two services possible.
   The latter invoice has a wrong-unit label but remains review-only because
   this baseline checks units after a unique match. Future candidate-consensus
   checks could establish violations shared by every candidate without selecting
   a service. This improvement was not made after exposing the held-aside labels.
2. **Uncertain records affect other calculations.** `INV-H1-000038` has uncertain
   volume discounts due to prior ambiguous usage. The engine propagates intervals
   rather than dropping those rows. If the lower bound already exceeds the
   deepest tier, the rate can still be resolved; otherwise it remains unknown.
   Completely unsupported descriptions create broad possible dependencies, which
   is conservative and lowers coverage. `INV-H1-000667`, labelled unknown service,
   goes to review and affects same-day duplicate/delivery context.
3. **Quantity, join and date evidence may not support a correction.** Unit
   mismatches such as `INV-H1-000211` are flagged but not converted. Reused header
   IDs have ambiguous joins. Conflicting duplicate quantities leave premium and
   retention decisions uncertain. A date violation may be known while its payable
   amount remains unknown. These are intended review outcomes, not zero charges.
4. **Approved correction conventions can disagree with expected labels.**
   `INV-H1-000015` bills nine Advanced Rheumatologic Laboratory Panel tests at
   14775 cents each. The contractual cap is four, so the policy retains four
   tests for 59100 cents. The calculated invoice total is 1210600 cents; the label
   says 1195825, lower by exactly one test's rate. This establishes a benchmark
   disagreement; it does not prove which latent quantity the label generator
   used. There is no independent evidence here to replace the approved four-unit
   cap allocation with three. The frozen engine and its reported mismatch remain.

These results do not establish that a runtime model is needed. Missing qualifiers
can require additional evidence that a model cannot reliably invent. More reviewed
text rules and candidate-consensus checks should be measured first.

## Scope and budget

Complete: Hospital 1 loading/joining, matching, cross-invoice context, restrictions,
pricing and corrections, uncertainty propagation, evidence, tests and separate
development/held-aside evaluations. Original invoices and extracted source evidence
are preserved. Policy-readiness means policies are defined; it does not mean
every input invoice has enough evidence for a complete decision.

Unresolved: the records in the review log, the held-aside cap/label discrepancy,
candidate-consensus violation detection and recovery from ambiguous invoice joins.
No runtime model, dashboard, warehouse or general rule framework was added.
Hospitals 2–5 and a final `submission.csv` are outside this milestone.

The implementation and evaluation were kept to one bounded work session; the
first recorded runtime checkpoint was 00:04 Riyadh time on 15 September 2026,
and the frozen evaluation was complete by 00:21. Earlier human/assessment time
is not fully recorded, so no remaining hours are invented. Further improvements
are documented rather than pursued through open-ended tuning.
