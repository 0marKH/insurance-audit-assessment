import unittest

from hospital_audit.evaluate import aggregate, score


class EvaluationTests(unittest.TestCase):
    def test_review_is_not_correct_and_amount_accuracy_is_conditional(self):
        labels = [{"invoice_id": "A", "is_erroneous": "1", "error_categories": "wrong_unit_basis", "expected_total_cents": "100"},
                  {"invoice_id": "B", "is_erroneous": "0", "error_categories": "", "expected_total_cents": "200"},
                  {"invoice_id": "C", "is_erroneous": "1", "error_categories": "unit_price_mismatch", "expected_total_cents": "300"}]
        pred = {"A": {"decision": "erroneous", "violations": ["unit_basis"], "uncertainty": ["quantity_uncertain"], "expected_total_cents": None},
                "B": {"decision": "correct", "violations": [], "uncertainty": [], "expected_total_cents": 200}}
        result = score(labels, pred)
        self.assertEqual(result["known_error_recall_including_abstentions"]["value"], .5)
        self.assertEqual(result["decision_coverage"]["numerator"], 2)
        self.assertEqual(result["expected_amount_coverage"]["numerator"], 1)
        self.assertEqual(result["exact_expected_amount_accuracy_when_known"]["denominator"], 1)
        self.assertEqual(result["confusion"]["erroneous_review"], 1)
        self.assertEqual(result["grouped_category_detection"]["unit_basis"]["true_positive"], 1)

    def test_reused_invoice_identifier_is_not_double_scored(self):
        row = {"invoice_id": "A", "violations": ["invoice_identifier"], "uncertainty": ["join"], "decision": "erroneous", "expected_total_cents": 100}
        result = aggregate([row, row])
        self.assertEqual(len(result), 1)
        self.assertIsNone(result["A"]["expected_total_cents"])

    def test_empty_denominators_are_not_perfect_scores(self):
        result = score([], {})
        self.assertIsNone(result["known_error_precision"]["value"])
        self.assertIsNone(result["exact_expected_amount_accuracy_when_known"]["value"])


if __name__ == "__main__":
    unittest.main()
