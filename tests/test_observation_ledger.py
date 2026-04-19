import json
import subprocess
import sys
import unittest
from pathlib import Path


class ObservationLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.script = self.repo_root / "scripts" / "build_observation_ledger.py"
        self.ledger_path = self.repo_root / "docs" / "internal" / "observation_claim_ledger_v1.json"

    def test_ledger_exists_and_is_consistent(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
        self.assertTrue(self.ledger_path.exists())

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertIsInstance(ledger, dict)
        entries = ledger.get("entries", [])
        self.assertGreaterEqual(len(entries), 10)

        allowed_statuses = {"baseline_fact", "empirical_pattern", "risky_open"}
        for entry in entries:
            self.assertIn(entry.get("status"), allowed_statuses)
            self.assertTrue(entry.get("run_ids"))
            self.assertTrue(entry.get("artifact_paths"))
            for rel_path in entry["artifact_paths"]:
                self.assertTrue((self.repo_root / rel_path).exists(), msg=rel_path)


if __name__ == "__main__":
    unittest.main()
