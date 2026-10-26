"""Bounded candidate retrieval regressions; these do not prove sector expertise."""
from pathlib import Path
import subprocess
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from query_domain import search_concepts, search_terms, term_matches

CATALOG = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
ALIASES = CATALOG["search_aliases"]


def query(*args):
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/query_domain.py"), *args],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr + result.stdout
    return yaml.safe_load(result.stdout)


class DomainRetrievalTests(unittest.TestCase):
    def test_known_variants_retrieve_same_existing_passages(self):
        for domain, zh, en in [
            ("traffic", "安全考核", "safety-assessments"),
            ("crm", "商机", "opportunities"),
            ("education-it", "高校", "universities"),
            ("education-it", "学籍", "student-statuses"),
            ("oa", "审批", "approvals"),
            ("medical-hospital-it", "电子病历", "electronic-medical-records"),
            ("data-product", "权限", "access-control"),
            ("ai-native", "工具授权", "tool-authorizations"),
            ("media-knowledge", "时间码", "time-codes"),
        ]:
            with self.subTest(domain=domain, query=en):
                record = next(d for d in CATALOG["domains"] if d["domain_id"] == domain)
                lines = (ROOT / record["knowledge_file"]).read_text(encoding="utf-8").splitlines()
                def hits(text):
                    terms = search_terms(text, ALIASES)
                    return {n for n, line in enumerate(lines) if any(term_matches(t, line) for t in terms)}
                assert hits(zh) and hits(zh) == hits(en)

    def test_long_mixed_query_keeps_literal_and_joint_concepts(self):
        text = "道路运输 road-transport 的 safety-assessments 要如何设置？"
        data = query("--domain", "traffic", "--search", text, "--limit", "8")
        assert data["expanded_terms"][0] == text
        assert {"道路运输", "安全考核"} <= set(data["matched_concepts"])
        assert data["hits"] and all(h["status"] == "candidate" for h in data["hits"])
        assert "法域" in data["source_usage_rule"]

    def test_natural_plural_sentence_recalls_curated_concepts(self):
        text = "How should universities retain student-status histories and education-data classifications?"
        assert {"高校", "学籍", "教育数据"} <= set(search_concepts(text, ALIASES))
        assert term_matches("safety assessment", "safety\u2011assessments")

    def test_near_words_remain_literal(self):
        for text in ["pledger", "expensive", "inactive", "milestoneary", "preuniversities", "universitiesque"]:
            with self.subTest(query=text):
                assert search_terms(text, ALIASES) == [text]

    def test_longest_concept_prevents_unrelated_alias_expansion(self):
        assert "里程" not in search_terms("How do milestones work?", ALIASES)
        assert "active enterprise" not in search_terms("active customers", ALIASES)
        assert "审批" in search_concepts("approvals", ALIASES)
        assert "审核" not in search_concepts("approvals", ALIASES)

    def test_unknown_sector_search_has_generic_route_without_fabricated_knowledge(self):
        data = query("--search", "How should aquaculture hatcheries reconcile fish biomass?", "--language", "en-US")
        assert data["total_matches"] == 0 and not data["hits"]
        assert data["fallback"]["dedicated_pack_available"] is None
        assert "sources" in data["fallback"]["next_action"]
        assert "expert" in data["fallback"]["claim_limit"]

    def test_explicit_unsupported_domain_can_continue_generic_work(self):
        data = query("--domain", "aquaculture", "--section", "State Machines", "--language", "en-US")
        assert data["origin"] == "generic_fallback" and data["knowledge_file"] is None
        assert data["maturity"] == "unsupported" and not data["source_refs"]
        assert data["fallback"]["dedicated_pack_available"] is False
        assert data["unavailable_sections"] == ["State Machines"] and data["selected_sections"] == []

    def test_known_pack_zero_hit_does_not_become_unsupported(self):
        data = query("--domain", "traffic", "--search", "unmatchedxyz555")
        assert data["total_matches"] == 0
        assert data["fallback"]["dedicated_pack_available"] is True

    def test_full_source_detail_exposes_verification_limits(self):
        data = query("--domain", "data-product", "--source-detail", "full", "--language", "en-US")
        source = next(s for s in data["source_refs"] if s["id"] == "KS-DATA-EU-AI-AMEND-2026")
        assert "verification_evidence" in source
        assert "JavaScript" in source["verification_evidence"]["method_and_limit"]
        assert all(s["binding_use"] == "prohibited" for s in data["source_refs"]
                   if s["effect_class"] in {"product_pattern", "change_watch"})

    def test_builtin_origin_does_not_imply_authoritative_policy(self):
        for language, explanation in [("en-US", "not government authority"), ("zh-CN", "不代表政府权威")]:
            data = query("--domain", "ai-native", "--language", language)
            assert data["origin"] == "official"
            assert explanation in data["source_usage_rule"]
            found = query("--domain", "ai-native", "--search", "工具授权", "--language", language)
            assert found["hits"] and all(h["origin"] == "official" for h in found["hits"])
            assert explanation in found["source_usage_rule"]
        unsupported = query("--domain", "aquaculture", "--language", "en-US")
        assert unsupported["origin"] == "generic_fallback" and not unsupported["source_refs"]


if __name__ == "__main__":
    unittest.main()
