# Jev description-matching pilot: documentation review and offline preparation

Status: API documentation read and a live pilot completed on 17 September 2026.
35 responses are cached: 23 unresolved descriptions and 12 clear positive controls.
See report.md and results.csv. No new matches were accepted and no baseline audit
outputs changed. The local .env credential is ignored by Git and is never logged.

## Documented interface

POST https://api.typesafe.ai/v1/systemone with a Bearer API key and JSON body:
`state`, `model`, and `questions`. State can be text, object or array. Questions
are keyed objects containing type, instructions and (for Choice) a criteria map.
Answers are returned under the same keys. State provides evidence; instructions
specify the decision. Several questions share one state but are evaluated
independently, so one question cannot consume a sibling answer in the same call.

Choice supplies choice, all option probabilities, and confidence. Noul supplies
a yes-probability; Score supplies a rubric-based score. Choice supports up to 255
options, so H4's 98 services plus NONE_OF_CATALOGUE and INSUFFICIENT_INFORMATION
fit in a single question. Full-catalogue comparison avoids restricting Jev to
our existing matcher's possibly wrong shortlist. Use string option descriptions
(the API reference and more advanced guide differ on richer criteria shapes).

Pin jev-1.13.0, currently the documented target of jev-latest, and record the
returned model version. Current advertised price: $0.042 per million input tokens,
output tokens free. Record actual usage and account billing rather than claiming
an exact cost before a run. The Python SDK requires Python >=3.10; direct HTTP
can preserve the current Python 3.9 standard-library runtime in a separate client.
Handle 401/422 as configuration/validation errors; bounded backoff for 429/529.
Keep credentials out of payload files, source control and logs.

## What the current data actually contains

The 194 H4 lines unresolved specifically by description have 23 unique original
strings. Of those lines, 181 have two plausible catalogue candidates (10 unique
strings), often because the distinguishing qualifier is missing; 13 have a broad
98-service fallback (13 strings). Separately, 104 lines have a recognized service
but an ambiguous contractual billing unit. Classification does not settle that
unit interpretation. The previously reported 253 affected invoice IDs include
propagation, not 253 distinct descriptions.

Example: CARDIAC physio SESS identifies cardiac physiotherapy but omits whether it
is Emergency or Outpatient. Both are contracted. A model's confident preference
is not additional evidence of which was delivered. Conversely an explicitly
unsupported specialty/service combination may be recognized as outside the
catalogue, potentially avoiding the current all-services fallback. That conclusion
needs independent review before shrinking dependency candidate sets.

## Prepared request and bounded test

`python3 experiments/jev/prepare.py` reproduces requests.jsonl,
example_request.json, review_inventory.json and preparation_summary.json. This
is offline preparation only. Each request carries a description (decorative CW
suffix removed) and reviewed abbreviation glossary, with all 98 exact service
names as Choice options. No prices, billed units, quantities, patient identifiers,
invoice identifiers, labels or baseline predictions are sent as model evidence.
The local inventory maps requests back to affected lines and records candidate
sets separately. Raw-description deduplication means repeated identical requests
can be cached without leaking an invoice-specific pricing hint.

Start with these 23 questions; add a small independently reviewed set of clear
matches as positive controls before assessing performance. Review targets before
seeing Jev answers: exact service, outside catalogue, or insufficient information.
These new line-level references are necessary: H1 invoice-error labels are not
service-match ground truth, and the baseline matcher's choices are not truth.
A reviewer may leave a target unknown. Keep such cases out of accuracy denominators.
Do not automatically accept a response based on a guessed confidence threshold.

Capture model/version, full probabilities, reported confidence, top-two margin,
request/response hashes, usage and latency. Cache exact requests and retain raw
responses. Measure exact service correctness, unsupported forced matches,
appropriate abstention and coverage on reviewed cases; report both unique-string
and line-weighted counts. Fit any acceptance threshold on a tuning portion and
report results on a separately reviewed, unused portion. This small pilot cannot
establish robust calibration. H1's already-exposed holdout is regression evidence,
not fresh validation, and H4 invoice accuracy remains unknown without labels.

Only reviewed accepted mappings should enter a separate experimental audit replay.
Then measure affected line amounts, dependent invoice changes, coverage recovered
and regressions relative to the frozen outputs. Keep current submission.csv and
H1/H4 baseline artifacts intact. A Noul evidence-sufficiency question can be a
later diagnostic, but its answer is correlated with the Choice and not independent
verification. Jev confidence measures distribution concentration; it must not
replace invoice confidence or be assumed calibrated on this dataset.

If Jev fails on genuinely recoverable descriptions, compare another classifier
on the same reviewed examples. Missing clinical qualifiers, unclear contractual
units, discount population/reset scope and exclusion endpoints need evidence or
policy clarification rather than another model's guess.

## Official references

- [State](https://docs.typesafe.ai/concepts/state)
- [Choice](https://docs.typesafe.ai/primitives/choice)
- [API reference](https://docs.typesafe.ai/api)
- [Quick start](https://docs.typesafe.ai/introduction/quickstart)
- [Models and pricing](https://docs.typesafe.ai/models)
- [Confidence](https://docs.typesafe.ai/confidence)


## Run and reproduce

```bash
# Reproduce analysis from checked-in response evidence; no API key/network needed.
python3 experiments/jev/evaluate.py
python3 -m unittest discover -s experiments/jev/tests -v

# The client loads TYPESAFE_API_KEY from environment or the ignored root .env.
# Cached exact payloads are reused; only missing responses cause paid API calls.
python3 experiments/jev/run.py --limit 23
python3 experiments/jev/run.py --requests experiments/jev/control_requests.jsonl --limit 12
python3 -m hospital_4 --check
```

The 23-case pre_response_reference.json was saved before the first live response;
control_reference.json was saved before control responses. They contain
Codex-assisted semantic reference judgments, not independent human annotations.
All ten ambiguous strings lack a discriminator; thirteen unsupported strings
were marked NONE_OF_CATALOGUE after catalogue inspection. Model refusal versus
catalogue rejection is reported separately, so a conservative refusal is not
misrepresented as an accepted wrong match. The clear control set intentionally
contains both members of several ambiguous pairs. Results on these controls are
not a population-accuracy estimate.

Eight observed response distributions sum to 0.99 rather than 1.00, apparently
from displayed probability rounding. Original values are retained; the schema
check tolerates 0.01 plus floating-point epsilon and rejects larger discrepancies.
No probability normalization or confidence calibration was performed. Preparation
summary records the offline stage; results.json records the subsequent live run.
