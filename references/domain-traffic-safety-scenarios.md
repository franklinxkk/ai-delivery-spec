# Traffic Safety Scenario Validation Library

Use this file to validate transport supervision, road transport safety, enterprise compliance, reporting, data mart, indicator, and AI analysis/report requirements.

## Scenario Validation Rule

Every product requirement in this domain should be tested against at least three scenario classes:

1. Routine regulatory reporting.
2. Risk/exception handling.
3. Evidence/audit/freeze/reporting.

For each selected scenario, define:

- role;
- trigger;
- data involved;
- operation path;
- state transition;
- evidence/audit requirement;
- output/report;
- permission boundary;
- test case.

## Scenario Library

| Scenario | Roles | Trigger | Required Path | State/Result |
|---|---|---|---|---|
| 安全教育培训月报 | 运管管理员、企业填报员 | 月度统计 | 创建模板/任务 -> 企业补填 -> 管理端查看进度 -> 完成冻结 | ReportTask 填报中/待审核/已完成 |
| 三超一疲劳动态监控 | 运管管理员、企业安全负责人 | 报警处理率低或待处理报警多 | 查看预警指标 -> 下钻企业/车辆 -> 企业说明整改 -> 监管复核 | Alert pending/processing/closed |
| 证照超期整改 | 运管管理员、企业填报员 | 企业/车辆/人员证照即将或已经超期 | 生成超期清单 -> 通知企业 -> 企业提交整改材料 -> 复核 | Rectification pending/submitted/accepted/rejected |
| 重大隐患闭环 | 安全科、企业、监管负责人 | 发现重大隐患 | 登记隐患 -> 分派整改 -> 上传材料 -> 验收 -> 挂牌/销号 | HiddenDanger open/rectifying/verifying/closed |
| 车辆维护保养 | 维修办、企业 | 无年度计划或维护异常 | 汇总异常车辆 -> 企业填报计划/说明 -> 运管确认 | MaintenancePlan missing/submitted/confirmed |
| 事故隐患内部报告奖励 | 企业、运管管理员、财务/领导 | 企业内部上报隐患奖励 | 企业申报 -> 运管审核 -> 奖励确认 -> 归档 | RewardApplication submitted/reviewed/approved/rejected |
| 节假日/恶劣天气应急报送 | 运管管理员、企业 | 临时专项统计 | 快速建表 -> 企业限时填报 -> 催办 -> 汇总上报 | EmergencyReport collecting/submitted/frozen |
| 企业风险画像 | 运管管理员、监管负责人 | 周期风险评估或专项检查 | 聚合培训/证照/隐患/报警 -> 生成风险等级 -> 人工确认 | RiskAssessment draft/confirmed/escalated |
| 智能月报/专题报告 | 监管负责人、文秘 | 月报或专项报告 | 选报告模板 -> 插入指标/知识库/变量 -> AI生成 -> 人审发布 | ReportDraft generated/reviewed/published |
| 执法检查/整改任务 | 运管管理员、执法人员、企业 | 风险高或专项检查 | 创建检查任务 -> 现场/线上反馈 -> 整改 -> 复查 | EnforcementTask assigned/processing/closed |

## Required Story Examples

### Training Monthly Report

User story:
- As a regulator, I need to create a monthly enterprise safety training report from platform indicators and enterprise-supplied remarks, so that I can submit accurate training statistics without repeated collection.

Paths:
- regulator: report list -> create task -> blank/template -> configure columns -> publish -> view enterprise progress -> freeze.
- enterprise: my fill tasks -> open training task -> view readonly system values -> fill remarks/attachments -> submit.

Tests:
- submitted enterprise appears in workbench with filled remarks;
- unsubmitted enterprise can be reminded;
- system fields are readonly for enterprise;
- frozen task exposes snapshot.

### Dynamic Monitoring Alert

User story:
- As a regulator, I need to see enterprises with low alert handling rate and inspect evidence, so that I can urge correction before safety risk escalates.

Paths:
- dashboard/report -> alert indicator -> enterprise drilldown -> vehicle evidence -> remind or create rectification task.

Tests:
- low rate row can drill into enterprise/vehicle evidence;
- batch reminder writes audit;
- closed alert cannot be edited without reopen permission.

### Hidden Danger Closure

User story:
- As safety office staff, I need to track major hidden danger from discovery to acceptance, so that closure evidence is auditable.

Paths:
- hidden danger list -> create/receive danger -> assign enterprise -> enterprise uploads rectification -> regulator accepts/rejects -> snapshot.

Tests:
- reject requires reason;
- accepted danger changes closure metrics;
- snapshot includes evidence and timeline.

## Scenario Review Checklist

- [ ] Does the prototype show both summary and item-level evidence?
- [ ] Can enterprise only see its own records?
- [ ] Does every correction/rejection/freeze action write audit?
- [ ] Does the final report/snapshot lock metric version and source data?
- [ ] Can the same indicator serve reporting, analysis, and AI report evidence?
- [ ] Does AI output have confidence, evidence, and human review before write/publish?
