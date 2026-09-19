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
    language = doc.get("document_language") or ("zh-CN" if re.search(r"[\u4e00-\u9fff]", str(doc.get("title", ""))) else "en")
    english = str(language).casefold().startswith("en")
    advice = "clarify" if doc.get("ambiguity") == "high" else "accept"
    reasons = []
    questions = result["content_review"]["findings"]
    required_questions = [item for item in questions if item.get("severity") != "WARN"]
    lexical = scan("\n".join(doc[k] for k in ("title", "description", "behavior") if isinstance(doc.get(k), str)))
    generic_goal = bool(re.fullmatch(r"(?:做个|做一个|建设|搭建|优化)(?:一个|个)?系统|优化体验|提升效率|(?:please\s+)?build\s+(?:me\s+)?(?:a|an)\s+(?:system|app)|improve\s+(?:the\s+)?(?:experience|efficiency)", str(doc.get("title", "")).strip("。！？.! "), re.I)) and not doc.get("description")
    # Bounded cues for a complaint with no task, not a general NLP classifier.
    # Concrete instructions elsewhere in the input take precedence over tone.
    title = str(doc.get("title", "")).strip()
    complaint = bool(re.search(r"(?:太烂|太差|难用|不想说|随便吧|你们看着办|\b(?:terrible|awful|useless|whatever)\b)", title, re.I))
    action_cue = re.search(r"(?:新增|增加|添加|改为|改成|删除|取消|修复|显示|筛选|导出|需要|希望|请|\b(?:add|remove|change|fix|show|filter|export|need|please)\b)", title, re.I)
    no_task_complaint = complaint and not action_cue and not any(doc.get(key) for key in ("description", "behavior", "goal", "expected_behavior"))
    if required_questions or lexical or generic_goal or no_task_complaint:
        advice = "clarify"
        reasons.extend(item["action_en"] if english else item["action"] for item in required_questions)
        if no_task_complaint:
            reasons.append("The feedback does not yet identify a concrete change." if english else "反馈尚未说明具体要改善的事情")
        elif (lexical or generic_goal) and not questions:
            reasons.append("The goal still leaves choices open; clarify only what changes scope, authority or acceptance." if english else "目标措辞尚有不明确之处；仅澄清会改变范围、授权或验收的部分")
    if doc.get("duplicate_of") or doc.get("out_of_product_boundary"):
        advice = "reject"
        reasons.append("A duplicate or scope exclusion is declared; verify its source and authority before disposition." if english else "已声明重复或越界；核对来源与授权后才能实际处置")
    elif doc.get("blocked_dependency"):
        advice = "defer"
        reasons.append("A dependency is declared blocked; this recommendation does not defer the requirement automatically." if english else "已声明依赖未满足；暂缓建议不自动改变需求状态")
    if not doc.get("title"):
        advice = "clarify"
        reasons.append("The task goal is missing." if english else "任务目标尚未给出")
    next_questions = list(dict.fromkeys(item["action_en"] if english else item["action"] for item in required_questions))
    if advice == "clarify" and not next_questions:
        next_questions.append(
            "Who is trying to do what, and what current problem should this change solve?" if english else
            "谁要完成什么事，现在遇到的具体问题是什么？")
    result.update({
        "document_language": language,
        "recommendation": advice, "decision_status": "proposed", "reasons": reasons,
        "lifecycle_mutated": False,
        "clarification_candidates": questions or lexical,
        "next_questions": next_questions,
    })
    return result


def render_markdown(result: dict) -> str:
    english = str(result["document_language"]).casefold().startswith("en")
    advice = {
        "accept": ("可以进入需求整理；本次扫描不证明信息已完整。", "Proceed to specification; this scan does not prove completeness."),
        "clarify": ("先澄清会改变实现的业务选择。", "Clarify the business choices that would change implementation."),
        "reject": ("建议核对后不纳入本次范围，尚未作出拒绝决定。", "Consider excluding this after verification; no rejection decision has been made."),
        "defer": ("建议先解决依赖，暂缓不等于已批准延期。", "Consider resolving the dependency first; no deferral has been approved."),
    }[result["recommendation"]][int(english)]
    mode = {"direct": ("直接完成必要差异", "direct change"), "card": ("简短需求卡", "short requirement card"), "prd": ("按业务切片组织的 PRD", "PRD organized by business slice")}[result["artifact_mode"]][int(english)]
    lines = ["# " + ("Requirement routing" if english else "需求处理建议"), "", advice, "",
             ("Suggested artifact: " if english else "建议产物：") + mode + ".", ""]
    if result["next_questions"]:
        lines += [("Start with the applicable questions below; reuse answers already in your sources." if english else "先处理下面适用的问题；已有来源回答过的直接继承。"), ""]
        lines += ["- " + question for question in result["next_questions"][:3]]
        if len(result["next_questions"]) > 3:
            lines += ["- " + ("More candidates are available in --format json." if english else "其余候选问题可用 --format json 查看，按影响选择。")]
    elif result["reasons"]:
        lines += ["- " + reason for reason in result["reasons"]]
    lines += ["", ("This is routing advice, not authorization, a lifecycle change or proof of implementation. Risk candidates and machine fields: --format json." if english else "这是处理建议，未修改需求状态，也未证明授权或实际实现。风险候选及机器字段可用 --format json 查看。")]
    return "\n".join(lines) + "\n"


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
