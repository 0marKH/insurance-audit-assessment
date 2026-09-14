import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from contract_extractor.extract import DEFAULT_CONTRACT, ROOT, extract
from contract_extractor.report import report


class HospitalOneExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = DEFAULT_CONTRACT.read_text()
        cls.result = extract(policy_path=None)

    def changed(self, before, after):
        self.assertIn(before, self.original)
        with tempfile.TemporaryDirectory() as temp:
            contract = Path(temp) / "contract.md"
            contract.write_text(self.original.replace(before, after, 1))
            return extract(contract, policy_path=None)

    def rules(self, kind, result=None):
        return [r for r in (result or self.result)["rules"] if r["kind"] == kind]

    def assertBlocked(self, result, code):
        self.assertEqual(result["status"], "blocked")
        self.assertIn(code, [d["code"] for d in result["diagnostics"]])
        self.assertFalse(result["ready_for_engine"])
        self.assertTrue(all(not r["ready_for_engine"] for r in result["rules"]))

    def test_complete_baseline_inventory(self):
        self.assertEqual(self.result["diagnostics"], [])
        self.assertEqual(self.result["coverage"]["unrecognized_lines"], [])
        self.assertEqual(len(self.result["rules"]), 174)
        expected = {"service_catalogue": 108, "threshold_premium": 9, "weekend_uplift": 7,
                    "volume_discount": 11, "daily_quantity_cap": 7, "bundle": 3, "exclusion_window": 6}
        for kind, count in expected.items():
            self.assertEqual(len(self.rules(kind)), count, kind)

    def test_contract_identity_and_term(self):
        contract = self.result["contract"]
        self.assertEqual(contract["provider"], "Northgate Regional Medical Centre")
        self.assertEqual(contract["contract_number"], "INS-H1-2024-0417")
        self.assertEqual((contract["effective_from"], contract["effective_to"]), ("2024-01-01", "2025-12-31"))
        self.assertEqual(contract["currency"], "GBP")

    def test_uniform_structure_and_exact_evidence(self):
        source_lines = self.original.splitlines()
        digest = hashlib.sha256(DEFAULT_CONTRACT.read_bytes()).hexdigest()
        ids = set()
        for rule in self.result["rules"]:
            self.assertTrue({"applies_to", "condition", "action", "scope", "order", "source", "uncertainty"} <= rule.keys())
            self.assertNotIn(rule["id"], ids)
            ids.add(rule["id"])
            self.assertTrue(rule["source"])
            for source in rule["source"]:
                self.assertEqual(source["quote"], source_lines[source["line_start"] - 1])
                self.assertEqual(source["sha256"], digest)

    def test_catalogue_preserves_unusual_units_and_exact_cents(self):
        by_name = {r["action"]["service_name"]: r["action"] for r in self.rules("service_catalogue")}
        self.assertEqual(by_name["Ambulatory Pulmonary Recovery Room Occupancy"]["base_rate_cents"], 112825)
        self.assertEqual(by_name["Ambulatory Immunologic Endoscopic Procedure"]["base_rate_cents"], 607900)
        self.assertEqual(by_name["Advanced Haematology Physiotherapy Session"]["base_rate_cents"], 10150)
        self.assertEqual(by_name["Standard Paediatric Biopsy Procedure"]["unit_basis"], "per item supplied")
        self.assertEqual(by_name["Emergency Orthopaedic Consultation"]["unit_basis"], "per procedure")
        self.assertEqual(by_name["Advanced Metabolic Nursing Observation"]["daily_cap"], {"value": 6, "unit": "days"})

    def test_all_discount_tiers_against_reviewed_values(self):
        expected = {
            "Ambulatory Pulmonary Recovery Room Occupancy": [(60, 10)],
            "Comprehensive Infectious Nursing Observation": [(80, 10), (240, 25)],
            "Extended Geriatric Wound Care": [(60, 15)],
            "Intensive Gastrointestinal Isolation Room Occupancy": [(60, 12), (180, 30)],
            "Intermittent Pulmonary Rehabilitation Programme": [(120, 10)],
            "Preoperative Immunologic Endoscopic Procedure": [(80, 12), (240, 20)],
            "Standard Otolaryngologic Radiotherapy Fraction": [(60, 12), (180, 30)]}
        actual = {}
        for rule in self.rules("volume_discount"):
            actual.setdefault(rule["applies_to"]["services"][0], []).append((rule["condition"]["threshold"]["value"], rule["action"]["percent"]))
        self.assertEqual(actual, expected)

    def test_volume_boundaries_counting_and_order(self):
        for rule in self.rules("volume_discount"):
            self.assertEqual(rule["condition"]["operator"], ">")
            self.assertTrue(rule["condition"]["exclude_current_line"])
            self.assertEqual(rule["scope"]["group_by"], ["contract_number", "service"])
            self.assertEqual(rule["scope"]["patients"], "all")
            self.assertEqual(rule["scope"]["period"], "whole_contract_term")
            self.assertEqual(rule["scope"]["counting"]["sort_by"], ["service_date ASC", "line_id ASC"])
            self.assertEqual(rule["action"]["tier_selection"], "deepest_qualifying_discount")
            self.assertFalse(rule["action"]["stack_tiers"])
            self.assertEqual(rule["action"]["applies_to"], "entire_current_line")
            self.assertIn("premium_or_uplift", rule["order"]["after"])
            self.assertTrue({"2.4", "3.1", "3.2", "7.1", "7.2"} <= {s["section"] for s in rule["source"]})

    def test_premiums_use_patient_day_aggregate(self):
        for rule in self.rules("threshold_premium"):
            self.assertEqual(rule["condition"]["metric"], "aggregate_daily_quantity")
            self.assertEqual(rule["condition"]["operator"], ">")
            self.assertIn("patient_id", rule["scope"]["group_by"])
            self.assertIn("service_date", rule["scope"]["group_by"])
            self.assertTrue(rule["scope"]["across_invoices"])
            self.assertEqual(rule["action"]["applies_to"], "all_units_on_matching_lines")

    def test_weekends_do_not_use_holiday_calendar(self):
        for rule in self.rules("weekend_uplift"):
            self.assertEqual(rule["condition"]["values"], ["Saturday", "Sunday"])
        business = next(r for r in self.rules("definition") if r["action"]["type"] == "define_business_day")
        self.assertFalse(business["action"]["public_holidays_excluded"])

    def test_bundles_preserve_both_rates_and_grouping(self):
        expected = [(16400, 19150), (15175, 21500), (37500, 7050)]
        for rule, rates in zip(self.rules("bundle"), expected):
            self.assertEqual(tuple(rule["action"]["rates_cents"].values()), rates)
            self.assertTrue(rule["condition"]["same_patient"])
            self.assertTrue(rule["condition"]["same_service_day"])
            self.assertTrue(rule["scope"]["across_invoices"])
            self.assertEqual(rule["order"]["position"], 1)

    def test_caps_cross_reference_both_sections(self):
        self.assertEqual([r["action"]["maximum_billable_units"]["value"] for r in self.rules("daily_quantity_cap")], [6, 4, 12, 4, 6, 6, 8])
        for rule in self.rules("daily_quantity_cap"):
            self.assertTrue({"4", "8"} <= {s["section"] for s in rule["source"]})
            self.assertIsNone(rule["action"]["correction_policy"])

    def test_exclusions_preserve_uncertainty_without_inventing_policy(self):
        for rule in self.rules("exclusion_window"):
            self.assertEqual(rule["condition"]["direction"], "both")
            self.assertIsNone(rule["condition"]["operator"])
            self.assertIsNone(rule["condition"]["same_patient"])
            self.assertEqual(rule["action"]["target_service"], rule["applies_to"]["services"][0])
            self.assertFalse(rule["ready_for_engine"])
            self.assertEqual(len(rule["uncertainty"]["questions"]), 2)

    def test_rounding_and_pipeline(self):
        rounding = self.rules("rounding")[0]["action"]
        self.assertEqual(rounding["exact_halves"], "away_from_zero")
        self.assertEqual(rounding["timing"], "after_each_individual_step")
        self.assertEqual(self.rules("adjustment_order")[0]["action"]["stages"], ["bundle_substitution", "facility_multiplier", "plan_tier_multiplier", "premium_or_uplift", "cumulative_volume_discount", "quantity_multiplication", "invoice_summation"])

    def test_valid_dates_and_duplicate_scope(self):
        dates = self.rules("valid_service_dates")[0]["condition"]["any"]
        self.assertEqual([c["operator"] for c in dates], ["<", ">", ">"])
        self.assertEqual(dates[-1]["reference"], "invoice.invoice_date")
        duplicate = self.rules("duplicate_billing")[0]
        self.assertEqual(duplicate["scope"]["group_by"], ["contract_number", "patient_id", "service_date", "service"])
        self.assertTrue(duplicate["scope"]["across_invoices"])

    def test_values_are_extracted_not_cached(self):
        changed = self.changed("GBP 200.00", "GBP 199.99")
        self.assertEqual(changed["diagnostics"], [])
        self.assertEqual(self.rules("service_catalogue", changed)[0]["action"]["base_rate_cents"], 19999)
        changed = self.changed("60 nights | 10%", "61 nights | 11%")
        self.assertEqual(changed["diagnostics"], [])
        first = self.rules("volume_discount", changed)[0]
        self.assertEqual(first["condition"]["threshold"]["value"], 61)
        self.assertEqual(first["action"]["percent"], 11)
        self.assertEqual(first["action"]["multiplier"], {"numerator": 89, "denominator": 100})

    def test_changed_comparison_word_is_not_silently_interpreted(self):
        changed = self.changed("Cumulative utilisation exceeds", "Cumulative utilisation is at least")
        self.assertBlocked(changed, "malformed_table")

    def test_changed_prose_and_missing_definition_block(self):
        self.assertBlocked(self.changed("other than a Saturday or a Sunday", "other than a Friday or a Saturday"), "unrecognized_clause")
        clause = next(line for line in self.original.splitlines() if line.startswith("2.4 "))
        self.assertBlocked(self.changed(clause, ""), "missing_clause")

    def test_unknown_added_clause_blocks(self):
        self.assertBlocked(self.changed("## 11. Invoicing", "11.9 A new rule applies.\n\n## 11. Invoicing"), "unrecognized_clause")

    def test_conflicting_cap_blocks(self):
        self.assertBlocked(self.changed("GBP 1,301.25 | 6 days", "GBP 1,301.25 | 7 days"), "conflicting_caps")

    def test_unknown_service_and_wrong_unit_block(self):
        self.assertBlocked(self.changed("| Ambulatory Pulmonary Recovery Room Occupancy | 60 nights", "| Unknown Recovery Room | 60 nights"), "invalid_table_value")
        self.assertBlocked(self.changed("60 nights | 10%", "60 hours | 10%"), "invalid_table_value")

    def test_bad_money_duplicate_rows_and_broken_tables_block(self):
        self.assertBlocked(self.changed("GBP 200.00", "GBP 200.001"), "invalid_table_value")
        row = "| Advanced Cardiac Recovery Room Occupancy | per hour | GBP 200.00 | — |"
        self.assertBlocked(self.changed(row, row + "\n" + row), "duplicate_table_rule")
        self.assertBlocked(self.changed(row, "| Advanced Cardiac Recovery Room Occupancy | GBP 200.00 |"), "malformed_table")

    def test_metadata_conflict_and_other_hospital_block(self):
        self.assertBlocked(self.changed("**Effective to:** 31 December 2025", "**Effective to:** 30 December 2025"), "conflicting_term")
        self.assertBlocked(self.changed("**Currency:** GBP", "**Currency:** USD"), "unsupported_identity")
        self.assertBlocked(extract(ROOT / "data/assessment/contracts/hospital_2/master_services_agreement.md"), "unsupported_identity")

    def test_no_float_values_anywhere(self):
        def visit(value):
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)
        visit(self.result)

    def test_reproducible_outputs_and_no_input_mutation(self):
        self.assertEqual(self.result, extract(policy_path=None))
        self.assertEqual(report(self.result), report(extract(policy_path=None)))
        self.assertEqual(self.original, DEFAULT_CONTRACT.read_text())
        self.assertEqual(json.loads((ROOT / "outputs/hospital_1.rules.json").read_text()), extract())
        self.assertEqual((ROOT / "outputs/hospital_1.rules.md").read_text(), report(extract()))

    def test_source_snapshot_hashes(self):
        base = ROOT / "data/assessment"
        manifest = json.loads((base / "SOURCE.json").read_text())
        for name, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256((base / name).read_bytes()).hexdigest(), digest, name)

    def test_cli_exit_codes_for_uncertainty_and_partial_parse(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            command = [sys.executable, "-m", "contract_extractor", "--output", str(out)]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            completed = subprocess.run(command + ["--require-resolved"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            completed = subprocess.run(command + ["--require-resolved", "--contract-only"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            bad = Path(temp) / "bad.md"
            bad.write_text(self.original + "\nAdditional unrecognized obligation.\n")
            completed = subprocess.run(command + ["--contract", str(bad)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertEqual(json.loads((out / "hospital_1.rules.json").read_text())["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
