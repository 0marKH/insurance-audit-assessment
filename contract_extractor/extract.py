"""A deliberately narrow parser: reviewed prose grammar plus typed table readers.

Unknown or changed prose is a diagnostic, never an invitation to infer a rule.
No invoice data, labels, network clients or language models are used here.
"""

import copy
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from .policies import DEFAULT_POLICY, apply_policy

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "data/assessment/contracts/hospital_1/provider_services_agreement.md"
DEFAULT_PROFILE = ROOT / "profiles/hospital_1.json"
STAGES = ["bundle_substitution", "facility_multiplier", "plan_tier_multiplier", "premium_or_uplift", "cumulative_volume_discount", "quantity_multiplication", "invoice_summation"]
UNITS = {"per hour": "hours", "per day of service": "days", "per visit": "visits", "per test": "tests", "per procedure": "procedures", "per night of occupancy": "nights", "per unit dispensed": "units", "per item supplied": "items"}
HEADERS = {
    "4": ["Service", "Unit basis", "Rate", "Daily cap"],
    "5": ["Service", "Applies when daily quantity exceeds", "Uplift"],
    "6": ["Service", "Uplift where the Service Date is not a Business Day"],
    "7": ["Service", "Cumulative utilisation exceeds", "Discount on subsequent units"],
    "8": ["Service", "Maximum billable units per Patient per Service Day"],
    "9": ["Service A", "Service B", "Bundled rate A", "Bundled rate B"],
    "10": ["Service", "Not billable within", "Of this Service"],
}


def cents(value):
    match = re.fullmatch(r"GBP ((?:\d{1,3}(?:,\d{3})+|\d+))\.(\d{2})", value)
    if not match:
        raise ValueError("Expected GBP amount with two decimal places: " + value)
    return int(match[1].replace(",", "")) * 100 + int(match[2])


def quantity(value):
    match = re.fullmatch(r"([1-9]\d*) (hours|days|visits|tests|procedures|nights|units|items)", value)
    if not match:
        raise ValueError("Unsupported quantity: " + value)
    return {"value": int(match[1]), "unit": match[2]}


def percent(value, uplift=False):
    match = re.fullmatch(r"\+(\d+)%" if uplift else r"(\d+)%", value)
    if not match or not 0 < int(match[1]) < 100:
        raise ValueError("Unsupported percentage: " + value)
    return int(match[1])


def uncertainty(interpretation, questions=None):
    return {"status": "unresolved" if questions else "explicit", "interpretation": interpretation,
            "questions": questions or [], "resolution": None if questions else "Supported by the cited contract text."}


def scope(group_by, **extra):
    return {"hospital_id": "hospital_1", "group_by": group_by, **extra}


def order(stage=None, after=None):
    return {"stage": stage, "after": after or [], "position": STAGES.index(stage) + 1 if stage in STAGES else None}


