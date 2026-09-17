"""Description-only matching. Billed prices and units are not inputs."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Matcher:
    def __init__(self, services, alias_path=ROOT / "policies/hospital_1_aliases.json"):
        self.policy = json.loads(Path(alias_path).read_text())
        self.services = sorted(services)
        self.tokens = {name: self.normalize(name) for name in self.services}
        self.vocabulary = set().union(*self.tokens.values())

    def normalize(self, description):
        description = re.sub(self.policy["ignored_pattern"], "", description, flags=re.I)
        return frozenset(self.policy["token_aliases"].get(t, t) for t in re.findall(r"[a-z]+", description.lower()))

    def match(self, description):
        tokens = self.normalize(description)
        known = tokens & self.vocabulary
        candidates = [name for name in self.services if known and known <= self.tokens[name]]
        supported = len(candidates) == 1 and len(tokens) >= 2 and not (tokens - self.vocabulary)
        # An unknown description remains potentially relevant to every service.
        return {"service": candidates[0] if supported else None,
                "candidates": candidates or self.services,
                "method": "reviewed_tokens_unique" if supported else "review_required",
                "normalized_tokens": sorted(tokens),
                "unknown_tokens": sorted(tokens - self.vocabulary),
                "basis": "description_only; reviewed abbreviations; no prices or unit hints"}
