#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import yaml
REQ={"L0":[],"L1":["views"],"L2":["views","roles"],"L3":["views","roles","modules"],"L4":["views","roles","modules"]}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("document",type=Path);p.add_argument("--level",choices=REQ,default="L2");p.add_argument("--domain-rules",type=Path);a=p.parse_args();d=yaml.safe_load(a.document.read_text(encoding="utf-8")) or {};fail=[]
 for key in REQ[a.level]:
  if not d.get(key):fail.append(f"missing non-empty {key}")
 ids=set()
 for v in d.get("views",[]):
  vid=v.get("id");
  if not vid or not str(vid).startswith("VIEW-"):fail.append("view id must start VIEW-")
  if vid in ids:fail.append(f"duplicate view id {vid}")
  ids.add(vid)
  if a.level in {"L2","L3","L4"}:
   for key in ["roles","regions","states"]:
    if not v.get(key):fail.append(f"{vid} missing {key}")
   for action in v.get("actions",[]):
    if not str(action).startswith("ACT-"):fail.append(f"{vid} invalid action {action}")
 if a.domain_rules:
  rules=yaml.safe_load(a.domain_rules.read_text(encoding="utf-8")) or {}
  for term in rules.get("validators",{}).get("ia",{}).get("required_view_ids",[]):
   if term not in ids:fail.append(f"missing domain view {term}")
 if fail:print("FAIL: "+"; ".join(fail));return 1
 print(f"PASS: IA satisfies current {a.level} contract ({len(ids)} views)");return 0
if __name__=="__main__":raise SystemExit(main())
