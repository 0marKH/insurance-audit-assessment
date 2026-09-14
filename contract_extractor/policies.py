"""Apply separately versioned user conventions without changing contract evidence."""

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "policies/hospital_1.json"


def apply_policy(result, path):
    path = Path(path)
    raw = path.read_bytes()
    policy = json.loads(raw)
    if policy.get("id") != "hospital_1_user_conventions_v1":
        raise ValueError("Unsupported implementation policy")
    source = ROOT / policy["source"]
    result["implementation_policy"] = {
        "document": path.resolve().relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "additional_source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in policy.get("additional_sources", [])},
        **copy.deepcopy(policy),
    }
    decisions = policy["decisions"]

    def resolve(rule, keys):
        u = rule["uncertainty"]
        u["contract_ambiguities"] = u["questions"]
        u["contract_interpretation"] = u["interpretation"]
        u["questions"] = []
        u["status"] = "implementation_convention"
        u["interpretation"] = " ".join(decisions[key]["interpretation"] for key in keys)
        u["resolution"] = "Resolved by the user's documented conventions; not explicit contract language."
        u["policy_references"] = [f"{policy['id']}#/decisions/{key}" for key in keys]

    for rule in result["rules"]:
        kind = rule["kind"]
        if kind in ("volume_discount", "cumulative_counting", "discount_grouping"):
            target = rule["scope"]["counting"] if kind == "volume_discount" else rule["action"]
            target.update({k: v for k, v in decisions["cumulative_usage"].items() if k != "interpretation"})
            target["identifier_comparison"] = decisions["line_ordering"]["identifier_comparison"]
            target["sort_by"] = ["service_date ASC", "line_id ASC"]
            resolve(rule, ["line_ordering", "cumulative_usage"])
        elif kind == "line_ordering":
            rule["action"]["identifier_comparison"] = decisions["line_ordering"]["identifier_comparison"]
            resolve(rule, ["line_ordering"])
        elif kind in ("exclusion_window", "exclusion_direction"):
            excluded = decisions["exclusions"]
            rule["condition"].update(operator=excluded["operator"], same_patient=excluded["same_patient"])
            rule["scope"].update(group_by=["contract_number", "patient_id"], patient_relationship="same_patient", across_invoices=excluded["across_invoices"])
            if kind == "exclusion_window":
                rule["action"]["expected_payable_cents"] = excluded["excluded_expected_payable_cents"]
            resolve(rule, ["exclusions"])
        elif kind in ("daily_quantity_cap", "duplicate_billing"):
            key = "daily_caps" if kind == "daily_quantity_cap" else "duplicates"
            rule["action"]["correction_policy"] = copy.deepcopy(decisions["corrections"][key])
            rule["action"]["correction_policy"]["shared_controls_reference"] = f"{policy['id']}#/decisions/corrections"
            resolve(rule, ["corrections", "line_ordering"])
        elif kind in ("threshold_premium", "premium_grouping") and "engine" in decisions:
            if kind == "threshold_premium":
                rule["condition"]["metric"] = "delivered_daily_quantity_excluding_duplicates"
                rule["action"]["applies_to"] = "all_units_on_matching_lines"
            else:
                rule["action"]["metric"] = "delivered_daily_quantity_excluding_duplicates"
            resolve(rule, ["engine"])
    return result
