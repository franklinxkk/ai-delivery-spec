#!/usr/bin/env python3
"""Return one compact domain assurance record without loading the full catalog."""

from __future__ import annotations

import argparse
import json
import unicodedata
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
VENDOR_AUTHORITY_TYPES = {
    "vendor_whitepaper", "vendor_product_docs", "vendor_case_library", "vendor_open_source",
}
EFFECT_CLASSES = {"binding_baseline", "design_guidance", "product_pattern", "change_watch"}
DISCOVERY = ROOT / "references" / "domains" / "domain-discovery.json"
DISCOVERY_DATA = json.loads(DISCOVERY.read_text(encoding="utf-8")) if DISCOVERY.is_file() else {}
DOMAIN_GUIDES = {d["domain_id"]: d for d in DISCOVERY_DATA.get("domains", [])}

SECTION_ALIASES = {
    "指标": "Metric / Indicator Governance", "指标口径": "Metric / Indicator Governance",
    "状态机": "State Machines", "核心流程": "Core Workflows",
    "角色路径": "Role Path Patterns", "验收清单": "Acceptance Checklist",
    "隐私约束": "Policy / Privacy Constraints", "测试场景": "Domain Test Scenarios",
}

SECTION_ALIASES.update(DISCOVERY_DATA.get("section_aliases", {}))

def stale(last_verified_at: object, refresh_days: object) -> bool:
    try:
        checked = datetime.strptime(str(last_verified_at), "%Y-%m-%d").date()
        return (date.today() - checked).days > int(refresh_days)
    except (TypeError, ValueError):
        return True


def effect_class(source: dict[str, object]) -> str:
    declared = str(source.get("effect_class", "")).strip()
    if declared:
        return declared if declared in EFFECT_CLASSES else "change_watch"
    status = str(source.get("status", "")).casefold()
    if source.get("authority_type") in VENDOR_AUTHORITY_TYPES:
        return "product_pattern"
    if any(token in status for token in ("draft", "watch", "proposed", "unverified")):
        return "change_watch"
    return "authoritative_reference"


def binding_use(source: dict[str, object]) -> str:
    classification = effect_class(source)
    if classification in {"product_pattern", "change_watch"}:
        return "prohibited"
    return "verify_applicability"


def select_sections(raw: str, requested: list[str]) -> tuple[list[str], list[str]]:
    headings = [
        (len(match.group(1)), match.group(2).strip(), match.start())
        for match in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", raw, re.M)
    ]
    selected: list[str] = []
    missing: list[str] = []
    for name in requested:
        name = SECTION_ALIASES.get(name.strip(), name.strip())
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


def search_terms(query: str, aliases: dict) -> list[str]:
    """Keep the literal query; expand known terms without inventing translations."""
    terms = [query.strip()]
    for group in search_concepts(query, aliases).values():
        terms.extend(group)
    return list(dict.fromkeys(terms))


def term_pattern(term: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9]+(?:[\s\-\u2010-\u2015]+[a-zA-Z0-9]+)*", term):
        return re.escape(term)
    # Match curated English phrases across spaces or hyphens, with bounded
    # noun plurals. Do not stem arbitrary query words or match word fragments.
    words = re.split(r"[\s\-\u2010-\u2015]+", term)
    final = words[-1]
    if re.search(r"[^aeiou]y$", final, re.I):
        ending = re.escape(final[:-1]) + r"(?:y|ies)"
    elif re.search(r"(?:ss|us|x|z|ch|sh)$", final, re.I):
        ending = re.escape(final) + r"(?:es)?"
    elif final.casefold().endswith("s"):
        ending = re.escape(final)
    else:
        ending = re.escape(final) + r"(?:s)?"
    literal = r"[\s\-\u2010-\u2015]+".join([*(re.escape(word) for word in words[:-1]), ending])
    return r"(?<![a-zA-Z0-9_])" + literal + r"(?![a-zA-Z0-9_])"


