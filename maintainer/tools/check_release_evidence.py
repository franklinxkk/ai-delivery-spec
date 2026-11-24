#!/usr/bin/env python3
"""Check a local A/B inventory for numbered, combined text tasks."""

import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile


MODELS = ("gpt-6.2-sol", "gpt-6.2-astra", "deepseek-flash")
ARMS = ("with", "without")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verified(path, expected):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected, f"SHA-256 mismatch: {path.name}")
    return data


def as_text(data, name):
    value = data.decode("utf-8-sig").replace("\r\n", "\n").strip()
    require(value, f"empty evidence: {name}")
    return value


def sections(content, name, distinct_tasks=False):
    # Numbered paragraphs are shared across the task bundle and first answers.
    parts = re.split(r"(?m)^([1-9][0-9]*)\.[ \t]+", content)
    numbers, bodies = parts[1::2], [body.strip() for body in parts[2::2]]
    require(len(numbers) >= 2 and len(numbers) == len(set(numbers))
            and all(bodies) and (not distinct_tasks or len(set(bodies)) == len(bodies)),
            f"need distinct, nonempty numbered scenarios: {name}")
    return set(numbers)


def check(candidate, root):
    root = root.resolve()

    def private(name):
        # Only filenames are accepted in the flat private evidence directory.
        require(isinstance(name, str) and re.fullmatch(r"[\w-]+[.][\w-]+", name),
                "invalid private filename")
        path = root / name
        require(path.resolve().parent == root and path.is_file(), f"missing local evidence: {name}")
        return path

    index = json.loads(private("release-evidence.json").read_bytes())
    frozen = json.loads(verified(private("frozen-inputs.json"), index["frozen_inputs_sha256"]))
    candidate_bytes = verified(candidate, index["candidate_sha256"])

    def read(name, digest):
        return as_text(verified(private(name), digest), name)

    task = read("tasks.md", frozen["task"])
    rubric = read("rubric.md", frozen["rubric"])
    scenarios = sections(task, "tasks.md", distinct_tasks=True)
    prompts = {arm: read(arm + ".txt", frozen["prompts"][arm + ".txt"]) for arm in ARMS}
    for arm, prompt in prompts.items():
        require(task in prompt and rubric not in prompt, f"task missing or rubric exposed: {arm}")
    with ZipFile(io.BytesIO(candidate_bytes)) as archive:
        sources = frozen["source_files"]
        require(isinstance(sources, dict) and "SKILL.md" in sources, "missing frozen SKILL.md")
        for name, digest in sources.items():
            require(archive.namelist().count(name) == 1, f"missing or ambiguous ZIP source: {name}")
            data = archive.read(name)
            require(hashlib.sha256(data).hexdigest() == digest, f"candidate source changed: {name}")
            source = as_text(data, name)
            require(source in prompts["with"] and source not in prompts["without"],
                    f"prompt/source mismatch: {name}")

    # Textual agreement is possible. Ambiguous copies need independent run records.
    inputs = {" ".join(value.split()) for value in (task, rubric, *prompts.values())}
    answer_runs = {}
    run_ids = set()
    authors = {}
    completed = set()
    for row in index["authors"]:
        card, model, arm = row["card"], row["model"], row["arm"]
        require(isinstance(card, str) and re.fullmatch(r"[\w-]+", card) and card not in authors,
                "invalid or duplicate card ID")
        require(model in MODELS and arm in ARMS and (model, arm) not in completed,
                "unknown or duplicate model/arm")
        name = f"card-{card}.md"
        answer = read(name, index["sha256"][name])
        require(sections(answer, f"card-{card}") == scenarios, f"scenario mismatch: card-{card}")
        normalized = " ".join(answer.split())
        require(normalized not in inputs, f"input supplied as answer: {card}")
        run_id = None
        if row.get("receipt"):
            receipt_name = row["receipt"]
            receipt = json.loads(read(receipt_name, index["sha256"][receipt_name]))
            run_id = receipt["run_id"]
            require(isinstance(run_id, str) and run_id.strip() and run_id not in run_ids,
                    f"missing or repeated run ID: {card}")
            require(receipt["model"] == model and receipt["input_sha256"] == frozen["prompts"][arm + ".txt"]
                    and receipt["output_sha256"] == index["sha256"][name], f"receipt mismatch: {card}")
            run_ids.add(run_id)
        answer_runs.setdefault(normalized, []).append(run_id)
        authors[card] = model
        completed.add((model, arm))
    require(len(completed) == len(MODELS) * len(ARMS), "missing model/arm")
    for records in answer_runs.values():
        require(len(records) == 1 or all(records), "matching answers: independent run receipts needed")

    seen = set(answer_runs) | inputs

    def review_record(name):
        value = read(name, index["sha256"][name])
        normalized = " ".join(value.split())
        require(normalized not in seen, f"reused evidence: {name}")
        seen.add(normalized)
        return value

    reviewed = set()
    for row in index["reviews"]:
        reviewer, cards = row["model"], row["cards"]
        require(reviewer in MODELS and isinstance(cards, list) and cards, "invalid review group")
        cold, judgment = review_record(row["cold"]), review_record(row["judgment"])
        for card in cards:
            require(card in authors and card not in reviewed, f"unknown or repeated review: {card}")
            require(reviewer != authors[card], f"self-review: {card}")
            label = rf"(?<![A-Za-z0-9_]){re.escape(card)}(?![A-Za-z0-9_])"
            require(re.search(label, cold) and re.search(label, judgment),
                    f"review missing card ID: {card}")
            reviewed.add(card)
    require(reviewed == set(authors), "missing cross-model review")
    return len(scenarios)


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Use a flat private directory containing release-evidence.json (candidate_sha256, "
        "frozen_inputs_sha256, authors [{card,model,arm}], reviews [{model,cards,cold,judgment}], "
        "sha256 keyed by artifact filename). frozen-inputs.json records task, rubric, prompts "
        "and ZIP source_files hashes. Use tasks.md, rubric.md, with.txt, without.txt and "
        "card-<id>.md. This format uses '1. ...', '2. ...' and cites card IDs in both review files. "
        "For matching answers, add an author receipt filename and its sha256. Each receipt records "
        "run_id, model, input_sha256 and output_sha256. Other formats including HTML and Word may "
        "be checked manually against the same comparison matrix, original artifacts and run records."))
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        count = check(args.candidate, args.evidence_dir)
    except (OSError, KeyError, TypeError, ValueError, BadZipFile) as error:
        print(f"Incomplete evidence: {error}", file=sys.stderr)
        return 1
    print(f"Evidence inventory complete: {count} scenarios, 6 answers, 6 cross-model reviews. "
          "Model execution, blind conditions and semantic quality require separate verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
