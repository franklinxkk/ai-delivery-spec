#!/usr/bin/env python3
"""Scan lexical ambiguity and missing clarification dimensions.

This is an advisory discovery scanner, not proof that a requirement is correct.
It combines cheap wording checks with structural prompts so a concise request
cannot appear ready merely because it avoids words such as "支持" or "灵活".
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PATTERNS = {
    "vague-capability": r"(?:支持|实现|提供)(?![^。；\n]{0,24}(?:条件|角色|结果|规则|范围))",
    "vague-quantity": r"(?:适量|若干|一定数量|大量|少量|较多|尽量)",
    "vague-time": r"(?:及时|尽快|实时处理|稍后|定期)(?![^。；\n]{0,16}\d)",
    "open-list": r"(?:等等|等功能|等场景|诸如此类)",
    "undefined-default": r"(?:默认|自动)(?![^。；\n]{0,24}(?:为|条件|规则|当|若|由))",
    "unbounded-config": r"(?:灵活配置|可配置|按需配置)(?![^。；\n]{0,24}(?:配置项|范围|权限|规则))",
    "unspecified-actor": r"(?:相关人员|有关人员|管理员等|业务人员)(?![^。；\n]{0,18}(?:角色|权限|范围))",
}

CONTENT_QUESTIONS_EN = {
    "publication": "Who publishes after approval, and when? Distinguish permission to publish from the publication event.",
    "return-object": "After return, is the same record edited or a new one created? What happens to its ID, history and resubmission destination?",
    "null-meaning": "Does null mean unknown, not applicable or not yet collected? How does it differ from zero in calculations?",
    "metric-population": "Define the population, denominator, deduplication and time window, including departures and late data.",
    "retry-result": "Could the failed request already have written data? How will a retry identify the existing result and avoid duplicate side effects?",
    "state-ordinal": "Which filters, reports, interfaces and historical records consume the changed state identity? Verify each dependency.",
    "rule-consumers": "Which consumers and historical interpretations depend on the changed definition? Verify the dependency before changing them.",
    "deep-link": "Does every direct link or API call still check identity, object and data scope? Hiding a control does not prove authorization.",
    "ai-write": "What authorizes this automatic write, limits its scope, and defines refusal, stopping and recovery? Confidence is not authorization.",
    "relevance-authority": "Retrieval relevance cannot grant access or execution permission.",
    "provenance-truth": "Valid provenance credentials do not prove the content is factually true.",
    "confidence-outcome": "Define and verify model confidence separately from task completion or business success.",
    "open-decision": "A business decision remains open. Identify its dependent scope, decision owner and blocking stage before claiming it is implementable.",
    "unresolved-conflict": "Resolve the incompatible rules or expected results for this scope before claiming implementation readiness.",
    "policy-basis": "Check the approved basis of this selection policy; calling it a default does not authorize it.",
    "undecided-policy": "The selection policy is still unresolved. Locate an authorized decision before using the proposed default.",
    "publication-conflict": "The same publication topic has different policies. Resolve their applicable conditions or supersession.",
    "decision-conflict": "The same decision topic has incompatible policies. Resolve their scope or supersession from authority.",
    "return-conflict": "The same section describes both reusing and replacing a returned record. Verify explicit branch conditions and object scope.",
}


def prose_lines(text: str) -> list[str]:
    """Mask metadata, fenced examples and comments while preserving line numbers."""
    lines = text.splitlines()
    fence, front, comment = "", bool(lines and lines[0].strip() == "---"), False
    result = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if front:
            if index and stripped in {"---", "..."}:
                front = False
            result.append("")
            continue
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            if not fence:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = ""
            result.append("")
            continue
        if fence:
            result.append("")
            continue
        visible = []
        for part in re.split(r"(<!--|-->)", line):
            if part == "<!--":
                comment = True
            elif part == "-->":
                comment = False
            elif not comment:
                visible.append(part)
        result.append("".join(visible))
    return result


def _affirmative_match(text: str, pattern: str) -> bool:
    """Reject a guard/policy that is locally negated or still only proposed."""
    for match in re.finditer(pattern, text, re.I):
        prefix = re.split(r"[。；;，,|\n]|但是|而是|但|而", text[:match.start()])[-1]
        if not re.search(r"不(?:能|可|会|必|需|须|得|应|允许)?|无(?:需|须)|尚未|未(?:曾|能|予以)?(?:拒绝|检查|校验|验证|实现)|禁止|待确认|计划|建议", prefix[-16:] + match[0]):
            return True
    return False


def _explicit_deep_link_guard(line: str) -> bool:
    # Bind the check to this link/request and require both caller and object
    # scope. A role-name mention or an unrelated nearby rule is not a guard.
    denied = _affirmative_match(line, r"(?:深链|直链|直接请求)(?:(?!未|没有|不|待)[^。；;|\n]){0,24}(?:返回拒绝|访问拒绝|拒绝|403)")
    # A server check may precede the sentence applying it to direct links.
    # Require caller AND object/data scope; a backend toast or a closed-state
    # response alone does not establish authorization.
    server_guard = _affirmative_match(
        line,
        r"服务端[^。；;|\n]{0,12}(?:检查|校验|验证)"
        r"[^。；;|\n]{0,12}(?:身份|角色|权限)"
        r"[^。；;|\n]{0,18}(?:对象(?:访问|归属)?范围|数据范围)",
    )
    if re.search(r"(?:是否|计划|建议|拟|待)[^。；;|\n]{0,18}服务端|服务端[^。；;|\n]{0,12}是否[^。；;|\n]{0,6}(?:检查|校验|验证)", line):
        return False
    return denied or server_guard or _affirmative_match(
        line,
        r"(?:深链|直链|直接请求|直接调用|实际请求)[^。；;|\n]{0,18}"
        r"(?:检查|校验|验证)[^。；;|\n]{0,12}(?:身份|角色|权限)"
        r"[^。；;|\n]{0,16}(?:对象|数据)(?:访问|归属)?范围",
    )


def _return_conflict(block: str) -> bool:
    """Compare affirmative return paths, not every creation in a section.

    These remain bounded probes: explicit object names distinguish independent
    paths; an unnamed path cannot disprove a conflict with a named one.
    """
    policies = []
    for sentence in re.split(r"[。；;|\n]", block):
        returned = re.search(r"退回(?!历史|记录|原因)", sentence)
        if not returned:
            continue
        prefix = sentence[:returned.start()].strip().strip("“”\" ")
        subject = prefix if re.fullmatch(r"[\w-]{1,20}(?:单|申请|请求|对象|记录)", prefix) else ""
        path = sentence[returned.start():]
        reuse = _affirmative_match(path, r"(?:编辑|修改|保留|沿用).{0,8}(?:原单|原对象)|(?:原单|原对象).{0,8}(?:编辑|修改|保留|沿用)")
        replace = _affirmative_match(path, r"新单|新对象|(?:新建|创建|复制)(?:新的?|一个)?(?:申请|单据|对象|记录|工单)|(?:原单|原对象).{0,8}(?:关闭|作废)|(?:关闭|作废).{0,8}(?:原单|原对象)")
        if reuse or replace:
            policies.append((subject, reuse, replace, sentence))
    for subject, reuse, _, sentence in policies:
        if not reuse:
            continue
        for other_subject, _, replace, other_sentence in policies:
            distinct_subjects = (subject and other_subject and subject != other_subject
                                 and not subject.endswith(other_subject) and not other_subject.endswith(subject))
            if not replace or distinct_subjects:
                continue
            # An explicit conditional split applies to these return paths only.
            paired = sentence if sentence == other_sentence else sentence + "\n" + other_sentence
            if not re.search(r"(?:如果|若|当).{0,30}(?:否则|分别)|(?:类型|场景).{0,20}(?:分别|不同)", paired):
                return True
    return False


def inspect_content(text: str) -> dict:
    """Bounded Chinese/English probes, never an NLP completeness or truth proof.

    Findings survive a declared review pass. A contextual guard can suppress a
    question, but does not create a semantic-review attestation or authorize it.
    """
    lines = prose_lines(text)
    findings, risks, categories = [], set(), set()
    headings = [i for i, line in enumerate(lines) if re.match(r"^#{1,6}\s", line)]
    # Each probe names an actual decision fork, its trigger, and nearby evidence
    # that makes the fork explicit. Never turn a domain pattern into a policy.
    probes = [
        ("publication", "state_authority", {"state"}, r"(?:审批|审核)通过.{0,15}(?:可|可以|允许)发布|\bapprov(?:al|ed)\b[^.;\n]{0,45}\b(?:can|may|eligible|allowed)\b[^.;\n]{0,25}\bpublish|\b(?:can|may|eligible|allowed)\b[^.;\n]{0,25}\bpublish[^.;\n]{0,25}\bafter approval\b", r"(?:手动|人工|点击|定时|自动|发布人|发布角色|不立即|不会自动).{0,25}发布|发布.{0,20}(?:手动|人工|角色|时机)|\b(?:manual(?:ly)?|automatic(?:ally)?|scheduled|publisher)\b[^.;\n]{0,35}\bpublish|\b(?:publish\w*|publication)\b[^.;\n]{0,35}\b(?:manual(?:ly)?|automatic(?:ally)?|scheduled|role)\b", "通过后谁在什么条件下发布？区分发布资格与实际发布事件。"),
        ("return-object", "recovery", {"state"}, r"退回(?!历史|记录|原因)[^。；;|\n]{0,20}(?:重新|再次|重提|提交)|\breturn(?:ed)?\b[^.;\n]{0,50}\bresubmit|\bresubmit\w*\b[^.;\n]{0,35}\breturn(?:ed)?\b", r"原单|原对象|新单|新对象|同一.{0,8}(?:ID|编号)|保留.{0,8}(?:ID|编号)|\b(?:same|original|new)\s+(?:record|object|request|ID)\b|\b(?:keep|retain|preserve)\w*\s+(?:the\s+)?(?:ID|identifier)\b", "退回后修改原对象还是新建？原编号、历史及再次提交去向如何处理？"),
        ("null-meaning", "null_stale", set(), r"字段.{0,12}(?:可空|为空)|允许.{0,8}空值|未采集.{0,10}(?:按|计为|记为)\s*(?:数值\s*)?0", r"(?:空值|为空|未采集).{0,30}(?:表示|代表|区别|不等于|未知|不适用)|(?:不|不得|不能)按\s*0", "空值在此字段代表未知、不适用还是尚未采集？是否与零不同，如何参与计算？"),
        ("metric-population", "metric_definition", {"metric"}, r"完成率|通过率|离职率|活跃用户|completion rate|active users", r"分母|统计人群|纳入.{0,20}(?:用户|人员)|去重.{0,12}(?:用户|人员)|denominator|population", "说明统计对象、去重/时间窗和分母；离职、退出与晚到数据如何计入？"),
        ("retry-result", "recovery", set(), r"(?:提交|保存|写入|支付)失败.{0,12}(?:重试|再试)|\b(?:submit|save|write|payment)\w*\b[^.;\n]{0,20}\bfail\w*\b[^.;\n]{0,25}\bretry|\bretry\b[^.;\n]{0,25}\bfailed\s+(?:submit|save|write|payment)", r"幂等|重复.{0,12}(?:不|防止)|未写入|已写入|保留.{0,10}输入|查询.{0,10}结果|\bidempot\w*|\b(?:avoid|prevent)\w*\s+duplicate|\balready\s+(?:written|saved|paid)|\bquery\w*[^.;\n]{0,20}\bresult", "失败时是否已产生副作用？再次提交会重复写入吗，如何确认与恢复？"),
        ("state-ordinal", "change_propagation", {"migration", "state"}, r"(?:已完成|状态).{0,35}第\s*[一二三四五六七八九十\d]+\s*(?:个)?(?:状)?态.{0,15}(?:改|变|调整)|(?:插入|新增).{0,10}状态.{0,20}(?:序号|编号)", r"稳定.{0,10}(?:键|编码|标识)|不使用.{0,10}(?:序号|顺序)|(?:消费者|筛选|报表|过滤).{0,30}(?:同步|映射|迁移|更新)", "状态序号改变会影响哪些筛选、报表、接口和历史对象？使用稳定含义并逐项核实消费者。"),
        ("rule-consumers", "change_propagation", {"migration"}, r"(?:定义|口径).{0,20}从.{0,50}(?:改为|调整为|变为)", r"(?:消费者|依赖|报表|看板).{0,30}(?:核实|验证|同步|保留|候选|回归)", "口径变更后哪些读写者、指标和历史解释可能受影响？先查依赖依据，再确认变更范围。"),
        ("deep-link", "permission_boundary", {"permission"}, r"深链|直链|/share/|/objects?/|复制链接|隐藏.{0,12}(?:按钮|入口)", r"服务端.{0,20}(?:校验|鉴权|权限)|(?:每次|所有|任何).{0,15}(?:入口|请求).{0,20}(?:鉴权|权限)|拒绝.{0,15}(?:跨租户|越权|他人)|server.side.{0,15}authoriz", "直达链接或直接调用是否仍检查身份、对象和数据范围？隐藏入口不能证明权限隔离。"),
    ]

    def add(kind, category, facets, index, line, action):
        risks.update(facets)
        categories.add(category)
        findings.append({"kind": kind, "category": category, "facets": sorted(facets), "line": index + 1,
                         "text": line.strip()[:240], "context": line.strip()[:240], "action": action,
                         "advisory": True, "action_en": CONTENT_QUESTIONS_EN.get(kind, "Review this candidate against the existing rule, scope and source before changing it.")})

    for i, line in enumerate(lines):
        if re.match(r"^\s*(?:>|[-*]\s*)?(?:说明|检查记录|门禁结果|扫描结果|诊断记录)[：:]", line) and re.search(r"(?:SPEC|PROTO)-", line) and re.search(r"gap|block|finding|诊断", line, re.I):
            # A report about earlier diagnostics is not another product rule.
            # Keep any following sentence so real behavior is still checked.
            line = line.partition("。")[2]
        if not line.strip() or re.match(r"^#{1,6}\s|^\s*(?:>|[-*]\s*)?(?:错误示例|反例[：:]|禁止|不得|不应)", line):
            continue
        start = max([j for j in headings if j <= i] or [0])
        end = min([j for j in headings if j > i] or [len(lines)])
        context = "\n".join(lines[max(start, i - 3):min(end, i + 5)])[:1600]
        # A selected business policy is not proof of an unauthorized decision.
        # Without evidence of an unresolved choice, only ask for its basis.
        if (re.search(r"补考|成绩|学分|费率|晚到数据|历史数据|retake|resit|score|credit|late.arriv|historical data", line, re.I)
                and re.search(r"取(?:最新|最早|最高|最低)|默认(?:取|按)|一律按|us(?:e|es|ing)\s+(?:the\s+)?(?:latest|earliest|highest|lowest)", line, re.I)
                and not re.search(r"禁止|不得|不能|不应|do not|must not|never|建议|候选|propos|option", line, re.I)):
            undecided = re.search(r"未决|未定|待定|尚未(?:最终|正式)?(?:决定|确定)|待确认|undecided|unresolved|not yet (?:decided|approved)", context, re.I)
            basis = re.search(r"(?:依据|按|经|已批准|已确认|approved|according to).{0,45}(?:DEC-|SRC-|批准|确认|policy|decision)|已(?:由|经)[^。；\n]{1,16}(?:确认|批准|决定)", context, re.I)
            if undecided or not basis:
                add("undecided-policy" if undecided else "policy-basis", "decision", set(), i, line,
                    "核对取值政策的授权依据与未决状态；取最新/最高等选择不能仅因被称为默认而成立。 Check the policy's approved basis; a default label does not resolve an open decision.")
                if not undecided:
                    findings[-1]["severity"] = "WARN"
        decision_subject = r"策略|规则|口径|权限|时点|范围|重试|超时|负责人|是否|取值|阈值|字段"
        decision_pending = r"尚未(?:最终|正式)?(?:决定|确定|选择)|待确认|待定|待裁决|未决定"
        # Bind the pending phrase to a decision, not an unrelated status enum.
        if (re.search(rf"(?:{decision_subject})[^。；|/\n]{{0,14}}(?:{decision_pending})|(?:{decision_pending})\s*[：:]?\s*(?:{decision_subject})|待.{{0,12}}(?:业务|负责人).{{0,8}}决定", line)
                and not re.match(r"\s*\|\s*`?UNK-", line)
                and not re.search(r"已(?:确认|决定|裁决|关闭)|不在本次范围|不影响本次|仅.{0,8}(?:提示|显示).{0,8}待确认", line)):
            add("open-decision", "decision", set(), i, line, "正文存在未决定事项；说明依赖范围、决定人和阻断阶段，不能据此宣称该行为已可实施。")
        if re.search(r"无法同时(?:成立|满足)|尚未解决.{0,6}冲突|相互矛盾", line):
            add("unresolved-conflict", "decision", set(), i, line, "正文声明了尚不相容的规则或验收结果；解决适用条件或优先关系后再作实施结论。")
        for kind, category, facets, trigger, guard, action in probes:
            if kind == "null-meaning" and re.search(r"oldValue|修改前", line) and re.search(r"新增类型为空", line):
                continue  # A newly created record has no before-value.
            if kind == "metric-population" and re.match(r"^#{1,6}.*(?:范围|目标|scope|goal)", lines[start], re.I):
                continue  # A scope reference does not redefine the metric contract.
            if re.search(trigger, line, re.I):
                risks.update(facets)
                guarded = bool(re.search(guard, context, re.I))
                if kind == "return-object":
                    guarded = guarded or _affirmative_match(context, r"(?:仍用|沿用|保留)原\s*(?:ID|编号|合同号)|(?:ID\s*[/与和]\s*号|编号|合同号)不变")
                    # A field row can itself state stable identity throughout
                    # return/resubmit; it need not repeat a recovery chapter.
                    identity_row = re.match(r"^\s*\|[^|]*(?:编号|身份|\bID\b)[^|]*\|", line, re.I)
                    guarded = guarded or bool(identity_row and _affirmative_match(
                        line, r"退回[^。；;|\n]{0,24}(?:全过程沿用|始终保留|始终不变)"))
                if kind == "deep-link":
                    guarded = (_affirmative_match(context, guard) or _explicit_deep_link_guard(line)
                               or _affirmative_match(line, r"服务端[^。；;|\n]{0,8}验证[^。；;|\n]{0,8}身份[^。；;|\n]{0,8}对象范围"))
                if not guarded:
                    add(kind, category, facets, i, line, action)
        ai_actor = r"(?<![A-Za-z0-9_-])(?:AI(?!\s*(?:coding|编程|开发))|LLM|模型|智能体|agent|置信度|confidence)(?![A-Za-z0-9_-])"
        if re.search(ai_actor + r"[^。；;\n]{0,70}(?:自动|直接|无需人工|\bautomatically\b|\bdirectly\b)[^。；;\n]{0,50}(?:发信|发送|创建|新建|更新|修改|保存|写回|删除|支付|退款|扣款|执行|\b(?:send|email|create|update|save|write|delete|pay|refund|execute)\w*\b)|自动.{0,15}给客户.{0,8}(?:发信|发送)", line, re.I):
            if not re.search(r"(?:禁止|不允许|不会|不|不得)(?:自动|直接)|仅.{0,12}(?:草稿|建议)|draft.only|\bonly\s+(?:produces?\s+)?drafts?\b|\b(?:not|never)\s+(?:automatically|directly)\b", line, re.I):
                risks.add("irreversible_ai_write")
                guards = (r"授权|允许.{0,20}(?:范围|对象)|权限范围|authoriz\w*|permission\s+scope", r"回退|撤销|补偿|停止|人工接管|重试|幂等|rollback|undo|compensat\w*|stop|human takeover|retry|idempot\w*")
                if not all(re.search(g, context, re.I) for g in guards) or re.search(r"(?:无|没有|不能|不支持).{0,3}(?:回退|撤销|补偿|停止|人工接管)|\b(?:no|without)\s+(?:rollback|undo|recovery|compensation|stop)\b", context, re.I):
                    add("ai-write", "recovery", {"irreversible_ai_write"}, i, line, "自动写入的授权范围、触发/拒绝条件、副作用确认、停止与恢复是什么？置信度不是授权。")
        for kind, trigger, action in (
            ("relevance-authority", r"相关性\s*(?:=|即|等于|视为).{0,8}授权|(?:相关|检索命中).{0,15}(?:即可|自动获得).{0,8}(?:权限|授权)|\brelevance\s*(?:=|equals|grants|is)\s+(?:authorization|permission|access)\b", "相关性仅解释检索或排序，不能授予访问与执行权限。"),
            ("provenance-truth", r"C2PA.{0,20}(?:有效|通过).{0,12}(?:=|即|等于|代表|说明|证明).{0,8}(?:为真|真实|事实)|\bvalid C2PA\b[^.;\n]{0,30}\b(?:proves?|means?|=)\s+(?:the\s+)?(?:content\s+is\s+)?(?:true|truth|factual)", "凭证有效说明可验证的来源/处理声明，不证明内容事实为真。"),
            ("confidence-outcome", r"置信度.{0,12}(?:=|即|作为|当作|等于|就是).{0,8}(?:完成率|成功率|完成)|\bconfidence\s*(?:=|equals|is|as)\s+(?:the\s+)?(?:task\s+)?(?:completion|success)\s+rate\b", "模型置信度与任务完成/业务成功需分别定义、取证与验收。"),
        ):
            if re.search(trigger, line, re.I) and not re.search(r"不(?:等于|代表|证明)|不能|≠|\b(?:not|never)\b", line, re.I):
                add(kind, "permission_boundary" if kind == "relevance-authority" else "metric_definition", {"authority"}, i, line, action)

    # Same-topic DEC rows with incompatible publication policies need resolution,
    # even if each has a plausible-looking source label. Dates alone do not settle it.
    topics = {}
    publication_policies = {}
    owner = ""
    for i, line in enumerate(lines):
        if re.match(r"^#{1,6}\s", line) and re.search(r"REQ-[A-Z0-9-]+", line):
            owner = re.search(r"REQ-[A-Z0-9-]+", line)[0]
        subject = re.search(r"^\s*([^|#。；]{1,24}?)(?:审核|审批)通过后", line)
        if subject and not re.search(r"不(?:会|得|应)?自动|取代|替代|废弃|反例|禁止|如果|若|当", line):
            policy = "auto" if re.search(r"自动发布", line) else "manual" if re.search(r"手动|人工.{0,15}发布", line) else ""
            key = (owner, subject[1].strip())
            if policy:
                old = publication_policies.get(key)
                if old and old[0] != policy:
                    add("publication-conflict", "state_authority", {"state"}, i, line, f"与第 {old[1] + 1} 行同对象的自动发布规则可能冲突；明确人工发布与自动发布的适用条件或替代关系。")
                publication_policies[key] = (policy, i)
        if line.strip().startswith("|") and re.search(r"DEC-[A-Z0-9-]+", line) and re.search(r"已确认|confirmed|approved", line, re.I):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            topic = cells[1] if len(cells) > 2 else ""
            if topic and not re.search(r"取代|替代|supersed|已失效", line, re.I):
                policy = "auto" if re.search(r"(?:自动|立即)发布", line) else "manual" if re.search(r"手动|人工|运营.{0,8}发布", line) else ""
                if policy:
                    old = topics.get(topic)
                    if old and old[0] != policy:
                        add("decision-conflict", "state_authority", {"state"}, i, line, f"与第 {old[1] + 1} 行同主题决定的发布方式不同；明确适用范围或替代关系。")
                    topics[topic] = (policy, i)
    # Return-object disagreement within one heading, not across unrelated features.
    rule_sections = [i for i in headings if re.match(r"^#{1,2}\s", lines[i])]
    for start, end in zip([0, *rule_sections], [*rule_sections, len(lines)]):
        block = "\n".join(lines[start:end])
        if _return_conflict(block):
            add("return-conflict", "recovery", {"state"}, start, block, "同一段出现退回保留原单与关闭/新建两种路径；核实是否有明确分支条件和适用对象。")
    return {"risk_facets": sorted(risks), "review_categories": sorted(categories), "findings": findings,
            "coverage": "bounded_probes; absence_of_findings_is_not_semantic_proof"}


def scan(text: str) -> list[dict[str, object]]:
    findings = []
    for line_no, line in enumerate(prose_lines(text), 1):
        for kind, pattern in PATTERNS.items():
            for match in re.finditer(pattern, line):
                if kind == "undefined-default":
                    before = re.split(r"[。；;]", line[:match.start()])[-1]
                    after = line[match.end():match.end() + 18]
                    if re.search(r"(?:不|不会|不得|不能|没有|无需|禁止|当|若|后|时|仅)", before) or re.match(r"(?:选择|选中|显示|全部|关闭|开启|为|[:：])", after):
                        continue
                if kind == "vague-capability" and re.search(r"(?:仅|只)(?:需|要)?$", line[max(0, match.start() - 3):match.start()]):
                    continue
                findings.append({
                    "id": f"AMB-{len(findings)+1:03d}",
                    "kind": kind,
                    "line": line_no,
                    "text": match.group(0),
                    "context": line.strip()[:240],
                    "action": "replace with actor/condition/threshold/result/exception that can be accepted",
                })
    return findings


def scan_closure(text: str) -> list[dict[str, object]]:
    """Return missing requirement dimensions; never infer their answers."""
    text = "\n".join(prose_lines(text))
    lowered = text.lower()
    actor_hits = re.findall(
        r"\bROLE-[A-Z0-9-]+\b|管理员|用户|运营|销售|申请人|审批人|财务|患者|医生|护士|药师|医保|质检|仓库|采购|供应商|门店|店长|调度|运维|客户|监管|测试",
        text,
        re.I,
    )
    lenses: list[tuple[str, bool, str]] = [
        ("actor-authority", bool(actor_hits) and bool(re.search(r"由|仅|负责|权限|允许|可以|可查看", text)), "locate the actor and authority needed for the current behavior"),
        ("scope-boundary", bool(re.search(r"范围|纳入|不包含|不做|边界|scope|out of scope", lowered)), "define included and excluded scope"),
        ("acceptance-evidence", bool(re.search(r"验收|预期结果|证据|签署|acceptance|expected|evidence|sign.?off", lowered)), "define executable acceptance and required evidence"),
    ]
    if re.search(r"状态|审批|审核|闭环|退费|调拨|workflow|lifecycle", lowered):
        lenses.append(("state-authority", bool(re.search(r"状态机|当前状态|下一状态|状态权威|谁维护|state owner|system of record|source of truth", lowered)), "locate authoritative transitions for this stateful behavior"))
    if re.search(r"退款|支付|赔付|金额|结算|退费|refund|payment|claim|settlement", lowered):
        lenses.append((
            "money-reconciliation",
            bool(re.search(r"幂等|重复|对账|差错|冲正|挂账|补偿|idempot|reconcil|reversal", lowered)),
            "define money authority, idempotency, partial success, reversal and reconciliation",
        ))
    if re.search(r"库存|批次|在途|调拨|收货|数量|来料|stock|inventory|batch|quantity", lowered):
        lenses.append((
            "quantity-conservation",
            bool(re.search(r"数量守恒|冻结|预占|可用|库存流水|部分|差异|回冲|conservation|reserved|ledger|partial", lowered)),
            "define quantity conservation, frozen/available/in-transit ledgers and partial disposition",
        ))
    if re.search(r"存量|旧系统|已有系统|改造|变更|迁移|兼容|brownfield|legacy|migration", lowered):
        lenses.append((
            "brownfield-baseline",
            bool(re.search(r"stage\s*0|现状基线|变更种子|before|after|差异|历史数据|回退|baseline", lowered)),
            "extract the trusted current-state baseline, change seed, history compatibility and rollback",
        ))

    findings: list[dict[str, object]] = []
    for kind, passed, action in lenses:
        if passed:
            continue
        findings.append({
            "kind": kind,
            "line": 0,
            "text": "missing clarification dimension",
            "context": "document-level structural gap",
            "action": action,
            "advisory": True,
        })
    return findings + inspect_content(text)["findings"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--profile", choices=["lexical", "closure", "full"], default="full")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()
    text = args.document.read_text(encoding="utf-8")
    findings = []
    if args.profile in {"lexical", "full"}:
        findings.extend(scan(text))
    if args.profile in {"closure", "full"}:
        findings.extend(scan_closure(text))
    for index, item in enumerate(findings, 1):
        item["id"] = f"AMB-{index:03d}"
    if args.format == "json":
        rendered = json.dumps({"findings": findings}, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = f"# Ambiguity Scan\n\nFindings: **{len(findings)}**\n\n"
        rendered += "".join(
            f"- `{item['id']}` line {item['line']} `{item['kind']}`: {item['context']}\n"
            for item in findings
        )
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    if findings and args.fail_on_findings:
        return 1
    if args.format != "json" or args.output:
        print(f"PASS: ambiguity scan completed ({len(findings)} findings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
