# Hospital 1 — extracted contract rules

**Northgate Regional Medical Centre** · INS-H1-2024-0417

Term: 2024-01-01 through 2025-12-31. Currency: GBP. All amounts below are integer cents.

Status: **extracted_with_assumptions**. Full contract ready for engine: **true**.

174 rules. 206/206 nonempty source lines recognized. This is parser coverage, not measured semantic accuracy or invoice-audit performance.

The extractor uses reviewed Hospital 1 prose templates and typed table parsing. It makes no AI or network calls. Rule interpretations are development-time readings of the cited text.

## Rule inventory

| Kind | Count |
|---|---:|
| adjustment order | 1 |
| bundle | 3 |
| bundle grouping | 1 |
| contract number restriction | 1 |
| contract scope | 1 |
| contract term | 1 |
| cumulative counting | 1 |
| daily quantity cap | 7 |
| definition | 3 |
| discount boundary | 1 |
| discount grouping | 1 |
| duplicate billing | 1 |
| exclusion direction | 1 |
| exclusion window | 6 |
| facility scope | 1 |
| invoice calculation | 1 |
| invoice identifier presence | 1 |
| invoice identifier restriction | 1 |
| line calculation | 1 |
| line ordering | 1 |
| plan scope | 1 |
| premium grouping | 1 |
| rounding | 1 |
| service catalogue | 108 |
| threshold premium | 9 |
| valid service dates | 1 |
| volume discount | 11 |
| weekend uplift | 7 |

## Questions to resolve before the engine

No unresolved policy decisions. Contract ambiguities remain documented below with the user-approved assumptions. Case-specific conflicting evidence must still be flagged for review.

## Implementation conventions

Policy: policies/hospital_1.json. Authority: User-approved implementation conventions, not additional contract clauses. User decision source: prompts/002_open_decisions.md.

- **exclusions:** Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.
- **line ordering:** Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.
- **cumulative usage:** Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.
- **corrections:** Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions.
- **engine:** Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

Original invoice lines and billed amounts remain immutable. Corrections affect calculated expected payables only; no invoice calculations have been performed in this milestone.

## All rules

Each entry follows Applies to → Condition → Action → Scope → Order → Source → Uncertainty.

### H1-C1-1-1 · contract term

**Applies to:** entity: service_lines

**Condition:** always: yes

**Action:** type: define_term; start source: preamble.Effective from; end source: preamble.Effective to; endpoints: inclusive

**Scope:** hospital id: hospital_1; group by: contract_number

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §1.1 · line 17: 1.1 The Agreement takes effect on 1 January 2024 and expires on 31 December 2025.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.3 · line 244: 11.3 Every Service Date must fall within the term stated in Section 1.1 and may not fall after the invoice date.

**Uncertainty:** interpretation. Treat the named effective and expiry dates as included calendar dates. This is the recorded reading of the term wording.

### H1-C1-2-1 · facility scope

**Applies to:** entity: service_lines

**Condition:** always: yes

**Action:** type: set_facility_multiplier; facility name: Main Campus; facility code: F-MAIN; multiplier: numerator: 1; denominator: 1

**Scope:** hospital id: hospital_1; group by: contract_number

**Order:** stage: facility_multiplier; after: none; position: 2

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §1.2 · line 19: 1.2 Services are delivered from a single facility, Main Campus (F-MAIN). No facility differential applies.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. A single facility is named and no facility differential applies.

### H1-C1-3-1 · plan scope

**Applies to:** entity: service_lines

**Condition:** plan tier: BRONZE, SILVER, GOLD

**Action:** type: set_plan_tier_multiplier; multiplier: numerator: 1; denominator: 1

**Scope:** hospital id: hospital_1; group by: contract_number

**Order:** stage: plan_tier_multiplier; after: none; position: 3

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §1.3 · line 21: 1.3 All patient plan tiers (BRONZE, SILVER, GOLD) are reimbursed at the same rate under this Agreement.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. All three named plan tiers use the same rate.

### H1-C2-1-1 · definition

**Applies to:** entity: service_date

**Condition:** always: yes

**Action:** type: define_service_day; value: calendar_day_of_line_service_date

**Scope:** hospital id: hospital_1; group by: line_id

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** explicit. Use the line service date as the service day, not the invoice date.

### H1-C2-2-1 · definition

**Applies to:** entity: service_date

**Condition:** always: yes

**Action:** type: define_business_day; excluded weekdays: Saturday, Sunday; public holidays excluded: no

**Scope:** hospital id: hospital_1; group by: service_date

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** explicit. Only Saturdays and Sundays are excluded; public holidays are not an additional exclusion.

### H1-C2-3-1 · definition

**Applies to:** entity: service_units

**Condition:** always: yes

**Action:** type: define_billable_unit; unit basis source: Section 4

**Scope:** hospital id: hospital_1; group by: service

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Billable units follow the service catalogue, even when the service name suggests a different unit.

### H1-C2-4-1 · cumulative counting

**Applies to:** entity: service_lines

**Condition:** always: yes

**Action:** type: define_cumulative_utilisation; quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The contract does not say whether to remove invalid or duplicate billed units from later cumulative totals.

### H1-C3-1-1 · rounding

**Applies to:** entity: monetary_calculations

**Condition:** fractional cent result: yes

**Action:** type: round; unit: whole_cent; mode: half_up; exact halves: away_from_zero; timing: after_each_individual_step

**Scope:** hospital id: hospital_1; group by: calculation_step

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.

**Uncertainty:** explicit. Use integer cents and exact arithmetic; round each step, with positive and negative halves away from zero.

### H1-C3-2-1 · adjustment order

**Applies to:** entity: service_lines

**Condition:** always: yes

**Action:** type: ordered_pipeline; stages: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift, cumulative_volume_discount, quantity_multiplication, invoice_summation; rate target: unit_rate

**Scope:** hospital id: hospital_1; group by: line_id

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.3 · line 39: 3.3 The line total for a line item is the effective unit rate multiplied by the billed quantity. The invoice total is the sum of the line totals on that invoice.

**Uncertainty:** explicit. Substitute a bundled rate, apply facility then plan multipliers, premiums/uplifts, then the volume discount; multiply quantity and sum the invoice afterwards.

### H1-C3-3-1 · line calculation

**Applies to:** entity: service_lines

**Condition:** always: yes

**Action:** type: multiply; operands: effective_unit_rate_cents, billed_quantity; result: line_total_cents

**Scope:** hospital id: hospital_1; group by: line_id

**Order:** stage: quantity_multiplication; after: none; position: 6

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.3 · line 39: 3.3 The line total for a line item is the effective unit rate multiplied by the billed quantity. The invoice total is the sum of the line totals on that invoice.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. The final effective unit rate is multiplied by billed quantity.

### H1-C3-3-2 · invoice calculation

**Applies to:** entity: invoices

**Condition:** always: yes

**Action:** type: sum; operand: line_total_cents; result: invoice_total_cents

**Scope:** hospital id: hospital_1; group by: invoice_id

**Order:** stage: invoice_summation; after: none; position: 7

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.3 · line 39: 3.3 The line total for a line item is the effective unit rate multiplied by the billed quantity. The invoice total is the sum of the line totals on that invoice.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.

**Uncertainty:** explicit. The invoice total equals the sum of its line totals.

### H1-C5-1-1 · premium grouping

**Applies to:** entity: threshold_premium_services

**Condition:** always: yes

**Action:** type: aggregate_quantity; metric: delivered_daily_quantity_excluding_duplicates

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.4 · line 246: 11.4 The same Service may not be billed twice for the same Patient and the same Service Date, whether on one invoice or across several.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-C7-1-1 · discount grouping

**Applies to:** entity: volume_discount_services

**Condition:** always: yes

**Action:** type: aggregate_quantity; metric: prior_cumulative_billed_units; quantity: original_billed_quantity; exclude current line: yes; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no; identifier comparison: lexical; sort by: service_date ASC, line_id ASC

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

### H1-C7-2-1 · discount boundary

**Applies to:** entity: volume_discount_services

**Condition:** operator: >; metric: prior_cumulative_billed_units; exclude current line: yes

**Action:** type: choose_discount; selection: deepest_qualifying_discount; stack tiers: no; split current line: no

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: cumulative_volume_discount; after: none; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. At exactly the threshold, the discount is not due. A line that crosses it retains the rate based on prior usage; use the deepest eligible tier.

### H1-C7-2-2 · line ordering

