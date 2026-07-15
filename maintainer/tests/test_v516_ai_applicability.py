#!/usr/bin/env python3
"""Regression: AI exclusions and AI-Coding consumers are not AI product scope."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validators" / "validate_coding_agent_contract.py"
sys.path.insert(0, str(VALIDATOR.parent))
SPEC = importlib.util.spec_from_file_location("coding_contract", VALIDATOR)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


excluded = """
本期不建设独立 AI 模型/能力中心。
第四部分：工程与 AI Coding 附录。
Coding Agent 读取稳定 ID 后实现页面。
"""
if module.ai_contract_applicable(excluded):
    raise SystemExit("AI exclusion or AI-Coding consumer was misread as product scope")

applicable = """
本期提供 AI 组课：调用大模型生成课程结构，由内容审核员人工确认后发布。
"""
if not module.ai_contract_applicable(applicable):
    raise SystemExit("positive AI product behavior did not activate AI contracts")

mixed = """
本期不建设 AI 模型中心；但 AI 组课调用大模型生成结构，并保留人工审核。
"""
if not module.ai_contract_applicable(mixed):
    raise SystemExit("positive AI clause after an exclusion was incorrectly suppressed")

print("PASS: AI product applicability ignores exclusions without hiding real AI scope")
