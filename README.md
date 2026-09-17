# Insurance invoice audit assessment

Deterministic, contract-grounded auditing for Hospitals **2–5**. Hospital 1's
labelled evaluation is preserved. No runtime AI, network, credentials or third-party
packages are required.

## My contribution and AI assistance

I chose a simple deterministic rules engine, supplied the architecture and rule
format, set the scope, and approved the interpretation and correction policies.
I approved Hospital 4 after Codex recommended its simpler contract, then requested
coverage of Hospitals 2–5. I also supplied Hospital 1 labelled examples for further
investigation and approved the documented H2 date and H5 facility assumptions.

Codex inspected the contracts and data, built the extractors, description matcher,
audit engines, tests, evaluation and submission tooling, and drafted the
supporting documentation. **Codex performed the source-based manual calculation
checks and implemented their scripted replay.** These were not independent human
adjudication or validation against hidden target-hospital labels.

I initiated a **TypeSafe Jev** classification experiment and later stopped that
work. Codex ran `jev-1.13.0` on 12 clear controls and 23 unresolved descriptions.
The controls agreed with Codex-assisted reference judgments; unresolved cases
produced 16 abstentions and seven unsupported proposals. **Zero new mappings were
accepted**, with no changes to matching thresholds or submission results. This
was exploratory, not an unbiased accuracy test. Experimental working files were
removed during cleanup; [the saved prompt](prompts/006_jev_matching_pilot.md) and
Git history preserve the experiment's disclosure and evidence.

The [write-up](docs/assessment_writeup.md) includes my reflection under
“What I would do with another week.”

## Run and verify

Use **Python 3.9+** (tested on 3.9.6), from the repository root:

```bash
python3 -m assessment_audit
python3 scripts/verify_assessment.py
```

The first command regenerates the submission and all target audit outputs. The
second runs **103 tests**, Codex-authored calculation checks, original-data/H1 integrity
checks and byte-for-byte reproduction. To check reproduction only:

```bash
python3 -m assessment_audit --check
```

The combined runner owns `submission.csv`. Individual hospital tools do not
replace it. Runtime requirements are standard-library only (`requirements.txt`).

## Submission

| Hospital | Submitted | Correct | Erroneous | Unique IDs | Coverage |
|---|---:|---:|---:|---:|---:|
| 2 | 492 | 481 | 11 | 1,125 | 43.73% |
| 3 | 425 | 417 | 8 | 932 | 45.60% |
| 4 | 374 | 364 | 10 | 835 | 44.79% |
| 5 | 466 | 456 | 10 | 1,050 | 44.38% |
| **Total** | **1,757** | **1,718** | **39** | **3,942** | **44.57%** |

All 49,796 target lines and 3,968 headers are processed. **2,185 unique IDs are
omitted** where evidence is insufficient. Reasons are recorded in
`outputs/final/omitted_invoices.csv`; unresolved invoices are not accepted as
correct. No target-hospital accuracy or calibration is claimed without labels.

## Assessment deliverables

- [submission.csv](submission.csv): exact template columns, integer-cent amounts.
- [Evaluation report](docs/evaluation_report.md): Hospital 1 per-category results
  and systematic failure analysis.
- [Decision log](docs/decision_log.md), with a [one-page PDF](output/pdf/decision_log.pdf).
- [Two-page write-up](output/pdf/assessment_writeup.pdf), with
  [editable source](docs/assessment_writeup.md).
- [Prompts](prompts/): the assessment requires versioned disclosure of AI-assisted
  development, including iterations and approved clarifications.

`outputs/hospital_*/` holds current source-linked rules, line/invoice evidence,
review cases and evaluation. `outputs/final/` holds combined coverage, omissions,
confidence, assumptions and checksums. Original files under `data/assessment/`
are protected by their source manifest. Tests and manual checks are included.
Earlier development archives and experimental material remain in Git history,
not in the assessment working tree.

## Interpretation and confidence

H2's recorded-date Service Day and H5's header facility context are explicitly
approved assumptions. H3 selects amended rates by service date. H4's volume scope
remains unresolved. Correction conventions are kept hospital-specific.

H4 invoices **000165, 000540 and 000554** are approved **assumption-dependent cap
estimates**, separate from their confirmed violations. H2/3/5 cap corrections and
duplicate allocations are withheld. Wrong units, dual units and uncertain matches
remain review cases and continue to affect dependent calculations.

Confidence uses the existing exposed-H1 heuristic: **0.892297** for correct and
**0.581503** for erroneous rows. These are not calibrated target probabilities;
no extra cap or hospital penalty is invented. See
`outputs/final/confidence_method.json` and the decision log for limitations.
H1's original evaluation remains unchanged; its labels are now exposed, so further
analysis is not fresh held-out validation.

## Optional tools

```bash
python3 scripts/compare_hospital_1.py
python3 -m hospital_audit --check
```

The comparison joins saved H1 predictions and labels. To rebuild the final PDFs
separately, use Python 3.11+ and the pinned documentation-only dependencies:

```bash
python3 -m pip install -r requirements-writeup.txt
python3 scripts/build_writeup.py
python3 scripts/build_writeup.py --source docs/decision_log.md --output output/pdf/decision_log.pdf
```
