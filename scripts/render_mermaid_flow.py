#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import yaml
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--truth",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    doc=yaml.safe_load(a.truth.read_text(encoding="utf-8")); lines=["flowchart LR"]
    for f in doc.get("flows",[]):
        fid=f.get("id","FLOW"); name=str(f.get("name",fid)).replace('"',"'")
        lines.append(f'  {fid.replace("-","_")}["{name}"]')
    flows=doc.get("flows",[])
    for left,right in zip(flows,flows[1:]): lines.append(f'  {left["id"].replace("-","_")} --> {right["id"].replace("-","_")}')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text("\n".join(lines)+"\n",encoding="utf-8");print(f"PASS: wrote {a.output}");return 0
if __name__=="__main__":raise SystemExit(main())
