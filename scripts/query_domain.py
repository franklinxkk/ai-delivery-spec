#!/usr/bin/env python3
"""Return one compact domain assurance record without loading the full catalog."""

from __future__ import annotations

import argparse
from datetime import date, datetime
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - clean-machine path
    print("缺少 PyYAML。请执行：python -m pip install -r scripts/requirements.txt", file=sys.stderr)
    raise SystemExit(4) from exc


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "domain-coverage.yaml"
SOURCE_CATALOG = ROOT / "references" / "domains" / "domain-sources.yaml"


def stale(last_verified_at: object, refresh_days: object) -> bool:
    try:
        checked = datetime.strptime(str(last_verified_at), "%Y-%m-%d").date()
        return (date.today() - checked).days > int(refresh_days)
    except (TypeError, ValueError):
        return True


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
    parser.add_argument("--custom-root", type=Path, default=Path("custom"), help="本地私有扩展目录")
    args = parser.parse_args()

    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    sources = yaml.safe_load(SOURCE_CATALOG.read_text(encoding="utf-8"))
    official = {item["domain_id"]: item for item in catalog.get("domains", [])}
    custom_root = args.custom_root.resolve()
    custom_config = {}
    if (custom_root / "config.yaml").is_file():
        custom_config = yaml.safe_load((custom_root / "config.yaml").read_text(encoding="utf-8")) or {}
    custom_domains = {
        item["domain_id"]: item
        for item in custom_config.get("domains", [])
        if isinstance(item, dict) and item.get("domain_id")
    } if isinstance(custom_config, dict) else {}

    records: list[dict[str, object]] = []
    for domain_id in [item.strip() for item in args.domain.split("+") if item.strip()]:
        item = official.get(domain_id)
        if item is not None:
            record: dict[str, object] = {
                "domain_id": item["domain_id"],
                "origin": "official",
                "knowledge_file": item["knowledge_file"],
                "applies_when": item.get("applies_when", []),
                "does_not_apply_when": item.get("does_not_apply_when", []),
                "maturity": item["maturity"],
                "practice_status": item["practice_status"],
                "coverage": item["coverage"],
                "evidence_refs": list(dict.fromkeys(evidence["location"] for evidence in item.get("evidence", []))),
                "source_refs": [
                    {
                        "id": source["id"], "type": source["authority_type"], "title": source["title"],
                        "last_verified_at": source.get("last_verified_at"), "refresh_days": source.get("refresh_days"),
                        "stale": stale(source.get("last_verified_at"), source.get("refresh_days")),
                    }
                    for source in sources.get("sources", []) if domain_id in source.get("domains", [])
                ],
                "known_gaps": item.get("known_gaps", []),
                "production_claim": item.get("production_claim", "prohibited"),
                "last_verified_at": item.get("last_verified_at"),
            }
            knowledge_path = ROOT / str(record["knowledge_file"])
        else:
            item = custom_domains.get(domain_id)
            fallback = custom_root / "domains" / f"{domain_id}.md"
            if item is None and fallback.is_file():
                item = {"domain_id": domain_id, "knowledge_file": f"domains/{domain_id}.md"}
            if item is None:
                available = ", ".join(sorted({*official, *custom_domains}))
                print(f"FAIL: unknown domain {domain_id!r}; available: {available}")
                return 1
            knowledge_path = custom_root / str(item.get("knowledge_file", f"domains/{domain_id}.md"))
            record = {
                "domain_id": domain_id,
                "origin": "local_private",
                "knowledge_file": str(knowledge_path),
                "applies_when": item.get("applies_when", []),
                "does_not_apply_when": item.get("does_not_apply_when", []),
                "maturity": item.get("maturity", "local"),
                "practice_status": item.get("practice_status", "team_private"),
                "coverage": item.get("coverage", []),
                "evidence_refs": item.get("evidence_refs", []),
                "source_refs": item.get("source_refs", []),
                "known_gaps": item.get("known_gaps", []),
                "production_claim": item.get("production_claim", "local_only"),
                "owner": item.get("owner"),
            }
            if not knowledge_path.is_file():
                print(f"FAIL: local domain knowledge file not found: {knowledge_path}")
                return 1
        record["source_refresh_warning"] = (
            "存在超过刷新周期或缺少日期的来源；使用其作约束前必须重新核验"
            if any(source.get("stale") for source in record.get("source_refs", []) if isinstance(source, dict)) else None
        )
        if args.section:
            knowledge_text = knowledge_path.read_text(encoding="utf-8")
            selected, missing = select_sections(knowledge_text, args.section)
            if missing:
                print(f"FAIL: {domain_id} unknown section(s): {', '.join(missing)}")
                return 1
            record["selected_sections"] = selected
        records.append(record)

    payload: dict[str, object] = records[0] if len(records) == 1 else {
        "composition": [record["domain_id"] for record in records],
        "domains": records,
        "precedence": "本地包可覆盖模板与展示默认值；绑定规则冲突必须创建 DEC-CONFLICT-*，禁止静默覆盖",
    }
    if args.format == "yaml":
        print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), end="")
    else:
        print(f"# {' + '.join(str(record['domain_id']) for record in records)} domain assurance\n")
        if len(records) > 1:
            print("- Precedence: 本地包可覆盖模板与展示默认值；绑定规则冲突必须创建 DEC-CONFLICT-*。")
        for record in records:
            print(f"\n## {record['domain_id']} ({record['origin']})")
            print(f"- Knowledge: {record['knowledge_file']}")
            print(f"- Maturity: {record['maturity']}")
            print(f"- Production claim: {record['production_claim']}")
            for section in record.get("selected_sections", []):
                print("\n" + str(section))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
