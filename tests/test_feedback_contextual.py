import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.feedback_contextual import Interval, apply_packaging_mode


class FeedbackContextualTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.validate_script = self.repo_root / "scripts" / "validate_metadata.py"
        self.runner_script = self.repo_root / "scripts" / "run_feedback_contextual_samples.py"

    def test_new_configs_validate(self) -> None:
        for rel in [
            "configs/experiments/contextual/feedback_lens_protocol_coupled.json",
            "configs/experiments/contextual/feedback_budget_gate_and_packaging.json",
        ]:
            proc = subprocess.run(
                [sys.executable, str(self.validate_script), "--config", rel],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

    def test_packaging_modes_are_distinct(self) -> None:
        raw = [Interval(0.0, 0.5), Interval(0.5, 1.0), Interval(0.55, 0.9)]
        identity = apply_packaging_mode(raw, "identity", {"budget_interval_cap": 2})
        merged = apply_packaging_mode(raw, "merge_touching", {"budget_interval_cap": 2})
        capped = apply_packaging_mode(raw, "budget_capped_merge", {"budget_interval_cap": 1})

        self.assertEqual(len(identity), 3)
        self.assertEqual(len(merged), 1)
        self.assertEqual(len(capped), 1)
        self.assertNotEqual(len(identity), len(merged))

        raw2 = [Interval(0.0, 0.2), Interval(0.3, 0.5), Interval(0.6, 0.8)]
        merged2 = apply_packaging_mode(raw2, "merge_touching", {"budget_interval_cap": 2})
        capped2 = apply_packaging_mode(raw2, "budget_capped_merge", {"budget_interval_cap": 2})
        self.assertEqual(len(merged2), 3)
        self.assertEqual(len(capped2), 2)

    def test_all_contextual_configs_have_explicit_modes(self) -> None:
        for path in sorted((self.repo_root / "configs" / "experiments" / "contextual").glob("*.json")):
            cfg = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("lens_mode", cfg, msg=f"missing lens_mode in {path}")
            self.assertIn("packaging_mode", cfg, msg=f"missing packaging_mode in {path}")

    def test_feedback_runs_causal_columns_and_cells(self) -> None:
        run_proc = subprocess.run(
            [sys.executable, str(self.runner_script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(run_proc.returncode, 0, msg=run_proc.stdout + "\n" + run_proc.stderr)

        family_a_dir = self.repo_root / "results" / "feedback_contextual" / "feedback-lens-protocol-coupled"
        family_b_dir = self.repo_root / "results" / "feedback_contextual" / "feedback-budget-gate-and-packaging"
        trace_a = family_a_dir / "feedback-lens-protocol-coupled-run-0001_trace.csv"
        trace_b = family_b_dir / "feedback-budget-gate-and-packaging-run-0001_trace.csv"
        self.assertTrue(trace_a.exists())
        self.assertTrue(trace_b.exists())

        with trace_a.open("r", encoding="utf-8", newline="") as f:
            rows_a = list(csv.DictReader(f))
            cols_a = set(rows_a[0].keys()) if rows_a else set()
        with trace_b.open("r", encoding="utf-8", newline="") as f:
            rows_b = list(csv.DictReader(f))
            cols_b = set(rows_b[0].keys()) if rows_b else set()

        required_cols = {
            "stage",
            "protocol_state_before",
            "protocol_state_after",
            "lens_mode_before",
            "lens_mode_after",
            "packaging_mode_before",
            "packaging_mode_after",
            "observed_metric_name",
            "observed_metric_value",
            "decision_rule",
            "triggered_cells",
            "gating_state_before",
            "gating_state_after",
            "gating_rule",
            "lens_metric_threshold",
            "p2_from_p4_fired",
            "p2_from_p6_fired",
            "p5_from_p4_fired",
            "p5_from_p6_fired",
            "raw_interval_count",
            "packaged_interval_count",
            "total_length_before_packaging",
            "total_length_after_packaging",
        }
        self.assertTrue(required_cols.issubset(cols_a))
        self.assertTrue(required_cols.issubset(cols_b))

        fired_a = set()
        for row in rows_a:
            for c in row["triggered_cells"].split(","):
                c = c.strip()
                if c:
                    fired_a.add(c)
        self.assertIn("P3<-P4", fired_a)
        self.assertIn("P4<-P3", fired_a)
        self.assertIn("P5<-P4", fired_a)
        p5_from_p4_rows = [row for row in rows_a if row.get("p5_from_p4_fired", "0") in {"1", "true", "True"}]
        self.assertGreaterEqual(len(p5_from_p4_rows), 1)
        p2_fired_rows = [row for row in rows_a if row.get("p2_from_p4_fired", "0") in {"1", "true", "True"}]
        self.assertGreaterEqual(len(p2_fired_rows), 1)

        fired_b = set()
        for row in rows_b:
            for c in row["triggered_cells"].split(","):
                c = c.strip()
                if c:
                    fired_b.add(c)
        self.assertIn("P2<-P6", fired_b)
        gating_switches_b = sum(1 for row in rows_b if row["gating_state_before"] != row["gating_state_after"])
        self.assertGreaterEqual(gating_switches_b, 1)
        p2_from_p6_rows = [row for row in rows_b if row.get("p2_from_p6_fired", "0") in {"1", "true", "True"}]
        self.assertGreaterEqual(len(p2_from_p6_rows), 1)

    def test_summary_json_exists(self) -> None:
        out_dir = self.repo_root / "results" / "feedback_contextual" / "feedback-lens-protocol-coupled"
        summary = out_dir / "feedback-lens-protocol-coupled-run-0001_summary.json"
        if not summary.exists():
            subprocess.run([sys.executable, str(self.runner_script)], cwd=self.repo_root, check=False)
        self.assertTrue(summary.exists())
        data = json.loads(summary.read_text(encoding="utf-8"))
        self.assertIn("cells_fired_at_least_once", data)

    def test_identity_snapshot_path_is_raw_variant(self) -> None:
        out_dir = self.repo_root / "results" / "feedback_contextual" / "feedback-lens-protocol-coupled"
        raw_png = out_dir / "feedback-lens-protocol-coupled-run-0001_final_snapshot_raw.png"
        if not raw_png.exists():
            subprocess.run([sys.executable, str(self.runner_script)], cwd=self.repo_root, check=False)
        self.assertTrue(raw_png.exists())

    def test_alignment_validates(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.validate_script), "--pica-alignment", "configs/pica/cantor_pica_alignment_v1.json"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

    def test_alignment_current_cells_match_fired_evidence_for_feedback_families(self) -> None:
        run_proc = subprocess.run(
            [sys.executable, str(self.runner_script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(run_proc.returncode, 0, msg=run_proc.stdout + "\n" + run_proc.stderr)

        summary_a = (
            self.repo_root
            / "results"
            / "feedback_contextual"
            / "feedback-lens-protocol-coupled"
            / "feedback-lens-protocol-coupled-run-0001_summary.json"
        )
        summary_b = (
            self.repo_root
            / "results"
            / "feedback_contextual"
            / "feedback-budget-gate-and-packaging"
            / "feedback-budget-gate-and-packaging-run-0001_summary.json"
        )
        self.assertTrue(summary_a.exists())
        self.assertTrue(summary_b.exists())

        fired_a = set(json.loads(summary_a.read_text(encoding="utf-8"))["cells_fired_at_least_once"])
        fired_b = set(json.loads(summary_b.read_text(encoding="utf-8"))["cells_fired_at_least_once"])

        expected_a = {"P2<-P4", "P3<-P4", "P4<-P3", "P5<-P4"}
        expected_b = {"P2<-P6", "P5<-P6"}
        self.assertTrue(expected_a.issubset(fired_a))
        self.assertTrue(expected_b.issubset(fired_b))

        alignment = json.loads(
            (self.repo_root / "configs" / "pica" / "cantor_pica_alignment_v1.json").read_text(encoding="utf-8")
        )
        by_family = {entry["family_id"]: entry for entry in alignment["family_alignment"]}
        current_a = set(by_family["contextual_local.feedback_lens_protocol_coupled"]["active_cells_current"])
        current_b = set(by_family["contextual_local.feedback_budget_gate_and_packaging"]["active_cells_current"])

        self.assertTrue(expected_a.issubset(current_a))
        self.assertTrue(expected_b.issubset(current_b))


if __name__ == "__main__":
    unittest.main()
