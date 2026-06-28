#!/usr/bin/env python3
"""Simulate AI+Data product delivery paths for ai-delivery-spec.

The harness is intentionally small and deterministic. It verifies that the
skill can support Chinese/English Human-First PRDs, Chinese AI-Coding PRDs,
bad-output rejection, lifecycle entry points, and ontology/data-agent coverage.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


def run(cmd: list[str], *, expect_success: bool = True) -> str:
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    if expect_success and result.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(cmd)}\n{output}")
    if not expect_success and result.returncode == 0:
        raise AssertionError(f"command unexpectedly passed: {' '.join(cmd)}\n{output}")
    return output


def require_markers(name: str, text: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise AssertionError(f"{name} missing markers: {', '.join(missing)}")


ZH_FRR = """
# AI+Data 平台 Human-First PRD 样例

## 阶段一 需求规划

目标是让监管人员在一个可信数据平台中完成数据接入、治理、分析、智能问数和任务派发。

## 阶段二 IA 与原型锁定

数据源管理、治理目录、语义本体、ChatBI、Data Agent 控制台进入本期范围。

## 阶段三 完整功能需求记录

### M01-F01 建立数据源接入

#### §1 业务场景
数据工程师在接入新业务系统时，需要登记数据源、测试连接、预览 schema，并生成同步任务，结果是数据源进入待治理目录。
#### §2 角色与场景
数据工程师负责接入，治理负责人负责审核，业务负责人确认用途。
#### §3 入口与前置条件
入口为数据源管理页；前置条件是具备接入权限、凭证负责人和业务用途。
#### §4 页面、区域与可见状态
页面包含连接器列表、凭证抽屉、schema 预览区、同步历史区，状态包括草稿、连接中、失败、已接入。
#### §5 字段、字典与校验
字段包括数据源名称、类型、凭证负责人、同步频率、schema 版本、敏感级别和失败隔离策略。
#### §6 编号交互流程
1. 用户点击 data-action connect-source 后，系统测试连接并展示 schema 预览；失败时进入异常队列。
#### §7 操作与规则
保存草稿、测试连接、提交审核、发布同步任务均需要幂等请求号和审计记录。
#### §8 业务规则、计算与口径
BR-M01-F01-01：未完成分级分类的数据源不得进入 ChatBI 和 Data Agent 可用范围。
#### §9 状态、按钮与生命周期行为
草稿可测试连接；连接成功可提交审核；审核通过进入同步中；失败可重试或隔离。
#### §10 权限与数据范围
数据工程师只能管理自己负责的数据源；治理负责人可查看血缘和敏感字段；普通分析用户不可见凭证。
#### §11 异常、降级与恢复
连接超时保留草稿；schema 变化触发影响分析；同步失败标记下游数据新鲜度风险。
#### §12 通知、审计与依赖
SchemaChanged、DataSourceConnected、IngestionFailed 事件写入审计并通知治理负责人。
#### §13 数据、AI 与算法契约
契约覆盖多源接入、清洗质量、治理目录、湖仓存储、语义本体、ChatBI、Data Agent 工具范围和人工门禁。
#### §14 功能级非功能需求
连接测试、schema 预览、权限校验、审计写入和失败重试需要有可观测日志。
#### §15 前端后端QA交接说明
前端验证连接状态和错误提示；后端验证凭证、幂等、审计、权限；QA 覆盖失败重试和越权。
#### §16 验收与追溯
AC-M01-F01-001：给定用户具备接入权限，当提交有效数据源时，则系统创建同步任务、登记目录资产并写入审计。

## 阶段四 评审与交付计划

任务按数据源接入、治理目录、语义本体、ChatBI、Data Agent 控制台拆分。

## 阶段五 测试与验收

验收覆盖接入、清洗、治理、检索、语义、本体、智能问数和智能体写入拦截。

## 阶段六 上线与复盘

