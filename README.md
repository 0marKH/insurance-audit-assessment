# Insurance audit assessment — Hospital 1

The repository extracts Hospital 1's contract and audits its invoices using
reviewed service aliases, explicit rule passes and exact arithmetic. Both stages
use deterministic Python: no runtime AI, embeddings, OCR, network access or
third-party packages. Original assessment files remain unchanged.

Start with the [engine results and limitations](docs/hospital_1_engine.md), the
[held-aside evaluation](outputs/hospital_1/evaluation_held_aside.md), or the
[line evidence](outputs/hospital_1/line_audit.jsonl).

## Run the Hospital 1 audit

From the repository root, with Python 3.9 or later:

```sh
python3 -m contract_extractor
python3 -m unittest discover -s tests -v
python3 -m hospital_audit
python3 -m hospital_audit.evaluate --split development
python3 -m hospital_audit.evaluate --freeze
python3 -m hospital_audit.evaluate --split held_aside
```

No installation is needed. The 63 tests cover extraction, policy resolution,
matching, rule interactions, uncertainty and evaluation accounting. The audit
takes a few seconds on the development machine; the generated evidence is
about 20 MB. All audit artifacts go under `outputs/hospital_1/`, separate from
the extraction artifacts and any future submission for Hospitals 2–5.

The implementation freeze is already included. Repeating `--freeze` with the
same implementation is safe; changed code cannot replace an existing freeze.
If you change the engine after inspecting held-aside results, preserve this
baseline and describe subsequent evaluation as reuse of an exposed holdout.
For a new output directory, pass the same `--output PATH` to both commands.

```sh
python3 -m hospital_audit --check
python3 -m contract_extractor --check
python3 -m contract_extractor.validate_line_ids --check
```

The checks reproduce artifacts and compare bytes. Evaluation verifies audit
hashes before reading labels. The engine itself never imports label values.
Missing/stale files or invalid references cause a nonzero command exit.

## Current results

| Measure | Development | Held aside |
|---|---:|---:|
| Labelled invoices | 717 | 196 |
| Known erroneous invoices detected | 44 / 44 | 12 / 14 |
| False-positive invoices | 0 | 0 |
| Decision coverage | 398 / 717 (55.5%) | 103 / 196 (52.6%) |
| Known expected totals | 363 / 717 (50.6%) | 94 / 196 (48.0%) |
| Exact amounts among known totals | 363 / 363 | 93 / 94 |

These are conditional results from a small synthetic dataset. Review cases are
not counted as correct. No numerical confidence or calibration is claimed.
The held-aside split is by invoice ID; all records still provide contractual
context, so it is not an independent hospital/patient evaluation. See both
generated reports for per-category precision/recall, coverage and examples.

`invoice_audit.csv` is a development review table, **not** `submission.csv`.
`line_audit.jsonl` includes originals, matched service/candidates, rule and
clause references, quantity tracks, adjustments, violations and uncertainty.
`review_log.jsonl` lists unresolved evidence and affected calculations.
`run_manifest.json` records code, policy, input and output hashes.

## Contract extraction

Read the [Hospital 1 review](docs/hospital_1_review.md), then inspect the
[complete extracted rules](outputs/hospital_1.rules.md) or their
[machine-readable JSON](outputs/hospital_1.rules.json).

## Run

From the repository root, using Python 3.9 or later:

```sh
python3 -m contract_extractor
python3 -m unittest discover -s tests -v
python3 -m contract_extractor --check
python3 -m contract_extractor.validate_line_ids --check
```

No installation is required. The local verification used Python 3.9.6. There
are no dependency versions to resolve; `requirements.txt` intentionally has
no packages.

The default run generates `outputs/hospital_1.rules.json` and
`outputs/hospital_1.rules.md`. A custom location is supported:

```sh
python3 -m contract_extractor --contract data/assessment/contracts/hospital_1/provider_services_agreement.md --output /tmp/hospital-1-rules
```

Exit codes:

- `0`: extraction completed; interpretation questions may remain.
- `1`: unsupported/malformed contract, conflicting evidence, I/O failure, or stale artifacts with `--check`.
- `2`: `--require-resolved` was supplied and interpretation questions remain.

`--check` compares both generated artifacts without modifying them.
`--require-resolved` is an optional gate for future engine integration. It now
passes with the user-approved conventions in `policies/hospital_1.json`.
The source ambiguities remain visible as resolved assumptions rather than being
presented as explicit contractual requirements.