**Applies to:** entity: service_lines

**Condition:** same service date: yes

**Action:** type: sort; keys: service_date ASC, line_id ASC; identifier comparison: lexical

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: Choose and document lexical or natural/numeric ordering before implementing the engine.

### H1-C9-1-1 · bundle grouping

**Applies to:** entity: bundled_services

**Condition:** both services present: yes; same patient: yes; same service day: yes

**Action:** type: substitute_both_unit_rates; rates source: Section 9

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date; across invoices: yes

**Order:** stage: bundle_substitution; after: none; position: 1

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9.1 · line 223: 9.1 The bundled rates in this Section replace the standalone rates in Section 4 whenever both Services in a pair are delivered to the same Patient on the same Service Day. They are substituted before any multiplier, premium or discount is applied.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Bundle eligibility depends on the patient/day and service pair, with no same-invoice condition.

### H1-C10-1-1 · exclusion direction

**Applies to:** entity: excluded_services

**Condition:** related service present: yes; operator: <=; same patient: yes

**Action:** type: measure_window; distance: absolute_calendar_day_difference; direction: both

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

### H1-C11-1-1 · contract number restriction

**Applies to:** entity: invoices

**Condition:** metric: invoice.contract_number; operator: !=; expected source: preamble.Contract number

**Action:** type: flag_contract_number_mismatch

**Scope:** hospital id: hospital_1; group by: invoice_id

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.1 · line 240: 11.1 Each invoice shall quote the contract number stated above.

**Uncertainty:** explicit. Every invoice must quote this agreement number.

### H1-C11-2-1 · invoice identifier restriction

**Applies to:** entity: invoices

**Condition:** metric: invoice_id_occurrences; operator: >; value: 1

**Action:** type: flag_reused_invoice_identifier

**Scope:** hospital id: hospital_1; group by: invoice_id

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.2 · line 242: 11.2 Each invoice shall carry a unique invoice identifier. An identifier may not be reused.

**Uncertainty:** explicit. Invoice identifiers may not be reused across invoice records; repeated invoice_id values in the line-item file are not invoice reuse.

### H1-C11-2-2 · invoice identifier presence

**Applies to:** entity: invoices

**Condition:** metric: invoice_id; operator: missing

**Action:** type: flag_missing_invoice_identifier

**Scope:** hospital id: hospital_1; group by: invoice_record

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.2 · line 242: 11.2 Each invoice shall carry a unique invoice identifier. An identifier may not be reused.

**Uncertainty:** explicit. Each invoice must carry an identifier.

### H1-C11-3-1 · valid service dates

**Applies to:** entity: service_lines

**Condition:** any: metric: service_date; operator: <; reference: contract.effective_from, metric: service_date; operator: >; reference: contract.effective_to, metric: service_date; operator: >; reference: invoice.invoice_date

**Action:** type: flag_invalid_service_date

**Scope:** hospital id: hospital_1; group by: line_id

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.3 · line 244: 11.3 Every Service Date must fall within the term stated in Section 1.1 and may not fall after the invoice date.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §1.1 · line 17: 1.1 The Agreement takes effect on 1 January 2024 and expires on 31 December 2025.

**Uncertainty:** interpretation. Service dates must be within the term and no later than the invoice date; the invoice date itself is not required to be within the term. Treat the named term endpoints as inclusive.

### H1-C11-4-1 · duplicate billing

**Applies to:** entity: service_lines

**Condition:** metric: matching_line_count; operator: >; value: 1

**Action:** type: flag_duplicate_service_billing; correction policy: group by: contract_number, patient_id, service, service_date; retain payable occurrences: 1; selection priority: eligible_occurrence_compliant_with_applicable_adjusted_contract_rate, earliest_line_id_lexical_among_compliant_occurrences, if_none_comply_and_service_remains_payable_retain_earliest_line_id_lexical_and_correct_price; excluded duplicate expected payable cents: 0; nonpayable service must not be reinstated: yes; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §11.4 · line 246: 11.4 The same Service may not be billed twice for the same Patient and the same Service Date, whether on one invoice or across several.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: Which line should be retained and what corrected invoice totals should be used when duplicates exist? The contract does not provide a retention policy.

### H1-SCOPE · contract scope

**Applies to:** entity: contract

**Condition:** always: yes

**Action:** type: set_contract_scope; values: hospital id: hospital_1; contract number: INS-H1-2024-0417; provider: Northgate Regional Medical Centre; payer: Meridian Health Assurance Group; currency: GBP; effective from: 2024-01-01; effective to: 2025-12-31

**Scope:** hospital id: hospital_1; group by: contract_number

**Order:** stage: unspecified; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 5: **Contract number:** INS-H1-2024-0417
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 6: **Provider:** Northgate Regional Medical Centre
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 7: **Payer:** Meridian Health Assurance Group
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 8: **Effective from:** 1 January 2024
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 9: **Effective to:** 31 December 2025
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 10: **Currency:** GBP
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §preamble · line 11: **Rounding convention:** half_up_cent
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §1.1 · line 17: 1.1 The Agreement takes effect on 1 January 2024 and expires on 31 December 2025.

**Uncertainty:** explicit. Hospital identity, term and currency are recorded verbatim; ISO dates are normalized.

### H1-T4-001 · service catalogue

**Applies to:** services: Advanced Cardiac Recovery Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Cardiac Recovery Room Occupancy; unit basis: per hour; base rate cents: 20000; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 47: | Advanced Cardiac Recovery Room Occupancy | per hour | GBP 200.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-002 · service catalogue

**Applies to:** services: Advanced Haematology Physiotherapy Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Haematology Physiotherapy Session; unit basis: per hour; base rate cents: 10150; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 48: | Advanced Haematology Physiotherapy Session | per hour | GBP 101.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-003 · service catalogue

**Applies to:** services: Advanced Infectious Critical Care Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Infectious Critical Care Occupancy; unit basis: per day of service; base rate cents: 70925; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 49: | Advanced Infectious Critical Care Occupancy | per day of service | GBP 709.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-004 · service catalogue

**Applies to:** services: Advanced Metabolic Anaesthesia Administration

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Metabolic Anaesthesia Administration; unit basis: per hour; base rate cents: 9200; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 50: | Advanced Metabolic Anaesthesia Administration | per hour | GBP 92.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-005 · service catalogue

**Applies to:** services: Advanced Metabolic Nursing Observation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Metabolic Nursing Observation; unit basis: per day of service; base rate cents: 130125; currency: GBP; daily cap: value: 6; unit: days

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 51: | Advanced Metabolic Nursing Observation | per day of service | GBP 1,301.25 | 6 days |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-006 · service catalogue

**Applies to:** services: Advanced Neurological Consultation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Neurological Consultation; unit basis: per visit; base rate cents: 14125; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 52: | Advanced Neurological Consultation | per visit | GBP 141.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-007 · service catalogue

**Applies to:** services: Advanced Rheumatologic Laboratory Panel

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Advanced Rheumatologic Laboratory Panel; unit basis: per test; base rate cents: 14775; currency: GBP; daily cap: value: 4; unit: tests

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 53: | Advanced Rheumatologic Laboratory Panel | per test | GBP 147.75 | 4 tests |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-008 · service catalogue

**Applies to:** services: Ambulatory Cardiac Home Visit

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Cardiac Home Visit; unit basis: per visit; base rate cents: 28425; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 54: | Ambulatory Cardiac Home Visit | per visit | GBP 284.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-009 · service catalogue

**Applies to:** services: Ambulatory Immunologic Endoscopic Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Immunologic Endoscopic Procedure; unit basis: per procedure; base rate cents: 607900; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 55: | Ambulatory Immunologic Endoscopic Procedure | per procedure | GBP 6,079.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-010 · service catalogue

**Applies to:** services: Ambulatory Immunologic Ward Bed Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Immunologic Ward Bed Occupancy; unit basis: per day of service; base rate cents: 87250; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 56: | Ambulatory Immunologic Ward Bed Occupancy | per day of service | GBP 872.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-011 · service catalogue

**Applies to:** services: Ambulatory Infectious Home Visit

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Infectious Home Visit; unit basis: per visit; base rate cents: 8225; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 57: | Ambulatory Infectious Home Visit | per visit | GBP 82.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-012 · service catalogue

**Applies to:** services: Ambulatory Musculoskeletal Ward Bed Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Musculoskeletal Ward Bed Occupancy; unit basis: per night of occupancy; base rate cents: 154575; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 58: | Ambulatory Musculoskeletal Ward Bed Occupancy | per night of occupancy | GBP 1,545.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-013 · service catalogue

