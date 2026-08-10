"""v5.4 workstations: semantic boundary, early artifacts, resume and CLI compatibility."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "ai_delivery_spec_cli.py"
STAGE = ROOT / "scripts" / "stage_contract.py"
failures: list[str] = []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=ROOT,
        text=True, encoding="utf-8", capture_output=True,
    )


def frontmatter(kind: str, stage: str, resume: dict | None = None, language: str = "zh-CN") -> str:
    meta = {
        "artifact": kind, "stage": stage, "schema_version": "5.4.0",
        "version": "0.1", "status": "draft", "document_language": language,
        "project_id": "PROJECT-TEST",
    }
    if kind == "requirement_brief":
        meta.update({"requirement_refs": ["REQ-CORE-001"], "assumption_refs": [], "assumption_resolutions": []})
    if resume is not None:
        meta["resume_context"] = resume
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n"


def good_frame(resume: dict | None = None) -> str:
    return frontmatter("problem_brief", "frame", resume) + """# 问题简报
<!-- ADS:problem_owner -->
## 人与责任
企业填报员遇到问题，产品负责人负责结果。
<!-- ADS:pain_moment -->
## 痛点时刻
每月上报前需人工逐项核对，遗漏会被退回。
<!-- ADS:success_signal -->
## 成功信号
一次发现全部缺项，退回率下降。
<!-- ADS:evidence_hypothesis -->
## 事实与假设
事实来自 SRC-001；假设是集中预检能减少退回。
<!-- ADS:unknowns -->
## 未知
UNK-FRAME-001 由业务负责人在 intake 前确认。
<!-- ADS:next_step -->
## 下一步
进入方案探索。
"""


def good_explore() -> str:
    return frontmatter("solution_sketch", "explore") + """# 方案探索
<!-- ADS:problem_ref -->
## 问题
引用 SRC-001。
<!-- ADS:options -->
## 选项
<!-- ADS:option OPT-001 -->
### OPT-001 集中预检
结果：一次提示；风险：规则维护；验证：纸面走查。
<!-- ADS:option OPT-002 -->
### OPT-002 分项提示
结果：就近修复；风险：路径更长；验证：可用性测试。
<!-- ADS:opt_out -->
### OPT-000 维持现状
退回率可接受时不开发。
<!-- ADS:assumptions -->
## 假设
ASM-001：用户愿意先预检；验证方法为 5 人任务测试；责任人为产品；状态 untested。
<!-- ADS:recommendation -->
## 推荐
先验证 OPT-001，失败退回 OPT-002。
<!-- ADS:next_validation -->
## 下一验证
5 人中 4 人一次完成才继续。
"""


def clarify(open_p0: bool, blocks_stage: str = "baseline") -> str:
    row = f"| `UNK-001` | P0 | 身份键 | 客户 | {blocks_stage} | 缩为人工核对 | open |" if open_p0 else "| `UNK-001` | P1 | 文案 | 产品 | baseline | 使用默认文案 | closed |"
    return frontmatter("requirement_brief", "clarify") + f"""# 需求澄清简报
