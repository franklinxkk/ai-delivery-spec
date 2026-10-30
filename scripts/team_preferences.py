"""Resolve external team assets; no copying into the installed skill or execution."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

PROFILE_NAME = ".ads-profile.json"
KEYS = {"schema_version", "extends", "template", "design", "interaction"}


class PreferenceError(ValueError):
    pass


def outside_install(path: Path, install_root: Path) -> None:
    if path == install_root or install_root in path.parents:
        raise PreferenceError(f"团队资料必须保存在 skill 安装目录外 / keep team assets outside the skill: {path}")


def local_path(value: str, base: Path) -> Path:
    if not isinstance(value, str) or not value.strip() or re.match(r"^[A-Za-z][\w+.-]*://", value):
        raise PreferenceError(f"需要非空本地文件路径 / expected a local file path: {value!r}")
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def profile_path(path: Path) -> Path:
    path = path.resolve()
    return path / PROFILE_NAME if path.is_dir() else path


def read_profile(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreferenceError(f"无法读取团队绑定 / cannot read team binding {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        raise PreferenceError(f"团队绑定格式不支持 / unsupported team binding format: {path}")
    if set(data) - KEYS:
        raise PreferenceError(f"未知绑定字段 / unknown binding fields in {path}: {sorted(set(data) - KEYS)}")
    return data


def _expand(path: Path, stack: tuple[Path, ...], install_root: Path, override: dict | None = None) -> tuple[dict, list[str]]:
    path = path.resolve()
    outside_install(path, install_root)
    if path in stack:
        raise PreferenceError("团队绑定循环 / cyclic team binding: " + " -> ".join(map(str, (*stack, path))))
    data = override if override is not None else read_profile(path)
    result: dict = {}
    sources: list[str] = []
    if data.get("extends") is not None:
        parent = profile_path(local_path(data["extends"], path.parent))
        result, sources = _expand(parent, (*stack, path), install_root)
    protected = list(result.pop("referenced_resources", []))
    for key in ("template", "design", "interaction"):
        if key not in data:
            continue
        value = data[key]
        if key == "template":
            result[key] = str(local_path(value, path.parent)) if value is not None else None
        else:
            if not isinstance(value, list):
                raise PreferenceError(f"{key} 必须是文件列表 / must be a file list: {path}")
            result[key] = [str(local_path(item, path.parent)) for item in value]
        referenced = ([result[key]] if result[key] else []) if key == "template" else result[key]
        protected.extend(referenced)
        result.setdefault("declared_by", {})[key] = str(path)
    sources.append(str(path))
    result["referenced_resources"] = list(dict.fromkeys(protected))
    return result, sources


def resolve_preferences(project: Path, install_root: Path, *, explicit_profile: Path | None = None,
                        template_override: Path | None = None, pending: tuple[Path, dict] | None = None) -> dict:
    """Outer defaults -> nearest project -> explicit profile -> explicit template."""
    project, install_root = project.resolve(), install_root.resolve()
    outside_install(project, install_root)
    candidates = [parent / PROFILE_NAME for parent in reversed((project, *project.parents))]
    # A broken/directory binding is an error, not permission to use defaults.
    candidates = [p for p in candidates if p.exists() or p.is_symlink() or (pending and p == pending[0])]
    if explicit_profile is not None:
        candidates.append(profile_path(explicit_profile))
    resolved: dict = {"template": None, "design": [], "interaction": [], "declared_by": {}}
    sources: list[str] = []
    protected: list[str] = []
    for candidate in candidates:
        settings, chain = _expand(candidate, (), install_root, pending[1] if pending and candidate == pending[0] else None)
        protected.extend(settings.pop("referenced_resources", []))
        declared = settings.pop("declared_by", {})
        resolved.update(settings)
        resolved["declared_by"].update(declared)
        sources.extend(chain)
    if template_override is not None:
        resolved["template"] = str(template_override.resolve())
        resolved["declared_by"]["template"] = "explicit --template-file"
    for key in ("template", "design", "interaction"):
        paths = [resolved[key]] if key == "template" and resolved[key] else ([] if key == "template" else resolved[key])
        for value in paths:
            path = Path(value)
            outside_install(path, install_root)
            if not path.is_file():
                raise PreferenceError(f"配置的 {key} 文件不存在 / configured file missing: {path}")
            if key == "template" and path.suffix.lower() not in {".md", ".docx"}:
                raise PreferenceError(f"模板仅支持 Markdown 或 DOCX / template must be .md or .docx: {path}")
    resolved["profiles"] = list(dict.fromkeys(sources))
    # Preserve all referenced originals, including overridden defaults. They
    # need not be current consumers to remain authoritative team files.
    if template_override is not None:
        protected.append(str(template_override.resolve()))
    resolved["referenced_resources"] = list(dict.fromkeys(protected))
    resolved["project"] = str(project)
    return resolved


def relative_reference(path: Path, directory: Path) -> str:
    """Portable within a shared directory tree; absolute across Windows drives."""
    try:
        return Path(os.path.relpath(path.resolve(), directory.resolve())).as_posix()
    except ValueError:
        return str(path.resolve())


def bind_preferences(args, install_root: Path) -> dict:
    project = args.project.resolve()
    outside_install(project, install_root.resolve())
    target = project / PROFILE_NAME
    outside_install(target.resolve(), install_root.resolve())
    if target.is_symlink() or (target.exists() and target.stat().st_nlink > 1):
        raise PreferenceError("不能通过共享文件链接改写团队绑定；请用 --team 引用 / do not rewrite a symlinked or hardlinked binding; inherit with --team")
    data = read_profile(target) if target.exists() else {"schema_version": 1}
    changed = False
    for key, attribute in (("extends", "team"), ("template", "template_file"), ("design", "design_file"), ("interaction", "interaction_file")):
        value = getattr(args, attribute, None)
        clear = getattr(args, "clear_" + ("team" if key == "extends" else key), False)
        if value is not None and clear:
            raise PreferenceError(f"不能同时设置和清除 {key} / cannot set and clear the same field")
        if value is not None:
            values = value if isinstance(value, list) else [value]
            paths = [profile_path(item) if key == "extends" else item.resolve() for item in values]
            stored = [relative_reference(item, project) for item in paths]
            data[key] = stored if key in {"design", "interaction"} else stored[0]
            changed = True
        elif clear:
            data[key] = [] if key in {"design", "interaction"} else None
            changed = True
    if not changed:
        raise PreferenceError("请指定要绑定的团队资料 / specify team resources to bind")
    resolved = resolve_preferences(project, install_root, pending=(target, data))
    project.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"binding": str(target), **resolved}
