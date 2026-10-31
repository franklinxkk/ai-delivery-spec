"""Fresh scaffolds must not invent decisions; shipped links need shipped targets."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/ai_delivery_spec_cli.py"


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8")


def read(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def schema_errors(kind, document):
    schema = json.loads((ROOT / f"schemas/{kind}.schema.json").read_text(encoding="utf-8"))
    return list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document))


def test_actual_initializers_do_not_invent_signoff_execution_or_priority(tmp_path):
    requirements = tmp_path / "requirements"
    delivery = tmp_path / "delivery"
    for args in [("init-requirements", "--output", requirements),
                 ("init-delivery", "--output", delivery, "--truth-layout", "monolith")]:
        result = run(CLI, *args)
        assert result.returncode == 0, result.stdout + result.stderr
    review = read(requirements / "reviews/REVIEW-CORE-001.yaml")
    acceptance = read(requirements / "acceptance/ARUN-CORE-001.yaml")
    register = read(requirements / "register.yaml")
    change = read(requirements / "changes/CHG-CORE-001.yaml")
    truth = read(delivery / "truth/product-truth.yaml")
    assert review["sign_offs"] == [] and review["findings"] == []
    assert review["status"] == "scheduled" and not review["conclusion"]
    assert acceptance["executed_at"] is None and acceptance["conclusion"] == "pending"
    assert acceptance["sign_offs"] == acceptance["residual_issues"] == acceptance["evidence_catalog"] == []
    assert all(item["result"] == "not_run" and not item["evidence_refs"] for item in acceptance["items"])
    assert register["audit_log"] == [] and change["audit_log"] == []
    assert "requested_at" not in change["request"]
    for requirement in register["requirements"] + truth["requirements"]:
        assert requirement["stage"] == "submitted" and "priority" not in requirement
    assert all(item["status"] == "proposed" for item in truth["assertions"])
    assert all("priority" not in item for item in truth["acceptance"])
    for name, document in [("review-record", review), ("acceptance-run", acceptance),
                           ("requirement-register", register), ("change-package", change),
                           ("product-truth", truth)]:
        assert not schema_errors(name, document), name
    # Pending is a valid record, not permission to report acceptance as completed.
    acceptance["conclusion"] = "accepted"
    path = requirements / "acceptance/forged.yaml"
    path.write_text(yaml.safe_dump(acceptance, allow_unicode=True), encoding="utf-8")
    rejected = run(ROOT / "scripts/validators/validate_acceptance_run.py", path)
    assert rejected.returncode != 0
    acceptance["executed_at"] = "2026-10-30T00:00:00Z"
    path.write_text(yaml.safe_dump(acceptance, allow_unicode=True), encoding="utf-8")
    # Supplying a valid timestamp still cannot promote unrun/unsigned work.
    rejected = run(ROOT / "scripts/validators/validate_acceptance_run.py", path)
    assert rejected.returncode != 0


@pytest.mark.parametrize("result", ["pass", "fail", "blocked"])
def test_actual_execution_requires_real_timestamp(result):
    doc = read(ROOT / "references/templates/acceptance-run-template.yaml")
    doc["items"][0]["result"] = result
    assert schema_errors("acceptance-run", doc)
    doc["executed_at"] = "2026-10-30T00:00:00Z"
    assert not schema_errors("acceptance-run", doc)


def test_neutral_inventory_has_no_claimed_observations():
    doc = read(ROOT / "references/templates/stage0-inventory-template.yaml")
    assert doc["inventory_status"] == "in_progress" and doc["target_status"] == "draft"
    assert not doc.get("critical_chains") and not doc["reachability_breaks"]
    assert all(item["classification"] == "unknown" for item in doc["items"])
    assert not schema_errors("stage0-inventory", doc)


def test_optional_priority_is_not_an_unvalidated_priority():
    truth = read(ROOT / "references/templates/product-truth-template.yaml")
    truth["requirements"][0]["priority"] = "whatever"
    assert schema_errors("product-truth", truth)


def test_scheduled_review_cannot_be_completed_without_roles_and_signoff():
    doc = read(ROOT / "references/templates/review-record-template.yaml")
    doc.update(status="completed", reviewed_at="2026-10-30T00:00:00Z")
    assert schema_errors("review-record", doc)


def test_discovery_template_does_not_create_unobserved_unknowns_or_allow_unknown_priority():
    doc = read(ROOT / "references/templates/discovery-contract-template.yaml")
    assert doc["unknowns"] == [] and "discovery_decision" not in doc
    assert not schema_errors("discovery-contract", doc)
    doc["unknowns"].append({"id": "UNK-A", "question": "Who decides?", "impact": "role",
                            "owner": "Product owner", "status": "open"})
    assert schema_errors("discovery-contract", doc)


def builder():
    spec = importlib.util.spec_from_file_location("cr1_package_builder", ROOT / "maintainer/tools/build_runtime_package.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_packager_rejects_source_only_link_before_zip_creation(tmp_path, monkeypatch):
    build = builder()
    repo = tmp_path / "repo"
    (repo / "maintainer").mkdir(parents=True)
    (repo / "SKILL.md").write_text("# AI Delivery Spec 5.5.6-cr1\n", encoding="utf-8")
    (repo / "README.md").write_text("[Evidence](maintainer/evidence.md)\n", encoding="utf-8")
    (repo / "maintainer/evidence.md").write_text("Actual source-only evidence", encoding="utf-8")
    config = repo / "maintainer/runtime-package.yaml"
    config.write_text("include: [SKILL.md, README.md]\nmax_files: 2\n", encoding="utf-8")
    archive = tmp_path / "runtime.zip"
    monkeypatch.setattr(build, "ROOT", repo)
    monkeypatch.setattr(build, "CONFIG", config)
    monkeypatch.setattr(sys, "argv", ["build", "--output", str(archive)])
    assert build.main() == 1 and not archive.exists()
    # Pointing at a file that really ships makes the same build distributable.
    (repo / "README.md").write_text("[Start](SKILL.md#start)\n", encoding="utf-8")
    assert build.main() == 0
    with zipfile.ZipFile(archive) as package:
        assert "SKILL.md" in package.namelist() and "maintainer/evidence.md" not in package.namelist()


def test_packaged_link_check_handles_unicode_references_and_code_examples(tmp_path):
    build = builder()
    (tmp_path / "团队 规范.md").write_text("# Team", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        '[Team](<团队 规范.md>)\n[Encoded](%E5%9B%A2%E9%98%9F%20%E8%A7%84%E8%8C%83.md)\n'
        '[ref]: <团队 规范.md>\n[external](https://example.org/path)\n[local](#anchor)\n'
        '```md\n[not an active link](missing.md)\n```\n`[example](missing.md)`\n', encoding="utf-8")
    assert build.runtime_link_failures(tmp_path) == []
    (tmp_path / "README.md").write_text('[missing]: nonexistent.md\n[escape](../outside.md)\n', encoding="utf-8")
    assert len(build.runtime_link_failures(tmp_path)) == 2


def test_packager_rejects_external_symlink_before_staging_private_bytes(tmp_path, monkeypatch):
    build = builder()
    repo = tmp_path / "repo"
    (repo / "maintainer").mkdir(parents=True)
    (repo / "SKILL.md").write_text("# AI Delivery Spec 5.5.6-cr1\n", encoding="utf-8")
    private = tmp_path / "private.md"
    private.write_text("PRIVATE TEAM DATA", encoding="utf-8")
    try:
        (repo / "README.md").symlink_to(private)
    except OSError as exc:
        pytest.skip(f"Host cannot create symlinks: {exc}")
    config = repo / "maintainer/runtime-package.yaml"
    config.write_text("include: [SKILL.md, README.md]\nmax_files: 2\n", encoding="utf-8")
    archive = tmp_path / "runtime.zip"
    monkeypatch.setattr(build, "ROOT", repo)
    monkeypatch.setattr(build, "CONFIG", config)
    monkeypatch.setattr(sys, "argv", ["build", "--output", str(archive)])
    assert build.main() == 1 and not archive.exists() and not (repo / "build").exists()
