"""Real Git regressions for a skill nested inside a larger project repository."""
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import manage_execution_state as execution


def git(repo, *arguments):
    result = subprocess.run(["git", *arguments], cwd=repo, capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def commit(repo, message):
    git(repo, "-c", "user.name=Scope Test", "-c", "user.email=scope@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", message)


@pytest.fixture
def nested_skill(tmp_path, monkeypatch):
    repo = tmp_path / "parent repo"
    skill = repo / "中文 技能"
    (skill / "schemas").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Skill 5.5.6\n", encoding="utf-8")
    (skill / "源代码.py").write_text("VALUE = 1\n", encoding="utf-8")
    shutil.copyfile(ROOT / "schemas/execution-state.schema.json", skill / "schemas/execution-state.schema.json")
    (repo / "sibling.txt").write_text("stable", encoding="utf-8")
    git(repo, "init", "--quiet")
    git(repo, "add", "--", ".")
    commit(repo, "initial files")
    monkeypatch.setattr(execution, "ROOT", skill)
    return repo, skill


def checkpoint(tmp_path, skill):
    anchors = []
    for kind in ("product_truth", "spec_config"):
        path = tmp_path / f"{kind}.yaml"
        path.write_text("verified: true\n", encoding="utf-8")
        anchors.append(dict(kind=kind, path=str(path), sha256=execution.sha256_file(path)))
    tree_hash, dirty = execution.repository_fingerprint()
    state = dict(
        schema_version="5.0.0", execution_id="EXEC-SCOPE-001", project_id="scope-test",
        contract_kind="product_truth", revision=0, environment="test", configured_environment="test", status="ready",
        versions=dict(expected_skill="5.5.6", repository_skill="5.5.6", installed_skill="5.5.6",
                      installed_skill_path=str(skill), repository_commit=execution.git_commit(),
                      repository_tree_hash=tree_hash, repository_dirty=dirty, dependencies={}),
        risk=dict(profile="minimal", signals=[], high_risk=False, classification_basis="structured_contract"),
        domain_assurance=[], anchors=anchors,
        access_scope=dict(allowed_ids=[], allowed_domains=[], denied_ids=[]),
        stage=dict(current="baseline", sequence=0, turns=0, completed=[], required_gates=[]),
        policy=dict(high_risk_failure="block", low_risk_failure="block", audit_mode="hash_chain", max_turns_per_stage=20),
        previous_state_hash=None, created_at="2026-10-28T00:00:00Z", updated_at="2026-10-28T00:00:00Z")
    state["state_hash"] = execution.object_hash(state, "state_hash")
    assert execution.verify_state_value(state) == []
    return state


def test_sibling_dirty_files_and_commits_do_not_invalidate_skill_checkpoint(nested_skill, tmp_path):
    repo, skill = nested_skill
    state = checkpoint(tmp_path, skill)
    baseline = execution.repository_fingerprint()
    source_commit = execution.git_commit()
    (repo / "sibling.txt").write_text("model output changed", encoding="utf-8")
    (repo / "兄弟 日志.md").write_text("parallel output", encoding="utf-8")
    assert execution.repository_fingerprint() == baseline
    assert execution.verify_state_value(state) == []
    git(repo, "add", "--", "sibling.txt", "兄弟 日志.md")
    commit(repo, "unrelated project changes")
    assert execution.git_commit() == source_commit
    assert execution.repository_fingerprint() == baseline
    assert execution.verify_state_value(state) == []


def test_untracked_chinese_space_path_content_edits_and_removal_are_hashed(nested_skill, tmp_path):
    repo, skill = nested_skill
    original = execution.repository_fingerprint()
    added = skill / "未跟踪 子目录" / "规则 配置.yaml"
    added.parent.mkdir()
    added.write_text("value: 1\n", encoding="utf-8")
    first = execution.repository_fingerprint()
    assert first[0] != original[0] and first[1] is True
    state = checkpoint(tmp_path, skill)
    # The porcelain status stays ??; content must nevertheless change the hash.
    added.write_text("value: 2\n", encoding="utf-8")
    second = execution.repository_fingerprint()
    assert second[0] != first[0] and second[1] is True
    assert "repository tree changed after checkpoint" in execution.verify_state_value(state)
    added.unlink()
    assert execution.repository_fingerprint() == original
    assert "repository tree changed after checkpoint" in execution.verify_state_value(state)


def test_real_tracked_source_change_and_deletion_remain_blocking(nested_skill, tmp_path):
    repo, skill = nested_skill
    state = checkpoint(tmp_path, skill)
    source = skill / "源代码.py"
    source.write_text("VALUE = 2\n", encoding="utf-8")
    assert "repository tree changed after checkpoint" in execution.verify_state_value(state)
    git(repo, "add", "--", "中文 技能/源代码.py")
    commit(repo, "actual skill change")
    failures = execution.verify_state_value(state)
    assert "repository commit changed after checkpoint" in failures
    assert "repository tree changed after checkpoint" in failures
    current = checkpoint(tmp_path, skill)
    source.unlink()
    assert "repository tree changed after checkpoint" in execution.verify_state_value(current)


def test_unborn_parent_repository_still_hashes_untracked_source(tmp_path, monkeypatch):
    repo = tmp_path / "new repo"
    skill = repo / "new skill"
    skill.mkdir(parents=True)
    git(repo, "init", "--quiet")
    monkeypatch.setattr(execution, "ROOT", skill)
    source = skill / "中文 配置.txt"
    source.write_text("first", encoding="utf-8")
    first = execution.repository_fingerprint()
    assert execution.git_commit() == "unavailable"
    source.write_text("second", encoding="utf-8")
    assert execution.repository_fingerprint()[0] != first[0]


def test_no_git_fallback_remains_content_sensitive(tmp_path, monkeypatch):
    skill = tmp_path / "standalone skill"
    skill.mkdir()
    monkeypatch.setattr(execution, "ROOT", skill)
    source = skill / "中文 配置.txt"
    source.write_text("first", encoding="utf-8")
    first = execution.repository_fingerprint()
    source.write_text("second", encoding="utf-8")
    assert execution.repository_fingerprint()[0] != first[0]
