# 排错与使用边界

遇到工具错误、范围疑问或恢复问题时按需读取。不要为已经顺利完成的小改增加检查清单。

| 现象 | 处理 |
|---|---|
| 清晰小改被要求长 PRD | 使用当前范围；artifact_mode 与风险分开，旧等级只作呈现提示。无需补固定章节。 |
| 用户决定又变成待批准 | 核对授权来源与适用范围；旧文档未同步不撤销新决定。 |
| 不同来源冲突 | 按议题核对权威、版本和授权；记录冲突，不能按文件名新旧自动选。 |
| 指标或权限缺口 | 保持未定，只阻断依赖项；不要借保守默认决定业务政策。 |
| YAML 元数据报错 | 按报错文件和行列修括号、引号、缩进或分隔线；尚未检查业务内容，不为语法错误补需求。 |
| 文件或依赖缺失 | 使用本次输出的绝对路径和当前 Python 解释器命令；确认输入存在后重跑，未读取不能称检查完成。 |
| Gate 报 GAP | 看具体 ref 和未证明事项；可能是定位/证据不足，不能一律理解为业务缺失。 |
| 局部 gate 被其他模块影响 | 使用 scope-ref；明确归属的正文发现可排除，无归属疑点仍待核实。不要通过删内容或降低等级隐藏缺口。 |
| 语义评阅显示 pass | 脚本只检查范围、版本与引用声明；仍需实际读取证据，不能证明签署者身份或全部业务正确。 |
| 原型可点击但主链走不通 | 核实对象、状态、版本、身份键与下一守卫；检查最终生效处理器，而非只数按钮。 |
| 影响清单过长 | 查看每项依赖路径、实际消费者及旧对象；图可达先是候选，核实和修改授权分开。 |
| 影响清单太短 | 看深度截断、未知引用、缺失种子和未盘点消费者；空清单不证明无影响。 |
| 不知道该选哪个模板 | 清晰小改直接回填；独立小需求用需求卡；复杂模块用正式PRD。过程记录与机器合同只在实际需要时启用，不一次交付所有模板。 |
| 检查规则变成了一堆表单项 | 规则必须说清不等于可配置。固定口径写默认行为或只读说明，只有真实用户任务需要调整时才提供输入控件。 |
| 模板校验不过 | 模板含占位符，本来不是项目事实；只填实际已知且当前目标必要的字段。 |
| 任务中断 | 从最新产物/检查点核实版本，保留未完成范围，继续当前目标。 |

进阶内容按问题进入：[业务判断与未知](discover.md)、[团队模板与设计原件](team-customization.md)、[评审抽屉与图示](review-workspace.md)、[变更与验收证据](change-acceptance.md)、[工具及输入示例](stages.md)。普通任务无需全部阅读。

## 命令边界

优先看实际工具帮助，不照搬旧版退出码：

```powershell
python scripts/ai_delivery_spec_cli.py --help
python scripts/ai_delivery_spec_cli.py gate --help
python scripts/ai_delivery_spec_cli.py explain-finding SPEC-REVIEW-EVIDENCE
```

PRD gate 的 PASS 是确定性声明检查结果；GAP 为待评阅/待证据，BLOCK 为发现的合同矛盾或当前阶段阻断。旧专业工具仍按其 Schema 执行。默认不运行 full/handoff；需要该合同才准备相应输入。

机器 JSON 中的原始 code、artifact、ref 和技术明细用于定位。无法识别的错误不要伪称已知修复；保留命令、输入版本、stderr 和退出码。修复后重跑受影响检查。

若门禁误认格式或环境不可用，保留失败证据，按同一规则人工核对受影响项并修工具，不删除业务内容换绿灯。可继续独立的语义和运行验证；静态失败与业务结论分别报告。prototype PASS 不执行按钮、接口或 SQL，也不证明导出文件存在、指标含义正确、跨产物语义一致；用可重置数据执行主链、关键拒绝与恢复，并比对真实结果。不要仅增加 data-assert 或 ARUN 标签冒充运行过。

