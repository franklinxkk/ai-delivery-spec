#!/usr/bin/env python3
"""Regression-test representative routing decisions for ai-delivery-spec.

This is a policy harness, not a production natural-language classifier. It keeps
trigger boundaries, mode precedence, tier selection, and plugin composition
executable while the prose skill evolves.
"""

from dataclasses import dataclass
import sys


def contains_any(text, terms):
    value = text.lower()
    return any(term.lower() in value for term in terms)


FULL_SIGNALS = (
    "正式验收",
    "生产上线",
    "上线准备",
    "发布就绪",
    "正式上线",
    "发布就绪方案",
    "迁移切换",
    "回滚",
    "on-call",
    "完整交付包",
    "稳定上线",
    "海外上线",
    "全球发布",
    "正式出海",
    "产品下线",
    "终止服务",
)

STANDARD_SIGNALS = (
    "开发",
    "qa",
    "测试用例",
    "测试组",
    "开工",
    "采购",
    "投标",
    "招标",
    "客户演示",
    "老板演示",
    "下周演示",
    "多角色",
    "全生命周期",
    "handoff",
    "董事会",
    "年度规划",
    "重大投资",
    "试点报告",
    "效果报告",
    "事故复盘",
)

LITE_SIGNALS = (
    "先看方向",
    "快速",
    "粗略",
    "草图",
    "草稿",
    "验证一下",
    "one-page",
    "只审",
    "只看",
)

DELIVERY_ARTIFACTS = (
    "prd",
    "需求文档",
    "原型",
    "用户故事",
    "角色路径",
    "状态机",
    "ddd",
    "开发契约",
    "验收报告",
    "验收方案",
    "上线方案",
    "发布方案",
    "发布就绪方案",
    "智能体",
    "ai学习助教",
    "ai数字人",
    "监管平台",
    "数据集市",
    "dashboard",
    "看板",
    "工作流",
    "调研报告",
    "访谈纪要",
    "商业论证",
    "路线图",
    "roadmap",
    "信息架构",
    "交互稿",
    "设计稿",
    "api契约",
    "接口契约",
    "架构设计",
    "技术方案",
    "数据模型",
    "迁移方案",
    "测试方案",
    "测试计划",
    "追溯矩阵",
    "uat",
    "发布计划",
    "灰度方案",
    "运行手册",
    "runbook",
    "试点方案",
    "试点报告",
    "实验报告",
    "效果报告",
    "指标复盘",
    "事故复盘",
    "运营复盘",
    "交付复盘",
    "下线计划",
    "退役计划",
    "数据删除证明",
)

DELIVERY_INTENT = (
    "做",
    "写",
    "编写",
    "起草",
    "整理",
    "输出",
    "实现",
    "设计",
    "生成",
    "完善",
    "评审",
    "审查",
    "验收",
    "逆向",
    "交付",
    "开发",
    "测试",
    "演示",
    "上线",
)

NON_DELIVERY = (
    "修复 css",
    "空指针错误",
    "代码语法",
    "宣传文案",
    "润色文案",
    "随便聊聊",
    "有哪些可能性",
    "解释什么是",
    "简历",
)

AI_CORE = (
    "ai native",
    "多智能体",
    "自主选择工具",
    "自动创建学习任务",
    "自动创建工单",
    "写业务状态",
    "自动执法",
    "自动审批",
    "精准培训智能体",
    "ai学习助教",
    "智能体稳定上线",
    "ai数字人",
    "自动退款",
    "自动生成处置",
    "自主路由工单",
)

AI_SUPPORTING = (
    "ai分类",
    "ai摘要",
    "ai提取",
    "ai推荐",
    "ai草拟",
    "ai生成",
    "ai报告",
    "智能报告",
    "生成报告",
    "智能问数",
    "人工确认",
    "律师确认",
    "人工审核",
)


