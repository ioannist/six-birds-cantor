import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


class ParameterSweepTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.plan = self.repo_root / "configs" / "sweeps" / "local_pressure_atlas_v1.json"
        self.run_script = self.repo_root / "scripts" / "run_parameter_sweep.py"
        self.regen_script = self.repo_root / "scripts" / "regenerate_sweep_summary.py"
        self.validate_script = self.repo_root / "scripts" / "validate_metadata.py"

    def test_sweep_execution_and_regeneration(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.run_script), "--plan", str(self.plan)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

        plan = json.loads(self.plan.read_text(encoding="utf-8"))
        sweep_id = plan["sweep_id"]
        sweep_root = self.repo_root / "results" / "atlas" / sweep_id
        summary_csv = sweep_root / "sweep_summary.csv"
        summary_json = sweep_root / "sweep_summary.json"

        self.assertTrue(summary_csv.exists())
        self.assertTrue(summary_json.exists())

        rows = list(csv.DictReader(summary_csv.open("r", encoding="utf-8", newline="")))
        self.assertGreaterEqual(len(rows), 20)
        family_ids = {row["family_id"] for row in rows}
        self.assertGreaterEqual(len(family_ids), 3)

        run_ids = set()
        for row in rows:
            run_ids.add(row["run_id"])
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

            artifact_index = self.repo_root / row["artifact_index_path"]
            self.assertTrue(artifact_index.exists())

        regen = subprocess.run(
            [sys.executable, str(self.regen_script), "--plan", str(self.plan)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(regen.returncode, 0, msg=regen.stdout + "\n" + regen.stderr)

        regen_csv = sweep_root / "sweep_summary_regenerated.csv"
        self.assertTrue(regen_csv.exists())
        regen_rows = list(csv.DictReader(regen_csv.open("r", encoding="utf-8", newline="")))
        regen_run_ids = {row["run_id"] for row in regen_rows}

        self.assertEqual(len(regen_rows), len(rows))
        self.assertEqual(regen_run_ids, run_ids)


if __name__ == "__main__":
    unittest.main()
