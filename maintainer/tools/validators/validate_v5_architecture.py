#!/usr/bin/env python3
"""Budgets, local routes and schemas, without freezing requirement prose."""
from pathlib import Path
import json
import re
import sys
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
DAILY = ["stages", "discover", "lifecycle", "specify", "prototype", "context", "change-acceptance"]
# Small changes can finish from the entry alone. A reader following a longer
# task can need multiple topics; retain the former reading ceiling per route.
READING_ROUTES = {
    "discovery through specification": ("discover", "specify", "stages"),
    "specification change and handoff": ("specify", "change-acceptance", "context"),
    "prototype acceptance and handoff": ("prototype", "change-acceptance", "context"),
    "governed change": ("lifecycle", "stages", "change-acceptance", "context"),
}


def main():
    failures = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if len(skill) > 2500:
        failures.append("SKILL.md exceeds the 2500-character entry budget")
    refs = [ROOT / "references" / (name + ".md") for name in DAILY]
    lengths = {path.stem: len(path.read_text(encoding="utf-8")) for path in refs}
    total = sum(lengths.values())
    if total > 18500:
        failures.append(f"optional reference library exceeds 18500 characters: {total}")
    for topic, length in lengths.items():
        if length > 3700:
            failures.append(f"optional reference {topic} exceeds 3700 characters: {length}")
    for route, topics in READING_ROUTES.items():
        length = len(skill) + sum(lengths[topic] for topic in topics)
        if length > 13000:
            failures.append(f"entry and references for {route} exceed 13000 characters: {length}")
    for path in [ROOT / "SKILL.md", *refs]:
        raw = re.sub(chr(96)*3 + r".*?" + chr(96)*3, "", path.read_text(encoding="utf-8"), flags=re.S)
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", raw):
            target = link.split("#", 1)[0]
            if target and not re.match(r"^[a-z]+://", target, re.I) and not (path.parent / target).is_file():
                failures.append(f"{path.relative_to(ROOT)}: missing route {target}")
    for path in (ROOT / "schemas").glob("*.json"):
        try:
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            failures.append(f"{path.name}: {exc}")
    metadata = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
    if set(metadata) - {"interface", "dependencies", "policy"}:
        failures.append("agent metadata contains unsupported top-level fields")
    if metadata.get("policy", {}).get("allow_implicit_invocation") is not True:
        failures.append("implicit invocation unexpectedly disabled")
    interface = metadata.get("interface", {})
    if not 25 <= len(interface.get("short_description", "")) <= 64:
        failures.append("short_description length is outside 25..64")
    if "$ai-delivery-spec" not in interface.get("default_prompt", ""):
        failures.append("default prompt does not identify the skill")
    for issue in failures:
        print("FAIL: " + issue)
    if not failures:
        print(f"PASS: entry {len(skill)}/2500 chars; optional references {total}/18500; "
              "each topic <=3700 and bounded reading routes <=13000; links, schemas and UI metadata valid")
    return bool(failures)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
