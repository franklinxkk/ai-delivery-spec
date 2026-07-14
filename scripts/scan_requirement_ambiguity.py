#!/usr/bin/env python3
"""Scan lexical ambiguity and missing clarification dimensions.

This is an advisory discovery scanner, not proof that a requirement is correct.
It combines cheap wording checks with structural prompts so a concise request
cannot appear ready merely because it avoids words such as "支持" or "灵活".
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PATTERNS = {
    "vague-capability": r"(?:支持|实现|提供)(?![^。；\n]{0,24}(?:条件|角色|结果|规则|范围))",
    "vague-quantity": r"(?:适量|若干|一定数量|大量|少量|较多|尽量)",
    "vague-time": r"(?:及时|尽快|实时处理|稍后|定期)(?![^。；\n]{0,16}\d)",
    "open-list": r"(?:等等|等功能|等场景|诸如此类)",
    "undefined-default": r"(?:默认|自动)(?![^。；\n]{0,24}(?:为|条件|规则|当|若|由))",
    "unbounded-config": r"(?:灵活配置|可配置|按需配置)(?![^。；\n]{0,24}(?:配置项|范围|权限|规则))",
    "unspecified-actor": r"(?:相关人员|有关人员|管理员等|业务人员)(?![^。；\n]{0,18}(?:角色|权限|范围))",
}


def scan(text: str) -> list[dict[str, object]]:
    findings = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            continue
        for kind, pattern in PATTERNS.items():
            for match in re.finditer(pattern, line):
                findings.append({
                    "id": f"AMB-{len(findings)+1:03d}",
                    "kind": kind,
                    "line": line_no,
                    "text": match.group(0),
                    "context": line.strip()[:240],
                    "action": "replace with actor/condition/threshold/result/exception that can be accepted",
                })
    return findings


def scan_closure(text: str) -> list[dict[str, object]]:
    """Return missing requirement dimensions; never infer their answers."""
    lowered = text.lower()
    actor_hits = re.findall(
        r"\bROLE-[A-Z0-9-]+\b|管理员|申请人|审批人|财务|患者|医生|护士|药师|医保|质检|仓库|采购|供应商|门店|店长|调度|运维|客户|监管|测试",
        text,
        re.I,
    )
    lenses: list[tuple[str, bool, str]] = [
        ("actor-authority", len(set(actor_hits)) >= 2, "name every actor, decision authority, permission and data scope"),
        ("scope-boundary", bool(re.search(r"范围|纳入|不包含|不做|边界|scope|out of scope", lowered)), "define included and excluded scope"),
        ("state-authority", bool(re.search(r"状态机|当前状态|下一状态|状态权威|谁维护|state owner|system of record|source of truth", lowered)), "define lifecycle states and the authoritative owner of each result"),
        ("exception-recovery", bool(re.search(r"异常|失败|超时|重试|补偿|回滚|人工处理|error|failure|retry|compensat|rollback", lowered)), "define failure, partial success, recovery and manual handling"),
        ("acceptance-evidence", bool(re.search(r"验收|预期结果|证据|签署|acceptance|expected|evidence|sign.?off", lowered)), "define executable acceptance and required evidence"),
    ]
    if re.search(r"退款|支付|赔付|金额|结算|退费|refund|payment|claim|settlement", lowered):
        lenses.append((
            "money-reconciliation",
            bool(re.search(r"幂等|重复|对账|差错|冲正|挂账|补偿|idempot|reconcil|reversal", lowered)),
            "define money authority, idempotency, partial success, reversal and reconciliation",
        ))
    if re.search(r"库存|批次|在途|调拨|收货|数量|来料|stock|inventory|batch|quantity", lowered):
        lenses.append((
            "quantity-conservation",
            bool(re.search(r"数量守恒|冻结|预占|可用|库存流水|部分|差异|回冲|conservation|reserved|ledger|partial", lowered)),
            "define quantity conservation, frozen/available/in-transit ledgers and partial disposition",
        ))
    if re.search(r"存量|旧系统|已有系统|改造|变更|迁移|兼容|brownfield|legacy|migration", lowered):
        lenses.append((
            "brownfield-baseline",
            bool(re.search(r"stage\s*0|现状基线|变更种子|before|after|差异|历史数据|回退|baseline", lowered)),
            "extract the trusted current-state baseline, change seed, history compatibility and rollback",
        ))

    findings: list[dict[str, object]] = []
    for kind, passed, action in lenses:
        if passed:
            continue
        findings.append({
            "kind": kind,
            "line": 0,
            "text": "missing clarification dimension",
            "context": "document-level structural gap",
            "action": action,
            "advisory": True,
        })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--profile", choices=["lexical", "closure", "full"], default="full")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()
    text = args.document.read_text(encoding="utf-8")
    findings = []
    if args.profile in {"lexical", "full"}:
        findings.extend(scan(text))
    if args.profile in {"closure", "full"}:
        findings.extend(scan_closure(text))
    for index, item in enumerate(findings, 1):
        item["id"] = f"AMB-{index:03d}"
    if args.format == "json":
        rendered = json.dumps({"findings": findings}, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = f"# Ambiguity Scan\n\nFindings: **{len(findings)}**\n\n"
        rendered += "".join(
            f"- `{item['id']}` line {item['line']} `{item['kind']}`: {item['context']}\n"
            for item in findings
        )
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    if findings and args.fail_on_findings:
        return 1
    print(f"PASS: ambiguity scan completed ({len(findings)} findings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