def generic_fallback(domain_id: str | None, available: list[str], english: bool, pack_available: bool | None = False) -> dict[str, object]:
    """Offer the generic workflow without inventing an unsupported domain pack."""
    return {
        "mode": "generic_requirement_patterns",
        "pattern_file": "references/patterns/common-requirement-patterns.yaml",
        "requested_domain": domain_id,
        "dedicated_pack_available": pack_available,
        "available_domain_ids": available,
        "next_action": (
            "Check the available domain IDs for a spelling mismatch. If the sector is unsupported, continue with common requirement patterns and collect project vocabulary, actors, objects, behavior and sources as relevant; obtain current authoritative sector/jurisdiction sources before stating domain obligations."
            if english else
            "先核对可用领域 ID，排除拼写差异。确无专用包时可继续通用需求模式，按问题补充项目术语、角色、对象、行为与来源；陈述行业义务前需取得匹配行业和法域的当前有权来源。"
        ),
        "claim_limit": (
            "No dedicated knowledge, expert review or regulatory applicability is established by this fallback or by a cross-industry mock."
            if english else
            "此退路及跨行业 Mock 均不证明已有专用领域知识、专家审查或法规适用。"
        ),
    }


def recognized_concepts(query: str, aliases: dict) -> tuple[dict[str, list[str]], list[tuple[int, int, str]]]:
    """Recognize curated phrases inside either language, longest phrase first.

    Overlapping short aliases must not expand milestones into mileage or
    active customers into all active entities. Unrelated words stay literal.
    """
    groups, candidates = {}, []
    for key, values in aliases.items():
        if not isinstance(key, str) or not key or not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
            continue
        groups[key] = list(dict.fromkeys([key, *values]))
        for term in groups[key]:
            for match in re.finditer(term_pattern(term), query, re.I):
                candidates.append((match.start(), match.end(), key))
    selected = []
    for start, end, key in sorted(candidates, key=lambda item: (-(item[1] - item[0]), -len(item[2]), item[0])):
        # A contained short alias can be misleading (active vs active customer).
        # Adjacent concepts may share a word: education data / data classification.
        if any((a <= start and end <= b) or (start <= a and b <= end) for a, b, _ in selected):
            continue
        selected.append((start, end, key))
    return {key: groups[key] for _, _, key in sorted(selected)}, selected


def search_concepts(query: str, aliases: dict) -> dict[str, list[str]]:
    return recognized_concepts(query, aliases)[0]


def scoped_query_concepts(query: str, aliases: dict, anchors: list[tuple[int, int, str]]) -> tuple[dict, list]:
    """Do not expand a fragment when another selected pack recognizes the phrase.

    Chinese customer-deduplication must not retrieve every passage mentioning
    a customer in unrelated packs. Anchors only limit query segmentation;
    translations remain scoped to the pack that declares them.
    """
    concepts, spans = recognized_concepts(query, aliases)
    spans = [(start, end, key) for start, end, key in spans
             if not any(a <= start and end <= b and (a, b) != (start, end) for a, b, _ in anchors)]
    return {key: concepts[key] for _, _, key in spans}, spans


def query_coverage(query: str, spans: list[tuple[int, int, str]], matched: list[str], literal: bool) -> int:
    """Lexical coverage, not semantic confidence or a domain applicability score.

    A whole curated phrase (customer deduplication) must rank before its broad
    fragment (customer). Use the same query denominator for every domain;
    otherwise a pack recognizing only one word looks like a complete match.
    """
    positions = {i for i, char in enumerate(query) if char.isalnum()}
    if literal:
        return 100
    covered = {i for start, end, key in spans if key in matched for i in range(start, end)}
    return round(100 * len(positions & covered) / len(positions)) if positions else 0


def rank_hits(hits: list[dict]) -> list[dict]:
    """Diversify ties only; never demote a stronger match below weak matches."""
    for hit in hits:
        hit["score"] = (hit["query_coverage"] + (12 if hit["match_type"] == "literal" else 0)
                        + 5 * len(hit["matched_concepts"]) + 6 * bool(hit.get("domain_matches")))
        if hit["excerpt"].startswith("**"):
            hit["score"] += 2
        if hit["section"] in {"", "Contents", "中文导读"}:
            hit["score"] -= 5
    hits.sort(key=lambda hit: (-hit["score"], hit["domain_id"], hit["line"]))
    ranked, bucket = [], []
    for hit in hits:
        if bucket and hit["score"] != bucket[0]["score"]:
            ranked.extend(diversify_ties(bucket))
            bucket = []
        bucket.append(hit)
    return ranked + diversify_ties(bucket)


