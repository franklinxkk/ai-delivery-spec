"""Read-only intake/routing advice. A recommendation never mutates a lifecycle."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
import yaml
from requirement_contract import route, load_declarations
from scan_requirement_ambiguity import scan

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load(path: Path) -> dict:
    try:
        value = load_declarations(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError("Use a readable YAML/JSON object containing known task facts: " + str(exc)) from exc
    if not isinstance(value, dict):
        raise ValueError("Input must be a YAML/JSON object; no lifecycle scaffold is required")
    return value


def recommend(doc: dict) -> dict:
    result = route(doc)
    advice = "clarify" if doc.get("ambiguity") == "high" else "accept"
    reasons = []
    questions = result["content_review"]["findings"]
    lexical = scan("\n".join(doc[k] for k in ("title", "description", "behavior") if isinstance(doc.get(k), str)))
    generic_goal = bool(re.fullmatch(r"(?:做个|做一个|建设|搭建|优化)(?:一个|个)?系统|优化体验|提升效率", str(doc.get("title", "")).strip("。！？.! "))) and not doc.get("description")
    if questions or lexical or generic_goal:
        advice = "clarify"
        reasons.extend(item["action"] for item in questions)
        if (lexical or generic_goal) and not questions:
            reasons.append("目标措辞尚有不明确之处；仅澄清会改变范围、授权或验收的部分")
    if doc.get("duplicate_of") or doc.get("out_of_product_boundary"):
        advice = "reject"
        reasons.append("已声明重复或越界；核对来源与授权后才能实际处置")
    elif doc.get("blocked_dependency"):
        advice = "defer"
        reasons.append("已声明依赖未满足；暂缓建议不自动改变需求状态")
    if not doc.get("title"):
        advice = "clarify"
        reasons.append("任务目标尚未给出")
    result.update({
        "document_language": doc.get("document_language") or ("zh-CN" if re.search(r"[\u4e00-\u9fff]", str(doc.get("title", ""))) else "en"),
        "recommendation": advice, "decision_status": "proposed", "reasons": reasons,
        "lifecycle_mutated": False,
        "clarification_candidates": questions or lexical,
    })
    return result


def render_markdown(result: dict) -> str:
    return "# 需求路由建议 / Requirement routing\n\n" + "\n".join([
        f"- 建议 / recommendation: {result['recommendation']} (proposed)",
        f"- 产物 / artifact_mode: {result['artifact_mode']}",
        f"- 风险 / risk_facets: {', '.join(result['risk_facets']) or '未声明 / undeclared'}",
        f"- 治理 / governed: {result['governed']}",
        f"- 用户优先级 / priority: {result['priority'] or '未给出 / unspecified'}",
        *[f"- 依据 / reason: {reason}" for reason in result["reasons"]],
        "- 未修改需求状态；未证明授权、业务正确性或实际实现。",
    ]) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["markdown", "yaml", "json"], default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = recommend(load(args.input))
    except ValueError as exc:
        print("BLOCKED TRIAGE-INPUT: " + str(exc), file=sys.stderr)
        return 2
    if args.format == "json":
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    elif args.format == "yaml":
        rendered = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    else:
        rendered = render_markdown(result)
        for issue in result["errors"]:
            rendered += "- BLOCKED: " + issue + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