**Applies to:** services: Ambulatory Ophthalmic Case Conference

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Ophthalmic Case Conference; unit basis: per visit; base rate cents: 16925; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 59: | Ambulatory Ophthalmic Case Conference | per visit | GBP 169.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-014 · service catalogue

**Applies to:** services: Ambulatory Ophthalmic Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Ophthalmic Dialysis Session; unit basis: per procedure; base rate cents: 479825; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 60: | Ambulatory Ophthalmic Dialysis Session | per procedure | GBP 4,798.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-015 · service catalogue

**Applies to:** services: Ambulatory Psychiatric Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Psychiatric Dialysis Session; unit basis: per procedure; base rate cents: 355550; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 61: | Ambulatory Psychiatric Dialysis Session | per procedure | GBP 3,555.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-016 · service catalogue

**Applies to:** services: Ambulatory Pulmonary Recovery Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Pulmonary Recovery Room Occupancy; unit basis: per night of occupancy; base rate cents: 112825; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 62: | Ambulatory Pulmonary Recovery Room Occupancy | per night of occupancy | GBP 1,128.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-017 · service catalogue

**Applies to:** services: Ambulatory Urologic Imaging Interpretation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Ambulatory Urologic Imaging Interpretation; unit basis: per test; base rate cents: 42700; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 63: | Ambulatory Urologic Imaging Interpretation | per test | GBP 427.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-018 · service catalogue

**Applies to:** services: Assisted Gastrointestinal Infusion Therapy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Assisted Gastrointestinal Infusion Therapy; unit basis: per hour; base rate cents: 8925; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 64: | Assisted Gastrointestinal Infusion Therapy | per hour | GBP 89.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-019 · service catalogue

**Applies to:** services: Assisted Geriatric Infusion Therapy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Assisted Geriatric Infusion Therapy; unit basis: per unit dispensed; base rate cents: 7825; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 65: | Assisted Geriatric Infusion Therapy | per unit dispensed | GBP 78.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-020 · service catalogue

**Applies to:** services: Assisted Infectious Discharge Planning

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Assisted Infectious Discharge Planning; unit basis: per hour; base rate cents: 8875; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 66: | Assisted Infectious Discharge Planning | per hour | GBP 88.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-021 · service catalogue

**Applies to:** services: Assisted Pulmonary Theatre Time

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Assisted Pulmonary Theatre Time; unit basis: per hour; base rate cents: 6700; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 67: | Assisted Pulmonary Theatre Time | per hour | GBP 67.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-022 · service catalogue

**Applies to:** services: Assisted Urologic Home Visit

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Assisted Urologic Home Visit; unit basis: per visit; base rate cents: 13625; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 68: | Assisted Urologic Home Visit | per visit | GBP 136.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-023 · service catalogue

**Applies to:** services: Bedside Otolaryngologic Recovery Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Bedside Otolaryngologic Recovery Room Occupancy; unit basis: per night of occupancy; base rate cents: 150450; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 69: | Bedside Otolaryngologic Recovery Room Occupancy | per night of occupancy | GBP 1,504.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-024 · service catalogue

**Applies to:** services: Bedside Psychiatric Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Bedside Psychiatric Dialysis Session; unit basis: per visit; base rate cents: 20575; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 70: | Bedside Psychiatric Dialysis Session | per visit | GBP 205.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-025 · service catalogue

**Applies to:** services: Bedside Pulmonary Biopsy Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Bedside Pulmonary Biopsy Procedure; unit basis: per procedure; base rate cents: 316825; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 71: | Bedside Pulmonary Biopsy Procedure | per procedure | GBP 3,168.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-026 · service catalogue

**Applies to:** services: Comprehensive Infectious Nursing Observation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Comprehensive Infectious Nursing Observation; unit basis: per day of service; base rate cents: 169825; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 72: | Comprehensive Infectious Nursing Observation | per day of service | GBP 1,698.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-027 · service catalogue

**Applies to:** services: Comprehensive Oncology Nursing Observation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Comprehensive Oncology Nursing Observation; unit basis: per hour; base rate cents: 8475; currency: GBP; daily cap: value: 12; unit: hours

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 73: | Comprehensive Oncology Nursing Observation | per hour | GBP 84.75 | 12 hours |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-028 · service catalogue

**Applies to:** services: Comprehensive Otolaryngologic Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Comprehensive Otolaryngologic Rehabilitation Programme; unit basis: per visit; base rate cents: 27025; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 74: | Comprehensive Otolaryngologic Rehabilitation Programme | per visit | GBP 270.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-029 · service catalogue

**Applies to:** services: Comprehensive Otolaryngologic Theatre Time

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Comprehensive Otolaryngologic Theatre Time; unit basis: per hour; base rate cents: 32100; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 75: | Comprehensive Otolaryngologic Theatre Time | per hour | GBP 321.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-030 · service catalogue

**Applies to:** services: Comprehensive Psychiatric Transfusion Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Comprehensive Psychiatric Transfusion Service; unit basis: per procedure; base rate cents: 383650; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 76: | Comprehensive Psychiatric Transfusion Service | per procedure | GBP 3,836.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-031 · service catalogue

**Applies to:** services: Comprehensive Urologic Transport Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Comprehensive Urologic Transport Service; unit basis: per visit; base rate cents: 42750; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 77: | Comprehensive Urologic Transport Service | per visit | GBP 427.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-032 · service catalogue

**Applies to:** services: Continuous Cardiac Nursing Observation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Cardiac Nursing Observation; unit basis: per hour; base rate cents: 9875; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 78: | Continuous Cardiac Nursing Observation | per hour | GBP 98.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-033 · service catalogue

**Applies to:** services: Continuous Immunologic Theatre Time

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Immunologic Theatre Time; unit basis: per hour; base rate cents: 20975; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 79: | Continuous Immunologic Theatre Time | per hour | GBP 209.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-034 · service catalogue

**Applies to:** services: Continuous Musculoskeletal Wound Care

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Musculoskeletal Wound Care; unit basis: per day of service; base rate cents: 36800; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 80: | Continuous Musculoskeletal Wound Care | per day of service | GBP 368.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-035 · service catalogue

**Applies to:** services: Continuous Obstetric Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Obstetric Rehabilitation Programme; unit basis: per day of service; base rate cents: 112400; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 81: | Continuous Obstetric Rehabilitation Programme | per day of service | GBP 1,124.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-036 · service catalogue

**Applies to:** services: Continuous Otolaryngologic Telemetry Monitoring

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Otolaryngologic Telemetry Monitoring; unit basis: per day of service; base rate cents: 111975; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 82: | Continuous Otolaryngologic Telemetry Monitoring | per day of service | GBP 1,119.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-037 · service catalogue

**Applies to:** services: Continuous Psychiatric Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Psychiatric Rehabilitation Programme; unit basis: per visit; base rate cents: 20300; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 83: | Continuous Psychiatric Rehabilitation Programme | per visit | GBP 203.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-038 · service catalogue

**Applies to:** services: Continuous Pulmonary Wound Care

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Pulmonary Wound Care; unit basis: per day of service; base rate cents: 144900; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 84: | Continuous Pulmonary Wound Care | per day of service | GBP 1,449.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-039 · service catalogue

**Applies to:** services: Continuous Vascular Pharmaceutical Dispensing

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Continuous Vascular Pharmaceutical Dispensing; unit basis: per unit dispensed; base rate cents: 6750; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 85: | Continuous Vascular Pharmaceutical Dispensing | per unit dispensed | GBP 67.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-040 · service catalogue

**Applies to:** services: Elective Cardiac Nutritional Support

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Elective Cardiac Nutritional Support; unit basis: per day of service; base rate cents: 158625; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 86: | Elective Cardiac Nutritional Support | per day of service | GBP 1,586.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-041 · service catalogue

**Applies to:** services: Elective Pulmonary Nutritional Support

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Elective Pulmonary Nutritional Support; unit basis: per unit dispensed; base rate cents: 7450; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 87: | Elective Pulmonary Nutritional Support | per unit dispensed | GBP 74.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-042 · service catalogue

**Applies to:** services: Emergency Dermatologic Case Conference

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Emergency Dermatologic Case Conference; unit basis: per hour; base rate cents: 3775; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 88: | Emergency Dermatologic Case Conference | per hour | GBP 37.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-043 · service catalogue

