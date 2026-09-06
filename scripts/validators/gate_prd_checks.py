"""5.5 scoped PRD checks; no tier, heading-count or table-count obligations."""
from pathlib import Path
import re
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from requirement_contract import check_spec, load_declarations
from validators.validate_prd_semantics import run_semantic_checks


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
                self.add("BLOCK", "PRD-FRONTMATTER", path, str(exc))
                return
            body = "".join(lines[end + 1:])
        findings, routing = check_spec(metadata, body, stage=stage, scope=scope_refs, legacy_level=level)
        self.metrics["routing"] = routing
        self.metrics["document_language"] = metadata.get("document_language", "")
        for finding in findings:
            self.add(finding["severity"], finding["code"], path, finding["message"], finding["ref"])
        ownership = line_scopes(raw) if scope_refs else {}
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
