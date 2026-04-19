import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.certified_bracketing import certify_config_root


class CertifiedBracketingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.run_script = self.repo_root / "scripts" / "run_certified_bracketing.py"
        self.validate_script = self.repo_root / "scripts" / "validate_metadata.py"

    def _load_config(self, rel: str) -> dict:
        return json.loads((self.repo_root / rel).read_text(encoding="utf-8"))

    def test_middle_thirds_contains_reference(self) -> None:
        cfg = self._load_config("configs/experiments/classical/middle_thirds.json")
        out = certify_config_root(cfg, precision_dps=70, max_steps=60)
        ref = math.log(2.0) / math.log(3.0)
        self.assertLessEqual(out["certified_lower"], ref)
        self.assertGreaterEqual(out["certified_upper"], ref)
        self.assertTrue(out["contains_reference_root"])

    def test_adjacency_contains_reference(self) -> None:
        cfg = self._load_config("configs/experiments/finite_state/adjacency_no_consecutive_2_base3.json")
        out = certify_config_root(cfg, precision_dps=70, max_steps=60)
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        ref = math.log(phi) / math.log(3.0)
        self.assertLessEqual(out["certified_lower"], ref)
        self.assertGreaterEqual(out["certified_upper"], ref)
        self.assertTrue(out["contains_reference_root"])

    def test_middle_thirds_width_improves_with_stronger_setting(self) -> None:
        cfg = self._load_config("configs/experiments/classical/middle_thirds.json")
        weak = certify_config_root(cfg, precision_dps=50, max_steps=20)
        strong = certify_config_root(cfg, precision_dps=90, max_steps=70)
        self.assertLess(strong["certified_width"], weak["certified_width"])

    def test_runner_manifest_and_nonrigorous_recorded(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(self.run_script),
                "--config",
                "configs/experiments/classical/middle_thirds.json",
                "--settings",
                "50:20,90:70",
            ],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

        out_dir = self.repo_root / "results" / "certified_bracketing" / "middle-thirds-baseline"
        manifest = out_dir / "result_manifest.json"
        summary = out_dir / "certified_settings_summary.csv"
        self.assertTrue(manifest.exists())
        self.assertTrue(summary.exists())

        val = subprocess.run(
            [sys.executable, str(self.validate_script), "--manifest", str(manifest)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(val.returncode, 0, msg=val.stdout + "\n" + val.stderr)

        data = json.loads(manifest.read_text(encoding="utf-8"))
        metrics = data["summary_metrics"]
        for key in [
            "certified_lower",
            "certified_upper",
            "certified_width",
            "nonrigorous_estimate",
            "reference_root",
            "contains_reference_root",
            "certification_method",
            "precision_dps",
            "max_steps",
        ]:
            self.assertIn(key, metrics)


if __name__ == "__main__":
    unittest.main()