def select_route(prompt):
    """Select one primary artifact route before composing optional plugins."""
    if contains_any(
        prompt,
        (
            "下线计划",
            "退役计划",
            "产品下线",
            "终止服务",
            "弃用",
            "sunset",
            "数据删除证明",
        ),
    ):
        return "retirement"
    if contains_any(
        prompt,
        (
            "试点报告",
            "实验报告",
            "效果报告",
            "指标复盘",
            "事故复盘",
            "运营复盘",
            "交付复盘",
            "上线后",
        ),
    ):
        return "post-launch-evidence"
    if contains_any(
        prompt,
        (
            "发布计划",
            "灰度方案",
            "运行手册",
            "runbook",
            "试点方案",
            "上线准备",
            "正式上线",
            "上线方案",
            "发布方案",
            "发布就绪",
            "发布就绪方案",
            "生产上线",
        ),
    ):
        return "release-readiness"
    if contains_any(
        prompt,
        (
            "测试方案",
            "测试计划",
            "测试用例",
            "追溯矩阵",
            "uat",
            "验收报告",
            "验收方案",
        ),
    ):
        return "verification-acceptance"
    if contains_any(
        prompt,
        (
            "api契约",
            "接口契约",
            "架构设计",
            "技术方案",
            "数据模型",
            "迁移方案",
            "ddd",
            "开发契约",
        ),
    ):
        return "engineering-contract"
    if contains_any(
        prompt,
        ("信息架构", "交互稿", "设计稿", "原型", "客户演示", "老板演示"),
    ):
        return "design-prototype"
    if contains_any(
        prompt,
        ("调研报告", "访谈纪要", "商业论证", "路线图", "roadmap", "董事会"),
    ):
        return "strategy-discovery"
    return "requirement-definition"


def classify(prompt):
    has_artifact = contains_any(prompt, DELIVERY_ARTIFACTS)
    has_intent = contains_any(prompt, DELIVERY_INTENT)
    excluded = contains_any(prompt, NON_DELIVERY)

    # An explicit delivery artifact plus a delivery/review intent overrides a
    # generic implementation word such as HTML. Code-only requests stay out.
    trigger = has_artifact and has_intent and not (excluded and not has_artifact)

    if not trigger:
        return {
            "trigger": False,
            "mode": None,
            "tier": None,
            "route": None,
            "plugins": set(),
        }

    if contains_any(prompt, FULL_SIGNALS):
        mode = "Full"
    elif contains_any(prompt, STANDARD_SIGNALS):
        mode = "Standard"
    else:
        mode = "Lite"

    route = select_route(prompt)

    if route in {"strategy-discovery", "post-launch-evidence", "retirement"}:
        tier = "N/A"
    elif contains_any(prompt, AI_CORE):
        tier = "L3"
    elif mode in {"Standard", "Full"}:
        tier = "L2"
    elif contains_any(prompt, ("prd", "需求文档", "用户故事", "状态机")):
        tier = "L1"
    else:
        tier = "L0"

    plugins = set()
    if contains_any(prompt, AI_CORE):
        plugins.add("ai-native")
    elif contains_any(prompt, AI_SUPPORTING):
        plugins.add("ai-feature")
    if contains_any(prompt, ("移动端", "小程序", "app", "手持终端", "司机端")):
        plugins.add("mobile")
    surface_count = sum(
        contains_any(prompt, (surface,))
        for surface in ("pc", "移动端", "小程序", "app")
    )
    if "多端" in prompt.lower() or surface_count >= 2:
        plugins.add("multi-surface")
    if contains_any(prompt, ("审批", "会签", "转审", "撤回", "整改验收", "许可办理")):
        plugins.add("approval")
    if contains_any(prompt, ("saas", "多租户", "rbac", "组织树", "数据隔离", "席位")):
        plugins.add("saas")
    if contains_any(prompt, ("指标", "报表", "数据集市", "bi", "dashboard", "看板", "智能问数")):
        plugins.add("reporting")
    if contains_any(prompt, ("低代码", "工作流画布", "连接器", "n8n", "dify", "flowise")):
        plugins.add("workflow")
    if contains_any(
        prompt,
        (
            "出海",
            "海外",
            "全球",
            "跨境",
            "多国家",
            "多地区",
            "多语言",
            "欧盟",
            "欧洲",
            "美国市场",
            "中东",
            "东南亚",
            "日本市场",
            "数据驻留",
            "区域部署",
            "gdpr",
            "eu ai act",
            "rtl",
            "阿拉伯语",
        ),
    ):
        plugins.add("global")
    if contains_any(prompt, ("交通", "运输", "司机", "车辆", "运智管家", "主动防控")):
        plugins.add("traffic-domain")
    if contains_any(prompt, ("crm", "客户管理", "线索", "商机", "客户经营", "经营响应")):
        plugins.add("crm-domain")
    if contains_any(
        prompt,
        (
            "高校",
            "教育信息化",
            "智慧校园",
            "数字校园",
            "教务",
            "学工",
            "教学质量",
            "智慧教室",
            "一网通办",
            "辅导员",
            "higher-education",
            "digital campus",
            "academic affairs",
            "student affairs",
            "teaching quality",
            "smart classroom",
            "campus ai assistant",
        ),
    ):
        plugins.add("education-domain")
    if contains_any(prompt, FULL_SIGNALS) or route in {"release-readiness", "retirement"}:
        plugins.add("readiness")
    if route == "strategy-discovery" or contains_any(
        prompt,
        ("新市场", "重大投资", "董事会", "商业化", "产品转型路线", "调研", "访谈"),
    ):
        plugins.add("strategy")
    if contains_any(prompt, ("skill发布", "prompt registry", "prompt注册", "模型注册", "工具注册")):
        plugins.add("prompt-ops")
    if contains_any(prompt, ("现有", "已有", "旧版", "截图", "sql", "逆向", "v1.8", "v15")):
        plugins.add("reverse-engineering")

    return {
        "trigger": True,
        "mode": mode,
        "tier": tier,
        "route": route,
        "plugins": plugins,
    }


