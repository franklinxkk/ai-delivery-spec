# Ecosystem Comparison / 社区生态客观化测评

Snapshot / 快照日期: **2026-07-12**

This is a source-traceable, rubric-based comparison of documented capability
coverage. It is not a benchmark of generated-output quality, a popularity
ranking, or proof that one tool is universally better.

本报告是基于统一量表、官方仓库与可检查源码的**客观化、可复核测评**；
它衡量“公开证据中是否有该机制”，不直接证明生成质量、项目成功率或谁全面更好。

## Execution disclosure / 执行环境披露

- User-interface model label / 用户侧界面显示: **GPT-5.6 SOL**.
- Attestation / 证明方式: **user-reported**.
- Independent verification / 独立校验: the repository and its validators
  cannot attest provider-side routing or model identity.
- Machine-readable record / 机器可读记录:
  [`evals/ecosystem-comparison.yaml`](../evals/ecosystem-comparison.yaml).

因此，“GPT-5.6 SOL”是本次执行环境的用户侧显示事实，不被扩写为
仓库可自证的模型性能结论。

## Method / 方法

### Rating vocabulary / 等级语义

| Mark | Meaning / 判定标准 |
|---|---|
| `P` primary / 主能力 | 有一级工作流，且有明确产物、规则、门禁或专属 skill |
| `S` supported / 支持 | 官方文档明确支持，但不是整个体系的主契约 |
| `A` adjacent / 相邻 | 能间接贡献，或需另一工具/产物承担主责 |
| `—` not evidenced / 未取证 | 本次已审核一手资料中未找到足够明确证据，不等于做不到 |

### Dimensions / 维度

1. 产品发现与策略：问题、用户、机会、目标、指标、取舍。
2. 需求澄清与范围：追问、假设、未知、边界、优先级与阻断条件。
3. 业务建模与统一规格：角色、对象、状态、流程、数据、规则与跨产物事实源。
4. 工程交接与 Coding Agent：实施规划、任务切片、仓库感知和代码交付。
5. 验收测试与追溯：验收标准、测试、证据、需求到交付反查。
6. 变更与存量演进：影响分析、兼容、迁移、回归、发布与回滚。
7. 上线、运营、学习与退役：发布准备、指标观测、复盘、迭代和终止。
8. AI 治理与运行风险：权限、数据、评测、人工门禁、降级、观测与审计。
9. Skill 工程质量与可维护性：模块化、渐进加载、校验、测试、版本、文档和发布工程。

Community popularity and platform reach are reported separately and do not
alter these ratings. No total score is calculated because a summed score would
hide whether a tool is optimized for discovery, product truth, or coding.

## Nine-dimension matrix / 九维详细矩阵

