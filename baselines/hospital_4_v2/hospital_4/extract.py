"""Source-pinned extraction of the reviewed Hospital 4 Markdown contract."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from contract_extractor.extract import cents, percent, quantity, STAGES

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies/hospital_4.json"


def extract(path=None):
    policy = json.loads(POLICY.read_text())
    path = Path(path) if path else ROOT / policy["document"]
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != policy["source_sha256"]:
        raise ValueError("Hospital 4 contract changed; review required before extraction")
    lines = raw.decode().splitlines()
    clauses, tables, metadata = {}, {}, {}
    section = None
    for n, text in enumerate(lines, 1):
        heading = re.match(r"## (\d+)\.", text)
        clause = re.match(r"(\d+\.\d+) ", text)
        meta = re.fullmatch(r"\*\*(.+):\*\* (.+)", text)
        if heading:
            section = heading[1]
        elif clause:
            clauses[clause[1]] = n
        elif meta:
            metadata[meta[1]] = (meta[2], n)
        elif text.startswith("|"):
            tables.setdefault(section, []).append((n, [c.strip() for c in text.strip("|").split("|")]))

    def source(n, sec):
        return {"document": policy["document"], "sha256": digest, "section": sec, "line_start": n, "line_end": n, "quote": lines[n-1]}

    rules = []
    def add(kind, applies, condition, action, refs, group=None, stage=None, row=None, questions=None):
        evidence = ([source(row[0], row[1])] if row else []) + [source(clauses[k], k) for k in refs]
        rules.append({"id": f"H4-{len(rules)+1:03d}", "kind": kind, "applies_to": applies,
                      "condition": condition, "action": action,
                      "scope": {"hospital_id": "hospital_4", "group_by": group or ["applicable_contract_number"]},
                      "order": {"stage": stage, "position": STAGES.index(stage)+1 if stage in STAGES else None},
                      "source": evidence, "uncertainty": {"status": "unresolved" if questions else "reviewed",
                          "interpretation": action.get("interpretation", kind.replace('_', ' ')), "questions": questions or []}})

    contract = {"hospital_id": "hospital_4", "contract_number": metadata["Contract number"][0],
                "provider": metadata["Provider"][0], "payer": metadata["Payer"][0], "currency": metadata["Currency"][0],
                "effective_from": "2024-01-01", "effective_to": "2025-12-31"}
    add("contract_scope", {"entity":"contract"}, {"always":True}, {"values":contract}, ["2.1"])
    rules[-1]["source"] += [source(n,"preamble") for value,n in metadata.values()]
    day_group = ["applicable_contract_number", "patient_id", "service_date", "service"]
    specs = {
        "1.1": ("definition", {"service_day":"calendar_service_date"}),
        "1.2": ("definition", {"business_days":"Monday-Friday"}),
        "1.3": ("definition", {"unit_basis_source":"Section 3"}),
        "1.4": ("definition", {"instance":"one_unit"}),
        "1.5": ("definition", {"adjustments":"Sections 5-9"}),
        "2.2": ("facility_scope", {"multiplier":{"numerator":1,"denominator":1}}),
        "2.3": ("calculation_instruction", {"base_rate_requires_all_applicable_adjustments":True}),
        "3.1": ("catalogue_scope", {"rate_basis":"per_contract_unit"}),
        "3.2": ("bundle_precedence", {"bundle_replaces_base_rate":True}),
        "4.1": ("adjustment_order", {"stages":STAGES}),
        "4.2": ("rounding", {"mode":"half_up", "timing":"after_each_step", "unit":"cent"}),
        "4.3": ("discount_tiers", {"selection":"deepest", "stack":False}),
        "4.4": ("line_calculation", {"multiply":"effective_unit_rate_times_quantity", "invoice_total":"sum_lines"}),
        "5.1": ("premium_grouping", {"metric":"delivered_daily_quantity", "group_by":day_group}),
        "5.2": ("premium_order", {"after":"bundle", "before":"discount"}),
        "5.3": ("premium_cap_interaction", {"premium_quantity":"delivered_before_cap"}),
        "6.1": ("cap_instruction", {"excess_payable_cents":0}),
        "6.2": ("cap_grouping", {"across_invoices":True}),
        "7.1": ("bundle_grouping", {"same_patient":True,"same_service_day":True}),
        "7.2": ("unpaired_service", {"use":"standalone_rate"}),
        "8.1": ("discount_scope", {"only_discounts":"Section 8"}),
        "8.2": ("discount_order", {"stage":"last_rate_adjustment"}),
        "8.3": ("discount_boundary", {"operator":">", "subsequent_units":True}),
        "8.4": ("cumulative_counting", {"exclude_current_line":True,"split_crossing_line":False}),
        "8.5": ("line_ordering", {"keys":["service_date ASC","line_id ASC"]}),
        "9.1": ("exclusion_direction", {"same_patient":True,"across_invoices":True,"direction":"both"}),
        "10.1": ("weekend_schedule", {"services":[],"interpretation":"Schedule explicitly states None; no weekend uplift rules."}),
        "11.1": ("contract_number_restriction", {"require_contract_number":True,"unique_invoice_identifier":True}),
        "11.2": ("valid_service_dates", {"term":"inclusive","service_date_lte_invoice_date":True}),
        "11.3": ("duplicate_billing", {"same_service_patient_day":True,"across_invoices":True,"correction":"approved_exact_copy_lexical_retention; conflicts reviewed"}),
    }
    if set(clauses) != set(specs) | {"2.1"}:
        raise ValueError("Unreviewed Hospital 4 clause")
    for ref,(kind,action) in specs.items():
        add(kind,{"entity":"contract_lines"},{"always":True},action,[ref])
    add("plan_scope", {"entity":"contract_lines"},{"always":True},{"multiplier":{"numerator":1,"denominator":1}},["2.2"])
    services = set()
    for sec, entries in tables.items():
        for n, cells in entries[2:]:
            name = cells[0]
            refs = ["4.1", "4.2", "4.4"]
            kw = dict(row=(n,sec))
            if sec == "3":
                service, unit, price = cells
                services.add(service)
                question = ["Does 'per hour, per item' require hours, items, or their product?"] if unit == "per hour, per item" else None
                add("service_catalogue",{"services":[service]},{"service_name_match":"exact"},
                    {"service_name":service,"unit_basis":unit,"base_rate_cents":cents(price),"currency":"GBP"},["1.3","3.1"],questions=question,**kw)
            elif sec == "5":
                threshold=quantity(cells[1].removeprefix("more than "))
                pct=percent(cells[2],True)
                add("threshold_premium",{"services":[name]}, {"metric":"delivered_daily_quantity","operator":">","threshold":threshold},
                    {"percent":pct,"multiplier":{"numerator":100+pct,"denominator":100},"applies_to":"all_units"},refs+["5.1","5.2","5.3"],day_group,"premium_or_uplift",**kw)
            elif sec == "6":
                add("daily_quantity_cap",{"services":[name]}, {"operator":">","threshold":quantity(cells[1])},
                    {"maximum_billable_units":quantity(cells[1]),"excess_payable_cents":0,"corrected_amount_status":"assumption_dependent","actual_delivered_quantity_established":False},["6.1","6.2"],day_group,**kw)
            elif sec == "7":
                a,ra,b,rb=cells
                add("bundle",{"services":[a,b]}, {"same_patient":True,"same_service_day":True},
                    {"rates_cents":{a:cents(ra),b:cents(rb)}},refs+["7.1","7.2"],day_group,"bundle_substitution",**kw)
            elif sec == "8":
                threshold=int(re.search(r"\((\d+)\)",cells[1])[1]); pct=int(re.search(r"\((\d+)%\)",cells[2])[1])
                add("volume_discount",{"services":[name]}, {"operator":">","threshold":{"value":threshold},"exclude_current_line":True},
                    {"percent":pct,"multiplier":{"numerator":100-pct,"denominator":100}},refs+["8.3","8.4","8.5"],
                    ["population_and_reset_scope_unspecified"],"cumulative_volume_discount",questions=["Population and reset horizon of cumulative usage are not specified. Do not inherit H1 all-patient/term scope."],**kw)
            elif sec == "9":
                add("exclusion_window",{"services":[name]}, {"trigger_service":cells[2],"window_days":quantity(cells[1])["value"],"direction":"both","same_patient":True,"endpoint":"inclusive_approved_interpretation","operator":"<="},
                    {"type":"not_billable","target_service":name,"interpretation":"Approved inclusive endpoints supported by analogous H1 labels, not direct H4 validation."},["9.1"],["patient_id"],**kw)
            else:
                raise ValueError("Unsupported table section " + sec)
    for rule in rules:
        names=rule["applies_to"].get("services",[])+([rule["condition"]["trigger_service"]] if "trigger_service" in rule["condition"] else [])
        if any(n not in services for n in names): raise ValueError("Unknown service reference")
        if rule["kind"] in ("exclusion_window","duplicate_billing","daily_quantity_cap"):
            rule["uncertainty"]["approval_prompt"]=policy["approval_prompt"]
            rule["uncertainty"]["status"]={"exclusion_window":"approved_interpretation",
                "duplicate_billing":"approved_convention","daily_quantity_cap":"approved_amount_assumption"}[rule["kind"]]
        if rule["kind"]=="daily_quantity_cap":
            rule["uncertainty"]["interpretation"]="Cap violation can be confirmed; corrected amount uses an approved cap-based estimate. Actual delivered quantity may be lower and is not established."
    return {"schema_version":"h4-1.1","contract":contract,"rules":rules,"policy":policy,
            "document_sha256":digest,"status":"reviewed_with_explicit_limits","counts":dict(Counter(r["kind"] for r in rules)),
            "coverage":{"reviewed_numbered_clauses":len(clauses),"table_rows":sum(len(t)-2 for t in tables.values())},
            "limitations":["dual_unit_service","cumulative_population_and_horizon","conflicting_duplicate_correction","cap_corrected_amount_assumption"]}
