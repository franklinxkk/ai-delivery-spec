"""Paired intake regressions; these do not prove general language completeness."""
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from triage_requirement import recommend
from query_domain import search_terms, term_matches


@pytest.mark.parametrize("title,advice,facet", [
    ("这个系统太难用了", "clarify", None),
    ("This system is too hard to use", "clarify", None),
    ("This system is difficult to use; please add date sorting", "accept", None),
    ("现有列表增加按创建日期升序排序，默认仍降序，权限不变", "accept", None),
    ("Add ascending creation-date sorting; keep descending as default and preserve permissions", "accept", None),
    ("排序默认", "clarify", None),
    ("排序默认仍按相关规则", "clarify", None),
    ("默认仍自动给客户发送邮件", "clarify", "irreversible_ai_write"),
    ("置信度超过0.8时自动给客户发送邮件", "clarify", "irreversible_ai_write"),
    ("Automatically send emails to customers when confidence exceeds 0.8", "clarify", "irreversible_ai_write"),
    ("When confidence exceeds 0.8, automatically send emails to customers", "clarify", "irreversible_ai_write"),
    ("离职率按离职人数除以员工人数计算", "clarify", "metric"),
    ("Calculate turnover as the number of departures divided by employee count", "clarify", "metric"),
    ("Show employee turnover", "clarify", "metric"),
])
def test_equivalent_intake_decisions(title, advice, facet):
    result = recommend({"title": title})
    assert result["recommendation"] == advice
    assert result["lifecycle_mutated"] is False
    if facet:
        assert facet in result["risk_facets"]


@pytest.mark.parametrize("title", [
    "Do not automatically send emails even when confidence exceeds 0.8",
    "AI only produces drafts; never automatically send emails to customers",
    "Automatically send a receipt after a confirmed payment",
    "Automatically send a receipt after payment. Show confidence separately in the AI report",
    "Show inventory turnover",
])
def test_new_cues_do_not_invent_ai_writes_or_employee_metrics(title):
    result = recommend({"title": title})
    assert "irreversible_ai_write" not in result["risk_facets"]
    assert "metric" not in result["risk_facets"]


@pytest.mark.parametrize("domain,zh,en", [
    ("oa", "报销", "expense"),
    ("ai-native", "人工确认", "human confirmation"),
    ("ai-native", "工具授权", "tool authorization"),
    ("media-knowledge", "视频", "video"),
    ("media-knowledge", "转写", "transcription"),
    ("media-knowledge", "时间码", "timecode"),
    ("oa", "分母", "denominator"),
    ("data-product", "血缘", "lineage"),
])
def test_known_concepts_retrieve_same_existing_passages(domain, zh, en):
    catalog = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
    record = next(item for item in catalog["domains"] if item["domain_id"] == domain)
    lines = (ROOT / record["knowledge_file"]).read_text(encoding="utf-8").splitlines()
    def hits(query):
        terms = search_terms(query, catalog["search_aliases"])
        return {i for i, line in enumerate(lines) if any(term_matches(term, line) for term in terms)}
    assert hits(zh) and hits(zh) == hits(en)


def test_glossary_keeps_unknown_terms_literal():
    catalog = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
    assert search_terms("expensive", catalog["search_aliases"]) == ["expensive"]
