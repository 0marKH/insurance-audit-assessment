# Insurance audit assessment — Hospital 1 extraction

This first milestone extracts Hospital 1's contract into evidence-backed rules.
The runnable extractor is deterministic Python: no AI calls, embeddings, OCR,
network access, or third-party packages.

Start with the [Hospital 1 review](docs/hospital_1_review.md), then inspect the
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

Only Hospital 1's contract is extracted. Invoice service-name matching,
calculation, label-based evaluation, other hospitals and `submission.csv`
belong to later milestones. No invoice or label values are used to derive
these rules. A source-integrity test hashes the supplied files without using
their contents to infer rules.

Corrections are represented as conventions for future expected payables:
inclusive same-patient exclusions; lexical allocation; original billed usage;
partial cap allocation; and pricing-aware duplicate retention. Original invoice
lines and billed amounts remain unchanged. Indefensible allocations must be
flagged for review, without a forced expected amount.

See the [extractor interface](docs/extractor_interface.md) for integration and
the [decision log](docs/decision_log.md) for readings and unresolved questions.
AI-assisted development is disclosed in [prompts/001_hospital_1_extraction.md](prompts/001_hospital_1_extraction.md);
the extractor itself uses no AI. The user's follow-up decisions are preserved
in [prompt 002](prompts/002_open_decisions.md).
