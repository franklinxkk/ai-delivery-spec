"""Exercise the shipped query-domain command. Pass ADS_SKILL_ROOT to test another copy."""

from datetime import date, timedelta
import os
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(os.environ.get("ADS_SKILL_ROOT", Path(__file__).resolve().parents[2]))
CLI = ROOT / "scripts" / "ai_delivery_spec_cli.py"


def query(*args, output="yaml"):
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(CLI), "query-domain", *args, "--format", output],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30,
    )
    return yaml.safe_load(result.stdout) if output == "yaml" else result.stdout


class DomainReviewTests(unittest.TestCase):
    def test_existing_passages_are_retrieved_in_context(self):
        cases = [
            ("双重预防机制", "traffic", "Core Workflows", "risk classification/control"),
            ("公文流转", "oa", "Core Workflows", "issued"),
            ("公共数据", "data-product", "Vocabulary", "authorized operation"),
            ("标注过渡期", "ai-native", "Policy / Privacy Constraints", "KS-DATA-EU-AI-AMEND-2026"),
            ("合成内容", "ai-native", "Policy / Privacy Constraints", "KS-DATA-EU-AI-AMEND-2026"),
            ("线索分配", "crm", "Domain Events", "LeadAssigned"),
            ("指标目录", "data-product", "Metric / Indicator Governance", "指标库"),
            ("知识库问答", "ai-native", "Domain Test Scenarios", "grounded answer with citations"),
            ("医疗互认", "medical-hospital-it", "Policy / Privacy Constraints", "KS-MEDICAL-MUTUAL-RECOGNITION-2024"),
        ]
        for term, domain, section, extract in cases:
            with self.subTest(term=term):
                hits = query("--search", term, "--limit", "3")["hits"]
                chosen = next((h for h in hits if h["domain_id"] == domain and h["section"] == section
                               and extract.casefold() in h["excerpt"].casefold()), None)
                self.assertIsNotNone(chosen, hits)
                original = (ROOT / chosen["knowledge_file"]).read_text(encoding="utf-8").splitlines()
                self.assertIn(chosen["excerpt"], original[chosen["line"] - 1])
                self.assertEqual(chosen["status"], "candidate")

    def test_scope_and_genuine_gaps(self):
        for domain, term in [("education-it", "课后服务"), ("media-knowledge", "三审三校"),
                             ("traffic", "标注过渡期"), ("crm", "公文流转")]:
            with self.subTest(domain=domain, term=term):
                result = query("--domain", domain, "--search", term)
                self.assertEqual(result["total_matches"], 0)
                self.assertTrue(result["fallback"]["dedicated_pack_available"])
                self.assertTrue(result["next_action"])
        hits = query("--domain", "media-knowledge", "--search", "知识库问答")["hits"]
        self.assertTrue(any("grounded Q&A" in h["excerpt"] for h in hits))

    def test_review_deadline_is_visible_and_does_not_change_effect_class(self):
        catalog = yaml.safe_load((ROOT / "references/domains/domain-sources.yaml").read_text(encoding="utf-8"))
        domain = "medical-hospital-it"
        expected = {}
        for source in catalog["sources"]:
            if domain in source["domains"]:
                checked = date.fromisoformat(str(source["last_verified_at"]))
                expected[source["id"]] = checked + timedelta(days=source["refresh_days"])
        overdue = {k: v.isoformat() for k, v in expected.items() if v < date.today()}
        full = query("--domain", domain, "--source-detail", "full")
        self.assertEqual(full["source_reviews_due"], overdue)
        for row in full["source_refs"]:
            key = row["id"]
            self.assertEqual(str(row["review_due_at"]), expected[key].isoformat())
            self.assertEqual(row["stale"], key in overdue)
            if row["effect_class"] in {"change_watch", "product_pattern"}:
                self.assertEqual(row["binding_use"], "prohibited")
            elif key in overdue:
                self.assertEqual(row["binding_use"], "reverify_source_before_use")
        compact = query("--domain", domain, "--section", "权限隐私")
        self.assertEqual(compact["source_reviews_due"], overdue)
        result = query("--domain", domain, "--search", "检查检验结果互认", "--limit", "1")
        self.assertEqual(result["domain_source_reviews_due"].get(domain, {}), overdue)
        cited = result["hits"][0]["source_refs"]
        self.assertIn("KS-MEDICAL-MUTUAL-RECOGNITION-2024", cited)
        self.assertEqual(result["cited_source_reviews_due"], {s: overdue[s] for s in cited if s in overdue})
        markdown = query("--domain", domain, "--search", "检查检验结果互认", output="markdown")
        for source, due in overdue.items():
            self.assertIn(f"{source} ({due})", markdown)


if __name__ == "__main__":
    unittest.main()
