#!/usr/bin/env python3
"""Compatibility entry that delegates unified-PRD judgment to quality_gate.Gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from quality_gate import Gate, result_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--level", choices=["L0", "L1", "L2", "L3", "L4"], default="L2")
    parser.add_argument("--stage", default="baseline")
    args = parser.parse_args()

    gate = Gate()
    if not args.document.is_file():
        gate.add("BLOCK", "GATE-NOT-FILE", args.document, "输入 PRD 不存在")
    else:
        gate.check_prd(args.document, args.level, stage=args.stage)
    payload = result_payload(gate, "prd")
    for item in gate.findings:
        print(f"{item.severity} {item.code} [{item.ref}]: {item.message}")
    if not gate.findings:
        print("PASS: unified PRD uses the same quality-gate kernel")
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
