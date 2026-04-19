import json
import subprocess
import sys
import unittest
from pathlib import Path


class FamilyRegistryTest(unittest.TestCase):
    def test_registry_validation_and_structure(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        validate_script = repo_root / "scripts" / "validate_metadata.py"
        registry_path = repo_root / "configs" / "registry" / "benchmark_family_registry_v1.json"

        proc = subprocess.run(
            [sys.executable, str(validate_script), "--registry", str(registry_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"command failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )

        data = json.loads(registry_path.read_text(encoding="utf-8"))
        tiers = data.get("tiers", {})
        self.assertEqual(set(tiers.keys()), {"classical", "finite_state", "contextual_local"})
        total = sum(len(tiers[name]) for name in ["classical", "finite_state", "contextual_local"])
        self.assertGreaterEqual(total, 9)


if __name__ == "__main__":
    unittest.main()
