---
artifact: decision_record
artifact_role: supporting
applicable_stages: [explore, clarify, specify, review, baseline, change]
applies_when: 确需独立记录选择理由与授权时使用；已有模块内决定优先复用。
---

# 决策记录：{议题}

优先复用现有PRD、变更单或评审记录中的DEC；确有独立记录用途时才使用本文件。同一决定只维护一处。

| ID | 建议/决定及理由 | 证据与适用范围 | 状态 | 有权决定者与授权来源 | 复议条件 |
|---|---|---|---|---|---|
| DEC-{稳定标识} | {采取/暂缓/不做/继续验证；已选与未选方案的取舍} | {实际证据与受影响范围} | proposed | {未决定时留空或注明待指定，不填“已确认”} | {会改变决定的新证据/到期条件} |

建议可以是分析任务的完成结果，不自动将需求设为rejected/deferred/cancelled。已获用户授权的范围内决定直接引用，不重复确认。

只记录仍影响当前选择的未知、可继续范围及解除证据；不借退路决定未定政策。需自动检查时按[声明规则](../stages.md)选用已有机器结构，不与本表重复维护。
