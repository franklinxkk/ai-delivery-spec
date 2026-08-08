#!/usr/bin/env python3
"""PRD 语义一致性静态检查（5.4.4 正式版）：悬空引用、ID 前缀碰撞、状态机态数不符、
守卫状态集合互斥（D4 弱信号 WARN）、枚举基数/取值覆盖（D5 弱信号 WARN）。

纯静态、零 LLM。接线方式：``gate --profile prd`` 由 quality_gate.Gate._check_semantics
调用 ``run_semantic_checks``；也可独立执行：

    python scripts/validators/validate_prd_semantics.py <prd.md>

独立执行退出码：存在 BLOCK 级发现为 1，否则为 0。

D2 误报控制约定（宁严勿宽）：
- 定义位：YAML frontmatter 登记、Markdown 标题、表格首列、列表项开头 ID、
  ``id:`` 机器行、``ID（…）`` 注解定义、``「标签」（ID…）`` 控件定义、
  ``动作：/事件：`` 枚举定义、含“事件”列的状态机表事件列。
- 示例行（格式/示例/例如/如 …）只贡献定义、不贡献引用；仅在示例行出现的 ID
  （如 COR-ENTERPRISE_DATA-001 格式举例）整体豁免。
- 通配家族（ACT-DIFF-*）、模板占位（COR-{大项 code…}）不参与判定；
  行内代码（反引号）字面量视为跨文件外部引用（如 intake/stage0 的 SRC-*），豁免。
- 斜杠合并引用（RULE-SUBMIT-001/002、REG-DIFF-HEADER/TOOLBAR）按前缀展开。
- 悬空引用中只有导航式引用（见/详见/参见/遵循 X）是 BLOCK；其余降级 WARN；
  孤儿定义一律 WARN，不影响 PASS。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ID_FAMILIES = (
    "FLOW", "RULE", "ACT", "STM", "REQ", "MOD", "AC", "UNK", "ASM", "DEC",
    "FLD", "EVT", "API", "INT", "ROLE", "VIEW", "REG", "SRC", "COR",
)
_FAMILY = "|".join(ID_FAMILIES)
ID_RE = re.compile(rf"(?<![A-Za-z0-9-])(?:{_FAMILY})-[A-Z0-9](?:[A-Z0-9_-]*[A-Z0-9])?")
STM_RE = re.compile(r"(?<![A-Za-z0-9-])STM-[A-Z0-9](?:[A-Z0-9_-]*[A-Z0-9])?")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)

# 示例行只贡献定义、不贡献引用；仅出现于示例行的 ID 整体豁免（格式举例）。
EXAMPLE_MARKERS = ("格式", "示例", "例如", "如：", "如 ", "举例", "e.g.")
# 导航式引用：读者被显式指向定义，未定义即断链 → BLOCK。
NAV_RE = re.compile(r"(?:详见|参见|参阅|遵循|(?<![意可听看闻遇])见)\s*(?:[A-Z0-9][A-Z0-9-]*\s*[/、]?\s*)*$")
NEGATION_MARKERS = ("禁止", "不得", "不允许", "不准", "避免", "勿", "防止", "会碰撞", "防碰撞")
DEF_ENUM_MARKERS = ("动作：", "动作:", "事件：", "事件:", "区域明细：", "区域：")
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

TRUNC_TEMPLATE_RE = re.compile(
    r"([A-Z]{2,8})-\{[^{}]{0,80}?(?:前\s*([0-9]+|[一二三四五六七八九十])\s*(?:位|个字符|个字)|截取|截断)[^{}]{0,60}?\}"
)
ENUM_RE = re.compile(r"枚举[值]?[：:]\s*([a-z][a-z0-9_]*(?:\s*[/、,，]\s*[a-z][a-z0-9_]*){2,})")
STATE_CLAIM_RE = re.compile(r"([0-9]+|[一二三四五六七八九十])\s*(态|个状态|种状态)")
STATE_TOKEN_RE = re.compile(r"[a-z][a-z0-9_]*")
SNAKE_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])[a-z][a-z0-9]*_[a-z0-9_]*")

# D4：同一动作的“仅 X/Y 可 Z”许可集与“Z ∉ {…} / X/Y 不可 Z”拒绝集。
_GUARD_ALLOW_RE = re.compile(
    r"仅\s*([a-z][a-z0-9_]*(?:\s*[/、,，]\s*[a-z][a-z0-9_]*)+)"
    r"\s*[一-龥]{0,12}?可\s*([一-龥]{2,4})"
)
_GUARD_DENY_SET_RE = re.compile(
    r"state\s*∉\s*[\{（(]?\s*([a-z][a-z0-9_]*(?:\s*[/、,，]\s*[a-z][a-z0-9_]*)+)"
)
_GUARD_DENY_CN_RE = re.compile(
    r"([a-z][a-z0-9_]*(?:\s*[/、,，]\s*[a-z][a-z0-9_]*)+)\s*不可\s*([一-龥]{2,4})"
)
_GUARD_ID_RE = re.compile(r"(?<![A-Za-z0-9-])(?:RULE|ACT)-[A-Z0-9](?:[A-Z0-9_-]*[A-Z0-9])?")

# D5 变体一：基数表述（N 组/类/大项/宫格）。排除章节号/版本号（5.2 大项、v1.1 类）。
CARDINALITY_CLAIM_RE = re.compile(r"(?<![0-9.])([0-9]+|[一二三四五六七八九十])\s*(组|类|大项|宫格)")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|[0-9]{1,2}[.、)])\s+\S")
# D5 变体二：枚举定义位（“枚举：”标记行 + FLD 字典行的纯中文斜杠链单元格）。
ENUM_SITE_RE = re.compile(r"枚举[值]?[：:]\s*([A-Za-z0-9_一-龥]+(?:\s*[/、,，]\s*[A-Za-z0-9_一-龥]+)+)")
CJK_TOKEN_RE = re.compile(r"^[一-龥]{1,8}$")
FLD_ROW_RE = re.compile(r"^\s*\|\s*FLD-[A-Z0-9-]+")
FLD_ENUM_ROW_HINT_RE = re.compile(r"周期|状态|cycle|state", re.I)
CJK_CHAIN_RE = re.compile(r"^[一-龥]{1,8}(?:\s*/\s*[一-龥]{1,8})+$")


@dataclass(frozen=True)
class SemFinding:
    severity: str  # BLOCK / WARN / INFO
    code: str
    message: str
    ref: str = ""


def _frontmatter_end(raw: str) -> int:
    match = FRONTMATTER_RE.match(raw)
    return match.end() if match else 0


def _headings(lines: list[str]) -> list[tuple[int, str, int]]:
    """Real Markdown headings outside fences: (level, title, line_index)."""
    headings: list[tuple[int, str, int]] = []
    in_fence = False
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        elif not in_fence:
            match = re.match(r"^(#{1,6})[ \t]+(.+?)\s*$", line)
            if match:
                title = re.sub(r"\s+#+\s*$", "", match.group(2)).strip()
                headings.append((len(match.group(1)), title, index))
    return headings


def _expand_slash(token: str, line: str, end: int) -> list[tuple[str, int, int]]:
    """Expand ``RULE-SUBMIT-001/002`` numeric chains into extra reference occurrences.

    仅展开纯数字段（001/002 风格）；字母段（HEADER/TOOLBAR）歧义太大，不展开。
    """
    head = token.rsplit("-", 1)[0]
    extras: list[tuple[str, int, int]] = []
    cursor = end
    while True:
        match = re.match(r"\s*/\s*([0-9]+)", line[cursor:])
        if not match:
            break
        segment = match.group(1)
        seg_start = cursor + match.start(1)
        cursor += match.end()
        extras.append((f"{head}-{segment}", seg_start, cursor))
    return extras


def _collect_ids(raw: str) -> tuple[dict[str, tuple[int, str]], dict[str, list[tuple[int, bool]]]]:
    """Split stable-ID occurrences into definition sites and reference sites.

    Returns (defined: id -> (first line, site kind), referenced: id -> [(line, is_navigation)]).
    site kind 为 "registry"（frontmatter/表格首列/事件列/区域列/枚举定义）或 "prose"；
    孤儿定义只对 prose 定义位报告，登记册式定义不报告。
    """
    lines = raw.splitlines()
    fm_end = _frontmatter_end(raw)
    heading_lines = {index for _level, _title, index in _headings(lines)}
    defined: dict[str, tuple[int, str]] = {}
    referenced: dict[str, list[tuple[int, bool]]] = {}
    occurrence_lines: dict[str, list[int]] = {}

    def define(token: str, line_no: int, kind: str) -> None:
        if token not in defined:
            defined[token] = (line_no, kind)

    in_fence = False
    offset = 0
    table_header: list[str] = []  # 当前表格表头单元格
    for index, line in enumerate(lines):
        line_no = index + 1
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        line_start = offset
        offset += len(line) + 1
        in_frontmatter = line_start < fm_end
        is_table = stripped.startswith("|") and not in_fence

        # 维护表头上下文：事件列/区域（REG）列中的 ID 视为登记式定义。
        if is_table and index + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[index + 1]):
            table_header = [cell.strip() for cell in stripped.strip("|").split("|")]
        elif not is_table:
            table_header = []

        occurrences: list[tuple[str, int, int]] = []
        for match in ID_RE.finditer(line):
            token = match.group(0)
            tail = line[match.end():match.end() + 2]
            if tail.startswith("*") or tail.startswith("-*"):
                continue  # 通配家族引用（ACT-DIFF-*），不参与判定
            occurrences.append((token, match.start(), match.end()))
            occurrences.extend(_expand_slash(token, line, match.end()))
        if not occurrences:
            continue
        for token, _s, _e in occurrences:
            occurrence_lines.setdefault(token, []).append(line_no)

        if in_frontmatter:
            for token, _s, _e in occurrences:
                define(token, line_no, "registry")
            continue
        if in_fence:
            for machine in re.finditer(rf"^\s*-?\s*id:\s*['\"]?((?:{_FAMILY})-[A-Z0-9][A-Z0-9_-]*)", line):
                define(machine.group(1).rstrip("-"), line_no, "registry")
            continue

        # 定义位判定（按出现位置）；表格列规则与注解规则相互独立。
        def_spans: set[int] = set()
        cells = [cell.strip() for cell in stripped.strip("|").split("|")] if is_table else []
        first_cell = cells[0].strip("`* ") if cells else ""
        list_lead = re.match(rf"^\s*[-*+]\s+(?:\*\*|__|`)?\s*((?:{_FAMILY})-[A-Z0-9][A-Z0-9_-]*)", line)
        machine_def = re.match(rf"^\s*-?\s*id:\s*['\"]?((?:{_FAMILY})-[A-Z0-9][A-Z0-9_-]*)", line)
        enum_ranges = [
            (line.index(marker) + len(marker), len(line))
            for marker in DEF_ENUM_MARKERS if marker in line
        ]
        # 动作：/事件：枚举内的字母斜杠链（ACT-REG-DATA-VIEW/EDIT/SAVE）逐段展开为定义。
        for lo, hi in enum_ranges:
            for chain in re.finditer(
                rf"((?:{_FAMILY})-[A-Z0-9][A-Z0-9_-]*(?:\s*/\s*[A-Z0-9][A-Z0-9_-]*)*)", line[lo:hi]
            ):
                parts = [part.strip() for part in chain.group(1).split("/")]
                head = parts[0].rsplit("-", 1)[0]
                for part in parts[1:]:
                    if not re.match(rf"(?:{_FAMILY})-", part):
                        define(f"{head}-{part.rstrip('-')}", line_no, "registry")
        backtick_spans = [(m.start(), m.end()) for m in re.finditer(r"`[^`]*`", line)]
        for token, start, end in occurrences:
            is_def = False
            kind = "prose"
            if index in heading_lines:
                is_def = True
            if is_table and first_cell and token in first_cell:
                is_def, kind = True, "registry"
            if is_table and table_header:
                column = line[:start].count("|") - 1
                header_cell = table_header[column] if 0 <= column < len(table_header) else ""
                if "事件" in header_cell:
                    is_def, kind = True, "registry"
                elif token.startswith("REG-") and (header_cell == "REG" or "区域" in header_cell):
                    is_def, kind = True, "registry"
                elif token.startswith("VIEW-") and ("落点" in header_cell or "目标" in header_cell):
                    is_def, kind = True, "registry"
            if list_lead and list_lead.group(1).rstrip("-") == token and list_lead.start(1) == start:
                is_def = True
            if machine_def and machine_def.group(1).rstrip("-") == token:
                is_def = True
            if end < len(line) and line[end] in "（(":
                is_def = True  # ID（…）注解定义
            if re.search(rf"」\s*[（(][^（）()]{{0,60}}{re.escape(token)}\b", line):
                is_def = True  # 「控件标签」（ID…）定义
            if any(lo <= start < hi for lo, hi in enum_ranges):
                is_def, kind = True, "registry"  # 动作：/事件：枚举定义
            if is_def:
                def_spans.add(start)
                define(token, line_no, kind)

        for token, start, end in occurrences:
            if start in def_spans:
                continue
            if any(lo <= start < hi for lo, hi in backtick_spans):
                continue  # 行内代码字面量：跨文件外部引用（intake/stage0 登记册等），豁免
            prefix = line[max(0, start - 30):start]
            is_nav = bool(NAV_RE.search(prefix))
            referenced.setdefault(token, []).append((line_no, is_nav))

    # 仅在示例行出现且未定义的 ID 整体豁免（格式举例，如 COR-ENTERPRISE_DATA-001）。
    for token, lines_seen in occurrence_lines.items():
        if token in defined:
            continue
        if all(
            any(marker in raw_line for marker in EXAMPLE_MARKERS)
            for raw_line in (lines[ln - 1] for ln in set(lines_seen))
        ):
            referenced.pop(token, None)
    return defined, referenced


def check_dangling_refs(raw: str) -> list[SemFinding]:
    """D2: 引用集 − 定义集 = 悬空引用；定义集 − 引用集 = 孤儿定义。"""
    defined, referenced = _collect_ids(raw)
    findings: list[SemFinding] = []
    for token in sorted(set(referenced) - set(defined)):
        sites = referenced[token]
        nav_lines = [line_no for line_no, is_nav in sites if is_nav]
        if nav_lines:
            findings.append(SemFinding(
                "BLOCK", "PRD-DANGLING-REF",
                f"正文以“见/详见”导航式引用 {token}，但全文没有该 ID 的定义位，读者与下游工件将断链",
                f"{token}@line {nav_lines[0]}",
            ))
        else:
            first = sites[0][0]
            findings.append(SemFinding(
                "WARN", "PRD-DANGLING-REF",
                f"引用了未显式定义的 ID {token}（非导航式引用，降级 WARN）；若为笔误请修正，否则补定义位",
                f"{token}@line {first}",
            ))
    for token in sorted(set(defined) - set(referenced)):
        first_line, kind = defined[token]
        if kind != "prose":
            continue  # 登记册式定义（frontmatter/字典表/事件列/枚举）天然无前向引用，不报告
        findings.append(SemFinding(
            "WARN", "PRD-ORPHAN-DEF",
            f"{token} 只有定义、正文无引用；若已废弃请移除，否则在正文/追溯中引用",
            f"{token}@line {first_line}",
        ))
    return findings


def check_prefix_collision(raw: str) -> list[SemFinding]:
    """D1: 截断式 ID 生成规则作用到同文档枚举后多对一 → 碰撞。"""
    lines = raw.splitlines()
    fm_end = _frontmatter_end(raw)
    in_fence = False
    offset = 0
    rules: list[tuple[str, int | None, int, str]] = []  # (family, width, line_no, sentence)
    enums: list[list[str]] = []
    for index, line in enumerate(lines):
        line_no = index + 1
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            offset += len(line) + 1
            continue
        line_start = offset
        offset += len(line) + 1
        if in_fence or line_start < fm_end:
            continue
        for match in TRUNC_TEMPLATE_RE.finditer(line):
            sentence = next(
                (seg for seg in re.split(r"[。；;]", line) if match.group(0) in seg),
                line,
            )
            if any(marker in sentence for marker in NEGATION_MARKERS):
                continue  # 禁止性说明（“禁止使用前三位截断”）不是生成规则
            width = None
            if match.group(2):
                width = int(match.group(2)) if match.group(2).isdigit() else CN_NUM.get(match.group(2))
            rules.append((match.group(1), width, line_no, sentence.strip()))
        for enum_match in ENUM_RE.finditer(line):
            tokens = [item.strip() for item in re.split(r"[/、,，]", enum_match.group(1)) if item.strip()]
            if len(tokens) >= 2:
                enums.append(tokens)
    findings: list[SemFinding] = []
    for family, width, line_no, sentence in rules:
        if width is None:
            findings.append(SemFinding(
                "INFO", "PRD-ID-PREFIX-COLLISION",
                f"发现截断式 ID 生成规则（{family}-…），但未给出截断宽度，无法静态判定碰撞",
                f"line {line_no}",
            ))
            continue
        if not enums:
            findings.append(SemFinding(
                "INFO", "PRD-ID-PREFIX-COLLISION",
                f"发现截断式 ID 生成规则（{family}-…，前 {width} 位），但文档内未定位 code 枚举，无法静态判定碰撞",
                f"line {line_no}",
            ))
            continue
        groups: dict[str, list[str]] = {}
        for tokens in enums:
            for token in tokens:
                groups.setdefault(token.upper()[:width], []).append(token)
        collisions = {prefix: sorted(set(members)) for prefix, members in groups.items() if len(set(members)) > 1}
        if collisions:
            rendered = "；".join(f"{prefix}←{'、'.join(members)}" for prefix, members in sorted(collisions.items()))
            findings.append(SemFinding(
                "BLOCK", "PRD-ID-PREFIX-COLLISION",
                f"{family} 关联号按前 {width} 位截断生成会发生多对一碰撞：{rendered}。改用完整 code 或保证截断后唯一",
                f"line {line_no}",
            ))
    return findings


def _stm_block(lines: list[str], stm_id: str) -> list[str] | None:
    headings = _headings(lines)
    for index, (level, title, line_index) in enumerate(headings):
        if stm_id not in title:
            continue
        end = len(lines)
        for next_level, _next_title, next_index in headings[index + 1:]:
            if next_level <= level:
                end = next_index
                break
        return lines[line_index:end]
    return None


def _stm_state_count(block: list[str]) -> set[str]:
    """统计状态机表覆盖的状态：状态列首词 + 全表 snake_case 状态词。"""
    states: set[str] = set()
    table = [line for line in block if line.strip().startswith("|")]
    if len(table) < 3:
        return states
    header_cells = [cell.strip() for cell in table[0].strip().strip("|").split("|")]
    state_columns = [
        col for col, cell in enumerate(header_cells)
        if "状态" in cell
        and not any(marker in cell for marker in ("动作", "触发", "事件", "状态机", "变化", "副作用"))
    ]
    for row in table[2:]:
        cells = [cell.strip().strip("`") for cell in row.strip().strip("|").split("|")]
        for col in state_columns:
            if col < len(cells):
                states.update(STATE_TOKEN_RE.findall(cells[col]))
        for cell in cells:
            states.update(SNAKE_TOKEN_RE.findall(cell))
    return states


def check_state_count(raw: str) -> list[SemFinding]:
    """D3: 文中“N 态”措辞与对应 STM-* 状态机表的状态数必须一致。"""
    lines = raw.splitlines()
    fm_end = _frontmatter_end(raw)
    in_fence = False
    offset = 0
    findings: list[SemFinding] = []
    for index, line in enumerate(lines):
        line_no = index + 1
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            offset += len(line) + 1
            continue
        line_start = offset
        offset += len(line) + 1
        if in_fence or line_start < fm_end:
            continue
        claims = list(STATE_CLAIM_RE.finditer(line))
        if not claims:
            continue
        stm_ids = STM_RE.findall(line)
        if not stm_ids:
            continue  # 未绑定具体 STM 的措辞不判定
        stm_id = stm_ids[0]
        block = _stm_block(lines, stm_id)
        if block is None:
            continue  # 找不到对应状态机章节 → 不报
        states = _stm_state_count(block)
        if not states:
            continue  # 章节内没有可统计的状态机表 → 不报
        for claim in claims:
            claimed = int(claim.group(1)) if claim.group(1).isdigit() else CN_NUM[claim.group(1)]
            if claimed != len(states):
                findings.append(SemFinding(
                    "BLOCK", "PRD-STATE-COUNT-MISMATCH",
                    f"文中称{claim.group(1)}{claim.group(2)}，但 {stm_id} 状态机表覆盖 {len(states)} 个状态"
                    f"（{'、'.join(sorted(states))}）。同步措辞或状态机表",
                    f"{stm_id}@line {line_no}",
                ))
    return findings


def _prose_lines(raw: str) -> list[tuple[int, str]]:
    """(line_no, line) pairs outside fenced code and YAML frontmatter."""
    lines = raw.splitlines()
    fm_end = _frontmatter_end(raw)
    result: list[tuple[int, str]] = []
    in_fence = False
    offset = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            offset += len(line) + 1
            continue
        line_start = offset
        offset += len(line) + 1
        if in_fence or line_start < fm_end:
            continue
        result.append((index + 1, line))
    return result


def _is_example_line(line: str) -> bool:
    return any(marker in line for marker in EXAMPLE_MARKERS)


def check_guard_contradiction(raw: str) -> list[SemFinding]:
    """D4（弱信号，WARN）：同一动作的“仅 X/Y 可 Z”许可集与“∉/不可”拒绝集显式互斥。

    配对条件（宁严勿宽）：两侧集合均 ≥2 个状态词，且绑定同一 RULE/ACT ID，
    或许可侧动词出现在拒绝侧同一行。两侧集合求交为空说明守卫的显式拒绝域
    完全没有覆盖规则声明的“仅”许可域（真实案例：RULE-SELECT-001 仅 due/ready
    可勾选 vs ACT-UNIT-SELECT 守卫 state ∉ succeeded/not_due/running）。
    信号不明确（无动词、无 ID、单侧缺失）一律不报。
    """
    allows: list[tuple[frozenset[str], str, str, int]] = []  # (states, verb, bound_id, line_no)
    denies: list[tuple[frozenset[str], str, str, int, str]] = []  # (states, verb, bound_id, line_no, line)
    for line_no, line in _prose_lines(raw):
        if _is_example_line(line):
            continue
        bound = _GUARD_ID_RE.search(line)
        bound_id = bound.group(0) if bound else ""
        for match in _GUARD_ALLOW_RE.finditer(line):
            states = frozenset(STATE_TOKEN_RE.findall(match.group(1)))
            if len(states) >= 2:
                allows.append((states, match.group(2), bound_id, line_no))
        for match in _GUARD_DENY_SET_RE.finditer(line):
            states = frozenset(STATE_TOKEN_RE.findall(match.group(1)))
            if len(states) >= 2:
                denies.append((states, "", bound_id, line_no, line))
        for match in _GUARD_DENY_CN_RE.finditer(line):
            states = frozenset(STATE_TOKEN_RE.findall(match.group(1)))
            if len(states) >= 2:
                denies.append((states, match.group(2), bound_id, line_no, line))
    findings: list[SemFinding] = []
    seen: set[tuple[frozenset[str], frozenset[str]]] = set()
    for allow_states, allow_verb, allow_id, allow_line in allows:
        for deny_states, deny_verb, deny_id, deny_line, deny_text in denies:
            if deny_line == allow_line:
                continue
            paired = bool(allow_id and deny_id and allow_id == deny_id)
            paired = paired or bool(allow_verb and allow_verb in deny_text)
            paired = paired or bool(deny_verb and deny_verb and allow_verb == deny_verb)
            if not paired or allow_states & deny_states:
                continue
            key = (allow_states, deny_states)
            if key in seen:
                continue
            seen.add(key)
            findings.append(SemFinding(
                "WARN", "PRD-GUARD-CONTRADICTION",
                f"“仅 {'/'.join(sorted(allow_states))} 可{allow_verb}”（line {allow_line}）与"
                f"“∉/不可 {'/'.join(sorted(deny_states))}”（line {deny_line}）的显式状态集合互斥："
                f"守卫拒绝域未覆盖规则许可域，其余状态两处结论可能相反。对齐两处状态集合",
                f"line {allow_line} vs line {deny_line}",
            ))
    return findings


def _introduced_enum_count(lines: list[str], line_no: int) -> int | None:
    """claim 直接引出的结构化枚举项数：其后 4 行内开始的连续列表段或表格数据行数。

    中间跨标题、列表/表格不以 claim 开头引出（如 claim 自身在列表/表格中）时返回 None。
    """
    for lookahead in range(line_no, min(line_no + 4, len(lines))):
        candidate = lines[lookahead]
        if re.match(r"^#{1,6}\s", candidate):
            return None
        if _BULLET_RE.match(candidate):
            cursor = lookahead
            while cursor < len(lines) and _BULLET_RE.match(lines[cursor]):
                cursor += 1
            return cursor - lookahead
        if (
            candidate.lstrip().startswith("|")
            and lookahead + 1 < len(lines)
            and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[lookahead + 1])
        ):
            cursor = lookahead + 2
            while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
                cursor += 1
            return cursor - lookahead - 2
        if candidate.strip():
            return None  # 非空散文行隔断：枚举不是由该 claim 引出
    return None


def check_enum_cardinality(raw: str) -> list[SemFinding]:
    """D5 变体一（WARN）：“N 组/类/大项/宫格”基数表述与其直接引出的结构化枚举数不符。

    宁严勿宽：一行多个基数表述、claim 在表格行/列表项内、枚举不是由 claim 直接引出
    （其后 4 行内无列表段或表格）时一律不报。
    """
    lines = raw.splitlines()
    findings: list[SemFinding] = []
    for line_no, line in _prose_lines(raw):
        if line.lstrip().startswith("|") or _BULLET_RE.match(line) or _is_example_line(line):
            continue
        claims = list(CARDINALITY_CLAIM_RE.finditer(line))
        if len(claims) != 1:
            continue
        claim = claims[0]
        claimed = int(claim.group(1)) if claim.group(1).isdigit() else CN_NUM[claim.group(1)]
        if not 2 <= claimed <= 12:
            continue
        count = _introduced_enum_count(lines, line_no)
        if count is None or count < 2 or claimed == count:
            continue
        findings.append(SemFinding(
            "WARN", "PRD-ENUM-NOT-DEFINED",
            f"文中称“{claim.group(1)}{claim.group(2)}”，但其引出的枚举清单只有 {count} 项；"
            f"若基数已修订请同步枚举清单，若枚举清单才是最新则修订措辞",
            f"line {line_no}",
        ))
    return findings


def check_enum_value_coverage(raw: str) -> list[SemFinding]:
    """D5 变体二（WARN）：枚举字段的中文取值在枚举定义位之外再未出现。

    枚举定义位：`枚举：` 标记行，以及行内含“周期/状态/cycle/state”语义的 FLD 字典行
    中的纯中文斜杠链单元格（其余 FLD 链如来源/结果类型不判定）。
    ascii code 枚举（如 enterprise_data/person）按机器标识豁免——它们通常只在
    字典中定义一次。仅当同枚举存在“至少一个取值被引用、其余取值零引用”时报告
    （真实案例：周期枚举含“实时”，但状态机与规则从未定义其实时流转）。
    """
    prose = _prose_lines(raw)
    sites: list[tuple[int, list[str]]] = []  # (line_no, cjk tokens)
    site_lines: set[int] = set()
    for line_no, line in prose:
        tokens: list[str] = []
        marked = ENUM_SITE_RE.search(line)
        if marked:
            site_lines.add(line_no)
            tokens = [t for t in re.split(r"[/、,，]\s*", marked.group(1)) if CJK_TOKEN_RE.match(t.strip())]
        elif FLD_ROW_RE.match(line) and FLD_ENUM_ROW_HINT_RE.search(line):
            for cell in (cell.strip().strip("`") for cell in line.strip().strip("|").split("|")):
                if CJK_CHAIN_RE.match(cell):
                    site_lines.add(line_no)
                    tokens.extend(part.strip() for part in cell.split("/"))
        tokens = sorted(set(tokens))
        if len(tokens) >= 2:
            sites.append((line_no, tokens))
    if not sites:
        return []
    coverage_text = "\n".join(line for line_no, line in prose if line_no not in site_lines)
    findings: list[SemFinding] = []
    for line_no, tokens in sites:
        missing = [token for token in tokens if token not in coverage_text]
        if missing and len(missing) < len(tokens):
            findings.append(SemFinding(
                "WARN", "PRD-ENUM-NOT-DEFINED",
                f"枚举取值 {'、'.join(missing)} 在枚举定义位之外（含状态机与规则）再未出现，"
                f"其流转/处理语义未定义；同枚举其余取值（{'、'.join(t for t in tokens if t not in missing)}）均有引用",
                f"line {line_no}",
            ))
    return findings


def run_semantic_checks(raw: str) -> list[SemFinding]:
    """Run D2/D1/D3 (BLOCK-capable) and D4/D5 (WARN-only) in one pass set; wired into gate --profile prd."""
    return [
        *check_dangling_refs(raw),
        *check_prefix_collision(raw),
        *check_state_count(raw),
        *check_guard_contradiction(raw),
        *check_enum_cardinality(raw),
        *check_enum_value_coverage(raw),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="PRD 语义一致性静态检查（悬空引用/前缀碰撞/态数不符）")
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    if not args.document.is_file():
        print(f"BLOCK: GATE-NOT-FILE: 输入 PRD 不存在: {args.document}")
        return 1
    findings = run_semantic_checks(args.document.read_text(encoding="utf-8"))
    for item in findings:
        ref = f" [{item.ref}]" if item.ref else ""
        print(f"{item.severity}: {item.code}: {item.message}{ref}")
    if any(item.severity == "BLOCK" for item in findings):
        return 1
    if not findings:
        print("PASS: PRD 语义一致性检查通过（无悬空引用、无前缀碰撞、态数一致）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