**Applies to:** services: Emergency Orthopaedic Consultation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Emergency Orthopaedic Consultation; unit basis: per procedure; base rate cents: 418900; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 89: | Emergency Orthopaedic Consultation | per procedure | GBP 4,189.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-044 · service catalogue

**Applies to:** services: Emergency Orthopaedic Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Emergency Orthopaedic Rehabilitation Programme; unit basis: per visit; base rate cents: 28950; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 90: | Emergency Orthopaedic Rehabilitation Programme | per visit | GBP 289.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-045 · service catalogue

**Applies to:** services: Emergency Renal Radiotherapy Fraction

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Emergency Renal Radiotherapy Fraction; unit basis: per item supplied; base rate cents: 11000; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 91: | Emergency Renal Radiotherapy Fraction | per item supplied | GBP 110.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-046 · service catalogue

**Applies to:** services: Extended Geriatric Wound Care

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Extended Geriatric Wound Care; unit basis: per item supplied; base rate cents: 10100; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 92: | Extended Geriatric Wound Care | per item supplied | GBP 101.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-047 · service catalogue

**Applies to:** services: Extended Metabolic Isolation Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Extended Metabolic Isolation Room Occupancy; unit basis: per night of occupancy; base rate cents: 87300; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 93: | Extended Metabolic Isolation Room Occupancy | per night of occupancy | GBP 873.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-048 · service catalogue

**Applies to:** services: Extended Palliative Laboratory Panel

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Extended Palliative Laboratory Panel; unit basis: per test; base rate cents: 17850; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 94: | Extended Palliative Laboratory Panel | per test | GBP 178.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-049 · service catalogue

**Applies to:** services: Extended Renal Transport Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Extended Renal Transport Service; unit basis: per item supplied; base rate cents: 25650; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 95: | Extended Renal Transport Service | per item supplied | GBP 256.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-050 · service catalogue

**Applies to:** services: Extended Vascular Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Extended Vascular Rehabilitation Programme; unit basis: per day of service; base rate cents: 65400; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 96: | Extended Vascular Rehabilitation Programme | per day of service | GBP 654.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-051 · service catalogue

**Applies to:** services: Focused Immunologic Physiotherapy Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Focused Immunologic Physiotherapy Session; unit basis: per hour; base rate cents: 3300; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 97: | Focused Immunologic Physiotherapy Session | per hour | GBP 33.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-052 · service catalogue

**Applies to:** services: Focused Orthopaedic Transport Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Focused Orthopaedic Transport Service; unit basis: per visit; base rate cents: 42100; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 98: | Focused Orthopaedic Transport Service | per visit | GBP 421.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-053 · service catalogue

**Applies to:** services: Focused Otolaryngologic Wound Care

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Focused Otolaryngologic Wound Care; unit basis: per visit; base rate cents: 24725; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 99: | Focused Otolaryngologic Wound Care | per visit | GBP 247.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-054 · service catalogue

**Applies to:** services: Inpatient Endocrine Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Endocrine Dialysis Session; unit basis: per procedure; base rate cents: 81750; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 100: | Inpatient Endocrine Dialysis Session | per procedure | GBP 817.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-055 · service catalogue

**Applies to:** services: Inpatient Hepatic Physiotherapy Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Hepatic Physiotherapy Session; unit basis: per visit; base rate cents: 42600; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 101: | Inpatient Hepatic Physiotherapy Session | per visit | GBP 426.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-056 · service catalogue

**Applies to:** services: Inpatient Musculoskeletal Ward Bed Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Musculoskeletal Ward Bed Occupancy; unit basis: per day of service; base rate cents: 35625; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 102: | Inpatient Musculoskeletal Ward Bed Occupancy | per day of service | GBP 356.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-057 · service catalogue

**Applies to:** services: Inpatient Ophthalmic Radiotherapy Fraction

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Ophthalmic Radiotherapy Fraction; unit basis: per item supplied; base rate cents: 25300; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 103: | Inpatient Ophthalmic Radiotherapy Fraction | per item supplied | GBP 253.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-058 · service catalogue

**Applies to:** services: Inpatient Ophthalmic Transport Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Ophthalmic Transport Service; unit basis: per item supplied; base rate cents: 4800; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 104: | Inpatient Ophthalmic Transport Service | per item supplied | GBP 48.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-059 · service catalogue

**Applies to:** services: Inpatient Palliative Isolation Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Palliative Isolation Room Occupancy; unit basis: per night of occupancy; base rate cents: 179600; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 105: | Inpatient Palliative Isolation Room Occupancy | per night of occupancy | GBP 1,796.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-060 · service catalogue

**Applies to:** services: Inpatient Palliative Specimen Analysis

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Palliative Specimen Analysis; unit basis: per item supplied; base rate cents: 29725; currency: GBP; daily cap: value: 4; unit: items

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 106: | Inpatient Palliative Specimen Analysis | per item supplied | GBP 297.25 | 4 items |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-061 · service catalogue

**Applies to:** services: Inpatient Renal Radiotherapy Fraction

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Renal Radiotherapy Fraction; unit basis: per procedure; base rate cents: 455300; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 107: | Inpatient Renal Radiotherapy Fraction | per procedure | GBP 4,553.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-062 · service catalogue

**Applies to:** services: Inpatient Vascular Diagnostic Imaging

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Inpatient Vascular Diagnostic Imaging; unit basis: per item supplied; base rate cents: 12725; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 108: | Inpatient Vascular Diagnostic Imaging | per item supplied | GBP 127.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-063 · service catalogue

**Applies to:** services: Intensive Gastrointestinal Isolation Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intensive Gastrointestinal Isolation Room Occupancy; unit basis: per night of occupancy; base rate cents: 160725; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 109: | Intensive Gastrointestinal Isolation Room Occupancy | per night of occupancy | GBP 1,607.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-064 · service catalogue

**Applies to:** services: Intensive Geriatric Nutritional Support

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intensive Geriatric Nutritional Support; unit basis: per unit dispensed; base rate cents: 4275; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 110: | Intensive Geriatric Nutritional Support | per unit dispensed | GBP 42.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-065 · service catalogue

**Applies to:** services: Intensive Ophthalmic Case Conference

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intensive Ophthalmic Case Conference; unit basis: per hour; base rate cents: 21875; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 111: | Intensive Ophthalmic Case Conference | per hour | GBP 218.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-066 · service catalogue

**Applies to:** services: Intermittent Dermatologic Transfusion Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intermittent Dermatologic Transfusion Service; unit basis: per procedure; base rate cents: 243150; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 112: | Intermittent Dermatologic Transfusion Service | per procedure | GBP 2,431.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-067 · service catalogue

**Applies to:** services: Intermittent Neurological Nutritional Support

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intermittent Neurological Nutritional Support; unit basis: per day of service; base rate cents: 50275; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 113: | Intermittent Neurological Nutritional Support | per day of service | GBP 502.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-068 · service catalogue

**Applies to:** services: Intermittent Pulmonary Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intermittent Pulmonary Rehabilitation Programme; unit basis: per visit; base rate cents: 13450; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 114: | Intermittent Pulmonary Rehabilitation Programme | per visit | GBP 134.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-069 · service catalogue

**Applies to:** services: Intermittent Rheumatologic Diagnostic Imaging

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Intermittent Rheumatologic Diagnostic Imaging; unit basis: per procedure; base rate cents: 197700; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 115: | Intermittent Rheumatologic Diagnostic Imaging | per procedure | GBP 1,977.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-070 · service catalogue

**Applies to:** services: Outpatient Immunologic Consultation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Outpatient Immunologic Consultation; unit basis: per procedure; base rate cents: 279225; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 116: | Outpatient Immunologic Consultation | per procedure | GBP 2,792.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-071 · service catalogue

**Applies to:** services: Outpatient Metabolic Radiotherapy Fraction

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Outpatient Metabolic Radiotherapy Fraction; unit basis: per item supplied; base rate cents: 22775; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 117: | Outpatient Metabolic Radiotherapy Fraction | per item supplied | GBP 227.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-072 · service catalogue

**Applies to:** services: Postoperative Metabolic Critical Care Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Postoperative Metabolic Critical Care Occupancy; unit basis: per night of occupancy; base rate cents: 59700; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 118: | Postoperative Metabolic Critical Care Occupancy | per night of occupancy | GBP 597.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-073 · service catalogue

