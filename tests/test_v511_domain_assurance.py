"""Regression for evidence-bounded domain maturity and OA source semantics."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
coverage = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
sources = yaml.safe_load((ROOT / "references/domains/domain-sources.yaml").read_text(encoding="utf-8"))
failures: list[str] = []

domains = coverage.get("domains", [])
if len(domains) != 7:
    failures.append("expected seven built-in domain packs")
for domain in domains:
    if domain.get("maturity") != "contract_tested":
        failures.append(f"{domain.get('domain_id')} did not pass contract-tested promotion")
    if domain.get("coverage", {}).get("contract_eval") != "passed":
        failures.append(f"{domain.get('domain_id')} lacks passing deterministic contract evaluation")
    if domain.get("coverage", {}).get("behavioral_eval") == "passed":
        failures.append(f"{domain.get('domain_id')} overclaims fresh-agent behavioral validation")

source_map = {source["id"]: source for source in sources.get("sources", [])}
for source_id in (
    "KS-OA-WEAVER-WHITEPAPER", "KS-OA-SEEYON-OPEN-PLATFORM",
    "KS-OA-LANDRAY-CASES", "KS-OA-DINGTALK-OSS", "KS-OA-FEISHU-OSS",
):
    source = source_map.get(source_id)
    if not source:
        failures.append(f"missing OA vendor evidence: {source_id}")
        continue
    if not source.get("evidence_role") or not source.get("claim_limit"):
        failures.append(f"{source_id} lacks evidence role/claim limit")

for source_id in ("KS-OA-DINGTALK-OSS", "KS-OA-FEISHU-OSS"):
    if "do not prove" not in source_map[source_id]["claim_limit"]:
        failures.append(f"{source_id} confuses open component with open core product")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: seven packs are contract-tested without behavioral overclaim; OA vendor evidence is scope-bounded")
