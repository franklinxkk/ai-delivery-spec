"""Exercise the published CLI and its validators using only the bundled template."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


HERE = Path(__file__).resolve()
ROOT = Path(os.environ.get("ADS_SKILL_ROOT", HERE.parents[2]))
SCRIPTS = ROOT / "scripts"
VALIDATORS = SCRIPTS / "validators"


class TraceReferences(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.truth_path = Path(temp.name) / "truth.yaml"
        self.ledger_path = Path(temp.name) / "ledger.yaml"
        template = ROOT / "references/templates/product-truth-template.yaml"
        self.truth = yaml.safe_load(template.read_text(encoding="utf-8"))
        self.truth["requirements"][0]["stage"] = "specified"
        self.truth["projections"][0]["generated_at"] = "2026-01-01T00:00:00Z"

    def command(self, script, *args, expected):
        result = subprocess.run(
            [sys.executable, str(script), *map(str, args)], capture_output=True,
            encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def trace(self, expected):
        self.truth_path.write_text(yaml.safe_dump(self.truth), encoding="utf-8")
        output = self.command(SCRIPTS / "ai_delivery_spec_cli.py", "trace", "--truth",
                              self.truth_path, "--output", self.ledger_path, expected=expected)
        return yaml.safe_load(self.ledger_path.read_text(encoding="utf-8")), output

    def test_missing_behavior_is_reported_even_without_any_orphans(self):
        self.truth["requirements"][0]["behavior_refs"].append("ACT-MISSING")
        ledger, output = self.trace(1)
        self.assertEqual(ledger["orphans"], [])
        self.assertEqual(ledger["unresolved_refs"], [{
            "from_id": "REQ-CORE-001", "to_id": "ACT-MISSING", "source": "behavior_refs",
            "path": "requirements[0].behavior_refs[4]",
        }])
        self.assertIn("ACT-MISSING", output)
        self.assertNotIn("ACT-MISSING", ledger["reverse_index"])
        self.assertIn("ACT-MISSING", self.command(VALIDATORS / "validate_traceability_ledger.py",
                                                  self.ledger_path, expected=1))

    def test_external_ids_are_explicitly_unverified(self):
        self.truth["sources"][0]["secret_refs"] = ["SECRET-TEST"]
        req = self.truth["requirements"][0]
        req["review_refs"] = ["REVIEW-TEST"]
        req["change_refs"] = ["CHG-TEST"]
        ledger, _ = self.trace(0)
        targets = {ref["to_id"] for ref in ledger["unverified_external_refs"]}
        self.assertEqual(targets, {"SECRET-TEST", "REVIEW-TEST", "CHG-TEST"})
        self.assertTrue(targets.isdisjoint(ledger["reverse_index"]))
        self.assertEqual(ledger["unresolved_refs"], [])
        self.assertIn("unverified", self.command(VALIDATORS / "validate_product_truth.py",
                                                 self.truth_path, expected=0))
        self.assertIn("unverified", self.command(VALIDATORS / "validate_traceability_ledger.py",
                                                 self.ledger_path, expected=0))
        req["behavior_refs"].append("REVIEW-TEST")
        ledger, _ = self.trace(1)
        self.assertEqual([ref["to_id"] for ref in ledger["unresolved_refs"]], ["REVIEW-TEST"])
        self.assertIn("unresolved behavior_refs", self.command(VALIDATORS / "validate_product_truth.py",
                                                               self.truth_path, expected=1))

    def test_nested_reference_is_owned_by_flow(self):
        step = self.truth["flows"][0]["steps"][0]
        step["action_ref"] = "ACT-SUBMIT-MISSING"
        ledger, _ = self.trace(1)
        self.assertEqual(ledger["unresolved_refs"], [{
            "from_id": "FLOW-CORE-001", "to_id": "ACT-SUBMIT-MISSING",
            "source": "action_ref", "path": "flows[0].steps[0].action_ref",
        }])
        step["action_ref"] = "ACT-CORE-SUBMIT"
        ledger, _ = self.trace(0)
        self.assertIn("ACT-CORE-SUBMIT", ledger["forward_index"]["FLOW-CORE-001"])
        self.assertIn("FLOW-CORE-001", ledger["reverse_index"]["ACT-CORE-SUBMIT"])

    def test_invalid_external_locator_cannot_pass_as_local_id(self):
        self.truth["requirements"][0]["review_refs"] = ["MOD-CORE-001"]
        ledger, _ = self.trace(1)
        self.assertEqual(ledger["unverified_external_refs"], [])
        self.assertEqual(ledger["unresolved_refs"][0]["source"], "review_refs")
        self.assertIn("invalid external locator", self.command(VALIDATORS / "validate_product_truth.py",
                                                              self.truth_path, expected=1))

    def test_legacy_index_cannot_introduce_edges(self):
        ledger, _ = self.trace(0)
        del ledger["unresolved_refs"], ledger["unverified_external_refs"]
        self.ledger_path.write_text(yaml.safe_dump(ledger), encoding="utf-8")
        self.assertIn("legacy ledger", self.command(VALIDATORS / "validate_traceability_ledger.py",
                                                    self.ledger_path, expected=0))
        ledger["forward_index"]["REQ-CORE-001"].append("ACT-MISSING")
        self.ledger_path.write_text(yaml.safe_dump(ledger), encoding="utf-8")
        self.assertIn("no edge", self.command(VALIDATORS / "validate_traceability_ledger.py",
                                              self.ledger_path, expected=1))


if __name__ == "__main__":
    unittest.main()
