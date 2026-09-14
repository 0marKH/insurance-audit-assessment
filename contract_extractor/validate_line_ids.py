"""Read-only validation of line-ID formatting and ordering in both data formats."""

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from .extract import ROOT
from .policies import DEFAULT_POLICY


def natural_key(value):
    return [(1, int(part)) if part.isdigit() else (0, part) for part in re.split(r"([0-9]+)", value)]


def inspect_ids(ids, hospital_number, pattern):
    exceptions = [{"row": i, "line_id": value} for i, value in enumerate(ids, 1)
                  if not re.fullmatch(pattern, value) or not value.startswith(f"H{hospital_number}-")]
    counts = Counter(ids)
    return {
        "line_count": len(ids),
        "format_exceptions": exceptions,
        "duplicate_ids": sorted(value for value, count in counts.items() if count > 1),
        "lexical_matches_natural": sorted(ids) == sorted(ids, key=natural_key),
    }


def validate(directory=ROOT / "data/assessment/invoices"):
    directory = Path(directory)
    pattern = json.loads(DEFAULT_POLICY.read_text())["decisions"]["line_ordering"]["expected_line_id_pattern"]
    hospitals, file_hashes = [], {}
    all_csv_ids, all_json_ids = [], []
    for hospital in range(1, 6):
        csv_path = directory / f"hospital_{hospital}_line_items.csv"
        json_path = directory / f"hospital_{hospital}_invoices.jsonl"
        with csv_path.open(newline="", encoding="utf-8") as handle:
            csv_ids = [row["line_id"] for row in csv.DictReader(handle)]
        json_ids = []
        with json_path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    json_ids.extend(row["line_id"] for row in json.loads(line)["line_items"])
        if any(not isinstance(value, str) for value in csv_ids + json_ids):
            raise ValueError("Line IDs must be text")
        for path in (csv_path, json_path):
            file_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        hospitals.append({"hospital_id": f"hospital_{hospital}",
                          "csv": inspect_ids(csv_ids, hospital, pattern),
                          "jsonl": inspect_ids(json_ids, hospital, pattern),
                          "csv_jsonl_line_id_multisets_match": Counter(csv_ids) == Counter(json_ids)})
        all_csv_ids.extend(csv_ids)
        all_json_ids.extend(json_ids)
    passed = all(h["csv_jsonl_line_id_multisets_match"] and all(
        h[fmt]["line_count"] > 0 and not h[fmt]["format_exceptions"] and
        not h[fmt]["duplicate_ids"] and h[fmt]["lexical_matches_natural"]
        for fmt in ("csv", "jsonl")) for h in hospitals)
    global_agreement = all(sorted(ids) == sorted(ids, key=natural_key) for ids in (all_csv_ids, all_json_ids))
    return {"status": "passed" if passed and global_agreement else "review_required",
            "expected_pattern": pattern, "total_csv_lines": len(all_csv_ids),
            "total_jsonl_lines": len(all_json_ids), "global_lexical_matches_natural": global_agreement,
            "hospitals": hospitals, "source_sha256": file_hashes,
            "exception_action": "Flag for review and revisit ordering only if exceptions appear; never silently switch comparison type."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "data/assessment/invoices")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/line_id_validation.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.directory)
        content = json.dumps(result, indent=2) + "\n"
        if args.check:
            if not args.output.exists() or args.output.read_text() != content:
                print("Line-ID validation artifact is missing or stale.")
                return 1
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content)
        print(f"{result['status']}: {result['total_csv_lines']} CSV and {result['total_jsonl_lines']} JSONL line IDs; all 5 hospitals.")
        return 0 if result["status"] == "passed" else 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Line-ID validation failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