| Tool | 发现策略 | 澄清范围 | 业务/统一规格 | 工程/Coding | 验收追溯 | 变更 | 上线/学习/退役 | AI 治理 | Skill 工程 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **AI Delivery Spec 5.0.0** | P | P | P | P | P | P | S | P | P |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | A | S | A | P | S | S | A | A | P |
| [mattpocock requirements chain](https://github.com/mattpocock/skills) | P | P | A | S | S | A | A | A | S |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | P | P | S | S | S | S | P | S | P |
| [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills) | P | P | S | S | S | S | P | A | P |
| [alirezarezvani Product Skills Pack](https://github.com/alirezarezvani/claude-skills) | S | S | A | S | A | A | S | S | S |
| [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) | P | P | S | S | S | A | S | A | P |
| [max4c requirements flow](https://github.com/max4c/skills) | S | P | A | P | P | A | S | A | S |
| [GitHub awesome-copilot PRD](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md) | S | S | A | S | A | A | A | A | P |
| [Digidai/product-manager-skills](https://github.com/Digidai/product-manager-skills) | P | P | S | S | S | A | P | S | S |
| [pratikshadake PM Skills](https://github.com/pratikshadake/claude-product-management-skills) | P | S | A | A | S | A | P | A | S |
| [Superpowers](https://github.com/obra/superpowers) | S | S | A | P | P | S | S | A | P |

### Interpretation / 结果解读

- **AI Delivery Spec 5.0.0** is differentiated by stable-ID Product Truth,
  projection consistency, domain-maturity boundaries, change packages, and
  execution-state gates. Its current weakness is evidence maturity: built-in
  domains remain experimental and launch/learn behavioral runs are incomplete.
- **Spec Kit** and **Superpowers** are stronger downstream composition choices
  when the main job is specification-to-code planning, TDD, implementation, and
  engineering verification; neither is documented as a ToB Product Truth layer.
- **mattpocock** and **max4c** provide the sharpest adversarial clarification
  patterns in this set. max4c additionally documents PRD → tech spec → TDD →
  verification composition; mattpocock's `to-prd` synthesizes available context
  and the broader chain remains intentionally composable.
- **phuryn**, **product-on-purpose**, and **deanpeters** provide broad lifecycle
  PM method libraries. They are especially useful for discovery, strategy,
  workshops, launch, and PM learning; reviewed sources do not show one canonical
  cross-artifact business schema equivalent to Product Truth.
- **Digidai** emphasizes decision pushback, SaaS metrics, reusable PM sprints,
  AI-product craft, and post-launch learning. **pratikshadake** is a compact,
  decision-first set covering discovery, prioritization, readiness, and learning.
- **awesome-copilot PRD** is an accessible PRD entry inside a much larger,
  actively engineered skill catalog; the reviewed PRD source is not a complete
  product lifecycle backbone.
- **alirezarezvani** offers broad multi-agent reach and a large skills catalog.
  Its own [2026 maintainability audit issue](https://github.com/alirezarezvani/claude-skills/issues/655)
  reports substantial legacy-file conformance debt, so this snapshot records
  skill engineering as supported rather than primary despite strong breadth.

## Activity snapshot / 社区活跃信号

GitHub API snapshot on 2026-07-12. Stars/forks aid discovery only; they are
not capability evidence and never change the matrix above.

| Repository | Stars | Forks | Last push |
|---|---:|---:|---|
| obra/superpowers | 252,416 | 22,530 | 2026-07-10 |
| mattpocock/skills | 165,691 | 14,248 | 2026-07-10 |
| github/spec-kit | 119,572 | 10,601 | 2026-07-10 |
| github/awesome-copilot | 36,453 | 4,547 | 2026-07-11 |
| phuryn/pm-skills | 23,514 | 2,492 | 2026-07-03 |
| alirezarezvani/claude-skills | 22,209 | 3,101 | 2026-07-11 |
| deanpeters/Product-Manager-Skills | 5,699 | 704 | 2026-07-08 |
| product-on-purpose/pm-skills | 456 | 59 | 2026-07-07 |
| Digidai/product-manager-skills | 122 | 12 | 2026-04-12 |
| pratikshadake/claude-product-management-skills | 30 | 5 | 2026-02-19 |
| franklinxkk/ai-delivery-spec | 13 | 3 | 2026-07-06 |
| max4c/skills | 6 | 1 | 2026-06-06 |

## Platform reach / 平台可达性

Platform reach is an installation/documentation fact, not a quality score.

- Claude Code has the broadest explicit support across the reviewed projects.
- Codex is explicitly documented by AI Delivery Spec, Spec Kit,
  product-on-purpose, alirezarezvani, deanpeters, Digidai, and Superpowers;
  open-skills-compatible packages may also be installed through the
  [Vercel Labs skills CLI](https://github.com/vercel-labs/skills).
- GitHub Copilot has first-party PRD access through
  [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md)
  and documented cross-agent paths in several libraries.
- WorkBuddy/work-buddy and TRAE are not marked as natively verified for this
  skill in this snapshot. WorkBuddy documentation describes a Claude Code-based
  runtime, while the reviewed TRAE sources did not provide a first-party
  installation proof for this repository. A portable `SKILL.md` suggests a
  possible manual path, not certified compatibility.
- If “WorkBuddy” meant Tencent CodeBuddy, its
  [official skills system](https://www.codebuddy.ai/docs/cli/skills) is a
  separate runtime contract and requires a dedicated adapter/installation test.

## Recommended composition / 按目标组合

| Goal | Evidence-aligned path |
|---|---|
| Fast idea challenge or lightweight PRD | mattpocock, max4c, Digidai, pratikshadake, or AI Delivery Spec Light |
| Broad discovery/strategy workshop | phuryn, product-on-purpose, or deanpeters → approved decisions |
| ToB/ToG multi-role committed delivery | approved decisions → AI Delivery Spec Product Truth and acceptance contracts |
| Spec-driven coding | AI Delivery Spec → GitHub Spec Kit |
| TDD/subagent engineering workflow | AI Delivery Spec → Superpowers or max4c engineering chain |
| Existing-system change | AI Delivery Spec Change Package → chosen engineering workflow |
| Post-launch PM learning | phuryn, product-on-purpose, Digidai, or pratikshadake; sync accepted changes back to Product Truth when used |

## Evidence and limitations / 证据与局限

Primary sources are the linked official repositories and first-party project
documentation. Detailed evidence URLs, platform declarations, activity data,
and every rating are frozen in
[`evals/ecosystem-comparison.yaml`](../evals/ecosystem-comparison.yaml).

- Ratings are documentary coverage judgments, not repeated blind output tests.
- Repository activity can change after the snapshot date.
- A broad repository may contain a capability not surfaced by its primary
  documentation; such cases remain `not_evidenced` or `adjacent` until cited.
- No directly comparable Gitee PM-skill repository met the same public-source
  evidence threshold in this review. This is not evidence that none exists.
- AI Delivery Spec's self-ratings are structurally checkable in this repository,
  but independent users should still reproduce the cases and challenge them.
