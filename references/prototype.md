# 可操作原型

按任务读取业务规格与存量基线。指定单 HTML 就交单 HTML；编辑时可分本地 CSS/JS/数据再合成。保留既有布局、密度、组件和代表数据，只有实际需要才改视觉方向。

## 范围与路径

按实际授权交付，缺决定只限制依赖部分。

存量盘点本次页面、角色/入口、最终处理器、状态、实体/字段/指标、权威源与 Mock 边界。大文件先索引再按路径读。需要机器盘点时用 `scripts/extract_interaction_ledger.py` 或 [Stage 0 模板](templates/stage0-inventory-template.yaml)，轻改只需简短盘点。

关键链核对对象、状态、版本和身份能否接续并通过守卫，失败有恢复入口。配置平台按[配置产生行为](specify.md#接收者冷读与行为验证)验证。查最终处理器，防后定义覆盖前者。

## 产品与评审

默认可操作产品态。双态按 [review-workspace.md](review-workspace.md)；先完成业务主链与就近说明，再组装机器映射。普通演示不额外询问双态偏好。

两态共用产品页面、状态、动作；评审选择/高亮/展开不得改业务数据。业务审批与需求评审分别建模。主阅读面说业务，稳定 ID、枚举和技术追溯收起。无 UI 的系统规则不伪造按钮；候选不自动成为正式点。辅助评审功能仅启用时承担对应合同。

## 交互约定

先按用户任务排布：筛选与主动作、列表、当前对象详情及编辑；非用户说明放需求或评审层。沿用设计体系的主次按钮、状态标记和必填提示，在常用宽度核对换行、宽表与弹层，不把某个产品的尺寸或颜色变成通用规则。

字段用一份定义对应新增/编辑/列表/详情/筛选及已有导出：输入字段有维护入口，派生字段写来源而非强加输入框。依赖选择先选来源再选有效字段，切换来源清失效引用、保留有效输入。节点配置须能用真实上游输出；名称相同不等于字段身份相同。

| 属性 | 机器约定 |
|---|---|
| `data-action` | `ACT-<DOMAIN>-<NAME>`；纯界面用 `UIACT-*`，评审用 `UIACT-REVIEW-*`；后缀仅字母、数字、连字符，禁止下划线 |
| `data-testid` | 页面 `page-VIEW-*`，浮层 `modal-MODAL-*` / `drawer-DRAWER-*`，区域 `region-REG-*`；稳定且当前 DOM 唯一 |
| `data-metric` | `METRIC-*` 按业务含义分配；重复展示须同口径和 `data-metric-label` |

每个业务动作须有真实处理器、允许条件、结果和失败反馈。普通导航不强绑业务 AC。JS 模板保留完整字面量 `data-action`，不能删除锚点规避检查；静态候选可枚举不代表运行时可达，须从真实入口打开验证。

- 同一动作的行内、详情、批量等实际入口按相同对象/状态/身份核对守卫与副作用；差异须有业务依据。修改字段后立即点击提交，检查失焦/重绘是否吞掉第一次点击；再关闭重开并读下游，防局部成功被另一缓存覆盖。记录实际写入对象，公开 Mock 边界。
- 字段按必要的必填、格式、依赖、重复、并发校验；失败保留输入并给下一动作。空、错、禁用、加载、成功须实际可达。空零、陈旧、部分数据按已决口径区分。
- 优先事件委托和 `data-*` 参数；父处理器排除输入控件，需保留光标时不要整片重建。浮层带当前对象，只由真实业务入口打开。
- 外部 iframe 仅用于真实集成，说明来源/信任边界/失败退路；可打开不等于集成验证。

未决在评审层引用原 UNK 和影响；产品只实现已授权边界，不代定冻结指标、取最新或自动补偿。负责人缺失写未指定。

## 验证与完成

按源范围反查角色、页面/动作、状态、数据及视觉；可用已有 PAGE-CONTRACT。逐项有落点或授权取消，不以 marker 自定分母；抽样不缩减交付。获准删除功能时同步入口/处理器并记录依据，不额外要求“原型锁”。

跨模块主链、受守卫状态、多系统数据流分别按需画最小流程/状态/数据图，与正文及运行对象一致；简单 CRUD 不堆图。

检查脚本语法、关键业务链及失败恢复；浏览器从真实按钮/拖拽入口核对浮层/返回、状态恢复和常用尺寸。直接调用处理器不算点击或拖拽验证。marker 不占业务 Grid/Flex 槽位、不挡按钮；动态观察须收敛。没有浏览器则保留未验证，不能称已验收。

```powershell
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype new.html --prototype-baseline old.html
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype review.html --prd PRD.md --stage specify --require-review-workspace --format json --diagnostics full
python scripts/scan_prototype_css.py app.html
```

评审交付显式带 `--require-review-workspace`；PRD/原型基线按实际传入。R* 是评审使用方式，L0–L4 仅为旧锚点兼容强度，不决定篇幅或风险。单 HTML 未附 IA YAML 时跳过 IA 侧车校验，须说明覆盖边界；不凭此缺侧车判业务不完整。长期机器协作才用 [context.md](context.md) 的 handoff。
