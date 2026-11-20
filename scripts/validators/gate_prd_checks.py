"""5.5 scoped PRD checks; no tier, heading-count or table-count obligations."""
from pathlib import Path
import re
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from requirement_contract import check_spec, load_declarations
from validators.validate_prd_semantics import run_semantic_checks


TABLE_RULE = re.compile(r"\|?\s*:?-{3,}:?(?:\s*\|\s*:?-{3,}:?)*\s*\|?")
AUTHORING_LABEL = re.compile(
    r"^(?:scope|behavior|acceptance|preconditions?|action|expected result|"
    r"范围|行为|验收|前提|操作|预期结果|场景编号)\s*[:：]\s*", re.I
)
PLACEHOLDER = re.compile(
    r"\{[^{}]+\}|TBD|TODO|placeholder|lorem ipsum|待补(?:充)?|待填写|待完善|占位(?:内容|文本)?|[-—–…]+",
    re.I,
)


def placeholder_only(body: str) -> bool:
    """Recognize a wholly unfilled Markdown skeleton; preserve code and mixed prose."""
    visible = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    if re.search(r"(?m)^(?:[ \t]*(?:`{3,}|~{3,})|(?: {4}|\t)[ \t]*\S)", visible):
        return False
    # The bundled template uses multi-line brace prompts as well as single-line fields.
    visible = re.sub(r"(?m)^[ \t]*\{[^{}\n]*\n[^{}]*\}[ \t]*$", "{placeholder}", visible)
    lines = visible.splitlines()
    found_placeholder = False
    for index, raw in enumerate(lines):
        line = raw.strip()
        if re.match(r"^#{1,6}(?:[ \t]|$)", line) or re.fullmatch(r"(?:[-=*_][ \t]*){3,}", line):
            continue
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if "|" in line and (TABLE_RULE.fullmatch(line) or TABLE_RULE.fullmatch(next_line)):
            continue
        for cell in line.split("|"):
            text = re.sub(r"^(?:[-+*]|\d+[.)])[ \t]+", "", cell.strip())
            text = AUTHORING_LABEL.sub("", text).strip("*_ \t")
            if text:
                if not PLACEHOLDER.fullmatch(text):
                    return False
                found_placeholder = True
    return found_placeholder


def line_scopes(raw: str) -> dict[int, set[str]]:
    """Only explicit requirement headings/rows establish textual ownership."""
    result, stack, fenced = {}, [], False
    for number, line in enumerate(raw.splitlines(), 1):
        if line.lstrip().startswith((chr(96) * 3, "~~~")):
            fenced = not fenced
        if fenced:
            continue
        refs = set(re.findall(r"\bREQ-[A-Z0-9][A-Z0-9_-]*", line))
        heading = re.match(r"^(#{1,6})\s+", line)
        if heading:
            level = len(heading[1])
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, refs))
        inherited = next((s for _, s in reversed(stack) if s), set())
        result[number] = refs if line.strip().startswith("|") and refs else inherited
    return result


class PRDChecks:
    def check_prd(self, path: Path, level: str = "auto", *, stage: str = "specify", scope_refs: tuple[str, ...] = ()) -> None:
        try:
            raw = self.read(path).lstrip("\ufeff")
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PRD-READ", path, str(exc))
            return
        if path.suffix.lower() not in {".md", ".markdown"}:
            self.add("BLOCK", "PRD-FORMAT", path, "Use readable Markdown for this checker; inspect other formats separately")
            return
        metadata, body = {}, raw
        lines = raw.splitlines(keepends=True)
        if lines and lines[0].strip() == "---":
            end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
            if end is None:
                self.add("BLOCK", "PRD-FRONTMATTER", path, "Frontmatter is not closed")
                return
            try:
                fragment = "".join(lines[1:end])
                metadata = load_declarations(fragment) if fragment.strip() else {}
                if not isinstance(metadata, dict):
                    raise ValueError("Frontmatter must be an object")
            except (yaml.YAMLError, ValueError) as exc:
                mark = getattr(exc, "problem_mark", None)
                message = f"YAML syntax invalid at document line {mark.line + 2}, column {mark.column + 1}; check brackets, quotes and indentation" if mark else str(exc)
                self.add("BLOCK", "PRD-FRONTMATTER", path, message)
                return
            body = "\n" * (end + 1) + "".join(lines[end + 1:])
        ownership = line_scopes(raw) if scope_refs else {}
        if scope_refs:
            body = "\n".join(line if not ownership.get(n) or ownership[n] & set(scope_refs) else ""
                             for n, line in enumerate(body.splitlines(), 1))
        findings, routing = check_spec(metadata, body, stage=stage, scope=scope_refs, legacy_level=level)
        self.metrics["routing"] = routing
        self.metrics["unknown_summary"] = routing["unknown_summary"]
        self.metrics["document_language"] = metadata.get("document_language", "")
        for finding in findings:
            self.add(finding["severity"], finding["code"], path, finding["message"], finding["ref"], message_en=finding.get("message_en", ""))
        if placeholder_only(body):
            self.add(
                "BLOCK", "SPEC-EMPTY", path,
                "正文只有编写占位。请在现有位置补充本次实际行为和可观察结果；不要求固定章节。",
                "body",
                message_en="The body contains only authoring placeholders. Add the actual behavior and observable result; fixed sections are not required.",
            )
        excluded, unlocated = 0, 0
        for item in run_semantic_checks(raw):
            severity, code, message = item.severity, item.code, item.message
            if scope_refs:
                positions = [int(n) for n in re.findall(r"@line (\d+)", item.ref)]
                owned = [ownership.get(n, set()) for n in positions]
                if owned and all(owned) and not any(s & set(scope_refs) for s in owned):
                    excluded += 1
                    continue
                if severity == "BLOCK" and (not owned or not all(owned)):
                    severity, code = "GAP", "SPEC-TEXT-SCOPE-NOT-PROVEN"
                    message = f"Locate the scope of {item.code} before treating it as a local blocker: {message}"
                    unlocated += 1
            self.add(severity, code, path, message, item.ref)
        self.metrics["text_scope"] = {"requested": list(scope_refs), "excluded_findings": excluded, "unlocated_findings": unlocated}