**Applies to:** services: Postoperative Obstetric Isolation Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Postoperative Obstetric Isolation Room Occupancy; unit basis: per day of service; base rate cents: 43525; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 119: | Postoperative Obstetric Isolation Room Occupancy | per day of service | GBP 435.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-074 · service catalogue

**Applies to:** services: Postoperative Ophthalmic Radiotherapy Fraction

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Postoperative Ophthalmic Radiotherapy Fraction; unit basis: per procedure; base rate cents: 413325; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 120: | Postoperative Ophthalmic Radiotherapy Fraction | per procedure | GBP 4,133.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-075 · service catalogue

**Applies to:** services: Postoperative Pulmonary Wound Care

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Postoperative Pulmonary Wound Care; unit basis: per visit; base rate cents: 18050; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 121: | Postoperative Pulmonary Wound Care | per visit | GBP 180.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-076 · service catalogue

**Applies to:** services: Preoperative Endocrine Physiotherapy Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Endocrine Physiotherapy Session; unit basis: per visit; base rate cents: 29975; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 122: | Preoperative Endocrine Physiotherapy Session | per visit | GBP 299.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-077 · service catalogue

**Applies to:** services: Preoperative Geriatric Ventilation Support

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Geriatric Ventilation Support; unit basis: per hour; base rate cents: 6875; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 123: | Preoperative Geriatric Ventilation Support | per hour | GBP 68.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-078 · service catalogue

**Applies to:** services: Preoperative Immunologic Endoscopic Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Immunologic Endoscopic Procedure; unit basis: per procedure; base rate cents: 151975; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 124: | Preoperative Immunologic Endoscopic Procedure | per procedure | GBP 1,519.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-079 · service catalogue

**Applies to:** services: Preoperative Oncology Consultation

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Oncology Consultation; unit basis: per visit; base rate cents: 42125; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 125: | Preoperative Oncology Consultation | per visit | GBP 421.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-080 · service catalogue

**Applies to:** services: Preoperative Otolaryngologic Sterilisation Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Otolaryngologic Sterilisation Service; unit basis: per procedure; base rate cents: 134725; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 126: | Preoperative Otolaryngologic Sterilisation Service | per procedure | GBP 1,347.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-081 · service catalogue

**Applies to:** services: Preoperative Renal Wound Care

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Renal Wound Care; unit basis: per visit; base rate cents: 40325; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 127: | Preoperative Renal Wound Care | per visit | GBP 403.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-082 · service catalogue

**Applies to:** services: Preoperative Vascular Diagnostic Imaging

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Preoperative Vascular Diagnostic Imaging; unit basis: per procedure; base rate cents: 396725; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 128: | Preoperative Vascular Diagnostic Imaging | per procedure | GBP 3,967.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-083 · service catalogue

**Applies to:** services: Routine Cardiac Specimen Analysis

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Cardiac Specimen Analysis; unit basis: per item supplied; base rate cents: 23350; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 129: | Routine Cardiac Specimen Analysis | per item supplied | GBP 233.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-084 · service catalogue

**Applies to:** services: Routine Dermatologic Transfusion Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Dermatologic Transfusion Service; unit basis: per unit dispensed; base rate cents: 5325; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 130: | Routine Dermatologic Transfusion Service | per unit dispensed | GBP 53.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-085 · service catalogue

**Applies to:** services: Routine Gastrointestinal Transfusion Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Gastrointestinal Transfusion Service; unit basis: per procedure; base rate cents: 341525; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 131: | Routine Gastrointestinal Transfusion Service | per procedure | GBP 3,415.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-086 · service catalogue

**Applies to:** services: Routine Haematology Infusion Therapy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Haematology Infusion Therapy; unit basis: per hour; base rate cents: 10200; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 132: | Routine Haematology Infusion Therapy | per hour | GBP 102.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-087 · service catalogue

**Applies to:** services: Routine Immunologic Ward Bed Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Immunologic Ward Bed Occupancy; unit basis: per night of occupancy; base rate cents: 215875; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 133: | Routine Immunologic Ward Bed Occupancy | per night of occupancy | GBP 2,158.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-088 · service catalogue

**Applies to:** services: Routine Infectious Critical Care Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Infectious Critical Care Occupancy; unit basis: per night of occupancy; base rate cents: 58375; currency: GBP; daily cap: value: 6; unit: nights

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 134: | Routine Infectious Critical Care Occupancy | per night of occupancy | GBP 583.75 | 6 nights |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-089 · service catalogue

**Applies to:** services: Routine Oncology Discharge Planning

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Oncology Discharge Planning; unit basis: per visit; base rate cents: 29050; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 135: | Routine Oncology Discharge Planning | per visit | GBP 290.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-090 · service catalogue

**Applies to:** services: Routine Palliative Critical Care Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Palliative Critical Care Occupancy; unit basis: per night of occupancy; base rate cents: 96975; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 136: | Routine Palliative Critical Care Occupancy | per night of occupancy | GBP 969.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-091 · service catalogue

**Applies to:** services: Routine Psychiatric Rehabilitation Programme

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Psychiatric Rehabilitation Programme; unit basis: per day of service; base rate cents: 72500; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 137: | Routine Psychiatric Rehabilitation Programme | per day of service | GBP 725.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-092 · service catalogue

**Applies to:** services: Routine Urologic Biopsy Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Routine Urologic Biopsy Procedure; unit basis: per procedure; base rate cents: 226950; currency: GBP; daily cap: value: 6; unit: procedures

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 138: | Routine Urologic Biopsy Procedure | per procedure | GBP 2,269.50 | 6 procedures |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-093 · service catalogue

**Applies to:** services: Specialist Dermatologic Transport Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Specialist Dermatologic Transport Service; unit basis: per visit; base rate cents: 43575; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 139: | Specialist Dermatologic Transport Service | per visit | GBP 435.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-094 · service catalogue

**Applies to:** services: Specialist Hepatic Physiotherapy Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Specialist Hepatic Physiotherapy Session; unit basis: per hour; base rate cents: 5350; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 140: | Specialist Hepatic Physiotherapy Session | per hour | GBP 53.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-095 · service catalogue

**Applies to:** services: Specialist Neurological Recovery Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Specialist Neurological Recovery Room Occupancy; unit basis: per hour; base rate cents: 15400; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 141: | Specialist Neurological Recovery Room Occupancy | per hour | GBP 154.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-096 · service catalogue

**Applies to:** services: Specialist Otolaryngologic Pharmaceutical Dispensing

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Specialist Otolaryngologic Pharmaceutical Dispensing; unit basis: per unit dispensed; base rate cents: 1425; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 142: | Specialist Otolaryngologic Pharmaceutical Dispensing | per unit dispensed | GBP 14.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-097 · service catalogue

**Applies to:** services: Specialist Otolaryngologic Theatre Time

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Specialist Otolaryngologic Theatre Time; unit basis: per hour; base rate cents: 8025; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 143: | Specialist Otolaryngologic Theatre Time | per hour | GBP 80.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-098 · service catalogue

**Applies to:** services: Specialist Paediatric Biopsy Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Specialist Paediatric Biopsy Procedure; unit basis: per procedure; base rate cents: 257325; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 144: | Specialist Paediatric Biopsy Procedure | per procedure | GBP 2,573.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-099 · service catalogue

**Applies to:** services: Standard Endocrine Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Endocrine Dialysis Session; unit basis: per visit; base rate cents: 37600; currency: GBP; daily cap: value: 8; unit: visits

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 145: | Standard Endocrine Dialysis Session | per visit | GBP 376.00 | 8 visits |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-100 · service catalogue

**Applies to:** services: Standard Endocrine Endoscopic Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Endocrine Endoscopic Procedure; unit basis: per procedure; base rate cents: 124450; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 146: | Standard Endocrine Endoscopic Procedure | per procedure | GBP 1,244.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-101 · service catalogue

**Applies to:** services: Standard Geriatric Nutritional Support

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Geriatric Nutritional Support; unit basis: per day of service; base rate cents: 42475; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 147: | Standard Geriatric Nutritional Support | per day of service | GBP 424.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-102 · service catalogue

**Applies to:** services: Standard Otolaryngologic Radiotherapy Fraction

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Otolaryngologic Radiotherapy Fraction; unit basis: per item supplied; base rate cents: 25250; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 148: | Standard Otolaryngologic Radiotherapy Fraction | per item supplied | GBP 252.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-103 · service catalogue

**Applies to:** services: Standard Paediatric Biopsy Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Paediatric Biopsy Procedure; unit basis: per item supplied; base rate cents: 16100; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 149: | Standard Paediatric Biopsy Procedure | per item supplied | GBP 161.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-104 · service catalogue

