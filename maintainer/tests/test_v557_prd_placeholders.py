import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate, result_payload


@pytest.mark.parametrize("content", [
    "## Scope\n{placeholder}\n## Behavior\n{placeholder}\n## Acceptance\n{placeholder}\n",
    "## 范围\n- **待补充**\n## 行为\n- TBD\n## 验收\nTODO\n",
    "| Scope | Behavior | Acceptance |\n| --- | --- | --- |\n| {scope} | TBD | 待填写 |\n",
])
def test_only_placeholders_do_not_pass(tmp_path, content):
    path = tmp_path / "prd.md"
    path.write_text(content, encoding="utf-8")
    gate = Gate()
    gate.check_prd(path, stage="baseline")

    assert any(item.severity == "BLOCK" and item.code == "SPEC-EMPTY" for item in gate.findings)
    assert result_payload(gate, "prd")["exit_code"] == 2


def test_published_prd_template_is_a_skeleton(tmp_path):
    template = ROOT / "references" / "templates" / "unified-requirement-prd-template.md"
    prd = tmp_path / "renamed.md"
    prd.write_bytes(template.read_bytes())
    gate = Gate()
    gate.check_prd(prd, stage="baseline")

    assert any(item.severity == "BLOCK" and item.code == "SPEC-EMPTY" for item in gate.findings)


@pytest.mark.parametrize("behavior", [
    "After reopening the order, GET /orders/{orderId} returns the saved rack.",
    "Render `{{ rack }}` in the location column of the reopened order.",
    "Use `TODO` as the literal value of the auditing tag.",
    "```json\n{\"status\": \"TODO\", \"id\": \"{orderId}\"}\n```",
    "~~~text\nTBD\n~~~",
    "    {orderId}\n",
])
def test_legitimate_contract_and_code_are_preserved(tmp_path, behavior):
    path = tmp_path / "prd.md"
    path.write_text(f"## Scope\nTBD\n\n## Behavior\n{behavior}\n\n## Acceptance\n{{placeholder}}\n", encoding="utf-8")
    gate = Gate()
    gate.check_prd(path, stage="baseline")

    assert not any(item.code == "SPEC-EMPTY" for item in gate.findings)
