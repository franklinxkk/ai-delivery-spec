#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
import yaml
REQ={"L0":["source"],"L1":["source","task","test"],"L2":["source","repository","module","view","action","state","data","api","test","forbidden","evidence"],"L3":["source","repository","module","view","action","state","data","api","event","permission","audit","test","forbidden","evidence","rollback"],"L4":["source","repository","module","view","action","state","data","api","event","permission","audit","test","forbidden","evidence","migration","rollback","operations"]}
TERMS={"source":["source-of-truth","事实源","generated_from"],"task":["task","任务"],"repository":["repository","仓库"],"module":["module","模块"],"view":["view-","页面"],"action":["act-","动作"],"state":["state","状态"],"data":["field","字段","数据"],"api":["api","command"],"event":["event","事件"],"permission":["permission","权限","scope"],"audit":["audit","审计"],"test":["test","测试","ac-"],"forbidden":["forbidden","禁止","不得"],"evidence":["evidence","证据"],"migration":["migration","迁移"],"rollback":["rollback","回滚"],"operations":["operations","运维","监控"]}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("document",type=Path);p.add_argument("--level",choices=REQ,default="L2");p.add_argument("--domain-rules",type=Path);a=p.parse_args();text=a.document.read_text(encoding="utf-8").lower();fail=[]
 for key in REQ[a.level]:
  if not any(x in text for x in TERMS[key]):fail.append(f"missing {key} contract")
 if a.level in {"L2","L3","L4"}:
  for pattern,label in [(r"act-[a-z0-9-]+","ACT IDs"),(r"ac-[a-z0-9-]+","AC IDs"),(r"(view|page)-[a-z0-9-]+","VIEW IDs")]:
   if not re.search(pattern,text):fail.append(f"missing {label}")
 if a.domain_rules:
  rules=yaml.safe_load(a.domain_rules.read_text(encoding="utf-8")) or {}
  for term in rules.get("validators",{}).get("coding_agent",{}).get("required_terms",[]):
   if term.lower() not in text:fail.append(f"missing domain term: {term}")
 if fail:print("FAIL: "+"; ".join(fail));return 1
 print(f"PASS: Coding Agent spec satisfies {a.level} v5.0.1 contract");return 0
if __name__=="__main__":raise SystemExit(main())
