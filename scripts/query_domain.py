#!/usr/bin/env python3
"""Return one compact domain assurance record without loading the full catalog."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "domain-coverage.yaml"
SOURCE_CATALOG = ROOT / "references" / "domains" / "domain-sources.yaml"


def select_sections(raw: str, requested: list[str]) -> tuple[list[str], list[str]]:
    headings = [
        (len(match.group(1)), match.group(2).strip(), match.start())
        for match in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", raw, re.M)
    ]
    selected: list[str] = []
    missing: list[str] = []
    for name in requested:
        index = next(
            (idx for idx, (_level, title, _start) in enumerate(headings) if title.casefold() == name.casefold()),
            None,
        )
        if index is None:
            missing.append(name)
            continue
        level, _title, start = headings[index]
        end = len(raw)
        for next_level, _next_title, next_start in headings[index + 1:]:
            if next_level <= level:
                end = next_start
                break
        selected.append(raw[start:end].strip())
    return selected, missing


def main() -> int:
    # Domain records intentionally contain multilingual source titles and gaps.
    # Emit a deterministic UTF-8 stream even when a Windows host exposes a
    # narrow legacy console encoding such as cp1252.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True)
    parser.add_argument("--format", choices=["yaml", "markdown"], default="yaml")
    parser.add_argument("--section", action="append", default=[], help="Load only an exact ##/### heading; repeat as needed")
    args = parser.parse_args()

    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    sources = yaml.safe_load(SOURCE_CATALOG.read_text(encoding="utf-8"))
    item = next(
        (domain for domain in catalog.get("domains", []) if domain.get("domain_id") == args.domain),
        None,
    )
    if item is None:
        available = ", ".join(domain["domain_id"] for domain in catalog.get("domains", []))
        print(f"FAIL: unknown domain {args.domain!r}; available: {available}")
        return 1

    compact = {
        "domain_id": item["domain_id"],
        "knowledge_file": item["knowledge_file"],
        "applies_when": item.get("applies_when", []),
        "does_not_apply_when": item.get("does_not_apply_when", []),
        "maturity": item["maturity"],
        "practice_status": item["practice_status"],
        "coverage": item["coverage"],
        "evidence_refs": list(dict.fromkeys(
            evidence["location"] for evidence in item.get("evidence", [])
        )),
        "source_refs": [
            {
                "id": source["id"],
                "type": source["authority_type"],
                "title": source["title"],
            }
            for source in sources.get("sources", [])
            if args.domain in source.get("domains", [])
        ],
        "known_gaps": item.get("known_gaps", []),
        "production_claim": item.get("production_claim", "prohibited"),
        "last_verified_at": item.get("last_verified_at"),
    }
    if args.section:
        knowledge_path = ROOT / compact["knowledge_file"]
        knowledge_text = knowledge_path.read_text(encoding="utf-8")
        selected, missing = select_sections(knowledge_text, args.section)
        if missing:
            available = [
                match.group(2).strip()
                for match in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", knowledge_text, re.M)
            ]
            print(f"FAIL: unknown section(s): {', '.join(missing)}")
            print("Available: " + "; ".join(available))
            return 1
        compact["selected_sections"] = selected
    if args.format == "yaml":
        print(yaml.safe_dump(compact, allow_unicode=True, sort_keys=False), end="")
    else:
        print(f"# {compact['domain_id']} domain assurance\n")
        print(f"- Knowledge: {compact['knowledge_file']}")
        print(f"- Applies when: {', '.join(compact['applies_when'])}")
        print(f"- Maturity: {compact['maturity']}")
        print(f"- Practice: {compact['practice_status']}")
        print(f"- Production claim: {compact['production_claim']}")
        print(f"- Sources: {len(compact['source_refs'])} ({', '.join(source['id'] for source in compact['source_refs'])})")
        print("- Known gaps:")
        for gap in compact["known_gaps"]:
            print(f"  - {gap}")
        for section in compact.get("selected_sections", []):
            print("\n" + section)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