UNK 表支持 `| ID | 状态 | 关闭依据 |`：`UNK-X | closed | DEC-X`；粗体与行内代码只是排版，`决议 / 来源` 为关闭依据别名。`closed` 无依据仍阻断；散文提到 DEC 不自动证明它解决了另一个 UNK。YAML/JSON 附录的显式 `*_refs` 参与引用扫描，任意程序示例及外部路径不当成本地定义。工具不证明 DEC 授权真伪或任意散文闭环。

本地 Python 缺 pyyaml/jsonschema 时按 scripts/requirements.txt 安装。Windows 文本解码异常可显式使用 `python -X utf8`；不要重编码原始客户材料来迎合脚本默认编码。

## 兼容与升级

旧调用可手动执行 `python scripts/validators/validate_prd_quality.py <PRD.md>`，它转调 `validate_unified_prd.py`，二者都使用当前 PRD gate，不另设判断标准。默认检查基线阶段；草稿可传 `--stage specify`。新调用优先使用 `gate --profile prd`。

手动执行 `python scripts/validators/validate_coding_agent_contract.py <PRD.md>` 默认采用当前 PRD 检查；只有明确复核历史附录合同时追加 `--legacy --level L2`。`--level L2` 单独使用不会恢复旧章节数/表格数门禁，`--domain-rules` 仅用于显式 legacy 模式。通常直接使用 `gate --profile prd` 即可，不必两套都跑。

5.4.x 工件保留已批准业务事实。新版本不保证旧标题门禁、旧 triage 结果键或逐阶段脚手架的行为兼容。调用专业评审/Truth/handoff 时保留实际 Schema 版本，不把版本号改成 5.5.0 就当作完成迁移。

高级 Schema 的结构通过不证明运行效果。外部链接存在、文件哈希匹配和签名字段完整也不能替代实际业务授权。详见 [当前工具](stages.md)、[变更与验收](change-acceptance.md)。

## 契约样例校验

已有机器契约需联调时，按需执行 `python scripts/ai_delivery_spec_cli.py check-examples --input cases.yaml --format json`。复用权威Schema及正反样例，核对拒绝原因；不自动加入PRD gate。输入直接引用同目录的现有 JSON Schema 与正反例；退出码 0=符合预期，1=与预期不符，2=输入/校验环境无效。它不证明自然语言一致性或运行行为，工具失败不能当合法拒绝。

示例 `cases.yaml`（只有机器契约联调需要，不是 PRD 必填项）：

```yaml
contracts:
  - id: name-required
    schema: schema.json
    cases:
      - {id: valid-name, instance: valid.json, valid: true}
      - id: missing-name
        instance: invalid.json
        valid: false
        error: {keyword: required, instance_path: ""}
```

`schema.json` 声明 JSON Schema 2020-12、对象类型及必填 `name`；`valid.json` 为 `{"name":"工单"}`，`invalid.json` 为 `{}`。负例因指定约束被拒绝才算通过，读不到文件不算。路径在输入目录内解析，不访问远程 Schema。

## 原型机器锚点与诊断

| 属性 | 机器约定 |
|---|---|
| `data-action` | `ACT-<DOMAIN>-<NAME>`；纯界面用 `UIACT-*`，评审用 `UIACT-REVIEW-*`；后缀仅字母、数字、连字符，禁止下划线 |
| `data-testid` | 页面 `page-VIEW-*`，浮层 `modal-MODAL-*` / `drawer-DRAWER-*`，区域 `region-REG-*`；稳定且当前 DOM 唯一 |
| `data-metric` | `METRIC-*` 按业务含义分配；重复展示须同口径和 `data-metric-label` |

```powershell
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype review.html --prd PRD.md --stage specify --require-review-workspace --format json --diagnostics full
python scripts/scan_prototype_css.py app.html
```

正式评审带 `--require-review-workspace` 和实际基线。R*表示评审方式，旧L0–L4不决定篇幅或风险。无IA侧车仅表示未查。机器交接见 [context.md](context.md)。
