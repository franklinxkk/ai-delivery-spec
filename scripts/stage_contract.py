#!/usr/bin/env python3
"""Deterministic v5.4 stage-artifact checks; never infer intent from prose."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - clean-machine path
    print(
        "缺少运行依赖 PyYAML。请执行：python -m pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(4) from exc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


STAGES = ("frame", "explore", "intake", "clarify", "specify", "review", "baseline", "change", "acceptance")
EARLY_PROFILES = ("frame", "explore", "clarify")
STAGE_INDEX = {name: index for index, name in enumerate(STAGES)}
GOVERNED_ORDER = ("frame", "explore", "intake", "clarify", "specify", "review", "baseline", "implementation", "change", "acceptance", "closed")
GOVERNED_INDEX = {name: index for index, name in enumerate(GOVERNED_ORDER)}
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
EN_GUIDANCE = {
    "GATE-NOT-FILE": ("The artifact cannot be read.", "Check the path, UTF-8 encoding, binary content and size."),
    "GATE-MISSING-INPUT": ("The selected profile has no artifact.", "Provide the main artifact for this stage."),
    "STAGE-ARTIFACT-TYPE": ("The artifact type does not match this stage.", "Start from the corresponding v5.4 template and keep artifact/stage metadata."),
    "STAGE-ANCHOR-MISSING": ("A required ADS semantic anchor is missing.", "Add the named ADS anchor and real content; headings may stay in the document language."),
    "STAGE-PLACEHOLDER": ("The artifact still contains placeholders.", "Replace each placeholder with evidence, an owned assumption or an owned UNK-* item."),
    "CLARIFY-P0-UNKNOWN": ("An open P0 unknown blocks the current stage.", "Close it, narrow scope, or set its real blocks_stage and reversal path."),
    "CLARIFY-P0-NOT-YET-BLOCKING": ("An open P0 unknown has not reached its blocking stage.", "Keep its owner and reversal path, and close it before blocks_stage."),
    "CLARIFY-UNKNOWN-OPEN": ("A non-P0 unknown remains open.", "Keep it owned and close it before its declared blocking stage."),
    "CLARIFY-SCOPE-EMPTY": ("In-scope or out-of-scope content is empty.", "State the real boundary; use an owned UNK-* if the boundary is undecided."),
    "CLARIFY-REQUIREMENT-REF-MISSING": ("The clarification brief is not linked to an intake REQ-*.", "Add requirement_refs in front matter."),
    "ASM-UNTESTED": ("An assumption has not been tested.", "Run the stated validation or keep it as a visible GAP; do not promote it to fact."),
    "ASM-TRACE-MISSING": ("An upstream ASM-* is not dispositioned in clarification.", "Carry, convert to UNK-*, or close it in assumption_refs/assumption_resolutions."),
    "DEC-NO-TRADEOFF": ("A DEC-* record has no option/trade-off evidence.", "Record the selected option, rejected alternative and reversal condition."),
}
ARTIFACT_STAGE = {
    "problem_brief": "frame",
    "solution_sketch": "explore",
    "assumption_register": "explore",
    "requirement_intake": "intake",
    "requirement_register": "intake",
    "requirement_brief": "clarify",
    "discovery_contract": "clarify",
    "decision_record": "clarify",
    "requirement_card": "specify",
    "unified_prd": "specify",
    "unified_requirement_prd": "specify",
    "review_record": "review",
    "baseline": "baseline",
    "change_package": "change",
    "change_request": "change",
    "acceptance_run": "acceptance",
}


@dataclass
class Artifact:
    path: Path
    text: str
    metadata: dict[str, Any]
    kind: str
    stage: str
    confidence: str = "declared"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_frontmatter(text: str) -> dict[str, Any]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.S)
    if not match:
        return {}
    try:
        value = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}
    return value if isinstance(value, dict) else {}


def infer_legacy(path: Path, text: str) -> tuple[str, str]:
    """Bounded compatibility only; this is not natural-language routing."""
    name = path.name.casefold()
    probes = (
        ("acceptance_run", ("arun-", "acceptance-run", "验收执行记录")),
        ("change_package", ("chg-", "change-package", "变更申请")),
        ("review_record", ("review-", "评审记录")),
        ("unified_prd", ("prd", "产品需求文档", "机器可读验收", "工程附录")),
        ("requirement_brief", ("requirement-brief", "需求澄清简报")),
        ("solution_sketch", ("solution-sketch", "方案探索")),
        ("problem_brief", ("problem-brief", "问题简报")),
    )
    sample = (name + "\n" + text[:16000]).casefold()
    for kind, markers in probes:
        if any(marker.casefold() in sample for marker in markers):
            return kind, ARTIFACT_STAGE[kind]
    return "unknown", "unknown"


def load_artifact(path: Path) -> Artifact:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError(f"artifact exceeds {MAX_ARTIFACT_BYTES // 1024 // 1024} MiB")
    text = path.read_text(encoding="utf-8-sig")
    if "\x00" in text:
        raise UnicodeError("binary/NUL content is not a text artifact")
    metadata: dict[str, Any] = {}
    if path.suffix.casefold() in {".yaml", ".yml", ".json"}:
        try:
            value = json.loads(text) if path.suffix.casefold() == ".json" else yaml.safe_load(text)
            metadata = value if isinstance(value, dict) else {}
        except (json.JSONDecodeError, yaml.YAMLError):
            metadata = {}
    else:
        metadata = markdown_frontmatter(text)
    kind = str(metadata.get("artifact", "")).strip().casefold()
    stage = str(metadata.get("stage", "")).strip().casefold()
    if not kind and metadata.get("assumptions") is not None:
        kind = "assumption_register"
    if not kind and metadata.get("review_id"):
        kind = "review_record"
    if not kind and metadata.get("change_id"):
        kind = "change_package"
    if not kind and (metadata.get("run_id") or metadata.get("acceptance_run_id")):
        kind = "acceptance_run"
    if kind in ARTIFACT_STAGE:
        mapped = ARTIFACT_STAGE[kind]
        if kind in {"requirement_card", "unified_prd", "unified_requirement_prd"} and stage in {"specify", "review", "baseline"}:
            mapped = stage
        return Artifact(path, text, metadata, kind, mapped, "declared")
    if stage in STAGE_INDEX:
        return Artifact(path, text, metadata, kind or "stage_artifact", stage, "declared")
    kind, stage = infer_legacy(path, text)
    return Artifact(path, text, metadata, kind, stage, "legacy_inferred")


def finding(severity: str, code: str, artifact: Path, message: str, fix: str) -> dict[str, Any]:
    message_en, fix_en = EN_GUIDANCE.get(
        code,
        (f"{code} violates the stage artifact contract.", "Use the matching v5.4 template and repair the referenced contract."),
    )
    return {
        "severity": severity,
        "code": code,
        "artifact": str(artifact),
        "ref": "",
        "message": message,
        "cause": message,
        "how_to_fix": fix,
        "repair_example": fix,
        "message_zh": message,
        "cause_zh": message,
        "fix_zh": fix,
        "repair_example_zh": fix,
        "message_en": message_en,
        "cause_en": message_en,
        "fix_en": fix_en,
        "repair_example_en": fix_en,
        "affected_consumers": ["product", "delivery"],
        "related_refs": [],
        "binding_source_refs": [],
    }


def localize_findings(findings: list[dict[str, Any]], language: str) -> None:
    if not language.casefold().startswith("en"):
        return
    for item in findings:
        item["message"] = item["message_en"]
        item["cause"] = item["cause_en"]
        item["how_to_fix"] = item["fix_en"]
        item["repair_example"] = item["repair_example_en"]


def anchor_count(text: str, name: str) -> int:
    return len(re.findall(rf"<!--\s*ADS:{re.escape(name)}(?:\s+[^>]*)?\s*-->", text, re.I))


def require_anchors(artifact: Artifact, names: tuple[str, ...], findings: list[dict[str, Any]]) -> None:
    for name in names:
        if not anchor_count(artifact.text, name):
            findings.append(finding(
                "BLOCK", "STAGE-ANCHOR-MISSING", artifact.path,
                f"缺少稳定语义锚点 ADS:{name}",
                f"使用对应 5.4 模板补充 <!-- ADS:{name} --> 及其真实内容；标题语言可以自定义。",
            ))


def has_placeholder(text: str) -> bool:
    return bool(re.search(r"\{[^{}]+\}|待补充|TBD|TODO|待确认内容", text, re.I))


def anchor_body(text: str, name: str) -> str:
    marker = re.search(rf"<!--\s*ADS:{re.escape(name)}(?:\s+[^>]*)?\s*-->", text, re.I)
    if not marker:
        return ""
    next_marker = re.search(r"<!--\s*ADS:[^>]+-->", text[marker.end():], re.I)
    end = marker.end() + next_marker.start() if next_marker else len(text)
    return text[marker.end():end]


def body_has_content(body: str) -> bool:
    lines = [
        re.sub(r"^[>*\s-]+", "", line).strip()
        for line in body.splitlines()
        if line.strip()
        and not line.lstrip().startswith(("<!--", "#"))
    ]
    payload = "\n".join(line for line in lines if line)
    return bool(payload)  # Placeholder text counts as draft content and is reported separately as GAP.


def table_cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def unknown_rows(text: str) -> list[dict[str, str]]:
    aliases = {
        "id": {"id", "编号"}, "priority": {"优先级", "priority"},
        "owner": {"责任人", "owner"}, "blocks_stage": {"blocks_stage", "阻断阶段"},
        "reversal": {"回退路径", "回退/缩范围路径", "回退/缩范围", "reversal path", "fallback"},
        "status": {"状态", "status"},
    }
    lines = text.splitlines()
    results: list[dict[str, str]] = []
    for index in range(len(lines) - 2):
        if not lines[index].lstrip().startswith("|") or not re.match(r"^\s*\|?\s*:?-{3,}", lines[index + 1]):
            continue
        headers = [cell.casefold() for cell in table_cells(lines[index])]
        positions = {
            key: next((pos for pos, header in enumerate(headers) if header in names), -1)
            for key, names in aliases.items()
        }
        cursor = index + 2
        while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
            cells = table_cells(lines[cursor])
            row_id = next((cell.upper() for cell in cells if re.fullmatch(r"UNK-[A-Z0-9-]+", cell, re.I)), "")
            if row_id:
                row = {"id": row_id}
                for key, pos in positions.items():
                    row[key] = cells[pos] if 0 <= pos < len(cells) else ""
                results.append(row)
            cursor += 1
    if results:
        return results
    for line in lines:
        if "UNK-" not in line or "|" not in line:
            continue
        cells = table_cells(line)
        if len(cells) >= 7 and re.fullmatch(r"UNK-[A-Z0-9-]+", cells[0], re.I):
            results.append({
                "id": cells[0].upper(), "priority": cells[1], "owner": cells[3],
                "blocks_stage": cells[4], "reversal": cells[5], "status": cells[6],
            })
    return results


def is_open(status: str) -> bool:
    return status.strip().casefold() in {"open", "pending", "待确认", "未关闭", "待处理"}


def validate_unknowns(artifact: Artifact, current_stage: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for row in unknown_rows(artifact.text):
        if not is_open(row.get("status", "")):
            continue
        missing = [key for key in ("owner", "blocks_stage", "reversal") if not row.get(key, "").strip()]
        if missing:
            findings.append(finding(
                "BLOCK", "CLARIFY-UNKNOWN-CONTRACT", artifact.path,
                f"{row['id']} 缺少 {', '.join(missing)}", "补齐责任人、blocks_stage、回退/缩范围路径和状态。",
            ))
            continue
        blocks_stage = row["blocks_stage"].strip().casefold()
        if blocks_stage not in GOVERNED_INDEX:
            findings.append(finding("BLOCK", "CLARIFY-UNKNOWN-STAGE", artifact.path, f"{row['id']} 的 blocks_stage 无效：{blocks_stage}", f"使用：{', '.join(GOVERNED_ORDER)}。"))
            continue
        priority = row.get("priority", "P1").strip().upper()
        if priority == "P0" and GOVERNED_INDEX[current_stage] >= GOVERNED_INDEX[blocks_stage]:
            findings.append(finding("P0_UNKNOWN", "CLARIFY-P0-UNKNOWN", artifact.path, f"{row['id']} 已阻断 {current_stage}", "由责任人关闭，或记录安全缩范围/回退路径。"))
        elif priority == "P0":
            findings.append(finding("GAP", "CLARIFY-P0-NOT-YET-BLOCKING", artifact.path, f"{row['id']} 必须在 {blocks_stage} 前关闭", "保留责任人和回退路径，并在 blocks_stage 前关闭。"))
        else:
            findings.append(finding("GAP", "CLARIFY-UNKNOWN-OPEN", artifact.path, f"{row['id']} 仍未关闭", "按责任人与 blocks_stage 跟踪关闭，不得静默推断。"))
    return findings


def upstream_assumption_ids(artifact: Artifact) -> set[str]:
    context = artifact.metadata.get("resume_context")
    if not isinstance(context, dict):
        return set()
    root = artifact.path.parent.resolve()
    found: set[str] = set()
    for item in context.get("prior_artifacts", []) or []:
        if not isinstance(item, dict) or str(item.get("stage", "")).casefold() != "explore":
            continue
        candidate = (root / Path(str(item.get("path", "")))).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file() and candidate.stat().st_size <= MAX_ARTIFACT_BYTES:
            try:
                found.update(re.findall(r"ASM-[A-Z0-9-]+", candidate.read_text(encoding="utf-8-sig"), re.I))
            except (OSError, UnicodeError):
                continue
    return {item.upper() for item in found}


def validate_assumption_trace(artifact: Artifact) -> list[dict[str, Any]]:
    upstream = upstream_assumption_ids(artifact)
    if not upstream:
        return []
    refs = {str(item).upper() for item in artifact.metadata.get("assumption_refs", []) or []}
    resolutions = artifact.metadata.get("assumption_resolutions", []) or []
    if isinstance(resolutions, list):
        refs.update(
            str(item.get("assumption_ref", "")).upper()
            for item in resolutions if isinstance(item, dict)
        )
    missing = sorted(upstream - refs)
    if not missing:
        return []
    return [finding(
        "GAP", "ASM-TRACE-MISSING", artifact.path,
        f"上游假设未承接、转未知项或关闭：{', '.join(missing)}",
        "在 assumption_refs 或 assumption_resolutions 中逐项登记 carried / converted_to_unknown / closed。",
    )]


def validate_resume(artifact: Artifact) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    context = artifact.metadata.get("resume_context")
    if context in (None, {}):
        return findings
    if not isinstance(context, dict):
        return [finding("BLOCK", "STAGE-RESUME-INVALID", artifact.path, "resume_context 必须是对象", "按 5.4 模板重建 resume_context。")]
    completed = context.get("completed_stages", [])
    if not isinstance(completed, list) or any(item not in STAGE_INDEX for item in completed):
        findings.append(finding("BLOCK", "STAGE-RESUME-STAGES", artifact.path, "completed_stages 含无效阶段", f"只使用：{', '.join(STAGES)}。"))
    elif any(STAGE_INDEX[left] > STAGE_INDEX[right] for left, right in zip(completed, completed[1:])):
        findings.append(finding("BLOCK", "STAGE-RESUME-ORDER", artifact.path, "completed_stages 顺序倒置", "按九工作站顺序排列已完成阶段。"))
    priors = context.get("prior_artifacts", [])
    if not isinstance(priors, list):
        findings.append(finding("BLOCK", "STAGE-RESUME-INVALID", artifact.path, "prior_artifacts 必须是数组", "每项填写 path、sha256、stage。"))
        return findings
    root = artifact.path.parent.resolve()
    for index, item in enumerate(priors):
        if not isinstance(item, dict) or not {"path", "sha256", "stage"}.issubset(item):
            findings.append(finding("BLOCK", "STAGE-RESUME-INVALID", artifact.path, f"prior_artifacts[{index}] 缺少 path/sha256/stage", "使用模板中的对象结构。"))
            continue
        relative = Path(str(item["path"]))
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            findings.append(finding("BLOCK", "STAGE-RESUME-PATH-ESCAPE", artifact.path, f"前序产物路径越界：{relative}", "仅引用当前工作目录内的相对路径。"))
            continue
        if not candidate.is_file():
            findings.append(finding("BLOCK", "STAGE-RESUME-MISSING", artifact.path, f"前序产物不存在：{relative}", "恢复文件或移除失效引用并重新评审。"))
            continue
        expected = str(item["sha256"]).casefold()
        if not re.fullmatch(r"[a-f0-9]{64}", expected):
            findings.append(finding("BLOCK", "STAGE-RESUME-HASH-INVALID", artifact.path, f"前序产物哈希格式无效：{relative}", "记录完整 SHA-256。"))
        elif sha256(candidate) != expected:
            findings.append(finding("BLOCK", "STAGE-RESUME-DRIFT", artifact.path, f"前序产物已漂移：{relative}", "确认变更、更新依赖产物后重新计算 SHA-256，不得静默续跑。"))
        if item["stage"] not in STAGE_INDEX:
            findings.append(finding("BLOCK", "STAGE-RESUME-STAGES", artifact.path, f"前序产物阶段无效：{item['stage']}", "使用九工作站之一。"))
    return findings


def gate_frame(artifact: Artifact) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if artifact.kind != "problem_brief":
        findings.append(finding("BLOCK", "STAGE-ARTIFACT-TYPE", artifact.path, "frame 需要 problem_brief", "使用 problem-brief-template.md。"))
    require_anchors(artifact, ("problem_owner", "pain_moment", "success_signal", "evidence_hypothesis", "unknowns", "next_step"), findings)
    if has_placeholder(artifact.text):
        findings.append(finding("GAP", "STAGE-PLACEHOLDER", artifact.path, "问题简报仍含占位内容", "用事实、显式假设或未知项替换占位符。"))
    return findings + validate_resume(artifact)


def gate_explore(artifact: Artifact) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if artifact.kind != "solution_sketch":
        findings.append(finding("BLOCK", "STAGE-ARTIFACT-TYPE", artifact.path, "explore 需要 solution_sketch", "使用 solution-sketch-template.md。"))
    require_anchors(artifact, ("problem_ref", "options", "assumptions", "recommendation", "next_validation"), findings)
    if anchor_count(artifact.text, "option") < 2:
        findings.append(finding("BLOCK", "EXPLORE-OPTIONS-TOO-FEW", artifact.path, "方案探索至少需要两个可比较选项", "为每个选项补结果、代价/风险和最小验证。"))
    if not anchor_count(artifact.text, "opt_out"):
        findings.append(finding("GAP", "EXPLORE-OPT-OUT-MISSING", artifact.path, "未显式比较“不做/延后/维持现状”", "增加 <!-- ADS:opt_out --> 选项，避免默认把做功能当成唯一答案。"))
    if "ASM-" not in artifact.text:
        findings.append(finding("GAP", "EXPLORE-ASSUMPTION-MISSING", artifact.path, "未登记可证伪假设", "对会影响推荐的假设使用 ASM-*，注明验证方法、责任人和状态。"))
    applicability_risk = re.search(r"竞品|competitor", artifact.text, re.I) and re.search(r"司法辖区|jurisdiction|文化|culture|本地化|合规适用", artifact.text, re.I)
    if applicability_risk and not re.search(r"DEC-COMPAT-|UNK-[A-Z0-9-]+", artifact.text, re.I):
        findings.append(finding("GAP", "EXPLORE-COMPAT-UNDECIDED", artifact.path, "竞品做法存在地区/文化/合规适用性风险，但未登记决策或未知项", "仅在适用性确有风险时登记 DEC-COMPAT-* 或有责任人的 UNK-*；普通竞品比较无需机械新增。"))
    if has_placeholder(artifact.text):
        findings.append(finding("GAP", "STAGE-PLACEHOLDER", artifact.path, "方案草图仍含占位内容", "用选项、证据、假设或未知项替换占位符。"))
    return findings + validate_resume(artifact)


def gate_clarify(artifact: Artifact, has_decision_sidecar: bool = False) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if artifact.kind not in {"requirement_brief", "discovery_contract"}:
        findings.append(finding("BLOCK", "STAGE-ARTIFACT-TYPE", artifact.path, "clarify 需要 requirement_brief 或兼容的 discovery_contract", "使用 requirement-brief-template.md；复杂治理项目也可继续使用 Discovery Contract。"))
    if artifact.kind == "requirement_brief":
        names = ["summary", "outcome", "users", "scope_in", "scope_out", "rules", "unknowns", "next_step"]
        if not has_decision_sidecar:
            names.append("decisions")
        require_anchors(artifact, tuple(names), findings)
        refs = artifact.metadata.get("requirement_refs")
        if not isinstance(refs, list) or not any(re.fullmatch(r"REQ-[A-Z0-9-]+", str(item), re.I) for item in refs):
            findings.append(finding("GAP", "CLARIFY-REQUIREMENT-REF-MISSING", artifact.path, "需求澄清简报没有承接 intake 的 REQ-*", "在 front matter 增加 requirement_refs: [REQ-*]。"))
        for name in ("scope_in", "scope_out"):
            body = anchor_body(artifact.text, name)
            if anchor_count(artifact.text, name) and not body_has_content(body):
                findings.append(finding("BLOCK", "CLARIFY-SCOPE-EMPTY", artifact.path, f"ADS:{name} 没有真实边界内容", "写明纳入/不做边界；未决定时转成有责任人的 UNK-*。"))
        decision_body = anchor_body(artifact.text, "decisions")
        if "DEC-" in decision_body and not re.search(r"取舍|未采用|未选|而非|trade[ -]?off|alternative|option", decision_body, re.I):
            findings.append(finding("GAP", "DEC-NO-TRADEOFF", artifact.path, "DEC-* 只有结论，没有选项与取舍", "补充已选方案、未选方案及反转条件。"))
    rows = unknown_rows(artifact.text)
    if "UNK-" in artifact.text and not rows:
        findings.append(finding("BLOCK", "CLARIFY-UNKNOWN-UNSTRUCTURED", artifact.path, "未知项未形成可解析的结构化记录", "使用模板表格登记 ID、优先级、责任人、blocks_stage、回退路径和状态。"))
    findings.extend(validate_unknowns(artifact, "clarify"))
    if has_placeholder(artifact.text):
        findings.append(finding("GAP", "STAGE-PLACEHOLDER", artifact.path, "需求简报仍含占位内容", "未确定内容必须转成有责任人的 UNK-*，不得保留无主占位符。"))
    findings.extend(validate_assumption_trace(artifact))
    return findings + validate_resume(artifact)

def validate_decision_sidecar(sidecar: Artifact, brief: Artifact) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    require_anchors(sidecar, ("decision_log", "rejected_options", "unknowns", "accepted_risks", "next_step"), findings)
    decision_ids = set(re.findall(r"DEC-[A-Z0-9-]+", sidecar.text, re.I))
    if not decision_ids:
        findings.append(finding("BLOCK", "DEC-RECORD-EMPTY", sidecar.path, "决策侧车没有 DEC-*", "至少记录决策、选项与取舍、依据和决策人。"))
    brief_refs = set(re.findall(r"DEC-[A-Z0-9-]+", brief.text, re.I))
    missing = sorted(item.upper() for item in brief_refs - decision_ids)
    if missing:
        findings.append(finding("BLOCK", "DEC-RECORD-UNBOUND", sidecar.path, f"需求简报引用了未登记决策：{', '.join(missing)}", "补入决策侧车，或移除无效引用。"))
    if not re.search(r"决策人|decision owner", sidecar.text, re.I):
        findings.append(finding("BLOCK", "DEC-OWNER-MISSING", sidecar.path, "决策记录缺少决策人字段", "为每个 DEC-* 记录有权责任人。"))
    if decision_ids and not re.search(r"取舍|未采用|未选|而非|trade[ -]?off|alternative|option", sidecar.text, re.I):
        findings.append(finding("GAP", "DEC-NO-TRADEOFF", sidecar.path, "决策记录没有可审计的选项与取舍", "补充已选方案、被拒方案、拒绝原因和反转条件。"))
    if "UNK-" in sidecar.text and not unknown_rows(sidecar.text) and not re.search(r"UNK-[A-Z0-9-]+[^\n]*(?:closed|已关闭)", sidecar.text, re.I):
        findings.append(finding("BLOCK", "CLARIFY-UNKNOWN-UNSTRUCTURED", sidecar.path, "决策侧车中的开放未知项不可解析", "使用标准未知项表格登记完整合同。"))
    findings.extend(validate_unknowns(sidecar, "clarify"))
    if has_placeholder(sidecar.text):
        findings.append(finding("GAP", "STAGE-PLACEHOLDER", sidecar.path, "决策记录仍含占位内容", "用已确认决策或有责任人的 UNK-* 替换。"))
    return findings + validate_resume(sidecar)

def validate_assumption_sidecar(sidecar: Artifact, solution: Artifact) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    rows = sidecar.metadata.get("assumptions")
    if not isinstance(rows, list) or not rows:
        return [finding("BLOCK", "ASM-REGISTER-EMPTY", sidecar.path, "假设寄存器没有 assumptions", "至少登记一个可证伪 ASM-*。")]
    required = {"id", "statement", "category", "validation_method", "success_threshold", "failure_action", "owner", "status"}
    ids: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not required.issubset(row):
            findings.append(finding("BLOCK", "ASM-REGISTER-ROW", sidecar.path, f"assumptions[{index}] 字段不完整", "使用 assumption-register-template.yaml 补齐验证阈值、失败动作、责任人和状态。"))
            continue
        row_id = str(row["id"]).upper()
        ids.append(row_id)
        if not re.fullmatch(r"ASM-[A-Z0-9-]+", row_id):
            findings.append(finding("BLOCK", "ASM-ID-INVALID", sidecar.path, f"假设 ID 无效：{row['id']}", "使用 ASM-* 稳定 ID。"))
        if str(row.get("status", "")).casefold() == "untested":
            findings.append(finding("GAP", "ASM-UNTESTED", sidecar.path, f"{row_id} 尚未验证", "执行 validation_method，或保留 GAP，禁止把假设晋升为事实。"))
        if has_placeholder(yaml.safe_dump(row, allow_unicode=True)):
            findings.append(finding("GAP", "STAGE-PLACEHOLDER", sidecar.path, f"{row_id} 仍含占位内容", "填入可证伪陈述、阈值、责任人和失败动作。"))
    if len(ids) != len(set(ids)):
        findings.append(finding("BLOCK", "ASM-ID-DUPLICATE", sidecar.path, "假设寄存器存在重复 ID", "为每个假设保留唯一 ASM-*。"))
    solution_refs = {item.upper() for item in re.findall(r"ASM-[A-Z0-9-]+", solution.text, re.I)}
    missing = sorted(solution_refs - set(ids))
    if missing:
        findings.append(finding("BLOCK", "ASM-REGISTER-UNBOUND", sidecar.path, f"方案草图引用了未登记假设：{', '.join(missing)}", "补入寄存器，或移除无效引用。"))
    return findings + validate_resume(sidecar)

def result(profile: str, findings: list[dict[str, Any]], artifacts: list[Artifact], language: str = "zh-CN") -> tuple[int, dict[str, Any]]:
    localize_findings(findings, language)
    english = language.casefold().startswith("en")
    blocks = sum(item["severity"] == "BLOCK" for item in findings)
    p0 = sum(item["severity"] == "P0_UNKNOWN" for item in findings)
    gaps = sum(item["severity"] == "GAP" for item in findings)
    code = 2 if blocks else 3 if p0 else 1 if gaps else 0
    statuses = {0: "PASS", 1: "REVIEW_COMPLETE_WITH_GAPS", 2: "BLOCKED", 3: "BLOCKED_BY_P0_UNKNOWN"}
    return code, {
        "status": statuses[code],
        "profile": profile,
        "summary": {"blockers": blocks, "p0_unknowns": p0, "gaps": gaps, "findings": len(findings)},
        "coverage": ("Deterministic stage structure, ADS anchors and checkpoint hashes; not business correctness or approval" if english else "确定性阶段产物结构、稳定锚点和断点哈希；不判断业务正确性，不替代责任人评审"),
        "not_proven": (["customer/domain correctness", "solution value", "implementation/runtime behavior", "real acceptance"] if english else ["客户/领域正确性", "方案价值", "实现与运行时行为", "真实验收"]),
        "retry_command": "python scripts/ai_delivery_spec_cli.py gate --profile " + profile + " " + " ".join(f"--artifact {item.path}" for item in artifacts),
        "metrics": {"artifact_count": len(artifacts), "artifact_kinds": [item.kind for item in artifacts]},
        "findings": findings,
    }


def run_gate(args: argparse.Namespace) -> int:
    findings: list[dict[str, Any]] = []
    artifacts: list[Artifact] = []
    for path in args.artifact:
        try:
            artifacts.append(load_artifact(path))
        except (OSError, UnicodeError, ValueError) as exc:
            findings.append(finding("BLOCK", "GATE-NOT-FILE", path, f"无法读取产物：{exc}", "检查路径、UTF-8 编码、二进制内容和文件大小。"))
    if not artifacts:
        findings.append(finding("BLOCK", "GATE-MISSING-INPUT", Path("<artifact>"), f"profile={args.profile} 至少需要一个 --artifact", "提供该阶段的主产物。"))
    else:
        primary = next((item for item in artifacts if item.stage == args.profile), artifacts[0])
        if args.profile == "frame":
            findings.extend(gate_frame(primary))
        elif args.profile == "explore":
            findings.extend(gate_explore(primary))
            sidecars = [item for item in artifacts if item.kind == "assumption_register"]
            for sidecar in sidecars:
                findings.extend(validate_assumption_sidecar(sidecar, primary))
        else:
            decision_sidecars = [item for item in artifacts if item.kind == "decision_record"]
            findings.extend(gate_clarify(primary, bool(decision_sidecars)))
            for sidecar in decision_sidecars:
                findings.extend(validate_decision_sidecar(sidecar, primary))
        for item in artifacts:
            if item is not primary and not (
                (args.profile == "explore" and item.kind == "assumption_register")
                or (args.profile == "clarify" and item.kind == "decision_record")
            ):
                findings.extend(validate_resume(item))
    language = str(primary.metadata.get("document_language", "zh-CN")) if artifacts else "zh-CN"
    code, payload = result(args.profile, findings, artifacts, language)
    english = language.casefold().startswith("en")
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        summary = payload["summary"]
        print(f"{payload['status']} profile={args.profile} blockers={summary['blockers']} p0_unknowns={summary['p0_unknowns']} gaps={summary['gaps']}")
        print("NOT_PROVEN: " + ("; " if english else "；").join(payload["not_proven"]))
        limit = 1 if args.diagnostics == "first" else 12 if args.diagnostics == "summary" else args.max_findings
        fix_label = "Fix" if english else "修复"
        for item in findings[:max(limit, 0)]:
            print(f"{item['severity']} {item['code']}: {item['message']}\n  {fix_label}: {item['how_to_fix']}")
        if findings:
            print("RETRY: " + payload["retry_command"])
    return code


def run_route(args: argparse.Namespace) -> int:
    artifacts: list[Artifact] = []
    findings: list[dict[str, Any]] = []
    for path in args.artifact:
        try:
            item = load_artifact(path)
            artifacts.append(item)
            findings.extend(validate_resume(item))
        except (OSError, UnicodeError, ValueError) as exc:
            findings.append(finding("BLOCK", "ROUTE-ARTIFACT-READ", path, f"无法读取已有产物：{exc}", "检查路径、UTF-8 编码、二进制内容和文件大小。"))
    target = args.target
    known = [item for item in artifacts if item.stage in STAGE_INDEX]
    current = max(known, key=lambda item: STAGE_INDEX[item.stage]) if known else None
    stages_present = {item.stage for item in known}
    already_reached = bool(
        current
        and STAGE_INDEX[current.stage] >= STAGE_INDEX[target]
        and not (current.stage == "change" and target == "baseline")
    )
    missing: set[str] = set()
    if not already_reached:
        if target == "review" and "specify" not in stages_present:
            missing = {"specify"}
        elif target == "baseline":
            missing = {"specify", "review"} - stages_present
        elif target in {"change", "acceptance"} and "baseline" not in stages_present:
            missing = {"baseline"}
    if missing:
        findings.append(finding(
            "BLOCK", "ROUTE-PREREQUISITE", Path("<route>"),
            f"{target} 缺少前置产物：{', '.join(sorted(missing))}",
            "提供当前统一 PRD/需求卡及相应评审/基线引用；不要凭空进入下游阶段。",
        ))
    if current and target == "acceptance" and current.stage == "baseline":
        path = ["baseline", "acceptance"]
        entry = "baseline"
    elif current and target == "acceptance" and current.stage == "change":
        path = ["change", "baseline", "acceptance"]
        entry = "change"
    elif current and target == "baseline" and current.stage == "change":
        path = ["change", "baseline"]
        entry = "change"
    elif current and STAGE_INDEX[current.stage] < STAGE_INDEX[target]:
        path = list(STAGES[STAGE_INDEX[current.stage]: STAGE_INDEX[target] + 1])
        entry = current.stage
    else:
        path = [target]
        entry = target
    blocks = sum(item["severity"] == "BLOCK" for item in findings)
    payload = {
        "status": "BLOCKED" if blocks else "PASS",
        "target_stage": target,
        "recommended_entry_stage": entry,
        "path": path,
        "current_artifact_stage": current.stage if current else None,
        "artifacts": [{"path": str(item.path), "artifact": item.kind, "stage": item.stage, "confidence": item.confidence} for item in artifacts],
        "findings": findings,
        "rule": "显式 target_stage 由用户/Agent 的语义判断提供；本工具不读取自然语言关键词，也不覆盖否定约束。",
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload['status']} target={target} entry={entry} path={' -> '.join(path)}")
        for item in findings:
            print(f"{item['severity']} {item['code']}: {item['message_zh']}")
    return 2 if blocks else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Delivery Spec 5.4 stage contract helper")
    sub = parser.add_subparsers(dest="command", required=True)
    gate = sub.add_parser("gate")
    gate.add_argument("--profile", choices=EARLY_PROFILES, required=True)
    gate.add_argument("--artifact", type=Path, action="append", default=[])
    gate.add_argument("--format", choices=("concise", "json"), default="concise")
    gate.add_argument("--diagnostics", choices=("first", "summary", "full"), default="first")
    gate.add_argument("--max-findings", type=int, default=20)
    gate.set_defaults(func=run_gate)
    route = sub.add_parser("route")
    route.add_argument("--target", choices=STAGES, required=True)
    route.add_argument("--artifact", type=Path, action="append", default=[])
    route.add_argument("--format", choices=("concise", "json"), default="concise")
    route.set_defaults(func=run_route)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