@dataclass(frozen=True)
class Scenario:
    name: str
    prompt: str
    trigger: bool
    mode: str | None = None
    tier: str | None = None
    plugins: frozenset[str] = frozenset()
    route: str | None = None


SCENARIOS = (
    # Real workspace patterns.
    Scenario(
        "Yunzhiguanjia PRD from screenshots and SQL",
        "用v1.8需求文档、系统截图和SQL完善运智管家监管平台PRD，交给开发和测试",
        True,
        "Standard",
        "L2",
        frozenset({"reverse-engineering", "traffic-domain"}),
    ),
    Scenario(
        "CRM lifecycle demo",
        "根据老板流程图实现CRM完整原型，下周给老板演示，覆盖多角色全生命周期、审批和SaaS数据隔离",
        True,
        "Standard",
        "L2",
        frozenset({"approval", "saas", "crm-domain"}),
    ),
    Scenario(
        "Simple CRUD PRD draft",
        "快速写一个ToB客户管理CRUD PRD草稿，先看方向",
        True,
        "Lite",
        "L1",
        frozenset({"crm-domain"}),
    ),
    Scenario(
        "CRM direction sketch",
        "快速做一个CRM线索列表原型草图，先看方向",
        True,
        "Lite",
        "L0",
        frozenset({"crm-domain"}),
    ),
    Scenario(
        "AI data report PRD",
        "编写数据智能报告PRD，包含AI生成报告、智能问数和指标报表，交开发和QA",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "reporting"}),
    ),
    Scenario(
        "Overseas SaaS release readiness",
        "输出海外多语言SaaS正式上线方案，覆盖发布就绪、数据驻留和回滚",
        True,
        "Full",
        "L2",
        frozenset({"saas", "global", "readiness"}),
        "release-readiness",
    ),
    Scenario(
        "Data application regression",
        "审查现有数据集市HTML原型的指标库、报表任务和填报流程，给测试组写测试用例",
        True,
        "Standard",
        "L2",
        frozenset({"reverse-engineering", "reporting"}),
    ),
    Scenario(
        "Detailed PRD evidence coverage",
        "用现有Dashboard指标Excel、AI巡检规则表、SQL字段字典和HTML原型编写完整PRD，交开发和测试",
        True,
        "Standard",
        "L2",
        frozenset({"reverse-engineering", "reporting"}),
    ),
    Scenario(
        "Driver precision training agent",
        "设计货运司机小程序精准培训智能体，基于主动防控数据自动创建学习任务，准备交开发",
        True,
        "Standard",
        "L3",
        frozenset({"ai-native", "mobile", "traffic-domain"}),
    ),
    Scenario(
        "Knowledge SaaS skill publishing",
        "完善SaaS知识库管理与Skill发布PRD，包含组织树、RBAC和人工审核，交开发",
        True,
        "Standard",
        "L2",
        frozenset({"saas", "prompt-ops"}),
    ),
    Scenario(
        "Prototype-only but development-bound",
        "只审这份HTML原型，开发下周开工",
        True,
        "Standard",
        "L2",
    ),
    Scenario(
        "Quick wording conflicts with customer demo",
        "先快速做个可点击原型，下周给客户演示",
        True,
        "Standard",
        "L2",
    ),
    # Cross-industry coverage.
    Scenario(
        "Healthcare AI triage launch",
        "评审移动端AI分诊智能体稳定上线方案，AI自主选择工具并生成处置任务，包含正式验收和回滚",
        True,
        "Full",
        "L3",
        frozenset({"ai-native", "mobile", "readiness"}),
    ),
    Scenario(
        "Finance human-approved recommendation",
        "编写贷款SaaS审批PRD，AI推荐授信额度但由人工审核，交开发和QA",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "approval", "saas"}),
    ),
    Scenario(
        "Manufacturing field diagnosis",
        "设计制造业移动端设备巡检原型，AI推荐故障原因并由人工确认，交开发",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "mobile"}),
    ),
    Scenario(
        "Government permit workflow",
        "设计政务许可办理PC和小程序多端PRD，包含会签、转审、撤回、组织树和数据隔离，交开发测试",
        True,
        "Standard",
        "L2",
        frozenset({"mobile", "multi-surface", "approval", "saas"}),
    ),
    Scenario(
        "Retail analytics SaaS",
        "编写零售SaaS经营Dashboard和指标报表PRD，交开发和QA",
        True,
        "Standard",
        "L2",
        frozenset({"reporting", "saas"}),
    ),
    Scenario(
        "Education learning assistant",
        "设计小程序AI学习助教PRD，自动创建个性化学习任务并跟踪效果，准备开发",
        True,
        "Standard",
        "L3",
        frozenset({"ai-native", "mobile"}),
    ),
    Scenario(
        "Legal contract review",
        "设计合同审查SaaS需求文档，AI草拟风险建议并由律师确认，交开发",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "saas"}),
    ),
    Scenario(
        "Low-code workflow builder",
        "编写低代码工作流画布PRD，包含连接器、执行历史和多租户RBAC，交开发",
        True,
        "Standard",
        "L2",
        frozenset({"workflow", "saas"}),
    ),
    Scenario(
        "Higher education academic affairs",
        "编写高校教育信息化教务系统PRD，覆盖培养方案、开课、排课、选课、考试、成绩发布、申诉和数据治理，交开发和QA",
        True,
        "Standard",
        "L2",
        frozenset({"education-domain"}),
    ),
    Scenario(
        "Higher education student affairs",
        "评审智慧校园学工系统PRD，覆盖辅导员工作台、请假审批、奖助、心理谈话、学生预警、一网通办、多租户RBAC和审计，交开发和QA",
        True,
        "Standard",
        "L2",
        frozenset({"approval", "saas", "education-domain"}),
    ),
    Scenario(
        "Higher education teaching quality AI",
        "设计高校教学质量与智慧教室PRD，包含AI推荐课堂分析结论、人工复核、指标看板、移动端取证和测试验收，交开发和QA",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "mobile", "reporting", "education-domain"}),
    ),
    Scenario(
        "Board strategy handoff",
        "为董事会评审新市场商业化产品转型路线和后续PRD交付要求",
        True,
        "Standard",
        "N/A",
        frozenset({"strategy"}),
        "strategy-discovery",
    ),
    # AI-native and product globalization coverage.
    Scenario(
        "EU AI learning tutor app launch",
        "评审欧盟多语言小程序AI学习助教正式海外上线，自动创建学习任务，要求区域部署和回滚",
        True,
        "Full",
        "L3",
        frozenset({"ai-native", "mobile", "global", "readiness"}),
    ),
    Scenario(
        "Middle East Arabic service agent",
        "设计面向中东市场的阿拉伯语CRM SaaS客服智能体PRD，支持RTL并自主路由工单，交开发",
        True,
        "Standard",
        "L3",
        frozenset({"ai-native", "saas", "global"}),
    ),
    Scenario(
        "SEA driver safety assistant",
        "设计东南亚多国家货运司机App安全智能体，自动生成处置任务并适配弱网，准备开发",
        True,
        "Standard",
        "L3",
        frozenset({"ai-native", "mobile", "traffic-domain", "global"}),
    ),
    Scenario(
        "US EU legal review SaaS",
        "编写美国市场和欧盟合同审查SaaS需求文档，AI草拟风险建议并由律师确认，交开发QA",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "saas", "global"}),
    ),
    Scenario(
        "Global AI avatar consumer app",
        "设计全球发布的移动端AI数字人App验收方案，包含生成内容举报、订阅取消、模型回滚和多语言评测",
        True,
        "Full",
        "L3",
        frozenset({"ai-native", "mobile", "global", "readiness"}),
    ),
    Scenario(
        "Cross-border commerce service automation",
        "设计跨境电商AI客服工作流PRD，智能体自主选择工具并自动退款，交开发和测试",
        True,
        "Standard",
        "L3",
        frozenset({"ai-native", "global"}),
    ),
    Scenario(
        "Japan field maintenance copilot",
        "设计日本市场移动端设备巡检PRD，AI推荐维修步骤并由工程师人工确认，交开发",
        True,
        "Standard",
        "L2",
        frozenset({"ai-feature", "mobile", "global"}),
    ),
    Scenario(
        "Multi-country retail analytics SaaS",
        "编写多国家零售SaaS经营Dashboard和指标报表PRD，包含时区币种和数据驻留，交开发QA",
        True,
        "Standard",
        "L2",
        frozenset({"reporting", "saas", "global"}),
    ),
    # Product lifecycle artifact coverage.
    Scenario(
        "Discovery research review",
        "评审用户访谈纪要和调研报告，决定是否进入PRD",
        True,
        "Lite",
        "N/A",
        frozenset({"strategy"}),
        "strategy-discovery",
    ),
    Scenario(
        "Major investment business case",
        "评审重大投资商业论证和年度产品路线图，提交董事会决策",
        True,
        "Standard",
        "N/A",
        frozenset({"strategy"}),
        "strategy-discovery",
    ),
    Scenario(
        "Requirement definition handoff",
        "评审订单履约需求文档和用户故事，交开发",
        True,
        "Standard",
        "L2",
        frozenset(),
        "requirement-definition",
    ),
    Scenario(
        "Mobile design handoff",
        "评审移动端信息架构和交互稿，给设计开发对齐",
        True,
        "Standard",
        "L2",
        frozenset({"mobile"}),
        "design-prototype",
    ),
    Scenario(
        "API and data contract",
        "评审订单状态API契约和数据模型，交开发测试",
        True,
        "Standard",
        "L2",
        frozenset(),
        "engineering-contract",
    ),
    Scenario(
        "QA test design",
        "评审测试方案、测试用例和需求追溯矩阵，准备QA执行",
        True,
        "Standard",
        "L2",
        frozenset(),
        "verification-acceptance",
    ),
    Scenario(
        "Customer UAT decision",
        "评审客户UAT验收报告和缺陷处置结论，准备正式验收",
        True,
        "Full",
        "L2",
        frozenset({"readiness"}),
        "verification-acceptance",
    ),
    Scenario(
        "Production release readiness",
        "评审生产发布计划、灰度方案、运行手册和回滚方案",
        True,
        "Full",
        "L2",
        frozenset({"readiness"}),
        "release-readiness",
    ),
    Scenario(
        "Pilot outcome review",
        "评审试点报告和指标复盘，决定扩大、迭代还是回滚",
        True,
        "Full",
        "N/A",
        frozenset({"readiness"}),
        "post-launch-evidence",
    ),
    Scenario(
        "Global AI effect review",
        "评审AI学习助教上线后的效果报告和多语言指标复盘",
        True,
        "Standard",
        "N/A",
        frozenset({"ai-native", "global"}),
        "post-launch-evidence",
    ),
    Scenario(
        "Production incident learning",
        "评审生产事故复盘和整改行动，更新上线准备",
        True,
        "Full",
        "N/A",
        frozenset({"readiness"}),
        "post-launch-evidence",
    ),
    Scenario(
        "SaaS retirement and customer exit",
        "评审旧版SaaS产品下线计划、客户迁移、数据导出删除和终止服务",
        True,
        "Full",
        "N/A",
        frozenset({"saas", "readiness"}),
        "retirement",
    ),
    # Trigger boundaries.
    Scenario(
        "HTML prototype implementation with handoff intent",
        "帮我用HTML实现这个可交付原型，给开发和测试作为交互契约",
        True,
        "Standard",
        "L2",
    ),
    Scenario("Code-only login page", "帮我写一个HTML登录页", False),
    Scenario("CSS-only fix", "修复CSS按钮颜色", False),
    Scenario("React bug", "修复React组件空指针错误", False),
    Scenario("Copy edit", "润色产品宣传文案", False),
    Scenario("Casual brainstorm", "随便聊聊AI客服有哪些可能性", False),
    Scenario("General PM question", "解释什么是用户故事", False),
    Scenario("Resume editing", "帮我修改简历里的项目亮点", False),
)


