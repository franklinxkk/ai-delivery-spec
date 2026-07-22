"""v5.3.x regression: authority, clarification, prototype evidence and handoff."""

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
GATE = ROOT / "scripts" / "quality_gate.py"
CLI = ROOT / "scripts" / "ai_delivery_spec_cli.py"
CHANGE_VALIDATOR = ROOT / "scripts" / "validators" / "validate_change_package.py"
ARUN_VALIDATOR = ROOT / "scripts" / "validators" / "validate_acceptance_run.py"
FIXTURE = ROOT / "maintainer" / "tests" / "fixtures" / "coding-l2.md"
failures: list[str] = []
card_lifecycle_results: list[str] = []

for relative, markers in {
    "references/lifecycle.md": (
        "Decision-Tree Clarification", "self-check gate", "recommended answer",
        "Only P0/P1 branches", "is unavailable",
    ),
    "references/prototype.md": (
        "DEC-AESTHETIC-*", "explicit taboo", "--acceptance-run",
        "browser_evidence_status", "region-REG-*",
    ),
    "references/troubleshooting.md": (
        "Exact-ID And Dynamic-Anchor Migration", "${act}", "dataset.action",
        "PROTO-BROWSER-EVIDENCE-MISSING",
    ),
}.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            failures.append(f"{relative} misses the current v5.3.x contract marker: {marker}")


def run_gate(*args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(GATE), *args, "--format", "json"], cwd=ROOT,
        text=True, encoding="utf-8", capture_output=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(result.stdout + result.stderr) from exc
    return result.returncode, payload


def codes(payload: dict) -> set[str]:
    return {item["code"] for item in payload["findings"]}


def with_frontmatter(document: str, updates: dict) -> str:
    match = __import__("re").match(r"\A---\s*\n(.*?)\n---\s*\n", document, __import__("re").S)
    current = yaml.safe_load(match.group(1)) if match else {}
    current.update(updates)
    body = document[match.end():] if match else document
    return "---\n" + yaml.safe_dump(current, allow_unicode=True, sort_keys=False) + "---\n\n" + body


def render_requirement_card(case: dict[str, str]) -> str:
    req = case["req"]
    act = case["act"]
    ac_positive = case["ac_positive"]
    ac_recovery = case["ac_recovery"]
    return f"""---
artifact: requirement_card
baseline_version: 1.0
delivery_level: L1
delivery_shape: requirement_card
document_language: zh-CN
language_source: user_request
bilingual: false
activated_facets: [ui]
open_p0_unknown_ids: []
status: baselined
---

# {case['title']}需求卡

## 0. 文档控制与 30 秒摘要

| 项目 | 内容 |
|---|---|
| REQ ID / 版本 | `{req}` / `v1.0` |
| 负责人 / 确认人 | 产品负责人 / {case['role_name']}代表 |
| 准入结论 | accept；单角色、可逆、局部读取体验调整 |
| 一句话结果 | {case['outcome']} |
| 成功信号 | 正向与恢复验收均通过，原业务数据和权限不改变 |

## 1. 来源、问题与价值

来源`{case['src']}`是现有项目材料中的可观察页面和字段。当前用户需要通过重复浏览或手工查找
才能完成该局部任务。增加一个不持久化业务状态的轻量控件，可减少查找步骤且不改变原有数据。

## 2. 目标、范围与非目标

- 目标：{case['outcome']}。
- 本期范围：只修改`{case['view']}`的展示与本地查询参数，不新增业务实体、审批或跨系统写入。
- 明确不做：不改变数据范围、后端权限、原记录状态、导入导出和统计口径。
- 约束与依赖：沿用页面已有字段来源；权限仍由原列表查询守卫控制。

## 3. 角色、用户故事与权限

| ROLE/REQ | 场景 | 用户故事 | 数据/权限边界 |
|---|---|---|---|
| `{case['role']}` / `{req}` | {case['scene']} | 作为{case['role_name']}，我希望{case['story']}，从而减少重复查找。 | 仅查看原本有权访问的记录；不得扩大组织、租户或所有者范围。 |

## 4. 用户旅程、主流程、异常与状态

入口`{case['view']}` → 执行`{act}` → 页面刷新当前列表 → 用户看到符合条件的记录 → 清除条件恢复默认。
查询失败时保留控件值并显示可重试错误；空结果显示空态与“清除条件”，无权时仍显示原无权页。

| FLOW/ACT | 前置与输入 | 可见结果 | 领域/状态结果 | 失败与恢复 | AC |
|---|---|---|---|---|---|
| `{case['flow']}` / `{act}` | `{case['role']}`已进入页面；输入`{case['field']}` | {case['visible_result']} | 只更新查询视图，不写业务数据 | 错误保留输入并可重试；清除后恢复默认 | `{ac_positive}`、`{ac_recovery}` |

## 5. 规则、字段与条件规格

- 页面入口与布局：控件放在现有列表筛选区，不新增导航和弹窗。
- 字段与控件：`{case['field']}`使用{case['control']}；默认值为“{case['default']}”。
- 动作权限：`{act}`对原页面可见角色开放；服务端继续应用原数据范围，不因控件值放宽权限。
- 页面状态：default显示默认结果；loading禁用重复触发；empty显示清除入口；error保留输入；no_permission不返回记录。
- 校验与长度：控件只接受既有选项或布尔/排序枚举，不允许自由输入未知值。
- 失败恢复：查询失败不改变业务数据，用户可以重试、清除或离开页面。
- `stateful`不适用：没有持久业务状态转换。
- `data_submission`不适用：只读查询，不上报或写回数据。
- `integration`、`batch_io`、`high_risk`不适用：不新增外部接口、批量文件或高风险决策。

## 6. 验收与测试

| AC/TEST | Given 前置/角色 | When 操作/输入 | Then 可见结果 | And 领域结果 | 反例/证据 |
|---|---|---|---|---|---|
| `{ac_positive}` / `{case['test_positive']}` | 有权{case['role_name']}进入页面且存在匹配/不匹配记录 | 执行`{act}`并选择非默认值 | {case['visible_result']} | 原记录、权限和总数据不变 | 截图/查询参数/结果集合对比 |
| `{ac_recovery}` / `{case['test_recovery']}` | 查询被模拟为失败或无匹配结果 | 保持条件并重试或清除 | 显示错误/空态；重试成功或清除后恢复默认 | 不产生写入和越权数据 | 错误态截图/请求日志 |

## 7. 未知项与升级判断

P0/P1未知项为空。字段来源、默认值、角色和恢复路径均由现有页面证据确认。若后续要求保存个人偏好、
改变数据范围、跨端同步、统计指标或批量操作，必须创建`CHG-*`并重新分诊，必要时升级统一PRD。
"""