**Applies to:** services: Standard Psychiatric Endoscopic Procedure

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Psychiatric Endoscopic Procedure; unit basis: per procedure; base rate cents: 242225; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 150: | Standard Psychiatric Endoscopic Procedure | per procedure | GBP 2,422.25 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-105 · service catalogue

**Applies to:** services: Standard Pulmonary Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Standard Pulmonary Dialysis Session; unit basis: per visit; base rate cents: 43175; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 151: | Standard Pulmonary Dialysis Session | per visit | GBP 431.75 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-106 · service catalogue

**Applies to:** services: Supervised Musculoskeletal Dialysis Session

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Supervised Musculoskeletal Dialysis Session; unit basis: per visit; base rate cents: 35150; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 152: | Supervised Musculoskeletal Dialysis Session | per visit | GBP 351.50 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-107 · service catalogue

**Applies to:** services: Supervised Otolaryngologic Sterilisation Service

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Supervised Otolaryngologic Sterilisation Service; unit basis: per item supplied; base rate cents: 24200; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 153: | Supervised Otolaryngologic Sterilisation Service | per item supplied | GBP 242.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T4-108 · service catalogue

**Applies to:** services: Supervised Renal Isolation Room Occupancy

**Condition:** service name match: exact

**Action:** type: set_base_rate; service name: Supervised Renal Isolation Room Occupancy; unit basis: per night of occupancy; base rate cents: 164500; currency: GBP; daily cap: unspecified

**Scope:** hospital id: hospital_1; group by: contract_number, service

**Order:** stage: base_rate; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 154: | Supervised Renal Isolation Room Occupancy | per night of occupancy | GBP 1,645.00 | — |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 45: | Service | Unit basis | Rate | Daily cap |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** explicit. Use the exact contractual service name and billing basis; do not infer a unit from its name.

### H1-T5-001 · threshold premium

**Applies to:** services: Ambulatory Ophthalmic Case Conference

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 6; unit: visits

**Action:** type: uplift_unit_rate; percent: 20; multiplier: numerator: 120; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 160: | Ambulatory Ophthalmic Case Conference | 6 visits | +20% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-002 · threshold premium

**Applies to:** services: Ambulatory Ophthalmic Dialysis Session

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 10; unit: procedures

**Action:** type: uplift_unit_rate; percent: 20; multiplier: numerator: 120; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 161: | Ambulatory Ophthalmic Dialysis Session | 10 procedures | +20% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-003 · threshold premium

**Applies to:** services: Continuous Musculoskeletal Wound Care

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 8; unit: days

**Action:** type: uplift_unit_rate; percent: 40; multiplier: numerator: 140; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 162: | Continuous Musculoskeletal Wound Care | 8 days | +40% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-004 · threshold premium

**Applies to:** services: Emergency Dermatologic Case Conference

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 10; unit: hours

**Action:** type: uplift_unit_rate; percent: 40; multiplier: numerator: 140; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 163: | Emergency Dermatologic Case Conference | 10 hours | +40% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-005 · threshold premium

**Applies to:** services: Preoperative Geriatric Ventilation Support

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 8; unit: hours

**Action:** type: uplift_unit_rate; percent: 20; multiplier: numerator: 120; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 164: | Preoperative Geriatric Ventilation Support | 8 hours | +20% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-006 · threshold premium

**Applies to:** services: Preoperative Renal Wound Care

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 8; unit: visits

**Action:** type: uplift_unit_rate; percent: 25; multiplier: numerator: 125; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 165: | Preoperative Renal Wound Care | 8 visits | +25% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-007 · threshold premium

**Applies to:** services: Routine Psychiatric Rehabilitation Programme

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 8; unit: days

**Action:** type: uplift_unit_rate; percent: 25; multiplier: numerator: 125; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 166: | Routine Psychiatric Rehabilitation Programme | 8 days | +25% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-008 · threshold premium

**Applies to:** services: Specialist Neurological Recovery Room Occupancy

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 8; unit: hours

**Action:** type: uplift_unit_rate; percent: 30; multiplier: numerator: 130; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 167: | Specialist Neurological Recovery Room Occupancy | 8 hours | +30% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T5-009 · threshold premium

**Applies to:** services: Standard Pulmonary Dialysis Session

**Condition:** metric: delivered_daily_quantity_excluding_duplicates; operator: >; threshold: value: 8; unit: visits

**Action:** type: uplift_unit_rate; percent: 25; multiplier: numerator: 125; denominator: 100; applies to: all_units_on_matching_lines

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 168: | Standard Pulmonary Dialysis Session | 8 visits | +25% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5 · line 158: | Service | Applies when daily quantity exceeds | Uplift |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §5.1 · line 170: 5.1 A threshold premium is assessed against the aggregate quantity of that Service delivered to the Patient on the Service Day, not against the quantity on any one line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use assessment hospital identity, preserve separate billed/delivered/payable quantities, deduplicate delivered usage for premiums, and apply a qualifying premium to all units. Uncertain identity or quantities propagate to dependent rules. Known violations and unknown expected totals are separate states.

**Policy references:** hospital_1_user_conventions_v1#/decisions/engine

### H1-T6-001 · weekend uplift

**Applies to:** services: Advanced Neurological Consultation

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 20; multiplier: numerator: 120; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 176: | Advanced Neurological Consultation | +20% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T6-002 · weekend uplift

**Applies to:** services: Assisted Geriatric Infusion Therapy

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 12; multiplier: numerator: 112; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 177: | Assisted Geriatric Infusion Therapy | +12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T6-003 · weekend uplift

**Applies to:** services: Assisted Infectious Discharge Planning

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 12; multiplier: numerator: 112; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 178: | Assisted Infectious Discharge Planning | +12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T6-004 · weekend uplift

**Applies to:** services: Emergency Renal Radiotherapy Fraction

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 20; multiplier: numerator: 120; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 179: | Emergency Renal Radiotherapy Fraction | +20% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T6-005 · weekend uplift

**Applies to:** services: Focused Orthopaedic Transport Service

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 10; multiplier: numerator: 110; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 180: | Focused Orthopaedic Transport Service | +10% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T6-006 · weekend uplift

**Applies to:** services: Specialist Dermatologic Transport Service

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 12; multiplier: numerator: 112; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 181: | Specialist Dermatologic Transport Service | +12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T6-007 · weekend uplift

**Applies to:** services: Supervised Musculoskeletal Dialysis Session

**Condition:** metric: service_date_weekday; operator: in; values: Saturday, Sunday

**Action:** type: uplift_unit_rate; percent: 12; multiplier: numerator: 112; denominator: 100

**Scope:** hospital id: hospital_1; group by: contract_number, service, service_date

**Order:** stage: premium_or_uplift; after: bundle_substitution, facility_multiplier, plan_tier_multiplier; position: 4

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 182: | Supervised Musculoskeletal Dialysis Session | +12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §6 · line 174: | Service | Uplift where the Service Date is not a Business Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.2 · line 27: 2.2 "Business Day" means any Service Day other than a Saturday or a Sunday.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.

### H1-T7-001 · volume discount

**Applies to:** services: Ambulatory Pulmonary Recovery Room Occupancy

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 60; unit: nights; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 10; multiplier: numerator: 90; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 188: | Ambulatory Pulmonary Recovery Room Occupancy | 60 nights | 10% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-002 · volume discount

**Applies to:** services: Comprehensive Infectious Nursing Observation

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 80; unit: days; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 10; multiplier: numerator: 90; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 189: | Comprehensive Infectious Nursing Observation | 80 days | 10% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-003 · volume discount

**Applies to:** services: Comprehensive Infectious Nursing Observation

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 240; unit: days; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 25; multiplier: numerator: 75; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 190: | Comprehensive Infectious Nursing Observation | 240 days | 25% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-004 · volume discount

**Applies to:** services: Extended Geriatric Wound Care

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 60; unit: items; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 15; multiplier: numerator: 85; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 191: | Extended Geriatric Wound Care | 60 items | 15% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-005 · volume discount

**Applies to:** services: Intensive Gastrointestinal Isolation Room Occupancy

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 60; unit: nights; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 12; multiplier: numerator: 88; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 192: | Intensive Gastrointestinal Isolation Room Occupancy | 60 nights | 12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-006 · volume discount

