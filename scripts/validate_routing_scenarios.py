#!/usr/bin/env python3
"""Regression-test representative routing decisions for ai-delivery-spec.

This is a lightweight policy harness, not a production NLP classifier. It keeps
trigger boundaries, mode precedence, work-path selection, PRD profile selection,
and add-on routing executable while the prose skill evolves.
"""

from __future__ import annotations

from dataclasses import dataclass
import sys


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    value = text.lower()
    return any(term.lower() in value for term in terms)


DELIVERY_ARTIFACTS = (
    "prd",
    "requirement",
    "requirements document",
    "product specification",
    "product",
    "prototype",
    "acceptance",
    "uat",
    "test case",
    "api contract",
    "data contract",
    "ddd",
    "roadmap",
    "launch plan",
    "delivery package",
    "需求",
    "需求文档",
    "产品规格",
    "产品",
    "原型",
    "验收",
    "测试用例",
    "接口契约",
    "数据契约",
    "上线方案",
    "交付包",
)

CODE_ONLY_EXCLUSIONS = (
    "fix this syntax error",
    "debug this stack trace",
    "rewrite this paragraph",
    "copy edit",
    "only code",
    "语法错误",
    "只改代码",
    "润色文案",
)

FULL_SIGNALS = (
    "production launch",
    "formal acceptance",
    "migration",
    "rollback",
    "on-call",
    "complete delivery package",
    "上线",
    "正式验收",
    "迁移",
    "回滚",
    "完整交付包",
)

STANDARD_SIGNALS = (
    "development",
    "developer",
    "engineering",
    "qa",
    "test",
    "customer demo",
    "bid",
    "procurement",
    "handoff",
    "implementation",
    "multi-role",
    "full lifecycle",
    "complete prd",
    "开发",
    "研发",
    "测试",
    "客户演示",
    "招标",
    "投标",
    "交付",
    "完整prd",
    "全生命周期",
)

LITE_SIGNALS = (
    "quick",
    "draft",
    "rough",
    "direction",
    "idea",
    "one-page",
    "快速",
    "草稿",
    "粗略",
    "方向",
    "想法",
)

AI_PRODUCT_SIGNALS = (
    "ai native",
    "agent",
    "multi-agent",
    "llm feature",
    "ai runtime",
    "prompt",
    "model evaluation",
    "智能体",
    "大模型",
    "模型评测",
    "提示词",
)

AI_CODING_SIGNALS = (
    "ai coding",
    "coding agent",
    "cursor",
    "claude code",
    "copilot workspace",
    "agents.md",
    "claude.md",
    ".cursor/rules",
    "ac-yaml",
    "ac_structured",
    "test stubs",
    "自动生成系统",
    "ai编程",
    "ai coding",
)

WORKFLOW_SIGNALS = (
    "approval",
    "workflow",
    "state transition",
    "escalation",
    "audit",
    "sla",
    "cross-module",
    "审批",
    "工作流",
    "状态流转",
    "升级",
    "审计",
    "跨模块",
)

PROTOTYPE_SIGNALS = (
    "prototype",
    "html prototype",
    "clickable prototype",
    "screenshot",
    "mockup",
    "wireframe",
    "原型",
    "截图",
    "交互",
)

REALTIME_SIGNALS = (
    "sse",
    "websocket",
    "polling",
    "push notification",
    "countdown",
    "real-time",
    "实时",
    "推送",
    "倒计时",
    "轮询",
)


@dataclass(frozen=True)
class Route:
    trigger: bool
    mode: str
    work_path: str
    profile: str
    entrypoints: tuple[str, ...]


@dataclass(frozen=True)
class Scenario:
    name: str
    prompt: str
    expected: Route


