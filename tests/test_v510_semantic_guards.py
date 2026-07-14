"""Regression for false-pass, clarification-closure and ledger-impact defects."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_change_impact import graph_from_truth
from scan_requirement_ambiguity import scan, scan_closure


def run(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *parts], cwd=ROOT, text=True, capture_output=True)


failures: list[str] = []
positive = ROOT / "tests/fixtures/coding-l2.md"
negative = ROOT / "tests/fixtures/prd-l2-keyword-shell.md"
validators = (
    ("scripts/validators/validate_prd_quality.py", "--level", "L2"),
    ("scripts/validators/validate_coding_agent_contract.py", "--level", "L2", "--profile", "full_prd"),
)
for script, *args in validators:
    good = run(script, str(positive), *args)
    bad = run(script, str(negative), *args)
    if good.returncode:
        failures.append(f"{script} rejected substantive fixture: {good.stdout}{good.stderr}")
    if bad.returncode == 0:
        failures.append(f"{script} accepted the keyword-only shell")

raw_requests = (
    "三甲医院做门诊退费与医保对账，多角色审批，原支付渠道退款，医保失败人工处理。",
    "制造企业做来料质量异常、隔离、评审、退货或让步接收和供应商整改闭环。",
    "连锁零售在存量系统增加跨门店调拨、在途、收货差异和库存回冲。",
)
for text in raw_requests:
    if scan(text):
        failures.append("fixture should prove lexical-only scan can be empty")
    structural = {item["kind"] for item in scan_closure(text)}
    if not {"actor-authority", "state-authority", "acceptance-evidence"}.issubset(structural):
        failures.append(f"clarification closure missed structural gaps: {sorted(structural)}")

ledger = {
    "schema_version": "5.1.0",
    "edges": [
        {"from_id": "REQ-DEMO-001", "to_id": "ACT-DEMO-001", "relation": "specifies", "source": "behavior_refs"},
        {"from_id": "ACT-DEMO-001", "to_id": "AC-DEMO-001", "relation": "verified_by", "source": "acceptance_refs"},
    ],
    "forward_index": {"REQ-DEMO-001": ["ACT-DEMO-001"]},
    "reverse_index": {"AC-DEMO-001": ["ACT-DEMO-001"]},
}
graph = graph_from_truth(ledger)
if graph.get("REQ-DEMO-001") != {"ACT-DEMO-001"} or graph.get("AC-DEMO-001") != {"ACT-DEMO-001"}:
    failures.append(f"traceability ledger did not become an impact graph: {dict(graph)}")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: v5.1.0 rejects keyword shells, exposes structural clarification gaps, and traverses trace ledgers")