**Applies to:** services: Intensive Gastrointestinal Isolation Room Occupancy

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 180; unit: nights; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 30; multiplier: numerator: 70; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 193: | Intensive Gastrointestinal Isolation Room Occupancy | 180 nights | 30% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-007 · volume discount

**Applies to:** services: Intermittent Pulmonary Rehabilitation Programme

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 120; unit: visits; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 10; multiplier: numerator: 90; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 194: | Intermittent Pulmonary Rehabilitation Programme | 120 visits | 10% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-008 · volume discount

**Applies to:** services: Preoperative Immunologic Endoscopic Procedure

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 80; unit: procedures; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 12; multiplier: numerator: 88; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 195: | Preoperative Immunologic Endoscopic Procedure | 80 procedures | 12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-009 · volume discount

**Applies to:** services: Preoperative Immunologic Endoscopic Procedure

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 240; unit: procedures; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 20; multiplier: numerator: 80; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 196: | Preoperative Immunologic Endoscopic Procedure | 240 procedures | 20% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-010 · volume discount

**Applies to:** services: Standard Otolaryngologic Radiotherapy Fraction

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 60; unit: items; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 12; multiplier: numerator: 88; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 197: | Standard Otolaryngologic Radiotherapy Fraction | 60 items | 12% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T7-011 · volume discount

**Applies to:** services: Standard Otolaryngologic Radiotherapy Fraction

**Condition:** metric: prior_cumulative_billed_units; operator: >; threshold: value: 180; unit: items; exclude current line: yes

**Action:** type: discount_unit_rate; percent: 30; multiplier: numerator: 70; denominator: 100; tier selection: deepest_qualifying_discount; stack tiers: no; applies to: entire_current_line

**Scope:** hospital id: hospital_1; group by: contract_number, service; patients: all; period: whole_contract_term; counting: quantity: original_billed_quantity; exclude current line: yes; sort by: service_date ASC, line_id ASC; identifier comparison: lexical; include duplicate units: yes; include disallowed units: yes; subtract rejected units: no

**Order:** stage: cumulative_volume_discount; after: bundle_substitution, facility_multiplier, plan_tier_multiplier, premium_or_uplift; position: 5

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 198: | Standard Otolaryngologic Radiotherapy Fraction | 180 items | 30% |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7 · line 186: | Service | Cumulative utilisation exceeds | Discount on subsequent units |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.4 · line 31: 2.4 "Cumulative utilisation" means the running total of Units of a Service billed under this Agreement, counted in Service Date order, up to but excluding the line item being priced.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.1 · line 200: 7.1 Cumulative utilisation is counted cumulatively across the whole term of this Agreement and aggregated across all Patients.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §7.2 · line 201: 7.2 Where two thresholds are met, the deeper discount applies. The discount applies to a line item where cumulative utilisation *prior to* that line item exceeds the threshold. Where two line items share a Service Date, they are counted in ascending order of line identifier.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** implementation_convention. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear. Count all prior original billed quantities for the service, including duplicates and disallowed units; payable corrections never rewrite usage history.

**Policy references:** hospital_1_user_conventions_v1#/decisions/line_ordering, hospital_1_user_conventions_v1#/decisions/cumulative_usage

- Contract ambiguity resolved by convention: Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.
- Contract ambiguity resolved by convention: The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total.

### H1-T8-001 · daily quantity cap

**Applies to:** services: Advanced Metabolic Nursing Observation

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 6; unit: days

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 6; unit: days; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 207: | Advanced Metabolic Nursing Observation | 6 days |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 51: | Advanced Metabolic Nursing Observation | per day of service | GBP 1,301.25 | 6 days |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T8-002 · daily quantity cap

**Applies to:** services: Advanced Rheumatologic Laboratory Panel

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 4; unit: tests

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 4; unit: tests; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 208: | Advanced Rheumatologic Laboratory Panel | 4 tests |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 53: | Advanced Rheumatologic Laboratory Panel | per test | GBP 147.75 | 4 tests |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T8-003 · daily quantity cap

**Applies to:** services: Comprehensive Oncology Nursing Observation

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 12; unit: hours

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 12; unit: hours; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 209: | Comprehensive Oncology Nursing Observation | 12 hours |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 73: | Comprehensive Oncology Nursing Observation | per hour | GBP 84.75 | 12 hours |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T8-004 · daily quantity cap

**Applies to:** services: Inpatient Palliative Specimen Analysis

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 4; unit: items

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 4; unit: items; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 210: | Inpatient Palliative Specimen Analysis | 4 items |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 106: | Inpatient Palliative Specimen Analysis | per item supplied | GBP 297.25 | 4 items |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T8-005 · daily quantity cap

**Applies to:** services: Routine Infectious Critical Care Occupancy

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 6; unit: nights

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 6; unit: nights; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 211: | Routine Infectious Critical Care Occupancy | 6 nights |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 134: | Routine Infectious Critical Care Occupancy | per night of occupancy | GBP 583.75 | 6 nights |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T8-006 · daily quantity cap

**Applies to:** services: Routine Urologic Biopsy Procedure

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 6; unit: procedures

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 6; unit: procedures; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 212: | Routine Urologic Biopsy Procedure | 6 procedures |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 138: | Routine Urologic Biopsy Procedure | per procedure | GBP 2,269.50 | 6 procedures |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T8-007 · daily quantity cap

**Applies to:** services: Standard Endocrine Dialysis Session

**Condition:** metric: aggregate_daily_quantity; operator: >; threshold: value: 8; unit: visits

**Action:** type: flag_quantity_cap_exceeded; maximum billable units: value: 8; unit: visits; correction policy: group by: contract_number, patient_id, service, service_date; allocation order: line_id ASC; identifier comparison: lexical; retain: earlier_eligible_units; exclude: latest_excess_units; partly excess line: reduce_expected_payable_quantity; exclude whole partly excess line: no; shared controls reference: hospital_1_user_conventions_v1#/decisions/corrections

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date, service; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 213: | Standard Endocrine Dialysis Session | 8 visits |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §4 · line 145: | Standard Endocrine Dialysis Session | per visit | GBP 376.00 | 8 visits |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §8 · line 205: | Service | Maximum billable units per Patient per Service Day |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.3 · line 29: 2.3 "Unit" means one billable unit of the Service on the unit basis stated for that Service in Section 4.

**Uncertainty:** implementation_convention. Preserve originals and flag violations. Cap allocation retains earlier eligible units, including partial lines. Duplicate selection prefers correctly adjusted pricing, then lexical line ID, or corrects the earliest payable occurrence if none comply. Conflicting evidence that prevents a defensible correction is sent for review. These are implementation conventions. Use ascending lexical text sorting. Validate fixed-width, zero-padded numeric components across the dataset; revisit if exceptions appear.

**Policy references:** hospital_1_user_conventions_v1#/decisions/corrections, hospital_1_user_conventions_v1#/decisions/line_ordering

- Contract ambiguity resolved by convention: The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded.

### H1-T9-001 · bundle

**Applies to:** services: Advanced Cardiac Recovery Room Occupancy, Routine Cardiac Specimen Analysis

**Condition:** all services present: Advanced Cardiac Recovery Room Occupancy, Routine Cardiac Specimen Analysis; same patient: yes; same service day: yes

**Action:** type: replace_unit_rates; rates cents: Advanced Cardiac Recovery Room Occupancy: 16400; Routine Cardiac Specimen Analysis: 19150; currency: GBP

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date; across invoices: yes

**Order:** stage: bundle_substitution; after: base_rate; position: 1

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9 · line 219: | Advanced Cardiac Recovery Room Occupancy | Routine Cardiac Specimen Analysis | GBP 164.00 | GBP 191.50 |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9 · line 217: | Service A | Service B | Bundled rate A | Bundled rate B |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9.1 · line 223: 9.1 The bundled rates in this Section replace the standalone rates in Section 4 whenever both Services in a pair are delivered to the same Patient on the same Service Day. They are substituted before any multiplier, premium or discount is applied.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Replace each service's own unit rate when the pair occurs for the same patient/day; these are two replacement rates, not one bundle total.

### H1-T9-002 · bundle

**Applies to:** services: Extended Palliative Laboratory Panel, Inpatient Ophthalmic Radiotherapy Fraction

**Condition:** all services present: Extended Palliative Laboratory Panel, Inpatient Ophthalmic Radiotherapy Fraction; same patient: yes; same service day: yes

