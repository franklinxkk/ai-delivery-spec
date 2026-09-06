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


def main():
    failures = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if len(skill) > 2500:
        failures.append("SKILL.md exceeds the 2500-character entry budget")
    refs = [ROOT / "references" / (name + ".md") for name in DAILY]
    total = sum(len(p.read_text(encoding="utf-8")) for p in refs)
    if total > 13000:
        failures.append("daily references exceed the 13000-character combined budget")
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
        print(f"PASS: entry {len(skill)}/2500 chars; daily references {total}/13000; routes, schemas and UI metadata valid")
    return bool(failures)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
