"""Release regressions: current-cycle evidence, proportional PRD checks and templates."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/validators")]
from requirement_contract import check_spec, language_drift
from stage_contract import load_artifact, validate_decision_sidecar

BODY = "# 保存提示\n## 范围\n本次只调整保存提示。\n## 行为\n保存成功显示完成，失败保留输入。\n## 验收\n成功显示完成；失败不会丢失输入。\n"


def command(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def route(tmp_path, docs, target="baseline"):
    args = [ROOT / "scripts/stage_contract.py", "route", "--target", target, "--format", "json"]
    for number, document in enumerate(docs):
        path = tmp_path / f"artifact-{number}.yaml"
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
        args.extend(("--artifact", path))
    result = command(*args)
    assert result.returncode in (0, 2), result.stderr
    return json.loads(result.stdout)


def artifact(kind, version="", **values):
    return dict(artifact=kind, **({"baseline_version": version} if version else {}), **values)


def test_old_acceptance_does_not_cover_new_change(tmp_path):
    data = route(tmp_path, [artifact("acceptance_run", "1.0", run_id="ARUN-OLD"),
                           artifact("change_request", "2.0-draft", change_id="CHG-NEW")])
    assert data["status"] == "BLOCKED"
    assert data["current_artifact_stage"] == "change"
    assert data["path"] == ["change", "baseline"]
    assert {f["code"] for f in data["findings"]} >= {"ROUTE-CYCLE-AMBIGUOUS", "ROUTE-PREREQUISITE"}


def test_current_change_accepts_its_review_not_source_baseline_review(tmp_path):
    base = [artifact("change_request", "1.0", target_version="2.0", change_id="CHG-NEW"),
            artifact("acceptance_run", "1.0", run_id="ARUN-OLD")]
    stale = route(tmp_path, base + [artifact("unified_prd", "1.0"), artifact("review_record", "1.0")])
    assert stale["status"] == "BLOCKED"
    current = route(tmp_path, base + [artifact("unified_prd", "2.0"), artifact("review_record", "2.0")])
    assert current["status"] == "PASS" and current["path"] == ["change", "baseline"]
    assert current["artifacts"][1]["selected_cycle"] is False


def test_rebased_change_routes_to_acceptance_from_new_baseline(tmp_path):
    data = route(tmp_path, [artifact("change_request", "1.0", target_version="2.0", change_id="CHG-NEW"),
                           artifact("acceptance_run", "1.0"), artifact("unified_prd", "2.0", stage="baseline")], "acceptance")
    assert data["status"] == "PASS" and data["path"] == ["baseline", "acceptance"]


def test_unchanged_single_baseline_remains_valid(tmp_path):
    data = route(tmp_path, [artifact("unified_prd", "1.0", stage="baseline")], "acceptance")
    assert data["status"] == "PASS" and data["current_artifact_stage"] == "baseline"


@pytest.mark.parametrize("key,first,second", [("project_id", "A", "B"), ("requirement_refs", ["REQ-A"], ["REQ-B"])])
def test_unrelated_scopes_do_not_supply_each_others_prerequisites(tmp_path, key, first, second):
    data = route(tmp_path, [artifact("unified_prd", "1", **{key: first}), artifact("review_record", "1", **{key: second})])
    assert data["status"] == "BLOCKED" and data["current_artifact_stage"] is None
    issue = next(f for f in data["findings"] if f["code"] == "ROUTE-SCOPE-AMBIGUOUS")
    assert "不要求" in issue["how_to_fix"]


def test_same_scope_multiple_baselines_need_current_cycle_selection(tmp_path):
    data = route(tmp_path, [artifact("acceptance_run", "1", requirement_refs=["REQ-A"]),
                           artifact("unified_prd", "2", requirement_refs=["REQ-A"])])
    assert data["status"] == "BLOCKED" and data["current_artifact_stage"] is None


def test_supporting_record_does_not_establish_progress(tmp_path):
    data = route(tmp_path, [dict(artifact="decision_record", artifact_role="supporting",
                                applicable_stages=["clarify", "review", "change"])])
    assert data["current_artifact_stage"] is None and data["status"] == "BLOCKED"


@pytest.mark.parametrize("template", sorted((ROOT / "references/templates").glob("*template.*")), ids=lambda p: p.name)
def test_templates_declare_identity_and_applicability_without_fake_progress(template):
    item = load_artifact(template)
    assert item.confidence == "declared" and item.kind != "unknown"
    assert item.metadata["artifact_role"] in {"main", "supporting"}
    assert item.metadata["applicable_stages"] and item.metadata["applies_when"]
    if item.metadata["artifact_role"] == "supporting":
        assert item.stage == "supporting"
    else:
        assert item.stage in item.metadata["applicable_stages"]


@pytest.mark.parametrize("template,schema", [
    ("acceptance-run", "acceptance-run"), ("agent-handoff-manifest", "agent-handoff"),
    ("assumption-register", "assumption-register"), ("change-request", "change-package"),
    ("discovery-contract", "discovery-contract"), ("product-truth-core-fragment", "product-truth-fragment"),
    ("product-truth-module-fragment", "product-truth-fragment"), ("product-truth-index", "product-truth-index"),
    ("product-truth", "product-truth"), ("requirement-intake", "requirement-intake"),
    ("requirement-register", "requirement-register"), ("review-record", "review-record"), ("stage0-inventory", "stage0-inventory")])
def test_template_metadata_is_accepted_by_its_real_schema(template, schema):
    document = yaml.safe_load((ROOT / f"references/templates/{template}-template.yaml").read_text(encoding="utf-8"))
    contract = json.loads((ROOT / f"schemas/{schema}.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(contract).iter_errors(document))
    metadata_fields = {"artifact", "artifact_role", "stage", "applicable_stages", "applies_when"}
    assert not [e.message for e in errors if (e.path and e.path[0] in metadata_fields) or
                (e.validator == "additionalProperties" and not e.path) or
                (e.validator == "required" and "'stage'" in e.message)]


def test_decision_template_is_a_usable_concise_sidecar(tmp_path):
    path = tmp_path / "decision.md"
    path.write_text("---\nartifact: decision_record\nartifact_role: supporting\n---\n# 决定\n"
                    "| ID | 建议/决定及理由 | 证据与适用范围 | 状态 | 有权决定者与授权来源 | 复议条件 |\n"
                    "| DEC-A | 采用原单修改，未选新建以保留历史 | REQ-A | confirmed | 产品负责人，SRC-A | 业务对象改变 |\n", encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_text("---\nartifact: requirement_brief\n---\n采用 DEC-A。", encoding="utf-8")
    assert not [f for f in validate_decision_sidecar(load_artifact(path), load_artifact(brief)) if f["severity"] == "BLOCK"]


@pytest.mark.parametrize("body", ["# PRD\n", "# PRD\n## 范围\n## 行为\n## 验收\n<!-- 空 -->\n"])
def test_title_shell_cannot_be_baselined(body):
    findings, _ = check_spec({}, body, stage="baseline")
    assert any(f["code"] == "SPEC-EMPTY" and f["severity"] == "BLOCK" for f in findings)


def test_short_human_prose_does_not_require_a_template():
    findings, _ = check_spec({}, "保存成功显示完成；失败保留输入。本次只改提示。", stage="baseline")
    assert not any(f["severity"] == "BLOCK" for f in findings)


ENGLISH = "The operator saves the record after checking its name. The system shows the saved result on this page and retains all entered values when the request fails."
CHINESE = "用户填写名称后保存当前记录。系统保存成功后在当前页面显示记录，保存失败时保留本次全部输入并显示失败原因，用户修正输入后可以再次提交。"


@pytest.mark.parametrize("language,body", [("zh-CN", ENGLISH), ("en-US", CHINESE)])
def test_obvious_declared_language_drift_is_advisory(language, body):
    findings, _ = check_spec({"document_language": language}, body)
    assert any(f["code"] == "PRD-LANGUAGE-DRIFT" and f["severity"] == "GAP" for f in findings)
    assert not any(f["code"] == "PRD-LANGUAGE-DRIFT" and f["severity"] == "BLOCK" for f in findings)


def test_language_check_excludes_deliberate_bilingual_code_ids_and_quotes():
    assert language_drift({"document_language": "zh-CN", "bilingual": True}, ENGLISH) is None
    assert language_drift({"document_language": "zh-CN", "document_languages": ["zh-CN", "en-US"]}, ENGLISH) is None
    assert language_drift({"document_language": "zh-CN"}, BODY + "\n```text\n" + ENGLISH + "\n```\n> " + ENGLISH + "\n`REQ-KEEP-ID` `Microsoft Azure`\n") is None
    assert language_drift({}, ENGLISH) is None


def test_global_signoff_does_not_close_open_unknown():
    doc = {"status": "approved", "baseline_version": "1.0", "signoff": "approved",
           "unknowns": [{"id": "UNK-A", "status": "open", "blocks_stage": "review", "affected_refs": ["REQ-A"]}]}
    findings, _ = check_spec(doc, BODY, stage="baseline")
    issue = next(f for f in findings if f["code"] == "SPEC-OPEN-DECISION")
    assert issue["severity"] == "BLOCK" and "签认" in issue["message"] and "真实决定" in issue["message"]
    assert doc["unknowns"][0]["status"] == "open"


def test_legacy_entry_defaults_to_current_contract_and_requires_opt_in(tmp_path):
    path = tmp_path / "small.md"
    path.write_text(BODY, encoding="utf-8")
    entry = ROOT / "scripts/validators/validate_coding_agent_contract.py"
    modern = command(entry, path, "--level", "L2")
    assert modern.returncode == 0, modern.stdout + modern.stderr
    assert "scoped PRD static checks" in modern.stdout
    assert "does not prove business correctness" in modern.stdout
    legacy = command(entry, path, "--legacy")
    assert legacy.returncode == 1 and "need at least 14" in legacy.stdout
    compatible = command(entry, ROOT / "maintainer/tests/fixtures/coding-l2.md", "--legacy")
    assert compatible.returncode == 0, compatible.stdout + compatible.stderr


def test_stage_format_failure_describes_this_check_not_permanent_loss(tmp_path):
    path = tmp_path / "brief.md"
    path.write_text("# 业务问题\n用户找不到已保存记录。", encoding="utf-8")
    result = command(ROOT / "scripts/stage_contract.py", "gate", "--profile", "frame", "--artifact", path, "--format", "json")
    data = json.loads(result.stdout)
    issue = next(f for f in data["findings"] if f["code"] == "STAGE-NO-FRONTMATTER")
    assert "本阶段结构检查" in issue["message"] and "无需" in issue["how_to_fix"]
    assert "永久" not in json.dumps(issue, ensure_ascii=False) and "5.4" not in json.dumps(issue)
