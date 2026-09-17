import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from contract_extractor.extract import DEFAULT_CONTRACT, ROOT, extract
from contract_extractor.policies import DEFAULT_POLICY
from contract_extractor.validate_line_ids import inspect_ids, validate


class ApprovedPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = extract(policy_path=None)
        cls.result = extract()

    def rules(self, *kinds):
        return [r for r in self.result["rules"] if r["kind"] in kinds]

    def test_resolution_retains_contract_ambiguities_and_evidence(self):
        self.assertEqual(self.result["status"], "extracted_with_assumptions")
        self.assertTrue(self.result["ready_for_engine"])
        self.assertFalse(self.raw["ready_for_engine"])
        self.assertEqual(self.result["coverage"], self.raw["coverage"])
        for raw, resolved in zip(self.raw["rules"], self.result["rules"]):
            self.assertEqual(raw["source"], resolved["source"])
            self.assertFalse(resolved["uncertainty"]["questions"])
            if raw["uncertainty"]["questions"]:
                self.assertEqual(resolved["uncertainty"]["contract_ambiguities"], raw["uncertainty"]["questions"])
                self.assertEqual(resolved["uncertainty"]["status"], "implementation_convention")
                self.assertTrue(resolved["uncertainty"]["policy_references"])

    def test_exclusions_are_inclusive_patient_scoped_and_not_a_discount(self):
        for rule in self.rules("exclusion_window"):
            self.assertEqual(rule["condition"]["operator"], "<=")
            self.assertTrue(rule["condition"]["same_patient"])
            self.assertEqual(rule["condition"]["direction"], "both")
            self.assertEqual(rule["scope"]["group_by"], ["contract_number", "patient_id"])
            self.assertTrue(rule["scope"]["across_invoices"])
            self.assertEqual(rule["action"]["type"], "not_billable")
            self.assertEqual(rule["action"]["expected_payable_cents"], 0)
            self.assertEqual(rule["action"]["target_service"], rule["applies_to"]["services"][0])
            self.assertNotEqual(rule["action"]["target_service"], rule["condition"]["trigger_service"])

    def test_cumulative_uses_original_billed_history_and_lexical_order(self):
        for rule in self.rules("volume_discount", "cumulative_counting", "discount_grouping"):
            counting = rule["scope"]["counting"] if rule["kind"] == "volume_discount" else rule["action"]
            self.assertEqual(counting["quantity"], "original_billed_quantity")
            self.assertTrue(counting["include_duplicate_units"])
            self.assertTrue(counting["include_disallowed_units"])
            self.assertFalse(counting["subtract_rejected_units"])
            self.assertTrue(counting["exclude_current_line"])
            self.assertEqual(counting["identifier_comparison"], "lexical")
            self.assertEqual(counting["sort_by"], ["service_date ASC", "line_id ASC"])
        self.assertEqual(self.rules("line_ordering")[0]["action"]["identifier_comparison"], "lexical")

    def test_corrections_preserve_originals_and_review_conflicts(self):
        controls = self.result["implementation_policy"]["decisions"]["corrections"]
        self.assertTrue(controls["preserve_original_invoice_lines"])
        self.assertTrue(controls["preserve_original_billed_amounts"])
        self.assertIn("adjusted_contract_unit_rate", controls["pricing_compliance_basis"])
        self.assertIn("bundles_premiums_and_discounts", controls["pricing_compliance_basis"])
        self.assertEqual(controls["ambiguity_policy"]["action"], "flag_for_review_without_forcing_allocation")
        self.assertIsNone(controls["ambiguity_policy"]["expected_payable_cents_when_indeterminate"])
        self.assertIn("differing_quantities_prevent_defensible_correction", controls["ambiguity_policy"]["triggers"])

    def test_cap_policy_preserves_partial_line_payability(self):
        for rule in self.rules("daily_quantity_cap"):
            correction = rule["action"]["correction_policy"]
            self.assertEqual(correction["allocation_order"], ["line_id ASC"])
            self.assertEqual(correction["identifier_comparison"], "lexical")
            self.assertEqual(correction["retain"], "earlier_eligible_units")
            self.assertEqual(correction["exclude"], "latest_excess_units")
            self.assertEqual(correction["partly_excess_line"], "reduce_expected_payable_quantity")
            self.assertFalse(correction["exclude_whole_partly_excess_line"])
            self.assertTrue(correction["shared_controls_reference"])

    def test_duplicate_policy_has_pricing_priority_and_fallback(self):
        correction = self.rules("duplicate_billing")[0]["action"]["correction_policy"]
        self.assertEqual(correction["retain_payable_occurrences"], 1)
        self.assertEqual(correction["selection_priority"], [
            "eligible_occurrence_compliant_with_applicable_adjusted_contract_rate",
            "earliest_line_id_lexical_among_compliant_occurrences",
            "if_none_comply_and_service_remains_payable_retain_earliest_line_id_lexical_and_correct_price"])
        self.assertEqual(correction["excluded_duplicate_expected_payable_cents"], 0)
        self.assertTrue(correction["nonpayable_service_must_not_be_reinstated"])

    def test_policy_provenance_and_contract_changes_still_block(self):
        policy = self.result["implementation_policy"]
        self.assertEqual(policy["sha256"], hashlib.sha256(DEFAULT_POLICY.read_bytes()).hexdigest())
        self.assertEqual(policy["source_sha256"], hashlib.sha256((ROOT / policy["source"]).read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "changed.md"
            path.write_text(DEFAULT_CONTRACT.read_text() + "\nA new restriction applies.\n")
            result = extract(path)
            self.assertEqual(result["status"], "blocked")
            self.assertFalse(result["ready_for_engine"])
            self.assertNotIn("implementation_policy", result)


class LineIdentifierValidationTests(unittest.TestCase):
    pattern = r"^H[1-5]-L[0-9]{5}-[0-9]{2}$"

    def test_all_hospitals_and_both_formats_pass(self):
        result = validate()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["total_csv_lines"], 61211)
        self.assertEqual(result["total_jsonl_lines"], 61211)
        self.assertEqual([h["csv"]["line_count"] for h in result["hospitals"]], [11415, 14360, 11655, 10560, 13221])
        self.assertEqual(result, json.loads((ROOT / "outputs/line_id_validation.json").read_text()))

    def test_bad_padding_prefix_duplicates_and_sort_disagreement(self):
        ids = ["H1-L2-01", "H1-L10-01", "H2-L00001-01", "H1-L00001-01", "H1-L00001-01", ""]
        result = inspect_ids(ids, 1, self.pattern)
        self.assertEqual(len(result["format_exceptions"]), 4)
        self.assertEqual(result["duplicate_ids"], ["H1-L00001-01"])
        self.assertFalse(result["lexical_matches_natural"])

    def test_csv_jsonl_mismatch_requires_review_even_with_valid_format(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            for h in range(1, 6):
                with (base / f"hospital_{h}_line_items.csv").open("w", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["line_id"])
                    writer.writerow([f"H{h}-L00001-01"])
                (base / f"hospital_{h}_invoices.jsonl").write_text(json.dumps({"line_items": [{"line_id": f"H{h}-L00001-02"}]}) + "\n")
            result = validate(base)
            self.assertEqual(result["status"], "review_required")
            self.assertTrue(all(not h["csv_jsonl_line_id_multisets_match"] for h in result["hospitals"]))


if __name__ == "__main__":
    unittest.main()
