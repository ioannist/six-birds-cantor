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

from contextual_cantor.transfer_operator import solve_transfer_root


class TransferOperatorTest(unittest.TestCase):
    def _load_config(self, rel_path: str) -> dict:
        repo_root = Path(__file__).resolve().parents[1]
        return json.loads((repo_root / rel_path).read_text(encoding="utf-8"))

    def test_middle_thirds_transfer_root(self) -> None:
        cfg = self._load_config("configs/experiments/classical/middle_thirds.json")
        root = solve_transfer_root(cfg, tol=1e-13, max_iter=300)
        ref = math.log(2.0) / math.log(3.0)
        self.assertLessEqual(abs(root - ref), 1e-10)

    def test_adjacency_transfer_root(self) -> None:
        cfg = self._load_config("configs/experiments/finite_state/adjacency_no_consecutive_2_base3.json")
        root = solve_transfer_root(cfg, tol=1e-13, max_iter=300)
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        ref = math.log(phi) / math.log(3.0)
        self.assertLessEqual(abs(root - ref), 1e-10)

    def test_comparison_runner_outputs_table(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "run_transfer_operator_comparison.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

        csv_path = repo_root / "results" / "transfer_operator" / "baseline_comparison.csv"
        json_path = repo_root / "results" / "transfer_operator" / "baseline_comparison.json"
        self.assertTrue(csv_path.exists())
        self.assertTrue(json_path.exists())

        rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8", newline="")))
        by_family = {r["family_id"]: r for r in rows}
        for family_id in [
            "classical.middle_thirds",
            "finite_state.adjacency_no_consecutive_2_base3",
        ]:
            self.assertIn(family_id, by_family)
            row = by_family[family_id]
            self.assertTrue(row.get("status"))
            self.assertNotEqual(row.get("status"), "")
            self.assertNotEqual(row.get("status"), "silent_failure")
            self.assertNotEqual(row.get("transfer_root"), "")
            self.assertNotEqual(row.get("partition_root"), "")
            self.assertNotEqual(row.get("runtime_ms_transfer"), "")
            self.assertNotEqual(row.get("runtime_ms_partition"), "")


if __name__ == "__main__":
    unittest.main()
