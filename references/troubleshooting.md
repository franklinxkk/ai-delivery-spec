# 排障、恢复与反模式 / Troubleshooting, Recovery And Anti-Patterns

仅在命令失败、大任务中断或用户询问阻断原因时加载本文件。Ultra-Light 或 Standard
顺利执行时不要加载，避免无谓占用上下文。

## 三分钟恢复

1. 保留失败工件和原命令，不要先批量改动。
2. 读取第一个 Finding 的错误码和引用，一次只修一个有边界的合同问题。
3. 执行：

    python scripts/ai_delivery_spec_cli.py explain-finding <CODE>

4. 按提示修复对应合同；门禁从不授权编造业务值。
5. 复制门禁输出的 RETRY 原命令重跑。
6. 大项目中断时先检查快照：

    python scripts/ai_delivery_spec_cli.py resume

只继续报告中的阶段和稳定 ID 切片。若快照发现版本、锚点或仓库漂移，必须建立经批准的
新快照，不能静默续跑。

## 常见症状

| 症状 | 常见原因 | 修复方法 |
|---|---|---|
| ModuleNotFoundError | 首次运行未安装 PyYAML/jsonschema | `python -m pip install -r scripts/requirements.txt`；Windows 可用 `py -3 -m pip ...` |
| GATE-MISSING-INPUT | 门禁 profile 与传入工件不一致 | 补充提示的 PRD/登记表/原型路径，或选择更窄的 profile |
| REQ-PARSE / REQ-SCHEMA | YAML 无效或生命周期字段缺失 | 按 requirement-register 模板修复准确 schema 路径 |
| PRD-STRUCTURE / PRD-TOO-THIN | 有标题但缺少可施工的局部合同 | 补齐对应正文和工程附录，禁止添加空标题骗过门禁 |
| PROTO-NO-PAGE-ANCHOR | 页面无法追溯到 `VIEW-*` | 添加唯一的 `data-testid="page-VIEW-*"` 根节点 |
| PROTO-NO-REGION-ANCHOR | L3 复杂页没有可测试区域 | 为有业务意义的区域添加 `data-testid="region-REG-*"` |
| PROTO-UNHANDLED-ACTION | 按钮没有分发逻辑或可见结果 | 绑定 `data-action` 处理器，并呈现成功/失败/状态结果 |
| PROTO-DYNAMIC-ANCHOR-CONSTRUCTION | data-* 名称由字符串拼接，无法枚举真实动作 | 在模板源码直接写稳定锚点，再用浏览器证据证明动态控件 |
| PROTO-DEPENDENCY-* | 本地 JS/CSS 缺失、使用绝对路径或越过原型目录 | 将依赖放回原型目录并使用可解析相对路径 |
| PROTO-REMOTE-DEPENDENCY | 原型依赖远程 JS/CSS，静态门禁无法检查 | 冻结为本地依赖，或将未扫描风险保留为 GAP |
| PROTO-BROWSER-EVIDENCE-MISSING | L3/L4 只有静态 PASS，没有逐动作证据 | 在浏览器执行 `data-ac`，记录 ARUN，并用 `--acceptance-run` 重跑 |
| ACCEPTANCE-EVIDENCE-INVALID | ARUN 引用的证据不存在、越界或 `EVD-*` 未登记 | 把文件放在 ARUN 目录内，或在 `evidence_catalog` 登记 URL/相对路径 |
| PRD-P0-UNKNOWN-NOT-STRUCTURED | 开放项只是 REV/自由文本，没有责任人和影响范围 | 使用 `UNK-*` 登记并同步 `open_p0_unknown_ids` |
| PROTO-CSS-* | 全局样式或 `!important` 污染可见性/状态 | 将样式限定到所属组件和显式 `data-state` |
| HANDOFF-XCT-INCOMPLETE | 横切工作包缺少关键运行约束 | 补影响模块、全局不变量、执行点、例外/失败处理和 AC |
| HANDOFF-* | PRD、原型或工作包发生漂移 | 以同一稳定 ID 修复唯一 PRD 基线及所有受影响表面 |
| Product Truth compile stops | 巨型单文件或跨分片引用未闭合 | 保留分片，校验当前片，编译并修复悬空 ID 后续跑 |
| run interrupted or context lost | 没有可见检查点或恢复入口 | 执行 resume，只继续最后有效阶段/ID 切片 |

