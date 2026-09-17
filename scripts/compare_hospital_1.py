"""Compare saved audit results with labels without running or changing the engine."""

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hospital_audit.data import split
from hospital_audit.evaluate import aggregate, pct, score

FIELDS = ["invoice_id", "split", "label_is_erroneous", "label_error_categories",
          "audit_decision", "decision_comparison", "requires_review", "audit_violations",
          "audit_uncertainty", "label_expected_total_cents", "audit_expected_total_cents",
          "amount_comparison", "amount_difference_cents", "audit_record_count",
          "label_ambiguity_sensitive"]


def read_inputs(label_path, audit_path):
    with Path(label_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"invoice_id", "is_erroneous", "error_categories", "expected_total_cents"}
        if not required <= set(reader.fieldnames or []):
            raise ValueError("Label CSV is missing required columns: " + ", ".join(sorted(required)))
        labels = list(reader)
    seen = set()
    for row in labels:
        invoice = row["invoice_id"]
        if not invoice or invoice in seen:
            raise ValueError(f"Missing or duplicate label invoice ID: {invoice!r}")
        seen.add(invoice)
        if row["is_erroneous"] not in ("0", "1"):
            raise ValueError(f"Invalid is_erroneous for {invoice}; expected 0 or 1")
        amount = row["expected_total_cents"]
        if amount is None or (amount != "" and not re.fullmatch(r"-?\d+", amount)):
            raise ValueError(f"Label amount must be integer cents or blank: {invoice}")
        if row["error_categories"] is None:
            raise ValueError(f"Malformed label row: {invoice}")
    audits = []
    with Path(audit_path).open(encoding="utf-8") as handle:
        for number, text in enumerate(handle, 1):
            if not text.strip():
                continue
            row = json.loads(text)
            if not isinstance(row, dict) or not isinstance(row.get("invoice_id"), str) or not row["invoice_id"]:
                raise ValueError(f"Missing audit invoice ID at JSONL row {number}")
            if row.get("decision") not in ("correct", "erroneous", "review"):
                raise ValueError(f"Invalid audit decision at row {number}")
            for key in ("violations", "uncertainty"):
                if not isinstance(row.get(key), list) or not all(isinstance(v, str) for v in row[key]):
                    raise ValueError(f"Audit {key} must be a string list at row {number}")
            if "expected_total_cents" not in row or (row["expected_total_cents"] is not None and type(row["expected_total_cents"]) is not int):
                raise ValueError(f"Audit amount must be integer cents or null at row {number}")
            if (row["decision"] == "erroneous") != bool(row["violations"]):
                raise ValueError(f"Decision and violations disagree at audit row {number}")
            if row["decision"] == "correct" and (row["uncertainty"] or row["expected_total_cents"] is None):
                raise ValueError(f"Correct audit decision has unresolved evidence at row {number}")
            if "requires_review" in row and type(row["requires_review"]) is not bool:
                raise ValueError(f"requires_review must be boolean at row {number}")
            audits.append(row)
    return labels, audits


