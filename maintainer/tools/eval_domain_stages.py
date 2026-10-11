"""Prepare blind inputs / compare verdicts; does NOT grade reasons or certify domain behavior."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "maintainer/evals/domain-stage-cases.json"
STAGES = {"frame/explore", "intake/clarify", "specify", "prototype", "review/baseline", "change/acceptance"}
DOMAINS = {"traffic", "crm", "education-it", "oa", "medical-hospital-it", "data-product", "ai-native", "media-knowledge"}
VERDICTS = {"accept", "revise", "clarify"}

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def read(path):
    raw = Path(path).read_bytes()
    doc = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)
    return doc, hashlib.sha256(raw).hexdigest()

def case_index(doc):
    cells, variants = set(), {}
    for case in doc["cases"]:
        cell = (case["domain"], case["stage"])
        if cell in cells:
            raise ValueError(f"duplicate cell: {cell}")
        cells.add(cell)
        for variant in case["variants"]:
            key = variant["id"]
            if key in variants or variant["expected"] not in VERDICTS:
                raise ValueError(f"duplicate ID or invalid oracle: {key}")
            if not variant.get("criterion") or not variant.get("proposal"):
                raise ValueError(f"empty case: {key}")
            variants[key] = (case, variant)
        if Counter(v["expected"] for v in case["variants"]) != Counter(accept=1, revise=2, clarify=1):
            raise ValueError(f"unbalanced controls: {case['id']}")
    if cells != {(d,s) for d in DOMAINS for s in STAGES}:
        raise ValueError("incomplete or unexpected domain/stage coverage")
    return variants

def blind(doc, domains):
    cases = []
    for case in doc["cases"]:
        if case["domain"] in domains:
            cases.append({**{k:v for k,v in case.items() if k != "variants"},
                          "variants":[{"id":v["id"], "proposal":v["proposal"]} for v in case["variants"]]})
    return {"decision_contract":doc["decision_contract"], "cases":cases}

def compare(index, responses):
    seen = {}
    for response in responses:
        if not isinstance(response, dict) or not response.get("reviewer") or not isinstance(response.get("results"), list):
            raise ValueError("response requires reviewer and results array")
        for item in response["results"]:
            if not isinstance(item, dict):
                raise ValueError("result must be an object")
            key = item.get("id")
            if not isinstance(key, str) or key not in index or key in seen:
                raise ValueError(f"unknown/duplicate result: {key}")
            if item.get("verdict") not in VERDICTS or not isinstance(item.get("reason"), str) or not item["reason"].strip():
                raise ValueError(f"invalid verdict/empty reason: {key}")
            seen[key] = {**item, "reviewer":response["reviewer"]}
    if set(seen) != set(index):
        raise ValueError(f"missing results: {sorted(set(index)-set(seen))}")
    results = []
    for key,(case,variant) in index.items():
        item = seen[key]
        results.append({"id":key, "domain":case["domain"], "stage":case["stage"],
                        "expected":variant["expected"], "actual":item["verdict"],
                        "verdict_match":variant["expected"]==item["verdict"],
                        "reason":item["reason"], "criterion":variant["criterion"],
                        "reviewer":item["reviewer"]})
    matched = sum(r["verdict_match"] for r in results)
    return {"scope":"Verdict comparison only; semantic reasons need separate review. No runtime/expert/production claim.",
            "semantic_review":"not_performed_by_this_tool",
            "total":len(results), "matched":matched, "mismatched":len(results)-matched,
            "results":results}

def write(path, doc):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def render(doc):
    lines=["# 5.5.3 领域 × 阶段反例集", "",
           "合成输入，不含真实客户或账号数据。8 个领域 × 6 个阶段入口 = 48 组；每组 1 个合法对照、2 个可判错误及 1 个缺失决定场景，共 192 项。阶段组合名称与 references/stages.md 一致。", "",
           "本文件由 domain-stage-cases.json 同源展开。判据在独立执行前冻结；数量不证明穷尽，判定匹配不代替理由语义复核或真实系统执行。", ""]
    for case in doc["cases"]:
        lines.extend([f"## {case['id']} · {case['stage']} · {case['title']}", "", case["context"], ""])
        for v in case["variants"]:
            lines.extend([f"- **{v['id']}**：{v['proposal']}", "",
                          f"  预期 "+chr(96)+v['expected']+chr(96)+f"：{v['criterion']}", ""])
        lines.append("")
    return "\n".join(lines).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    q=sub.add_parser("prepare")
    q.add_argument("--output",required=True,type=Path)
    q=sub.add_parser("score")
    q.add_argument("--responses",nargs="+",required=True,type=Path)
    q.add_argument("--output",required=True,type=Path)
    sub.add_parser("render")
    args=p.parse_args()
    try:
        doc,case_hash=read(CASES)
        index=case_index(doc)
        if args.command=="render":
            CASES.with_suffix(".md").write_text(render(doc),encoding="utf-8")
            print("Rendered from canonical cases; no evaluation performed")
            return 0
        if args.command=="prepare":
            for n,group in enumerate([["traffic","crm","education-it"],["oa","medical-hospital-it","media-knowledge"],["data-product","ai-native"]],1):
                write(args.output/f"blind-{n}.json",blind(doc,group))
            write(args.output/"input-manifest.json",{"cases_sha256":case_hash,"scope":"Blind input only; no execution results"})
            print("Prepared 3 blind inputs; do not give oracle or other responses to reviewers")
            return 0
        responses, hashes=[],{}
        for path in args.responses:
            response,digest=read(path)
            if path.name in hashes:
                raise ValueError("response filenames must be distinct")
            responses.append(response)
            hashes[path.name]=digest
        result=compare(index,responses)
        result.update({"cases_sha256":case_hash,"response_sha256":hashes})
        write(args.output,result)
        print(f"Verdict agreement: {result['matched']}/{result['total']}; reasons require semantic review")
        return 0 if result["mismatched"]==0 else 1
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"INVALID: {exc}")
        return 2

if __name__=="__main__":
    raise SystemExit(main())
