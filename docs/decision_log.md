# Assessment decision log

Final decisions, 17 September 2026. Requests and approved clarifications are
preserved in prompts/. Historical development records remain in Git history.

## Scope and preservation

I chose a deterministic engine, supplied its architecture and rule format, and approved
the policies. I approved H4 after Codex recommended it, then expanded to H2/3/5.
All 49,796 target lines were processed; 1,757/3,942 unique invoices are submitted.
Abstentions remain explicit. Original data and H1 code/evaluation remain hash-protected. Prior H4 snapshots
remain in Git history; current audit results are reproducible.

## Contract interpretation

H2: I approved recorded service date for the 07:00 Service Day because timestamps
are missing. Discount scope is expressly all patients/whole
term. Same-patient, bidirectional exclusions are explicit; exact endpoints remain
unresolved. Episode definition does not introduce an identified price adjustment.
Actual submission timing and waivers are unavailable; screen the 60-day clause
without fabricating a submission date or zero reimbursement.

H3: amendment overrides Appendix B by service date from 2025-01-01; seven changed
rates and two newly eligible services. New services before that date are expressly
nonbillable. Other rules remain unchanged. Settlement history is unavailable.

H4: I approved inclusive exclusion endpoints and earliest eligible lexical
retention of exact copies, including multi-unit copies. Conflicts stay unresolved.
Caps are confirmed violations with assumption-dependent corrected amounts; retain
the three otherwise-eligible cap estimates. Cumulative population/reset remains
unresolved: accept only invariant rates under documented bounds. H1 analogies
support approved interpretations, not H4 validation.

H5: I approved invoice-header facility for line context despite the contract's
line-level wording. Apply service-specific facility then plan
multipliers, rounding after each step. Whole-term/all-patient usage is explicit;
“subsequent units” is interpreted as excluding the current line.

H2/3/5: do not transfer H1/H4 cap correction or duplicate allocation conventions.
Withhold affected amounts. H3/H5 positive exclusion cases remain uncertain because
scope/direction/endpoints are not explicit; same-patient candidate searching is a
documented limitation. H2 repeats are uncertain identities, not a confirmed
contractual duplicate offence absent an identified prohibition.

## Evidence, money and confidence

Match descriptions only using reviewed aliases; never choose a service or quantity
from prices. Wrong units and “per hour, per item” remain unresolved. Propagate
uncertain candidate membership and quantities. Separate original billed history,
delivered context and payable quantities. Invalid dates/IDs are reviewed; originals
never change. Integer cents and rational arithmetic round after each rate step.

Confidence retains the existing exposed-H1 class heuristic: 0.90 × Wilson lower
bound of joint flag/amount correctness, yielding 0.892297 correct and 0.581503
erroneous. The transfer factor is heuristic; no H2–5 or cap-specific calibration,
new penalty, or validated probability is claimed. H1 label reuse is development
analysis. No runtime model or experimental mapping is used.

## AI assistance and check provenance

Codex inspected the contracts, built extraction, matching, engines, tests, evaluation
and submission tooling, and drafted documentation. Codex performed the source-based
manual calculation checks and scripted replay; these were not independent human
adjudication. I initiated and later stopped the TypeSafe Jev experiment. Its 35-case
trial accepted no new mappings and changed no audit decisions. Working files were
removed during cleanup; prompt 006 and Git history retain disclosure and evidence.
