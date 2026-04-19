import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


class AblationHarnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.plan = self.repo_root / "configs" / "ablations" / "local_pressure_stability_v1.json"
        self.thresholds = self.repo_root / "configs" / "regressions" / "local_pressure_regression_thresholds_v1.json"
        self.run_script = self.repo_root / "scripts" / "run_ablation_harness.py"
        self.validate_script = self.repo_root / "scripts" / "validate_metadata.py"
        self.output_root = self.repo_root / "results" / "robustness" / "local_pressure_stability_v1"

    def test_ablation_harness_outputs_and_regressions(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.run_script), "--plan", str(self.plan)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

        table = self.output_root / "stability_table.csv"
        summary = self.output_root / "stability_summary.json"
        report = self.output_root / "stability_report.md"
        self.assertTrue(table.exists())
        self.assertTrue(summary.exists())
        self.assertTrue(report.exists())

        rows = list(csv.DictReader(table.open("r", encoding="utf-8", newline="")))
        self.assertGreater(len(rows), 0)

        family_ids = {r["family_id"] for r in rows}
        expected_families = {
            "classical.middle_thirds",
            "classical.restricted_digits_base5_024",
            "finite_state.adjacency_no_consecutive_2_base3",
            "contextual_local.prefix_memory_no_22_base3",
            "contextual_local.feedback_lens_protocol_coupled",
        }
        self.assertTrue(expected_families.issubset(family_ids))

        factors = {r["ablation_factor"] for r in rows}
        for required in [
            "default",
            "depth_cutoff",
            "numerical_precision",
            "discretization_choice",
            "branch_ordering",
            "random_seed",
        ]:
            self.assertIn(required, factors)

        unstable_rows = [r for r in rows if str(r["is_unstable"]).lower() in {"true", "1"}]
        self.assertGreaterEqual(len(unstable_rows), 1)

        thresholds = json.loads(self.thresholds.read_text(encoding="utf-8"))
        fam_thresholds = thresholds.get("families", {})

        defaults = [r for r in rows if r["ablation_factor"] == "default"]
        by_family = {r["family_id"]: r for r in defaults}

        for family_id in [
            "classical.middle_thirds",
            "classical.restricted_digits_base5_024",
            "finite_state.adjacency_no_consecutive_2_base3",
        ]:
            self.assertIn(family_id, by_family)
            self.assertIn(family_id, fam_thresholds)
            row = by_family[family_id]
            thr = fam_thresholds[family_id]

            abs_error = row["abs_error"]
            if abs_error not in {"", "None", "null"} and thr.get("abs_error_max") is not None:
                self.assertLessEqual(float(abs_error), float(thr["abs_error_max"]))

            drift = row["last_step_drift"]
            if drift not in {"", "None", "null"} and thr.get("last_step_drift_max") is not None:
                self.assertLessEqual(float(drift), float(thr["last_step_drift_max"]))

            width = row["interval_root_width"]
            if width not in {"", "None", "null"} and thr.get("interval_root_width_max") is not None:
                self.assertLessEqual(float(width), float(thr["interval_root_width_max"]))

        # validate all generated manifests
        for row in rows:
            manifest = self.repo_root / row["manifest_path"]
            self.assertTrue(manifest.exists())
            val = subprocess.run(
                [sys.executable, str(self.validate_script), "--manifest", str(manifest)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(val.returncode, 0, msg=val.stdout + "\n" + val.stderr)


if __name__ == "__main__":
    unittest.main()