<!-- ADS:summary -->
## 摘要
企业可预检并提交三类数据。
<!-- ADS:outcome -->
## 目标
退回率下降；按成功提交数/提交数计算。
<!-- ADS:users -->
## 角色
企业填报员发起，监管员接收。
<!-- ADS:scope_in -->
## 范围
企业、人员、车辆数据。
<!-- ADS:scope_out -->
## 非目标
不含维修数据。
<!-- ADS:decisions -->
## 决策
DEC-001 选择全部阻断而非部分成功，客户确认，来源 SRC-001。
<!-- ADS:rules -->
## 规则
BR-001 提交前拉取配置，失败保留待办，验收 AC-001。
<!-- ADS:unknowns -->
## 未知项
| ID | 优先级 | 内容 | 责任人 | blocks_stage | 回退路径 | 状态 |
|---|---|---|---|---|---|---|
{row}
<!-- ADS:next_step -->
## 下一步
READY_FOR_UNIFIED_PRD。
"""


schema = json.loads((ROOT / "schemas" / "assumption-register.schema.json").read_text(encoding="utf-8"))
sample = yaml.safe_load((ROOT / "references" / "templates" / "assumption-register-template.yaml").read_text(encoding="utf-8"))
schema_errors = list(Draft202012Validator(schema).iter_errors(sample))
if schema_errors:
    failures.extend(f"assumption template/schema mismatch: {item.message}" for item in schema_errors)
intake_schema = json.loads((ROOT / "schemas" / "requirement-intake.schema.json").read_text(encoding="utf-8"))
intake_sample = yaml.safe_load((ROOT / "references" / "templates" / "requirement-intake-template.yaml").read_text(encoding="utf-8"))
intake_errors = list(Draft202012Validator(intake_schema).iter_errors(intake_sample))
if intake_errors:
    failures.extend(f"intake template/schema mismatch: {item.message}" for item in intake_errors)

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
for marker in ("entry_stage", "target_stage", "否定约束", "references/stages.md"):
    if marker not in skill:
        failures.append(f"SKILL.md misses routing marker: {marker}")
if "--request" in (ROOT / "scripts" / "stage_contract.py").read_text(encoding="utf-8"):
    failures.append("stage_contract.py must not expose keyword-based --request routing")
adapters = (ROOT / "references" / "tool-adapters.md").read_text(encoding="utf-8")
for marker in ("Moonshot / Kimi", "Anthropic / Claude", "OpenAI / Codex", "Z.AI / GLM", "DeepSeek", "Alibaba / Qwen"):
    if marker not in adapters:
        failures.append(f"tool adapters miss current model family: {marker}")

with tempfile.TemporaryDirectory(prefix="ads-v540-") as temp_name:
    temp = Path(temp_name)
    frame = temp / "problem-brief.md"
    frame.write_text(good_frame(), encoding="utf-8")
    result = run("gate", "--profile", "frame", "--artifact", str(frame), "--format", "json")
    frame_payload = json.loads(result.stdout)
    if result.returncode != 0 or frame_payload.get("status") != "PASS":
        failures.append("valid frame artifact did not pass: " + result.stdout + result.stderr)
    gate_schema_for_result = json.loads((ROOT / "schemas" / "gate-result.schema.json").read_text(encoding="utf-8"))
    result_errors = list(Draft202012Validator(gate_schema_for_result).iter_errors(frame_payload))
    if result_errors:
        failures.extend(f"early gate output violates gate-result schema: {item.message}" for item in result_errors)

    explore = temp / "solution-sketch.md"
    explore.write_text(good_explore(), encoding="utf-8")
    result = run("gate", "--profile", "explore", "--artifact", str(explore), "--format", "json")
    if result.returncode != 0 or json.loads(result.stdout).get("status") != "PASS":
        failures.append("valid explore artifact did not pass: " + result.stdout + result.stderr)

    assumption = temp / "assumptions.yaml"
    assumption.write_text(yaml.safe_dump({
        "artifact": "assumption_register", "stage": "explore", "assumptions": [{
            "id": "ASM-001", "statement": "用户愿意先预检", "category": "desirability",
            "validation_method": "5人任务测试", "success_threshold": "4人一次完成",
            "failure_action": "改用分项提示", "owner": "产品负责人", "status": "testing",
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    result = run("gate", "--profile", "explore", "--artifact", str(explore), "--artifact", str(assumption), "--format", "json")
    if result.returncode != 0:
        failures.append("valid optional assumption sidecar did not bind: " + result.stdout + result.stderr)

    brief = temp / "requirement-brief.md"
    brief.write_text(clarify(True, "baseline"), encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    payload = json.loads(result.stdout)
    if result.returncode != 1 or "CLARIFY-P0-NOT-YET-BLOCKING" not in {item["code"] for item in payload["findings"]}:
        failures.append("future-stage P0 unknown did not remain a visible GAP: " + result.stdout + result.stderr)
    brief.write_text(clarify(True, "clarify"), encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    payload = json.loads(result.stdout)
    if result.returncode != 3 or payload.get("status") != "BLOCKED_BY_P0_UNKNOWN":
        failures.append("current-stage P0 unknown did not use the global P0 status: " + result.stdout + result.stderr)

    brief.write_text(clarify(False), encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    if result.returncode != 0:
        failures.append("closed clarification brief did not pass: " + result.stdout + result.stderr)

    brief.write_text(clarify(False).replace("<!-- ADS:decisions -->", "<!-- decisions moved to sidecar -->"), encoding="utf-8")
    decision = temp / "decision-record.md"
    decision.write_text(frontmatter("decision_record", "clarify") + """# 决策记录
