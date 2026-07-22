#!/usr/bin/env python3
"""Validate executable acceptance results, evidence and sign-off semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    doc = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(doc)
    ]
    items = doc.get("items", []) if isinstance(doc, dict) else []
    if isinstance(doc, dict):
        failures.extend(validate_evidence_refs(doc, args.document))
    conclusion = doc.get("conclusion") if isinstance(doc, dict) else None
    incomplete = [item.get("id") for item in items if item.get("mandatory") and item.get("result") != "pass"]
    if conclusion == "accepted" and incomplete:
        failures.append("accepted 结论仍有未通过的 mandatory 项：" + ", ".join(incomplete))
    if conclusion == "accepted_with_conditions" and not doc.get("conditions"):
        failures.append("accepted_with_conditions 必须填写条件、责任人和完成标准")
    if conclusion in {"accepted", "accepted_with_conditions"} and not doc.get("sign_offs"):
        failures.append(f"{conclusion} 必须包含签署记录")
    if conclusion in {"accepted", "accepted_with_conditions"}:
        missing_signoff_evidence = [
            str(item.get("actor", "<unknown>"))
            for item in doc.get("sign_offs", [])
            if isinstance(item, dict) and not str(item.get("evidence_ref", "")).strip()
        ]
        if missing_signoff_evidence:
            failures.append("接受结论存在未绑定证据的签署：" + ", ".join(missing_signoff_evidence))
    sign_offs = doc.get("sign_offs", []) if isinstance(doc, dict) else []
    rejected_sign_offs = [item.get("actor") for item in sign_offs if isinstance(item, dict) and item.get("decision") == "reject"]
    if conclusion in {"accepted", "accepted_with_conditions"} and rejected_sign_offs:
        failures.append("接受结论与拒绝签署冲突：" + ", ".join(rejected_sign_offs))
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: 验收执行记录 {doc.get('run_id')} 结构、证据与结论一致（{conclusion}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