观察数据新鲜度、问数成功率、拒答准确率、越权拦截率和洞察采纳率。
"""


EN_FRR = """
# AI Data Platform Human-First PRD Sample

## Stage 1 Requirement Planning

The product helps analysts use governed data sources, semantic models, ChatBI, and data agents without bypassing security.

## Stage 2 IA And Prototype Lock

The release includes source onboarding, catalog governance, semantic modeling, ontology actions, ChatBI, and the data agent console.

## Stage 3 Complete Functional Requirement Records

### M01-F01 Connect Data Source

#### §1 Business Scenario
The data engineer connects a source system, previews schema, and creates a governed sync job for downstream analytics.
#### §2 Roles And Scenario
The data engineer initiates; the governance owner reviews; analysts consume only certified assets.
#### §3 Entry And Preconditions
Entry is the source management page; credential owner and business purpose are required.
#### §4 Pages, Regions, And Visible States
The page includes connector list, credential drawer, schema preview, and sync history with draft, syncing, failed, and active states.
#### §5 Fields, Dictionaries, And Validation
Fields include source name, connector type, schema version, cadence, credential owner, sensitivity, and quarantine rule.
#### §6 Numbered Interaction Flow
1. The user clicks data-action connect-source; the system tests the connection, previews schema, and creates an audit trace.
#### §7 Actions And Operation Rules
Save draft, test connection, submit review, and publish sync are idempotent and audited.
#### §8 Business Rules, Calculations, And Calibers
BR-M01-F01-01: uncertified sources cannot be used by ChatBI or data agents.
#### §9 State, Button, And Lifecycle Behavior
draft -> connected -> syncing -> active; failed sync can retry or quarantine.
#### §10 Permissions And Data Scope
Engineers manage owned sources; governance owners inspect lineage; analysts cannot view credentials.
#### §11 Exceptions, Fallback, And Recovery
Timeout preserves draft; schema drift triggers impact analysis; failed sync marks downstream freshness risk.
#### §12 Notifications, Audit, And Dependencies
DataSourceConnected, SchemaChanged, and IngestionFailed events are audited.
#### §13 Data, AI, And Algorithm Contract
The function covers ingestion, quality, catalog, lakehouse storage, semantic model, ontology, ChatBI, data agent tool scope, and human gate.
#### §14 Function-Level NFR
Connection testing, schema preview, permission, audit, and retry must be observable.
#### §15 Frontend / Backend / QA Handoff Notes
Frontend covers states; backend covers credentials and idempotency; QA covers retry and overreach.
#### §16 Acceptance And Traceability
AC-M01-F01-001: Given valid permission and credential, when the user connects a source, then the system creates a sync job and catalog asset.
"""


ZH_AI_CODING = """
# AI+Data 平台 AI-Coding PRD 样例

## 第一部分 人类可读基础层

### M01-F01 建立数据源接入

#### §1 业务场景
数据工程师接入多源数据，系统生成可治理、可检索、可供 ChatBI 使用的数据资产。
#### §2 角色与场景
数据工程师提交，治理负责人审核，分析师消费。
#### §3 入口与前置条件
入口为数据源管理页，前置条件为凭证、用途和权限。
#### §4 页面、区域与可见状态
页面包括连接器、凭证、schema、同步历史和异常队列。
#### §5 字段、字典与校验
字段包括 source_id、schema_version、sync_mode、sensitivity、owner。
#### §6 编号交互流程
1. 用户触发 connect-source，系统测试连接并登记目录。
#### §7 操作与规则
测试连接、发布同步、禁用数据源均需审计和幂等。
#### §8 业务规则、计算与口径
BR-M01-F01-01：未认证数据不得进入智能问数。
#### §9 状态、按钮与生命周期行为
draft -> connected -> syncing -> active -> degraded。
#### §10 权限与数据范围
继承组织、数据源负责人和敏感字段权限。
#### §11 异常、降级与恢复
失败进入隔离队列，已发布语义模型标记新鲜度风险。
#### §12 通知、审计与依赖
发布 DataSourceConnected、SchemaChanged、IngestionFailed。
#### §13 数据、AI 与算法契约
定义接入、治理、检索、语义本体、ChatBI 和 Data Agent 工具范围。
#### §14 功能级非功能需求
同步失败、权限拦截和智能问数拒答要可观测。
#### §15 前端后端QA交接说明
前端实现状态展示；后端实现权限和同步；QA 验证越权和失败。
#### §16 验收与追溯
AC-M01-F01-001：给定有效凭证，当接入数据源，则生成同步任务、目录资产和审计。

