import copy
import unittest
from fractions import Fraction

from contract_extractor.extract import extract
from hospital_audit.engine import Engine, allocate_cap, half_up
from hospital_audit.matching import Matcher

PULM = "Ambulatory Pulmonary Recovery Room Occupancy"
PREMIUM = "Ambulatory Ophthalmic Case Conference"
CAP = "Advanced Rheumatologic Laboratory Panel"
BUNDLE_A = "Advanced Cardiac Recovery Room Occupancy"
BUNDLE_B = "Routine Cardiac Specimen Analysis"
EXCLUDED = "Advanced Metabolic Anaesthesia Administration"
TRIGGER = "Standard Endocrine Endoscopic Procedure"


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = extract()

    def header(self, invoice="I1", patient="P1", **changes):
        return {"invoice_id": invoice, "hospital_id": "H1", "contract_number": "INS-H1-2024-0417",
                "invoice_date": "2024-12-31", "patient_id": patient, "facility_code": "F-MAIN",
                "plan_tier": "GOLD", "invoice_total_cents": "0", **changes}

    def line(self, service, qty=1, invoice="I1", dt="2024-01-01", number=1, price=None, **changes):
        from hospital_audit.engine import UNITS
        rule = next(r for r in self.reference["rules"] if r["kind"] == "service_catalogue" and r["action"]["service_name"] == service)
        rate = price if price is not None else rule["action"]["base_rate_cents"]
        return {"line_id": f"H1-L{number:05d}-01", "invoice_id": invoice, "line_no": "1",
                "service_date": dt, "description": service, "quantity": str(qty),
                "unit_basis_as_billed": UNITS[rule["action"]["unit_basis"]],
                "unit_price_cents": str(rate), "line_total_cents": str(half_up(Fraction(str(qty)) * rate)), **changes}

    def run_audit(self, lines, headers=None, reference=None):
        headers = headers or [self.header()]
        headers = copy.deepcopy(headers)
        for h in headers:
            h["invoice_total_cents"] = str(sum(int(r["line_total_cents"]) for r in lines if r["invoice_id"] == h["invoice_id"]))
        return Engine(reference or self.reference).audit(headers, lines)

    def test_half_up_exact_including_negative_halves(self):
        self.assertEqual([half_up(Fraction(n, 2)) for n in [1, 3, -1, -3]], [1, 2, -1, -2])
        self.assertEqual(half_up(Fraction(1249, 100)), 12)

    def test_premium_boundary_and_all_units(self):
        for qty, expected in [(6, 6 * 16925), (7, 7 * 20310)]:
            row = self.run_audit([self.line(PREMIUM, qty)])['lines'][0]
            self.assertEqual(row["expected_payable_cents"], expected)
            self.assertEqual(row["premium_eligible"], qty > 6)

    def test_round_after_each_step_not_at_the_end(self):
        reference = copy.deepcopy(self.reference)
        # Controlled fixture overlays two supported adjustments on a service to
        # distinguish rounding at each step from rounding the combined multiplier.
        catalogue = next(r for r in reference["rules"] if r["kind"] == "service_catalogue" and r["action"]["service_name"] == PREMIUM)
        catalogue["action"]["base_rate_cents"] = 5
        premium = next(r for r in reference["rules"] if r["kind"] == "threshold_premium" and r["applies_to"]["services"] == [PREMIUM])
        premium["action"]["multiplier"] = {"numerator": 110, "denominator": 100}
        discount = copy.deepcopy(next(r for r in reference["rules"] if r["kind"] == "volume_discount"))
        discount.update(id="TEST-DISCOUNT", applies_to={"services": [PREMIUM]})
        discount["condition"]["threshold"]["value"] = 0
        reference["rules"].append(discount)
        rows = [self.line(PREMIUM, 1, dt="2024-01-01"), self.line(PREMIUM, 7, dt="2024-01-02", number=2)]
        # 5 * 1.1 -> 6; 6*.75 -> 5 vs 5*1.1*.75 -> 4.
        discount["action"].update(percent=25, multiplier={"numerator": 75, "denominator": 100})
        result = self.run_audit(rows, reference=reference)["lines"][1]
        self.assertEqual(result["expected_unit_rate_cents"], 5)
        self.assertEqual(result["expected_payable_cents"], 35)

    def test_volume_prior_usage_equality_crossing_and_same_date_order(self):
        rows = [self.line(PULM, 60, number=1), self.line(PULM, 2, invoice="I2", number=2),
                self.line(PULM, 1, invoice="I3", number=3)]
        result = self.run_audit(list(reversed(rows)), [self.header(), self.header("I2", "P2"), self.header("I3", "P3")])
        by_id = {r["line_id"]: r for r in result["lines"]}
        self.assertEqual(by_id[rows[1]["line_id"]]["expected_unit_rate_cents"], 112825)
        self.assertEqual(by_id[rows[2]["line_id"]]["expected_unit_rate_cents"], 101543)
        self.assertEqual(by_id[rows[2]["line_id"]]["prior_billed_usage"]["exact"], 62)

    def test_cross_invoice_bundle_and_wrong_printed_contract(self):
        result = self.run_audit([self.line(BUNDLE_A, invoice="I1"), self.line(BUNDLE_B, invoice="I2", number=2)],
                                [self.header(), self.header("I2", contract_number="WRONG")])
        self.assertEqual([r["expected_payable_cents"] for r in result["lines"]], [16400, 19150])
        self.assertIn("contract_number", result["invoices"][1]["violations"])

    def test_exclusions_both_directions_boundary_and_only_first_service(self):
        for dt, excluded in [("2024-01-01", True), ("2024-01-15", True), ("2024-01-16", False)]:
            result = self.run_audit([self.line(EXCLUDED, dt="2024-01-08"), self.line(TRIGGER, invoice="I2", dt=dt, number=2)], [self.header(), self.header("I2")])
            self.assertEqual(result["lines"][0]["expected_payable_cents"], 0 if excluded else 9200)
            self.assertEqual(result["lines"][1]["expected_payable_cents"], 124450)
        different_patient = self.run_audit([self.line(EXCLUDED), self.line(TRIGGER, invoice="I2", number=2)], [self.header(), self.header("I2", "P2")])
        self.assertEqual(different_patient["lines"][0]["expected_payable_cents"], 9200)

    def test_duplicate_quantities_do_not_trigger_premium(self):
        rows = [self.line(PREMIUM, 4), self.line(PREMIUM, 4, invoice="I2", number=2)]
        result = self.run_audit(rows, [self.header(), self.header("I2")])
        self.assertEqual([r["quantities"]["delivered_quantity"] for r in result["lines"]], [4, 4])
        self.assertEqual([r["premium_eligible"] for r in result["lines"]], [False, False])
        self.assertEqual([r["expected_payable_cents"] for r in result["lines"]], [67700, 0])
        self.assertNotIn("duplicate_billing", result["lines"][0]["violations"])
        self.assertIn("duplicate_billing", result["lines"][1]["violations"])

    def test_duplicate_retention_uses_adjusted_price_then_cap(self):
        rows = [self.line(PREMIUM, 7, price=16925), self.line(PREMIUM, 7, invoice="I2", number=2, price=20310)]
        result = self.run_audit(rows, [self.header(), self.header("I2")])
        self.assertEqual([r["expected_payable_cents"] for r in result["lines"]], [0, 142170])
        rows = [self.line(CAP, 6, price=14000), self.line(CAP, 6, invoice="I2", number=2)]
        result = self.run_audit(rows, [self.header(), self.header("I2")])
        self.assertEqual([r["quantities"]["expected_payable_quantity"] for r in result["lines"]], [0, 4])
        self.assertEqual([r["expected_payable_cents"] for r in result["lines"]], [0, 59100])

    def test_duplicate_none_compliant_correct_earliest_and_tie_lexically(self):
        for prices in [(14000, 15000), (14775, 14775)]:
            rows = [self.line(CAP, 2, number=2, price=prices[1]), self.line(CAP, 2, number=1, price=prices[0])]
            result = self.run_audit(rows)
            self.assertEqual([r["expected_payable_cents"] for r in result["lines"]], [0, 29550])

    def test_partial_cap_allocation(self):
        self.assertEqual(allocate_cap([Fraction(3), Fraction(3)], 4), [3, 1])
        result = self.run_audit([self.line(CAP, 6)])
        self.assertEqual(result["lines"][0]["quantities"]["expected_payable_quantity"], 4)
        self.assertEqual(result["lines"][0]["expected_payable_cents"], 59100)

    def test_conflicting_duplicate_quantities_require_review(self):
        result = self.run_audit([self.line(PREMIUM, 4), self.line(PREMIUM, 7, number=2)])
        for row in result["lines"]:
            self.assertIsNone(row["premium_eligible"])
            self.assertIsNone(row["expected_payable_cents"])
        self.assertTrue(result["invoices"][0]["known_violation"])
        self.assertIsNone(result["invoices"][0]["expected_total_cents"])

    def test_unit_mismatch_never_converts_or_becomes_zero(self):
        result = self.run_audit([self.line(PULM, 3, unit_basis_as_billed="per_day")])
        row = result["lines"][0]
        self.assertIn("unit_basis", row["violations"])
        self.assertEqual(row["quantities"]["original_billed_quantity"], 3)
        self.assertIsNone(row["expected_payable_cents"])

    def test_unit_uncertainty_propagates_to_later_volume_discount(self):
        rows = [self.line(PULM, 70, unit_basis_as_billed="per_hour"), self.line(PULM, 1, number=2, dt="2024-01-02")]
        second = self.run_audit(rows)["lines"][1]
        self.assertIn("volume_discount_uncertain", second["uncertainty"])
        self.assertIsNone(second["expected_payable_cents"])

    def test_unknown_service_propagates_bundle_exclusion_and_premium(self):
        for service, reason in [(BUNDLE_A, "bundle_eligibility_uncertain"), (EXCLUDED, "exclusion_presence_uncertain"), (PREMIUM, "premium_eligibility_uncertain")]:
            unknown = self.line(CAP, number=2, description="unrecognized mystery")
            row = self.run_audit([self.line(service), unknown])["lines"][0]
            self.assertIn(reason, row["uncertainty"])
            self.assertIsNone(row["expected_payable_cents"])

    def test_uncertain_trigger_quantity_propagates_to_exclusion_and_bundle(self):
        for target, trigger, reason in [(EXCLUDED, TRIGGER, "exclusion_presence_uncertain"), (BUNDLE_A, BUNDLE_B, "bundle_eligibility_uncertain")]:
            result = self.run_audit([self.line(target), self.line(trigger, number=2, quantity="unknown")])
            self.assertIn(reason, result["lines"][0]["uncertainty"])
            self.assertIsNone(result["lines"][0]["expected_payable_cents"])

    def test_wrong_contract_does_not_hide_cross_invoice_duplicate(self):
        result = self.run_audit([self.line(CAP), self.line(CAP, invoice="I2", number=2)],
                                [self.header(), self.header("I2", contract_number="WRONG")])
        self.assertEqual([r["expected_payable_cents"] for r in result["lines"]], [14775, 0])
        self.assertIn("duplicate_billing", result["lines"][1]["violations"])

    def test_missing_or_reused_header_keeps_join_unresolved(self):
        for headers in [[self.header("OTHER")], [self.header(), self.header()]]:
            result = self.run_audit([self.line(CAP)], headers)
            self.assertIn("record_join", result["lines"][0]["violations"])
            self.assertIsNone(result["lines"][0]["expected_payable_cents"])

    def test_interval_usage_can_resolve_deepest_tier(self):
        rows = [self.line(PULM, 70), self.line(CAP, number=2, dt="2024-01-02", description="mystery"),
                self.line(PULM, 1, number=3, dt="2024-01-03")]
        last = self.run_audit(rows)["lines"][-1]
        self.assertIsNone(last["prior_billed_usage"]["upper"])
        self.assertEqual(last["expected_unit_rate_cents"], 101543)

    def test_duplicate_billed_history_not_reduced_by_zero_payable(self):
        rows = [self.line(PULM, 31), self.line(PULM, 31, number=2), self.line(PULM, 1, number=3, dt="2024-01-02")]
        result = self.run_audit(rows)
        self.assertEqual(result["lines"][1]["expected_payable_cents"], 0)
        self.assertEqual(result["lines"][2]["prior_billed_usage"]["exact"], 62)
        self.assertEqual(result["lines"][2]["expected_unit_rate_cents"], 101543)

    def test_nonpayable_service_still_establishes_delivery(self):
        reference = copy.deepcopy(self.reference)
        exclusion = copy.deepcopy(next(r for r in reference["rules"] if r["kind"] == "exclusion_window"))
        exclusion.update(id="TEST-EXCLUSION", applies_to={"services": [PREMIUM]})
        exclusion["condition"]["trigger_service"] = TRIGGER
        reference["rules"].append(exclusion)
        result = self.run_audit([self.line(PREMIUM, 7), self.line(TRIGGER, number=2)], reference=reference)
        self.assertTrue(result["lines"][0]["premium_eligible"])
        self.assertEqual(result["lines"][0]["quantities"]["delivered_quantity"], 7)
        self.assertEqual(result["lines"][0]["expected_payable_cents"], 0)

    def test_invalid_dates_flag_without_zero_correction(self):
        result = self.run_audit([self.line(CAP, dt="2026-01-01")])
        self.assertIn("service_date", result["lines"][0]["violations"])
        self.assertIsNone(result["invoices"][0]["expected_total_cents"])

    def test_original_inputs_unchanged_and_reordering_deterministic_amounts(self):
        headers, rows = [self.header()], [self.line(CAP, 2, number=2), self.line(CAP, 2, number=1)]
        original = copy.deepcopy((headers, rows))
        first = Engine(self.reference).audit(headers, rows)
        second = Engine(self.reference).audit(headers, list(reversed(rows)))
        self.assertEqual((headers, rows), original)
        self.assertEqual({r['line_id']:r['expected_payable_cents'] for r in first['lines']}, {r['line_id']:r['expected_payable_cents'] for r in second['lines']})

    def test_known_violation_and_unknown_total_are_separate(self):
        rows = [self.line(CAP, description="unknown service")]
        result = self.run_audit(rows, [self.header(contract_number="WRONG")])
        invoice = result["invoices"][0]
        self.assertEqual(invoice["decision"], "erroneous")
        self.assertTrue(invoice["requires_review"])
        self.assertIsNone(invoice["expected_total_cents"])
        self.assertIsNone(invoice["confidence"])

    def test_matcher_refuses_ambiguous_description_and_expands_reviewed_aliases(self):
        matcher = Engine(self.reference).matcher
        self.assertEqual(matcher.match("Adv Card Recov Rm Occ /NG-1234")["service"], BUNDLE_A)
        match = matcher.match("Procedure Immun Endosc")
        self.assertIsNone(match["service"])
        self.assertEqual(len(match["candidates"]), 2)

    def test_policy_change_cannot_silently_reuse_old_semantics(self):
        reference = copy.deepcopy(self.reference)
        reference["implementation_policy"]["decisions"]["engine"]["daily_premium_quantity"] = "all_billed_units"
        with self.assertRaisesRegex(ValueError, "Unsupported policy"):
            Engine(reference)


if __name__ == "__main__":
    unittest.main()
