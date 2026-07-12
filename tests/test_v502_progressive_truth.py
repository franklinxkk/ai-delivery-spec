from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "examples/publishing-learning-v5/delivery/truth/product-truth.yaml"
COMPILER = ROOT / "scripts/compile_product_truth.py"
LIST_KEYS = {
    "sources", "assertions", "unknowns", "decisions", "conflicts", "roles",
    "features", "modules", "entities", "fields", "flows", "views", "actions",
    "states", "rules", "events", "integrations", "acceptance", "evidence", "projections",
}

truth = yaml.safe_load(TRUTH.read_text(encoding="utf-8"))
core_keys = {"truth_id", "product", "delivery_context", "sources", "assertions", "unknowns", "decisions", "conflicts", "roles", "features"}
core = {key: value for key, value in truth.items() if key in core_keys}
module = {key: value for key, value in truth.items() if key in LIST_KEYS and key not in core_keys}

with tempfile.TemporaryDirectory(prefix="truth-shards-") as temp:
    base = Path(temp)
    (base / "fragments").mkdir()
    index = {
        "schema_version": "5.0.2", "truth_id": truth["truth_id"],
        "layout": "progressive_shards", "compiled_output": "compiled/product-truth.yaml",
        "fragments": [
            {"id": "FRAG-CORE", "path": "fragments/00-core.yaml", "owner": "test", "status": "approved"},
            {"id": "FRAG-MODULE", "path": "fragments/MOD-ALL.yaml", "owner": "test", "status": "approved"},
        ],
    }
    fragments = [
        ("00-core.yaml", {"schema_version": "5.0.2", "fragment_id": "FRAG-CORE", "truth_id": truth["truth_id"], "content": core}),
        ("MOD-ALL.yaml", {"schema_version": "5.0.2", "fragment_id": "FRAG-MODULE", "truth_id": truth["truth_id"], "content": module}),
    ]
    (base / "index.yaml").write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
    for name, value in fragments:
        (base / "fragments" / name).write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")

    result = subprocess.run([sys.executable, str(COMPILER), "--index", str(base / "index.yaml")], cwd=ROOT)
    if result.returncode:
        raise SystemExit("progressive truth compilation failed")
    compiled = yaml.safe_load((base / "compiled/product-truth.yaml").read_text(encoding="utf-8"))
    if compiled != truth:
        raise SystemExit("compiled Product Truth differs from source truth")

print("PASS: progressive Product Truth compiles losslessly from resumable fragments")