## 第二部分 机器可读扩展层

### 2.1 结构化验收标准

```yaml
ac_structured:
  - id: AC-M01-F01-001
    frr_ref: M01-F01
    given: "用户具备数据源接入权限"
    when: "用户触发 connect-source"
    then: "系统创建同步任务、目录资产和审计记录"
    test_type: integration
    priority: P0
    data_action: connect-source
```
"""


BAD_ZH_HEADING = """
# 坏样例

## Stage 1 Requirement Planning

### M01-F01 数据源接入

#### §1 Business Scenario
这是坏样例。
"""


BAD_AI_CODING = """
# 坏的 AI-Coding PRD

## 第一部分 人类可读基础层

FRR Index Map:

| FRR ID | Name |
|---|---|
| M01-F01 | 数据源接入 |

详见 human-first-prd-template.md。

## 第二部分 机器可读扩展层

### 2.1 结构化验收标准
"""


def main() -> int:
    domain = (REFERENCES / "domain-data-mart.md").read_text(encoding="utf-8")
    advanced = (REFERENCES / "advanced-extensions.md").read_text(encoding="utf-8")
    release = (ROOT / "scripts" / "validate_release_readiness.py").read_text(encoding="utf-8")
    corpus = "\n".join([domain, advanced, release])
    require_markers(
        "AI+Data corpus",
        corpus,
        [
            "multi-source data",
            "Source and acquisition",
            "Processing and cleaning",
            "Governance and catalog",
            "Storage and retrieval",
            "Semantic and ontology",
            "Ontology And Semantic Contract",
            "Data Agent",
            "ChatBI",
            "data_agent_contract",
            "AgentWritebackBlocked",
            "insight-to-action loop",
        ],
    )

    with tempfile.TemporaryDirectory(prefix="ads-ai-data-") as tmp:
        base = Path(tmp)
        files = {
            "zh-human.md": ZH_FRR,
            "en-human.md": EN_FRR,
            "zh-ai-coding.md": ZH_AI_CODING,
            "bad-zh-heading.md": BAD_ZH_HEADING,
            "bad-ai-coding.md": BAD_AI_CODING,
        }
        paths: dict[str, Path] = {}
        for name, content in files.items():
            path = base / name
            path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
            paths[name] = path

        run([sys.executable, "scripts/validate_prd_quality.py", str(paths["zh-human.md"]), "--target-language", "zh"])
        run([sys.executable, "scripts/validate_prd_quality.py", str(paths["en-human.md"]), "--target-language", "en"])
        run([sys.executable, "scripts/validate_prd_quality.py", str(paths["zh-ai-coding.md"]), "--target-language", "zh"])
        run([sys.executable, "scripts/validate_prd_quality.py", str(paths["bad-zh-heading.md"]), "--target-language", "zh"], expect_success=False)
        bad_ai_output = run([sys.executable, "scripts/validate_prd_quality.py", str(paths["bad-ai-coding.md"]), "--target-language", "zh"], expect_success=False)
        if "FRR_INLINE_GAP" not in bad_ai_output and "FRR_COMPLETENESS_GAP" not in bad_ai_output:
            raise AssertionError("bad AI-Coding sample failed, but not for inline/completeness gap")

    print("PASS: AI+Data product, ontology, ChatBI, Data Agent, bilingual PRD, and AI-Coding simulations passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
