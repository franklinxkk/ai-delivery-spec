#!/usr/bin/env python3
"""Check declared ID projections or opt-in JSON Schema example conformance.

Neither mode establishes natural-language consistency or business correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

DIALECT = "https://json-schema.org/draft/2020-12/schema"


class StrictFormatChecker(FormatChecker):
    def check(self, instance, format):
        if format not in self.checkers:
            raise ValueError(f"format checker unavailable: {format}")
        return super().check(instance, format)


def _unique_yaml(raw: str) -> Any:
    class Loader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        pairs = loader.construct_pairs(node)
        if any(not isinstance(key, str) for key, _ in pairs):
            raise ValueError("YAML mapping keys must be strings")
        return _unique_pairs(pairs)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    return yaml.load(raw, Loader=Loader)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _non_json_number(value):
    raise ValueError(f"non-JSON number: {value}")


def _local_json(base: Path, ref: str, identities: dict, cache: dict) -> Any:
    if not isinstance(ref, str) or not ref or Path(ref).is_absolute():
        raise ValueError("expected a relative local JSON path")
    path = (base / ref).resolve()
    if not path.is_relative_to(base) or path.suffix.lower() != ".json":
        raise ValueError("JSON reference must stay inside the input directory")
    if path in cache:
        return cache[path]
    data = path.read_bytes()
    identities[path.relative_to(base).as_posix()] = hashlib.sha256(data).hexdigest()
    cache[path] = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_pairs,
                            parse_constant=_non_json_number)
    return cache[path]


def _pointer(document: Any, fragment: str) -> Any:
    fragment = unquote(fragment, errors="strict")
    if not fragment:
        return document
    if not fragment.startswith("/"):
        raise ValueError("schema fragment must be a JSON Pointer, not an anchor")
    value = document
    for token in fragment.split("/")[1:]:
        if re.search(r"~(?![01])", token):
            raise ValueError("invalid JSON Pointer escape")
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", token):
                raise ValueError("invalid array pointer")
            value = value[int(token)]
        else:
            value = value[token]
    return value


def _no_retrieve(uri):
    raise ValueError("external schema retrieval is disabled")


def _instance_pointer(parts) -> str:
    return "".join("/" + str(x).replace("~", "~0").replace("/", "~1") for x in parts)


def verify_examples(input_path: Path) -> dict:
    """Validate referenced examples, including the expected negative reason.

    Existing schema and sample files remain the only definitions. No source is
    modified, no remote resource is retrieved, and no instance values are logged.
    """
    input_path = input_path.resolve()
    base = input_path.parent
    results, problems, identities, cache = [], [], {}, {}
    try:
        raw = input_path.read_bytes()
        identities[input_path.name] = hashlib.sha256(raw).hexdigest()
        if input_path.suffix.lower() == ".json":
            document = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs,
                                  parse_constant=_non_json_number)
        else:
            document = _unique_yaml(raw.decode("utf-8-sig"))
        if not isinstance(document, dict) or set(document) != {"contracts"}:
            raise ValueError("input must contain only contracts")
        contracts = document["contracts"]
        if not isinstance(contracts, list) or not contracts:
            raise ValueError("contracts must be a non-empty list")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return {"status": "INVALID", "errors": [str(exc)], "results": [],
                "checked": 0, "passed": 0, "identities": identities,
                "not_proven": ["business semantics", "runtime behavior", "unlisted examples"]}

    seen = set()
    for index, contract in enumerate(contracts):
        label = f"contracts[{index}]"
        try:
            if not isinstance(contract, dict) or set(contract) != {"id", "schema", "cases"}:
                raise ValueError("contract requires exactly id, schema, cases")
            identity = contract["id"]
            if not isinstance(identity, str) or not identity.strip() or identity in seen:
                raise ValueError("contract id must be non-empty and unique")
            seen.add(identity)
            label = identity
            ref = contract["schema"]
            if not isinstance(ref, str):
                raise ValueError("schema must be a relative JSON path with optional #/pointer")
            filename, _, fragment = ref.partition("#")
            source = _local_json(base, filename, identities, cache)
            if not isinstance(source, dict) or source.get("$schema") != DIALECT:
                raise ValueError("schema document must explicitly declare JSON Schema 2020-12")
            Draft202012Validator.check_schema(source)
            Draft202012Validator.check_schema(_pointer(source, fragment))
            registry = Registry(retrieve=_no_retrieve).with_resource(
                "urn:ads:source", Resource.from_contents(source)).crawl()
            validator = Draft202012Validator(
                {"$ref": "urn:ads:source" + ("#" + fragment if fragment else "")},
                registry=registry, format_checker=StrictFormatChecker())
            cases = contract["cases"]
            if not isinstance(cases, list) or not cases:
                raise ValueError("cases must contain positive and negative examples")
            case_ids = set()
            checked_cases = []
            for case in cases:
                if not isinstance(case, dict) or not {"id", "instance", "valid"} <= set(case):
                    raise ValueError("case requires id, instance, valid")
                if set(case) - {"id", "instance", "valid", "error"}:
                    raise ValueError("case contains unknown keys")
                cid = case["id"]
                if not isinstance(cid, str) or not cid.strip() or cid in case_ids:
                    raise ValueError("case id must be non-empty and unique within its contract")
                case_ids.add(cid)
                if type(case["valid"]) is not bool:
                    raise ValueError("valid must be a boolean")
                if case["valid"]:
                    if "error" in case:
                        raise ValueError("positive case cannot declare an expected error")
                else:
                    expected = case.get("error")
                    if (not isinstance(expected, dict) or
                            set(expected) != {"keyword", "instance_path"} or
                            not isinstance(expected["keyword"], str) or not expected["keyword"] or
                            not isinstance(expected["instance_path"], str) or
                            (expected["instance_path"] and not expected["instance_path"].startswith("/"))):
                        raise ValueError("negative case requires error.keyword and error.instance_path")
                checked_cases.append((case, _local_json(base, case["instance"], identities, cache)))
            if {case["valid"] for case, _ in checked_cases} != {True, False}:
                raise ValueError("each contract needs at least one positive and one negative example")
            for case, instance in checked_cases:
                try:
                    errors = list(validator.iter_errors(instance))
                    actual_errors = [{"keyword": e.validator,
                                      "instance_path": _instance_pointer(e.absolute_path)} for e in errors]
                    actual_valid = not errors
                    passed = actual_valid == case["valid"]
                    if not case["valid"]:
                        passed = passed and case["error"] in actual_errors
                    results.append({"contract": identity, "case": case["id"],
                                    "expected_valid": case["valid"], "actual_valid": actual_valid,
                                    "status": "PASS" if passed else "FAIL", "errors": actual_errors})
                except Exception as exc:
                    # jsonschema wraps resolution errors; do not turn them into a
                    # successful rejection of a negative instance.
                    detail = str(exc) if isinstance(exc, ValueError) and str(exc).startswith("format checker unavailable:") else type(exc).__name__
                    problems.append(f"{label}/{case['id']}: schema evaluation failed ({detail})")
        except Exception as exc:
            # Invalid schema/type/reference is an input failure, never business PASS.
            problems.append(f"{label}: {type(exc).__name__}: {str(exc).splitlines()[0]}")
    passed_count = sum(x["status"] == "PASS" for x in results)
    return {"status": "INVALID" if problems else ("PASS" if passed_count == len(results) else "FAIL"),
            "checked": len(results), "passed": passed_count, "results": results,
            "errors": problems, "identities": identities,
            "not_proven": ["business semantics", "runtime behavior", "unlisted examples"]}


ID_PATTERN = re.compile(
    r"\b(?:SRC|AST|DEC|UNK|CFL|REQ|REV|ROLE|FEAT|MOD|ENT|FLD|FLOW|VIEW|REG|ACT|STM|RULE|API|EVT|INT|AC|TEST|ARUN|DEFECT|EVD|CHG|METRIC|TRUTH)-[A-Z0-9-]+\b"
)


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def truth_ids(document: dict[str, Any]) -> set[str]:
    ids = {node["id"] for node in walk(document) if isinstance(node.get("id"), str)}
    if document.get("truth_id"):
        ids.add(document["truth_id"])
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path)
    parser.add_argument("--projection", type=Path)
    parser.add_argument("--examples", type=Path, help="Opt-in local schema/example contract manifest")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.examples:
        if args.truth or args.projection:
            parser.error("--examples cannot be combined with --truth/--projection")
        report = verify_examples(args.examples)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"{report['status']}: {report['passed']}/{report['checked']} declared examples")
            for problem in report["errors"]:
                print("INVALID: " + problem)
            for case in report["results"]:
                if case["status"] != "PASS":
                    print(f"FAIL: {case['contract']}/{case['case']}: {case['errors']}")
            print("NOT PROVEN: business semantics, runtime behavior, unlisted examples")
        return {"PASS": 0, "FAIL": 1, "INVALID": 2}[report["status"]]
    if not args.truth or not args.projection:
        parser.error("supply --truth and --projection, or --examples")

    truth = yaml.safe_load(args.truth.read_text(encoding="utf-8"))
    text = args.projection.read_text(encoding="utf-8")
    known = truth_ids(truth)
    referenced = set(ID_PATTERN.findall(text))
    invented = sorted(referenced - known)
    failures: list[str] = []
    if invented:
        failures.append("projection invents IDs: " + ", ".join(invented))
    if "product-truth" not in text.lower() and "product truth" not in text.lower():
        failures.append("projection does not name Product Truth as its source")
    if not referenced:
        failures.append("projection contains no stable Product Truth IDs")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        f"PASS: projection references {len(referenced)} known Product Truth IDs "
        f"and invents none ({args.projection.name})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
