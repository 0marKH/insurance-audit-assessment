# Prompt 002 — resolve implementation decisions

Date: 14 September 2026. Authority: user instructions in this task.

## User prompt

for the Open decisions:

1- it's this `≤ N`.

2- Exclusion windows are checked for the same patient across all invoices, in both date directions, here is important details: **Check both directions:** the triggering service can happen before or after the excluded service. **The exclusion is directional between services:** it excludes the first service’s charge, not automatically both. **Search across invoices**, because related services might be billed separately. **Record ambiguities:** Section 10 does not explicitly specify the patient scope or whether the exact boundary—precisely seven days apart—is included. Same-patient matching and an inclusive boundary are reasonable interpretations, but should be documented as assumptions. An excluded charge should not be reimbursed under that rule; it isn’t simply given a discount.

3- Use ascending lexical (text) sorting for line IDs. The observed IDs contain fixed-width, zero-padded numeric components, so lexical and natural sorting agree. Validate this format across the dataset; revisit only if exceptions appear.

4- Cumulative utilisation includes all prior billed quantities for the service, without subtracting duplicate or disallowed units. The contract defines utilisation by billed units and does not specify an adjustment for rejected charges.

5-Original invoice lines and billed amounts will remain unchanged. Violations will be flagged, and corrections will affect only the calculated expected payable amounts.

- **Daily caps:** Retain earlier eligible units and exclude the latest excess units. Within each patient–service–day group, use ascending line ID as the allocation order. If a line partly exceeds the cap, reduce its payable quantity rather than excluding the whole line.
- **Duplicates:** Retain one payable occurrence. Prefer an occurrence that complies with the applicable contract pricing rules. If multiple occurrences comply, retain the earliest by ascending line ID. If none comply but the service remains payable, retain the earliest and correct its price. Assign zero expected payable amount to excluded duplicates.
- **Pricing:** Assess compliance against the applicable adjusted contract rate, including relevant bundles, premiums, and discounts.
- **Uncertainty:** If differing quantities or other conflicting evidence prevent a defensible correction, flag the ambiguity for review rather than force an allocation.

**Rationale:** The contract establishes caps and duplicate-billing violations but does not specify correction allocation. These are reproducible implementation conventions, not explicit contractual requirements.

## Development disclosure

Codex encoded these choices in a separate versioned policy, linked them to the
extracted rules without modifying contract evidence, and validated identifiers
in every hospital's CSV and JSONL files. No calculation engine or corrected
invoice output is implemented by this change. No runtime AI is used.
