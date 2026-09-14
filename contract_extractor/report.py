"""Readable review document generated from the same rules as the JSON output."""

import json
from collections import defaultdict


def describe(value):
    if isinstance(value, dict):
        return "; ".join(f"{k.replace('_', ' ')}: {describe(v)}" for k, v in value.items())
    if isinstance(value, list):
        return ", ".join(describe(v) for v in value) or "none"
    if value is None:
        return "unspecified"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def report(result):
    contract, coverage = result["contract"], result["coverage"]
    lines = ["# Hospital 1 — extracted contract rules", "",
             f"**{contract.get('provider', 'Unknown provider')}** · {contract.get('contract_number', 'Unknown contract')}", "",
             f"Term: {contract.get('effective_from', '?')} through {contract.get('effective_to', '?')}. Currency: {contract.get('currency', '?')}. All amounts below are integer cents.", "",
             f"Status: **{result['status']}**. Full contract ready for engine: **{str(result['ready_for_engine']).lower()}**.", "",
             f"{len(result['rules'])} rules. {coverage['recognized_lines']}/{coverage['nonempty_lines']} nonempty source lines recognized. This is parser coverage, not measured semantic accuracy or invoice-audit performance.", "",
             "The extractor uses reviewed Hospital 1 prose templates and typed table parsing. It makes no AI or network calls. Rule interpretations are development-time readings of the cited text.", "",
             "## Rule inventory", "", "| Kind | Count |", "|---|---:|"]
    lines += [f"| {kind.replace('_', ' ')} | {count} |" for kind, count in coverage["rules_by_kind"].items()]
    lines += ["", "## Questions to resolve before the engine", ""]
    questions = defaultdict(list)
    for rule in result["rules"]:
        for question in rule["uncertainty"]["questions"]:
            questions[question].append(rule["id"])
    for question, ids in questions.items():
        lines += [f"- {question} ({', '.join(ids)})"]
    if not questions:
        lines += ["No unresolved policy decisions. Contract ambiguities remain documented below with the user-approved assumptions. Case-specific conflicting evidence must still be flagged for review."]
    if "implementation_policy" in result:
        policy = result["implementation_policy"]
        lines += ["", "## Implementation conventions", "", f"Policy: {policy['document']}. Authority: {policy['authority']}. User decision source: {policy['source']}.", ""]
        for name, decision in policy["decisions"].items():
            lines += [f"- **{name.replace('_', ' ')}:** {decision['interpretation']}"]
        lines += ["", "Original invoice lines and billed amounts remain immutable. Corrections affect calculated expected payables only; no invoice calculations have been performed in this milestone."]
    if result["diagnostics"]:
        lines += ["", "## Blocking extraction diagnostics", "", "```json", json.dumps(result["diagnostics"], indent=2), "```"]
    lines += ["", "## All rules", "", "Each entry follows Applies to → Condition → Action → Scope → Order → Source → Uncertainty.", ""]
    for rule in result["rules"]:
        lines += [f"### {rule['id']} · {rule['kind'].replace('_', ' ')}", ""]
        for key in ("applies_to", "condition", "action", "scope", "order"):
            lines += [f"**{key.replace('_', ' ').capitalize()}:** {describe(rule[key])}", ""]
        lines += ["**Source:**", ""]
        for source in rule["source"]:
            lines += [f"- {source['document']} · §{source['section']} · line {source['line_start']}: {source['quote']}"]
        lines += ["", f"**Uncertainty:** {rule['uncertainty']['status']}. {rule['uncertainty']['interpretation']}", ""]
        lines += [f"- {question}" for question in rule["uncertainty"]["questions"]]
        if rule["uncertainty"].get("policy_references"):
            lines += ["**Policy references:** " + ", ".join(rule["uncertainty"]["policy_references"]), ""]
        for ambiguity in rule["uncertainty"].get("contract_ambiguities", []):
            lines += [f"- Contract ambiguity resolved by convention: {ambiguity}"]
        if rule["uncertainty"].get("contract_ambiguities"):
            lines += [""]
        if rule["uncertainty"]["questions"]:
            lines += [""]
    lines += ["## Provenance", "", f"Source SHA-256: `{result['document']['sha256']}`", "",
              f"Reviewed grammar SHA-256: `{result['extractor']['profile_sha256']}`", "",
              "The Markdown and JSON outputs are deterministic. The source snapshot and its upstream commit are recorded in data/assessment/SOURCE.json.", ""]
    return "\n".join(lines)