<!-- ADS:decision_log -->
## 已固化决策
DEC-001 全部阻断；选择整体失败而非部分成功；依据 SRC-001；决策人：客户负责人。
<!-- ADS:rejected_options -->
## 未采用选项
部分成功因一致性风险未采用，复议条件为二期批次化。
<!-- ADS:unknowns -->
## 剩余未知
UNK-001 已关闭。
<!-- ADS:accepted_risks -->
## 接受风险
客户负责人接受提示信息较长的风险。
<!-- ADS:next_step -->
## 下一步
进入 specify。
""", encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--artifact", str(decision), "--format", "json")
    if result.returncode != 0:
        failures.append("valid optional decision sidecar did not bind: " + result.stdout + result.stderr)
    decision.write_text(decision.read_text(encoding="utf-8").replace("UNK-001 已关闭。", "| UNK-002 | P0 | 数据权威 | 客户 | baseline | 缩范围 | open |"), encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--artifact", str(decision), "--format", "json")
    if result.returncode != 1:
        failures.append("future-stage P0 in decision sidecar was not a GAP: " + result.stdout + result.stderr)
    decision.write_text(decision.read_text(encoding="utf-8").replace("| baseline |", "| clarify |"), encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--artifact", str(decision), "--format", "json")
    if result.returncode != 3:
        failures.append("current-stage P0 in decision sidecar did not block: " + result.stdout + result.stderr)

    prior = temp / "prior.md"
    prior.write_text("approved problem evidence\n", encoding="utf-8")
    digest = hashlib.sha256(prior.read_bytes()).hexdigest()
    resume = {
        "completed_stages": ["frame"],
        "prior_artifacts": [{"path": "prior.md", "sha256": digest, "stage": "frame"}],
        "open_threads": [], "next_stage_options": ["explore"],
    }
    frame.write_text(good_frame(resume), encoding="utf-8")
    result = run("gate", "--profile", "frame", "--artifact", str(frame), "--format", "json")
    if result.returncode != 0:
        failures.append("matching resume hash did not pass: " + result.stdout + result.stderr)
    prior.write_text("silently changed\n", encoding="utf-8")
    result = run("gate", "--profile", "frame", "--artifact", str(frame), "--format", "json")
    if result.returncode != 2 or "STAGE-RESUME-DRIFT" not in {item["code"] for item in json.loads(result.stdout)["findings"]}:
        failures.append("resume drift was not blocked: " + result.stdout + result.stderr)

    legacy_prd = temp / "legacy-product-PRD.md"
    legacy_prd.write_text("# 产品需求文档\n\n## 业务规则\n内容\n## 验收标准\n内容\n", encoding="utf-8")
    result = run("route-stage", "--target", "review", "--artifact", str(legacy_prd), "--format", "json")
    route = json.loads(result.stdout)
    if result.returncode != 0 or route.get("current_artifact_stage") != "specify":
        failures.append("legacy PRD could not continue at review: " + result.stdout + result.stderr)

    review_only = temp / "review-record.yaml"
    review_only.write_text(yaml.safe_dump({"artifact": "review_record", "stage": "review", "review_id": "REVIEW-001"}), encoding="utf-8")
    result = run("route-stage", "--target", "baseline", "--artifact", str(review_only), "--format", "json")
    if result.returncode != 2:
        failures.append("review record without its specification was allowed to baseline: " + result.stdout + result.stderr)

    baselined = temp / "baselined-prd.md"
    baselined.write_text(frontmatter("unified_prd", "baseline") + "# 产品需求文档\n", encoding="utf-8")
    result = run("route-stage", "--target", "acceptance", "--artifact", str(baselined), "--format", "json")
    acceptance_route = json.loads(result.stdout)
    if result.returncode != 0 or acceptance_route.get("path") != ["baseline", "acceptance"]:
        failures.append("declared baselined PRD could not continue to acceptance: " + result.stdout + result.stderr)

    result = run("route-stage", "--target", "review", "--format", "json")
    if result.returncode != 2 or json.loads(result.stdout).get("status") != "BLOCKED":
        failures.append("review without a specification was not blocked: " + result.stdout + result.stderr)

    for target in ("baseline", "change", "acceptance"):
        result = run("route-stage", "--target", target, "--format", "json")
        if result.returncode != 2 or json.loads(result.stdout).get("status") != "BLOCKED":
            failures.append(f"{target} without a specification/baseline was not blocked: " + result.stdout + result.stderr)

    result = run("route-stage", "--target", "clarify", "--format", "json")
    route = json.loads(result.stdout)
    if result.returncode != 0 or route.get("recommended_entry_stage") != "clarify":
        failures.append("direct entry to clarify was incorrectly forced through frame/explore: " + result.stdout + result.stderr)

    intake = temp / "intake.yaml"
    intake.write_text((ROOT / "references" / "templates" / "requirement-intake-template.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    result = run("route-stage", "--target", "clarify", "--artifact", str(intake), "--format", "json")
    intake_route = json.loads(result.stdout)
    if result.returncode != 0 or intake_route.get("current_artifact_stage") != "intake":
        failures.append("official intake was not recognized by stage routing: " + result.stdout + result.stderr)

    custom = temp / "custom"
    result = run("init-custom", "--output", str(custom), "--force")
    candidate = custom / "learning" / "candidates" / "project-local" / "CAND-EXAMPLE.yaml"
    candidate_doc = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    if not isinstance(candidate_doc.get("created_at"), str):
        failures.append("init-custom created_at is not a schema string")
    result = run("candidate", "validate", "--input", str(candidate))
    if result.returncode != 0:
        failures.append("fresh init-custom candidate did not validate: " + result.stdout + result.stderr)

    markdown_card = temp / "requirement-card.md"
    markdown_card.write_text("# 需求卡\n", encoding="utf-8")
    result = run("gate", "--profile", "requirement", "--requirement", str(markdown_card))
    if result.returncode != 2 or "--profile prd" not in result.stdout:
        failures.append("Markdown requirement input did not receive profile correction guidance: " + result.stdout + result.stderr)

    bom_frame = temp / "bom-frame.md"
    bom_frame.write_bytes(b"\xef\xbb\xbf" + good_frame().replace("\n", "\r\n").encode("utf-8"))
    result = run("gate", "--profile", "frame", "--artifact", str(bom_frame), "--format", "json")
    if result.returncode != 0:
        failures.append("UTF-8 BOM/CRLF artifact did not pass: " + result.stdout + result.stderr)

    malformed = temp / "malformed.yaml"
    malformed.write_text("artifact: [\n", encoding="utf-8")
    empty = temp / "empty.md"
    empty.write_text("", encoding="utf-8")
    binary = temp / "binary.md"
    binary.write_bytes(b"\x00\x01\x02")
    oversized = temp / "oversized.md"
    oversized.write_bytes(b"x" * (8 * 1024 * 1024 + 1))
    for boundary in (malformed, empty, binary, oversized):
        result = run("gate", "--profile", "frame", "--artifact", str(boundary), "--format", "json")
        try:
            boundary_payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            failures.append(f"boundary input leaked non-JSON output for {boundary.name}: " + result.stdout + result.stderr)
            continue
        if result.returncode != 2 or boundary_payload.get("status") != "BLOCKED":
            failures.append(f"boundary input was not safely blocked for {boundary.name}: " + result.stdout + result.stderr)

    english_frame = temp / "english-frame.md"
    english_frame.write_text(frontmatter("problem_brief", "frame", language="en-US") + """# Problem Brief
