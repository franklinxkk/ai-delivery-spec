"""Observable 5.5 behavior: proportional routing, authority, scoped claims and impact."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from requirement_contract import route, check_spec
from triage_requirement import recommend
from analyze_change_impact import analyze
from change_package_contract import ChangeContractError

BODY = "# 小改\n## 范围\n只调整当前保存提示。\n## 行为\n保存成功显示完成，失败保留输入。\n## 验收\n成功显示完成；失败不会丢失输入。\n"


def codes(doc=None, body=BODY, **kwargs):
    return {f["code"] for f in check_spec(doc or {}, body, **kwargs)[0]}


@pytest.mark.parametrize("mode", ["direct", "card", "prd"])
def test_risk_does_not_override_explicit_artifact_or_priority(mode):
    result = route({"artifact_mode": mode, "priority": "P3", "money": True, "tenant_isolation": True})
    assert result["artifact_mode"] == mode and result["priority"] == "P3"
    assert {"irreversible", "permission"} <= set(result["risk_facets"])
    assert {"permission_boundary", "recovery"} <= set(result["semantic_review_categories"])


def test_explicit_governed_survives_direct():
    assert route({"artifact_mode": "direct", "governed_truth_requested": True})["governed"] is True
    assert route({"artifact_mode": "direct", "delivery_shape": "governed_truth"})["governed"] is True
    assert route({"artifact_mode": "direct", "governed": "false"})["errors"]


def test_conflicting_shapes_fail_but_legacy_level_never_invents_risk():
    assert route({"artifact_mode": "direct", "delivery_shape": "unified_prd"})["errors"]
    assert not route({"delivery_level": "L4"})["risk_facets"]
    assert route({"artifact_mode": "direct", "delivery_level": "L4"})["artifact_mode"] == "direct"


@pytest.mark.parametrize("raw", [None, "metric", {}, [2]])
def test_bad_risk_declaration_is_controlled(raw):
    assert route({"risk_facets": raw})["errors"]


def test_plain_small_change_does_not_require_metadata_or_long_sections():
    findings, routed = check_spec({}, BODY)
    assert not [f for f in findings if f["severity"] in {"BLOCK", "GAP"}]
    assert routed["not_proven"]
    renamed = BODY.replace("## 范围", "<!-- ADS:scope -->\n## 此次边界").replace("## 行为", "<!-- ADS:behavior -->\n## 用户体验").replace("## 验收", "<!-- ADS:acceptance -->\n## 判断标准")
    assert not [f for f in check_spec({}, renamed)[0] if f["severity"] in {"BLOCK", "GAP"}]


def test_free_prose_gap_is_locator_not_a_false_completeness_failure():
    findings, _ = check_spec({}, "保存成功显示完成；失败保留输入。本次只改提示。")
    assert not any(f["severity"] == "BLOCK" for f in findings)
    assert all("not proved incomplete" in f["message"] for f in findings)


def test_empty_sections_do_not_pass_as_content():
    assert "SPEC-EMPTY-SECTION" in codes(body="## 范围\n## 行为\n## 验收\n")
    assert "SPEC-EMPTY" in codes(body="")


def test_content_under_subheadings_counts_for_the_parent_section():
    nested = BODY.replace("## 范围\n", "## 范围\n### 当前边界\n").replace("## 验收\n", "## 验收\n### 验收用例\n")
    assert "SPEC-EMPTY-SECTION" not in codes(body=nested)


def test_unknown_only_blocks_dependent_scope_at_named_stage():
    doc = {"unknowns": [{"id": "UNK-A", "status": "open", "affected_refs": ["REQ-A"], "blocks_stage": "baseline"}]}
    before = check_spec(doc, BODY, stage="specify", scope=("REQ-A",))[0]
    assert any(f["severity"] == "GAP" for f in before) and not any(f["severity"] == "BLOCK" for f in before)
    assert "SPEC-OPEN-DECISION" in codes(doc, stage="baseline", scope=("REQ-A",))
    assert "SPEC-OPEN-DECISION" not in codes(doc, stage="baseline", scope=("REQ-B",))
    doc["unknowns"][0].pop("affected_refs")
    assert "SPEC-OPEN-DECISION" in codes(doc, stage="baseline", scope=("REQ-B",))


def test_unknown_cannot_close_without_decision_or_repeat_with_conflicting_priority():
    unknown = {"id": "UNK-A", "status": "closed"}
    assert "SPEC-UNKNOWN-CLOSURE" in codes({"unknowns": [unknown]})
    assert "PRD-DUPLICATE-UNKNOWN-DEFINITION" in codes({"unknowns": [unknown, dict(unknown, priority="P1")]})
    unknown["resolution_ref"] = "DEC-A"
    assert "SPEC-UNKNOWN-CLOSURE" not in codes({"unknowns": [unknown]})


def test_recommendations_never_mutate_lifecycle_or_user_priority():
    doc = {"title": "保留现有流程", "priority": "P1", "blocked_dependency": True, "status": "draft"}
    before = deepcopy(doc)
    result = recommend(doc)
    assert doc == before and result["lifecycle_mutated"] is False
    assert result["recommendation"] == "defer" and result["decision_status"] == "proposed"
    assert result["priority"] == "P1"


def test_disposition_visible_without_fabricating_approval():
    disposition = {"outcome": "defer", "status": "proposed", "reason": "需要验证", "scope_refs": ["REQ-A"]}
    assert "SPEC-DISPOSITION-NOT-AUTHORIZED" in codes({"status": "deferred", "disposition": disposition})
    assert "SPEC-DISPOSITION-NOT-AUTHORIZED" not in codes({"status": "draft", "disposition": disposition})
    disposition["status"] = "confirmed"
    assert "SPEC-DISPOSITION-AUTHORITY" in codes({"disposition": disposition})
    disposition.update(actor="授权用户", source_refs=["SRC-CONVERSATION"])
    assert not codes({"status": "deferred", "disposition": disposition})


def test_existing_authorized_decision_is_not_reopened():
    doc = {"decisions": [{"id": "DEC-A", "status": "confirmed", "actor": "用户", "source_refs": ["SRC-USER"]}]}
    assert not codes(doc)
    del doc["decisions"][0]["actor"]
    assert "SPEC-DECISION-AUTHORITY" in codes(doc)


def test_source_conflict_closure_requires_a_resolution():
    doc = {"source_conflicts": [{"id": "CON-A", "status": "resolved"}]}
    assert "SPEC-CONFLICT-CLOSURE" in codes(doc)
    doc["source_conflicts"][0]["resolution_ref"] = "DEC-A"
    assert "SPEC-CONFLICT-CLOSURE" not in codes(doc)


def review(scope=None, **updates):
    result = {"category": "metric_definition", "result": "pass", "scope_refs": scope or ["REQ-A"],
              "source_refs": ["SRC-A"], "reviewer": "independent reviewer", "evidence_ref": "review.md",
              "baseline_version": "1.0"}
    return dict(result, **updates)


def test_one_review_cannot_launder_other_scopes_or_versions():
    doc = {"risk_facets": ["metric"], "baseline_version": "1.0", "requirement_ids": ["REQ-A", "REQ-B"],
           "semantic_reviews": [review()]}
    findings, routing = check_spec(doc, BODY)
    assert any(f["ref"] == "metric_definition" and "REQ-B" in f["message"] for f in findings)
    assert routing["semantic_coverage"]["declared_covered"] == {"metric_definition": ["REQ-A"]}
    doc["semantic_reviews"] = [review(baseline_version="0.9")]
    assert "SPEC-REVIEW-BASELINE" in codes(doc)
    doc["semantic_reviews"] = [review(evidence_ref="")]
    assert "SPEC-REVIEW-EVIDENCE" in codes(doc)


def test_exclusion_is_scoped_and_does_not_prove_execution():
    doc = {"risk_facets": ["metric"], "baseline_version": "1.0", "requirement_ids": ["REQ-A"],
           "semantic_reviews": [review(result="not_applicable", reason="只调整标签，不改口径")]}
    findings, routing = check_spec(doc, BODY)
    assert not any(f["ref"] == "metric_definition" for f in findings)
    assert "not independently authenticated" in routing["semantic_coverage"]["proof"]
    assert "implementation" in routing["not_proven"]
    del doc["semantic_reviews"][0]["reason"]
    assert "SPEC-REVIEW-EXCLUSION" in codes(doc)


def graph_fixture():
    return {"items": [{"id": "REQ-A", "action_refs": ["ACT-A"]}, {"id": "ACT-A", "test_ref": "AC-A"},
                      {"id": "AC-A"}, {"id": "REQ-UNRELATED"}]}


def change():
    return {"change_id": "CHG-A", "request": {"seed_refs": ["REQ-A"]}}


def test_impact_has_grounded_paths_and_never_approves_candidates():
    result = analyze(graph_fixture(), change())
    items = {x["ref"]: x for x in result["affected"]}
    assert set(items) == {"REQ-A", "ACT-A", "AC-A"}
    assert items["AC-A"]["dependency_path"] == ["REQ-A", "ACT-A", "AC-A"]
    assert len(items["AC-A"]["edge_sources"]) == 2
    assert all(x["status"] == "candidate" for x in items.values())
    assert result["authority"] == "candidate_only" and not result["coverage"]["depth_truncated"]


def test_impact_discloses_depth_and_unresolved_edges():
    truth = graph_fixture()
    truth["items"][1]["external_ref"] = "EXT-MISSING"
    result = analyze(truth, change(), max_depth=1)
    assert result["coverage"]["depth_truncated"] and result["coverage"]["frontier_refs"] == ["ACT-A"]
    assert result["coverage"]["unresolved_refs"][0]["ref"] == "EXT-MISSING"
    assert analyze(truth, {"request": {"seed_refs": ["REQ-MISSING"]}})["missing_seed_refs"] == ["REQ-MISSING"]


def test_impact_handles_index_only_cycles_and_invalid_edges():
    result = analyze({"forward_index": {"REQ-A": ["ACT-A"], "ACT-A": ["REQ-A"]}}, change())
    assert len(result["affected"]) == 2
    for depth in (-1, 101):
        with pytest.raises(ChangeContractError):
            analyze({}, change(), depth)
    with pytest.raises(ChangeContractError):
        analyze({"edges": ["not-an-edge"]}, change())
    with pytest.raises(ChangeContractError):
        analyze({"items": [{"id": "REQ-A", "child_refs": [{}]}]}, change())


def run_cli(*args):
    return subprocess.run([sys.executable, str(ROOT / "scripts/ai_delivery_spec_cli.py"), *args],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_public_gate_and_triage_share_route(tmp_path):
    metadata = {"title": "权限提示", "artifact_mode": "direct", "priority": "P2", "tenant_isolation": True}
    intake, prd = tmp_path / "in.yaml", tmp_path / "prd.md"
    intake.write_text(yaml.safe_dump(metadata, allow_unicode=True), encoding="utf-8")
    prd.write_text("---\n" + yaml.safe_dump(metadata, allow_unicode=True) + "---\n" + BODY, encoding="utf-8")
    triage = json.loads(run_cli("triage", "--input", str(intake), "--format", "json").stdout)
    gate = json.loads(run_cli("gate", "--profile", "prd", "--prd", str(prd), "--format", "json").stdout)
    routing = gate["metrics"]["routing"]
    for key in ("artifact_mode", "risk_facets", "priority", "semantic_review_categories", "governed"):
        assert triage[key] == routing[key]
    assert gate["not_proven"]


@pytest.mark.parametrize("metadata", ["false", "0", "[]", "x: [", "artifact_mode: [prd]"])
def test_bad_frontmatter_fails_without_traceback(tmp_path, metadata):
    path = tmp_path / "bad.md"
    path.write_text("---\n" + metadata + "\n---\n" + BODY, encoding="utf-8")
    result = run_cli("gate", "--profile", "prd", "--prd", str(path), "--format", "json")
    assert result.returncode != 0 and "Traceback" not in result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "BLOCKED"

def test_short_precise_results_and_adopted_suggestions_are_valid():
    from validators.validate_prd_semantics import run_semantic_checks
    raw = """# Decisions
