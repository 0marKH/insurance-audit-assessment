# Insurance invoice audit assessment

A deterministic, contract-grounded audit of Hospitals **2–5**, with Hospital 1's
labelled development evaluation preserved. Start with the five deliverables below.

## Deliverables

| Requirement | Where to find it |
|---|---|
| **1. Runnable repository** | [Reproduce the submission](#reproduce-the-submission). Runtime and tests use only Python's standard library; [runtime requirements](requirements.txt) and [pinned PDF dependencies](requirements-writeup.txt) are separate. |
| **2. Submission** | [submission.csv](submission.csv) — the exact six-column template, with integer-cent amounts. |
| **3. Short evaluation report** | [Evaluation report](deliverables/evaluation_report.md) — Hospital 1 development performance by category and four systematic failure types, each with examples. |
| **4. Versioned prompts** | [Prompt history](prompts/README.md) — numbered requests, iterations and approved clarifications. |
| **5. One-page decision log** | [Decision log PDF](deliverables/decision_log.pdf), with [editable source](deliverables/decision_log.md) — assumptions, unresolved ambiguities and choices. |

The supplementary [two-page write-up](deliverables/assessment_writeup.pdf)
([source](deliverables/assessment_writeup.md)) includes contribution disclosure,
limitations and “What I would do with another week.” All reports are together in
[`deliverables/`](deliverables/); the submission stays at the repository root.

## Reproduce the submission

Use **Python 3.9+** (tested on **3.9.6**). The assessment implementation is on the
**Develop** branch:

```bash
git clone --branch Develop https://github.com/0marKH/insurance-audit-assessment.git
cd insurance-audit-assessment
python3 -m assessment_audit
python3 scripts/verify_assessment.py
```

From an existing checkout, run the last two commands from its root. No package
installation, API key, network access or model is needed to run the audit. There
are **zero third-party runtime/test dependencies** to pin. PDF regeneration is
optional and uses exact dependency versions listed below.

The audit regenerates `submission.csv` and target evidence under `outputs/`.
Verification runs **103 tests**, Codex-authored calculation checks, source-data and
frozen-H1 integrity checks, and byte-for-byte reproduction. A nonzero exit means a
check failed. To verify reproduction without writing outputs:

```bash
python3 -m assessment_audit --check
```

Only the combined runner writes the final submission; individual hospital tools
do not replace it.

## Submission coverage

| Hospital | Submitted | Correct | Erroneous | Unique IDs | Coverage |
|---|---:|---:|---:|---:|---:|
| 2 | 492 | 481 | 11 | 1,125 | 43.73% |
| 3 | 425 | 417 | 8 | 932 | 45.60% |
| 4 | 374 | 364 | 10 | 835 | 44.79% |
| 5 | 466 | 456 | 10 | 1,050 | 44.38% |
| **Total** | **1,757** | **1,718** | **39** | **3,942** | **44.57%** |

All 49,796 target lines and 3,968 headers are processed. **2,185 unique IDs are
omitted** where evidence is insufficient. Unresolved invoices are not accepted as
correct; coverage is not accuracy. Hospital 1 is not submitted.

For supporting evidence, open the [coverage summary](outputs/final/summary.json),
[omission reasons](outputs/final/omitted_invoices.csv),
[submission assumptions](outputs/final/submission_evidence.jsonl), or
[confidence method](outputs/final/confidence_method.json).

## Repository map

```text
README.md                   Start here: deliverables and reproduction
submission.csv              Final predictions for Hospitals 2–5
deliverables/               Evaluation, decision log and write-up
prompts/                    Indexed, versioned prompt history
assessment_audit/           Combined runner; Hospital 2, 3 and 5 adapters
hospital_4/                 Hospital 4 extraction and audit engine
hospital_audit/             Frozen Hospital 1 audit engine and shared helpers
contract_extractor/         Frozen Hospital 1 contract extractor
policies/                   Hospital-specific policies and service aliases
profiles/                   Hospital 1 extraction profile
scripts/                    Verification, label comparison and PDF renderer
tests/                      Frozen Hospital 1 tests
outputs/                    Reproducible audit evidence, grouped by hospital
data/assessment/            Original contracts, invoices, labels and template
requirements*.txt           Runtime declaration and pinned PDF dependencies
```

Target-hospital tests live beside their packages; comparison tests are in
`scripts/tests/`. `scripts/verify_assessment.py` runs all four suites. Source
packages and frozen files retain their paths so existing hash checks stay valid.
`outputs/` contains detailed evidence, while `deliverables/` contains the reports
to review. Original inputs remain unchanged. Earlier experiments and development
archives are retained in Git history.

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

The [write-up](deliverables/assessment_writeup.md) includes my reflection under
“What I would do with another week.”

## Optional tools

Compare saved Hospital 1 predictions with labels, or verify its frozen outputs:

```bash
python3 scripts/compare_hospital_1.py
python3 -m hospital_audit --check
```

To regenerate the PDFs, use **Python 3.11+** in a separate documentation environment.
These pinned packages are not required to reproduce the submission:

```bash
python3.11 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r requirements-writeup.txt
.venv-docs/bin/python scripts/build_writeup.py
.venv-docs/bin/python scripts/build_writeup.py --source deliverables/decision_log.md --output deliverables/decision_log.pdf
```
