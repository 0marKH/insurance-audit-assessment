"""Run the Hospital 1 audit; labels are deliberately not imported here."""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from contract_extractor.extract import ROOT, extract
from .data import load, split
from .engine import Engine

OUTPUT = ROOT / "outputs/hospital_1"


def fingerprints():
    files = (list((ROOT / "hospital_audit").glob("*.py")) + list((ROOT / "contract_extractor").glob("*.py"))
             + list((ROOT / "policies").glob("hospital_1*.json")) + list((ROOT / "tests").glob("test_*.py"))
             + [ROOT / "outputs/hospital_1.rules.json", ROOT / "profiles/hospital_1.json"])
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="Recompute and compare artifacts without changing files")
    args = parser.parse_args()
    reference = json.loads((ROOT / "outputs/hospital_1.rules.json").read_text())
    if reference != extract():
        parser.error("Rule output is stale. Run python3 -m contract_extractor first.")
    headers, lines = load()
    result = Engine(reference).audit(headers, lines)
    for invoice in result["invoices"]:
        invoice["evaluation_split"] = split(invoice["invoice_id"])
    summary = {"invoice_records": len(headers), "unique_invoice_ids": len({r['invoice_id'] for r in headers}),
               "line_records": len(lines), "matched_lines": sum(bool(r["matched_service"]) for r in result["lines"]),
               "known_line_amounts": sum(r["expected_payable_cents"] is not None for r in result["lines"]),
               "known_invoice_amounts": sum(r["expected_total_cents"] is not None for r in result["invoices"]),
               "invoice_decisions": dict(Counter(r["decision"] for r in result["invoices"])),
               "line_uncertainty_reasons": dict(Counter(reason for r in result["lines"] for reason in r["uncertainty"])),
               "confidence": None, "runtime_model_dependencies": [],
               "scope": "Hospital 1 development only; not a Hospitals 2–5 submission"}
    def jsonl(rows):
        return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    files = {"line_audit.jsonl": jsonl(result["lines"]), "invoice_audit.jsonl": jsonl(result["invoices"]),
             "summary.json": json.dumps(summary, indent=2) + "\n"}
    reviews = [{"level": "line", **{k: row[k] for k in ("record_key", "line_id", "invoice_id", "matched_service", "uncertainty", "dependencies", "expected_payable_cents")}}
               for row in result["lines"] if row["uncertainty"] or row["expected_payable_cents"] is None]
    reviews += [{"level": "invoice", **{k: row[k] for k in ("invoice_id", "invoice_record_index", "uncertainty", "known_violation", "expected_total_cents")}}
                for row in result["invoices"] if row["requires_review"]]
    files["review_log.jsonl"] = jsonl(reviews)
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=["invoice_id", "invoice_record_index", "evaluation_split", "decision", "known_violation", "requires_review", "expected_total_cents", "billed_total_cents", "violations", "uncertainty"])
    writer.writeheader()
    for row in result["invoices"]:
        writer.writerow({key: "|".join(row[key]) if isinstance(row[key], list) else row[key] for key in writer.fieldnames})
    files["invoice_audit.csv"] = csv_buffer.getvalue()
    manifest = {"implementation_sha256": fingerprints(), "input_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ("data/assessment/invoices/hospital_1_invoices.csv", "data/assessment/invoices/hospital_1_line_items.csv")},
                "artifact_sha256": {name: hashlib.sha256(value.encode()).hexdigest() for name, value in files.items()},
                "labels_used_by_engine": False, "split": "sha256(invoice_id).first_8_hex_as_integer % 5 == 0 => held_aside; otherwise development"}
    files["run_manifest.json"] = json.dumps(manifest, indent=2) + "\n"
    if args.check:
        # Compare bytes, preserving CSV CRLF rather than universal-newline translation.
        stale = [name for name, content in files.items() if not (args.output / name).exists() or (args.output / name).read_bytes() != content.encode()]
        if stale:
            parser.error("Stale or missing artifacts: " + ", ".join(stale))
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (args.output / name).write_bytes(content.encode())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
