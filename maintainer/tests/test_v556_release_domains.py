"""Bounded retrieval evidence, not proof of sector expertise or legal applicability."""
from functools import lru_cache
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from query_domain import rank_hits, term_matches


@lru_cache(maxsize=None)
def query(*args):
    run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/query_domain.py"), *args],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert run.returncode == 0, run.stderr + run.stdout
    return yaml.safe_load(run.stdout)


@pytest.mark.parametrize("domain,zh,en,body", [
    ("traffic", "疲劳驾驶", "fatigue driving", "Dynamic monitoring"),
    ("traffic", "超速", "speeding", "Dynamic monitoring"),
    ("ai-native", "记忆", "memory", "| conversation memory |"),
    ("ai-native", "工具调用", "tool calling", "idempotent tool call"),
    ("crm", "客户去重", "customer deduplication", "dedup caliber"),
    ("media-knowledge", "视频检索", "video retrieval", "| moment retrieval |"),
])
def test_bilingual_terms_reach_business_body_not_just_added_aliases(domain, zh, en, body):
    left = query("--domain", domain, "--search", zh, "--limit", "50")["hits"]
    right = query("--domain", domain, "--search", en, "--limit", "50")["hits"]
    assert any(body in hit["excerpt"] for hit in left)
    assert any(body in hit["excerpt"] for hit in right)
    assert {h["line"] for h in left} == {h["line"] for h in right}


@pytest.mark.parametrize("text", ["客户去重", "customer deduplication",
                                 "客户去重时如何保留原负责人？", "How should customer deduplication preserve ownership?"])
def test_specific_customer_phrase_does_not_expand_into_unrelated_customer_mentions(text):
    result = query("--search", text)
    assert result["hits"]
    assert all(h["domain_id"] == "crm" for h in result["hits"])
    assert "客户" not in result["matched_concepts"]


def test_section_diversification_cannot_promote_a_weaker_match():
    def hit(number, coverage, section):
        return {"domain_id": "test", "line": number, "section": section,
                "excerpt": "business content", "query_coverage": coverage,
                "matched_concepts": ["topic"], "match_type": "alias", "domain_matches": []}
    result = rank_hits([hit(1, 100, "A"), hit(2, 100, "A"), hit(3, 100, "A"), hit(4, 30, "B")])
    assert [h["line"] for h in result] == [1, 2, 3, 4]


@pytest.mark.parametrize("domain,zh,en", [
    ("traffic", "疲劳驾驶告警如何保留来源？不由报警名决定处罚。", "How should fatigue driving alerts preserve evidence without deciding penalties?"),
    ("crm", "客户去重时不能只比较名称，如何保留关联？", "How should customer deduplication preserve linked records instead of only comparing names?"),
    ("education-it", "补考重修后如何保留成绩，不默认采用最高分？", "How should retake grades preserve their origin rather than automatically choose the highest score?"),
    ("oa", "报销费用申请失败如何避免重复付款？", "How should reimbursement handle failed payments without paying twice?"),
    ("medical-hospital-it", "电子病历如何区分草稿与签署，不能把保存当签署？", "How should electronic medical records distinguish drafts from signed records?"),
    ("data-product", "指标口径调整后如何定位依赖，不能把缺数当零？", "How should a metric definition identify affected consumers and distinguish missing values from zero?"),
    ("ai-native", "不启用长期记忆时，如何清除会话上下文？", "When memory is disabled, how should conversation memory be deleted?"),
    ("media-knowledge", "视频检索如何定位片段，不能只返回整段视频？", "How should video retrieval locate a playable moment rather than only the whole video?"),
])
def test_eight_domains_long_and_negative_queries_keep_relevant_candidates(domain, zh, en):
    for text in (zh, en):
        result = query("--search", text, "--limit", "5")
        assert any(h["domain_id"] == domain for h in result["hits"][:3])
        assert result["query"] == text  # No conversion of a negated need into an authorized requirement.
        assert result["retrieval_limit"] and all(h["status"] == "candidate" for h in result["hits"])


@pytest.mark.parametrize("text", ["ZXQDOMAINNONEXISTENT-661", "expensive", "memorial", "speedingness"])
def test_unknown_and_near_words_do_not_invent_aliases(text):
    result = query("--search", text)
    assert not result["hits"] and result["fallback"] and result["next_action"]