def compare(labels, audits, selected="all"):
    keep = lambda invoice: selected == "all" or split(invoice) == selected
    labels = [r for r in labels if keep(r["invoice_id"])]
    audits = [r for r in audits if keep(r["invoice_id"])]
    label_map = {r["invoice_id"]: r for r in labels}
    predictions = aggregate(audits)
    groups = defaultdict(list)
    for row in audits:
        groups[row["invoice_id"]].append(row)
    rows = []
    for invoice in sorted(label_map.keys() | predictions.keys()):
        label, audit = label_map.get(invoice), predictions.get(invoice)
        truth = int(label["is_erroneous"]) if label else None
        decision = audit["decision"] if audit else "missing"
        # Reused header IDs have no defensible single amount or clean decision.
        if len(groups[invoice]) > 1 and decision == "correct":
            decision = "review"
            audit["decision"] = decision
        if label is None:
            outcome = "missing_label"
        elif audit is None:
            outcome = "missing_audit"
        elif decision == "review":
            outcome = "review_label_erroneous" if truth else "review_label_correct"
        else:
            outcome = {(1, "erroneous"): "true_positive", (0, "correct"): "true_negative",
                       (0, "erroneous"): "false_positive", (1, "correct"): "false_negative"}[(truth, decision)]
        expected_label = int(label["expected_total_cents"]) if label and label["expected_total_cents"] != "" else None
        expected_audit = audit["expected_total_cents"] if audit else None
        delta = None
        if label is None:
            amount_status = "missing_label"
        elif audit is None:
            amount_status = "missing_audit"
        elif expected_label is None:
            amount_status = "label_amount_unavailable"
        elif expected_audit is None:
            amount_status = "audit_amount_unresolved"
        else:
            delta = expected_audit - expected_label
            amount_status = "exact" if delta == 0 else "mismatch"
        rows.append({"invoice_id": invoice, "split": split(invoice), "label_is_erroneous": truth,
                     "label_error_categories": label["error_categories"] if label else None,
                     "audit_decision": decision, "decision_comparison": outcome,
                     "requires_review": audit is None or decision == "review" or expected_audit is None or bool(audit["uncertainty"]) or any(r.get("requires_review", False) for r in groups[invoice]),
                     "audit_violations": "|".join(audit["violations"]) if audit else "",
                     "audit_uncertainty": "|".join(audit["uncertainty"]) if audit else "prediction_missing",
                     "label_expected_total_cents": expected_label, "audit_expected_total_cents": expected_audit,
                     "amount_comparison": amount_status, "amount_difference_cents": delta,
                     "audit_record_count": len(groups[invoice]),
                     "label_ambiguity_sensitive": label.get("ambiguity_sensitive", "") if label else None})
    summary = {"split": selected, "labelled_invoices": len(labels), "audit_records": len(audits),
               "unique_audit_invoice_ids": len(predictions), "comparison_rows": len(rows),
               "decision_comparison": dict(sorted(Counter(r["decision_comparison"] for r in rows).items())),
               "amount_comparison": dict(sorted(Counter(r["amount_comparison"] for r in rows).items())),
               "requires_review": sum(r["requires_review"] for r in rows),
               "duplicate_audit_invoice_ids": sorted(i for i, rs in groups.items() if len(rs) > 1),
               "missing_audit_ids": sorted(label_map.keys() - predictions.keys()),
               "unlabelled_audit_ids": sorted(predictions.keys() - label_map.keys()),
               "evaluation": score(labels, predictions),
               "evaluation_by_split": {name: score([r for r in labels if split(r["invoice_id"]) == name], predictions)
                                       for name in ("development", "held_aside") if selected in ("all", name)}}
    return rows, summary


