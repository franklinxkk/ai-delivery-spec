from pathlib import Path
import sys, yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from recommend_mode import recommend
doc=yaml.safe_load((ROOT/"evals/triage-benchmark.yaml").read_text(encoding="utf-8"))
fail=[]
for case in doc["cases"]:
    got=recommend(case["prompt"])
    want=(case["expected_mode"],case["expected_tier"])
    if got!=want: fail.append(f"{case['id']}: {got} != {want}")
if fail: raise SystemExit("\n".join(fail))
print("PASS: 10/10 triage benchmark cases")
