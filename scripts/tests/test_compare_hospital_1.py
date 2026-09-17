import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.compare_hospital_1 import ROOT, compare, csv_text, read_inputs


def label(invoice, erroneous, cents="100"):
    return {"invoice_id": invoice, "is_erroneous": str(erroneous),
            "error_categories": "wrong_unit_basis" if erroneous else "", "expected_total_cents": cents}


def audit(invoice, decision, cents=100, uncertain=False):
    return {"invoice_id": invoice, "decision": decision, "expected_total_cents": cents,
            "violations": ["unit_basis"] if decision == "erroneous" else [],
            "uncertainty": ["quantity_unknown"] if uncertain else []}


class ComparisonTests(unittest.TestCase):
    def test_all_decision_outcomes_and_reviews(self):
        labels = [label("TP", 1), label("TN", 0), label("FP", 0), label("FN", 1), label("RE", 1), label("RC", 0)]
        audits = [audit("TP", "erroneous"), audit("TN", "correct"), audit("FP", "erroneous"), audit("FN", "correct"),
                  audit("RE", "review", None, True), audit("RC", "review", None, True)]
        rows, summary = compare(labels, audits)
        self.assertEqual(summary["decision_comparison"], {"false_negative": 1, "false_positive": 1, "review_label_correct": 1,
                                                         "review_label_erroneous": 1, "true_negative": 1, "true_positive": 1})
        self.assertEqual(summary["evaluation"]["known_error_recall_including_abstentions"]["denominator"], 3)
        self.assertEqual(summary["evaluation"]["decision_coverage"]["numerator"], 4)

    def test_unknown_amount_is_not_zero_and_signed_difference(self):
        rows, _ = compare([label("A", 1), label("B", 1, "0"), label("C", 1, "120")],
                          [audit("A", "erroneous", None, True), audit("B", "erroneous", 0), audit("C", "erroneous", 100)])
        self.assertIsNone(rows[0]["amount_difference_cents"])
        self.assertEqual(rows[0]["decision_comparison"], "true_positive")
        self.assertTrue(rows[0]["requires_review"])
        self.assertEqual(rows[1]["amount_comparison"], "exact")
        self.assertEqual(rows[2]["amount_difference_cents"], -20)
        parsed = list(csv.DictReader(csv_text(rows).splitlines()))
        self.assertEqual(parsed[0]["audit_expected_total_cents"], "")
        self.assertEqual(parsed[1]["audit_expected_total_cents"], "0")

    def test_missing_records_are_visible_on_both_sides(self):
        rows, summary = compare([label("LABEL_ONLY", 1)], [audit("AUDIT_ONLY", "correct")])
        self.assertEqual(summary["missing_audit_ids"], ["LABEL_ONLY"])
        self.assertEqual(summary["unlabelled_audit_ids"], ["AUDIT_ONLY"])
        self.assertEqual({r["decision_comparison"] for r in rows}, {"missing_label", "missing_audit"})
        self.assertEqual(summary["evaluation"]["decision_coverage"]["numerator"], 0)

    def test_reused_headers_do_not_duplicate_scoring_or_create_amount(self):
        rows, summary = compare([label("A", 1)], [audit("A", "erroneous"), audit("A", "erroneous")])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["audit_record_count"], 2)
        self.assertIsNone(rows[0]["audit_expected_total_cents"])
        self.assertEqual(summary["evaluation"]["known_error_precision"]["numerator"], 1)

    def test_empty_and_unavailable_label_amount(self):
        rows, summary = compare([], [])
        self.assertEqual(rows, [])
        self.assertIsNone(summary["evaluation"]["known_error_precision"]["value"])
        rows, _ = compare([label("A", 0, "")], [audit("A", "correct")])
        self.assertEqual(rows[0]["amount_comparison"], "label_amount_unavailable")

    def test_real_outputs_agree_with_frozen_split_metrics(self):
        labels, audits = read_inputs(ROOT / "data/assessment/labels/hospital_1_labels.csv", ROOT / "outputs/hospital_1/invoice_audit.jsonl")
        for selected in ("development", "held_aside"):
            rows, summary = compare(labels, audits, selected)
            frozen = json.loads((ROOT / f"outputs/hospital_1/evaluation_{selected}.json").read_text())
            self.assertEqual(len(rows), frozen["labelled_invoices"])
            for key in ("decision_coverage", "known_error_precision", "known_error_recall_including_abstentions",
                        "expected_amount_coverage", "exact_expected_amount_accuracy_when_known"):
                self.assertEqual(summary["evaluation"][key], frozen[key])

    def test_rejects_duplicate_labels_and_float_money(self):
        with tempfile.TemporaryDirectory() as temp:
            labels = Path(temp) / "labels.csv"
            audits = Path(temp) / "audit.jsonl"
            labels.write_text("invoice_id,is_erroneous,error_categories,expected_total_cents\nA,0,,100\nA,0,,100\n")
            audits.write_text(json.dumps(audit("A", "correct")) + "\n")
            with self.assertRaisesRegex(ValueError, "duplicate label"):
                read_inputs(labels, audits)
            labels.write_text("invoice_id,is_erroneous,error_categories,expected_total_cents\nA,0,,100\n")
            audits.write_text(json.dumps(audit("A", "correct", 100.5)) + "\n")
            with self.assertRaisesRegex(ValueError, "integer cents"):
                read_inputs(labels, audits)

    def test_cli_from_another_directory_and_repeatable_files(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "comparison"
            command = [sys.executable, str(ROOT / "scripts/compare_hospital_1.py"), "--split", "held_aside", "--output", str(output)]
            result = subprocess.run(command, cwd=temp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            first = {p.name: p.read_bytes() for p in output.iterdir()}
            self.assertEqual(len(first), 5)
            result = subprocess.run(command, cwd=temp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir()})


if __name__ == "__main__":
    unittest.main()
