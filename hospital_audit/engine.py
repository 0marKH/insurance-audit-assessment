"""Hospital 1 only: explicit passes, immutable inputs, exact money and uncertainty.

The engine consumes the extracted rule register. It does not read labels.
"""

import copy
import re
from collections import Counter, defaultdict
from datetime import date
from fractions import Fraction

from .matching import Matcher

UNITS = {"per hour": "per_hour", "per day of service": "per_day", "per visit": "per_visit",
         "per test": "per_test", "per procedure": "per_procedure", "per night of occupancy": "per_night",
         "per unit dispensed": "per_unit_dispensed", "per item supplied": "per_item"}


def half_up(value):
    value = Fraction(value)
    sign = -1 if value < 0 else 1
    value = abs(value)
    return sign * ((2 * value.numerator + value.denominator) // (2 * value.denominator))


def quantity(value):
    if not re.fullmatch(r"\d+(?:\.\d+)?", str(value)):
        return None
    number = Fraction(str(value))
    return number if number > 0 else None


def integer(value):
    return int(value) if re.fullmatch(r"-?\d+", str(value)) else None


def day(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def serial(value):
    if isinstance(value, Fraction):
        return value.numerator if value.denominator == 1 else {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: serial(item) for key, item in value.items() if not key.startswith("_")}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def allocate_cap(quantities, maximum):
    """Caller supplies retained eligible quantities in lexical line-ID order."""
    remaining = Fraction(maximum)
    allocated = []
    for qty in quantities:
        payable = min(qty, remaining)
        allocated.append(payable)
        remaining -= payable
    return allocated


class Engine:
    def __init__(self, reference, matcher=None):
        if not reference.get("ready_for_engine") or reference.get("diagnostics"):
            raise ValueError("A complete extracted contract with resolved policies is required")
        self.ref = reference
        self.contract = reference["contract"]
        if self.contract["hospital_id"] != "hospital_1":
            raise ValueError("Only Hospital 1 is supported")
        self.policy = reference["implementation_policy"]["decisions"]
        if "engine" not in self.policy:
            raise ValueError("Prompt 003 engine decisions must be present")
        supported = [
            self.policy["line_ordering"]["identifier_comparison"] == "lexical",
            self.policy["exclusions"]["operator"] == "<=",
            self.policy["exclusions"]["same_patient"] is True,
            self.policy["exclusions"]["across_invoices"] is True,
            self.policy["cumulative_usage"]["include_duplicate_units"] is True,
            self.policy["cumulative_usage"]["include_disallowed_units"] is True,
            self.policy["cumulative_usage"]["subtract_rejected_units"] is False,
            self.policy["engine"]["daily_premium_quantity"] == "delivered_quantity_excluding_duplicate_charges",
            self.policy["engine"]["threshold_premium_scope"] == "all_applicable_units",
            self.policy["engine"]["contract_identity"] == "assessment_hospital_context_not_printed_invoice_contract_number",
        ]
        if not all(supported):
            raise ValueError("Unsupported policy change: update and test the Hospital 1 engine before use")
        self.by_kind = defaultdict(list)
        for rule in reference["rules"]:
            self.by_kind[rule["kind"]].append(rule)
        self.catalogue = {r["action"]["service_name"]: r for r in self.by_kind["service_catalogue"]}
        self.matcher = matcher or Matcher(self.catalogue)
        self.start, self.end = day(self.contract["effective_from"]), day(self.contract["effective_to"])
        self.single = {kind: {r["applies_to"]["services"][0]: r for r in self.by_kind[kind]}
                       for kind in ("threshold_premium", "weekend_uplift", "daily_quantity_cap", "exclusion_window")}
        self.discounts = defaultdict(list)
        for rule in self.by_kind["volume_discount"]:
            self.discounts[rule["applies_to"]["services"][0]].append(rule)

    def use(self, line, rule, triggered=False):
        if rule["id"] not in line["rules_considered"]:
            line["rules_considered"].append(rule["id"])
        if triggered and rule["id"] not in line["triggered_rules"]:
            line["triggered_rules"].append(rule["id"])

    def violation(self, line, category, kind=None):
        if category not in line["violations"]:
            line["violations"].append(category)
        for rule in self.by_kind.get(kind, []):
            self.use(line, rule, True)

    @staticmethod
    def uncertain(line, reason, blockers=None):
        if reason not in line["uncertainty"]:
            line["uncertainty"].append(reason)
        if blockers:
            ids = sorted({r["record_key"] for r in blockers})
            line["dependencies"][reason] = {"count": len(ids), "sample_record_keys": ids[:20], "sample_limit": 20}

    @staticmethod
    def patient_possible(a, b):
        return not a["_patient"] or not b["_patient"] or a["_patient"] == b["_patient"]

    @staticmethod
    def day_possible(a, b):
        return a["_date"] is None or b["_date"] is None or a["_date"] == b["_date"]

    def presence(self, line, service, lines, window=0):
        """True, False or None; unknown match/patient/date can make presence uncertain."""
        possible = []
        for other in lines:
            if other is line or service not in other["_candidates"] or not self.patient_possible(line, other):
                continue
            distance = abs((line["_date"] - other["_date"]).days) if line["_date"] and other["_date"] else None
            if distance is not None and distance > window:
                continue
            if other["matched_service"] == service and other["_qty"] is not None and line["_patient"] and other["_patient"] == line["_patient"] and distance is not None:
                return True, [other]
            possible.append(other)
        return (None, possible) if possible else (False, [])

    def audit(self, headers, records):
        headers, records = copy.deepcopy(headers), copy.deepcopy(records)
        by_invoice = defaultdict(list)
        for header in headers:
            by_invoice[header.get("invoice_id")].append(header)
        id_counts = Counter(row.get("line_id") for row in records)
        lines = []
        for index, row in enumerate(records):
            matches = by_invoice.get(row.get("invoice_id"), [])
            header = matches[0] if len(matches) == 1 else {}
            match = self.matcher.match(row.get("description", ""))
            service = match["service"]
            qty, dt = quantity(row.get("quantity")), day(row.get("service_date"))
            line = {"record_key": f"row-{index + 1}", "line_id": row.get("line_id"), "invoice_id": row.get("invoice_id"),
                    "original": row, "applicable_contract_number": self.contract["contract_number"],
                    "patient_id": header.get("patient_id"), "matched_service": service, "match": match,
                    "quantities": {"original_billed_quantity": qty, "delivered_quantity": None, "expected_payable_quantity": None},
                    "expected_unit_rate_cents": None, "expected_payable_cents": None, "violations": [], "uncertainty": [],
                    "rules_considered": [], "triggered_rules": [], "calculation_steps": [], "dependencies": {},
                    "_patient": header.get("patient_id"), "_date": dt, "_qty": qty, "_candidates": set(match["candidates"]),
                    "_header": header, "_valid": True, "_order_valid": True, "_excluded": False, "_duplicate_zero": False,
                    "_unit_price": integer(row.get("unit_price_cents")), "_billed_total": integer(row.get("line_total_cents"))}
            if len(matches) != 1:
                self.uncertain(line, "missing_or_ambiguous_invoice_join")
                self.violation(line, "record_join")
                line["_valid"] = False
            if not line["_patient"]:
                self.uncertain(line, "missing_patient_context")
                line["_valid"] = False
            if not re.fullmatch(self.policy["line_ordering"]["expected_line_id_pattern"], str(row.get("line_id", ""))) or id_counts[row.get("line_id")] != 1:
                self.violation(line, "line_identifier")
                self.uncertain(line, "invalid_or_reused_line_identifier")
                line["_valid"] = False
                line["_order_valid"] = False
            if header and header.get("hospital_id") != "H1":
                self.violation(line, "hospital_identity")
                self.uncertain(line, "header_hospital_disagrees_with_assessment_context")
                line["_valid"] = False
            if header and header.get("contract_number") != self.contract["contract_number"]:
                self.violation(line, "contract_number", "contract_number_restriction")
            invoice_date = day(header.get("invoice_date"))
            if dt is None or invoice_date is None or not self.start <= dt <= self.end or dt > invoice_date:
                self.violation(line, "service_date", "valid_service_dates")
                self.uncertain(line, "invalid_date_payability_requires_review")
                line["_valid"] = False
            if not service:
                self.uncertain(line, "service_match_unresolved")
            else:
                self.use(line, self.catalogue[service])
                if row.get("unit_basis_as_billed") != UNITS[self.catalogue[service]["action"]["unit_basis"]]:
                    self.violation(line, "unit_basis")
                    self.uncertain(line, "contract_quantity_unknown_due_to_unit_mismatch")
                    line["_qty"] = None
            if qty is None:
                self.violation(line, "quantity")
                self.uncertain(line, "invalid_quantity")
            if line["_unit_price"] is None or line["_billed_total"] is None:
                self.violation(line, "monetary_format")
            elif qty is not None and half_up(qty * line["_unit_price"]) != line["_billed_total"]:
                self.violation(line, "line_arithmetic", "line_calculation")
            lines.append(line)

        self.context = defaultdict(list)
        for line in lines:
            for service in line["_candidates"]:
                self.context[service].append(line)
        # Context is scoped by applicable hospital contract, never the printed number.
        groups = defaultdict(list)
        for line in lines:
            if line["matched_service"]:
                groups[(line["_patient"], line["_date"], line["matched_service"])].append(line)
        # Exclusion presence does not depend on another charge's payability.
        for line in lines:
            rule = self.single["exclusion_window"].get(line["matched_service"])
            if rule:
                self.use(line, rule)
                present, related = self.presence(line, rule["condition"]["trigger_service"], lines, rule["condition"]["window_days"])
                line["exclusion"] = {"applies": present, "related_record_keys": [r["record_key"] for r in related[:20]]}
                line["_excluded"] = present
                if present:
                    self.use(line, rule, True)
                    self.violation(line, "exclusion_window")
                elif present is None:
                    self.uncertain(line, "exclusion_presence_uncertain", related)

        # Delivered usage: equal-quantity duplicates represent one occurrence.
        # Conflicting quantities or possible extra occurrences remain uncertain.
        for (patient, dt, service), group in groups.items():
            group_keys = {r["record_key"] for r in group}
            possible = [r for r in self.context[service] if r["record_key"] not in group_keys and
                        self.patient_possible(group[0], r) and self.day_possible(group[0], r)]
            quantities = {r["_qty"] for r in group}
            delivered = next(iter(quantities)) if len(quantities) == 1 and None not in quantities and not possible and patient and dt else None
            for line in group:
                line["quantities"]["delivered_quantity"] = delivered
                line["delivered_group_record_keys"] = [r["record_key"] for r in group]
                line["_possible_duplicates"] = possible
                if len(group) > 1:
                    self.violation(line, "duplicate_billing", "duplicate_billing")
                if delivered is None:
                    self.uncertain(line, "delivered_quantity_or_duplicate_identity_uncertain", possible or group)

        self.history(lines)
        for line in lines:
            if line["matched_service"]:
                self.price(line, lines)

        # Choose the payable occurrence using each line's applicable adjusted rate.
        for (_, _, service), group in groups.items():
            retained = []
            eligible = [r for r in group if r["_excluded"] is not True]
            ambiguous = any(not r["_valid"] or r["_excluded"] is None or r["_qty"] is None or r["_possible_duplicates"] for r in eligible)
            if len(group) > 1 and len({r["_qty"] for r in group}) != 1:
                ambiguous = True
            if len(eligible) > 1 and any(r["expected_unit_rate_cents"] is None or r["_unit_price"] is None for r in eligible):
                ambiguous = True
            if ambiguous:
                for line in eligible:
                    self.uncertain(line, "retention_or_payable_quantity_requires_review", group)
            elif eligible:
                ordered = sorted(eligible, key=lambda r: r["line_id"])
                compliant = [r for r in ordered if r["_unit_price"] == r["expected_unit_rate_cents"]]
                chosen = (compliant or ordered)[0]
                retained = [chosen]
                # Preserve duplicate-group evidence on the retained occurrence,
                # but attribute the rejected duplicate charge to discarded lines.
                # With conflicting evidence no retention is made, so violations
                # remain on all involved records for review.
                if "duplicate_billing" in chosen["violations"]:
                    chosen["violations"].remove("duplicate_billing")
                for line in ordered:
                    line["retained_record_key"] = chosen["record_key"]
                    if line is not chosen:
                        line["_duplicate_zero"] = True
                        line["quantities"]["expected_payable_quantity"] = Fraction(0)
            cap = self.single["daily_quantity_cap"].get(service)
            if cap:
                for line in group:
                    self.use(line, cap)
                delivered = group[0]["quantities"]["delivered_quantity"]
                if delivered is not None and delivered > cap["action"]["maximum_billable_units"]["value"]:
                    for line in group:
                        self.use(line, cap, True)
                        self.violation(line, "daily_cap")
            if retained:
                payable = allocate_cap([r["_qty"] for r in retained], cap["action"]["maximum_billable_units"]["value"]) if cap else [r["_qty"] for r in retained]
                for line, qty in zip(retained, payable):
                    line["quantities"]["expected_payable_quantity"] = qty

        for line in lines:
            if (line["_excluded"] is True or line["_duplicate_zero"]) and line["_valid"] and line["_qty"] is not None:
                line["expected_payable_cents"] = 0
                line["quantities"]["expected_payable_quantity"] = Fraction(0)
                line["calculation_steps"].append({"stage": "nonpayable_charge", "reason": "exclusion" if line["_excluded"] else "duplicate", "result_cents": 0})
            elif line["_valid"] and line["_excluded"] is False:
                qty, rate = line["quantities"]["expected_payable_quantity"], line["expected_unit_rate_cents"]
                if qty is not None and rate is not None:
                    line["expected_payable_cents"] = half_up(qty * rate)
                    line["calculation_steps"].append({"stage": "quantity_multiplication", "unit_rate_cents": rate, "payable_quantity": qty, "result_cents": line["expected_payable_cents"]})
            line["rate_is_provisional"] = not line["_valid"]
            if line["_valid"] and line["expected_unit_rate_cents"] is not None and line["_unit_price"] is not None and line["_unit_price"] != line["expected_unit_rate_cents"]:
                self.violation(line, "unit_price")
            if line["expected_payable_cents"] is not None and line["_billed_total"] is not None and line["expected_payable_cents"] != line["_billed_total"]:
                self.violation(line, "line_amount")
            if line["expected_payable_cents"] is None and not line["uncertainty"]:
                self.uncertain(line, "expected_payable_unresolved")
            line["decision"] = "erroneous" if line["violations"] else "review" if line["expected_payable_cents"] is None or line["uncertainty"] else "correct"
            line["source_clauses"] = sorted({source["section"] for rule in self.ref["rules"] if rule["id"] in line["rules_considered"] for source in rule["source"]})

        invoices = []
        for index, header in enumerate(headers):
            children = [r for r in lines if r["invoice_id"] == header.get("invoice_id")]
            violations = set(v for r in children for v in r["violations"])
            uncertainty = set(v for r in children for v in r["uncertainty"])
            if len(by_invoice[header.get("invoice_id")]) > 1 or not header.get("invoice_id"):
                violations.add("invoice_identifier")
                uncertainty.add("invoice_identifier_join_ambiguous")
            if header.get("contract_number") != self.contract["contract_number"]:
                violations.add("contract_number")
            if not children:
                uncertainty.add("no_invoice_lines")
            expected = sum(r["expected_payable_cents"] for r in children) if children and len(by_invoice[header.get("invoice_id")]) == 1 and all(r["expected_payable_cents"] is not None for r in children) else None
            billed = integer(header.get("invoice_total_cents"))
            if billed is None:
                violations.add("monetary_format")
            if children and all(r["_billed_total"] is not None for r in children) and billed is not None and sum(r["_billed_total"] for r in children) != billed:
                violations.add("invoice_arithmetic")
            if expected is not None and billed is not None and expected != billed:
                violations.add("invoice_amount")
            invoices.append({"invoice_id": header.get("invoice_id"), "invoice_record_index": index + 1,
                             "original": header, "expected_total_cents": expected, "billed_total_cents": billed,
                             "known_violation": bool(violations), "violations": sorted(violations), "uncertainty": sorted(uncertainty),
                             "decision": "erroneous" if violations else "review" if uncertainty or expected is None else "correct",
                             "requires_review": bool(uncertainty) or expected is None,
                             "line_record_keys": [r["record_key"] for r in children], "confidence": None})
        return {"invoices": serial(invoices), "lines": serial(lines)}

    def history(self, lines):
        # Interval totals preserve uncertain membership and incompatible quantity units.
        for service in self.discounts:
            relevant = [r for r in lines if service in r["_candidates"] and (r["_date"] is None or self.start <= r["_date"] <= self.end)]
            dated = sorted([r for r in relevant if r["_date"] and r["_order_valid"]], key=lambda r: (r["_date"], str(r["line_id"]), r["record_key"]))
            undated = [r for r in relevant if r["_date"] is None or not r["_order_valid"]]
            lower, upper, uncertain = Fraction(0), None if undated else Fraction(0), list(undated)
            count = 0
            for line in dated:
                if line["matched_service"] == service:
                    line["prior_billed_usage"] = {"lower": lower, "upper": upper, "exact": lower if lower == upper else None,
                                                   "prior_dated_record_count": count, "uncertain_record_count": len(uncertain),
                                                   "uncertain_record_sample": [r["record_key"] for r in uncertain[:20]]}
                raw_qty = line["quantities"]["original_billed_quantity"]
                compatible = line["original"].get("unit_basis_as_billed") == UNITS[self.catalogue[service]["action"]["unit_basis"]]
                if line["matched_service"] == service and raw_qty is not None and compatible:
                    lower += raw_qty
                else:
                    uncertain.append(line)
                if raw_qty is None or not compatible:
                    upper = None
                elif upper is not None:
                    upper += raw_qty
                count += 1

    def price(self, line, lines):
        service = line["matched_service"]
        rate = self.catalogue[service]["action"]["base_rate_cents"]
        line["calculation_steps"].append({"stage": "base_rate", "result_cents": rate})
        for bundle in self.by_kind["bundle"]:
            if service not in bundle["applies_to"]["services"]:
                continue
            self.use(line, bundle)
            other = next(s for s in bundle["applies_to"]["services"] if s != service)
            present, related = self.presence(line, other, lines)
            if present:
                rate = bundle["action"]["rates_cents"][service]
                self.use(line, bundle, True)
                line["calculation_steps"].append({"stage": "bundle_substitution", "result_cents": rate, "rule_id": bundle["id"], "related_record_keys": [r["record_key"] for r in related]})
            elif present is None:
                self.uncertain(line, "bundle_eligibility_uncertain", related)
                rate = None
        for kind, stage in (("facility_scope", "facility_multiplier"), ("plan_scope", "plan_tier_multiplier")):
            rule = self.by_kind[kind][0]
            self.use(line, rule)
            mult = rule["action"]["multiplier"]
            if rate is not None:
                rate = half_up(Fraction(rate * mult["numerator"], mult["denominator"]))
            line["calculation_steps"].append({"stage": stage, "multiplier": mult, "result_cents": rate})
        premium = self.single["threshold_premium"].get(service)
        if premium:
            self.use(line, premium)
            delivered = line["quantities"]["delivered_quantity"]
            applies = delivered > premium["condition"]["threshold"]["value"] if delivered is not None else None
            line["premium_eligible"] = applies
            if applies is None:
                self.uncertain(line, "premium_eligibility_uncertain")
                rate = None
            elif applies:
                rate = self.adjust(line, rate, premium, "threshold_premium")
        weekend = self.single["weekend_uplift"].get(service)
        if weekend:
            self.use(line, weekend)
            if line["_date"] is None:
                self.uncertain(line, "weekend_eligibility_uncertain")
                rate = None
            elif line["_date"].weekday() >= 5:
                rate = self.adjust(line, rate, weekend, "weekend_uplift")
        tiers = self.discounts.get(service)
        if tiers:
            for tier in tiers:
                self.use(line, tier)
            usage = line.get("prior_billed_usage", {"lower": 0, "upper": None})
            def select(value):
                applicable = [r for r in tiers if value is None or value > r["condition"]["threshold"]["value"]]
                return max(applicable, key=lambda r: r["action"]["percent"], default=None)
            lowest, highest = select(usage["lower"]), select(usage["upper"])
            if lowest != highest:
                self.uncertain(line, "volume_discount_uncertain")
                rate = None
            elif lowest:
                rate = self.adjust(line, rate, lowest, "cumulative_volume_discount")
        line["expected_unit_rate_cents"] = rate
        for kind in ("rounding", "adjustment_order", "line_calculation"):
            for rule in self.by_kind[kind]:
                self.use(line, rule)

    def adjust(self, line, rate, rule, stage):
        self.use(line, rule, True)
        mult = rule["action"]["multiplier"]
        output = half_up(Fraction(rate * mult["numerator"], mult["denominator"])) if rate is not None else None
        line["calculation_steps"].append({"stage": stage, "input_cents": rate, "multiplier": mult, "result_cents": output, "rounding": "half_up_cent", "rule_id": rule["id"]})
        return output
