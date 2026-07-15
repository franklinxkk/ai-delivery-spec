#!/usr/bin/env python3
"""Run deterministic, token-free domain contract fixtures.

This verifies that each declared scenario invariant is present in its referenced
domain pack. It is a contract test, not a fresh-agent behavioral evaluation,
expert review, customer acceptance, or production proof.
"""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "maintainer" / "evals" / "domain-fixtures.yaml"


def main() -> int:
    catalog = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []
    per_domain: dict[str, list[dict]] = {}

    for fixture in catalog.get("fixtures", []):
        fixture_id = fixture.get("id", "<missing>")
        domain = fixture.get("domain", "<missing>")
        source = ROOT / str(fixture.get("source", ""))
        per_domain.setdefault(domain, []).append(fixture)
        if not source.exists():
            failures.append(f"{fixture_id} source is missing: {source}")
            continue
        assertions = fixture.get("contract_assertions", {})
        required = assertions.get("must_include", [])
        alternatives = assertions.get("must_include_one_of", [])
        forbidden = assertions.get("must_not_include", [])
        if not required or fixture.get("status") != "passed":
            failures.append(f"{fixture_id} must declare passed contract assertions")
            continue
        text = source.read_text(encoding="utf-8").lower()
        for phrase in required:
            if phrase.lower() not in text:
                failures.append(f"{fixture_id} missing required invariant: {phrase!r}")
        for group in alternatives:
            if not isinstance(group, list) or not group or not any(term.lower() in text for term in group):
                failures.append(f"{fixture_id} missing every alternative in: {group!r}")
        for phrase in forbidden:
            if phrase.lower() in text:
                failures.append(f"{fixture_id} contains forbidden claim: {phrase!r}")

    for domain, fixtures in per_domain.items():
        if len(fixtures) < 2:
            failures.append(f"{domain} needs at least two contract fixtures")
        types = {fixture.get("type") for fixture in fixtures}
        if len(types) < 2:
            failures.append(f"{domain} fixtures need at least two risk/behavior types")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    count = sum(len(items) for items in per_domain.values())
    print(
        "PASS: token-free domain contract regression covers "
        f"{len(per_domain)} packs and {count} scenario invariants; "
        "no behavioral/expert/production claim is implied"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
