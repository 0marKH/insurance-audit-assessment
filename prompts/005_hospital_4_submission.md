# Prompt 005 - Select and complete one unlabelled hospital

User request, 17 September 2026. Codex assisted contract inspection, implementation,
tests, confidence proposal and documentation. There is no runtime model dependency.
This prompt does not replace Hospital 1's frozen prompts or policies.

> Preserve the current Hospital 1 implementation and evaluation.
>
> First, briefly inspect Contracts 2–5 and recommend the hospital requiring the fewest new rule types and unresolved assumptions. Explain the choice before implementation.
>
> Then, within the remaining assessment time:
>
> 1. Extract and review that hospital’s contract, keeping its rules and policies separate from Hospital 1.
> 2. Reuse the existing engine where applicable. Do not assume Hospital 1’s definitions or correction conventions apply unchanged.
> 3. Audit the selected hospital and manually inspect representative calculations and uncertain cases.
> 4. Propose and document a numerical confidence method informed by Hospital 1’s evaluation. Do not claim it is validated on the unlabelled hospital.
> 5. Generate `submission.csv` with the exact template columns. Include defensible correct and erroneous predictions; omit cases without a defensible submission row and report that coverage.
> 6. Validate identifiers, billed amounts, integer-cent totals, confidence values, and reproducibility.
> 7. Prepare the two-page write-up and update the decision log, README, and saved prompts.
>
> Prioritize one hospital completed carefully over broad, incomplete coverage. Do not tune against the already-exposed Hospital 1 holdout while presenting it as fresh evaluation.
