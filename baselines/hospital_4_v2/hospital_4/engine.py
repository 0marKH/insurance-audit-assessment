"""Reuse H1 calculation passes through an isolated, explicit Hospital 4 adapter."""
import copy
from collections import defaultdict
from fractions import Fraction

from hospital_audit.engine import Engine, UNITS
from hospital_audit.matching import Matcher
from .extract import ROOT


class ReviewedMatcher(Matcher):
    def __init__(self, catalogue):
        super().__init__(catalogue, ROOT / "policies/hospital_4_aliases.json")
        self.unsupported = {name for name,r in catalogue.items() if r["action"]["unit_basis"] not in UNITS}

    def match(self, text):
        result = super().match(text)
        if result["service"] in self.unsupported:
            result["recognized_service"] = result["service"]
            result["service"] = None
            result["method"] = "contractual_unit_unresolved"
        return result


class Hospital4Engine(Engine):
    def __init__(self, reference):
        # Do not invoke the H1 initializer or import its policy object.
        if reference["contract"]["hospital_id"] != "hospital_4" or reference["status"] != "reviewed_with_explicit_limits":
            raise ValueError("Reviewed Hospital 4 reference required")
        self.ref, self.contract = reference, reference["contract"]
        self.policy = {"line_ordering":{"expected_line_id_pattern":r"^H4-L[0-9]{5}-[0-9]{2}$"}}
        self.by_kind=defaultdict(list)
        for rule in reference["rules"]: self.by_kind[rule["kind"]].append(rule)
        self.catalogue={r["action"]["service_name"]:r for r in self.by_kind["service_catalogue"]}
        self.matcher=ReviewedMatcher(self.catalogue)
        from hospital_audit.engine import day
        self.start,self.end=day(self.contract["effective_from"]),day(self.contract["effective_to"])
        self.single={k:{r["applies_to"]["services"][0]:r for r in self.by_kind[k]} for k in
                     ("threshold_premium","weekend_uplift","daily_quantity_cap","exclusion_window")}
        self.discounts=defaultdict(list)
        for r in self.by_kind["volume_discount"]:self.discounts[r["applies_to"]["services"][0]].append(r)

    def history(self, lines):
        super().history(lines)
        # Contract-wide billed usage is a working upper bound, not an adopted
        # H4 discount population. Zero covers plausible narrower/reset scopes.
        for line in lines:
            if "prior_billed_usage" in line:
                usage=line["prior_billed_usage"]
                usage["contract_wide_lower_scenario"]=usage["lower"]
                usage["lower"]=0
                usage["exact"]=0 if usage["upper"] == 0 else None
                usage["scope_uncertain"]=True

    def presence(self, line, service, lines, window=0):
        if window == 0: return super().presence(line,service,lines,window)
        possible=[]
        for other in self.context[service]:
            if other is line or not self.patient_possible(line,other):continue
            distance=abs((line["_date"]-other["_date"]).days) if line["_date"] and other["_date"] else None
            if distance is not None and distance>window:continue
            if (distance is not None and distance<=window and other["matched_service"]==service and other["_qty"] is not None
                and line["_patient"] and other["_patient"]==line["_patient"]):return True,[other]
            possible.append(other)
        return (None,possible) if possible else (False,[])

    def audit(self, headers, records):
        # The frozen base audit has exactly one hardcoded H1 header check. This
        # private compatibility translation affects that check only. Contract
        # number, grouping, service rules and public originals remain H4.
        translated=copy.deepcopy(headers)
        for h in translated:
            if h.get("hospital_id")=="H4":h["hospital_id"]="H1"
            else:h["hospital_id"]="INVALID_H4_CONTEXT"
        result=super().audit(translated,records)
        grouped=defaultdict(list)
        for line in result["lines"]:
            if line["matched_service"]:
                grouped[(line["patient_id"],line["original"].get("service_date"),line["matched_service"])].append(line)
            if line["match"]["method"]=="contractual_unit_unresolved":
                line["uncertainty"].append("hospital_4_contractual_unit_unresolved")
                rule=self.catalogue[line["match"]["recognized_service"]]
                line["rules_considered"].append(rule["id"])
                line["source_clauses"]=sorted({s["section"] for s in rule["source"]})
        # Accept the shared engine's result only where every eligible copy has
        # the same original and adjusted rate. Its price-aware preference then
        # necessarily equals H4's approved lexical choice. Conflicts stay open.
        for group in grouped.values():
            if len(group)<2:continue
            signatures={(l["original"].get("quantity"), l["original"].get("unit_basis_as_billed"),
                         l["original"].get("unit_price_cents"), l["original"].get("line_total_cents")) for l in group}
            exact=(len(signatures)==1 and all(not l["uncertainty"] and not l["rate_is_provisional"]
                   and l["expected_payable_cents"] is not None for l in group)
                   and len({l["expected_unit_rate_cents"] for l in group})==1
                   and len({l.get("exclusion",{}).get("applies",False) for l in group})==1)
            if exact:
                eligible=[l for l in group if l.get("exclusion",{}).get("applies",False) is False]
                retained=min(eligible,key=lambda l:l["line_id"]) if eligible else None
                for line in group:
                    if retained:
                        assert line["retained_record_key"]==retained["record_key"]
                    line["duplicate_resolution"]={"policy":"exact_copy_lexical_retention",
                        "approval":self.ref["policy"]["approval_prompt"],
                        "group_line_ids":sorted(l["line_id"] for l in group),
                        "retained_line_id":retained["line_id"] if retained else None,
                        "all_copies_independently_excluded":not eligible}
                continue
            for line in group:
                line["expected_payable_cents"]=None
                line["quantities"]["expected_payable_quantity"]=None
                line.pop("retained_record_key",None)
                line["violations"]=[v for v in line["violations"] if v != "line_amount"]
                line["calculation_steps"]=[s for s in line["calculation_steps"] if s["stage"] not in ("nonpayable_charge","quantity_multiplication")]
                line["uncertainty"].append("hospital_4_duplicate_conflict_requires_review")
                if "duplicate_billing" not in line["violations"]:line["violations"].append("duplicate_billing")
                line["decision"]="erroneous"
        by_invoice=defaultdict(list)
        for line in result["lines"]:
            by_invoice[line["invoice_id"]].append(line)
            line["amount_assumptions"]=[]
            line["quantities"]["delivered_quantity_basis"]="inferred_from_original_billing_and_duplicate_context; not independent delivery evidence"
            payable=line["quantities"]["expected_payable_quantity"]
            if "daily_cap" in line["violations"] and payable is not None and Fraction(str(payable))>0:
                line["amount_assumptions"].append("cap_quantity_is_reimbursable_estimate")
                line["cap_evidence"]={"violation_status":"confirmed_from_billed_quantity",
                    "corrected_amount_status":"assumption_dependent", "actual_delivered_quantity_established":False,
                    "contractual_cap":self.single["daily_quantity_cap"][line["matched_service"]]["action"]["maximum_billable_units"]["value"],
                    "explanation":"Cap limits reimbursement; it does not establish the actual delivered quantity. Payable quantity is an approved estimate."}
            self.amount_evidence(line,"expected_payable_cents")
        for header,invoice in zip(headers,result["invoices"]):
            invoice["original"]=copy.deepcopy(header)
            children=by_invoice[invoice["invoice_id"]]
            invoice["uncertainty"]=sorted(set(invoice["uncertainty"])|{u for l in children for u in l["uncertainty"]})
            invoice["violations"]=sorted(set(invoice["violations"])|{v for l in children for v in l["violations"]})
            if any(l["expected_payable_cents"] is None for l in children):invoice["expected_total_cents"]=None
            invoice["requires_review"]=bool(invoice["uncertainty"]) or invoice["expected_total_cents"] is None
            if invoice["expected_total_cents"] is None:
                invoice["violations"]=[v for v in invoice["violations"] if v not in ("invoice_amount", "line_amount")]
                if any("line_amount" in l["violations"] for l in children): invoice["violations"].append("line_amount")
                invoice["violations"]=sorted(invoice["violations"])
            invoice["known_violation"]=bool(invoice["violations"])
            invoice["decision"]="erroneous" if invoice["known_violation"] else "review" if invoice["requires_review"] else "correct"
            invoice["amount_assumptions"]=sorted({a for l in children for a in l["amount_assumptions"]})
            invoice["amount_assumption_line_ids"]=[l["line_id"] for l in children if l["amount_assumptions"]]
            self.amount_evidence(invoice,"expected_total_cents")
        return result

    @staticmethod
    def amount_evidence(row, field):
        row["expected_amount_status"]=("unresolved" if row[field] is None else
            "assumption_dependent" if row["amount_assumptions"] else "determined_under_reviewed_policies")
        row["amount_dependent_violations"]=[v for v in row["violations"] if row["amount_assumptions"] and v in ("line_amount","invoice_amount")]
        row["confirmed_violations"]=[v for v in row["violations"] if v not in row["amount_dependent_violations"]]
