import json
import subprocess
import sys
import unittest
from pathlib import Path


class TheoremDiagnosticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.script = self.repo_root / "scripts" / "run_theorem_diagnostics.py"
        self.report = self.repo_root / "results" / "theorem_diagnostics" / "classification_report.json"

    def test_report_exists_and_is_consistent(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
        self.assertTrue(self.report.exists())

        data = json.loads(self.report.read_text(encoding="utf-8"))
        families = data.get("families", [])
        self.assertGreaterEqual(len(families), 6)
        allowed = {"likely_in", "inconclusive", "likely_out"}
        metric_keys = {
            "concatenation_quasimultiplicativity_defect",
            "overlap_defect",
            "memory_growth_proxy",
            "upper_lower_pressure_gap",
            "depth_sensitivity",
        }
        contextual_primary_in = 0
        any_likely_out = 0
        stage_dep = None
        for entry in families:
            self.assertTrue(entry.get("artifact_paths"))
            self.assertTrue(entry.get("run_ids"))
            self.assertIn(entry.get("primary_classification"), allowed)
            self.assertIn(entry.get("stretch_classification"), allowed)
            self.assertTrue(metric_keys.issubset(set(entry.get("metrics", {}).keys())))
            if entry["family_id"].startswith("contextual_local.") and entry["primary_classification"] == "likely_in":
                contextual_primary_in += 1
            if entry["primary_classification"] == "likely_out" or entry["stretch_classification"] == "likely_out":
                any_likely_out += 1
            if entry["family_id"] == "contextual_local.stage_dependent_alternating_removal":
                stage_dep = entry
        self.assertGreaterEqual(contextual_primary_in, 1)
        self.assertGreaterEqual(any_likely_out, 1)
        self.assertIsNotNone(stage_dep)
        self.assertNotEqual(stage_dep["primary_classification"], "likely_in")


if __name__ == "__main__":
    unittest.main()