def test_ambiguous_terms_do_not_claim_semantic_resolution():
    result = query("--search", "metal fatigue", "--language", "en-US")
    # Lexical matches can be partial. Report that limit; do not claim materials expertise.
    assert "not semantic confidence" in result["retrieval_limit"]
    assert all(h["query_coverage"] < 100 and h["status"] == "candidate" for h in result["hits"])
    scoped = query("--domain", "materials-science", "--search", "metal fatigue", "--language", "en-US")
    assert not scoped["hits"] and scoped["fallback"]["dedicated_pack_available"] is False


def test_explicit_domain_and_private_evidence_remain_scoped(tmp_path):
    explicit = query("--domain", "ai-native", "--search", "memory")
    assert explicit["hits"] and all(h["domain_id"] == "ai-native" for h in explicit["hits"])
    (tmp_path / "domains").mkdir()
    (tmp_path / "config.yaml").write_text("domains:\n  - domain_id: private-test\n    knowledge_file: domains/test.md\n", encoding="utf-8")
    (tmp_path / "domains/test.md").write_text("# Private\n## Workflow\nPrivate vocabulary ZXQPRIVATE661 belongs to the customer.\n", encoding="utf-8")
    private = query("--search", "ZXQPRIVATE661", "--custom-root", str(tmp_path))
    assert len(private["hits"]) == 1 and private["hits"][0]["origin"] == "local_private"
    assert not query("--search", "ZXQPRIVATE661")["hits"]


def test_chinese_and_english_directory_have_readable_summaries():
    guides = json.loads((ROOT / "references/domains/domain-discovery.json").read_text(encoding="utf-8"))["domains"]
    assert len(guides) == 8
    for guide in guides:
        assert guide["name_zh"] and guide["summary_zh"] and guide["name_en"] and guide["summary_en"]
        text = (ROOT / guide["knowledge_file"]).read_text(encoding="utf-8")
        for term, aliases, section, note in guide["terms"]:
            assert "## " + section in text
            assert "**" + term + "**" in text
    for language, phrase in [("zh-CN", "领域知识中文目录"), ("en-US", "Domain knowledge directory")]:
        run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/query_domain.py"),
                              "--list", "--language", language, "--format", "markdown"],
                             capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 0 and phrase in run.stdout
    assert term_matches("memory", "memories") and not term_matches("memory", "memorial")


@pytest.mark.parametrize("text", ["补考成绩", "重修成绩", "retake grade", "retake grades",
                                 "retake scores", "resit grade", "resit scores"])
def test_retake_result_phrase_does_not_expand_into_generic_scores(text):
    result = query("--search", text, "--limit", "50")
    assert result["hits"] and all(h["domain_id"] == "education-it" for h in result["hits"])
    assert not {"grade", "score", "成绩"} & set(result["expanded_terms"])
    assert any("不能自行采用最高分或最新分" in h["excerpt"] for h in result["hits"])
    assert not any("technical grade" in h["excerpt"] or "risk score" in h["excerpt"]
                   or "calibrated score" in h["excerpt"] for h in result["hits"])


def test_retake_phrase_is_bilingual_and_preserves_negative_or_multi_topic_queries():
    left = query("--search", "补考成绩", "--limit", "50")["hits"]
    right = query("--search", "retake grades", "--limit", "50")["hits"]
    assert {(h["domain_id"], h["line"]) for h in left} == {(h["domain_id"], h["line"]) for h in right}
    for text in ("补考成绩不默认取最高分", "Do not automatically use the highest retake score"):
        result = query("--search", text)
        assert result["query"] == text
        assert result["hits"] and all(h["domain_id"] == "education-it" for h in result["hits"])
    # The complete phrase must not suppress another topic explicitly requested alongside it.
    combined = query("--search", "补考成绩和审批权限", "--limit", "50")
    assert {"education-it", "oa"} <= {h["domain_id"] for h in combined["hits"]}


def test_educational_alias_scope_does_not_force_broad_words_into_one_domain():
    for text in ("成绩", "academic grade"):
        result = query("--search", text, "--limit", "50")
        assert result["hits"] and all(h["domain_id"] == "education-it" for h in result["hits"])
    broad = query("--search", "grade", "--limit", "50")
    assert {"education-it", "traffic"} <= {h["domain_id"] for h in broad["hits"]}
    assert any("technical grade" in h["excerpt"] for h in broad["hits"])
    assert len({h["domain_id"] for h in query("--search", "审批", "--limit", "50")["hits"]}) > 1
    limited = query("--search", "score", "--limit", "3")
    assert len(limited["hits"]) == 3 and limited["total_matches"] > 3 and limited["truncated"]
