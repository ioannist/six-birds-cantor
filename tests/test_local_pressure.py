import csv
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.local_pressure import analyze_config


class LocalPressureTest(unittest.TestCase):
    def _load_config(self, rel_path: str) -> dict:
        repo_root = Path(__file__).resolve().parents[1]
        return json.loads((repo_root / rel_path).read_text(encoding="utf-8"))

    def test_classical_middle_thirds_upper_root(self) -> None:
        config = self._load_config("configs/experiments/classical/middle_thirds.json")
        analysis = analyze_config(config, depths=[8], s_max=2.0)
        root = analysis["rows"][-1]["upper_root"]
        expected = math.log(2.0) / math.log(3.0)
        self.assertIsNotNone(root)
        self.assertLessEqual(abs(root - expected), 1e-6)

    def test_classical_base5_upper_root(self) -> None:
        config = self._load_config("configs/experiments/classical/restricted_digits_base5_024.json")
        analysis = analyze_config(config, depths=[8], s_max=2.0)
        root = analysis["rows"][-1]["upper_root"]
        expected = math.log(3.0) / math.log(5.0)
        self.assertIsNotNone(root)
        self.assertLessEqual(abs(root - expected), 1e-6)

    def test_adjacency_no_consecutive_2_trend(self) -> None:
        config = self._load_config("configs/experiments/finite_state/adjacency_no_consecutive_2_base3.json")
        analysis = analyze_config(config, depths=[2, 4, 6, 8, 10], s_max=2.0)
        rows = analysis["rows"]
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        expected = math.log(phi) / math.log(3.0)
        final_root = rows[-1]["upper_root"]
        self.assertIsNotNone(final_root)
        self.assertLessEqual(abs(final_root - expected), 2e-2)
        drift = abs(rows[-1]["upper_root"] - rows[-2]["upper_root"])
        self.assertLessEqual(drift, 2e-2)

    def test_feedback_families_have_mode_state_outputs(self) -> None:
        cfg_a = self._load_config("configs/experiments/contextual/feedback_lens_protocol_coupled.json")
        cfg_b = self._load_config("configs/experiments/contextual/feedback_budget_gate_and_packaging.json")
        rows_a = analyze_config(cfg_a, depths=[1, 2, 4, 6, 8], s_max=2.0)["rows"]
        rows_b = analyze_config(cfg_b, depths=[1, 2, 4, 6, 8], s_max=2.0)["rows"]

        self.assertGreaterEqual(len(rows_a), 5)
        self.assertGreaterEqual(len(rows_b), 5)
        for row in rows_a + rows_b:
            self.assertIsNotNone(row["upper_root"])
            self.assertIn("protocol_state", row)
            self.assertIn("gating_state", row)
            self.assertIn("lens_mode", row)
            self.assertIn("packaging_mode", row)

        modes_a = {(r["protocol_state"], r["lens_mode"], r["packaging_mode"], r["gating_state"]) for r in rows_a}
        modes_b = {(r["protocol_state"], r["lens_mode"], r["packaging_mode"], r["gating_state"]) for r in rows_b}
        self.assertGreaterEqual(len(modes_b), 2)

    def test_prefix_memory_contextual_outputs_nonempty(self) -> None:
        cfg_prefix = self._load_config("configs/experiments/contextual/prefix_memory_no_22_base3.json")
        rows_prefix = analyze_config(cfg_prefix, depths=[4, 6], s_max=2.0)["rows"]
        self.assertEqual(len(rows_prefix), 2)
        self.assertIsNotNone(rows_prefix[-1]["upper_root"])

    def test_runner_csv_and_manifest_reference_fields(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        run_script = repo_root / "scripts" / "run_local_pressure.py"
        validate_script = repo_root / "scripts" / "validate_metadata.py"

        targets = [
            (
                "configs/experiments/classical/middle_thirds.json",
                repo_root / "results" / "local_pressure" / "middle-thirds-baseline",
                True,
            ),
            (
                "configs/experiments/contextual/feedback_lens_protocol_coupled.json",
                repo_root / "results" / "local_pressure" / "feedback-lens-protocol-coupled",
                False,
            ),
        ]

        for config_rel, out_dir, expect_ref in targets:
            proc = subprocess.run(
                [sys.executable, str(run_script), "--config", config_rel],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

            manifest = out_dir / "result_manifest.json"
            csvs = list(out_dir.glob("*_summary.csv"))
            self.assertTrue(manifest.exists())
            self.assertTrue(len(csvs) >= 1)

            val = subprocess.run(
                [sys.executable, str(validate_script), "--manifest", str(manifest)],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(val.returncode, 0, msg=val.stdout + "\n" + val.stderr)

            data = json.loads(manifest.read_text(encoding="utf-8"))
            summary = data.get("summary_metrics", {})
            self.assertIn("reference_root", summary)
            self.assertIn("abs_error", summary)
            if expect_ref:
                self.assertIsNotNone(summary["reference_root"])
                self.assertIsNotNone(summary["abs_error"])

            with csvs[0].open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertGreaterEqual(len(rows), 1)
            required_cols = {
                "depth",
                "upper_root",
                "lower_root",
                "interval_root_width",
                "branch_count_raw",
                "interval_count_packaged",
                "protocol_state",
                "gating_state",
                "lens_mode",
                "packaging_mode",
                "triggered_cells",
            }
            self.assertTrue(required_cols.issubset(set(reader.fieldnames or [])))


if __name__ == "__main__":
    unittest.main()