def lifecycle_register(case: dict[str, str], changed: bool) -> dict:
    req = case["req"]
    audit_actions = [
        ("CREATED", "created", "登记来源、结果与责任人"),
        ("TRIAGED", "triaged", "确认单角色、可逆、局部变化，采用需求卡"),
        ("CLARIFIED", "clarification_closed", "默认值、权限、异常和非目标已关闭"),
        ("SPECIFIED", "specified", "L1需求卡和正反验收已完成"),
        ("REVIEWED", "reviewed", "产品、角色代表和QA完成轻量评审"),
        ("BASELINED", "baselined", "v1.0需求卡成为受控基线"),
    ]
    if changed:
        audit_actions.extend([
            ("CHANGE", "change_requested", "评审后补充清除条件的恢复文案"),
            ("REBASELINED", "rebaselined", "CHG影响、同步和回归完成，基线更新为v1.1"),
        ])
    audit_actions.extend([
        ("ACCEPTED", "acceptance_signed", "实验室生命周期夹具完成正向与恢复验收"),
        ("CLOSED", "closed", "强制验收、证据和签署均闭合"),
    ])
    audit_log = []
    for index, (suffix, action, reason) in enumerate(audit_actions, start=1):
        audit_log.append({
            "id": f"AUDIT-{case['code']}-{suffix}",
            "requirement_ref": req,
            "actor": "v5.3.3生命周期验证器",
            "action": action,
            "at": f"2026-07-22T{8 + index:02d}:00:00+08:00",
            "reason": reason,
            "to_version": "1.1" if changed and action in {"rebaselined", "acceptance_signed", "closed"} else "1.0",
            "evidence_refs": [case["evd"] if action in {"acceptance_signed", "closed"} else case["src"]],
        })
    return {
        "schema_version": "5.1.0",
        "register_id": f"REGISTER-{case['code']}",
        "product": case["project"],
        "current_baseline": "1.1" if changed else "1.0",
        "iterations": [{
            "id": f"ITER-{case['code']}", "name": "v5.3.3需求卡生命周期验证",
            "status": "closed", "requirement_refs": [req],
        }],
        "requirements": [{
            "id": req, "title": case["title"], "type": "experience", "stage": "closed",
            "intake_decision": "accept", "priority": "P2", "outcome": case["outcome"],
            "source_refs": [case["src"]],
            "value": {"level": "medium", "rationale": "减少列表查找步骤且不改变业务数据", "evidence_refs": [case["src"]]},
            "complexity": {"band": "S", "dimensions": ["roles"], "rationale": "单角色单页面只读体验调整"},
            "uncertainty": {"level": "low", "rationale": "默认、权限、异常与范围已由场景夹具固定"},
            "owner": "产品负责人", "requester": case["role_name"],
            "iteration_ref": f"ITER-{case['code']}", "dependency_refs": [],
            "behavior_refs": [case["flow"], case["act"]],
            "acceptance_refs": [case["ac_positive"], case["ac_recovery"]],
            "review_refs": [f"REV-{case['code']}-001"],
            "change_refs": [case["change"]] if changed else [],
            "baseline_version": "1.1" if changed else "1.0",
            "notes": "仅为Skill生命周期实验室验证，不代表真实产品功能已开发上线。",
        }],
        "dependency_edges": [],
        "audit_log": audit_log,
    }


def lifecycle_change(case: dict[str, str]) -> dict:
    return {
        "schema_version": "5.1.0", "change_id": case["change"],
        "title": f"{case['title']}恢复文案补充", "reason": "评审要求空态和错误态都提供清除条件入口",
        "source_refs": [case["src"]], "status": "baselined", "baseline_version": "1.0",
        "target_version": "1.1", "decision_owner": "产品负责人",
        "request": {
            "requester": case["role_name"], "requested_at": "2026-07-22T15:00:00+08:00",
            "authority": "项目需求卡评审", "urgency": "normal", "seed_refs": [case["act"]],
            "before": "异常时仅展示失败信息", "after": "异常和空态均展示清除条件与重试入口",
        },
        "diff": [{
            "ref": case["act"], "path": "failure_recovery.visible_result",
            "before": "展示失败信息", "after": "保留条件并提供重试、清除入口",
            "reason": "保证用户可以返回默认结果",
        }],
        "impacts": {
            "requirements": [{"ref": case["req"], "change_type": "modify", "reason": "补充恢复行为"}],
            "roles": [], "modules": [{"ref": case["mod"], "change_type": "modify", "reason": "更新局部页面合同"}],
            "flows": [{"ref": case["flow"], "change_type": "modify", "reason": "补充失败返回路径"}],
            "views": [{"ref": case["view"], "change_type": "modify", "reason": "增加清除入口"}],
            "actions": [{"ref": case["act"], "change_type": "modify", "reason": "补充恢复结果"}],
            "fields": [], "states": [], "events": [], "rules": [], "interfaces": [],
            "acceptance": [{"ref": case["ac_recovery"], "change_type": "modify", "reason": "验证清除和重试"}],
            "tests": [{"ref": case["test_recovery"], "change_type": "modify", "reason": "覆盖恢复入口"}],
            "defects": [], "evidence": [{"ref": case["evd"], "change_type": "add", "reason": "绑定实验室回归证据"}],
            "integrations": [], "documentation": [],
            "data_migration": {"required": False, "strategy": "无业务数据变化", "rollback": "回退需求卡v1.0", "reconciliation": "不适用"},
        },
        "compatibility": {"stable_ids_preserved": True, "deprecated_ids": [], "replacement_map": {}, "consumer_actions": ["前端和QA接收v1.1需求卡"]},
        "approvals": [{"role": "产品负责人", "actor": "实验室产品角色", "decision": "approved", "decided_at": "2026-07-22T16:00:00+08:00", "evidence_ref": case["evd"]}],
        "synchronization": [{"consumer": "前端/QA实验角色", "artifact": f"{case['code']}-card.md", "version": "1.1", "status": "acknowledged", "synchronized_at": "2026-07-22T17:00:00+08:00"}],
        "audit_log": [{"actor": "实验室产品角色", "action": "change_baselined", "at": "2026-07-22T17:00:00+08:00", "reason": "影响、审批、同步和回归均完成"}],
        "verification": {"acceptance_refs": [case["ac_recovery"]], "regression_refs": [case["ac_positive"]], "evidence_refs": [case["evd"]], "result": "passed"},
    }


