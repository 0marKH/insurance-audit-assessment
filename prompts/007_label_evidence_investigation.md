# Prompt 007 - Investigate labelled evidence before any policy changes

User request, 17 September 2026:

> Ok let's ditch that for now, after inspecting the Hospital 1 labeled results as source of truth here is the what is next for you:
>
> Before changing the engine’s uncertainty policies, investigate the following findings from Hospital 1’s labelled data. Treat them as evidence to verify, not blanket authorization to transfer Hospital 1 rules to Hospital 4.
>
> 1. Exact exclusion boundaries are included in labelled examples
>
> INV-H1-000847: Excluded line H1-L00847-17 and trigger H1-L00830-09 belong to the same patient and occur exactly 7 days apart, across invoices. Billed total: 3,988,200 cents. Labelled expected total: 3,960,600 cents. Difference: 27,600 cents, exactly the excluded line’s charge.
>
> INV-H1-000211: Excluded line H1-L00211-08 and trigger H1-L00211-04 occur exactly 10 days apart for the same patient. Billed total: 1,567,925 cents. Labelled expected total: 1,471,325 cents. Difference: 96,600 cents, exactly the excluded line’s charge.
>
> These support inclusive ≤ N boundaries in Hospital 1. Compare Hospital 4’s wording and present the implications of adopting the same interpretation.
>
> 2. Wrong units do not always change expected amounts
>
> These invoices are labelled erroneous only for wrong_unit_basis: INV-H1-000657: Billed and expected totals both 4,217,639 cents. INV-H1-000717: Billed and expected totals both 2,651,162 cents.
>
> This suggests that some injected errors change the unit label without changing the underlying quantity or money.
>
> Investigate all 11 Hospital 1 invoices with wrong-unit labels. Determine when the evidence supports retaining the quantity and when conversion remains genuinely unknown. Do not assume every unit mismatch is merely a typo.
>
> Hospital 4’s “per hour, per item” ambiguity has no directly equivalent Hospital 1 example identified so far.
>
> 3. A labelled duplicate example removes the later charge
>
> INV-H1-000231, line H1-L00231-07, repeats the service/patient/date of line H1-L00079-05 on INV-H1-000079. Both charges are 134,725 cents. Invoice 000231’s billed total is 1,991,725 cents; its expected total is 1,857,000 cents. The difference removes exactly the repeated charge.
>
> Inspect all four invoices labelled with cross-invoice duplicates before proposing a general retention policy. This example alone does not establish how conflicting quantities or rates should be handled.
>
> 4. Volume-discount evidence requires contract-specific interpretation
>
> Hospital 1 has eight invoices labelled with volume-discount errors. Its contract explicitly defines utilisation across all patients over the whole contract term.
>
> Use those examples to verify calculation behavior. Separately compare Hospital 4’s clauses: Hospital 1 labels do not automatically establish Hospital 4’s missing population or reset scope.
>
> 5. The cap discrepancy remains unexplained
>
> INV-H1-000015, line H1-L00015-11: Nine tests billed at 14,775 cents each. Contractual cap: four tests. Billed invoice total: 1,284,475 cents. Labelled expected total: 1,195,825 cents. Difference: 88,650 cents, equivalent to six tests. Our four-test cap correction produces 1,210,600 cents, exceeding the label by one test’s price.
>
> Investigate whether other same-patient/day records explain this. Do not silently change the cap to three or claim the label is wrong without supporting evidence.
>
> Requested output before policy changes
>
> Provide a short evidence table covering: verified labelled examples; what each example establishes; remaining alternative explanations; whether the finding transfers to Hospital 4; proposed changes and their effect on coverage.
>
> Preserve the frozen baseline. Any further Hospital 1 analysis uses already-exposed labels and must be described as development analysis, not fresh held-out validation.
>
> Do not change interpretations yet; bring the findings back for my decision.