def extract(path=DEFAULT_CONTRACT, profile_path=DEFAULT_PROFILE, policy_path=DEFAULT_POLICY):
    path = Path(path)
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    profile = json.loads(Path(profile_path).read_text())
    try:
        source_path = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        source_path = str(path.resolve())
    digest = hashlib.sha256(raw).hexdigest()
    diagnostics, rules, covered, evidence = [], [], set(), {}
    tables = {key: [] for key in HEADERS}
    metadata, metadata_lines, headings = {}, {}, {}
    clauses, seen_headers, separators = {}, set(), set()
    section = None

    def problem(code, message, line=None):
        diagnostics.append({"severity": "error", "code": code, "message": message, "line": line})

    def cite(number, section_id):
        return {"document": source_path, "sha256": digest, "section": section_id,
                "line_start": number, "line_end": number, "quote": lines[number - 1]}

    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        heading = re.fullmatch(r"## (\d+)\. (.+)", line)
        meta = re.fullmatch(r"\*\*(.+):\*\* (.+)", line)
        clause = re.match(r"(\d+\.\d+) ", line)
        if heading:
            section = heading[1]
            if section in headings or profile["headings"].get(section) != line:
                problem("unknown_heading", "Duplicate or unsupported section heading", number)
            else:
                headings[section] = number
                covered.add(number)
        elif meta and section is None:
            key, value = meta.groups()
            if key not in profile["metadata_keys"] or key in metadata:
                problem("unknown_metadata", "Unknown or duplicate metadata: " + key, number)
            else:
                metadata[key], metadata_lines[key] = value, number
                covered.add(number)
        elif clause:
            key = clause[1]
            spec = profile["clauses"].get(key)
            if key in clauses or not spec or spec["section"] != section or spec["text"] != line:
                problem("unrecognized_clause", "Clause differs from reviewed grammar: " + key, number)
            else:
                clauses[key] = number
                evidence[key] = cite(number, key)
                covered.add(number)
        elif line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if section not in HEADERS:
                problem("unexpected_table", "Table outside supported sections", number)
            elif cells == HEADERS[section] and section not in seen_headers:
                seen_headers.add(section)
                evidence["table_" + section] = cite(number, section)
                covered.add(number)
            elif section in seen_headers and section not in separators and len(cells) == len(HEADERS[section]) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                separators.add(section)
                covered.add(number)
            elif section not in separators or len(cells) != len(HEADERS[section]):
                problem("malformed_table", "Unsupported table header or row shape", number)
            else:
                tables[section].append((number, cells))
        elif {"section": section, "text": line} in profile["literals"]:
            covered.add(number)
        else:
            problem("unrecognized_text", "Text has no reviewed parser", number)

    for key in profile["metadata_keys"]:
        if key not in metadata:
            problem("missing_metadata", "Missing " + key)
    for key in profile["headings"]:
        if key not in headings:
            problem("missing_section", "Missing section " + key)
    for key in profile["clauses"]:
        if key not in clauses:
            problem("missing_clause", "Missing supported clause " + key)
    for key in HEADERS:
        if key not in separators or not tables[key]:
            problem("missing_table", "Missing table in section " + key)

    contract = {"hospital_id": "hospital_1", "metadata_as_written": metadata}
    try:
        contract.update({"contract_number": metadata["Contract number"], "provider": metadata["Provider"],
                         "payer": metadata["Payer"], "currency": metadata["Currency"],
                         "effective_from": datetime.strptime(metadata["Effective from"], "%d %B %Y").date().isoformat(),
                         "effective_to": datetime.strptime(metadata["Effective to"], "%d %B %Y").date().isoformat()})
        for key, expected in profile["identity"].items():
            if metadata[key] != expected:
                problem("unsupported_identity", "Hospital 1 profile does not support " + key + "=" + metadata[key])
        if contract["effective_from"] > contract["effective_to"]:
            problem("invalid_term", "Effective dates are reversed")
        if "1.1" in clauses:
            clause_text = lines[clauses["1.1"] - 1]
            if f"takes effect on {metadata['Effective from']} and expires on {metadata['Effective to']}." not in clause_text:
                problem("conflicting_term", "Header dates disagree with Section 1.1")
    except (KeyError, ValueError) as exc:
        problem("invalid_metadata", str(exc))

    def add(rule_id, kind, applies_to, condition, action, rule_scope, rule_order, refs, interpretation, questions=None, row=None, evidence_status=None):
        sources = []
        if row:
            sources.append(cite(row[0], row[1]))
        for ref in refs:
            if ref in evidence:
                sources.append(copy.deepcopy(evidence[ref]))
            else:
                problem("missing_dependency", rule_id + " requires " + ref)
        rules.append({"id": rule_id, "kind": kind, "applies_to": applies_to, "condition": condition,
                      "action": action, "scope": rule_scope, "order": rule_order, "source": sources,
                      "uncertainty": uncertainty(interpretation, questions)})
        if evidence_status and not questions:
            rules[-1]["uncertainty"]["status"] = evidence_status
            rules[-1]["uncertainty"]["resolution"] = "Recorded interpretation; see decision log."

    # The reviewed prose map is a grammar of exact clauses, not runtime inference.
    for key, spec in profile["clauses"].items():
        if key not in clauses:
            continue
        for template in spec["rules"]:
            item = copy.deepcopy(template)
            add(refs=[key] + item.pop("also_source", []), **item)

    if metadata_lines:
        add("H1-SCOPE", "contract_scope", {"entity": "contract"}, {"always": True},
            {"type": "set_contract_scope", "values": {key: value for key, value in contract.items() if key != "metadata_as_written"}},
            scope(["contract_number"]), order(), ["1.1"], "Hospital identity, term and currency are recorded verbatim; ISO dates are normalized.")
        rules[-1]["source"] = [cite(n, "preamble") for n in metadata_lines.values()] + rules[-1]["source"]

    services = {}
    caps_in_schedule, caps_in_section = {}, {}
    seen_rows = set()

    def service(name):
        if name not in services:
            raise ValueError("Service not in catalogue: " + name)
        return services[name]

    def checked_quantity(value, name):
        result = quantity(value)
        if result["unit"] != UNITS[service(name)["unit_basis"]]:
            raise ValueError("Quantity unit disagrees with catalogue for " + name)
        return result

    for sec, rows in tables.items():
        for number, cells in rows:
            signature = (sec, cells[0], cells[1] if sec in ("7", "9", "10") else "")
            if signature in seen_rows:
                problem("duplicate_table_rule", "Duplicate service/threshold/pair row", number)
                continue
            seen_rows.add(signature)
            rule_id = f"H1-T{sec}-{len([r for r in rules if r['id'].startswith('H1-T' + sec + '-')]) + 1:03d}"
            row, refs = (number, sec), ["table_" + sec]
            applies = {"services": [cells[0]]}
            patient_day = scope(["contract_number", "patient_id", "service_date", "service"], across_invoices=True)
            try:
                if sec == "4":
                    name, unit, rate, cap = cells
                    if unit not in UNITS:
                        raise ValueError("Unsupported billing unit: " + unit)
                    record = {"service_name": name, "unit_basis": unit, "base_rate_cents": cents(rate), "currency": metadata.get("Currency")}
                    if cap != "—":
                        parsed_cap = quantity(cap)
                        if parsed_cap["unit"] != UNITS[unit]:
                            raise ValueError("Daily cap unit disagrees with billing unit")
                        caps_in_schedule[name] = parsed_cap
                    record["daily_cap"] = caps_in_schedule.get(name)
                    services[name] = record
                    add(rule_id, "service_catalogue", applies, {"service_name_match": "exact"}, {"type": "set_base_rate", **record}, scope(["contract_number", "service"]), order("base_rate"), refs + ["2.3"], "Use the exact contractual service name and billing basis; do not infer a unit from its name.", row=row)
                else:
                    service(cells[0])
                    if sec == "5":
                        threshold, pct = checked_quantity(cells[1], cells[0]), percent(cells[2], True)
                        add(rule_id, "threshold_premium", applies, {"metric": "aggregate_daily_quantity", "operator": ">", "threshold": threshold}, {"type": "uplift_unit_rate", "percent": pct, "multiplier": {"numerator": 100 + pct, "denominator": 100}, "applies_to": "all_units_on_matching_lines"}, patient_day, order("premium_or_uplift", STAGES[:3]), refs + ["5.1", "3.1", "3.2"], "Compare the patient's aggregate daily service quantity, then uplift the unit rate; the table says exceeds, not at least.", row=row)
                    elif sec == "6":
                        pct = percent(cells[1], True)
                        add(rule_id, "weekend_uplift", applies, {"metric": "service_date_weekday", "operator": "in", "values": ["Saturday", "Sunday"]}, {"type": "uplift_unit_rate", "percent": pct, "multiplier": {"numerator": 100 + pct, "denominator": 100}}, scope(["contract_number", "service", "service_date"]), order("premium_or_uplift", STAGES[:3]), refs + ["2.1", "2.2", "3.1", "3.2"], "Saturday and Sunday trigger the uplift. The business-day definition does not exclude public holidays.", row=row)
                    elif sec == "7":
                        threshold, pct = checked_quantity(cells[1], cells[0]), percent(cells[2])
                        add(rule_id, "volume_discount", applies, {"metric": "prior_cumulative_billed_units", "operator": ">", "threshold": threshold, "exclude_current_line": True}, {"type": "discount_unit_rate", "percent": pct, "multiplier": {"numerator": 100 - pct, "denominator": 100}, "tier_selection": "deepest_qualifying_discount", "stack_tiers": False, "applies_to": "entire_current_line"}, scope(["contract_number", "service"], patients="all", period="whole_contract_term", counting={"quantity": "billed_units", "exclude_current_line": True, "sort_by": ["service_date ASC", "line_id ASC"], "identifier_comparison": None}), order("cumulative_volume_discount", STAGES[:4]), refs + ["2.4", "7.1", "7.2", "3.1", "3.2"], "Use usage before the line, across all patients and the full term; never split a threshold-crossing line or stack discount tiers.", questions=["Ascending line identifier is specified, but lexical versus natural/numeric comparison is not defined.", "The text counts billed units; it does not explain whether subsequently rejected or duplicate units are removed from the running total."], row=row)
                    elif sec == "8":
                        cap = checked_quantity(cells[1], cells[0])
                        caps_in_section[cells[0]] = cap
                        add(rule_id, "daily_quantity_cap", applies, {"metric": "aggregate_daily_quantity", "operator": ">", "threshold": cap}, {"type": "flag_quantity_cap_exceeded", "maximum_billable_units": cap, "correction_policy": None}, patient_day, order("validation"), refs + ["2.1", "2.3"], "The cap is per service, patient and day, including lines on separate invoices.", questions=["The contract does not specify how to allocate allowed units between lines or calculate a corrected total when the cap is exceeded."], row=row)
                    elif sec == "9":
                        a, b, rate_a, rate_b = cells
                        service(b)
                        if a == b:
                            raise ValueError("Bundle must contain two distinct services")
                        add(rule_id, "bundle", {"services": [a, b]}, {"all_services_present": [a, b], "same_patient": True, "same_service_day": True}, {"type": "replace_unit_rates", "rates_cents": {a: cents(rate_a), b: cents(rate_b)}, "currency": metadata.get("Currency")}, scope(["contract_number", "patient_id", "service_date"], across_invoices=True), order("bundle_substitution", ["base_rate"]), refs + ["9.1", "3.1", "3.2"], "Replace each service's own unit rate when the pair occurs for the same patient/day; these are two replacement rates, not one bundle total.", row=row)
                    elif sec == "10":
                        excluded, window, trigger = cells
                        service(trigger)
                        days = quantity(window)
                        if days["unit"] != "days":
                            raise ValueError("Exclusion window must be in days")
                        add(rule_id, "exclusion_window", applies, {"trigger_service": trigger, "metric": "absolute_service_date_difference_days", "window_days": days["value"], "direction": "both", "operator": None, "same_patient": None}, {"type": "not_billable", "target_service": excluded}, scope(["contract_number"], patient_relationship="unspecified", across_invoices=True), order("validation"), refs + ["10.1", "2.1"], "Only the first-column service is excluded; either direction refers to time before or after the related service.", questions=["Does 'within N days' include exactly N days?", "Is the exclusion limited to the same patient? Section 10 does not state a patient relationship."], row=row)
                covered.add(number)
            except ValueError as exc:
                problem("invalid_table_value", str(exc), number)

    if caps_in_schedule != caps_in_section:
        problem("conflicting_caps", "Sections 4 and 8 do not list identical daily caps")
    for rule in rules:
        if rule["kind"] == "daily_quantity_cap":
            name = rule["applies_to"]["services"][0]
            if name in services:
                catalogue = next(r for r in rules if r["kind"] == "service_catalogue" and r["applies_to"]["services"] == [name])
                rule["source"].insert(1, copy.deepcopy(catalogue["source"][0]))

    nonempty = {i for i, line in enumerate(lines, 1) if line.strip()}
    counts = dict(sorted(Counter(r["kind"] for r in rules).items()))
    result = {"schema_version": "1.1", "extractor": {"name": "hospital_1_reviewed_grammar", "version": "0.2.0", "runtime_ai": False, "profile_sha256": hashlib.sha256(Path(profile_path).read_bytes()).hexdigest()},
              "document": {"path": source_path, "sha256": digest, "line_count": len(lines)},
              "contract": contract, "rules": rules, "diagnostics": diagnostics,
              "coverage": {"nonempty_lines": len(nonempty), "recognized_lines": len(covered), "unrecognized_lines": sorted(nonempty - covered), "rules_by_kind": counts},
              "status": "blocked" if diagnostics else "extracted_with_uncertainties" if any(r["uncertainty"]["questions"] for r in rules) else "extracted"}
    # A policy cannot make unknown contract language safe to consume.
    if policy_path is not None and not diagnostics:
        apply_policy(result, policy_path)
        result["status"] = "extracted_with_uncertainties" if any(r["uncertainty"]["questions"] for r in rules) else "extracted_with_assumptions"
    # Consumers must not treat a partial parse as a usable contract.
    for rule in rules:
        rule["ready_for_engine"] = not diagnostics and not rule["uncertainty"]["questions"]
    result["ready_for_engine"] = not diagnostics and all(r["ready_for_engine"] for r in rules)
    return result