<!-- ADS:problem_owner -->\nOwner and user are known.
<!-- ADS:pain_moment -->\nA recurring failure is evidenced.
<!-- ADS:success_signal -->\nSuccess has an observable signal.
<!-- ADS:evidence_hypothesis -->\nSRC-001 and ASM-001 are separated.
<!-- ADS:unknowns -->\nNo open unknowns.
""", encoding="utf-8")
    result = run("gate", "--profile", "frame", "--artifact", str(english_frame), "--diagnostics", "full")
    if result.returncode != 2 or "A required ADS semantic anchor is missing" not in result.stdout or "缺少稳定语义锚点" in result.stdout:
        failures.append("en-US finding did not follow document language: " + result.stdout + result.stderr)

    empty_scope = re.sub(r"(<!-- ADS:scope_in -->\n## 范围\n).*?(?=<!-- ADS:scope_out -->)", r"\1", clarify(False), flags=re.S)
    brief.write_text(empty_scope, encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    if result.returncode != 2 or "CLARIFY-SCOPE-EMPTY" not in {item["code"] for item in json.loads(result.stdout)["findings"]}:
        failures.append("empty scope was not blocked: " + result.stdout + result.stderr)

    no_tradeoff = clarify(False).replace("选择全部阻断而非部分成功", "全部阻断")
    brief.write_text(no_tradeoff, encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    if result.returncode != 1 or "DEC-NO-TRADEOFF" not in {item["code"] for item in json.loads(result.stdout)["findings"]}:
        failures.append("decision without trade-off was not a GAP: " + result.stdout + result.stderr)

    assumption_doc = yaml.safe_load(assumption.read_text(encoding="utf-8"))
    assumption_doc["assumptions"][0]["status"] = "untested"
    assumption.write_text(yaml.safe_dump(assumption_doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    result = run("gate", "--profile", "explore", "--artifact", str(explore), "--artifact", str(assumption), "--format", "json")
    if result.returncode != 1 or "ASM-UNTESTED" not in {item["code"] for item in json.loads(result.stdout)["findings"]}:
        failures.append("untested assumption was not preserved as a GAP: " + result.stdout + result.stderr)

    upstream = temp / "upstream-explore.md"
    upstream.write_text(good_explore(), encoding="utf-8")
    resume = {
        "completed_stages": ["explore"],
        "prior_artifacts": [{"path": upstream.name, "sha256": hashlib.sha256(upstream.read_bytes()).hexdigest(), "stage": "explore"}],
        "open_threads": [], "next_stage_options": ["clarify"],
    }
    brief_body = re.sub(r"\A---.*?---\n\n", "", clarify(False), flags=re.S)
    brief.write_text(frontmatter("requirement_brief", "clarify", resume) + brief_body, encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    if result.returncode != 1 or "ASM-TRACE-MISSING" not in {item["code"] for item in json.loads(result.stdout)["findings"]}:
        failures.append("upstream ASM was not traced into clarification: " + result.stdout + result.stderr)
    brief.write_text(brief.read_text(encoding="utf-8").replace("assumption_refs: []", "assumption_refs:\n- ASM-001"), encoding="utf-8")
    result = run("gate", "--profile", "clarify", "--artifact", str(brief), "--format", "json")
    if result.returncode != 0:
        failures.append("explicit ASM carry-forward did not close trace GAP: " + result.stdout + result.stderr)

    for sector, role, scope in (
        ("retail", "运营专员", "订单退款"),
        ("healthcare", "医院审核员", "转诊申请"),
        ("traffic-data", "企业填报员", "人车企数据上报"),
    ):
        sector_brief = clarify(False).replace("企业填报员", role).replace("企业、人员、车辆数据", scope)
        sector_path = temp / f"{sector}-brief.md"
        sector_path.write_text(sector_brief, encoding="utf-8")
        result = run("gate", "--profile", "clarify", "--artifact", str(sector_path), "--format", "json")
        if result.returncode != 0:
            failures.append(f"generic clarify contract regressed in {sector}: " + result.stdout + result.stderr)


gate_schema = json.loads((ROOT / "schemas" / "gate-result.schema.json").read_text(encoding="utf-8"))
profiles = gate_schema["$defs"]["artifactGate"]["properties"]["profile"]["enum"]
for profile in ("frame", "explore", "clarify"):
    if profile not in profiles:
        failures.append(f"gate-result schema misses early profile: {profile}")

if failures:
    for item in failures:
        print("FAIL: " + item)
    raise SystemExit(1)

print("PASS: v5.4 stage workstations preserve semantic routing, early artifacts, P0 blocking, resume hashes and legacy continuation")
