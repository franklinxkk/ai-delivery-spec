"""Domain assurance regression."""

from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]
coverage = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
sources = yaml.safe_load((ROOT / "references/domains/domain-sources.yaml").read_text(encoding="utf-8"))
failures: list[str] = []

domains = coverage.get("domains", [])
if len(domains) != 8:
    failures.append("expected eight built-in domain packs")
for domain in domains:
    domain_id = domain.get("domain_id")
    if domain.get("maturity") != "contract_tested" or domain.get("coverage", {}).get("contract_eval") != "passed":
        failures.append(f"{domain_id} lacks contract maturity")
    if domain.get("coverage", {}).get("behavioral_eval") == "passed":
        failures.append(f"{domain_id} overclaims behavior")

source_map = {source["id"]: source for source in sources.get("sources", [])}


def require_sources(ids: tuple[str, ...], label: str) -> None:
    for source_id in ids:
        if source_id not in source_map:
            failures.append(f"missing {label} evidence: {source_id}")


oa_vendors = (
    "KS-OA-WEAVER-WHITEPAPER", "KS-OA-SEEYON-OPEN-PLATFORM",
    "KS-OA-LANDRAY-CASES", "KS-OA-DINGTALK-OSS", "KS-OA-FEISHU-OSS",
)
require_sources(oa_vendors, "OA vendor")
for source_id in oa_vendors:
    source = source_map.get(source_id, {})
    if not source.get("evidence_role") or not source.get("claim_limit"):
        failures.append(f"{source_id} lacks evidence role/claim limit")
for source_id in ("KS-OA-DINGTALK-OSS", "KS-OA-FEISHU-OSS"):
    if "do not prove" not in source_map.get(source_id, {}).get("claim_limit", ""):
        failures.append(f"{source_id} confuses open component with open core product")

require_sources((
    "KS-DATA-PROPERTY-REGISTER-2026", "KS-DATA-PUBLIC-AUTH-2025",
    "KS-DATA-HQ-DATASET-2026", "KS-DATA-MODEL-DATA-2026",
    "KS-DATA-ACCOUNTING-2023", "KS-DATA-EU-AI-ACT-2024",
), "data-value/AI-supply")

def require_text(path: str, phrases: tuple[str, ...], label: str) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            failures.append(f"{label} misses invariant: {phrase}")


require_text("references/domains/domain-data-mart.md", (
    "registration-accounting separation", "digital-contract enforcement",
    "model feedback flywheel", "split leakage/contamination",
), "data pack")
require_text("references/domains/domain-media-knowledge.md", (
    "KnowledgeMoment = asset_id + rendition_id + temporal/spatial selector",
    "`/ads`, `/dig`, `/prd` and `/proto`",
), "media-knowledge pack")


def check_section(domain_id: str) -> None:
    query = subprocess.run(
        [sys.executable, str(ROOT / "scripts/query_domain.py"), "--domain", domain_id,
         "--section", "Core Workflows", "--format", "markdown"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if query.returncode or "## Core Workflows" not in query.stdout or "## Acceptance Checklist" in query.stdout:
        failures.append(f"{domain_id} query did not return the exact requested section")


for domain_id in ("data-product", "media-knowledge"):
    check_section(domain_id)

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: eight evidence-bounded domain packs verified")