def csv_text(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def render(summary, rows):
    lines = [f"# Hospital 1 — labels versus audit ({summary['split']})", "",
             f"Compared {summary['labelled_invoices']} labelled invoices with {summary['audit_records']} audit records ({summary['unique_audit_invoice_ids']} distinct invoice IDs).", "",
             "## Decision comparison", "", "| Outcome | Invoices |", "|---|---:|"]
    for name in ("true_positive", "true_negative", "false_positive", "false_negative", "review_label_erroneous", "review_label_correct", "missing_audit", "missing_label"):
        lines.append(f"| {name} | {summary['decision_comparison'].get(name, 0)} |")
    lines += ["", "Review is an abstention, not a correct result or an explicit false negative. Recall still counts review-only erroneous labels as undetected. A known violation can coexist with an unresolved amount.", "",
              "## Expected-amount comparison", "", "| Outcome | Invoices |", "|---|---:|"]
    for name, count in summary["amount_comparison"].items():
        lines.append(f"| {name} | {count} |")
    lines += ["", "All amounts and differences are integer cents. Difference = audit expected total − label expected total. Blank amounts and differences are unknown, not zero. Reused audit invoice IDs are scored once, with expected amounts left unresolved.", "",
              "## Development and held-aside results", "",
              "| Split | Decision coverage | Error precision | Error recall | Amount coverage | Exact known amounts |",
              "|---|---|---|---|---|---|"]
    for name, metrics in summary["evaluation_by_split"].items():
        lines.append("| " + name + " | " + " | ".join(pct(metrics[k]) for k in (
            "decision_coverage", "known_error_precision", "known_error_recall_including_abstentions", "expected_amount_coverage", "exact_expected_amount_accuracy_when_known")) + " |")
    lines += ["", "This script compares already-produced outputs. It does not retune the engine, create a new holdout, or claim confidence calibration. Category names are shown side by side; they are not assumed to be identical vocabularies. Existing grouped/per-label category metrics are retained in summary.json.", "",
              "## Wrong decisions and amount mismatches", "",
              "| Invoice | Decision comparison | Label cents | Audit cents | Difference cents |", "|---|---|---:|---:|---:|"]
    discrepancies = [r for r in rows if r["decision_comparison"] in ("false_positive", "false_negative") or r["amount_comparison"] == "mismatch"]
    for row in discrepancies:
        lines.append("| " + " | ".join(str(row[k]) if row[k] is not None else "unknown" for k in ("invoice_id", "decision_comparison", "label_expected_total_cents", "audit_expected_total_cents", "amount_difference_cents")) + " |")
    if not discrepancies:
        lines += ["| None | | | | |"]
    lines += ["", "## Labelled errors sent to review", ""]
    reviews = [r for r in rows if r["decision_comparison"] == "review_label_erroneous"]
    lines += [f"- {r['invoice_id']}: {r['label_error_categories']}; {r['audit_uncertainty']}" for r in reviews] or ["None."]
    lines += ["", "## Files", "",
              "- `invoice_comparison.csv`: every labelled or predicted invoice, joined by ID.",
              "- `differences.csv`: wrong decisions, differing known amounts, and missing IDs only.",
              "- `review_cases.csv`: cases still requiring review, including known violations with unknown totals.",
              "- `summary.json`: counts, category metrics, split metrics and input hashes.", "",
              f"Missing audit IDs: {summary['missing_audit_ids']}. Unlabelled audit IDs: {summary['unlabelled_audit_ids']}.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, default=ROOT / "data/assessment/labels/hospital_1_labels.csv")
    parser.add_argument("--audit", type=Path, default=ROOT / "outputs/hospital_1/invoice_audit.jsonl", help="Saved invoice audit JSONL")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/hospital_1/comparison")
    parser.add_argument("--split", choices=("all", "development", "held_aside"), default="all")
    args = parser.parse_args()
    try:
        labels, audits = read_inputs(args.labels, args.audit)
        rows, summary = compare(labels, audits, args.split)
        summary["provenance"] = {"labels_sha256": hashlib.sha256(args.labels.read_bytes()).hexdigest(),
                                 "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
                                 "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        files = {"invoice_comparison.csv": csv_text(rows),
                 "differences.csv": csv_text([r for r in rows if r["decision_comparison"] in ("false_positive", "false_negative", "missing_audit", "missing_label") or r["amount_comparison"] == "mismatch"]),
                 "review_cases.csv": csv_text([r for r in rows if r["requires_review"]]),
                 "summary.json": json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                 "report.md": render(summary, rows)}
        for name in files:
            if (args.output / name).resolve() in (args.labels.resolve(), args.audit.resolve()):
                raise ValueError("Output would overwrite an input file")
        args.output.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (args.output / name).write_bytes(content.encode("utf-8"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({k: summary[k] for k in ("split", "labelled_invoices", "decision_comparison", "amount_comparison")}, indent=2))
    print("Comparison written to " + str(args.output.resolve()))


if __name__ == "__main__":
    main()