JSON 输出包含中文原因、修复、示例、RETRY 命令和 `not_proven`，IDE/Coding Agent
无需解析自然语言长文，也不能把静态 PASS 误读成业务完成。

## 精确 ID 与动态锚点迁移 / Exact-ID And Dynamic-Anchor Migration

`PRD-NONEXACT-ID` 表示范围、通配符或组合写法无法追到单个对象。把
`AC-AUDIT-001..003`、`ACT-USER-*` 或 `REQ-ORDER-001/002` 展开为独立 ID，更新正反追溯后
重跑门禁。不得自行补造未知 ID；未确定成员必须登记为有责任人的 `UNK-*`。

动态锚点扫描覆盖以下已知模式：

- `'data-' + 'action'`、`data-'+'action` 等拆分名称；
- `${act}` 等隐藏实际动作集合的模板占位符；
- `setAttribute('data-action', ...)` 或 `dataset.action = ...` 运行时补挂。

这是启发式源码检查，不是完整 JavaScript 语义。发现新模式时应增加最小回归样例。
动态生成控件仍需可检查的静态注册表和浏览器 `ARUN-*`；通过已知模式扫描并不能证明
运行时交互闭环。

## Product Truth 长任务避免死锁

Product Truth 仍是条件能力，只用于受控多投影、反复跨模块变更、血缘、强审计或明确
权威决策；页面、模块或输入数量本身不是充分触发条件。

触发后按以下顺序执行：

1. 每次只写 `00-core.yaml` 或一个 `MOD-*` 分片；
2. 增加下一个分片前先验证当前分片；
3. 编译并修复悬空引用；
4. 保存编译 hash 和当前 ID 切片；
5. 从检查点续跑，禁止让子 Agent 重新生成整个巨型 Product Truth。

编译失败不代表可以删除未知项、捏造目标或放松 schema。必须保留 `UNK/REV`，直到责任人决策。

## 集中 FAQ

**PASS 代表需求业务正确吗？** 不代表。它只证明有边界的静态合同；领域负责人、浏览器
旅程、QA执行和客户验收仍需各自证据。

**为什么 L3 原型静态通过后仍有缺口？** 交互完成需要浏览器证据。提供环境明确、覆盖原型
`data-ac`、证据可解析且已签署的 `ARUN-*`；否则正确结果就是 `REVIEW_COMPLETE_WITH_GAPS`。

**ARUN 为什么还会被阻断？** `pass` 不再只检查证据字段非空。本地文件必须真实存在且不能
越过 ARUN 目录；`EVD-*` 必须通过同一文件的 `evidence_catalog` 解析；接受结论的签署也要有证据。

**应该自动修完所有警告吗？** 不应该。格式问题可机械修复；角色、规则、限值、权限、状态和
验收值必须来自证据或责任人。

**为什么小需求产生了很多工件？** 检查静默路由。单角色、可逆、非监管的局部变化应该走需求卡；
只有影响证据支持时才覆盖 `delivery_shape`。

**为什么很长的 PRD 仍被拒绝？** 长度不等于完整。每个实际页面都要就近具备字段、动作、状态、
指标、异常、数据流和验收链接。

**验证器不可用时能继续吗？** 只能走 execution state 已定义的服务中断和人工批准路径；
不得把验证器不可用当成隐式 PASS。

**如何避免私有规则进入公共仓库？** 执行 `init-custom`。生成目录默认忽略，只加载声明式正则规则；
绑定规则冲突必须由 `DEC-CONFLICT-*` 处理。

## 反模式

- 需求准入或 P0 澄清前生成巨型 Product Truth。
- 因一个悬空引用让子 Agent 重写全部事实源。
- 为骗过门禁而增加空标题、关键词、按钮或 `data-testid`。
- 把静态 PASS 当成领域判断、法律意见、客户签署或生产证据。
- 维护规则不同的“人类版 PRD”和“AI版 PRD”。
- 通过叠加重复处理器、全局 CSS 或 `!important` 修复原型漂移。
- 修改仓库、Skill 版本或来源集合后，未经新检查点批准直接续跑。
