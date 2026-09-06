# 决策记录：{议题}

复用现有 PRD、变更单或评审记录中的 DEC 即可；本文件只供确有独立记录需要时使用。

| ID | 建议/决定及理由 | 证据与适用范围 | 状态 | 有权决定者与授权来源 | 复议条件 |
|---|---|---|---|---|---|
| DEC-{稳定标识} | {采取/暂缓/不做/继续验证及理由} | {实际证据；受影响范围} | proposed | {尚未决定时留空，不填“已确认”} | {会改变决定的新证据/到期条件} |

建议完成本身可以是当前任务的成功结果，但不会自动将需求设为 rejected/deferred/cancelled。
用户已明确作出的范围内决定直接引用，无需再走一轮确认。

机器声明（只在需要自动检查时使用；不要与上表重复维护）：

```yaml
disposition:
  id: DEC-EXAMPLE
  outcome: defer
  status: proposed
  reason: 缺少能区分方案收益的观察
  scope_refs: [REQ-EXAMPLE]
  source_refs: [SRC-EXAMPLE]
  revisit_when: 最小验证结果可用
# confirmed 时还需 actor 和实际授权 source_refs；gate PASS 不构成授权。
```

剩余未知只记录影响范围、阻断阶段和解除证据；可继续的工作照常交付。
