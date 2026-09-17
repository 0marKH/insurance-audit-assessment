# Jev pilot results - 17 September 2026

**The API integration works, but this pilot produced no defensible new exact
service matches.** Jev matched the clear controls and proposed specific services
for some genuinely under-specified inputs. We have not changed the audit engine,
source data, policies, confidence scores or submission.

## Experiment

Model: **jev-1.13.0**, pinned instead of the moving latest alias. One Choice per
state; 98 exact H4 catalogue services plus NONE_OF_CATALOGUE and
INSUFFICIENT_INFORMATION. State contains the description and reviewed abbreviation
glossary. Prices, quantities, billed units, labels, patient/invoice IDs and baseline
predictions were not supplied. Each distinct description was called once and cached.

23 unresolved descriptions represent 194 line records. Twelve additional clear
positive controls test that the model can distinguish fully stated services,
including both alternatives in several ambiguous pairs. References were recorded
before the respective responses, using Codex-assisted contract review. They are
not independently adjudicated ground truth. This is an exploratory pilot, with
no new H1 holdout, tuned threshold or hidden-label H4 accuracy measurement.

| Cohort | Distinct descriptions | Model outcome | Interpretation |
|---|---:|---|---|
| Clear controls | 12 | 12 correct catalogue selections | All agreed with pre-response review; intentionally easy controls, not an unbiased accuracy estimate. |
| Missing service qualifier | 10 | 3 abstentions; 7 specific selections | The seven selections cannot be justified by the supplied description alone. |
| Unsupported catalogue combination | 13 | 13 abstentions; 0 NONE_OF_CATALOGUE | Conservative responses, but no usable catalogue-exclusion evidence to narrow propagation. |

Across unresolved inputs, 16 descriptions (74 line records) received
INSUFFICIENT_INFORMATION. Seven descriptions (120 line records) received a specific
service proposal. There were **zero accepted new mappings** and no claimed invoice
coverage gain. The seven proposals are not established ground-truth errors: the
underlying delivered service is unknown. They are unsupported disambiguations.

## Specific proposals that remain under review

| Description (decorative suffix omitted) | Jev selected | Missing discriminator | Returned confidence |
|---|---|---|---:|
| CONF ger CS | Intensive Geriatric Case Conference | Intensive vs Postoperative | 0.64 |
| OBS - gi NURS | Supervised Gastrointestinal Nursing Observation | Elective vs Supervised | 0.36 |
| RHEUM rehabilitation PROGRAMME | Ambulatory Rheumatologic Rehabilitation Programme | Ambulatory vs Emergency | 0.47 |
| card - HOME vst | Routine Cardiac Home Visit | Bedside vs Routine | 0.44 |
| card VENT support | Specialist Cardiac Ventilation Support | Assisted vs Specialist | 0.44 |
| hep - DISCHARGE plng | Specialist Hepatic Discharge Planning | Extended vs Specialist | 0.68 |
| occupancy ONC wd BD | Standard Oncology Ward Bed Occupancy | Advanced vs Standard | 0.73 |

The model can distinguish clear variants: the controls containing "INTENS" and
"POSTOP" selected their respective Geriatric Case Conference services at 0.99.
The qualifier is absent from the unresolved description; a different classifier
cannot establish it from the same words. A model confidence value expresses its
own distribution, not contractual evidence or validated invoice confidence.

## Operational observations

35 successful responses; **131,118 input tokens** and **35,856 output tokens**.
Mean recorded request latency **1.27 seconds**, range **1.06-2.83 seconds**.
At the documented $0.042 per million input tokens with free output tokens, the
estimated token charge is **$0.005506956** (about half a US cent). This is not a
verified account invoice. No SDK or runtime package dependency was added.

Eight full distributions sum to 0.99, apparently because of probability rounding.
Values are preserved and the validation tolerance is documented. Request bodies,
model/version, response distributions, token usage, timestamps and latency are
retained locally. The API key is read from the ignored .env and never logged.

## Recommendation

Keep Jev as an experimental classification component; this small trial does not
justify replacing the matcher or changing submission rows. First separate missing
information from recoverable language variation. Use legitimate additional service
evidence, if available, to distinguish emergency/outpatient and other qualifiers;
do not use price fit as a shortcut. A follow-up atomic matchability question could
test unique match vs ambiguous vs outside catalogue before attempting a specific
choice. Treat that as a new prompt experiment, not independent validation of this
one. Review targets independently before selecting an acceptance threshold.

For uncertainty propagation, review the thirteen unsupported descriptions and
whether they can safely be ruled out as context for particular contracted services.
Rejecting a catalogue match does not by itself establish zero payable amount.
Contractual dual units, discount scope, duplicate allocation and exclusion
endpoints remain policy/evidence questions. Another ML classifier should be
compared on the same reviewed, recoverable cases, not rewarded simply for guessing
more missing qualifiers. Cached pilot outputs support that later comparison.

## Reproduction and evidence

Run `python3 experiments/jev/evaluate.py` to regenerate results.json/results.csv
from the 35 cached responses. Run `python3 -m hospital_4 --check` to verify the
unchanged H4 outputs and submission. The client test covers invalid response
options, values, model versions, ordering and probability mass. Raw live outputs
are evidence, not deterministic future model guarantees.

Official references: [API](https://docs.typesafe.ai/api),
[Choice](https://docs.typesafe.ai/primitives/choice),
[Confidence](https://docs.typesafe.ai/confidence),
[Models and pricing](https://docs.typesafe.ai/models).
