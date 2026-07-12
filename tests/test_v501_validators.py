from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
cases=[("validate_prd_quality.py","prd-l2.md"),("validate_ia_skeleton.py","ia-l2.yaml"),("validate_coding_agent_contract.py","coding-l2.md")]
for level in ("L0","L1","L2","L3","L4"):
 for script,fixture in cases:
  r=subprocess.run([sys.executable,str(ROOT/"scripts"/script),str(ROOT/"tests/fixtures"/fixture),"--level",level],cwd=ROOT)
  if r.returncode:raise SystemExit(f"failed {script} {level}")
print("PASS: three v5.0.1 core validators enforce L0-L4")
