---
artifact: solution_sketch
stage: explore
schema_version: 5.4.0
version: "0.1"
status: draft
document_language: zh-CN
project_id: PROJECT-EXAMPLE
resume_context:
  completed_stages: [frame]
  # 续跑对象示例（全新任务保持空数组）：
  # - path: prior/problem-brief.md
  #   sha256: "0000000000000000000000000000000000000000000000000000000000000000"
  #   stage: frame
  prior_artifacts: []
  open_threads: []
  next_stage_options: [intake, frame]
---

# 方案探索：{问题名称}

<!-- ADS:problem_ref -->
## 问题与约束

- 问题引用：`SRC-*` / 问题简报
- 不可突破的约束：{权限、法规、成本、时间或现状}

<!-- ADS:options -->
## 选项比较

<!-- ADS:option OPT-001 -->
### OPT-001：{方案一}

- 预期结果：{结果}
- 代价/风险：{代价与负迁移}
- 最小验证：{不开发完整系统也能验证的方法}

<!-- ADS:option OPT-002 -->
### OPT-002：{方案二}

- 预期结果：{结果}
- 代价/风险：{代价与负迁移}
- 最小验证：{方法}

<!-- ADS:opt_out -->
### OPT-000：不做、延后或维持现状

- 可接受条件：{什么情况下不值得做}
- 风险：{继续现状的代价}

<!-- ADS:assumptions -->
## 可证伪假设

| ID | 假设 | 影响选项 | 验证方法 | 责任人 | 状态 |
|---|---|---|---|---|---|
| `ASM-001` | {假设} | OPT-001 | {验证} | {责任人} | 未验证（`untested`） |

<!-- ADS:recommendation -->
## 推荐与取舍

推荐{选项}，因为{证据}；放弃{选项}，因为{代价}。该结论仍受`ASM-*`约束。

<!-- ADS:next_validation -->
## 下一验证与停止条件

- 下一步：{原型/访谈/数据分析/准入}
- 继续条件：{信号}
- 停止或回退条件：{信号}
