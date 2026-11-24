"""Offline release evidence inventory, using synthetic call and review records."""

import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_release_evidence import main


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(root, name, value):
    (root / name).write_text(value, encoding="utf-8")
    return digest(root / name)


@pytest.fixture
def batch(tmp_path, monkeypatch):
    root = tmp_path
    candidate = root / "rc.zip"
    skill = "candidate instructions"
    with ZipFile(candidate, "w") as archive:
        archive.writestr("SKILL.md", skill)
    tasks = "Same business information.\n1. An extension request.\n2. A message delivery."
    frozen = {
        "source_files": {"SKILL.md": hashlib.sha256(skill.encode()).hexdigest()},
        "task": save(root, "tasks.md", tasks),
        "rubric": save(root, "rubric.md", "frozen expectations"),
        "prompts": {"with.txt": save(root, "with.txt", skill + "\n" + tasks),
                    "without.txt": save(root, "without.txt", tasks)},
    }
    index = {"candidate_sha256": digest(candidate), "authors": [], "reviews": [], "sha256": {}}
    models = ["gpt-6.2-sol", "gpt-6.2-astra", "deepseek-flash"]
    for group, model in enumerate(models):
        cards = []
        for offset, arm in enumerate(("with", "without")):
            card = str(10 * (group + 1) + offset)
            cards.append(card)
            name = f"card-{card}.md"
            index["sha256"][name] = save(root, name, f"1. Answer {card}.\n2. More detail {card}.")
            index["authors"].append(dict(card=card, arm=arm, model=model))
        review = dict(model=models[(group + 1) % 3], cards=cards)
        for stage in ("cold", "judgment"):
            name = f"{stage}-{group}.md"
            index["sha256"][name] = save(root, name, f"{stage} comments on {' and '.join(cards)}")
            review[stage] = name
        index["reviews"].append(review)

    def run():
        index["frozen_inputs_sha256"] = save(root, "frozen-inputs.json", json.dumps(frozen))
        save(root, "release-evidence.json", json.dumps(index))
        return main()

    monkeypatch.setattr(sys, "argv", ["check", "--candidate", str(candidate), "--evidence-dir", str(root)])
    return root, frozen, index, run


def test_complete_inventory(batch, capsys):
    assert batch[3]() == 0
    assert "Evidence inventory complete: 2 scenarios, 6 answers, 6 cross-model reviews" in capsys.readouterr().out


@pytest.mark.parametrize(("case", "message"), [
    ("independent", ""),
    ("shared run", "repeated run ID"),
    ("wrong output", "receipt mismatch"),
    ("wrong input", "receipt mismatch"),
    ("one receipt", "independent run receipts needed"),
])
def test_identical_answers_with_run_records(batch, case, message, capsys):
    root, frozen, index, run = batch
    for author in index["authors"][:2]:
        card = author["card"]
        output = f"card-{card}.md"
        # The same business answer may also apply to two different scenarios.
        index["sha256"][output] = save(root, output, "1. Confirm separately.\n2. Confirm separately.")
        if card == "11" and case == "one receipt":
            continue
        receipt = {
            "run_id": "shared" if case == "shared run" else f"invocation-{card}",
            "model": author["model"],
            "input_sha256": frozen["prompts"][author["arm"] + ".txt"],
            "output_sha256": index["sha256"][output],
        }
        if case == "wrong output":
            receipt["output_sha256"] = "0" * 64
        if case == "wrong input":
            receipt["input_sha256"] = "0" * 64
        filename = f"receipt-{card}.json"
        index["sha256"][filename] = save(root, filename, json.dumps(receipt))
        author["receipt"] = filename
    assert run() == (1 if message else 0)
    assert message in capsys.readouterr().err


@pytest.mark.parametrize(("defect", "reason"), [
    ("missing arm", "missing model/arm"),
    ("duplicate arm", "duplicate model/arm"),
    ("borrowed answer", "independent run receipts needed"),
    ("stale zip", "SHA-256 mismatch: rc.zip"),
    ("stale source", "candidate source changed"),
    ("different task", "task missing"),
    ("one scenario", "numbered scenarios: tasks.md"),
    ("incomplete answer", "scenario mismatch"),
    ("missing answer", "missing local evidence"),
    ("edited answer", "SHA-256 mismatch"),
    ("same model", "self-review"),
    ("missing review", "missing cross-model review"),
    ("omitted ID", "review missing card ID"),
    ("reused judgment", "reused evidence"),
    ("outside path", "invalid private filename"),
])
def test_incomplete_inventory(batch, defect, reason, capsys):
    root, frozen, index, run = batch
    first = index["reviews"][0]
    if defect == "missing arm":
        index["authors"].pop()
    elif defect == "duplicate arm":
        index["authors"][0]["arm"] = "without"
    elif defect == "borrowed answer":
        copied = (root / "card-11.md").read_text(encoding="utf-8").replace(" ", "  ")
        index["sha256"]["card-10.md"] = save(root, "card-10.md", copied)
    elif defect == "stale zip":
        index["candidate_sha256"] = "0" * 64
    elif defect == "stale source":
        frozen["source_files"]["SKILL.md"] = "0" * 64
    elif defect == "different task":
        frozen["prompts"]["without.txt"] = save(root, "without.txt", "1. Other case.\n2. Another.")
    elif defect == "one scenario":
        frozen["task"] = save(root, "tasks.md", "1. An extension request.")
    elif defect == "incomplete answer":
        index["sha256"]["card-10.md"] = save(root, "card-10.md", "1. First answer.\n3. Other scenario.")
    elif defect == "missing answer":
        (root / "card-10.md").unlink()
    elif defect == "edited answer":
        save(root, "card-10.md", "Edited.")
    elif defect == "same model":
        first["model"] = index["authors"][0]["model"]
    elif defect == "missing review":
        index["reviews"].pop()
    elif defect == "omitted ID":
        index["sha256"][first["cold"]] = save(root, first["cold"], "10 only; 211 is a different ID")
    elif defect == "reused judgment":
        first["judgment"] = first["cold"]
    elif defect == "outside path":
        first["cold"] = "../cold-0.md"
        index["sha256"][first["cold"]] = "0" * 64
    assert run() == 1
    assert reason in capsys.readouterr().err
