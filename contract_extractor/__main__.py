import argparse
import json
import sys
from pathlib import Path

from .extract import DEFAULT_CONTRACT, ROOT, extract
from .report import report
from .policies import DEFAULT_POLICY


def main():
    parser = argparse.ArgumentParser(description="Extract Hospital 1 rules with source evidence; no AI.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT, help="Hospital 1 Markdown contract")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs", help="Directory for JSON and Markdown")
    parser.add_argument("--require-resolved", action="store_true", help="Exit 2 if any interpretation remains unresolved")
    parser.add_argument("--check", action="store_true", help="Verify committed artifacts without changing them")
    parser.add_argument("--contract-only", action="store_true", help="Omit user conventions and retain raw contractual ambiguities")
    args = parser.parse_args()
    try:
        result = extract(args.contract, policy_path=None if args.contract_only else DEFAULT_POLICY)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot extract contract: {exc}", file=sys.stderr)
        return 1
    files = {"hospital_1.rules.json": json.dumps(result, indent=2, ensure_ascii=False) + "\n",
             "hospital_1.rules.md": report(result)}
    if args.check:
        stale = [name for name, content in files.items() if not (args.output / name).is_file() or (args.output / name).read_text() != content]
        if stale:
            print("Missing or stale artifacts: " + ", ".join(stale), file=sys.stderr)
            return 1
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (args.output / name).write_text(content, encoding="utf-8")
    print(f"{result['status']}: {len(result['rules'])} rules; {result['coverage']['recognized_lines']}/{result['coverage']['nonempty_lines']} source lines recognized; {len(result['diagnostics'])} blocking diagnostics.")
    print(f"Unresolved rules: {sum(bool(r['uncertainty']['questions']) for r in result['rules'])}. Full contract ready for engine: {result['ready_for_engine']}.")
    if result["diagnostics"]:
        return 1
    return 2 if args.require_resolved and not result["ready_for_engine"] else 0


if __name__ == "__main__":
    sys.exit(main())