To inspect the contract without implementation conventions:

```sh
python3 -m contract_extractor --contract-only --output /tmp/hospital-1-contract-only
```

That mode retains the original 27 unresolved rule records; adding
`--require-resolved` returns exit code 2.

The read-only identifier validator checks every hospital's CSV and JSONL files:

```sh
python3 -m contract_extractor.validate_line_ids
```

All **61,211** line IDs in each format match `H[1-5]-L[0-9]{5}-[0-9]{2}`.
CSV and JSONL identifiers match, IDs are unique, and lexical/natural sorting
agree both per hospital and globally. Exceptions on future datasets return
`review_required` (exit code 2); missing/broken inputs or a stale `--check`
artifact return exit code 1. Revalidate when data changes; do not switch sorting
methods automatically.

## What is included

The baseline produces **174 rules**: 108 catalogue entries, 9 threshold
premiums, 7 weekend uplifts, 11 volume-discount tiers, 7 caps, 3 bundle pairs,
6 exclusions, and 23 scope/definition/calculation/grouping/invoicing rules.
Every rule follows:

**Applies to → Condition → Action → Scope → Order → Source → Uncertainty**

Source evidence contains the exact quote, section, line numbers and SHA-256
of the source document. Monetary values are integer cents; multipliers are
integer fractions. No floating-point amounts are introduced.

The parser recognizes **206/206 nonempty lines** in this source version.
That is structural coverage, not an accuracy score. See the
[extraction evaluation](docs/extraction_evaluation.md) for validation and limits.

## How it works

`contract_extractor/extract.py` reads the original Markdown. It parses values
from the tables and links them to exact, reviewed prose in
`profiles/hospital_1.json`. The profile encodes the meaning of clauses such as
prior usage, patient/day aggregation and adjustment order. Those meanings
were authored during development, not discovered by a general language parser.
`contract_extractor/policies.py` then applies the separately versioned user
conventions, retaining original contract evidence and ambiguity questions.
Policies cannot override blocking extraction diagnostics.

Unknown prose, altered table headers, missing required clauses, invalid units,
unrecognized service references and contradictory caps produce blocking
diagnostics. A partial parse is saved for review with `status: blocked` and
every rule marked `ready_for_engine: false`.

This is a Hospital 1 Markdown profile. Other hospitals, arbitrary rewrites,
plain text and PDFs require additional parsers or reviewed templates. Changed
rates and table thresholds are read dynamically when the supported structure
remains intact. A deleted standalone rate row cannot be identified as missing
from structure alone; the pinned snapshot and baseline inventory tests protect
against that regression in this assessment.

## Assessment source and scope

The [upstream assessment](https://github.com/majedzahrani3/insurance_auditing)
was cloned at commit `6fee1da60b74512156637a22be15d996a36627e1`. Its files are
copied unchanged into `data/assessment/`, with an individual file hash manifest
in `data/assessment/SOURCE.json`. The original brief remains at
`data/assessment/README.md`. Your existing repository and Git remote are retained.

Only Hospital 1's contract is extracted and audited. Other hospitals and
`submission.csv` remain outside scope. No invoice or label values are used to
derive contract rules. Development descriptions inform the reviewed alias
map, and development labels inform evaluation and error analysis. The split
protocol and the development-only correction to duplicate-violation attribution
are documented in the engine report. Source-integrity tests verify the supplied
files against their original hashes.

The engine implements these expected-payable conventions:
inclusive same-patient exclusions; lexical allocation; original billed usage;
partial cap allocation; and pricing-aware duplicate retention. Original invoice
lines and billed amounts remain unchanged. Indefensible allocations are flagged
for review, without a forced expected amount. Delivered quantities exclude
duplicate charges for premium eligibility, while cumulative history retains
all original billed quantities. Missing compatible quantity units propagate
uncertainty rather than an invented conversion.

See the [extractor interface](docs/extractor_interface.md) for integration and
the [decision log](docs/decision_log.md) for readings and unresolved questions.
AI-assisted development is disclosed in [prompts/001_hospital_1_extraction.md](prompts/001_hospital_1_extraction.md);
the extractor itself uses no AI. The user's follow-up decisions are preserved
in [prompt 002](prompts/002_open_decisions.md), and the engine request in
[prompt 003](prompts/003_hospital_1_engine.md).
