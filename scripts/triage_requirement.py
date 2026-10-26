"""Read-only intake/routing advice. A recommendation never mutates a lifecycle."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
import yaml
from requirement_contract import route, load_declarations, intake_text
from scan_requirement_ambiguity import scan

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class TriageInputError(ValueError):
    """Controlled diagnostics never retain a parser message or input excerpt."""

    def __init__(self, reason: str, language: str = "zh-CN", line: int | None = None, column: int | None = None):
        super().__init__(reason)
        self.reason, self.language, self.line, self.column = reason, language, line, column


def input_error_language(raw: str) -> str:
    declared = re.search(r"(?m)^\s*document_language:\s*['\"]?(en(?:-[A-Za-z]+)?|zh(?:-[A-Za-z]+)?)(?=['\"\s#]|$)", raw, re.I)
    if declared:
        return "en-US" if declared[1].casefold().startswith("en") else "zh-CN"
    # With no readable language declaration, broken input cannot reliably supply
    # a task language. Use the CLI's Chinese default; English callers can select
    # --language en-US explicitly.
    return "zh-CN"


def load(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeError:
        raise TriageInputError("encoding") from None
    except FileNotFoundError:
        raise TriageInputError("missing") from None
    except PermissionError:
        raise TriageInputError("permission") from None
    except OSError:
        raise TriageInputError("unreadable") from None
    language = input_error_language(raw)
    if not raw.strip():
        raise TriageInputError("empty", language)
    try:
        value = load_declarations(raw)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        raise TriageInputError("syntax", language,
                               mark.line + 1 if mark else None, mark.column + 1 if mark else None) from None
    except ValueError as exc:
        reason = "keys" if str(exc) == "Declaration keys must be unique strings" else "object"
        raise TriageInputError(reason, language) from None
    return value


def render_input_error(path: Path, error: TriageInputError, language: str = "auto") -> str:
    english = (error.language if language == "auto" else language) == "en-US"
    reasons = {
        "missing": ("找不到输入文件", "Input file not found"),
        "permission": ("没有读取输入文件的权限", "Input file is not readable with the current permissions"),
        "unreadable": ("输入路径不可读取或不是普通文件", "Input path is unreadable or is not a regular file"),
        "encoding": ("输入不是有效的 UTF-8 文本", "Input is not valid UTF-8 text"),
        "empty": ("输入为空", "Input is empty"),
        "syntax": ("YAML/JSON 语法无效", "Invalid YAML/JSON syntax"),
        "keys": ("对象中的键必须是唯一的字符串", "Object keys must be unique strings"),
        "object": ("输入根节点必须是 YAML/JSON 对象，不能是列表或标量", "Input root must be a YAML/JSON object, not a list or scalar"),
    }
    reason = reasons[error.reason][int(english)]
    if error.line is not None:
        reason += (f" at line {error.line}, column {error.column}" if english else
                   f"（第 {error.line} 行，第 {error.column} 列）")
    if error.reason in {"missing", "permission", "unreadable"}:
        step = "Check the input path and read permissions, then run again." if english else "核对输入路径及读取权限后重新运行。"
    elif error.reason == "encoding":
        step = "Save the input as UTF-8, then run again." if english else "将输入保存为 UTF-8 后重新运行。"
    elif error.reason == "syntax":
        step = "Check brackets, quotes and indentation at the reported position, then run again." if english else "检查所示位置的括号、引号和缩进后重新运行。"
    else:
        step = "Provide a YAML/JSON object with known task facts, then run again; no lifecycle scaffold is required." if english else "使用 YAML/JSON 对象填写已知任务事实后重新运行；无需生命周期模板。"
    limit = "No routing recommendation was produced." if english else "本次未形成业务处置建议。"
    return (f"BLOCKED TRIAGE-INPUT: input {path}: {reason}. Next: {step} {limit}" if english else
            f"BLOCKED TRIAGE-INPUT: 输入 {path}：{reason}。下一步：{step}{limit}")


def recommend(doc: dict, output_language: str = "auto") -> dict:
    result = route(doc)
    narrative = intake_text(doc)
    detail = intake_text(doc, include_title=False)
    language = doc.get("document_language") or ("zh-CN" if re.search(r"[\u4e00-\u9fff]", narrative) else "en")
    language_for_output = ("en-US" if str(language).casefold().startswith("en") else "zh-CN") if output_language == "auto" else output_language
    english = language_for_output == "en-US"
    advice = "clarify" if doc.get("ambiguity") == "high" else "accept"
    reasons = []
    questions = result["content_review"]["findings"]
    required_questions = [item for item in questions if item.get("severity") != "WARN"]
    lexical = scan(narrative)
    generic_goal = bool(re.fullmatch(r"(?:做个|做一个|建设|搭建|优化)(?:一个|个)?系统|优化体验|提升效率|(?:please\s+)?build\s+(?:me\s+)?(?:a|an)\s+(?:system|app)|improve\s+(?:the\s+)?(?:experience|efficiency)", str(doc.get("title", "")).strip("。！？.! "), re.I)) and not detail
    # Bounded cues for a complaint with no task, not a general NLP classifier.
    # Concrete instructions elsewhere in the input take precedence over tone.
    title = str(doc.get("title", "")).strip()
    complaint = bool(re.search(r"(?:太烂|太差|难用|不想说|随便吧|你们看着办|\b(?:terrible|awful|useless|whatever)\b|\b(?:hard|difficult)\s+to\s+use\b)", title, re.I))
    action_cue = re.search(r"(?:新增|增加|添加|改为|改成|删除|取消|修复|显示|筛选|导出|需要|希望|请|\b(?:add|remove|change|fix|show|filter|export|need|please)\b)", title, re.I)
    no_task_complaint = complaint and not action_cue and not detail
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
        "output_language": language_for_output,
        "recommendation": advice, "decision_status": "proposed", "reasons": reasons,
        "lifecycle_mutated": False,
        "clarification_candidates": questions or lexical,
        "next_questions": next_questions,
    })
    band = result["complexity_band"]
    if band:
        result["complexity_advice"] = (
            f"Declared complexity {band} informs planning. Artifact form still follows the requested deliverable and affected behavior; this band does not set priority or prove risk coverage."
            if english else f"已声明复杂度 {band}，用于工作规划。产物形式仍按约定交付物和受影响行为选择；该分档不决定优先级，也不证明风险已覆盖。")
    return result


def render_markdown(result: dict) -> str:
    english = str(result.get("output_language", result["document_language"])).casefold().startswith("en")
    advice = {
        "accept": ("可以进入需求整理；本次扫描不证明信息已完整。", "Proceed to specification; this scan does not prove completeness."),
        "clarify": ("先澄清会改变实现的业务选择。", "Clarify the business choices that would change implementation."),
        "reject": ("建议核对后不纳入本次范围，尚未作出拒绝决定。", "Consider excluding this after verification; no rejection decision has been made."),
        "defer": ("建议先解决依赖，暂缓不等于已批准延期。", "Consider resolving the dependency first; no deferral has been approved."),
    }[result["recommendation"]][int(english)]
    mode = {"direct": ("直接完成必要差异", "direct change"), "card": ("简短需求卡", "short requirement card"), "prd": ("按业务切片组织的 PRD", "PRD organized by business slice")}[result["artifact_mode"]][int(english)]
    lines = ["# " + ("Requirement routing" if english else "需求处理建议"), "", advice, "",
             ("Suggested artifact: " if english else "建议产物：") + mode + ".", ""]
    if result.get("complexity_advice"):
        lines += [result["complexity_advice"], ""]
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
    parser.add_argument("--language", choices=["auto", "zh-CN", "en-US"], default="auto",
                        help="Output language; auto follows valid task input")
    args = parser.parse_args()
    try:
        result = recommend(load(args.input), output_language=args.language)
    except TriageInputError as exc:
        print(render_input_error(args.input, exc, args.language), file=sys.stderr)
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
