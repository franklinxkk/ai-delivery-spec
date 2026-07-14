#!/usr/bin/env python3
"""Scan a requirement document for common ambiguous or non-testable wording."""

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()
    findings = scan(args.document.read_text(encoding="utf-8"))
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
