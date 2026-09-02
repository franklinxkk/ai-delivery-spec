from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate
from validators.validate_prd_semantics import run_semantic_checks


ONE_LINE_ROUTING_CASES = [
    ("帮我做一个企业约谈 HTML。", True, False, False, "blocked_by_p0_unknown"),
    ("先做概念 HTML 看效果，允许合理假设。", True, True, True, "concept_candidate"),
    ("不要问，先画一个 HTML，缺口写待确认。", True, True, True, "restricted_concept_candidate"),
    ("附件需求已确认，生成可开发 HTML，不要 PRD。", False, False, True, "implementation_candidate"),
    ("直接生成带标号的评审版 HTML 给开发测试。", True, False, False, "blocked_by_p0_unknown"),
    ("Show me a rough HTML prototype first and list the gaps.", True, True, True, "concept_candidate"),
]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )


def test_one_line_prototype_routing_has_no_unsafe_or_dead_end_combination() -> None:
    assert len(ONE_LINE_ROUTING_CASES) >= 6
    for _prompt, p0_open, concept_explicit, generate_now, state in ONE_LINE_ROUTING_CASES:
        if p0_open and not concept_explicit:
            assert generate_now is False and state == "blocked_by_p0_unknown"
        if p0_open and concept_explicit:
            assert generate_now is True and "concept_candidate" in state
        if not p0_open:
            assert generate_now is True and state == "implementation_candidate"

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    stages = (ROOT / "references/stages.md").read_text(encoding="utf-8")
    prototype = (ROOT / "references/prototype.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "一句话要求 HTML/原型" in skill
    assert "不能停在需求清单或无解释地不出 HTML" in skill
    assert "concept_candidate" in stages and "concept_candidate" in prototype
    assert "只要求 HTML 时不机械附送 PRD" in stages
    assert "帮我做一个企业约谈 HTML" in readme and "不会停在一张需求清单" in readme
    contract = (ROOT / "references/review-workspace.md").read_text(encoding="utf-8")
    schema = (ROOT / "schemas/review-workspace.schema.json").read_text(encoding="utf-8")
    assert "右侧不得出现没有左侧落点的“1/2/3”" in skill
    assert "target、marker、card" in contract
    assert '"selection_contract"' in schema and '"bidirectional_marker_card_target"' in schema


def review_point(ref: str, context: str, target: str, title: str, summary: str, ac: str) -> dict:
    return {
        "ref": ref,
        "subject_ref": target,
        "owner_context_ref": context,
        "marker_required": True,
        "target_ref": target,
        "target_selector": f"[data-review-anchor='{target}']",
        "target_mode": "selector_exactly_one",
        "title": title,
        "business_status": "confirmed",
        "verification_status": "not_run",
        "evidence_origin": "explicit_source",
        "evidence_refs": [],
        "summary": summary,
        "actor_refs": ["ROLE-OPERATOR"],
        "precondition_refs": ["RULE-READY"],
        "visible_result_refs": ["REG-RESULT"],
        "domain_result_refs": ["STATE-SAVED", "EVT-SAVED"],
        "boundary_refs": ["RULE-DUPLICATE"],
        "acceptance_refs": [ac],
        "source_refs": ["SRC-X", "REQ-X"],
    }


def candidate(subject: str = "PROTO-OBS-ACT-SAVE-LEGACY") -> dict:
    return {
        "candidate_id": "CAND-VIEW-X-SAVE-LEGACY", "owner_context_ref": "VIEW-X",
        "subject_ref": subject, "candidate_type": "动作", "label": "保存",
        "selector": "[data-action='save-legacy']", "cardinality_policy": "exactly_one",
        "candidate_reason": ["state_guard"], "business_status": "gap",
        "evidence_origin": "prototype_inferred", "unknown_ref": "UNK-VIEW-X-SAVE-LEGACY",
    }


BASELINE_REFS = " / ".join((
    "REQ-X", "SRC-X", "ROLE-OPERATOR", "VIEW-X", "DRAWER-X", "ACT-X-SUBMIT", "ACT-X-CONFIRM",
    "RULE-READY", "REG-RESULT", "STATE-SAVED", "EVT-SAVED", "RULE-DUPLICATE",
    "AC-X-SUBMIT", "AC-X-CONFIRM", "FLOW-X", "STEP-X", "EDGE-X", "STM-X", "DFD-X", "TEST-X",
))


def baseline_prd() -> str:
    rows = "\n".join(f"| {ref} | 已确认定义 |" for ref in BASELINE_REFS.split(" / "))
    return f"# 基线\n\n| ID | 定义 |\n|---|---|\n{rows}\n"


def manifest(baseline_hash: str, *, level: str = "R1") -> dict:
    points = [
        review_point(
            "RVP-VIEW-SUBMIT", "VIEW-X", "ACT-X-SUBMIT", "提交记录",
            "校验通过后提交当前记录，并在原页面显示持久化结果。", "AC-X-SUBMIT",
        ),
        review_point(
            "RVP-DRAWER-CONFIRM", "DRAWER-X", "ACT-X-CONFIRM", "确认变更",
            "确认后写入当前变更，并将处理结果返回所属业务页面。", "AC-X-CONFIRM",
        ),
    ]
    return {
        "schema_version": "5.4.8",
        "contract_revision": "RC3",
        "workspace_id": "REVIEW-X",
        "language": "zh-CN",
        "baseline": {"version": "1.0", "hash": baseline_hash, "requirement_ref": "prd.md"},
        "workspace": {"review_level": level, "default_tab": "overview", "initial_context_ref": "VIEW-X"},
        "tabs": ["overview", "function_flow", "boundary_acceptance"],
        "context_contract": {
            "resolution": "topmost_business_overlay_else_active_view",
            "allowed_types": ["VIEW", "MODAL", "DRAWER", "POPOVER"],
            "current_context_control": "read_only",
            "resolution_priority": ["product_context_event", "declared_detection_contract", "mutation_observer_reresolve_only"],
            "product_context_event": "product-context-change",
        },
        "product_location_contract": {
            "view_policy": "exactly_one_active_entry_or_declared_exempt",
            "overlay_policy": "inherit_parent_view_location",
            "synchronized_fields": [
                "active_view", "route", "active_menu_path", "expanded_menu_ancestors",
                "breadcrumb", "page_title", "current_context",
            ],
            "review_actions_preserve_location": True,
            "mismatch_result": "block",
        },
        "review_contexts": [
            {
                "context_ref": "VIEW-X", "context_type": "VIEW", "title": "记录列表",
                "detection": {"type": "product_state_equals", "target": "activeView", "expected": "VIEW-X", "overlay_priority": 0},
                "product_location": {
                    "navigation_mode": "menu_bound", "menu_path": ["业务管理", "记录列表"],
                    "active_entry_selector": "[data-view-target='VIEW-X']", "route_ref": "VIEW-X",
                    "breadcrumb": ["业务管理", "记录列表"], "page_title": "记录列表",
                    "parent_view_ref": None, "exemption_reason": None,
                },
                "surface_types": ["list", "drawer_form"],
                "secondary_context_refs": ["DRAWER-X"],
                "review_point_refs": ["RVP-VIEW-SUBMIT"],
            },
            {
                "context_ref": "DRAWER-X", "context_type": "DRAWER", "title": "变更确认",
                "detection": {"type": "selector_visible", "target": "[data-review-context-root='DRAWER-X']", "expected": True, "overlay_priority": 10},
                "product_location": {
                    "navigation_mode": "inherit_parent", "menu_path": ["业务管理", "记录列表"],
                    "active_entry_selector": "[data-view-target='VIEW-X']", "route_ref": "VIEW-X#DRAWER-X",
                    "breadcrumb": ["业务管理", "记录列表", "变更确认"], "page_title": "变更确认",
                    "parent_view_ref": "VIEW-X", "exemption_reason": None,
                },
                "surface_types": ["form"],
                "secondary_context_refs": [],
                "review_point_refs": ["RVP-DRAWER-CONFIRM"],
            },
        ],
        "review_points": points,
        "candidate_review_points": [],
        "candidate_diff_contract": {
            "enabled": True, "auto_promote_to_declared": False,
            "candidate_sources": ["product_truth", "page_contracts", "stable_anchors"],
            "high_risk_omission": "block",
        },
        "semantic_coverage_contract": {
            "denominator": "all_implementation_acceptance_relevant_semantic_items",
            "source_layers": ["prd_page_contracts", "stable_anchors", "cold_read"],
            "critical_coverage": 1,
            "simple_projection": "one_sentence_or_rule_equivalent_group",
            "uncovered_result": "gap_or_block_never_silent",
        },
        "semantic_coverage_items": [
            {
                "coverage_id": "SCOV-VIEW-SUBMIT", "subject_ref": "ACT-X-SUBMIT",
                "owner_context_ref": "VIEW-X", "semantic_type": "action", "criticality": "P1",
                "label": "提交记录", "source_refs": ["REQ-X", "ACT-X-SUBMIT"],
                "ui_grounded": True, "target_ref": "ACT-X-SUBMIT", "coverage_status": "covered",
                "review_point_refs": ["RVP-VIEW-SUBMIT"],
                "human_summary": "校验通过后提交当前记录，并在原页面显示持久化结果。",
                "detail_owner": "function_flow", "unknown_ref": None, "not_applicable_reason": None,
            },
            {
                "coverage_id": "SCOV-DRAWER-CONFIRM", "subject_ref": "ACT-X-CONFIRM",
                "owner_context_ref": "DRAWER-X", "semantic_type": "data_write", "criticality": "P0",
                "label": "确认变更", "source_refs": ["REQ-X", "ACT-X-CONFIRM"],
                "ui_grounded": True, "target_ref": "ACT-X-CONFIRM", "coverage_status": "covered",
                "review_point_refs": ["RVP-DRAWER-CONFIRM"],
                "human_summary": "确认后写入当前变更，并将处理结果返回所属业务页面。",
                "detail_owner": "boundary_acceptance", "unknown_ref": None, "not_applicable_reason": None,
            },
        ],
        "layout_contract": {
            "desktop_mode": "participate_in_layout", "overlay_product_ui": False,
            "resizable": True, "collapsible": True,
            "compact_mode": "product_review_fullscreen_switcher",
        },
        "product_effect_contract": {
            "review_actions_preserve_product_fingerprint": True,
            "product_fingerprint_fields": [
                "active_view", "route", "active_menu_path", "expanded_menu_ancestors", "breadcrumb", "page_title",
                "overlay_stack", "selected_business_object", "business_state",
                "form_values_hash", "checked_hash", "disabled_hash", "filter_hash", "pagination_hash", "selection_hash",
            ],
            "review_fingerprint_separate": True,
        },
        "target_resolution": {
            "scope": "current_context_root", "visible_only": True, "cardinality": "exactly_one",
            "zero_result": "unresolved", "multiple_result": "block_ambiguous",
        },
        "selection_contract": {
            "ui_grounded_points_require_marker": True,
            "interaction": "bidirectional_marker_card_target",
            "selected_surfaces": ["marker", "card", "target"],
            "target_selected_attribute": "data-review-target-selected",
            "target_focus_style": "visible_focus_ring",
        },
        "progress_contract": {
            "denominator": "declared_applicable_review_points",
            "resolved_states": ["confirmed", "accepted_with_gap"],
            "navigation_advances_progress": False,
        },
        "share_contract": {
            "locator_fields": ["baseline_ref", "context_ref", "review_point_ref", "active_tab"],
            "forbidden_locator_fields": ["journey", "step", "role"],
            "hydrate_on_load": True,
        },
        "review_record_contract": {
            "persistence_required": True,
            "key_fields": ["baseline_ref", "context_ref", "review_point_ref"],
            "dispositions": ["unreviewed", "confirmed", "accepted_with_gap", "blocked"],
            "static_fallback": ["localStorage", "json_export", "json_import"],
            "baseline_mismatch": "do_not_reuse",
        },
        "cold_read_contract": {
            "required_for": ["R1", "R2"],
            "participant_roles": ["product", "frontend", "backend", "qa"],
            "time_limit_seconds": 180,
            "declared_point_recall_min": 0.8,
            "critical_point_recall": 1,
            "status": "pending",
            "evidence_refs": [],
        },
        "unknown_refs": [],
        "machine_handoff": {"status": "not_requested", "manifest_ref": None, "packet_refs": [], "gap_refs": []},
        "not_proven": ["静态合同不证明浏览器行为、真实系统实现或客户验收。"],
    }


def review_html(document: dict, *, include_tabs: bool = True) -> str:
    point_by_ref = {item["ref"]: item for item in document["review_points"]}
    context_parts = []
    for context in document["review_contexts"]:
        context_ref = context["context_ref"]
        hidden = "" if context_ref == document["workspace"]["initial_context_ref"] else " hidden"
        testid = ' data-testid="page-VIEW-X"' if context_ref == "VIEW-X" else ""
        points = []
        for number, point_ref in enumerate(context["review_point_refs"], start=1):
            point = point_by_ref[point_ref]
            points.append(
                f'<button data-action="{point["target_ref"]}" data-ac="{point["acceptance_refs"][0]}">{point["title"]}</button>'
                f'<button data-action="UIACT-REVIEW-SELECT" data-review-ref="{point_ref}" '
                f'data-review-context="{context_ref}" data-review-number="{number}" aria-current="false">{number}</button>'
            )
        page_contract = ""
        if context["context_type"] == "VIEW":
            surfaces = ",".join(context.get("surface_types", []))
            layout = "composite" if len(context.get("surface_types", [])) > 1 else "single"
            page_contract = f'<!-- PAGE-CONTRACT: {context_ref}; primary=list; layout={layout}; surfaces={surfaces} -->'
        context_parts.append(
            f'{page_contract}<main{testid}{hidden} data-review-context-root="{context_ref}" '
            f'data-review-context-type="{context["context_type"]}">{"".join(points)}</main>'
        )

    cards = []
    for context in document["review_contexts"]:
        for number, point_ref in enumerate(context["review_point_refs"], start=1):
            point = point_by_ref[point_ref]
            cards.append(
                f'<article data-action="UIACT-REVIEW-SELECT" data-review-point="{point_ref}" data-review-context="{context["context_ref"]}" '
                f'data-review-number="{number}" data-review-business-status="{point["business_status"]}" '
                f'data-review-verification-status="{point["verification_status"]}" '
                f'data-review-evidence-origin="{point["evidence_origin"]}" aria-current="false">'
                f'<h3>{point["title"]}</h3><p>{point["summary"]}</p>'
                f'<p>业务：已确认 · 验证：未执行 · 来源：明确来源</p></article>'
            )

    tab_buttons = "".join(
        f'<button data-action="UIACT-REVIEW-TAB" data-review-tab-target="{tab}">{label}</button>'
        for tab, label in (
            ("overview", "总览"), ("function_flow", "功能与流转"),
            ("boundary_acceptance", "边界与验收"),
        )
    )
    semantic_function = "".join(
        f'<p data-review-semantic-ref="{item["coverage_id"]}" data-review-semantic-owner="function_flow" '
        f'data-review-context="{item["owner_context_ref"]}">{item["human_summary"]}</p>'
        for item in document.get("semantic_coverage_items", [])
        if item.get("detail_owner") == "function_flow"
    )
    semantic_boundary = "".join(
        f'<p data-review-semantic-ref="{item["coverage_id"]}" data-review-semantic-owner="boundary_acceptance" '
        f'data-review-context="{item["owner_context_ref"]}">{item["human_summary"]}</p>'
        for item in document.get("semantic_coverage_items", [])
        if item.get("detail_owner") == "boundary_acceptance"
    )
    tab_sections = f'''
      <nav>{tab_buttons}</nav>
      <section data-review-tab="overview">
        <div data-review-content="goals_success" data-review-owner-tab="overview">目标与成功信号</div>
        <div data-review-content="scope" data-review-owner-tab="overview">范围与非目标</div>
        <div data-review-content="main_chain" data-review-owner-tab="overview">业务主链</div>
      </section>
      <section data-review-tab="function_flow">
        <div data-review-content="current_context" data-review-owner-tab="function_flow">当前上下文</div>
        <div data-review-content="review_points" data-review-owner-tab="function_flow">{"".join(cards)}</div>
        {semantic_function}
        <div data-review-content="visible_domain_results" data-review-owner-tab="function_flow">可见结果与领域结果</div>
      </section>
      <section data-review-tab="boundary_acceptance">
        <div data-review-content="rules" data-review-owner-tab="boundary_acceptance">规则与权限</div>
        {semantic_boundary}
        <div data-review-content="acceptance_tests" data-review-owner-tab="boundary_acceptance">AC-X-SUBMIT / AC-X-CONFIRM</div>
        <div data-review-content="open_items" data-review-owner-tab="boundary_acceptance">开放项已核对：0 项</div>
      </section>''' if include_tabs else f'<section data-review-r0>{"".join(cards)}{semantic_function}{semantic_boundary}</section>'

    workspace = document["workspace"]
    review_controls = f'''
      <button data-action="UIACT-REVIEW-TOGGLE" data-ads-act="collapse">收起说明</button>
      <button data-action="UIACT-REVIEW-TOGGLE" data-ads-act="expand">展开说明</button>
      <button data-action="UIACT-REVIEW-SHARE" data-review-share-locator>复制定位</button>
      <button data-action="UIACT-REVIEW-RECORD">提交评审结论</button>
      <button data-action="UIACT-REVIEW-EXPORT">导出记录</button>
      <button data-action="UIACT-REVIEW-IMPORT">导入记录</button>
      <button data-action="UIACT-REVIEW-COMPACT">切换全屏</button>
      <div data-review-progress data-review-progress-denominator="{sum(len(item['review_point_refs']) for item in document['review_contexts'])}" data-review-progress-resolved="0">0/{sum(len(item['review_point_refs']) for item in document['review_contexts'])}</div>
      <div data-review-records>评审记录</div>'''
    handlers = [
        "ACT-X-NAVIGATE", *[str(item["target_ref"]) for item in document["review_points"]],
        "UIACT-REVIEW-SELECT", "UIACT-REVIEW-TOGGLE",
        "UIACT-REVIEW-SHARE", "UIACT-REVIEW-RECORD", "UIACT-REVIEW-EXPORT",
        "UIACT-REVIEW-IMPORT", "UIACT-REVIEW-COMPACT",
    ] + (["UIACT-REVIEW-TAB"] if include_tabs else [])
    registry = ",".join(f'"{item}":()=>true' for item in handlers)
    script = f'''
      const productContextEvent="product-context-change";
      window.__ADS_REVIEW_GATE__={{status:"passed",violations:[]}};
      function resolveProductLocation(){{const observed={{active_menu_path:["业务管理","记录列表"],expanded_menu_ancestors:["业务管理"],breadcrumb:["业务管理","记录列表"],page_title:"记录列表"}},expected={{...observed}},diff={{}};return {{observed,expected,diff,...observed}}}}
      function syncProductLocation(){{return resolveProductLocation()}}
      function assertProductLocationSynchronized(){{const location=syncProductLocation();if(!location.active_menu_path.length)throw new Error("product location missing");return true}}
      function captureProductFingerprint(){{const productLocation=resolveProductLocation();return JSON.stringify({{active_view:"VIEW-X",route:window.location.hash,active_menu_path:productLocation.active_menu_path,expanded_menu_ancestors:productLocation.expanded_menu_ancestors,breadcrumb:productLocation.breadcrumb,page_title:productLocation.page_title,overlay_stack:[],selected_business_object:null,business_state:"ready",form_values_hash:"0",checked_hash:"0",disabled_hash:"0",filter_hash:"0",pagination_hash:"0",selection_hash:"0"}})}}
      function captureReviewFingerprint(){{return JSON.stringify({{tab:document.querySelector("[data-review-workspace]").dataset.reviewActiveTab}})}}
      function assertProductFingerprintInvariant(before,after){{if(before!==after){{window.__ADS_REVIEW_GATE__.status="failed";throw new Error("PROTO-REVIEW-PRODUCT-FINGERPRINT-INVARIANT")}}}}
      function runReviewAction(handler){{const before=captureProductFingerprint();handler();const after=captureProductFingerprint();assertProductFingerprintInvariant(before,after);captureReviewFingerprint()}}
      function resolveCurrentContext(){{assertProductLocationSynchronized();return document.querySelector("[data-review-current-context]").dataset.reviewCurrentContext}}
      const PROTO_REVIEW_OVERLAY_UNDECLARED="PROTO-REVIEW-OVERLAY-UNDECLARED";
      window.addEventListener(productContextEvent,resolveCurrentContext);
      new MutationObserver(()=>resolveCurrentContext()).observe(document.body,{{attributes:true,subtree:true}});
      function currentContextRoot(){{return document.querySelector(`[data-review-context-root="${{resolveCurrentContext()}}"]`)}}
      function isTargetVisible(node){{return !node.hidden}}
      function exactlyOne(nodes){{if(nodes.length!==1)throw new Error("target cardinality");return nodes[0]}}
      function resolveReviewTarget(selector){{const nodes=[...currentContextRoot().querySelectorAll(selector)].filter(isTargetVisible);if(nodes.length===0)throw new Error("PROTO-REVIEW-TARGET-UNRESOLVED");if(nodes.length>1)throw new Error("PROTO-REVIEW-TARGET-AMBIGUOUS");return nodes[0]}}
      function focusReviewTarget(pointRef,selector){{document.querySelectorAll("[data-review-target-selected]").forEach(node=>node.removeAttribute("data-review-target-selected"));document.querySelectorAll("[data-review-ref],[data-review-point]").forEach(node=>node.setAttribute("aria-current",String((node.dataset.reviewRef||node.dataset.reviewPoint)===pointRef)));resolveReviewTarget(selector).setAttribute("data-review-target-selected","true")}}
      const pointSelectors={json.dumps({item['ref']: f"[data-action='{item['target_ref']}']" for item in document['review_points']}, ensure_ascii=False)};
      const shareLocator=new URLSearchParams({{baseline_ref:"{document['baseline']['version']}",context_ref:"VIEW-X",review_point_ref:"{document['review_contexts'][0]['review_point_refs'][0]}",active_tab:"overview"}}); location.hash=shareLocator.toString();
      function hydrateLocator(){{return new URLSearchParams(location.hash.slice(1)).get("context_ref")}}
      function saveReviewRecords(value){{localStorage.setItem("review:{document['baseline']['version']}",JSON.stringify(value))}}
      function loadReviewRecords(){{return JSON.parse(localStorage.getItem("review:{document['baseline']['version']}")||"[]")}}
      function applyDomainResult(){{document.querySelector("[data-domain-state]").setAttribute("data-state","updated")}}
      const actionRegistry={{{registry}}};
      {''.join(f'actionRegistry["{item["target_ref"]}"]=applyDomainResult;' for item in document['review_points'])}
      actionRegistry["UIACT-REVIEW-SELECT"]=(node)=>{{const pointRef=node.dataset.reviewRef||node.dataset.reviewPoint;focusReviewTarget(pointRef,pointSelectors[pointRef])}};
      document.addEventListener("click",event=>{{const node=event.target.closest("[data-action]");if(!node)return;const handler=actionRegistry[node.dataset.action];if(!handler)return;if(node.dataset.action==="UIACT-REVIEW-TOGGLE")document.body.classList.toggle("ads-collapsed",node.dataset.adsAct==="collapse");if(node.dataset.action.startsWith("UIACT-REVIEW-"))runReviewAction(()=>handler(node));else handler(node)}});
    '''
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><style>body{{display:grid;grid-template-columns:minmax(0,1fr) minmax(320px,420px)}}.active{{font-weight:700}}[data-review-workspace]{{min-width:0}}[data-review-target-selected="true"]{{outline:3px solid #6d5dfc;outline-offset:3px}}</style></head><body>
      <nav><button class="active" data-action="ACT-X-NAVIGATE" data-view-target="VIEW-X">记录列表</button></nav>
      {"".join(context_parts)}
      <output data-domain-state data-state="ready">等待业务操作</output>
      <aside data-review-workspace="REVIEW-X" data-review-level="{workspace["review_level"]}"
        data-review-active-tab="{workspace["default_tab"]}" data-review-current-context="{workspace["initial_context_ref"]}"
        data-review-current-context-control="read-only" data-review-layout="participate-in-layout"
        data-review-overlay-product-ui="false" data-review-resizable="true" data-review-collapsible="true">
        <p data-review-product-location>系统位置：业务管理 / 记录列表</p>
        {tab_sections}{review_controls}
      </aside>
      <script type="application/json" id="review-workspace-manifest">{json.dumps(document, ensure_ascii=False)}</script>
      <script>{script}</script>
    </body></html>'''


def html_gate(path: Path, raw: str) -> Gate:
    path.write_text(raw, encoding="utf-8")
    gate = Gate()
    gate.check_prototype(path, "L2")
    return gate


def review_codes(path: Path, document: dict, *, include_tabs: bool = True) -> set[str]:
    return {item.code for item in html_gate(path, review_html(document, include_tabs=include_tabs)).findings}


def cli_codes(prototype: Path, *runs: Path) -> tuple[int, set[str]]:
    args = [
        str(ROOT / "scripts/ai_delivery_spec_cli.py"), "gate", "--profile", "prototype",
        "--prototype", str(prototype), "--level", "L2", "--format", "json",
    ]
    for path in runs:
        args.extend(("--acceptance-run", str(path)))
    result = run(*args)
    return result.returncode, {item["code"] for item in json.loads(result.stdout)["findings"]}


def test_complete_final_workspace_passes_static_review_contract(tmp_path: Path) -> None:
    codes = review_codes(tmp_path / "review.html", manifest("1" * 64))
    assert not {code for code in codes if code.startswith("PROTO-REVIEW-")}
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" not in codes


def test_v548_metrics_workflow_and_secondary_surfaces_cannot_silently_escape(tmp_path: Path) -> None:
    for surface, code in (("metrics", "PROTO-REVIEW-METRIC-UNCOVERED"), ("workflow", "PROTO-REVIEW-STATE-PATH-UNCOVERED")):
        document = manifest("1" * 64)
        document["review_contexts"][0]["surface_types"].append(surface)
        assert code in review_codes(tmp_path / f"{surface}-missing.html", document)

    partial = manifest("1" * 64)
    partial["review_contexts"][0]["surface_types"].append("metrics")
    partial["semantic_coverage_items"][0].update({
        "subject_ref": "METRIC-ONE", "semantic_type": "metric", "target_ref": "METRIC-ONE",
        "detail_owner": "boundary_acceptance",
    })
    partial["review_points"][0].update({
        "subject_ref": "METRIC-ONE", "target_ref": "METRIC-ONE",
        "target_selector": "[data-action='METRIC-ONE']",
    })
    raw = review_html(partial).replace("</main>", '<div data-metric="METRIC-TWO">未声明指标</div><div class="metric">无 ID 指标</div></main>', 1)
    assert "PROTO-REVIEW-METRIC-UNCOVERED" in {item.code for item in html_gate(tmp_path / "metrics-partial.html", raw).findings}

    secondary = manifest("1" * 64)
    secondary["review_contexts"][0]["secondary_context_refs"] = []
    assert "PROTO-REVIEW-OVERLAY-UNCOVERED" in review_codes(tmp_path / "drawer-missing.html", secondary)


def test_v548_semantic_projection_must_be_visible_and_critical_gap_blocks(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    raw = review_html(document).replace('data-review-semantic-ref="SCOV-VIEW-SUBMIT"', 'data-review-semantic-ref="SCOV-MISSING"', 1)
    codes = {item.code for item in html_gate(tmp_path / "semantic-hidden.html", raw).findings}
    assert "PROTO-REVIEW-SEMANTIC-COVERAGE" in codes

    gap = manifest("1" * 64)
    gap_item = gap["semantic_coverage_items"][1]
    gap_item["coverage_status"] = "gap"
    gap_item["unknown_ref"] = "UNK-DRAWER-CONFIRM-RULE"
    gap["unknown_refs"] = ["UNK-DRAWER-CONFIRM-RULE"]
    assert "PROTO-REVIEW-SEMANTIC-COVERAGE" in review_codes(tmp_path / "semantic-gap.html", gap)


def test_v548_business_dialog_without_current_context_is_blocked(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace(
        "</main>", '<section role="dialog" data-testid="drawer-unmapped">未声明二级功能</section></main>', 1,
    )
    assert "PROTO-REVIEW-OVERLAY-UNCOVERED" in {item.code for item in html_gate(tmp_path / "unmapped-dialog.html", raw).findings}


def test_review_workspace_structural_mutations_are_blocked(tmp_path: Path) -> None:
    base = review_html(manifest("1" * 64))
    candidate_raw = base.replace('</main>', '<button data-action="ACT-X-DELETE" data-ac="AC-X-DELETE">删除</button></main>', 1).replace(
        '"ACT-X-SUBMIT":()=>true', '"ACT-X-SUBMIT":()=>true,"ACT-X-DELETE":()=>true')
    cases = (
        (base.replace('<button class="active" data-action="ACT-X-NAVIGATE"', '<button class="active" disabled data-action="ACT-X-NAVIGATE"', 1), "PROTO-PRODUCT-LOCATION-MISMATCH"),
        (base.replace("syncProductLocation", "lostProductLocationSync"), "PROTO-PRODUCT-LOCATION-MISMATCH"),
        (base.replace('<nav><button data-action="UIACT-REVIEW-TAB"', '<nav data-review-mode="journey"><button data-action="UIACT-REVIEW-TAB"', 1), "PROTO-REVIEW-LEVEL"),
        (base.replace('data-review-context="DRAWER-X" data-review-number="1"', 'data-review-context="DRAWER-X" data-review-number="2"'), "PROTO-REVIEW-CONTEXT-NUMBERING"),
        (base.replace('<button data-action="ACT-X-SUBMIT"', '<button data-action="ACT-X-SUBMIT">副本</button><button data-action="ACT-X-SUBMIT"', 1), "PROTO-REVIEW-TARGET-RESOLUTION"),
        (base.replace("focusReviewTarget", "missingTargetFocus"), "PROTO-REVIEW-SELECTION-NOT-SYNCED"),
        (base.replace('data-review-evidence-origin="explicit_source"', '', 1), "PROTO-REVIEW-STATUS-AXES"),
        (base.replace("assertProductFingerprintInvariant", "lostInvariant"), "PROTO-REVIEW-PRODUCT-FINGERPRINT-INVARIANT"),
        (base.replace('[data-review-workspace]{min-width:0}', '[data-review-workspace]{position:fixed;min-width:0}'), "PROTO-REVIEW-LAYOUT-NONOVERLAP"),
        (base.replace("localStorage.setItem", "memoryStore.setItem").replace("localStorage.getItem", "memoryStore.getItem"), "PROTO-REVIEW-RECORD-PERSISTENCE"),
        (candidate_raw, "PROTO-REVIEW-CANDIDATE-DIFF"),
    )
    for index, (raw, expected) in enumerate(cases):
        assert expected in {item.code for item in html_gate(tmp_path / f"mutation-{index}.html", raw).findings}


def test_overlay_can_inherit_a_menu_exempt_parent_without_fake_menu_path(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    parent = document["review_contexts"][0]["product_location"]
    parent.update({
        "navigation_mode": "menu_exempt", "menu_path": [], "active_entry_selector": None,
        "exemption_reason": "独立 H5 页面通过扫码或外部链接进入",
    })
    child = document["review_contexts"][1]["product_location"]
    child.update({"menu_path": [], "active_entry_selector": None})
    codes = review_codes(tmp_path / "menu-exempt-parent.html", document)
    assert "PROTO-REVIEW-WORKSPACE-SCHEMA" not in codes
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" not in codes

    child["menu_path"] = ["伪造菜单"]
    codes = review_codes(tmp_path / "menu-exempt-drift.html", document)
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" in codes


def test_declaration_is_the_only_denominator_and_numbers_restart_per_context(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_contexts"][1]["review_point_refs"] = ["RVP-VIEW-SUBMIT", "RVP-DRAWER-CONFIRM"]
    assert "PROTO-REVIEW-DECLARED-DENOMINATOR" in review_codes(tmp_path / "duplicate-owner.html", document)

def test_ui_grounded_review_point_requires_left_marker(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_points"][0]["marker_required"] = False
    assert "PROTO-REVIEW-MARKER-REQUIRED" in review_codes(tmp_path / "card-only.html", document)


def test_r0_may_omit_visible_tabs_but_keeps_context_and_denominator(tmp_path: Path) -> None:
    document = manifest("1" * 64, level="R0")
    codes = review_codes(tmp_path / "r0.html", document, include_tabs=False)
    assert not {code for code in codes if code.startswith("PROTO-REVIEW-")}


def test_overlay_detection_rejects_ambiguous_topmost_candidates(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_contexts"].append({
        "context_ref": "MODAL-X", "context_type": "MODAL", "title": "冲突浮层",
        "detection": copy.deepcopy(document["review_contexts"][1]["detection"]),
        "product_location": copy.deepcopy(document["review_contexts"][1]["product_location"]),
        "surface_types": ["form"],
        "secondary_context_refs": [],
        "review_point_refs": [],
    })
    assert "PROTO-REVIEW-OVERLAY-DETECTION" in review_codes(tmp_path / "ambiguous-overlay.html", document)


def test_passed_review_point_requires_resolved_acceptance_evidence(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    point = document["review_points"][0]
    point["verification_status"] = "passed"
    point["evidence_refs"] = ["ARUN-X"]
    prototype = tmp_path / "passed.html"
    prototype.write_text(review_html(document), encoding="utf-8")
    code, codes = cli_codes(prototype)
    assert code == 2 and "PROTO-REVIEW-VERIFICATION-ARUN-UNRESOLVED" in codes


def test_legacy_overlay_is_gap_for_visual_review_but_blocked_for_handoff(tmp_path: Path) -> None:
    old = tmp_path / "old.html"
    old.write_text('<body class="review-mode"><main data-testid="page-VIEW-OLD-001"><button data-action="UIACT-REVIEW-SELECT" data-review-id="R1">1</button><aside data-review-id="R1">说明</aside><script>const actions={"UIACT-REVIEW-SELECT":()=>true};</script></main></body>', encoding="utf-8")
    prd = tmp_path / "prd.md"
    prd.write_text("# 基线\n\nREQ-OLD-001 / VIEW-OLD-001 / AC-OLD-001\n", encoding="utf-8")
    gate = Gate()
    gate.check_prototype(old, "L2")
    assert any(item.code == "PROTO-REVIEW-WORKSPACE-LEGACY" and item.severity == "GAP" for item in gate.findings)
    gate.check_handoff(prd, [old], "L2")
    assert any(item.code == "PROTO-REVIEW-WORKSPACE-REQUIRED" and item.severity == "BLOCK" for item in gate.findings)


def test_versioned_review_compatibility_matrix_is_enforced(tmp_path: Path) -> None:
    stages = (ROOT / "references/stages.md").read_text(encoding="utf-8")
    for marker in ("5.4.6—5.4.9 兼容与迁移矩阵", "PROTO-REVIEW-WORKSPACE-LEGACY", "5.4.7-final", "5.4.8/RC3", "5.4.9", "RC4", "兼容读取不等于自动升级"):
        assert marker in stages

    rc2 = manifest("1" * 64)
    rc2["schema_version"] = "5.4.7-final"
    rc2["contract_revision"] = "RC2"
    rc2.pop("semantic_coverage_contract")
    rc2.pop("semantic_coverage_items")
    for context in rc2["review_contexts"]:
        context.pop("surface_types")
        context.pop("secondary_context_refs")
    rc2_codes = review_codes(tmp_path / "v547-final.html", rc2)
    assert "PROTO-REVIEW-WORKSPACE-MANIFEST-INVALID" not in rc2_codes
    assert "PROTO-REVIEW-SEMANTIC-COVERAGE" not in rc2_codes

    downgraded = copy.deepcopy(rc2)
    downgraded["schema_version"] = "5.4.8"
    downgraded_codes = review_codes(tmp_path / "v548-downgraded.html", downgraded)
    assert "PROTO-REVIEW-WORKSPACE-SCHEMA" in downgraded_codes


def test_review_workspace_hash_and_handoff_indicator_match_real_inputs(tmp_path: Path) -> None:
    prd = tmp_path / "prd.md"
    prd.write_text(baseline_prd(), encoding="utf-8")
    document = manifest("2" * 64)
    html = tmp_path / "review.html"
    gate = html_gate(html, review_html(document))
    gate.check_handoff(prd, [html], "L2")
    assert any(item.code == "PROTO-REVIEW-BASELINE-DRIFT" for item in gate.findings)

    baseline_hash = hashlib.sha256(prd.read_text(encoding="utf-8").encode()).hexdigest()
    document["baseline"]["hash"] = baseline_hash
    handoff = tmp_path / "handoff.yaml"
    handoff.write_text(
        f"schema_version: 5.3.0\nstatus: ready_for_implementation\nbaseline:\n  version: '1.0'\n  hash: {baseline_hash}\n  requirement_ref: prd.md\npackets:\n  - id: MOD-X\n    kind: mod\n    owner: team\n    path: packets/core.md\n    baseline_hash: {baseline_hash}\n    scope_refs: [REQ-X]\n    acceptance_refs: [AC-X-SUBMIT]\nhandoffs: []\n",
        encoding="utf-8",
    )
    document["machine_handoff"] = {"status": "ready", "manifest_ref": "handoff.yaml", "packet_refs": ["MOD-X"], "gap_refs": []}
    gate = html_gate(html, review_html(document))
    gate.check_review_manifest_binding(handoff)
    assert not {item.code for item in gate.findings if item.code.startswith("PROTO-REVIEW-HANDOFF-")}


def test_rc2_closes_semantic_escape_hatches(tmp_path: Path) -> None:
    cases = []
    bad_target = manifest("1" * 64)
    bad_target["review_points"][0]["target_mode"] = "context_root"
    cases.append((bad_target, "PROTO-REVIEW-TARGET-MODE-INVALID"))
    overlap = manifest("1" * 64)
    overlap["candidate_review_points"] = [candidate("ACT-X-SUBMIT")]
    cases.append((overlap, "PROTO-REVIEW-CANDIDATE-DECLARATION-OVERLAP"))
    no_cold_read = manifest("1" * 64, level="R2")
    no_cold_read["cold_read_contract"]["status"] = "not_applicable"
    cases.append((no_cold_read, "PROTO-REVIEW-COLD-READ"))
    no_hydration = manifest("1" * 64)
    no_hydration["share_contract"]["hydrate_on_load"] = False
    cases.append((no_hydration, "PROTO-REVIEW-SHARE-LOCATOR"))
    for index, (document, expected) in enumerate(cases):
        assert expected in review_codes(tmp_path / f"escape-{index}.html", document)

    r0 = manifest("1" * 64, level="R0")
    r0["cold_read_contract"]["status"] = "not_applicable"
    assert "PROTO-REVIEW-COLD-READ" not in review_codes(tmp_path / "r0-na.html", r0, include_tabs=False)


def test_handoff_resolves_every_reviewpoint_reference_against_prd(tmp_path: Path) -> None:
    prd = tmp_path / "prd.md"
    prd.write_text(baseline_prd(), encoding="utf-8")
    document = manifest(hashlib.sha256(prd.read_bytes()).hexdigest())
    html = tmp_path / "resolved.html"
    gate = html_gate(html, review_html(document))
    gate.check_handoff(prd, [html], "L2")
    unresolved = {item.code for item in gate.findings if "UNRESOLVED" in item.code}
    assert not unresolved

    point = document["review_points"][0]
    point.update({
        "subject_ref": "ACT-GHOST", "target_ref": "ACT-GHOST", "source_refs": ["SRC-GHOST"],
        "precondition_refs": ["RULE-GHOST"], "boundary_refs": ["EDGE-GHOST"],
        "acceptance_refs": ["AC-GHOST"],
    })
    prd.write_text(baseline_prd() + "\nACT-GHOST / SRC-GHOST / RULE-GHOST / EDGE-GHOST / AC-GHOST\n", encoding="utf-8")
    html = tmp_path / "unresolved.html"
    gate = html_gate(html, review_html(document))
    gate.check_handoff(prd, [html], "L2")
    codes = {item.code for item in gate.findings}
    assert {"PROTO-REVIEW-SUBJECT-UNRESOLVED", "PROTO-REVIEW-SOURCE-UNRESOLVED",
            "PROTO-REVIEW-REF-UNRESOLVED", "PROTO-REVIEW-AC-UNRESOLVED"} <= codes


def test_repaired_cli_and_query_surfaces_are_truthful() -> None:
    candidate = run("scripts/ai_delivery_spec_cli.py", "candidate", "--help")
    assert candidate.returncode == 0 and "validate" in candidate.stdout and "校验本地候选" in candidate.stdout
    section = run("scripts/query_domain.py", "--domain", "crm", "--section", "Domain Events", "--format", "markdown")
    assert section.returncode == 0 and "Domain Events" in section.stdout and "Compact context" not in section.stdout
    for code in ("PROTO-REVIEW-MODE-MISSING", "PROTO-REVIEW-LENS-NOT-INTERACTIVE"):
        explained = run("scripts/ai_delivery_spec_cli.py", "explain-finding", code, "--format", "json")
        payload = explained.stdout
        assert explained.returncode == 0 and "CurrentContext" in payload and "orientation/journey/focus/page" not in payload


def test_prototype_cannot_label_one_value_confirmed_and_unknown(tmp_path: Path) -> None:
    path = tmp_path / "conflict.html"
    raw = '<main data-testid="page-VIEW-METRIC-001"><div data-metric="METRIC-RATE-001" data-metric-status="confirmed" data-unk="UNK-RATE-001" data-unk-priority="P1" data-unk-owner="产品负责人" data-unk-blocks-stage="baseline" data-unk-affected-refs="METRIC-RATE-001" data-unk-fallback="不展示该指标">完成率</div></main>'
    gate = html_gate(path, raw)
    assert any(item.code == "PROTO-UNKNOWN-CONFIRMED-CONFLICT" for item in gate.findings)


def test_stage0_and_l1_skeletons_cannot_pass_as_content(tmp_path: Path) -> None:
    gate = Gate()
    gate.check_stage0(ROOT / "references/templates/stage0-inventory-template.yaml")
    assert any(item.code == "STAGE0-PLACEHOLDER" and item.severity == "BLOCK" for item in gate.findings)
    prd = tmp_path / "l1.md"
    prd.write_text('---\ndocument_language: zh-CN\ndelivery_level: L1\nactivated_facets: ui\n---\n# 需求卡\n## 来源、问题与价值\n来源与价值已确认。\n## 目标、范围与非目标\n提交单条记录，不做批量。\n## 角色、用户故事与权限\n业务员提交，管理员查看。\n## 旅程、流程、异常与状态\n失败保留输入，成功可见。\n## 验收与测试\n校验成功和拒绝路径。\n## 未知项与升级判断\n无开放未知项。\n', encoding="utf-8")
    gate = Gate()
    gate.check_prd(prd, "L1")
    codes = {item.code for item in gate.findings}
    assert "PRD-L1-SECTION-MISSING" in codes and "PRD-BAD-ACTIVATED-FACETS" in codes


def test_baseline_status_cannot_contradict_draft_version_or_document_control(tmp_path: Path) -> None:
    prd = tmp_path / "draft-claimed-baseline.md"
    prd.write_text(
        """---
document_language: zh-CN
delivery_level: L2
baseline_version: 0.1-draft
status: baseline
open_p0_unknown_ids: []
unknowns: []
activated_facets: []
---
# 示例需求

| 项目 | 内容 |
|---|---|
| 状态 | 草稿（待评审基线） |
""",
        encoding="utf-8",
    )
    gate = Gate()
    gate.check_prd(prd, "L2")
    assert "PRD-STATUS-CONTRADICTION" in {item.code for item in gate.findings}


def test_rc2_candidate_is_physically_separate_from_declaration(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["candidate_review_points"] = [candidate()]
    before = sum(len(item["review_point_refs"]) for item in document["review_contexts"])
    codes = review_codes(tmp_path / "candidate.html", document)
    after = sum(len(item["review_point_refs"]) for item in document["review_contexts"])
    assert before == after == 2
    assert "PROTO-REVIEW-DECLARED-DENOMINATOR" not in codes


def test_rc2_rejects_confirmed_prototype_inference(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_points"][0]["evidence_origin"] = "prototype_inferred"
    codes = review_codes(tmp_path / "inferred-confirmed.html", document)
    assert "PROTO-REVIEW-WORKSPACE-SCHEMA" in codes or "PROTO-REVIEW-STATUS-AXES" in codes


def test_rc2_requires_separate_rvp_record_identity(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_points"][0]["ref"] = "RP-VIEW-SUBMIT"
    document["review_contexts"][0]["review_point_refs"] = ["RP-VIEW-SUBMIT"]
    codes = review_codes(tmp_path / "legacy-review-id.html", document)
    assert "PROTO-REVIEW-TRUTH-ID" in codes


def test_rc2_requires_expand_button_and_hydration(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace('data-ads-act="expand"', 'data-ads-act="missing"', 1)
    codes = {item.code for item in html_gate(tmp_path / "no-expand.html", raw).findings}
    assert "PROTO-REVIEW-COLLAPSE-ROUNDTRIP" in codes
    raw = review_html(manifest("1" * 64)).replace("function hydrateLocator()", "function omittedHydration()", 1)
    codes = {item.code for item in html_gate(tmp_path / "no-hydrate.html", raw).findings}
    assert "PROTO-REVIEW-SHARE-LOCATOR" in codes


def manifest_v549(baseline_hash: str) -> dict:
    document = manifest(baseline_hash)
    document["schema_version"] = "5.4.9"
    document["contract_revision"] = "RC4"
    for point in document["review_points"]:
        point["implementation_detail"] = {
            "required": True,
            "reason": "该动作会写入业务对象并影响后续页面结果",
            "roles": ["frontend", "backend", "qa"],
        }
    document["human_projection_contract"] = {
        "primary_copy": "business_natural_language",
        "stable_ids_visibility": "collapsed_technical_trace_only",
        "field_enums_visibility": "collapsed_technical_trace_only",
        "implementation_detail_mode": "progressive_disclosure",
        "implementation_detail_roles": ["frontend", "backend", "qa"],
        "technical_terms": ["recordStatus", "saved"],
    }
    document["diagram_contract"] = {
        "simple_crud_policy": "not_required",
        "decisions": [
            {
                "context_ref": "VIEW-X", "complexity_drivers": ["cross_page", "cross_role"],
                "required_types": ["core_flow"], "diagram_refs": ["DIAG-X-CORE"],
                "not_required_reason": None,
            },
            {
                "context_ref": "DRAWER-X", "complexity_drivers": ["cross_page"],
                "required_types": ["core_flow"], "diagram_refs": ["DIAG-X-CORE"],
                "not_required_reason": None,
            },
        ],
        "diagrams": [
            {
                "diagram_ref": "DIAG-X-CORE", "diagram_type": "core_flow", "owner_tab": "overview",
                "title": "记录提交与确认流程", "context_refs": ["VIEW-X", "DRAWER-X"],
                "current_context_highlight": True,
            }
        ],
    }
    document["acceptance_examples"] = [
        {
            "example_ref": "TEST-X-VIEW-POS", "owner_context_ref": "VIEW-X", "kind": "positive",
            "precondition": "操作者拥有提交权限且记录内容完整", "action": "点击提交当前记录",
            "expected_visible_result": "页面显示提交成功并刷新当前记录", "expected_domain_result": "记录被持久保存且产生一条审计记录",
            "acceptance_ref": "AC-X-SUBMIT",
        },
        {
            "example_ref": "TEST-X-VIEW-NEG", "owner_context_ref": "VIEW-X", "kind": "negative",
            "precondition": "必填内容缺失或操作者没有提交权限", "action": "尝试提交当前记录",
            "expected_visible_result": "页面指出具体问题并保留已有输入", "expected_domain_result": "记录不写入且不产生成功事件",
            "acceptance_ref": "AC-X-SUBMIT",
        },
        {
            "example_ref": "TEST-X-DRAWER-POS", "owner_context_ref": "DRAWER-X", "kind": "positive",
            "precondition": "确认抽屉已打开且变更仍是最新版本", "action": "点击确认变更",
            "expected_visible_result": "抽屉关闭并在原页面显示最新结果", "expected_domain_result": "变更被保存并记录操作者与时间",
            "acceptance_ref": "AC-X-CONFIRM",
        },
        {
            "example_ref": "TEST-X-DRAWER-NEG", "owner_context_ref": "DRAWER-X", "kind": "negative",
            "precondition": "当前记录已被其他人更新为新版本", "action": "继续确认旧版本变更",
            "expected_visible_result": "抽屉保留并提示刷新后重新确认", "expected_domain_result": "旧版本不覆盖新版本且记录冲突日志",
            "acceptance_ref": "AC-X-CONFIRM",
        },
    ]
    return document


def review_html_v549(document: dict) -> str:
    raw = review_html(document)
    raw = raw.replace("AC-X-SUBMIT / AC-X-CONFIRM", "以下样例覆盖提交成功、权限拒绝、确认成功和版本冲突。")
    core_flow = '''<div data-review-content="core_flow_diagram" data-review-owner-tab="overview">
      <figure data-review-diagram="DIAG-X-CORE" data-review-diagram-type="core_flow" data-review-diagram-owner="overview" data-review-context="VIEW-X">
        <figcaption>记录提交与确认流程</figcaption>
        <div data-review-flow-context="VIEW-X" data-review-diagram-ref="DIAG-X-CORE" data-flow-current="true">填写并提交记录（当前页面）</div>
        <div>校验通过后进入确认</div>
        <div data-review-flow-context="DRAWER-X" data-review-diagram-ref="DIAG-X-CORE" data-flow-current="false">确认变更并返回原页面</div>
      </figure>
    </div>'''
    if document.get("diagram_contract", {}).get("diagrams"):
        raw = raw.replace(
            '<div data-review-content="main_chain" data-review-owner-tab="overview">业务主链</div>',
            '<div data-review-content="main_chain" data-review-owner-tab="overview">业务主链</div>' + core_flow,
        )
    for point in document["review_points"]:
        point_ref = point["ref"]
        title = point["title"]
        detail = f'''<details data-review-role-details data-review-detail-for="{point_ref}"><summary>查看实现与验收要点</summary>
          <p data-review-role-detail="frontend"><b>前端实现：</b>保持当前输入与页面上下文，提交中禁用重复操作，成功和失败都给出明确可见反馈。</p>
          <p data-review-role-detail="backend"><b>后端处理：</b>校验权限、当前版本和业务前提，成功写入并记录审计，失败不得产生成功副作用。</p>
          <p data-review-role-detail="qa"><b>测试验收：</b>分别执行成功、权限拒绝和版本冲突，核对页面反馈与持久数据是否同时符合预期。</p>
        </details>'''
        raw = raw.replace(f'<h3>{title}</h3><p>{point["summary"]}</p>', f'<h3>{title}</h3><p>{point["summary"]}</p>{detail}', 1)
    examples = []
    labels = {"positive": "正向", "negative": "反向"}
    for item in document["acceptance_examples"]:
        examples.append(
            f'<article data-review-example="{item["example_ref"]}" data-review-example-kind="{item["kind"]}" '
            f'data-review-context="{item["owner_context_ref"]}" data-review-acceptance-ref="{item["acceptance_ref"]}">'
            f'<b>{labels[item["kind"]]}样例</b><p>前提：{item["precondition"]}</p><p>动作：{item["action"]}</p>'
            f'<p>页面结果：{item["expected_visible_result"]}</p><p>业务结果：{item["expected_domain_result"]}</p></article>'
        )
    trace_refs = sorted(set(re.findall(r"\b[A-Z][A-Z0-9]*-[A-Z0-9-]+\b", json.dumps(document, ensure_ascii=False))))
    trace_terms = document["human_projection_contract"]["technical_terms"]
    boundary_insert = (
        '<div data-review-content="acceptance_examples" data-review-owner-tab="boundary_acceptance">'
        + "".join(examples) + '</div><details data-review-trace><summary>技术追溯</summary><p>'
        + " / ".join(trace_refs) + '</p><p>' + " / ".join(trace_terms) + '</p></details>'
    )
    raw = raw.replace(
        '<div data-review-content="open_items" data-review-owner-tab="boundary_acceptance">开放项已核对：0 项</div>',
        boundary_insert + '<div data-review-content="open_items" data-review-owner-tab="boundary_acceptance">开放项已核对：0 项</div>',
    )
    raw = raw.replace(
        '</body>',
        '<script>function syncReviewDiagramContext(contextRef){document.querySelectorAll("[data-review-flow-context]").forEach(node=>node.setAttribute("data-flow-current",String(node.dataset.reviewFlowContext===contextRef)))}</script></body>',
    )
    return raw


def v549_codes(tmp_path: Path, document: dict | None = None, raw: str | None = None) -> set[str]:
    document = document or manifest_v549("1" * 64)
    raw = raw or review_html_v549(document)
    return {item.code for item in html_gate(tmp_path / "v549-review.html", raw).findings}


def test_v549_lightweight_human_projection_passes(tmp_path: Path) -> None:
    codes = v549_codes(tmp_path)
    assert not {code for code in codes if code.startswith("PROTO-REVIEW-")}


def test_v549_human_projection_adversarial_failures_are_blocked(tmp_path: Path) -> None:
    document = manifest_v549("1" * 64)
    base = review_html_v549(document)
    cases = (
        (base.replace("业务主链", "业务主链 ACT-X-SUBMIT", 1), "PROTO-REVIEW-HUMAN-COPY-LEAK"),
        (base.replace("<details data-review-trace>", "<details data-review-trace open>", 1), "PROTO-REVIEW-TECHNICAL-TRACE"),
        (base.replace('data-review-role-detail="backend"', 'data-review-role-detail="product"', 1), "PROTO-REVIEW-ROLE-DETAIL"),
        (base.replace('data-review-diagram="DIAG-X-CORE"', 'data-review-diagram="DIAG-X-MISSING"', 1), "PROTO-REVIEW-DIAGRAM-VISIBLE"),
        (base.replace('data-flow-current="true"', 'data-flow-current="false"', 1), "PROTO-REVIEW-DIAGRAM-CONTEXT"),
        (base.replace('data-review-example="TEST-X-VIEW-NEG"', 'data-review-example="TEST-X-VIEW-POS"', 1), "PROTO-REVIEW-EXECUTABLE-EXAMPLE"),
    )
    for index, (raw, expected) in enumerate(cases):
        codes = {item.code for item in html_gate(tmp_path / f"v549-bad-{index}.html", raw).findings}
        assert expected in codes


def test_v549_simple_crud_does_not_require_a_diagram(tmp_path: Path) -> None:
    document = manifest_v549("1" * 64)
    document["review_contexts"][0]["secondary_context_refs"] = []
    document["review_contexts"] = document["review_contexts"][:1]
    document["review_points"] = document["review_points"][:1]
    document["semantic_coverage_items"] = document["semantic_coverage_items"][:1]
    document["workspace"]["initial_context_ref"] = "VIEW-X"
    document["diagram_contract"] = {
        "simple_crud_policy": "not_required",
        "decisions": [{
            "context_ref": "VIEW-X", "complexity_drivers": ["simple_crud"],
            "required_types": [], "diagram_refs": [],
            "not_required_reason": "单页局部提交，没有跨页面、角色或系统交接",
        }],
        "diagrams": [],
    }
    document["acceptance_examples"] = []
    raw = review_html_v549(document)
    trace_refs = sorted(set(re.findall(r"\b[A-Z][A-Z0-9]*-[A-Z0-9-]+\b", json.dumps(document, ensure_ascii=False))))
    raw = re.sub(r'(<details data-review-trace><summary>技术追溯</summary><p>)[^<]*(</p>)', rf'\1{" / ".join(trace_refs)}\2', raw, count=1)
    codes = {item.code for item in html_gate(tmp_path / "v549-simple.html", raw).findings}
    assert "PROTO-REVIEW-DIAGRAM-DECISION" not in codes
    assert "PROTO-REVIEW-DIAGRAM-VISIBLE" not in codes
    assert "PROTO-REVIEW-EXECUTABLE-EXAMPLE" not in codes


def review_feedback_manifest(*, after: bool) -> dict:
    document = manifest_v549(("2" if after else "1") * 64)
    document["baseline"]["version"] = "1.1" if after else "1.0"
    document["workspace"]["initial_context_ref"] = "VIEW-X"
    document["review_contexts"] = document["review_contexts"][:1]
    document["review_contexts"][0]["secondary_context_refs"] = []
    document["review_contexts"][0]["surface_types"] = ["form", "preview" if after else "import"]

    before_specs = [
        ("001", "ACT-RULE-QUERY", "查询配置", "按规则名称查询当前机构可见的配置。"),
        ("002", "ACT-RULE-SCOPE", "设置适用范围", "选择本规则适用的企业范围。"),
        ("003", "ACT-RULE-EFFECTIVE", "设置生效时间", "设置规则开始生效的日期。"),
        ("004", "ACT-RULE-VALIDATE", "保存前校验", "保存前检查全部必填项，缺失时留在当前页面并提示。"),
        ("005", "ACT-RULE-IMPORT", "批量导入", "下载模板填写规则后批量导入，并显示每条记录的处理结果。"),
    ]
    after_specs = [
        ("001", "ACT-RULE-QUERY", "查询配置", "可组合规则名称、状态和适用范围查询；查询结果仍受当前机构数据范围限制。"),
        ("002", "ACT-RULE-SCOPE", "设置适用范围", "先选企业类型再选具体企业；没有数据权限的企业不出现在候选列表中。"),
        ("003", "ACT-RULE-EFFECTIVE", "设置生效时间", "按北京时间生效；同一企业的相同规则时间段不得重叠。"),
        ("004", "ACT-RULE-VALIDATE", "保存前校验", "前端提示缺项，服务端再次校验范围、时间冲突和当前版本；失败时不写入。"),
        ("006", "ACT-RULE-PREVIEW", "试运行预览", "只预览当前条件预计命中的企业和异常，不保存配置，也不触发正式检查。"),
    ]
    specs = after_specs if after else before_specs
    points = []
    semantic_items = []
    for suffix, target, title, summary in specs:
        point = review_point(f"RVP-RULE-{suffix}", "VIEW-X", target, title, summary, f"AC-RULE-{suffix}")
        point["implementation_detail"] = {
            "required": True,
            "reason": "该操作影响规则查询、保存或预览结果",
            "roles": ["frontend", "backend", "qa"],
        }
        points.append(point)
        semantic_items.append({
            "coverage_id": f"SCOV-RULE-{suffix}", "subject_ref": target,
            "owner_context_ref": "VIEW-X", "semantic_type": "action", "criticality": "P1",
            "label": title, "source_refs": ["REQ-X", target],
            "ui_grounded": True, "target_ref": target, "coverage_status": "covered",
            "review_point_refs": [f"RVP-RULE-{suffix}"], "human_summary": summary,
            "detail_owner": "function_flow", "unknown_ref": None, "not_applicable_reason": None,
        })
    document["review_points"] = points
    document["semantic_coverage_items"] = semantic_items
    document["review_contexts"][0]["review_point_refs"] = [item["ref"] for item in points]
    document["diagram_contract"] = {
        "simple_crud_policy": "not_required",
        "decisions": [{
            "context_ref": "VIEW-X", "complexity_drivers": ["simple_crud"],
            "required_types": [], "diagram_refs": [],
            "not_required_reason": "本次变更都在同一配置页面完成，不涉及跨页、跨角色或跨系统流转",
        }],
        "diagrams": [],
    }
    document["acceptance_examples"] = []
    return document


def test_v549_review_feedback_modify_delete_add_is_a_versioned_change(tmp_path: Path) -> None:
    before = review_feedback_manifest(after=False)
    after = review_feedback_manifest(after=True)
    before_raw = review_html_v549(before)
    after_raw = review_html_v549(after)

    before_findings = html_gate(tmp_path / "review-before.html", before_raw).findings
    after_findings = html_gate(tmp_path / "review-after.html", after_raw).findings
    before_codes = {item.code for item in before_findings}
    after_codes = {item.code for item in after_findings}
    assert not [item for item in before_findings if item.severity != "INFO"], [
        (item.severity, item.code, item.message) for item in before_findings
    ]
    assert not [item for item in after_findings if item.severity != "INFO"], [
        (item.severity, item.code, item.message) for item in after_findings
    ]
    assert not {code for code in before_codes if code.startswith("PROTO-REVIEW-")}, [
        (item.code, item.message) for item in before_findings
    ]
    assert not {code for code in after_codes if code.startswith("PROTO-REVIEW-")}, [
        (item.code, item.message) for item in after_findings
    ]

    for point_before, point_after in zip(before["review_points"][:4], after["review_points"][:4]):
        assert point_before["ref"] == point_after["ref"]
        assert point_before["summary"] != point_after["summary"]
    assert "RVP-RULE-005" in before["review_contexts"][0]["review_point_refs"]
    assert "RVP-RULE-005" not in after["review_contexts"][0]["review_point_refs"]
    assert "RVP-RULE-006" in after["review_contexts"][0]["review_point_refs"]
    assert 'data-review-ref="RVP-RULE-005"' not in after_raw
    assert 'data-review-point="RVP-RULE-005"' not in after_raw
    assert 'data-review-ref="RVP-RULE-006" data-review-context="VIEW-X" data-review-number="5"' in after_raw
    assert 'data-review-point="RVP-RULE-006" data-review-context="VIEW-X" data-review-number="5"' in after_raw
    assert "review:1.0" in before_raw and "review:1.1" not in before_raw
    assert "review:1.1" in after_raw and "review:1.0" not in after_raw

    missing_new_marker = after_raw.replace(
        '<button data-action="UIACT-REVIEW-SELECT" data-review-ref="RVP-RULE-006"',
        '<button data-action="UIACT-REVIEW-SELECT" data-review-ref="RVP-RULE-REMOVED"',
        1,
    )
    missing_codes = {item.code for item in html_gate(tmp_path / "review-after-missing-marker.html", missing_new_marker).findings}
    assert "PROTO-REVIEW-POINT-COVERAGE" in missing_codes


def test_v549_prd_semantic_escape_hatches_are_blocked() -> None:
    raw = """# 需求

| UNK/REV/DEC ID | 原问题/冲突 | 批次回答或证据 | 影响的 REQ/RULE/AC | 责任人 | 结论/状态 |
|---|---|---|---|---|---|
| DEC-RULE-001 | 是否自动通过 | 模型推断 | REQ-RULE-001 | 产品负责人 | 已确认 |

| AC ID | REQ/行为 | 前置与角色 | 步骤/输入 | 预期可见结果 | 预期领域结果 | 反例 | 证据 |
|---|---|---|---|---|---|---|---|
| AC-RULE-001 | REQ-RULE-001 | 管理员 | 点击保存 | 功能正常 | 处理成功 | 无 | 截图 |

## 附录 A：全局字段字典
| FLD ID | 实体.字段 | 中文名/含义 | 类型/字典 | 必填/默认 | 来源 | 编辑权/数据范围 | 校验 | 敏感级别 |
|---|---|---|---|---|---|---|---|---|
| FLD-ERROR-001 | Record.errorReason | 失败原因 | string | 否 | 页面 | 管理员 | 500字 | 内部 |
"""
    codes = {item.code for item in run_semantic_checks(raw)}
    assert {
        "PRD-CONFIRMED-DECISION-NO-AUTHORITY",
        "PRD-AC-NOT-FALSIFIABLE",
        "PRD-REPRESENTATION-GAP",
    } <= codes


def test_v549_duplicate_unknown_frontmatter_is_blocked(tmp_path: Path) -> None:
    prd = tmp_path / "duplicate-unknown.md"
    prd.write_text("""---
document_language: zh-CN
delivery_level: L1
open_p0_unknown_ids: [UNK-RULE-001]
unknowns:
  - id: UNK-RULE-001
    priority: P0
    status: open
    blocks_stage: baseline
    owner: 产品负责人
    affected_refs: [REQ-RULE-001]
  - id: UNK-RULE-001
    priority: P1
    status: open
    blocks_stage: review
    owner: 测试负责人
    affected_refs: [REQ-RULE-001]
activated_facets: []
---
# 需求卡

REQ-RULE-001 / UNK-RULE-001
""", encoding="utf-8")
    gate = Gate()
    gate.check_prd(prd, "L1")
    assert "PRD-DUPLICATE-UNKNOWN-DEFINITION" in {item.code for item in gate.findings}
