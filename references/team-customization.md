# 沿用团队模板与设计体系 / Team conventions

用户提供现有模板、设计规范或参考原型即可，不需要理解模板目录、YAML 或内部数量。先从当前上下文、项目文件和已有绑定查找已确认的资料；只有关键资料确实缺失且影响当前输出时才询问，不重复确认已定偏好。已有成品直接修改，不重新初始化。只在需要以后复用时，由 Agent 维护下面的轻量绑定。

## 原件在哪里，谁说了算

模板、组件规范、CSS、交互说明和参考界面保存在团队或项目目录，不能放进 skill 安装目录。原文件是权威，Agent 记忆只帮助找到它们；每次工作重新读取相关文件，不能只依赖对话摘要。本文工具只读取本地文件，不下载、不运行资料里的命令，也不把私人内容打进公共包。

换模板前后按同一业务任务核对已定决定、待决及其影响、权限、状态、异常和验收是否保留。沿用稳定编号或维护明确映射；GAP 数减少不代表内容更完整。缺项补回所属模块，不以另加 DEC/UNK/AC 专章代替内容保真。

业务决定优先级：本次明确约定 → 项目约定 → 团队默认 → skill 兜底。不同原件对业务规则有实质冲突时，就相应范围澄清，不能用模板优先级替代业务授权。沿用模板骨架，必要条件就近补入模块；不为迁就内置章节重排已有 PRD。

## Agent 使用的三个轻量操作

以下命令中的路径由 Agent 按实际资料填写；普通用户只需说“以后沿用这个模板和这些设计规范”。`--project` 是项目目录，也可指向多个项目共同的父目录。资源参数相对执行命令时的当前目录解析。

```sh
python scripts/ai_delivery_spec_cli.py bind-team --project /work/team --template-file /work/team/需求模板.docx --design-file /work/team/设计规范.md --interaction-file /work/team/交互规范.md
python scripts/ai_delivery_spec_cli.py show-team --project /work/team/project-a
python scripts/ai_delivery_spec_cli.py init-prd --project /work/team/project-a
```

- `bind-team` 只写目标目录的 `.ads-profile.json`，存原件路径，不复制正文。后续只改指定项，其他绑定保留；`--design-file`、`--interaction-file` 可重复，设置时替换该类清单。`--clear-template`、`--clear-design`、`--clear-interaction` 明确停用该类继承项；`--clear-team` 去掉显式团队链接，不取消父目录的继承。
- `show-team` 逐层读取父目录到当前项目的绑定，并展开显式团队链接；最近项目的同项覆盖父目录默认。输出原始文件路径及声明位置，Agent 据此读取模板、设计和交互资料。材料缺失、绑定格式不支持或循环引用会指出文件并停止，不悄悄换成官方模板。
- `init-prd` 只创建一份模板副本。MD 默认完整沿用团队文本；DOCX 原字节复制以保留原格式。返回 `template_only`，并不表示已经编写需求或完成 Word 排版验收。已有输出默认保持原样；`--force` 只在确实要重建输出时使用，永远不能覆盖原模板。

不在同一父目录的项目，显式链接团队目录一次：

```sh
python scripts/ai_delivery_spec_cli.py bind-team --project /other/project-b --team /work/team
```

同项目的新对话读取已有绑定；同父目录的新项目继承父目录默认。其他目录的新项目必须显式链接，没有机器全局隐式设置。`init-prd --template-file /path/本次模板.md` 只覆盖本次模板，不修改团队默认；`--profile` 可显式读取另一绑定文件。解析顺序为父目录 → 当前项目 → 显式 profile → 本次模板。绑定中路径相对其声明文件，因此整体移动共同目录后仍可解析；跨磁盘保留绝对路径，移动后需重新绑定。

团队 Markdown 只有明确写了 `<!-- extends: unified-requirement-prd-template.md -->` 才按同名二级标题扩展内置骨架，否则全量采用。Word 不做自动转 Markdown；用宿主文档工具编辑副本，保留模板的段落及字符直接格式，不能只比对样式定义文件。渲染后对照封面、表格、页眉页脚和实际目录；目录域存在或“打开后更新”提示不等于已形成可传阅导航。旧 `init-requirements --custom-root … --template …` 仍是显式创建机器交接工作区的高级入口，不用于普通模板导入。

## 设计资源怎样真正生效

绑定只解决定位，不等于自动应用。生成或修改原型前，Agent 读取 `show-team` 返回的设计与交互文件，确认需要沿用的导航、组件、字号间距、表单反馈和浮层方式。参考原型中的业务数据和权限不是默认新需求。完成后实际打开受影响页面、弹窗及关键交互，对照原规范验证；不以“已绑定 CSS 路径”宣称符合团队设计。

## 升级和隐私

升级替换 skill 核心目录，不触碰外部团队原件或项目绑定。更新后重新运行 `show-team`，核对文件可读，再用一个真实输出确认模板和设计仍被消费。此约定不承诺任意宿主安装器都保留任意目录；若宿主重建整个工作区，团队仍应有自己的文件保管或版本管理。绑定包含内部路径，不默认提交公共仓库；按用户实际共享范围管理，不自动修改项目的 Git 策略。

## English quick contract

Keep authoritative team files outside the installed skill. The agent maintains optional `.ads-profile.json` pointers; users provide their existing documents and design references, not YAML. `bind-team` records pointers, `show-team` resolves inherited resources, and `init-prd` makes only one template copy. Existing output is preserved unless explicitly replaced; DOCX copying does not author a PRD or prove rendered quality. Relative paths are based on the declaring profile, and missing or cyclic bindings fail visibly. Ordinary projects do not need the formal `init-requirements` workspace. Read and apply the actual resources before authoring; verify representative pages and interactions afterward. Upgrade the core separately and re-resolve the external references. A project elsewhere needs its own explicit link; there is no hidden global team registry.
