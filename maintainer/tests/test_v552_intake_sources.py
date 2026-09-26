"""Sanitized intake-text and compatibility routing regressions."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from requirement_contract import intake_text, route
from triage_requirement import recommend, render_markdown


@pytest.mark.parametrize("slot", ["brief", "outcome", "value_evidence"])
@pytest.mark.parametrize("bad,good,kind", [
    ("审批通过后可发布。", "审批通过后可发布，由运营手动发布。", "publication"),
    ("Approved requests can be published.", "Approved requests can be published; operators publish manually.", "publication"),
    ("退回后重新提交。", "退回后修改原单重新提交，编号和历史保留。", "return-object"),
    ("Retry failed payments.", "Retry failed payments with the same idempotency key and query the existing result.", "retry-result"),
])
def test_known_intake_slots_read_prose_and_structured_text(slot, bad, good, kind):
    for wrap in (lambda x: x, lambda x: [x], lambda x: {"summary": x},
                 lambda x: [{"content": {"text": x}, "source_refs": ["SRC-FACT"]}]):
        doc = {"title": "Requested change", slot: wrap(bad)}
        before = deepcopy(doc)
        result = recommend(doc)
        assert result["recommendation"] == "clarify"
        assert kind in {f["kind"] for f in result["content_review"]["findings"]}
        assert result["next_questions"] and not result["lifecycle_mutated"]
        assert doc == before
        doc[slot] = wrap(good)
        clarified = recommend(doc)
        assert clarified["recommendation"] == "accept"
        assert kind not in {f["kind"] for f in clarified["content_review"]["findings"]}


@pytest.mark.parametrize("slot", ["brief", "outcome", "value_evidence"])
def test_lexical_triage_uses_the_same_known_text_slots(slot):
    assert recommend({"title": "列表改动", slot: [{"text": "及时处理"}]})["recommendation"] == "clarify"
    assert recommend({"title": "列表改动", slot: [{"text": "保存成功后显示完成，失败保留输入。"}]})["recommendation"] == "accept"


def test_sources_ids_unknown_mapping_keys_and_metadata_are_not_product_prose():
    risky = "审批通过后可发布。AI 自动修改账单并保存。"
    doc = {"title": "Display change", "metadata": {"description": risky}, "source_refs": [risky],
           "brief": {"source_refs": [risky], "source_id": risky, "id": risky, "metadata": {"text": risky},
                     "unrecognized_wrapper": {"text": risky}, "text": "Save succeeded shows Done."},
           "value_evidence": ["SRC-REFERENCE", {"evidence_refs": [risky], "text": "Existing users confirmed the label."}]}
    text = intake_text(doc)
    assert risky not in text and "SRC-REFERENCE" not in text
    result = recommend(doc)
    assert result["recommendation"] == "accept"
    assert not result["content_risk_candidates"]
    assert not result["content_review"]["findings"]
    doc["brief"]["text"] = risky
    assert recommend(doc)["recommendation"] == "clarify"


def test_text_extractor_can_read_a_recursive_yaml_shape_without_scanning_metadata():
    brief = {"text": "Approved requests can be published."}
    brief["items"] = [brief]
    doc = {"title": "Publishing change", "brief": brief}
    assert intake_text(doc).count("Approved requests can be published.") == 1
    assert recommend(doc)["recommendation"] == "clarify"


@pytest.mark.parametrize("title", ["这系统太烂了，不想说了", "This system is terrible", "Build a system", "做个系统"])
def test_concrete_brief_answers_generic_or_complaint_title(title):
    assert recommend({"title": title})["recommendation"] == "clarify"
    result = recommend({"title": title, "brief": {"text": "Please add sorting by creation date."}})
    assert result["recommendation"] == "accept"
    # A metadata-only object cannot masquerade as a supplied task.
    assert recommend({"title": title, "brief": {"source_refs": ["SRC-USER"]}})["recommendation"] == "clarify"


@pytest.mark.parametrize("language", ["zh-CN", "en"])
@pytest.mark.parametrize("mode", ["direct", "card", "prd"])
def test_large_complexity_is_explained_without_overriding_deliverable_or_priority(language, mode):
    doc = {"title": "Display change", "document_language": language, "artifact_mode": mode,
           "priority": "P3", "complexity": {"band": "L", "dimensions": ["clients"]}}
    before = deepcopy(doc)
    result = recommend(doc)
    assert result["artifact_mode"] == mode and result["priority"] == "P3"
    assert result["complexity_band"] == "L" and any("complexity band L" in note for note in result["notes"])
    assert result["complexity_advice"] in render_markdown(result)
    assert ("复杂度 L" if language == "zh-CN" else "complexity L") in result["complexity_advice"]
    assert not result["risk_facets"] and not result["lifecycle_mutated"]
    assert doc == before


def test_compatibility_is_not_migration_but_explicit_migration_still_applies():
    compatible = route({"version_compatibility": True})
    assert compatible["declared_risk_facets"] == ["compatibility"]
    assert compatible["semantic_review_categories"] == ["change_propagation"]
    assert "migration" not in compatible["risk_facets"]
    assert route({"version_compatibility": False})["risk_facets"] == []
    assert route({"migration": True})["risk_facets"] == ["migration"]
    assert route({"version_compatibility": True, "migration": True})["risk_facets"] == ["compatibility", "migration"]
    assert route({"version_compatibility": True, "risk_facets": ["migration"]})["risk_facets"] == ["compatibility", "migration"]


def test_declared_risk_and_body_risk_are_both_retained():
    doc = {"title": "Change", "version_compatibility": True, "approval": True,
           "brief": {"text": "AI automatically updates invoices and saves them."}}
    intake = route(doc)
    assert {"compatibility", "state", "irreversible_ai_write"} <= set(intake["risk_facets"])
    explicit_body = route(doc, body="AI 自动修改账单并保存。")
    assert {"compatibility", "state", "irreversible_ai_write"} <= set(explicit_body["risk_facets"])
    assert "migration" not in intake["risk_facets"]


def test_unknown_complexity_values_do_not_invent_a_band_or_raise_type_error():
    for value in (None, "L", {}, {"band": ["L"]}, {"band": "unknown"}):
        result = recommend({"title": "Display change", "complexity": value})
        assert result["complexity_band"] is None
        assert "complexity_advice" not in result
