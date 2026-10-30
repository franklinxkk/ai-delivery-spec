"""User-facing reuse chain, independent from private data and skill installation."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/ai_delivery_spec_cli.py"


def run(*args, cli=CLI, cwd=None):
    return subprocess.run([sys.executable, str(cli), *map(str, args)], text=True,
                          encoding="utf-8", capture_output=True, cwd=cwd)


def ok(*args, cli=CLI):
    result = run(*args, cli=cli)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def profile(path: Path, **values):
    return write(path / ".ads-profile.json", json.dumps({"schema_version": 1, **values}, ensure_ascii=False))


def test_team_md_default_used_in_sibling_projects_without_governance_files(tmp_path):
    team = tmp_path / "团队"
    template = write(team / "需求模板.md", "# 团队骨架\n\n## 业务模块\n保留原始细节。\n")
    design = write(team / "design.md", "抽屉宽度沿用已有组件。")
    interactions = write(team / "interactions.md", "提交失败保留输入。")
    bound = ok("bind-team", "--project", team, "--template-file", template,
               "--design-file", design, "--interaction-file", interactions)
    binding = Path(bound["binding"])
    assert json.loads(binding.read_text(encoding="utf-8"))["template"] == "需求模板.md"
    before = binding.read_bytes()
    for name in ("project-one", "project-two"):
        project = team / name
        copied = ok("init-prd", "--project", project)
        assert copied["status"] == "template_only"
        assert Path(copied["output"]).read_bytes() == template.read_bytes()
        assert [p.name for p in project.iterdir()] == ["PRD.md"]
        resolved = ok("show-team", "--project", project)
        assert resolved["design"] == [str(design)]
        assert resolved["interaction"] == [str(interactions)]
        assert resolved["declared_by"]["template"] == str(binding)
    assert binding.read_bytes() == before


def test_project_override_explicit_override_and_external_link(tmp_path):
    team = tmp_path / "team"
    default = write(team / "default.md", "team original")
    project_template = write(tmp_path / "project.md", "project original")
    once = write(tmp_path / "once.md", "explicit once")
    ok("bind-team", "--project", team, "--template-file", default)
    project = tmp_path / "unrelated" / "project"
    ok("bind-team", "--project", project, "--team", team, "--template-file", project_template)
    binding = (project / ".ads-profile.json").read_bytes()
    a = ok("init-prd", "--project", project)
    assert Path(a["output"]).read_text() == "project original"
    b = ok("init-prd", "--project", project, "--template-file", once, "--output", project / "once.md")
    assert Path(b["output"]).read_text() == "explicit once"
    assert (project / ".ads-profile.json").read_bytes() == binding
    assert ok("show-team", "--project", project)["template"] == str(project_template)


def test_force_cannot_overwrite_shadowed_team_originals(tmp_path):
    team = tmp_path / 'team'
    original = write(team / 'original.md', 'authoritative original')
    old_design = write(team / 'design.md', 'authoritative design')
    once = write(tmp_path / 'once.md', 'one-time template')
    new_design = write(tmp_path / 'new-design.md', 'project design')
    project = team / 'project'
    ok('bind-team', '--project', team, '--template-file', original, '--design-file', old_design)
    ok('bind-team', '--project', project, '--design-file', new_design)
    for target in (original, old_design):
        before = target.read_bytes()
        result = run('init-prd', '--project', project, '--template-file', once,
                     '--output', target, '--force')
        assert result.returncode == 2 and target.read_bytes() == before
    assert not (project / 'PRD.md').exists()


def test_hardlink_output_cannot_overwrite_an_original(tmp_path):
    team = tmp_path / 'team'
    template = write(team / 'template.md', 'template')
    design = write(team / 'design.md', 'design original')
    alias = tmp_path / 'alias.md'
    try:
        os.link(design, alias)
    except OSError as exc:
        pytest.skip(f'host cannot create hardlinks: {exc}')
    ok('bind-team', '--project', team, '--template-file', template, '--design-file', design)
    result = run('init-prd', '--project', team / 'project', '--output', alias, '--force')
    assert result.returncode == 2 and design.read_text() == 'design original'


def test_directory_binding_is_not_silently_ignored(tmp_path):
    project = tmp_path / 'project'
    (project / '.ads-profile.json').mkdir(parents=True)
    result = run('init-prd', '--project', project)
    assert result.returncode == 2 and not (project / 'PRD.md').exists()
    assert run('show-team', '--project', project).returncode == 2


def test_binding_hardlink_cannot_mutate_shared_team_profile(tmp_path):
    template = write(tmp_path / 'template.md', 'template')
    team_profile = profile(tmp_path / 'team', template=str(template))
    project = tmp_path / 'project'
    project.mkdir()
    try:
        os.link(team_profile, project / '.ads-profile.json')
    except OSError as exc:
        pytest.skip(f'host cannot create hardlinks: {exc}')
    before = team_profile.read_bytes()
    result = run('bind-team', '--project', project, '--clear-template')
    assert result.returncode == 2 and team_profile.read_bytes() == before


def test_docx_copy_keeps_original_bytes_and_no_implicit_conversion(tmp_path):
    team = tmp_path / "team"
    team.mkdir()
    template = team / "原模板.docx"
    with zipfile.ZipFile(template, "w") as archive:
        archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')
        archive.writestr("word/styles.xml", "<styles/>")
    digest = hashlib.sha256(template.read_bytes()).hexdigest()
    ok("bind-team", "--project", team, "--template-file", template)
    project = team / "project"
    result = ok("init-prd", "--project", project)
    assert result["status"] == "template_only"
    assert hashlib.sha256(Path(result["output"]).read_bytes()).hexdigest() == digest
    wrong = run("init-prd", "--project", project, "--output", project / "converted.md")
    assert wrong.returncode == 2 and not (project / "converted.md").exists()
    protected = run("init-prd", "--project", project, "--output", template, "--force")
    assert protected.returncode == 2 and hashlib.sha256(template.read_bytes()).hexdigest() == digest


@pytest.mark.parametrize("data", ["not JSON", '{"schema_version":2}', '{"schema_version":true}', '{"schema_version":1,"unknown":1}', '{"schema_version":1,"design":"x"}'])
def test_bad_bindings_never_fallback_or_create_output(tmp_path, data):
    project = tmp_path / "project"
    write(project / ".ads-profile.json", data)
    result = run("init-prd", "--project", project)
    assert result.returncode == 2
    assert not (project / "PRD.md").exists()


def test_missing_configured_template_and_cycles_are_actionable(tmp_path):
    project = tmp_path / "project"
    profile(project, template="missing.md")
    missing = run("init-prd", "--project", project)
    assert missing.returncode == 2 and "missing.md" in missing.stdout
    other = tmp_path / "other"
    profile(project, extends="../other/.ads-profile.json")
    profile(other, extends="../project/.ads-profile.json")
    cycle = run("show-team", "--project", project)
    assert cycle.returncode == 2 and "cyclic" in cycle.stdout
    assert not (project / "PRD.md").exists()


def test_missing_template_can_be_explicitly_overridden_but_not_silently(tmp_path):
    project = tmp_path / "project"
    profile(project, template="missing.md")
    once = write(tmp_path / "once.md", "Explicit authorized replacement")
    result = ok("init-prd", "--project", project, "--template-file", once)
    assert Path(result["output"]).read_bytes() == once.read_bytes()
    assert run("show-team", "--project", project).returncode == 2


def test_existing_prd_preserved_and_clear_options_have_defined_scope(tmp_path):
    team = tmp_path / "team"
    source = write(team / "template.md", "template")
    design = write(team / "design.md", "authoritative design")
    ok("bind-team", "--project", team, "--template-file", source, "--design-file", design)
    project = team / "project"
    original = write(project / "PRD.md", "user modified PRD")
    assert ok("init-prd", "--project", project)["status"] == "preserved"
    assert original.read_text() == "user modified PRD"
    protected = run("init-prd", "--project", project, "--output", design, "--force")
    assert protected.returncode == 2 and design.read_text() == "authoritative design"
    ok("bind-team", "--project", project, "--clear-template", "--clear-design")
    resolved = ok("show-team", "--project", project)
    assert resolved["template"] is None and resolved["design"] == []
    assert source.read_text() == "template"


def test_bind_rejects_install_directory_and_does_not_mutate_on_failure(tmp_path):
    source = write(tmp_path / "template.md", "external")
    result = run("bind-team", "--project", ROOT / "should-not-exist", "--template-file", source)
    assert result.returncode == 2 and not (ROOT / "should-not-exist").exists()
    project = tmp_path / "project"
    result = run("bind-team", "--project", project, "--template-file", tmp_path / "missing.md")
    assert result.returncode == 2 and not project.exists()
    result = run("bind-team", "--project", project, "--template-file", ROOT / "SKILL.md")
    assert result.returncode == 2 and not project.exists()


def test_core_upgrade_leaves_external_bindings_and_files_readable(tmp_path):
    team = tmp_path / "private-team"
    source = write(team / "template.md", "private confidential template")
    ok("bind-team", "--project", team, "--template-file", source)
    snapshot = {p.name: p.read_bytes() for p in team.iterdir()}
    # A different installed-core directory must read the same external profile.
    core = tmp_path / "upgraded-core"
    (core / "scripts").mkdir(parents=True)
    for name in ("ai_delivery_spec_cli.py", "team_preferences.py"):
        shutil.copy2(ROOT / "scripts" / name, core / "scripts" / name)
    write(core / "SKILL.md", "# AI Delivery Spec 5.5.6-cr1\n")
    result = ok("init-prd", "--project", team / "new-project", cli=core / "scripts/ai_delivery_spec_cli.py")
    assert Path(result["output"]).read_bytes() == source.read_bytes()
    assert all((team / name).read_bytes() == before for name, before in snapshot.items())
    assert not any(p.name in snapshot for p in core.rglob("*"))
    version = run("version", cli=core / "scripts/ai_delivery_spec_cli.py")
    assert version.returncode == 0 and "5.5.6-cr1" in version.stdout


def test_builtin_daily_template_has_no_machine_preamble_or_side_files(tmp_path):
    project = tmp_path / "daily"
    result = ok("init-prd", "--project", project)
    assert result["status"] == "template_only"
    text = Path(result["output"]).read_text(encoding="utf-8")
    assert text.startswith("# ") and not text.startswith("---")
    assert sorted(p.name for p in project.iterdir()) == ["PRD.md"]


def test_legacy_custom_root_template_still_works(tmp_path):
    custom = tmp_path / "custom"
    source = write(custom / "templates" / "existing.md", "# Existing custom template\n")
    result = run("init-requirements", "--output", tmp_path / "formal", "--custom-root", custom, "--template", "existing")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "formal/PRD.md").read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
    assert (tmp_path / "formal/manifest.json").is_file()


def test_legacy_init_custom_rejects_default_inside_install(tmp_path):
    existed = (ROOT / "custom").exists()
    result = run("init-custom", cwd=ROOT)
    assert result.returncode == 2 and "--output" in result.stdout
    assert (ROOT / "custom").exists() == existed
    external = tmp_path / "private-extensions"
    result = run("init-custom", "--output", external, cwd=ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    candidate = external / "learning/candidates/project-local/CAND-EXAMPLE.yaml"
    before = candidate.read_bytes()
    assert b"2026-01-01T00:00:00" not in before
    result = run("init-custom", "--output", external, cwd=ROOT)
    assert result.returncode == 0 and candidate.read_bytes() == before


def test_binding_symlink_is_never_written_through(tmp_path):
    original = profile(tmp_path / "team")
    project = tmp_path / "project"
    project.mkdir()
    link = project / ".ads-profile.json"
    try:
        link.symlink_to(original)
    except OSError as exc:
        pytest.skip(f"host cannot create a symlink: {exc}")
    source = write(tmp_path / "template.md", "template")
    before = original.read_bytes()
    result = run("bind-team", "--project", project, "--template-file", source)
    assert result.returncode == 2 and original.read_bytes() == before
