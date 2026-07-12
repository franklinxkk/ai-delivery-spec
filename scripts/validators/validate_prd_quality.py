#!/usr/bin/env python3
from __future__ import annotations
import argparse, re
from pathlib import Path
import yaml

LEVELS={
"L0":["goal","acceptance"],
"L1":["goal","scope","role","flow","acceptance"],
"L2":["goal","scope","role","flow","view","action","state","data","exception","acceptance"],
"L3":["goal","scope","role","flow","view","action","state","data","exception","permission","audit","integration","acceptance","nfr"],
"L4":["goal","scope","role","flow","view","action","state","data","exception","permission","audit","integration","acceptance","nfr","migration","rollback","operations"],}
TERMS={"goal":["目标","goal"],"scope":["范围","scope"],"role":["角色","role"],"flow":["流程","flow","路径"],"view":["页面","view"],"action":["动作","action","操作","act-"],"state":["状态","state"],"data":["数据","data","字段"],"exception":["异常","exception","失败"],"permission":["权限","permission"],"audit":["审计","audit"],"integration":["接口","integration","api"],"acceptance":["验收","acceptance","ac-"],"nfr":["非功能","nfr","性能"],"migration":["迁移","migration"],"rollback":["回滚","rollback"],"operations":["运维","operations","监控"]}
def plugin_terms(path:Path|None)->list[str]:
    if not path:return []
    d=yaml.safe_load(path.read_text(encoding="utf-8")) or {};return d.get("validators",{}).get("prd",{}).get("required_terms",[])
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("document",type=Path);p.add_argument("--level",choices=LEVELS,default="L2");p.add_argument("--domain-rules",type=Path);a=p.parse_args()
    text=a.document.read_text(encoding="utf-8").lower();fail=[]
    for key in LEVELS[a.level]:
        if not any(t in text for t in TERMS[key]):fail.append(f"missing {key} contract")
    for term in plugin_terms(a.domain_rules):
        if term.lower() not in text:fail.append(f"missing domain term: {term}")
    if a.level in {"L2","L3","L4"}:
        for pattern,label in [(r"role-[a-z0-9-]+","stable ROLE IDs"),(r"(view|page)-[a-z0-9-]+","stable VIEW/PAGE IDs"),(r"act-[a-z0-9-]+","stable ACT IDs"),(r"ac-[a-z0-9-]+","stable AC IDs")]:
            if not re.search(pattern,text):fail.append(f"missing {label}")
    if fail: print("FAIL: "+"; ".join(fail));return 1
    print(f"PASS: PRD satisfies {a.level} v5.0.2 quality contract");return 0
if __name__=="__main__":raise SystemExit(main())