**Action:** type: replace_unit_rates; rates cents: Extended Palliative Laboratory Panel: 15175; Inpatient Ophthalmic Radiotherapy Fraction: 21500; currency: GBP

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date; across invoices: yes

**Order:** stage: bundle_substitution; after: base_rate; position: 1

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9 · line 220: | Extended Palliative Laboratory Panel | Inpatient Ophthalmic Radiotherapy Fraction | GBP 151.75 | GBP 215.00 |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9 · line 217: | Service A | Service B | Bundled rate A | Bundled rate B |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9.1 · line 223: 9.1 The bundled rates in this Section replace the standalone rates in Section 4 whenever both Services in a pair are delivered to the same Patient on the same Service Day. They are substituted before any multiplier, premium or discount is applied.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Replace each service's own unit rate when the pair occurs for the same patient/day; these are two replacement rates, not one bundle total.

### H1-T9-003 · bundle

**Applies to:** services: Inpatient Hepatic Physiotherapy Session, Specialist Otolaryngologic Theatre Time

**Condition:** all services present: Inpatient Hepatic Physiotherapy Session, Specialist Otolaryngologic Theatre Time; same patient: yes; same service day: yes

**Action:** type: replace_unit_rates; rates cents: Inpatient Hepatic Physiotherapy Session: 37500; Specialist Otolaryngologic Theatre Time: 7050; currency: GBP

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id, service_date; across invoices: yes

**Order:** stage: bundle_substitution; after: base_rate; position: 1

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9 · line 221: | Inpatient Hepatic Physiotherapy Session | Specialist Otolaryngologic Theatre Time | GBP 375.00 | GBP 70.50 |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9 · line 217: | Service A | Service B | Bundled rate A | Bundled rate B |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §9.1 · line 223: 9.1 The bundled rates in this Section replace the standalone rates in Section 4 whenever both Services in a pair are delivered to the same Patient on the same Service Day. They are substituted before any multiplier, premium or discount is applied.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.1 · line 35: 3.1 All monetary amounts are expressed in whole cents. Where the application of a multiplier, premium or discount produces a fraction of a cent, the result shall be rounded to the nearest whole cent, with exact halves rounded away from zero ("half up"). Rounding is applied after each individual step of the calculation, not once at the end.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §3.2 · line 37: 3.2 Where more than one adjustment applies to the same Service, the adjustments shall be applied to the base rate strictly in the following order: (a) substitution of a bundled rate; (b) the facility multiplier; (c) the plan-tier multiplier; (d) any premium or uplift; and (e) any cumulative volume discount. The line total is then the resulting unit rate multiplied by the billed quantity.

**Uncertainty:** explicit. Replace each service's own unit rate when the pair occurs for the same patient/day; these are two replacement rates, not one bundle total.

### H1-T10-001 · exclusion window

**Applies to:** services: Advanced Metabolic Anaesthesia Administration

**Condition:** trigger service: Standard Endocrine Endoscopic Procedure; metric: absolute_service_date_difference_days; window days: 7; direction: both; operator: <=; same patient: yes

**Action:** type: not_billable; target service: Advanced Metabolic Anaesthesia Administration; expected payable cents: 0

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 229: | Advanced Metabolic Anaesthesia Administration | 7 days | Standard Endocrine Endoscopic Procedure |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 227: | Service | Not billable within | Of this Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

- Contract ambiguity resolved by convention: Does 'within N days' include exactly N days?
- Contract ambiguity resolved by convention: Is the exclusion limited to the same patient? Section 10 does not state a patient relationship.

### H1-T10-002 · exclusion window

**Applies to:** services: Continuous Immunologic Theatre Time

**Condition:** trigger service: Supervised Otolaryngologic Sterilisation Service; metric: absolute_service_date_difference_days; window days: 21; direction: both; operator: <=; same patient: yes

**Action:** type: not_billable; target service: Continuous Immunologic Theatre Time; expected payable cents: 0

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 230: | Continuous Immunologic Theatre Time | 21 days | Supervised Otolaryngologic Sterilisation Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 227: | Service | Not billable within | Of this Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

- Contract ambiguity resolved by convention: Does 'within N days' include exactly N days?
- Contract ambiguity resolved by convention: Is the exclusion limited to the same patient? Section 10 does not state a patient relationship.

### H1-T10-003 · exclusion window

**Applies to:** services: Intensive Ophthalmic Case Conference

**Condition:** trigger service: Continuous Otolaryngologic Telemetry Monitoring; metric: absolute_service_date_difference_days; window days: 7; direction: both; operator: <=; same patient: yes

**Action:** type: not_billable; target service: Intensive Ophthalmic Case Conference; expected payable cents: 0

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 231: | Intensive Ophthalmic Case Conference | 7 days | Continuous Otolaryngologic Telemetry Monitoring |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 227: | Service | Not billable within | Of this Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

- Contract ambiguity resolved by convention: Does 'within N days' include exactly N days?
- Contract ambiguity resolved by convention: Is the exclusion limited to the same patient? Section 10 does not state a patient relationship.

### H1-T10-004 · exclusion window

**Applies to:** services: Postoperative Ophthalmic Radiotherapy Fraction

**Condition:** trigger service: Inpatient Palliative Isolation Room Occupancy; metric: absolute_service_date_difference_days; window days: 30; direction: both; operator: <=; same patient: yes

**Action:** type: not_billable; target service: Postoperative Ophthalmic Radiotherapy Fraction; expected payable cents: 0

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 232: | Postoperative Ophthalmic Radiotherapy Fraction | 30 days | Inpatient Palliative Isolation Room Occupancy |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 227: | Service | Not billable within | Of this Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

- Contract ambiguity resolved by convention: Does 'within N days' include exactly N days?
- Contract ambiguity resolved by convention: Is the exclusion limited to the same patient? Section 10 does not state a patient relationship.

### H1-T10-005 · exclusion window

**Applies to:** services: Routine Immunologic Ward Bed Occupancy

**Condition:** trigger service: Comprehensive Otolaryngologic Theatre Time; metric: absolute_service_date_difference_days; window days: 10; direction: both; operator: <=; same patient: yes

**Action:** type: not_billable; target service: Routine Immunologic Ward Bed Occupancy; expected payable cents: 0

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 233: | Routine Immunologic Ward Bed Occupancy | 10 days | Comprehensive Otolaryngologic Theatre Time |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 227: | Service | Not billable within | Of this Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

- Contract ambiguity resolved by convention: Does 'within N days' include exactly N days?
- Contract ambiguity resolved by convention: Is the exclusion limited to the same patient? Section 10 does not state a patient relationship.

### H1-T10-006 · exclusion window

**Applies to:** services: Standard Paediatric Biopsy Procedure

**Condition:** trigger service: Advanced Infectious Critical Care Occupancy; metric: absolute_service_date_difference_days; window days: 10; direction: both; operator: <=; same patient: yes

**Action:** type: not_billable; target service: Standard Paediatric Biopsy Procedure; expected payable cents: 0

**Scope:** hospital id: hospital_1; group by: contract_number, patient_id; patient relationship: same_patient; across invoices: yes

**Order:** stage: validation; after: none; position: unspecified

**Source:**

- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 234: | Standard Paediatric Biopsy Procedure | 10 days | Advanced Infectious Critical Care Occupancy |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10 · line 227: | Service | Not billable within | Of this Service |
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §10.1 · line 236: 10.1 An exclusion window is measured in either direction from the Service Date of the excluded Service.
- data/assessment/contracts/hospital_1/provider_services_agreement.md · §2.1 · line 25: 2.1 "Service Day" means the calendar day recorded as the Service Date of the line item.

**Uncertainty:** implementation_convention. Check the same patient across all invoices in either date direction, including exactly N days. Only the excluded service charge becomes non-payable; this is not a discount. Inclusive endpoints and patient scope are documented assumptions.

**Policy references:** hospital_1_user_conventions_v1#/decisions/exclusions

- Contract ambiguity resolved by convention: Does 'within N days' include exactly N days?
- Contract ambiguity resolved by convention: Is the exclusion limited to the same patient? Section 10 does not state a patient relationship.

## Provenance

Source SHA-256: `695c50dbb32667446f8330e1fddf785981dd544bd5c2b0d28ac9bb402ad15853`

Reviewed grammar SHA-256: `99d38f3f061de9788034956f9e24e9c4b560f8502835e738ddec6ba9b4ba08be`

The Markdown and JSON outputs are deterministic. The source snapshot and its upstream commit are recorded in data/assessment/SOURCE.json.
