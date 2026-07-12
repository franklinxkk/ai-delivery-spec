#!/usr/bin/env python3
from __future__ import annotations
import argparse, re

def recommend(text: str) -> tuple[str, str]:
    lower = text.lower()
    mode = re.search(r"mode\s*=\s*(ultra_light|lite|standard|full)", lower)
    tier = re.search(r"tier\s*=\s*(l[0-4])", lower)
    if mode or tier:
        return (mode.group(1) if mode else "standard", tier.group(1).upper() if tier else "L2")
    high = any(x in lower for x in ["medical", "patient", "payment", "settlement", "migration", "rollback", "production", "large platform", "10 roles", "20 modules"])
    workflow = any(x in lower for x in ["approval", "workflow", "audit", "two roles", "prototype", "coding", "qa"])
    tiny = any(x in lower for x in ["rename one", "one reversible", "one optional field"]) and not workflow
    if "large platform" in lower or "medical" in lower or "migration" in lower:
        return "full", "L3"
    if tiny: return "ultra_light", "L0"
    if "toc idea" in lower or "lightweight prd" in lower: return "lite", "L1"
    if high: return "standard", "L3"
    if workflow: return "standard", "L2"
    return "lite", "L1"

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("text"); a=p.parse_args()
    print(" ".join(recommend(a.text))); return 0
if __name__ == "__main__": raise SystemExit(main())
