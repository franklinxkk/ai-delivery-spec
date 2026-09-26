# 可操作原型

按任务读取业务规格与存量基线。指定单 HTML 就交单 HTML；编辑时可分本地 CSS/JS/数据再合成。保留既有布局、密度、组件和代表数据，只有实际需要才改视觉方向。

## 范围与路径

一句话要原型仍须交原型；明确小改直接做。缺决定只限制依赖部分；评审默认分析，修改按授权执行。

存量先盘点本次页面、角色/入口、动作及最终处理器、状态、实体/字段/指标、权威源与 Mock 边界。大文件先索引再按路径读；区分观察、推断和目标。机器盘点用 `scripts/extract_interaction_ledger.py` 或 [Stage 0 模板](templates/stage0-inventory-template.yaml)；跨文件用 CLI `plan-context` 选范围，轻改只需简短盘点。

关键链核对上一步对象、状态、版本、身份能否进入下一入口、通过守卫；失败/退回须有恢复入口。按钮各自可点不证明闭环。核对最终生效处理器，避免后面重定义覆盖前面。

## 产品与评审

默认可操作产品态。双态、评审抽屉或逐项评审按 [review-workspace.md](review-workspace.md)，可用其中构建工具拆分已验证样例；先完成业务主链与就近说明，再组装机器映射。普通演示不额外询问双态偏好。

两态共用产品页面、状态、动作；评审选择/高亮/展开不得改业务数据。业务审批与需求评审分别建模。主阅读面说业务，稳定 ID、枚举和技术追溯收起。无 UI 的系统规则不伪造按钮；候选不自动成为正式点。辅助评审功能仅启用时承担对应合同。

## 交互约定

| 属性 | 机器约定 |
|---|---|
| `data-action` | `ACT-<DOMAIN>-<NAME>`；纯界面用 `UIACT-*`，评审用 `UIACT-REVIEW-*`；后缀仅字母、数字、连字符，禁止下划线 |
| `data-testid` | 页面 `page-VIEW-*`，浮层 `modal-MODAL-*` / `drawer-DRAWER-*`，区域 `region-REG-*`；稳定且当前 DOM 唯一 |
| `data-metric` | `METRIC-*` 按业务含义分配；重复展示须同口径和 `data-metric-label` |

每个业务动作须有真实处理器、允许条件、结果和失败反馈。普通导航不强绑业务 AC。JS 模板保留完整字面量 `data-action`，不能删除锚点规避检查；静态候选可枚举不代表运行时可达，须从真实入口打开验证。

- 页面状态、按钮权限、筛选、计数和下游读同一业务事实；跨角色/刷新按约定持久范围实现，公开 Mock 边界。
- 字段按必要的必填、格式、依赖、重复、并发校验；失败保留输入并给下一动作。空、错、禁用、加载、成功须实际可达。空零、陈旧、部分数据按已决口径区分。
- 优先事件委托和 `data-*` 参数；父处理器排除输入控件，需保留光标时不要整片重建。浮层带当前对象，只由真实业务入口打开。
- 外部 iframe 仅用于真实集成，说明来源/信任边界/失败退路；可打开不等于集成验证。

未决在评审层引用原 UNK 和影响；产品只实现已授权边界，不代定冻结指标、取最新或自动补偿。负责人缺失写未指定。

## 验证与完成

从源范围反查角色、页面/动作、状态、数据和视觉；已有 PAGE-CONTRACT 可作范围输入。逐项有落点或已授权取消，不能以已画 marker 自定分母。抽样不等于缩减交付。删除已批准功能时同步清理入口/处理器，在现有变更记录注明来源；没有额外“原型锁”义务。

跨模块主链、受守卫状态、多系统数据流分别按需画最小流程/状态/数据图，与正文及运行对象一致；简单 CRUD 不堆图。

检查脚本语法、关键业务链及失败恢复；浏览器核对入口/浮层/返回、状态恢复和常用尺寸。marker 不占业务 Grid/Flex 槽位、不挡按钮；动态观察须收敛。没有浏览器则保留未验证，不能称已验收。

```powershell
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype new.html --prototype-baseline old.html
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype review.html --prd PRD.md --stage specify --require-review-workspace --format json --diagnostics full
python scripts/scan_prototype_css.py app.html
```

评审交付显式带 `--require-review-workspace`；PRD/原型基线按实际传入。R* 是评审使用方式，L0–L4 仅为旧锚点兼容强度，不决定篇幅或风险。单 HTML 未附 IA YAML 时跳过 IA 侧车校验，须说明覆盖边界；不凭此缺侧车判业务不完整。长期机器协作才用 [context.md](context.md) 的 handoff。