def main():
    failures = []
    for case in SCENARIOS:
        actual = classify(case.prompt)
        expected = {
            "trigger": case.trigger,
            "mode": case.mode,
            "tier": case.tier,
            "plugins": set(case.plugins),
            "route": case.route,
        }
        for field in ("trigger", "mode", "tier"):
            if actual[field] != expected[field]:
                failures.append(
                    f"{case.name}: {field} expected {expected[field]!r}, got {actual[field]!r}"
                )
        missing_plugins = expected["plugins"] - actual["plugins"]
        if missing_plugins:
            failures.append(
                f"{case.name}: missing plugins {sorted(missing_plugins)}; got {sorted(actual['plugins'])}"
            )
        if case.route is not None and actual["route"] != case.route:
            failures.append(
                f"{case.name}: route expected {case.route!r}, got {actual['route']!r}"
            )

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    real_count = 12
    boundary_count = 8
    global_count = 8
    lifecycle_count = 12
    industry_count = (
        len(SCENARIOS)
        - real_count
        - boundary_count
        - global_count
        - lifecycle_count
    )
    print(
        "PASS: "
        f"{len(SCENARIOS)} routing scenarios "
        f"({real_count} real patterns, {industry_count} cross-industry, "
        f"{global_count} global/AI-native, {lifecycle_count} lifecycle stages, "
        f"{boundary_count} trigger boundaries)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
