"""Label evaluation kept separate from invoice calculations and service matching."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from .__main__ import OUTPUT, fingerprints
from .data import DATA, read_csv, split

LABEL_GROUPS = {
    "pricing": {"unit_price_mismatch", "premium_omitted", "premium_incorrectly_applied", "volume_discount_omitted", "volume_discount_incorrectly_applied", "bundle_not_applied"},
    "arithmetic": {"invoice_total_mismatch", "line_total_arithmetic"},
    "dates": {"malformed_service_date", "service_date_out_of_window", "service_date_after_invoice_date"},
    "unit_basis": {"wrong_unit_basis"}, "daily_caps": {"daily_cap_exceeded"},
    "duplicate_service": {"cross_invoice_duplicate"}, "duplicate_invoice_id": {"duplicate_invoice_id"},
    "exclusions": {"exclusion_window_violation"}, "contract_identity": {"contract_number_mismatch"},
    "uncontracted_service": {"unknown_service"},
}
PREDICTED_GROUPS = {
    "pricing": {"unit_price"}, "arithmetic": {"line_arithmetic", "invoice_arithmetic"},
    "dates": {"service_date"}, "unit_basis": {"unit_basis"}, "daily_caps": {"daily_cap"},
    "duplicate_service": {"duplicate_billing"}, "duplicate_invoice_id": {"invoice_identifier"},
    "exclusions": {"exclusion_window"}, "contract_identity": {"contract_number"},
    "uncontracted_service": set(),
}


def fraction(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "value": numerator / denominator if denominator else None}


def aggregate(rows):
    """Labels have one row per invoice ID; reused headers cannot be double scored."""
    by_id = defaultdict(list)
    for row in rows:
        by_id[row["invoice_id"]].append(row)
    result = {}
    for invoice, group in by_id.items():
        violations = sorted({v for r in group for v in r["violations"]})
        uncertainty = sorted({v for r in group for v in r["uncertainty"]})
        result[invoice] = {"decision": "erroneous" if violations else "review" if any(r["decision"] == "review" for r in group) else "correct",
                           "violations": violations, "uncertainty": uncertainty,
                           "expected_total_cents": group[0]["expected_total_cents"] if len(group) == 1 else None}
    return result


def score(labels, predictions):
    confusion, category = Counter(), defaultdict(Counter)
    paired, amounts, absolute_error = [], 0, 0
    amount_exact, amount_examples = 0, []
    reasons, error_examples = Counter(), defaultdict(list)
    for label in labels:
        pred = predictions.get(label["invoice_id"], {"decision": "review", "violations": [], "uncertainty": ["prediction_missing"], "expected_total_cents": None})
        truth = label["is_erroneous"] == "1"
        decision = pred["decision"]
        confusion[("erroneous" if truth else "correct") + "_" + decision] += 1
        categories = set(filter(None, label["error_categories"].split("|")))
        for cat in categories:
            category[cat]["labelled_invoices"] += 1
            category[cat]["known_error_detected"] += decision == "erroneous"
            category[cat]["sent_for_review_without_known_violation"] += decision == "review"
            category[cat]["incorrectly_accepted"] += decision == "correct"
        expected = pred["expected_total_cents"]
        if expected is not None and label["expected_total_cents"]:
            amounts += 1
            delta = abs(expected - int(label["expected_total_cents"]))
            absolute_error += delta
            amount_exact += delta == 0
            for cat in categories:
                category[cat]["known_expected_amounts"] += 1
                category[cat]["exact_expected_amounts"] += delta == 0
            if delta and len(amount_examples) < 5:
                amount_examples.append({"invoice_id": label["invoice_id"], "calculated_cents": expected, "label_cents": int(label["expected_total_cents"]), "categories": sorted(categories)})
        reasons.update(pred["uncertainty"])
        for reason in pred["uncertainty"]:
            if len(error_examples[reason]) < 2:
                error_examples[reason].append(label["invoice_id"])
        if (truth and decision != "erroneous") or (not truth and decision == "erroneous"):
            key = "missed_known_error" if truth else "false_positive"
            if len(error_examples[key]) < 5:
                error_examples[key].append({"invoice_id": label["invoice_id"], "decision": decision, "label_categories": sorted(categories), "violations": pred["violations"]})
        paired.append((categories, set(pred["violations"])))
    grouped = {}
    for name, actual in LABEL_GROUPS.items():
        predicted = PREDICTED_GROUPS[name]
        tp = sum(bool(a & actual) and bool(p & predicted) for a, p in paired)
        fp = sum(not (a & actual) and bool(p & predicted) for a, p in paired)
        fn = sum(bool(a & actual) and not (p & predicted) for a, p in paired)
        grouped[name] = {"true_positive": tp, "false_positive": fp, "false_negative": fn,
                         "precision": fraction(tp, tp + fp), "recall": fraction(tp, tp + fn)}
    tp, fp = confusion["erroneous_erroneous"], confusion["correct_erroneous"]
    positive = sum(r["is_erroneous"] == "1" for r in labels)
    decided = sum(value for key, value in confusion.items() if not key.endswith("_review"))
    return {"labelled_invoices": len(labels), "confusion": dict(confusion),
            "decision_coverage": fraction(decided, len(labels)), "known_error_precision": fraction(tp, tp + fp),
            "known_error_recall_including_abstentions": fraction(tp, positive),
            "accuracy_on_decided_invoices": fraction(tp + confusion["correct_correct"], decided),
            "expected_amount_coverage": fraction(amounts, len(labels)), "exact_expected_amount_accuracy_when_known": fraction(amount_exact, amounts),
            "mean_absolute_error_cents_when_known": {"numerator": absolute_error, "denominator": amounts},
            "per_label_category_invoice_detection": {k: dict(v) for k, v in sorted(category.items())},
            "grouped_category_detection": grouped, "uncertainty_reasons": dict(reasons),
            "systematic_examples": dict(error_examples), "amount_mismatch_examples": amount_examples,
            "confidence_calibration": "Not measured; no numerical confidence scores are emitted."}


def pct(metric):
    return f"{metric['value'] * 100:.2f}% ({metric['numerator']}/{metric['denominator']})" if metric['value'] is not None else "not measurable"


def render(result):
    lines = [f"# Hospital 1 evaluation — {result['split']}", "",
             "Development descriptions and labels informed implementation. Held-aside labels were reserved until the implementation freeze; all invoice records still supply cross-invoice contractual context. The split is by invoice ID, not an independent hospital or patient cohort.", "",
             "Duplicate header records are consolidated by ID for label scoring; their amount remains unresolved. Missing predictions count as review. Review is never counted as correct.", "",
             "| Measure | Result |", "|---|---:|"]
    for key in ("decision_coverage", "known_error_precision", "known_error_recall_including_abstentions", "accuracy_on_decided_invoices", "expected_amount_coverage", "exact_expected_amount_accuracy_when_known"):
        lines.append(f"| {key.replace('_', ' ')} | {pct(result[key])} |")
    mae = result["mean_absolute_error_cents_when_known"]
    lines += [f"| Mean absolute error on known amounts | {mae['numerator']}/{mae['denominator']} cents |", "",
              "Amounts are evaluated only where the engine can establish them. Conditional accuracy is not full-dataset accuracy. No numeric confidence scores or calibration claims are made.", "",
              "## Per-category invoice detection", "",
              "These rows measure whether an invoice with the given label category has any known violation. They do not claim exact identification of each injected category. Multi-label invoices appear in multiple rows.", "",
              "| Label category | Invoices | Known error detected | Review only | Incorrectly accepted | Known amounts | Exact amounts |", "|---|---:|---:|---:|---:|---:|---:|"]
    for cat, counts in result["per_label_category_invoice_detection"].items():
        lines.append("| " + cat + " | " + " | ".join(str(counts.get(k, 0)) for k in ("labelled_invoices", "known_error_detected", "sent_for_review_without_known_violation", "incorrectly_accepted", "known_expected_amounts", "exact_expected_amounts")) + " |")
    lines += ["", "## Grouped category detection", "",
              "Categories are mapped explicitly in hospital_audit/evaluate.py. Pricing groups bundles/premiums/discounts/rate errors; arithmetic groups line/invoice arithmetic. Unknown-service matching is conservatively reviewed rather than asserted as an uncontracted charge.", "",
              "| Category group | TP | FP | FN | Precision | Recall |", "|---|---:|---:|---:|---|---|"]
    for name, values in result["grouped_category_detection"].items():
        lines.append(f"| {name} | {values['true_positive']} | {values['false_positive']} | {values['false_negative']} | {pct(values['precision'])} | {pct(values['recall'])} |")
    lines += ["", "## Systematic limitations and examples", ""]
    families = {
        "Ambiguous descriptions": ["service_match_unresolved"],
        "Uncertain cross-invoice dependencies": ["volume_discount_uncertain", "bundle_eligibility_uncertain", "exclusion_presence_uncertain", "premium_eligibility_uncertain"],
        "Quantity or duplicate conflicts": ["contract_quantity_unknown_due_to_unit_mismatch", "delivered_quantity_or_duplicate_identity_uncertain", "retention_or_payable_quantity_requires_review"],
        "Malformed identity/date evidence": ["missing_or_ambiguous_invoice_join", "invalid_date_payability_requires_review"]}
    for family, reasons in families.items():
        entries = [f"{r}: {result['uncertainty_reasons'][r]} invoices (e.g. {', '.join(result['systematic_examples'].get(r, []))})" for r in reasons if r in result["uncertainty_reasons"]]
        lines += [f"- **{family}:** " + ("; ".join(entries) if entries else "No observed examples in this split.")]
    for name in ("false_positive", "missed_known_error"):
        lines += ["", f"{name.replace('_', ' ').capitalize()} examples: `{json.dumps(result['systematic_examples'].get(name, []))}`"]
    lines += ["", "Expected-amount mismatch examples: `" + json.dumps(result["amount_mismatch_examples"]) + "`", "",
              "Original billed quantities and money are unchanged. A known violation may coexist with an unknown expected total. Date defects and unit mismatches do not receive invented zero corrections.", "",
              "## Evaluation provenance", "", f"Labels SHA-256: `{result['labels_sha256']}`", "",
              f"Unlabelled prediction IDs: {result['unlabelled_prediction_ids']}. Missing labelled IDs: {result['missing_labelled_prediction_ids']}.", "",
              "See run_manifest.json for implementation, input and output hashes, and evaluation_freeze.json for the held-aside implementation freeze.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--split", choices=["development", "held_aside"], default="development")
    parser.add_argument("--freeze", action="store_true", help="Freeze implementation before opening held-aside labels; does not evaluate")
    args = parser.parse_args()
    manifest = json.loads((args.output / "run_manifest.json").read_text())
    if manifest["implementation_sha256"] != fingerprints():
        parser.error("Audit implementation changed; rerun the audit before evaluation")
    for name, digest in manifest["artifact_sha256"].items():
        if hashlib.sha256((args.output / name).read_bytes()).hexdigest() != digest:
            parser.error("Audit artifact modified: " + name)
    freeze_path = args.output / "evaluation_freeze.json"
    if args.freeze:
        freeze = {"implementation_sha256": fingerprints(), "split": manifest["split"],
                  "protocol": "Development descriptions and development labels inspected. Held-aside labels not used before this freeze. All records provide contract context; target holdout is by invoice ID, not patient or hospital."}
        if freeze_path.exists() and json.loads(freeze_path.read_text()) != freeze:
            parser.error("An earlier freeze exists. Preserve it and document any later evaluation as reused holdout.")
        freeze_path.write_text(json.dumps(freeze, indent=2) + "\n")
        print("Implementation frozen; held-aside labels have not been evaluated by this command.")
        return
    if args.split == "held_aside":
        if not freeze_path.exists() or json.loads(freeze_path.read_text())["implementation_sha256"] != fingerprints():
            parser.error("Create a matching --freeze before evaluating held-aside labels")
    rows = [json.loads(line) for line in (args.output / "invoice_audit.jsonl").read_text().splitlines()]
    predictions = aggregate(rows)
    label_path = DATA / "labels/hospital_1_labels.csv"
    # Only the selected split's label values enter scoring or reports.
    labels = [r for r in read_csv(label_path) if split(r["invoice_id"]) == args.split]
    if len({r['invoice_id'] for r in labels}) != len(labels):
        parser.error("Duplicate label IDs require review")
    result = score(labels, predictions)
    label_ids = {r["invoice_id"] for r in labels}
    result.update(split=args.split, labels_sha256=hashlib.sha256(label_path.read_bytes()).hexdigest(),
                  unlabelled_prediction_ids=sorted(i for i in predictions if split(i) == args.split and i not in label_ids),
                  missing_labelled_prediction_ids=sorted(label_ids - predictions.keys()))
    (args.output / f"evaluation_{args.split}.json").write_text(json.dumps(result, indent=2) + "\n")
    (args.output / f"evaluation_{args.split}.md").write_text(render(result))
    print(json.dumps({k: result[k] for k in ("split", "labelled_invoices", "confusion", "decision_coverage", "known_error_precision", "known_error_recall_including_abstentions", "expected_amount_coverage", "exact_expected_amount_accuracy_when_known")}, indent=2))


if __name__ == "__main__":
    main()
