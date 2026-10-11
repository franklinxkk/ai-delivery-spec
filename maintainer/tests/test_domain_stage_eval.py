"""Audit the comparison harness, not the quality of model/domain judgments."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("domain_stage_eval",ROOT/"maintainer/tools/eval_domain_stages.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

def sample():
    index={"a":({"domain":"synthetic","stage":"specify"},{"expected":"accept","criterion":"legal bounded control"}),
           "b":({"domain":"synthetic","stage":"specify"},{"expected":"revise","criterion":"breaks authorized state"})}
    response={"reviewer":"fixture","results":[{"id":"a","verdict":"accept","reason":"keeps the authorized path"},
                                            {"id":"b","verdict":"revise","reason":"overwrites the retained old object"}]}
    return index,response

def test_real_blind_inputs_do_not_expose_oracles():
    doc,_=mod.read(mod.CASES)
    index=mod.case_index(doc)
    blind=mod.blind(doc,mod.DOMAINS)
    assert len(index)==192
    assert {v["id"] for c in blind["cases"] for v in c["variants"]}==set(index)
    assert all(set(v)=={"id","proposal"} for c in blind["cases"] for v in c["variants"])
    assert set(blind)=={"decision_contract","cases"}

def test_wrong_verdict_is_not_counted_as_pass():
    index,response=sample()
    response["results"][1]["verdict"]="accept"
    result=mod.compare(index,[response])
    assert (result["matched"],result["mismatched"])==(1,1)
    assert result["semantic_review"]=="not_performed_by_this_tool"

@pytest.mark.parametrize("mutation",["missing","duplicate","unknown","empty_reason","invalid_verdict"])
def test_incomplete_or_malformed_evidence_is_invalid(mutation):
    index,response=sample()
    if mutation=="missing": response["results"].pop()
    elif mutation=="duplicate": response["results"].append(response["results"][0].copy())
    elif mutation=="unknown": response["results"][0]["id"]="unknown"
    elif mutation=="empty_reason": response["results"][0]["reason"]=" "
    else: response["results"][0]["verdict"]="PASS"
    with pytest.raises(ValueError):
        mod.compare(index,[response])

def test_duplicate_json_key_cannot_overwrite_failure(tmp_path):
    path=tmp_path/"duplicate.json"
    path.write_text('{"results":[{"verdict":"revise"}],"results":[]}',encoding="utf-8")
    with pytest.raises(ValueError,match="duplicate JSON key"):
        mod.read(path)

def test_legal_control_and_changed_case_digest(tmp_path):
    index,response=sample()
    result=mod.compare(index,[response])
    assert result["matched"]==2
    path=tmp_path/"input.json"
    path.write_text(json.dumps(response),encoding="utf-8")
    _,before=mod.read(path)
    response["results"][0]["reason"]="different evidence"
    path.write_text(json.dumps(response),encoding="utf-8")
    _,after=mod.read(path)
    assert before!=after

def test_cli_missing_response_exits_invalid_without_success_report(tmp_path):
    output=tmp_path/"score.json"
    run=subprocess.run([sys.executable,str(ROOT/"maintainer/tools/eval_domain_stages.py"),
                        "score","--responses",str(tmp_path/"missing.json"),"--output",str(output)],
                       capture_output=True,text=True,encoding="utf-8")
    assert run.returncode==2
    assert "INVALID:" in run.stdout and not output.exists()