def diversify_ties(hits: list[dict]) -> list[dict]:
    first, rest, per_section = [], [], {}
    for hit in hits:
        key = (hit["domain_id"], hit["section"])
        n = per_section.get(key, 0)
        per_section[key] = n + 1
        (first if n < 2 else rest).append(hit)
    return first + rest


def term_matches(term: str, line: str) -> bool:
    return bool(term and re.search(term_pattern(term), line, re.I))


def common_pattern_candidates(query: str) -> list[dict]:
    """Return cross-domain decision aids separately from sourced domain hits."""
    path = ROOT / 'references/patterns/common-requirement-patterns.yaml'
    library = yaml.safe_load(path.read_text(encoding='utf-8'))
    return [dict(pattern_ref=p['id'], name=p['name'], path=path.relative_to(ROOT).as_posix(),
                 applies_when=p['applies_when'], questions=p['required_questions'],
                 authority='decision_prompts_not_project_policy')
            for p in library.get('patterns', [])
            if any(term_matches(term, query) for term in [p['name'], *p.get('aliases', [])])][:3]


def main() -> int:
    # Domain records intentionally contain multilingual source titles and gaps.
    # Emit a deterministic UTF-8 stream even when a Windows host exposes a
    # narrow legacy console encoding such as cp1252.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="领域 ID 或中文名称；多个领域用 + 分隔")
    parser.add_argument("--list", action="store_true", help="列出每个领域的中文简介、别名及知识文件")
    parser.add_argument("--search", help="Find literal keywords and curated Chinese/English aliases across packs")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--format", choices=["yaml", "markdown"], default="yaml")
    parser.add_argument("--source-detail", choices=["compact", "full"], default="compact")
    parser.add_argument("--language", choices=["auto", "zh-CN", "en-US"], default="auto")
    parser.add_argument("--section", action="append", default=[], help="Load only an exact ##/### heading; repeat as needed")
    parser.add_argument("--custom-root", type=Path, default=Path("custom"), help="本地私有扩展目录")
    args = parser.parse_args()
    if not args.domain and not args.search and not args.list:
        parser.error("provide --domain, --search or --list")
    if args.search is not None and (not args.search.strip() or not 1 <= args.limit <= 50):
        parser.error("--search must be nonempty; --limit must be 1..50")
    if args.search and args.section:
        parser.error("search locates candidate sections; select --section in a separate call")

    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    sources = yaml.safe_load(SOURCE_CATALOG.read_text(encoding="utf-8"))
    aliases = catalog.get("search_aliases", {})
    english = args.language == "en-US" or (args.language == "auto" and not re.search(r"[\u4e00-\u9fff]", (args.search or "") + (args.domain or "") + " ".join(args.section)))
    if args.list:
        listing = [{k: d[k] for k in ("domain_id", "name_zh", "summary_zh", "name_en", "summary_en", "aliases", "knowledge_file") if k in d} for d in DOMAIN_GUIDES.values()]
        claim_limit = ("Summaries help select a domain; a match does not establish applicability or complete knowledge."
                       if english else "简介只帮助选择领域；命中不等于项目适用或完整知识。")
        if args.format == "yaml":
            print(yaml.safe_dump({"domains": listing, "claim_limit": claim_limit}, allow_unicode=True, sort_keys=False))
        else:
            print("# Domain knowledge directory\n" if english else "# 领域知识中文目录\n")
            for d in listing:
                name, summary = (d.get("name_en", d['domain_id']), d.get("summary_en", "")) if english else (d['name_zh'], d['summary_zh'])
                print(f"## {name} ({d['domain_id']})\n\n{summary}\n\n{'Aliases' if english else '别名'}: {', '.join(d['aliases'])}\n\n{'File' if english else '文件'}: {d['knowledge_file']}\n")
            print(claim_limit)
        return 0
    usage_rule = (
        "Search hits and domain patterns are candidates, not approved project rules. Verify jurisdiction, covered entities, effective version and authority; response language does not determine jurisdiction. origin=official identifies the Skill's built-in catalog, not government authority or binding force; inspect each source_ref's authority/effect class and original text."
        if english else
        "检索命中与领域经验只是候选，不是项目已批准规则。核实法域、适用对象、生效版本与来源权威；提问语言不决定适用法域。origin=official表示Skill内置目录，不代表政府权威或强制效力；须查看各source_ref的权威与效力分类并核对原文。"
    )
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
    def resolve_domain(name):
        folded = unicodedata.normalize("NFKC", name).casefold()
        candidates = [d["domain_id"] for d in DOMAIN_GUIDES.values() if folded in {unicodedata.normalize("NFKC", v).casefold() for v in [d["domain_id"], d["name_zh"], *d["aliases"]]}]
        return candidates[0] if len(candidates) == 1 else name
    domain_ids = [resolve_domain(item.strip()) for item in args.domain.split("+") if item.strip()] if args.domain else list(dict.fromkeys([*official,*custom_domains]))
    recognition_aliases = dict(aliases)
    for domain_id in domain_ids:
        for term, variants, _section, _note in DOMAIN_GUIDES.get(domain_id, {}).get("terms", []):
            recognition_aliases[term] = list(dict.fromkeys([*recognition_aliases.get(term, []), *variants]))
    query_anchors = recognized_concepts(args.search, recognition_aliases)[1] if args.search else []
    for domain_id in domain_ids:
        item = official.get(domain_id)
        if item is not None:
            domain_sources = [source for source in sources.get("sources", []) if domain_id in source.get("domains", [])]
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
                "known_gaps": item.get("known_gaps", []),
                "production_claim": item.get("production_claim", "prohibited"),
                "last_verified_at": item.get("last_verified_at"),
                "source_catalog": "references/domains/domain-sources.yaml",
                "jurisdictions": sorted({str(s["jurisdiction"]) for s in domain_sources if s.get("jurisdiction")}),
            }
            if args.source_detail == "full":
                record["source_refs"] = [
                    {
                        "id": source["id"], "title": source["title"],
                        "url": source.get("url"), "jurisdiction": source.get("jurisdiction"),
                        "applicability": source.get("applicability"), "status": source.get("status"),
                        "effect_class": effect_class(source), "binding_use": binding_use(source),
                        "last_verified_at": source.get("last_verified_at"), "refresh_days": source.get("refresh_days"),
                        "stale": stale(source.get("last_verified_at"), source.get("refresh_days")),
                        **({"claim_limit": source["claim_limit"]} if source.get("claim_limit") else {}),
                        **({key: source[key] for key in ("verification_evidence", "verification_attempt") if source.get(key)}),
                    }
                    for source in domain_sources
                ]
            else:
                record["source_refs"] = [source["id"] for source in domain_sources]
                record["source_effects"] = {
                    kind: [source["id"] for source in domain_sources if effect_class(source) == kind]
                    for kind in ("binding_baseline", "design_guidance", "product_pattern", "change_watch")
                    if any(effect_class(source) == kind for source in domain_sources)
                }
                record["stale_source_refs"] = [
                    source["id"] for source in domain_sources
                    if stale(source.get("last_verified_at"), source.get("refresh_days"))
                ]
                limits = {source["id"]: source["claim_limit"] for source in domain_sources if source.get("claim_limit")}
                if limits:
                    record["source_claim_limits"] = limits
            knowledge_path = ROOT / str(record["knowledge_file"])
        else:
            item = custom_domains.get(domain_id)
            fallback = custom_root / "domains" / f"{domain_id}.md"
            if item is None and fallback.is_file():
                item = {"domain_id": domain_id, "knowledge_file": f"domains/{domain_id}.md"}
            if item is None:
                fallback_info = generic_fallback(domain_id, sorted({*official, *custom_domains}), english)
                record = {"domain_id": domain_id, "origin": "generic_fallback",
                          "knowledge_file": None, "maturity": "unsupported", "practice_status": "not_evaluated",
                          "production_claim": "prohibited", "source_refs": [], "jurisdictions": [],
                          "source_usage_rule": usage_rule, "source_refresh_warning": None,
                          "fallback": fallback_info}
                if args.search:
                    record["search_hits"] = []
                if args.section:
                    record["selected_sections"] = []
                    record["unavailable_sections"] = args.section
                records.append(record)
                continue
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
                "jurisdictions": item.get("jurisdictions", []),
            }
            if not knowledge_path.is_file():
                print(f"FAIL: local domain knowledge file not found: {knowledge_path}")
                return 1
        guide = DOMAIN_GUIDES.get(domain_id, {})
        record.update({k: guide[k] for k in ("name_zh", "summary_zh", "name_en", "summary_en", "aliases") if k in guide})
        if guide: record["vocabulary"] = [{"term": t[0], "aliases": t[1], "section": t[2]} for t in guide["terms"]]
        record["source_refresh_warning"] = (
            ("Some sources are stale or undated; recheck them before using them as constraints." if english else
             "存在超过刷新周期或缺少日期的来源；使用其作约束前必须重新核验")
            if record.get("stale_source_refs") or any(
                source.get("stale") for source in record.get("source_refs", []) if isinstance(source, dict)
            ) else None
        )
        record["source_usage_rule"] = usage_rule + (
            " product_pattern/change_watch cannot establish binding requirements."
            if english else " product_pattern/change_watch 不能生成硬要求。")
        if args.search:
            section = ""
            matches = []
            local_aliases = dict(aliases)
            # Domain-scoped expansions prevent e.g. education credit from becoming a finance obligation.
            for term, variants, _section, _note in guide.get("terms", []):
                local_aliases[term] = list(dict.fromkeys([*local_aliases.get(term, []), *variants]))
            local_concepts, concept_spans = scoped_query_concepts(args.search, local_aliases, query_anchors)
            local_terms = list(dict.fromkeys([args.search.strip(), *(term for group in local_concepts.values() for term in group)]))
            record['expanded_terms'] = local_terms
            domain_matches = [a for a in [guide.get("name_zh", ""), *guide.get("aliases", [])] if a and term_matches(a, args.search)]
            record["query_domain_matches"] = domain_matches
            for number, line in enumerate(knowledge_path.read_text(encoding="utf-8").splitlines(), 1):
                heading = re.match(r"^#{2,3}\s+(.+)", line)
                if heading:
                    section = heading[1].strip()
                matched = [term for term in local_terms if term_matches(term, line)]
                if matched:
                    matched_concepts = [key for key, group in local_concepts.items() if any(term_matches(term, line) for term in group)]
                    literal = term_matches(args.search, line)
                    matches.append({"domain_id": domain_id, "section": section, "line": number,
                                    "knowledge_file": record["knowledge_file"], "excerpt": line.strip()[:300],
                                    "status": "candidate", "origin": record["origin"],
                                    "matched_terms": matched,
                                    "matched_concepts": matched_concepts,
                                    "domain_matches": domain_matches,
                                    "query_coverage": query_coverage(args.search, concept_spans, matched_concepts, literal),
                                    "match_type": "literal" if literal else "alias"})
            record["search_hits"] = matches
        if args.section:
            knowledge_text = knowledge_path.read_text(encoding="utf-8")
            selected, missing = select_sections(knowledge_text, args.section)
            if missing:
                available_headings = [
                    match.group(1).strip()
                    for match in re.finditer(r"^#{2,3}\s+(.+?)\s*$", knowledge_text, re.M)
                ]
                available = "; ".join(available_headings[:30]) or "<none>"
                print(
                    f"FAIL: {domain_id} unknown section(s): {', '.join(missing)}; "
                    f"available headings: {available}"
                )
                return 1
            record["selected_sections"] = selected
        records.append(record)

    if args.search:
        hits = [hit for record in records for hit in record.get("search_hits", [])]
        hits = rank_hits(hits)
        next_action = None if hits else (
            "No local passage matched. Try a shorter business term, or use --domain <id> to inspect a relevant pack and its sections; no hit does not prove no applicable rule."
            if english else
            "本地语料未命中。尝试更短的业务词，或用 --domain <领域 ID> 查看相关包及章节；零命中不代表没有适用规则。")
        payload = {"query": args.search, "searched_domains": domain_ids, "total_matches": len(hits),
                   "common_patterns": common_pattern_candidates(args.search),
                   "expanded_terms": list(dict.fromkeys(t for r in records for t in r.get('expanded_terms',[]))), "retrieval": "literal_with_domain_scoped_aliases_and_ranked_sections",
                   "retrieval_limit": ("query_coverage is lexical coverage, not semantic confidence. Negation and scope remain in the original query; a hit does not select or authorize a requirement."
                                       if english else "query_coverage 是查询字词覆盖度，不是语义置信度。否定与范围关系保留在原查询中；命中不表示采纳或授权该需求。"),
                   "domain_expansions": {r['domain_id']:r.get('expanded_terms',[]) for r in records},
                   "matched_concepts": list(dict.fromkeys(k for h in hits for k in h["matched_concepts"])), "next_action": next_action,
                   "domain_summaries": [{k: r[k] for k in ("domain_id", "name_zh", "summary_zh", "name_en", "summary_en") if k in r} for r in records if r.get("search_hits")],
                   "truncated": len(hits) > args.limit, "hits": hits[:args.limit],
                   "source_usage_rule": usage_rule}
        if not hits:
            availability = all(record["origin"] != "generic_fallback" for record in records) if args.domain else None
            payload["fallback"] = generic_fallback(args.domain, sorted({*official, *custom_domains}), english, availability)
        if args.format == "yaml":
            print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), end="")
        else:
            print(f"# {'Domain search' if english else '领域检索'}: {args.search}\n\n{payload['source_usage_rule']}\n")
            print(f"{'Search terms' if english else '检索词'}: {', '.join(payload['expanded_terms'])}\n")
            print(payload["retrieval_limit"] + "\n")
            for pattern in payload['common_patterns']:
                print(f"- {pattern['pattern_ref']} / {pattern['path']}: {pattern['name']}")
                print(('  Decision prompts only; inherit existing answers.' if english else '  共性决策提示，已有答案直接继承，不是项目政策。'))
                for question in pattern['questions']:
                    print('  - ' + question)
            for row in payload["domain_summaries"]:
                name_key, summary_key = ("name_en", "summary_en") if english else ("name_zh", "summary_zh")
                print(f"- {row.get(name_key, row['domain_id'])}: {row.get(summary_key, '')}")
            print()
            for hit in hits[:args.limit]:
                print(f"- {hit['domain_id']} / {hit['section']} [{hit['line']}, {hit['match_type']}]: {hit['excerpt']}")
            print(f"\n{'Matches / shown' if english else '匹配 / 显示'}: {len(hits)} / {min(len(hits), args.limit)}")
            if next_action:
                print(next_action)
                print(payload["fallback"]["next_action"])
                print(payload["fallback"]["claim_limit"])
        return 0

    if args.section:
        if args.format == "yaml":
            slices = [
                {key: record.get(key) for key in ("domain_id", "origin", "knowledge_file", "maturity", "practice_status", "production_claim", "jurisdictions", "source_catalog", "source_refs", "source_refresh_warning", "source_usage_rule", "selected_sections", "unavailable_sections", "fallback") if key in record}
                for record in records
            ]
            payload: object = slices[0] if len(slices) == 1 else {"domains": slices}
            print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), end="")
        else:
            for index, record in enumerate(records):
                print(f"<!-- {record['domain_id']} | maturity={record['maturity']} | practice={record['practice_status']} | production_claim={record['production_claim']} -->")
                print(f"> {record['source_usage_rule']}" + (f"；{record['source_refresh_warning']}" if record['source_refresh_warning'] else "") + "\n")
                if record.get("fallback"):
                    print(record["fallback"]["next_action"] + "\n" + record["fallback"]["claim_limit"] + "\n")
                if len(records) > 1:
                    if index:
                        print()
                    print(f"# {record['domain_id']}")
                for section_index, section in enumerate(record.get("selected_sections", [])):
                    if index or section_index:
                        print()
                    print(str(section), end="" if str(section).endswith("\n") else "\n")
        return 0

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
            summary_key = "summary_en" if english else "summary_zh"
            if record.get(summary_key):
                print(record[summary_key] + "\n")
                print(("Aliases: " if english else "常用别名：") + ", ".join(record.get("aliases", [])))
            print(f"- Knowledge: {record['knowledge_file']}")
            print(f"- Maturity: {record['maturity']}")
            print(f"- Production claim: {record['production_claim']}")
            if record.get("fallback"):
                print(record["fallback"]["next_action"] + "\n" + record["fallback"]["claim_limit"])
            for section in record.get("selected_sections", []):
                print("\n" + str(section))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