def route(prompt: str) -> Route:
    text = prompt.lower()
    trigger = contains_any(text, DELIVERY_ARTIFACTS) and not contains_any(text, CODE_ONLY_EXCLUSIONS)

    if not trigger:
        return Route(False, "none", "none", "none", ())

    if contains_any(text, FULL_SIGNALS):
        mode = "Full"
    elif contains_any(text, STANDARD_SIGNALS) or contains_any(text, AI_CODING_SIGNALS):
        mode = "Standard"
    elif contains_any(text, LITE_SIGNALS):
        mode = "Lite"
    else:
        mode = "Standard"

    if contains_any(text, AI_CODING_SIGNALS):
        work_path = "AI Coding Delivery"
        profile = "AI-Coding Full PRD"
    elif contains_any(text, AI_PRODUCT_SIGNALS):
        work_path = "AI Native Product Discovery"
        profile = "Human-First Full PRD"
    elif contains_any(text, FULL_SIGNALS) or "full lifecycle" in text or "全生命周期" in prompt:
        work_path = "Traditional Product Lifecycle"
        profile = "Human-First Full PRD"
    else:
        work_path = "Traditional Product Lifecycle"
        profile = "Contract Summary" if mode == "Lite" else "Human-First Full PRD"

    entrypoints = ["delivery-core.md"]
    ai_coding = contains_any(text, AI_CODING_SIGNALS)

    if contains_any(text, PROTOTYPE_SIGNALS):
        entrypoints.append("prototype-testability.md")
    if (contains_any(text, AI_PRODUCT_SIGNALS) and not ai_coding) or contains_any(text, WORKFLOW_SIGNALS):
        entrypoints.append("advanced-extensions.md")
    if ai_coding:
        entrypoints.append("coding-agent-compat.md")
    if contains_any(text, REALTIME_SIGNALS):
        entrypoints.append("realtime-contract.md")

    return Route(True, mode, work_path, profile, tuple(entrypoints))


SCENARIOS = (
    Scenario(
        "English simple CRM idea",
        "Write a PRD for a simple CRM system from this rough idea.",
        Route(True, "Lite", "Traditional Product Lifecycle", "Contract Summary", ("delivery-core.md",)),
    ),
    Scenario(
        "English development PRD",
        "Write a complete PRD for a CRM system for frontend, backend and QA development handoff.",
        Route(True, "Standard", "Traditional Product Lifecycle", "Human-First Full PRD", ("delivery-core.md",)),
    ),
    Scenario(
        "English AI coding PRD",
        "Use this prototype to produce an AI Coding PRD with AGENTS.md, AC-YAML and API stubs for Cursor.",
        Route(True, "Standard", "AI Coding Delivery", "AI-Coding Full PRD", ("delivery-core.md", "prototype-testability.md", "coding-agent-compat.md")),
    ),
    Scenario(
        "English AI native product",
        "Brainstorm an AI native learning agent product and define runtime fallback and evaluation.",
        Route(True, "Standard", "AI Native Product Discovery", "Human-First Full PRD", ("delivery-core.md", "advanced-extensions.md")),
    ),
    Scenario(
        "English realtime prototype",
        "Review this clickable prototype with WebSocket alerts and countdown SLA behavior.",
        Route(True, "Standard", "Traditional Product Lifecycle", "Human-First Full PRD", ("delivery-core.md", "prototype-testability.md", "advanced-extensions.md", "realtime-contract.md")),
    ),
    Scenario(
        "Chinese rough idea",
        "我有一个简单CRM想法，帮我快速整理成需求草稿。",
        Route(True, "Lite", "Traditional Product Lifecycle", "Contract Summary", ("delivery-core.md",)),
    ),
    Scenario(
        "Chinese full lifecycle",
        "帮我写一个全生命周期的产品需求文档，给研发和测试评审。",
        Route(True, "Standard", "Traditional Product Lifecycle", "Human-First Full PRD", ("delivery-core.md",)),
    ),
    Scenario(
        "Chinese AI coding",
        "根据这个原型生成AI coding需要的完整PRD，并输出AGENTS.md和ac_structured。",
        Route(True, "Standard", "AI Coding Delivery", "AI-Coding Full PRD", ("delivery-core.md", "prototype-testability.md", "coding-agent-compat.md")),
    ),
    Scenario(
        "Chinese workflow",
        "设计一个带审批、状态流转和审计的工单需求文档。",
        Route(True, "Standard", "Traditional Product Lifecycle", "Human-First Full PRD", ("delivery-core.md", "advanced-extensions.md")),
    ),
    Scenario(
        "Code-only exclusion",
        "Fix this syntax error in my React component.",
        Route(False, "none", "none", "none", ()),
    ),
)


def main() -> int:
    failures: list[str] = []
    for scenario in SCENARIOS:
        actual = route(scenario.prompt)
        if actual != scenario.expected:
            failures.append(
                f"{scenario.name}: expected {scenario.expected}, got {actual}"
            )

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1

    print(f"PASS: {len(SCENARIOS)} bilingual routing scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
