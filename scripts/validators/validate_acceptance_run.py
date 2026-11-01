#!/usr/bin/env python3
"""Validate executable acceptance results, evidence and sign-off semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import Draft202012Validator, FormatChecker


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_support import input_error_detail
SCHEMA = ROOT / "schemas" / "acceptance-run.schema.json"


def _local_evidence_path(document_path: Path, uri: str) -> tuple[Path | None, str | None]:
    """Resolve a local evidence URI without allowing it to escape the ARUN directory."""
    parsed = urlsplit(uri)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return None, None
    if parsed.scheme or parsed.netloc:
        return None, f"不支持的证据 URI：{uri}；仅允许相对路径或 http(s) URL"
    relative = Path(unquote(parsed.path))
    if relative.is_absolute():
        return None, f"本地证据必须使用 ARUN 目录内的相对路径：{uri}"
    root = document_path.parent.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, f"本地证据路径越过 ARUN 目录：{uri}"
    if not candidate.is_file():
        return None, f"本地证据文件不存在：{uri}"
    return candidate, None


def validate_evidence_refs(document: dict, document_path: Path) -> list[str]:
    """Validate direct paths/URLs and EVD-* references declared by one ARUN."""
    failures: list[str] = []
    catalog: dict[str, dict] = {}
    for entry in document.get("evidence_catalog", []) or []:
        if not isinstance(entry, dict):
            continue
        evidence_id = str(entry.get("id", ""))
        if evidence_id in catalog:
            failures.append(f"evidence_catalog 存在重复 ID：{evidence_id}")
        elif evidence_id:
            catalog[evidence_id] = entry

    def resolve(ref: str, owner: str) -> bool:
        uri = ref
        expected_hash = ""
        if ref.startswith("EVD-"):
            entry = catalog.get(ref)
            if not entry:
                failures.append(f"{owner} 引用的 {ref} 未在 evidence_catalog 中登记")
                return False
            uri = str(entry.get("uri", ""))
            expected_hash = str(entry.get("sha256", ""))
        local_path, error = _local_evidence_path(document_path, uri)
        if error:
            failures.append(f"{owner}：{error}")
            return False
        if local_path is not None and expected_hash:
            actual_hash = hashlib.sha256(local_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                failures.append(f"{owner} 的证据哈希不一致：{ref}")
                return False
        return True

    for item in document.get("items", []) or []:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "<unknown>"))
        refs = item.get("evidence_refs", []) or []
        if item.get("result") == "pass" and not refs:
            failures.append(f"{item_id} 结果为 pass，但没有证据引用")
        for ref in refs:
            resolve(str(ref), item_id)
    for sign_off in document.get("sign_offs", []) or []:
        if not isinstance(sign_off, dict) or not sign_off.get("evidence_ref"):
            continue
        resolve(str(sign_off["evidence_ref"]), f"签署人 {sign_off.get('actor', '<unknown>')}")
    return failures


def execution_environment(doc: dict) -> tuple[bool, bool]:
    """Classify declarations, never infer execution from a keyword mention."""
    kind = doc.get("execution_type")
    if kind is not None:
        return kind == "browser", kind == "integration"
    environment = str(doc.get("environment", "")).strip().casefold()
    # Legacy free text is accepted only as an affirmative environment label.
    if re.search(r"\b(?:no|not|without|unavailable|missing|unexecuted)\b|未|没有|仅|无法|不支持", environment):
        return False, False
    browser = bool(re.match(r"(?:browser\b|chrome\b|chromium\b|edge\b|firefox\b|safari\b|webkit\b|playwright\b|真实浏览器|浏览器)", environment))
    integration = bool(re.match(r"(?:integration\b|sit\b|uat\b|staging\b|集成|联调|预发布)", environment))
    return browser, integration


def validate_acceptance_document(doc: object, path: Path) -> list[dict[str, str]]:
    """One semantic authority for the standalone CLI and the composed gate."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    issues = [
        dict(code="ACCEPTANCE-SCHEMA", ref='.'.join(str(part) for part in error.path) or '<root>', message=error.message)
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(doc)
    ]
    if issues:
        return issues
    def add(code, message, ref=""):
        issues.append(dict(code=code, message=message, ref=ref))
    negative_execution = {
        'browser': r"\b(?:no|without)\s+(?:real\s+)?browser|\bnot\s+(?:a\s+)?browser|未(?:进行|执行)?(?:真实)?浏览器|浏览器.{0,5}未执行",
        'integration': r"\b(?:no|without)\s+(?:real\s+)?integration|\bnot\s+integration|未(?:进行|执行)?(?:真实)?(?:联调|集成)|(?:联调|集成).{0,5}未执行",
    }
    negative_pattern = negative_execution.get(doc.get('execution_type'))
    if negative_pattern and re.search(negative_pattern, str(doc.get('environment', '')), re.I):
        add("ACCEPTANCE-EXECUTION-CONFLICT", "execution_type 与环境中的未执行声明冲突；按实际执行修正，不升级证据等级")
    for message in validate_evidence_refs(doc, path):
        add("ACCEPTANCE-EVIDENCE-INVALID", message)
    items = doc.get("items", [])
    seen = set()
    for item in items:
        if item['id'] in seen:
            add("ACCEPTANCE-DUPLICATE-ITEM", "验收项 ID 重复，不能覆盖先前结果", item['id'])
        seen.add(item['id'])
        if item.get('result') == 'pass' and not item.get('actual_result', '').strip():
            add("ACCEPTANCE-PASS-NO-EVIDENCE", "pass 项必须填写实际结果和证据引用", item['id'])
    conclusion = doc.get("conclusion")
    accepted = conclusion in {"accepted", "accepted_with_conditions"}
    incomplete = [item.get("id") for item in items if item.get("mandatory") and item.get("result") != "pass"]
    if accepted and incomplete:
        add("ACCEPTANCE-INCOMPLETE-CONCLUSION", "接受结论仍有未通过的 mandatory 项；条件不能代替关键验收", ", ".join(incomplete))
    if conclusion == "accepted_with_conditions" and not doc.get("conditions"):
        add("ACCEPTANCE-CONDITION-MISSING", "accepted_with_conditions 必须填写条件、责任人和完成标准")
    if accepted and not doc.get("sign_offs"):
        add("ACCEPTANCE-SIGNOFF-MISSING", f"{conclusion} 必须包含签署记录")
    if accepted:
        missing_signoff_evidence = [
            str(item.get("actor", "<unknown>"))
            for item in doc.get("sign_offs", [])
            if isinstance(item, dict) and not str(item.get("evidence_ref", "")).strip()
        ]
        if missing_signoff_evidence:
            add("ACCEPTANCE-SIGNOFF-NO-EVIDENCE", "接受结论存在未绑定证据的签署", ", ".join(missing_signoff_evidence))
    sign_offs = doc.get("sign_offs", [])
    rejected_sign_offs = [item.get("actor") for item in sign_offs if isinstance(item, dict) and item.get("decision") == "reject"]
    if accepted and rejected_sign_offs:
        add("ACCEPTANCE-SIGNOFF-CONFLICT", "接受结论与拒绝签署冲突", ", ".join(rejected_sign_offs))
    conditional = any(item.get('decision') == 'approve_with_conditions' for item in sign_offs)
    if accepted and conditional and not doc.get('conditions'):
        add("ACCEPTANCE-CONDITION-MISSING", "有条件签署必须保留条件、责任人和完成标准")
    if conclusion == 'accepted' and (conditional or doc.get('conditions')):
        add("ACCEPTANCE-CONDITION-CONFLICT", "记录仍有条件，不能声明无条件 accepted；保留有条件结论或引用条件已解除的实际签认")
    blockers = [item['id'] for item in doc.get('residual_issues', []) if item.get('disposition') == 'fix_before_acceptance']
    if accepted and blockers:
        add("ACCEPTANCE-RESIDUAL-BLOCK", "仍有验收前必须修复的问题；处理或记录真实的范围/处置变更后再接受", ', '.join(blockers))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    try:
        doc = yaml.safe_load(args.document.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"FAIL: ACCEPTANCE-INPUT {args.document}: {input_error_detail(exc)}; 检查路径、UTF-8 编码及 YAML 缩进后重跑。")
        return 1
    issues = validate_acceptance_document(doc, args.document)
    if issues:
        for item in issues:
            print(f"FAIL: {item['code']} {item['ref']}: {item['message']}")
        return 1
    print(f"PASS: 验收执行记录 {doc.get('run_id')} 的声明与引用检查通过（{doc.get('conclusion')}）；未核实执行及签认的真实性")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