with tempfile.TemporaryDirectory(prefix="ads-v530-") as temp_name:
    temp = Path(temp_name)
    base = FIXTURE.read_text(encoding="utf-8")

    triage_markdown = temp / "triage-source.md"
    triage_markdown.write_text("# 客户需求\n\n需要新增数据上报。\n", encoding="utf-8")
    triage_result = subprocess.run(
        [sys.executable, str(CLI), "triage", "--input", str(triage_markdown)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if (
        triage_result.returncode != 2
        or "TRIAGE-INPUT-INVALID" not in triage_result.stderr
        or "Traceback" in triage_result.stderr
    ):
        failures.append(
            "non-structured triage input did not fail with bounded guidance: "
            + triage_result.stdout + triage_result.stderr
        )

    legacy_stage0 = temp / "legacy-stage0.yaml"
    legacy_stage0.write_text(yaml.safe_dump({
        "inventory_id": "INV-LEGACY-001",
        "views": [{
            "id": "VIEW-LEGACY-001", "source_ref": "app.html#view",
            "classification": "confirmed",
        }],
        "actions": [{
            "id": "ACT-LEGACY-001", "source_ref": "app.html#action",
            "classification": "confirmed",
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate(
        "--profile", "stage0", "--inventory", str(legacy_stage0), "--level", "L2"
    )
    if code != 2 or "STAGE0-LEGACY-INVENTORY" not in codes(payload):
        failures.append(f"legacy Stage 0 shape lacked explicit migration guidance: {codes(payload)}")

    card_cases = [
        {
            "code": "ANJIA-RESOURCE-FORMAT", "project": "安驾融合出版与服务平台",
            "title": "资源列表增加文件格式筛选", "outcome": "内容制作人员可按视频、音频、文档或图片快速缩小资源范围",
            "scene": "资源管理列表查找素材", "story": "按已有文件格式筛选当前资源列表",
            "role": "ROLE-ANJIA-CONTENT", "role_name": "内容制作人员", "mod": "MOD-ANJIA-RESOURCE",
            "view": "VIEW-ANJIA-RESOURCE-LIST", "field": "FLD-ANJIA-FILE-FORMAT", "control": "单选下拉", "default": "全部格式",
            "visible_result": "列表只显示所选格式资源并展示当前条件", "src": "SRC-ANJIA-PROTO-RESOURCE",
        },
        {
            "code": "ANJIA-COURSE-MINE", "project": "安驾融合出版与服务平台",
            "title": "课程列表增加仅看我创建", "outcome": "课程编辑可一键只查看本人创建且原本有权访问的课程",
            "scene": "课程管理列表定位本人课程", "story": "使用仅看我创建开关减少翻页查找",
            "role": "ROLE-ANJIA-EDITOR", "role_name": "课程编辑", "mod": "MOD-ANJIA-COURSE",
            "view": "VIEW-ANJIA-COURSE-LIST", "field": "FLD-ANJIA-COURSE-MINE", "control": "布尔开关", "default": "关闭",
            "visible_result": "开启后只显示createdBy为当前用户的有权课程", "src": "SRC-ANJIA-PROTO-COURSE", "changed": True,
        },
        {
            "code": "CRM-LEAD-SOURCE", "project": "神通CRM经营响应中台",
            "title": "线索列表增加来源筛选", "outcome": "销售可按现有线索来源字典筛选自己有权查看的线索",
            "scene": "线索列表按来源查找", "story": "选择来源后只查看对应渠道线索",
            "role": "ROLE-CRM-SALES", "role_name": "销售", "mod": "MOD-CRM-LEAD",
            "view": "VIEW-CRM-LEAD-LIST", "field": "FLD-CRM-LEAD-SOURCE", "control": "可清除单选下拉", "default": "全部来源",
            "visible_result": "列表和结果数按所选来源刷新", "src": "SRC-CRM-PROTO-LEAD",
        },
        {
            "code": "CRM-TICKET-OVERDUE", "project": "神通CRM经营响应中台",
            "title": "工单列表增加仅看超期", "outcome": "客服可快速查看截止时间已过且未关闭的有权工单",
            "scene": "工单列表处理超期待办", "story": "使用仅看超期筛选定位需要优先响应的工单",
            "role": "ROLE-CRM-SERVICE", "role_name": "客服", "mod": "MOD-CRM-TICKET",
            "view": "VIEW-CRM-TICKET-LIST", "field": "FLD-CRM-TICKET-OVERDUE", "control": "布尔开关", "default": "关闭",
            "visible_result": "开启后只显示截止时间早于当前时间且状态非关闭的工单", "src": "SRC-CRM-PROTO-TICKET", "changed": True,
        },
        {
            "code": "REPORT-TEMPLATE-CREATOR", "project": "数据报告管理",
            "title": "报告模板列表增加创建人筛选", "outcome": "报告配置管理员可按已有创建人筛选模板",
            "scene": "模板管理列表定位责任人", "story": "选择创建人后查看对应模板",
            "role": "ROLE-REPORT-ADMIN", "role_name": "报告配置管理员", "mod": "MOD-REPORT-TEMPLATE",
            "view": "VIEW-REPORT-TPL-LIST", "field": "FLD-REPORT-TPL-CREATOR", "control": "可搜索单选下拉", "default": "全部创建人",
            "visible_result": "列表只显示对应创建人的有权模板", "src": "SRC-REPORT-PROTO-TEMPLATE",
        },
        {
            "code": "REPORT-FAILED-FILTER", "project": "数据报告管理",
            "title": "我的报告增加生成失败筛选", "outcome": "报告使用人可快速查看本人有权访问的生成失败报告",
            "scene": "我的报告列表定位失败结果", "story": "选择生成失败状态后快速定位需重新处理的报告",
            "role": "ROLE-REPORT-USER", "role_name": "报告使用人", "mod": "MOD-REPORT-GENERATED",
            "view": "VIEW-REPORT-MY-LIST", "field": "FLD-REPORT-GEN-STATUS", "control": "状态单选下拉", "default": "全部状态",
            "visible_result": "列表只显示status=failed的有权报告", "src": "SRC-REPORT-PROTO-GENERATED", "changed": True,
        },
        {
            "code": "REG-UNIT-LAST-SUCCESS", "project": "人车企数据核对与自动上报",
            "title": "上报单元按上次成功时间排序", "outcome": "企业管理员可按上次成功时间升序或降序查看七个上报单元",
            "scene": "企业上报页识别长期未成功单元", "story": "切换上次成功时间排序后优先检查较久未完成的单元",
            "role": "ROLE-ENT-ADMIN", "role_name": "企业管理员", "mod": "MOD-REPORT-RECONCILE",
            "view": "VIEW-ENT-REPORT", "field": "FLD-UNIT-LAST-SUCCESS-SORT", "control": "排序枚举按钮", "default": "固定业务顺序",
            "visible_result": "七个单元按所选时间顺序重排且状态不变", "src": "SRC-REPORTING-BASELINE-001",
        },
        {
            "code": "REG-COPY-CORRELATION", "project": "人车企数据核对与自动上报",
            "title": "系统失败结果支持复制关联号", "outcome": "企业管理员可复制当前系统失败单元的关联号用于反馈",
            "scene": "上报进度查看系统失败详情", "story": "点击复制关联号并在反馈中粘贴准确标识",
            "role": "ROLE-ENT-ADMIN", "role_name": "企业管理员", "mod": "MOD-REPORT-RECONCILE",
            "view": "VIEW-REPORT-PROGRESS", "field": "FLD-REPORT-CORRELATION-ID", "control": "只读文本和复制按钮", "default": "无关联号时隐藏",
            "visible_result": "成功复制后按钮短暂显示已复制且原失败状态不变", "src": "SRC-REPORTING-BASELINE-001", "changed": True,
        },
        {
            "code": "KB-MY-CREATED", "project": "SaaS知识库管理",
            "title": "知识列表增加仅看我创建", "outcome": "知识管理员可只查看本人创建且原本有权访问的知识条目",
            "scene": "知识列表定位本人内容", "story": "开启仅看我创建以减少搜索范围",
            "role": "ROLE-KB-ADMIN", "role_name": "知识管理员", "mod": "MOD-KB-CONTENT",
            "view": "VIEW-KB-LIST", "field": "FLD-KB-MY-CREATED", "control": "布尔开关", "default": "关闭",
            "visible_result": "开启后只显示createdBy为当前用户的有权知识", "src": "SRC-KB-PROTO-001",
        },
        {
            "code": "KB-COPY-ASSET-ID", "project": "SaaS知识库管理",
            "title": "知识资产详情支持复制资产编号", "outcome": "知识管理员可复制当前资产稳定编号用于沟通定位",
            "scene": "知识资产详情沟通问题", "story": "点击复制资产编号并粘贴到评审记录",
            "role": "ROLE-KB-ADMIN", "role_name": "知识管理员", "mod": "MOD-KB-ASSET",
            "view": "VIEW-KB-ASSET-DETAIL", "field": "FLD-KB-ASSET-ID", "control": "只读文本和复制按钮", "default": "显示现有编号",
            "visible_result": "复制成功后显示已复制，资产内容和状态不改变", "src": "SRC-KB-PROTO-001", "changed": True,
        },
    ]

    for case in card_cases:
        case.update({
            "req": f"REQ-{case['code']}", "flow": f"FLOW-{case['code']}",
            "act": f"ACT-{case['code']}", "ac_positive": f"AC-{case['code']}-POSITIVE",
            "ac_recovery": f"AC-{case['code']}-RECOVERY",
            "test_positive": f"TEST-{case['code']}-POSITIVE",
            "test_recovery": f"TEST-{case['code']}-RECOVERY",
            "evd": f"EVD-{case['code']}", "change": f"CHG-{case['code']}-RECOVERY",
        })
        changed = bool(case.get("changed"))
        case_dir = temp / "requirement-card-lifecycle" / case["code"].lower()
        case_dir.mkdir(parents=True)

        intake = {
            "title": case["title"], "outcome": case["outcome"], "owner": "产品负责人",
            "document_language": "zh-CN", "source_refs": [case["src"]],
            "value": "medium", "value_evidence": ["现有页面和角色任务可观察"],
            "roles": [case["role"]], "modules": [case["mod"]], "integrations": [],
            "states": [], "cross_role_handoffs": [], "reversible": True, "ui": True,
            "data_submission": False, "data_reporting": False, "metric_caliber": False,
            "batch_io": False, "approval": False, "audit_required": False,
            "irreversible_write": False, "version_compatibility": False,
            "cross_module_state": False, "sensitive_data": False, "compliance": False,
            "migration": False, "customer_acceptance": False, "ai_behavior": False,
            "ambiguity": "low", "blocked_dependency": False,
        }
        intake_path = case_dir / "intake.yaml"
        intake_path.write_text(yaml.safe_dump(intake, allow_unicode=True, sort_keys=False), encoding="utf-8")
        triage_result = subprocess.run(
            [sys.executable, str(CLI), "triage", "--input", str(intake_path), "--format", "json"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
        )
        try:
            triage_payload = json.loads(triage_result.stdout)
        except json.JSONDecodeError:
            triage_payload = {}
        if (
            triage_result.returncode != 0
            or triage_payload.get("decision") != "accept"
            or triage_payload.get("delivery_shape") != "requirement_card"
            or triage_payload.get("assurance_profile") != "bounded"
        ):
            failures.append(f"{case['code']} triage mismatch: {triage_result.stdout}{triage_result.stderr}")

        card_path = case_dir / "requirement-card.md"
        card_path.write_text(render_requirement_card(case), encoding="utf-8")
        code, card_payload = run_gate("--profile", "prd", "--prd", str(card_path), "--level", "L1")
        if code != 0:
            failures.append(f"{case['code']} L1 card failed: {codes(card_payload)}")

        evidence_path = case_dir / "acceptance-evidence.txt"
        evidence_path.write_text(
            "LAB SIMULATION ONLY / 仅用于需求卡生命周期机制验证。\n"
            f"{case['ac_positive']}: deterministic positive fixture passed.\n"
            f"{case['ac_recovery']}: deterministic empty/error recovery fixture passed.\n",
            encoding="utf-8",
        )
        arun = {
            "schema_version": "5.1.0", "run_id": f"ARUN-{case['code']}",
            "baseline_version": "1.1" if changed else "1.0",
            "environment": "v5.3.3 lifecycle laboratory / deterministic fixture",
            "executor": "v5.3.3生命周期验证器", "executed_at": "2026-07-22T20:00:00+08:00",
            "evidence_catalog": [{"id": case["evd"], "uri": evidence_path.name}],
            "items": [
                {"id": f"ARITEM-{case['code']}-POSITIVE", "acceptance_ref": case["ac_positive"], "requirement_refs": [case["req"]], "mandatory": True, "result": "pass", "actual_result": "正向夹具得到需求卡声明的可见结果且无业务写入", "evidence_refs": [case["evd"]], "defect_refs": []},
                {"id": f"ARITEM-{case['code']}-RECOVERY", "acceptance_ref": case["ac_recovery"], "requirement_refs": [case["req"]], "mandatory": True, "result": "pass", "actual_result": "空态/错误夹具保留条件并可重试或清除，未扩大权限", "evidence_refs": [case["evd"]], "defect_refs": []},
            ],
            "residual_issues": [], "conclusion": "accepted", "conditions": [],
            "sign_offs": [{"role": "实验室QA", "actor": "v5.3.3生命周期验证器", "decision": "approve", "at": "2026-07-22T20:10:00+08:00", "evidence_ref": case["evd"]}],
        }
        arun_path = case_dir / "acceptance-run.yaml"
        arun_path.write_text(yaml.safe_dump(arun, allow_unicode=True, sort_keys=False), encoding="utf-8")
        arun_result = subprocess.run(
            [sys.executable, str(ARUN_VALIDATOR), str(arun_path)], cwd=ROOT,
            text=True, encoding="utf-8", capture_output=True,
        )
        if arun_result.returncode != 0:
            failures.append(f"{case['code']} ARUN failed: {arun_result.stdout}{arun_result.stderr}")

        register_path = case_dir / "requirement-register.yaml"
        register_path.write_text(
            yaml.safe_dump(lifecycle_register(case, changed), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        code, register_payload = run_gate(
            "--profile", "requirement", "--requirement", str(register_path), "--level", "L1"
        )
        if code != 0:
            failures.append(f"{case['code']} lifecycle register failed: {codes(register_payload)}")

        if changed:
            change_path = case_dir / "change-package.yaml"
            change_path.write_text(
                yaml.safe_dump(lifecycle_change(case), allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            change_result = subprocess.run(
                [sys.executable, str(CHANGE_VALIDATOR), str(change_path)], cwd=ROOT,
                text=True, encoding="utf-8", capture_output=True,
            )
            if change_result.returncode != 0:
                failures.append(f"{case['code']} change failed: {change_result.stdout}{change_result.stderr}")

        required_actions = {
            "created", "triaged", "clarification_closed", "specified", "reviewed",
            "baselined", "acceptance_signed", "closed",
        }
        register = yaml.safe_load(register_path.read_text(encoding="utf-8"))
        observed_actions = {item["action"] for item in register["audit_log"]}
        if not required_actions.issubset(observed_actions):
            failures.append(f"{case['code']} lifecycle audit misses {sorted(required_actions - observed_actions)}")
        if changed and not {"change_requested", "rebaselined"}.issubset(observed_actions):
            failures.append(f"{case['code']} changed card lacks change/rebaseline audit")
        card_lifecycle_results.append(
            f"{case['code']}: intake=accept/card, card=PASS, register=closed, "
            f"change={'PASS' if changed else 'N/A'}, ARUN=accepted(lab-only)"
        )

    # A fenced/prose mention of an appendix cannot satisfy heading order.
    heading_probe = temp / "heading-probe.md"
    heading_probe.write_text(
        base.replace("## 4. 角色旅程", "```markdown\n## 附录 A：假的提前附录\n```\n正文提到 ## 附录 A 不算标题。\n\n## 4. 角色旅程"),
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(heading_probe), "--level", "L2")
    if code != 0:
        failures.append(f"real Markdown heading parser rejected a valid baseline: {codes(payload)}")

    language_drift = temp / "language-drift.md"
    language_drift.write_text(
        base.replace("# 通用事项登记需求规格说明书", "# Item Registration Product Requirements")
        .replace("## 1. 背景、目标与成功指标", "## 1. Background, Goals And Success Metrics"),
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(language_drift), "--level", "L2")
    if code != 2 or "PRD-LANGUAGE-DRIFT" not in codes(payload):
        failures.append(f"Chinese baseline with English structural drift escaped: {codes(payload)}")

    english_headings = {
        "# 通用事项登记需求规格说明书": "# Item Registration Product Requirements",
        "## 0. 文档控制与来源优先级": "## 0. Document Control And Source Precedence",
        "### 0.1 任务式阅读导航": "### 0.1 Reader Task Map",
        "### 0.2 30 秒摘要": "### 0.2 30-Second Summary",
        "## 1. 背景、目标与成功指标": "## 1. Background, Goals And Success Metrics",
        "## 2. 需求准入与范围": "## 2. Requirement Intake And Scope",
        "## 3. 角色与数据范围": "## 3. Roles And Data Scope",
        "## 4. 角色旅程 FLOW-ITEM-CREATE": "## 4. Role Journey FLOW-ITEM-CREATE",
        "## 5. 业务流程与状态机 STATE-ITEM": "## 5. Business Flow And State Machine STATE-ITEM",
        "## 6. 功能总览与信息架构": "## 6. Functional Overview And Information Architecture",
        "## 7. 分模块功能需求": "## 7. Module Requirements",
        "### 7.1 事项管理 MOD-ITEM": "### 7.1 Item Management MOD-ITEM",
        "## 8. 数据与字段流转": "## 8. Data And Field Flow",
        "## 9. 非功能、安全与隐私": "## 9. Non-Functional Security And Privacy",
        "## 10. 指标与统计口径": "## 10. Metrics And Statistical Caliber",
        "## 11. 验收方案": "## 11. Acceptance Plan",
        "## 12. 验收结论规则": "## 12. Acceptance Decision Rules",
        "## 附录 A：页面—区域—动作索引": "## Engineering And AI Coding Annex A: Page Region Action Index",
        "## 附录 B：全局字段字典": "## Annex B: Global Field Dictionary",
        "## 附录 C：规则与状态机": "## Annex C: Rules And State Machines",
        "## 附录 D：API、事件与集成业务契约": "## Annex D: API Events And Integration Contracts",
        "## 附录 E：机器可读验收": "## Annex E: Machine-Readable Acceptance",
        "## 附录 F：双向追溯矩阵": "## Annex F: Bidirectional Traceability",
        "## 附录 G：禁止推断清单": "## Annex G: Forbidden Invention",
    }
    english = with_frontmatter(base, {"document_language": "en"})
    for source, target in english_headings.items():
        english = english.replace(source, target)
    english_prd = temp / "english-valid.md"
    english_prd.write_text(english, encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(english_prd), "--level", "L2")
    if code != 0:
        refs = [(item["code"], item.get("ref")) for item in payload["findings"]]
        failures.append(f"explicit English baseline failed bilingual structure aliases: {refs}")

    requirement_card = temp / "requirement-card-zh.md"
    requirement_card.write_text("""---
delivery_level: L1
document_language: zh-CN
bilingual: false
open_p0_unknown_ids: []
---
# 列表字段调整需求卡
## 0. 需求准入与 30 秒摘要
REQ-LIGHT-001 已准入；目标是让运营查看归属地，价值来自已确认客服反馈。
## 1. 目标、范围与非目标
范围只增加只读归属地；不改变编辑、权限和存量数据。
## 2. 角色与用户故事
ROLE-OPERATOR 希望查看字段以减少查询时间，数据范围仍为本部门。
## 3. 用户旅程、流程与异常
FLOW-LIGHT-001：用户进入列表即可查看；数据缺失显示短横线，失败时刷新恢复。
## 4. 验收
AC-LIGHT-001：给定有权用户，打开列表后显示归属地；越权用户不得获得额外数据。
""", encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(requirement_card), "--level", "L1")
    if code != 0:
        failures.append(f"bounded Chinese requirement card was forced into a full PRD: {codes(payload)}")

    incomplete_slice = temp / "incomplete-module-slice.md"
    incomplete_slice.write_text(base.replace("无未决项。", ""), encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(incomplete_slice), "--level", "L2")
    if code != 2 or "PRD-MODULE-SLICE-INCOMPLETE" not in codes(payload):
        failures.append(f"module-local acceptance/unknown closure escaped: {codes(payload)}")

    data_facet = temp / "data-submission-thin.md"
    data_facet.write_text(
        base.replace("activated_facets: [ui, stateful]", "activated_facets: [ui, stateful, data_submission]"),
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(data_facet), "--level", "L2")
    if code != 2 or "PRD-DATA-SUBMISSION-CONTRACT-INCOMPLETE" not in codes(payload):
        failures.append(f"thin data-submission contract escaped: {codes(payload)}")

    unknown_prd = temp / "unknown.md"
    unknown_prd.write_text(with_frontmatter(base, {
        "open_p0_unknown_ids": ["UNK-ITEM-001"],
        "unknowns": [{
            "id": "UNK-ITEM-001", "priority": "P0", "status": "open",
            "owner": "product-owner", "blocks_stage": "baseline",
            "affected_refs": ["REQ-ITEM-001"],
        }],
    }), encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(unknown_prd), "--level", "L2", "--stage", "clarify")
    if code != 1 or payload["status"] != "REVIEW_COMPLETE_WITH_GAPS":
        failures.append(f"future-stage P0 should be a scoped gap: {payload['status']} {codes(payload)}")
    code, payload = run_gate("--profile", "prd", "--prd", str(unknown_prd), "--level", "L2", "--stage", "baseline", "--scope-ref", "REQ-ITEM-001")
    if code != 3 or payload["status"] != "BLOCKED_BY_P0_UNKNOWN":
        failures.append(f"active P0 did not use exit 3: {payload['status']} {codes(payload)}")

    unstructured_prd = temp / "unstructured-unknown.md"
    unstructured_prd.write_text(with_frontmatter(base, {"open_p0_unknown_ids": ["REV-ITEM-001"]}), encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(unstructured_prd), "--level", "L2")
    if code != 2 or not {"PRD-P0-UNKNOWN-ID-NOT-UNK", "PRD-P0-UNKNOWN-NOT-STRUCTURED"}.issubset(codes(payload)):
        failures.append(f"manual REV/open-P0 bypass escaped: {codes(payload)}")

    dynamic_prototype = temp / "dynamic-anchor.html"
    dynamic_prototype.write_text(
        """<!doctype html><main data-testid="page-VIEW-DEMO"></main>
<script>
const act=(id)=>'<button data-'+'action="'+id+'">run</button>';
document.querySelector('main').innerHTML=act('ACT-DEMO-RUN');
</script>""",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prototype", "--prototype", str(dynamic_prototype), "--level", "L2")
    if code != 2 or "PROTO-DYNAMIC-ANCHOR-CONSTRUCTION" not in codes(payload):
        failures.append(f"dynamic data-action construction escaped L2: {codes(payload)}")
    if payload.get("metrics", {}).get("prototype_dynamic_action_candidates") != 1:
        failures.append("dynamic ACT candidate was not included in prototype inventory metrics")

    placeholder_prototype = temp / "placeholder-anchor.html"
    placeholder_prototype.write_text(
        '''<!doctype html><main data-testid="page-VIEW-DEMO"></main>
<script>const template=(act)=>`<button data-action="${act}">运行</button>`;</script>''',
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prototype", "--prototype", str(placeholder_prototype), "--level", "L2")
    if code != 2 or "PROTO-UNSTABLE-ACTION" not in codes(payload):
        failures.append(f"template placeholder action escaped stable-ID gate: {codes(payload)}")

    prototype_source = """<!doctype html>
<!-- PAGE-CONTRACT: VIEW-DEMO; primary=form; layout=composite; surfaces=form,list -->
<main data-testid="page-VIEW-DEMO">
__REGION_OPEN__<button data-action="ACT-DEMO-SAVE" data-ac="AC-DEMO-SAVE">保存</button>
<span data-state="idle">待保存</span>__REGION_CLOSE__</main>
<script>
const GlobalState={status:"idle"};
const ActionRegistry={"ACT-DEMO-SAVE":function(){GlobalState.status="saved";document.querySelector("[data-state]").textContent="已保存";}};
document.addEventListener("click",function(event){const target=event.target.closest("[data-action]");if(!target)return;ActionRegistry[target.dataset.action]();});
</script>"""
    regionless = temp / "regionless.html"
    regionless.write_text(prototype_source.replace("__REGION_OPEN__", "").replace("__REGION_CLOSE__", ""), encoding="utf-8")
    code, payload = run_gate("--profile", "prototype", "--prototype", str(regionless), "--level", "L3")
    if code != 2 or "PROTO-NO-REGION-ANCHOR" not in codes(payload):
        failures.append(f"complex L3 prototype without REG-* escaped: {payload['status']} {codes(payload)}")
    if "PROTO-BROWSER-EVIDENCE-MISSING" not in codes(payload):
        failures.append("L3 prototype without ARUN did not expose the browser evidence gap")

    evidenced_prototype = temp / "evidenced.html"
    evidenced_prototype.write_text(
        prototype_source.replace(
            "__REGION_OPEN__", '<section data-testid="region-REG-DEMO-FORM">'
        ).replace("__REGION_CLOSE__", "</section>"),
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prototype", "--prototype", str(evidenced_prototype), "--level", "L3")
    if code != 1 or payload["status"] != "REVIEW_COMPLETE_WITH_GAPS" or "PROTO-BROWSER-EVIDENCE-MISSING" not in codes(payload):
        failures.append(f"static-only L3 prototype was presented as complete: {payload['status']} {codes(payload)}")

    acceptance_run = temp / "ARUN-PROTOTYPE-001.yaml"
    acceptance_evidence = temp / "prototype-save-evidence.txt"
    acceptance_evidence.write_text("Chrome/Playwright: ACT-DEMO-SAVE -> saved", encoding="utf-8")
    acceptance_run.write_text(yaml.safe_dump({
        "schema_version": "5.1.0",
        "run_id": "ARUN-PROTOTYPE-001",
        "baseline_version": "1.0",
        "environment": "Chrome 127 / Windows 11 / Playwright",
        "executor": "qa-owner",
        "executed_at": "2026-07-19T10:00:00+08:00",
        "evidence_catalog": [{"id": "EVD-PROTOTYPE-SAVE-001", "uri": acceptance_evidence.name}],
        "items": [{
            "id": "ARITEM-PROTOTYPE-001", "acceptance_ref": "AC-DEMO-SAVE",
            "requirement_refs": ["REQ-DEMO-SAVE"], "mandatory": True,
            "result": "pass", "actual_result": "点击保存后状态区显示已保存",
            "evidence_refs": ["EVD-PROTOTYPE-SAVE-001"], "defect_refs": [],
        }],
        "residual_issues": [], "conclusion": "accepted", "conditions": [],
        "sign_offs": [{
            "role": "qa", "actor": "qa-owner", "decision": "approve",
            "at": "2026-07-19T10:05:00+08:00", "evidence_ref": "EVD-PROTOTYPE-SAVE-001",
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    cli_result = subprocess.run(
        [
            sys.executable, str(CLI), "gate", "--profile", "prototype",
            "--prototype", str(evidenced_prototype), "--level", "L3",
            "--acceptance-run", str(acceptance_run), "--format", "json",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    try:
        payload = json.loads(cli_result.stdout)
    except json.JSONDecodeError:
        failures.append("public CLI acceptance-run did not return JSON: " + cli_result.stdout + cli_result.stderr)
        payload = {"status": "INVALID", "findings": [], "metrics": {}, "not_proven": []}
    code = cli_result.returncode
    if code != 0 or payload["status"] != "PASS":
        failures.append(f"evidence-bound L3 prototype failed: {payload['status']} {codes(payload)}")
    if payload.get("metrics", {}).get("prototype_browser_evidence") is not True:
        failures.append("accepted browser ARUN was not reflected in gate metrics")
    if not any("DEC-AESTHETIC" in item for item in payload.get("not_proven", [])):
        failures.append("gate did not disclose the unproven aesthetic direction")
    if any(item == "原型在真实浏览器中的交互、视觉、可访问性与多端适配" for item in payload.get("not_proven", [])):
        failures.append("valid browser ARUN did not narrow the static not_proven statement")
    if any(item == "验收用例已经实际执行并形成签认证据" for item in payload.get("not_proven", [])):
        failures.append("conclusive ARUN was still reported as entirely unexecuted")

    missing_evidence_run = temp / "ARUN-MISSING-EVIDENCE.yaml"
    missing_document = yaml.safe_load(acceptance_run.read_text(encoding="utf-8"))
    missing_document["run_id"] = "ARUN-MISSING-EVIDENCE"
    missing_document["evidence_catalog"][0]["uri"] = "missing-screenshot.png"
    missing_evidence_run.write_text(yaml.safe_dump(missing_document, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, missing_payload = run_gate(
        "--profile", "prototype", "--prototype", str(evidenced_prototype),
        "--level", "L3", "--acceptance-run", str(missing_evidence_run),
    )
    if code != 2 or "ACCEPTANCE-EVIDENCE-INVALID" not in codes(missing_payload):
        failures.append("missing local ARUN evidence was not blocked")

    drifted_evidence_run = temp / "ARUN-DRIFTED-EVIDENCE.yaml"
    drifted_document = yaml.safe_load(acceptance_run.read_text(encoding="utf-8"))
    drifted_document["run_id"] = "ARUN-DRIFTED-EVIDENCE"
    drifted_document["evidence_catalog"][0]["sha256"] = "0" * 64
    drifted_evidence_run.write_text(yaml.safe_dump(drifted_document, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, drifted_payload = run_gate(
        "--profile", "prototype", "--prototype", str(evidenced_prototype),
        "--level", "L3", "--acceptance-run", str(drifted_evidence_run),
    )
    if code != 2 or "ACCEPTANCE-EVIDENCE-INVALID" not in codes(drifted_payload):
        failures.append("ARUN evidence hash drift was not blocked")

    multi_dir = temp / "multi-file-prototype"
    multi_dir.mkdir()
    script_match = re.search(r"<script>(.*?)</script>", evidenced_prototype.read_text(encoding="utf-8"), re.S)
    multi_script = multi_dir / "app.js"
    multi_script.write_text(script_match.group(1), encoding="utf-8")
    (multi_dir / "app.css").write_text(".demo { color: #1677ff; }\n", encoding="utf-8")
    multi_html = multi_dir / "index.html"
    multi_html.write_text(
        re.sub(
            r"<script>.*?</script>",
            '<link rel="stylesheet" href="app.css"><script src="app.js"></script>',
            evidenced_prototype.read_text(encoding="utf-8"), flags=re.S,
        ),
        encoding="utf-8",
    )
    code, multi_payload = run_gate("--profile", "prototype", "--prototype", str(multi_html), "--level", "L2")
    if code != 0 or any(item.startswith("PROTO-EXTERNAL-JS") for item in codes(multi_payload)):
        failures.append(f"local multi-file prototype did not pass as one engineering artifact: {codes(multi_payload)}")
    if multi_payload.get("metrics", {}).get("prototype_local_dependencies") != 2:
        failures.append("local JS/CSS dependencies were not included in prototype metrics")
    missing_dependency_html = multi_dir / "missing-dependency.html"
    missing_dependency_html.write_text(multi_html.read_text(encoding="utf-8").replace("app.js", "missing.js"), encoding="utf-8")
    code, missing_dependency_payload = run_gate(
        "--profile", "prototype", "--prototype", str(missing_dependency_html), "--level", "L2",
    )
    if code != 2 or "PROTO-DEPENDENCY-MISSING" not in codes(missing_dependency_payload):
        failures.append("missing local prototype dependency was not blocked")

    conflict_prd = temp / "conflict.md"
    conflict_prd.write_text(with_frontmatter(base, {
        "canonical_candidates": ["SRC-PRD-A", "SRC-PROTOTYPE-B"],
        "governance": {
            "canonical_authoring_surface": "unified_prd",
            "binding_sources": [
                {"source_ref": "SRC-PRD-A", "canonical": True},
                {"source_ref": "SRC-PROTOTYPE-B", "canonical": True},
            ],
        },
    }), encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(conflict_prd), "--level", "L2")
    if code != 2 or "AUTH-MULTIPLE-CANONICAL-SOURCES" not in codes(payload):
        failures.append("multiple canonical candidates escaped DEC-CONFLICT gate")

    page_prd = temp / "page-profiles.md"
    page_prd.write_text(with_frontmatter(base, {
        "source_refs": ["SRC-ITEM-001"], "open_p0_unknown_ids": [],
        "page_contract_view_ids": ["VIEW-COMPOSITE", "VIEW-BUILDER"],
    }) + """

<!-- PAGE-CONTRACT: VIEW-COMPOSITE; primary=list; layout=composite; surfaces=list -->
页面目标与入口；区域布局；动作与权限；状态与异常；原型绑定；筛选；列表列；分页。
ACT-COMPOSITE-OPEN / ACT-COMPOSITE-EXPORT / AC-COMPOSITE-001；VIEW-COMPOSITE → API-COMPOSITE-LIST /api/composite。

<!-- PAGE-CONTRACT: VIEW-BUILDER; primary=composer; layout=builder; surfaces=composer -->
页面目标与入口；区域布局；动作与权限；状态与异常；原型绑定；拖拽、层级、资源池和排序。
ACT-BUILDER-ADD / ACT-BUILDER-SAVE / AC-BUILDER-001；VIEW-BUILDER → API-BUILDER-SAVE /api/builder。
""",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(page_prd), "--level", "L3")
    page_codes = codes(payload)
    if "PRD-PAGE-COMPOSITE-TOO-THIN" not in page_codes:
        failures.append("composite page with one surface escaped")
    if "PRD-PAGE-BUILDER-INCOMPLETE" not in page_codes:
        failures.append("builder without composer/resource_pool/hierarchy set escaped")
    if "PRD-NO-ACCEPTANCE-PLAN" not in page_codes:
        failures.append("L3 baseline without an owned acceptance plan escaped")

    range_prd = temp / "range-id.md"
    range_prd.write_text(with_frontmatter(base, {
        "source_refs": ["SRC-ITEM-001"], "open_p0_unknown_ids": [],
        "page_contract_view_ids": ["VIEW-ITEM"],
    }) + "\n正文错误缩写：AC-AUDIT-001..003。\n", encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(range_prd), "--level", "L3")
    if "PRD-NONEXACT-ID" not in codes(payload):
        failures.append("range stable ID in prose escaped exact-ID gate")

    # A v5.2 page contract may explicitly declare a surface not applicable.  It
    # must not be upgraded into a v5.3 mandatory surface merely because the
    # explanatory text contains the surface label.
    legacy_na_prd = temp / "legacy-na-page.md"
    legacy_na_prd.write_text(with_frontmatter(base, {
        "source_refs": ["SRC-ITEM-001"], "open_p0_unknown_ids": [],
        "page_contract_view_ids": ["VIEW-LEGACY-NA"],
    }) + """

<!-- PAGE-CONTRACT: VIEW-LEGACY-NA -->
页面目标与入口；区域布局；动作与权限；状态与异常；原型绑定。
指标口径：不适用。字段与控件：不存在可编辑业务字段。导入：不适用。导出：不适用。
ACT-LEGACY-OPEN / AC-LEGACY-001；VIEW-LEGACY-NA → API-LEGACY-GET /api/legacy。
""",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(legacy_na_prd), "--level", "L3")
    legacy_codes = codes(payload)
    forbidden_legacy_na = {
        "PRD-METRIC-NO-CALIBER", "PRD-FIELD-DICTIONARY-INCOMPLETE",
        "PRD-IMPORT-CONTRACT-INCOMPLETE", "PRD-EXPORT-CONTRACT-INCOMPLETE",
    }
    if forbidden_legacy_na & legacy_codes:
        failures.append(f"legacy N/A surfaces were falsely required: {forbidden_legacy_na & legacy_codes}")

    good_inventory = temp / "stage0-good.yaml"
    good_inventory.write_text(yaml.safe_dump({
        "inventory_status": "inventory_complete",
        "canonical_candidates": ["SRC-PRD-A"],
        "items": [{
            "id": "VIEW-ITEM", "type": "view", "source_ref": "SRC-PRD-A",
            "source_location": "PRD.md#VIEW-ITEM", "classification": "confirmed",
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "stage0", "--inventory", str(good_inventory))
    if code != 0:
        failures.append(f"complete Stage 0 inventory failed: {codes(payload)}")

    reverse_inventory = temp / "stage0-reverse-bad.yaml"
    reverse_inventory.write_text(yaml.safe_dump({
        "inventory_status": "inventory_complete",
        "target_status": "baseline_ready",
        "baseline_requirement_refs": ["REQ-ITEM-001"],
        "canonical_candidates": ["SRC-PRD-A"],
        "items": [{
            "id": "REQ-REVERSE-001", "type": "action", "source_ref": "SRC-PROTOTYPE-A",
            "source_location": "app.html#run", "classification": "inferred", "core_behavior": True,
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "stage0", "--inventory", str(reverse_inventory))
    expected_reverse = {"STAGE0-REVERSE-ID-COLLISION", "STAGE0-MISSING-BASELINE-MAPPING", "STAGE0-INFERRED-NOT-CONFIRMED"}
    if code != 2 or not expected_reverse.issubset(codes(payload)):
        failures.append(f"reverse ID/mapping/batch contract escaped: {codes(payload)}")

    bad_inventory = temp / "stage0-bad.yaml"
    bad_inventory.write_text(yaml.safe_dump({
        "inventory_status": "inventory_complete",
        "canonical_candidates": ["SRC-PRD-A", "SRC-PROTOTYPE-B"],
        "items": [{
            "id": "ACT-UNKNOWN", "type": "action", "source_ref": "SRC-PROTOTYPE-B",
            "source_location": "app.html#button", "classification": "unknown",
            "core_behavior": True,
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "stage0", "--inventory", str(bad_inventory))
    if code != 2 or not {"STAGE0-CORE-UNKNOWN-NOT-OWNED", "STAGE0-MULTIPLE-BASELINES", "STAGE0-FALSE-COMPLETE"}.issubset(codes(payload)):
        failures.append(f"Stage 0 false completeness escaped: {codes(payload)}")

    engineering = temp / "engineering-baseline.md"
    engineering.write_text("# Engineering baseline v1\nowner: architect\n", encoding="utf-8")
    baseline_prd = temp / "PRD.md"
    baseline_prd.write_text(base, encoding="utf-8")
    packet = temp / "MOD-ITEM.md"
    packet_text = "# MOD-ITEM\nREQ-ITEM-001\nAC-ITEM-001\n## qa_projection\npositive, negative, permission, recovery evidence\n"
    packet.write_text(packet_text, encoding="utf-8")
    xct_packet = temp / "XCT-AUDIT.md"
    xct_text = """# XCT-AUDIT
REQ-ITEM-001
AC-ITEM-001
## 影响模块
MOD-CONTENT 与 MOD-AUDIT。
## 全局不变量
每次写入必须保留操作者和基线版本。
## 执行点
在命令入口与持久化完成时执行。
## 例外与失败处理
审计失败时阻断写入并返回可重试错误。
"""
    xct_packet.write_text(xct_text, encoding="utf-8")
    baseline_hash = hashlib.sha256(base.encode("utf-8")).hexdigest()
    manifest = temp / "handoff.yaml"
    manifest.write_text(yaml.safe_dump({
        "schema_version": "5.3.0",
        "status": "ready_for_implementation",
        "engineering_baseline_ref": engineering.name,
        "baseline": {"version": "1.0", "hash": baseline_hash, "requirement_ref": baseline_prd.name},
        "packets": [
            {
                "id": "MOD-ITEM", "kind": "mod", "owner": "team-item", "path": packet.name,
                "baseline_hash": baseline_hash,
                "content_sha256": hashlib.sha256(packet_text.encode("utf-8")).hexdigest(),
                "scope_refs": ["REQ-ITEM-001"], "input_refs": [], "output_refs": [],
                "acceptance_refs": ["AC-ITEM-001"],
            },
            {
                "id": "XCT-AUDIT", "kind": "xct", "owner": "team-platform", "path": xct_packet.name,
                "baseline_hash": baseline_hash,
                "content_sha256": hashlib.sha256(xct_text.encode("utf-8")).hexdigest(),
                "scope_refs": ["REQ-ITEM-001"], "input_refs": [], "output_refs": [],
                "acceptance_refs": ["AC-ITEM-001"],
            },
        ],
        "handoffs": [],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "agent_handoff", "--manifest", str(manifest))
    if code != 0:
        failures.append(f"valid Agent handoff failed: {codes(payload)}")

    incomplete_xct_text = "# XCT-AUDIT\nREQ-ITEM-001\nAC-ITEM-001\n"
    xct_packet.write_text(incomplete_xct_text, encoding="utf-8")
    incomplete_manifest = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    incomplete_manifest["packets"][1]["content_sha256"] = hashlib.sha256(incomplete_xct_text.encode("utf-8")).hexdigest()
    incomplete_manifest_path = temp / "handoff-incomplete-xct.yaml"
    incomplete_manifest_path.write_text(yaml.safe_dump(incomplete_manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, incomplete_payload = run_gate("--profile", "agent_handoff", "--manifest", str(incomplete_manifest_path))
    if code != 2 or "HANDOFF-XCT-INCOMPLETE" not in codes(incomplete_payload):
        failures.append("incomplete XCT cross-cutting packet was not blocked")
    xct_packet.write_text(xct_text, encoding="utf-8")
    code, payload = run_gate(
        "--profile", "handoff", "--prd", str(baseline_prd),
        "--prototype", str(ROOT / "maintainer/tests/fixtures/gate-prototype-valid.html"),
        "--manifest", str(manifest), "--level", "L2",
    )
    if code != 0:
        failures.append(f"combined PRD/prototype/Agent handoff failed: {codes(payload)}")

    candidate = temp / "candidate.yaml"
    candidate.write_text(yaml.safe_dump({
        "schema_version": "5.3.0", "candidate_id": "CAND-CRM-001", "domain": "crm",
        "statement": "A won opportunity must retain its source lead reference.",
        "candidate_type": "invariant", "status": "proposed", "reuse_scope": "project_only",
        "submitted_by": "product-agent", "decision_owner": "product-owner",
        "reuse_approver": None, "source_refs": ["SRC-CRM-001"], "evidence_refs": ["EVD-CRM-001"],
        "applicability": ["project-demo"], "exclusions": [], "jurisdiction": None,
        "regulatory_version": None, "sensitive_data": False, "created_at": "2026-07-18T12:00:00+08:00",
        "expires_at": None,
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CLI), "candidate", "validate", "--input", str(candidate)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0:
        failures.append("project-only candidate validation failed: " + result.stdout + result.stderr)

    usage_dir = temp / "candidate-usage"
    for usage_id, project_ref, outcome in (
        ("USAGE-CRM-001", "project-alpha", "adopted"),
        ("USAGE-CRM-002", "project-beta", "modified"),
    ):
        result = subprocess.run(
            [
                sys.executable, str(CLI), "candidate", "record-usage",
                "--candidate", str(candidate), "--usage-id", usage_id,
                "--project", project_ref, "--outcome", outcome,
                "--evidence", f"EVD-{usage_id}", "--recorded-by", "domain-reviewer",
                "--output", str(usage_dir / f"{usage_id}.yaml"),
            ],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
        )
        if result.returncode != 0:
            failures.append("candidate usage record failed: " + result.stdout + result.stderr)
    result = subprocess.run(
        [
            sys.executable, str(CLI), "candidate", "assess", "--candidate", str(candidate),
            "--usage", str(usage_dir), "--format", "json",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    try:
        assessment = json.loads(result.stdout)
    except json.JSONDecodeError:
        failures.append("candidate assessment did not return JSON: " + result.stdout + result.stderr)
    else:
        if result.returncode != 0 or assessment.get("recommendation") != "eligible_for_organization_review":
            failures.append("candidate with two independent uses was not routed to organization review")
        if assessment.get("auto_promoted") is not False:
            failures.append("candidate assessment performed or implied automatic promotion")

    custom_root = temp / "custom"
    result = subprocess.run(
        [sys.executable, str(CLI), "init-custom", "--output", str(custom_root)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or not (custom_root / "validators" / "my-team.yaml").is_file():
        failures.append("init-custom did not create the private declarative extension skeleton")
    if not (custom_root / "learning" / "candidates" / "project-local" / "CAND-EXAMPLE.yaml").is_file():
        failures.append("init-custom did not create the governed learning candidate example")
    if (custom_root / ".gitignore").read_text(encoding="utf-8") != "*\n!.gitignore\n":
        failures.append("local init-custom is not private-by-default")

    team_custom_root = temp / "team-custom"
    result = subprocess.run(
        [
            sys.executable, str(CLI), "init-custom", "--output", str(team_custom_root),
            "--sharing", "team",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    team_config = yaml.safe_load((team_custom_root / "config.yaml").read_text(encoding="utf-8"))
    team_ignore = (team_custom_root / ".gitignore").read_text(encoding="utf-8")
    if result.returncode != 0 or team_config.get("privacy") != "private_repository":
        failures.append("team init-custom did not create a private-repository collaboration mode")
    if (
        team_ignore == "*\n!.gitignore\n" or "learning/evidence/" not in team_ignore
        or "learning/candidates/project-local/" not in team_ignore
    ):
        failures.append("team init-custom either ignored the whole package or exposed sensitive evidence")
    custom_requirements = temp / "custom-requirements"
    result = subprocess.run(
        [
            sys.executable, str(CLI), "init-requirements", "--output", str(custom_requirements),
            "--custom-root", str(custom_root), "--template", "my-team",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or "## 项目私有补充" not in (custom_requirements / "PRD.md").read_text(encoding="utf-8"):
        failures.append("local inherited PRD template did not overlay the official template")
    result = subprocess.run(
        [
            sys.executable, str(CLI), "query-domain", "--domain", "traffic+my-team",
            "--custom-root", str(custom_root), "--format", "yaml",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or "local_private" not in result.stdout or "DEC-CONFLICT" not in result.stdout:
        failures.append("official + local private domain composition did not preserve conflict semantics")

    caller_project = temp / "caller-project"
    caller_project.mkdir()
    for command in (
        [sys.executable, str(CLI), "init-custom", "--output", "custom"],
        [
            sys.executable, str(CLI), "init-requirements", "--output", "requirements",
            "--custom-root", "custom", "--template", "my-team",
        ],
    ):
        result = subprocess.run(
            command, cwd=caller_project, text=True, encoding="utf-8", capture_output=True,
        )
        if result.returncode != 0:
            failures.append("five-minute project setup failed outside the Skill repository: " + result.stdout + result.stderr)
    result = subprocess.run(
        [
            sys.executable, str(CLI), "query-domain", "--domain", "traffic+my-team",
            "--custom-root", "custom", "--format", "yaml",
        ],
        cwd=caller_project, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or "local_private" not in result.stdout:
        failures.append("relative custom domain did not resolve from the caller project")
    result = subprocess.run(
        [
            sys.executable, str(CLI), "gate", "--profile", "prd", "--prd", "requirements/PRD.md",
            "--level", "L2", "--custom-root", "custom", "--format", "json",
        ],
        cwd=caller_project, text=True, encoding="utf-8", capture_output=True,
    )
    try:
        caller_gate = json.loads(result.stdout)
    except json.JSONDecodeError:
        failures.append("relative caller-project gate did not return JSON: " + result.stdout + result.stderr)
    else:
        if "GATE-NOT-FILE" in codes(caller_gate):
            failures.append("relative PRD path was still resolved from the installed Skill directory")

    # Chinese is a first-class delivery language: user-facing triage must not
    # emit mojibake merely because the source intake is Chinese.
    chinese_intake = temp / "triage-zh-regression.yaml"
    chinese_intake.write_text(
        yaml.safe_dump(
            {
                "title": "复制已配置的回调地址",
                "outcome": "让管理员无需手抄即可复制地址",
                "owner": "产品负责人",
                "source_refs": ["SRC-TEST-01"],
                "value_evidence": ["减少复制错误"],
                "roles": ["管理员"],
                "modules": ["设置"],
                "reversible": True,
                "ambiguity": "low",
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    chinese_triage = subprocess.run(
        [sys.executable, str(CLI), "triage", "--input", str(chinese_intake)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if (
        chinese_triage.returncode != 0
        or "# 需求准入与分诊建议" not in chinese_triage.stdout
        or "目标、责任人与价值证据足以进入需求设计" not in chinese_triage.stdout
        or "�" in chinese_triage.stdout
    ):
        failures.append("Chinese triage output is not readable: " + chinese_triage.stdout + chinese_triage.stderr)

    # New gate output remains schema-valid and exposes consumer/source diagnostics.
    gate_schema = json.loads((ROOT / "schemas" / "gate-result.schema.json").read_text(encoding="utf-8"))
    schema_errors = list(Draft202012Validator(gate_schema).iter_errors(payload))
    if schema_errors:
        failures.append("gate-result schema rejected v5.3 payload: " + schema_errors[0].message)
    if not payload.get("not_proven"):
        failures.append("static gate payload did not disclose its not-proven boundary")


if failures:
    raise SystemExit("\n".join(failures))
for item in card_lifecycle_results:
    print("PASS CARD: " + item)
print(f"PASS: {len(card_lifecycle_results)} requirement-card lifecycle cases completed")
print("PASS: current v5.3.x language, module slices, evidence, multi-file prototype and Agent handoff contracts are deterministic")
