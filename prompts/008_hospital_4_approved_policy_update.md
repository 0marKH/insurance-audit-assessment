# Hospital 4 approved policy update

User prompt, preserved verbatim (Markdown formatting normalized), 2026-09-17.

Update the Hospital 4 policies, audit outputs, submission, and write-up using the decisions below. Preserve the current baseline and original assessment data.

### Approved decisions

1. **Inclusive exclusion endpoints**
   Adopt `≤ N` for Hospital 4 exclusion windows. Preserve same-patient matching across invoices, both temporal directions, and exclusion of only the first-column service. Document this as an approved interpretation supported by similar Hospital 1 wording and labelled examples—not direct Hospital 4 validation.
2. **Exact-copy duplicate retention**
   Retain the earliest eligible occurrence by ascending lexical line ID when copies represent the same service, patient, service date, quantity, billing unit, and charge. Apply this convention to identical multi-unit copies too. Reject the other copies’ payable charges without deleting original records. Conflicting quantities, rates, or eligibility remain unresolved; do not extend this into Hospital 1’s broader price-aware retention policy.
3. **Keep cap calculations as uncertain corrections**
   Continue using the contractual cap to calculate payable quantities. Keep otherwise-eligible cap-corrected submission rows, but explicitly record that these are assumption-dependent estimates—not established actual delivered quantities. Hospital 1 labels imply below-cap quantities in all four investigated cap cases, and the explanation remains unproven.

   Keep certainty that a cap violation occurred separate from certainty in its corrected amount. Ensure this distinction is reflected in supporting evidence, the confidence method, and the write-up. Do not invent a confidence penalty or claim these estimates are calibrated.
4. **Retain uncertainty about volume-discount scope**
   Do **not** assume all-patient, whole-term aggregation for Hospital 4. Sections 8.3–8.5 establish thresholds, prior-line eligibility, and ordering, but do not explicitly establish population or reset scope.

   Preserve uncertainty whenever plausible scopes produce different rates. Accept an invariant result only when its bounds and assumptions are justified. Do not treat uncertain prior records as absent.
5. **Wrong-unit cases require individual evidence**
   Retain a billed quantity only where case-specific evidence supports it. Hospital 1’s wrong-unit labels do not authorize treating every mismatch as a harmless unit-label error. Do not infer actual quantities from billed prices. Hospital 4’s “per hour, per item” ambiguity remains unresolved unless additional evidence establishes its meaning.

### Implementation and verification

- Save this prompt and update the decision log, machine-readable policies, and relevant documentation.
- Recalculate affected invoices and dependencies using the existing engine.
- Verify whether the inclusive endpoint decision resolves invoice **000235**, and whether exact-copy retention resolves **000018, 000069, and 000084**. These were conditional candidates, not guaranteed additions.
- Add focused tests for inclusive endpoints, identical multi-unit duplicates, conflicting duplicates, and cap-amount uncertainty.
- Preserve the existing Hospital 1 baseline and evaluation. Further label analysis must be described as development analysis using already-exposed labels.
- Validate the regenerated submission against the template, source amounts, identifiers, and reproducibility checks.
- Report a before/after comparison: rows added or removed, changed expected totals or confidence values, remaining omissions, and the evidence for each change.
- Update the two-page write-up to distinguish confirmed violations, uncertain corrected amounts, and unresolved contract scope.

This request does not authorize forcing Jev matches or changing matching acceptance thresholds. Preserve Jev’s experimental status unless separately approved.

Proceed with these approved decisions. Bring back any new interpretation requiring my judgment rather than silently choosing it.
