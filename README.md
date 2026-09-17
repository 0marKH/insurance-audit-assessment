# Insurance invoice audit assessment

Deterministic, contract-grounded invoice auditing for Hospitals **2–5**, with the
original Hospital 1 implementation and labelled evaluation preserved. No runtime
AI, network, API key or third-party dependency is required.

## Reproduce the final submission

From the repository root, using **Python 3.9+** (tested on 3.9.6):

```bash
python3 -m assessment_audit
python3 scripts/verify_assessment.py
```

The first command generates `submission.csv` and target audit evidence. The second
runs **103 tests**, independent manual checks, original-data/H1/H4 preservation
checks, and byte-for-byte reproduction. For reproduction alone:

```bash
python3 -m assessment_audit --check
```

Runtime dependencies are standard-library only (`requirements.txt`). Optional PDF
rendering dependencies are pinned in `requirements-writeup.txt`; they are not
needed to reproduce or validate the submission.

## Results and scope

| Hospital | Submitted | Correct | Erroneous | Unique IDs | Coverage |
|---|---:|---:|---:|---:|---:|
| 2 | 492 | 481 | 11 | 1,125 | 43.73% |
| 3 | 425 | 417 | 8 | 932 | 45.60% |
| 4 | 374 | 364 | 10 | 835 | 44.79% |
| 5 | 466 | 456 | 10 | 1,050 | 44.38% |
| **Total** | **1,757** | **1,718** | **39** | **3,942** | **44.57%** |

All 49,796 line items and 3,968 header records were processed. **2,185 unique IDs
are omitted**, with reasons in `outputs/final/omitted_invoices.csv`; an unresolved
invoice is never silently counted as correct. This is bounded financial auditing,
not certification of every administrative obligation. Target labels are absent:
no H2–5 precision, recall, amount accuracy or calibrated confidence is claimed.

H4's 374-row submission is unchanged. H2/3/5 contribute 1,383 additional rows.
H2's recorded-date Service Day and H5's header facility context are explicitly
user-approved assumptions. H3 implements amendment precedence by service date.
Hospital-specific uncertainties and correction limits remain separate.

## Assessment deliverables

- [submission.csv](submission.csv): exact template columns; source billed cents,
  integer expected totals, unique identifiers and numerical confidence validated.
- [Short evaluation report](docs/evaluation_report.md): frozen H1 per-category
  performance and four systematic failure types; full detail linked below.
- [One-page decision log](docs/decision_log.md) and [PDF](output/pdf/decision_log.pdf).
- [Two-page write-up](output/pdf/assessment_writeup.pdf) and
  [editable source](docs/assessment_writeup.md).
- [Versioned prompts](prompts/): requests, iterations and approved clarifications;
  AI-assisted development is disclosed. No runtime model is used.
- [Contract review and manual calculations](docs/target_hospitals_review.md),
  [H4 review](docs/hospital_4_review.md), and
  [final coverage/validation](outputs/final/summary.json).

`outputs/hospital_{2,3,5}/` contains source-linked rules, all line/invoice results,
review logs and description decisions. `outputs/hospital_4/` remains its frozen v2
record. `outputs/final/` contains combined omissions, confidence method, submission
assumptions and a reproducibility manifest. Original files in `data/assessment/`
are protected by their original SHA-256 inventory.

## Confidence and uncertain corrections

The existing confidence heuristic uses already-exposed H1 outcomes: **0.892297**
for correct rows and **0.581503** for erroneous rows. It is not validated on any
target hospital. No new per-hospital or cap penalty is invented. See
`outputs/final/confidence_method.json` for sample sizes, formula and limitations.

H4 invoices **000165, 000540 and 000554** remain approved **assumption-dependent
cap estimates**, distinguished from their confirmed cap violations in audit and
submission evidence. H2/3/5 cap corrections and duplicate allocations are withheld;
H4-specific correction approval is not automatically transferred. Wrong units,
dual units and uncertain service matches remain review cases. Uncertain original
records still affect cumulative history and other dependencies.

## Preserved development and experiments

- [H1 development evaluation](outputs/hospital_1/evaluation_development.md) and
  [historical held-aside evaluation](outputs/hospital_1/evaluation_held_aside.md).
  Labels are now exposed: subsequent analysis is development analysis, not a fresh
  holdout. `python3 -m hospital_audit --check` verifies the frozen audit.
- [H1 label comparison](outputs/hospital_1/comparison/report.md), reproducible with
  `python3 scripts/compare_hospital_1.py`; original H1 artifacts remain unchanged.
- `baselines/hospital_4_v1/` and `baselines/hospital_4_v2/` preserve both previous
  H4 submissions and associated code/policy/evidence. Run
  `python3 scripts/check_hospital_4_baseline.py` to replay v1 in a temporary tree.
- [Decision history](docs/decision_history.md) and
  [exposed-label investigation](analysis/hospital_1_label_investigation/report.md)
  are historical records. Their old baseline checks refer to the pre-update state.
- [Jev experiment](experiments/jev/report.md) remains separate and experimental:
  no accepted mappings, changed thresholds or runtime dependency. Credentials and
  scratch/cache files are ignored and are not assessment deliverables.

Use the **combined runner** above for the final submission. The preserved
`python3 -m hospital_4` command intentionally writes the old H4-only submission;
if run, rerun `python3 -m assessment_audit` to restore the final file. The final
runner verifies H4 evidence and compares its rows against the v2 snapshot.

## Rebuild documentation (optional)

In a Python 3.11+ virtual environment:

```bash
python3 -m pip install -r requirements-writeup.txt
python3 scripts/build_writeup.py
python3 scripts/build_writeup.py --source docs/decision_log.md --output output/pdf/decision_log.pdf
```

Remaining limits: unresolved quantities/descriptions, H4 discount scope, H3/H5
exclusion interpretation, administrative evidence, and target confidence validation.
The assessment permits partial coverage; no invented payable amounts fill the gaps.