| DEC ID | Source | Status |
|---|---|---|
| DEC-A | AI suggestion, not authorized | unconfirmed |
| DEC-B | 用户在工单中批准采用模型建议；SRC-USER-B | 已确认 |
# Acceptance
| AC ID | 步骤 | 可见结果 | 领域结果 | 反例 | 证据 |
|---|---|---|---|---|---|
| AC-A | 点击保存 | 显示完成 | 无写入 | 保存失败不清空输入 | 未运行 |
"""
    found = {f.code for f in run_semantic_checks(raw)}
    assert "PRD-CONFIRMED-DECISION-NO-AUTHORITY" not in found
    assert "PRD-AC-NOT-FALSIFIABLE" not in found
    bad = raw.replace("unconfirmed", "confirmed").replace("用户在工单中批准采用模型建议；SRC-USER-B", "模型建议")
    assert "PRD-CONFIRMED-DECISION-NO-AUTHORITY" in {f.code for f in run_semantic_checks(bad)}


def test_scoped_body_review_preserves_local_failures_and_excludes_other_drafts(tmp_path):
    path = tmp_path / "scoped.md"
    raw = BODY + """
# REQ-SCORE
| AC ID | 步骤 | 可见结果 | 领域结果 | 反例 | 证据 |
|---|---|---|---|---|---|
| AC-SCORE | 保存 | 功能正常 | 处理成功 | 无 | 未运行 |
"""
    path.write_text(raw, encoding="utf-8")
    local = run_cli("gate", "--profile", "prd", "--prd", str(path), "--scope-ref", "REQ-LABEL", "--format", "json")
    assert local.returncode == 0
    assert json.loads(local.stdout)["metrics"]["text_scope"]["excluded_findings"] > 0
    dependent = run_cli("gate", "--profile", "prd", "--prd", str(path), "--scope-ref", "REQ-SCORE", "--format", "json")
    assert dependent.returncode == 2
    global_check = run_cli("gate", "--profile", "prd", "--prd", str(path), "--format", "json")
    assert global_check.returncode == 2
    path.write_text(raw.replace("# REQ-SCORE", "# 暂未归属"), encoding="utf-8")
    unlocated = json.loads(run_cli("gate", "--profile", "prd", "--prd", str(path), "--scope-ref", "REQ-LABEL", "--format", "json").stdout)
    assert any(f["code"] == "SPEC-TEXT-SCOPE-NOT-PROVEN" for f in unlocated["findings"])


def test_inventory_is_a_supported_early_stage():
    assert not codes(stage="inventory")


def test_impact_reports_both_actual_and_requested_baselines():
    truth = dict(graph_fixture(), baseline_version="v2")
    request = dict(change(), baseline_version="v1")
    result = analyze(truth, request)
    assert result["input_baselines"] == {"truth": "v2", "change": "v1", "match": False}
    assert analyze(graph_fixture(), change())["input_baselines"]["match"] is None


def test_duplicate_metadata_keys_cannot_hide_a_declaration(tmp_path):
    path = tmp_path / "duplicate.md"
    path.write_text("---\nartifact_mode: prd\nartifact_mode: direct\n---\n" + BODY, encoding="utf-8")
    result = run_cli("gate", "--profile", "prd", "--prd", str(path), "--format", "json")
    assert result.returncode == 2 and "PRD-FRONTMATTER" in result.stdout
