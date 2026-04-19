import subprocess
import sys
import unittest
from pathlib import Path


class ValidateMetadataCliTest(unittest.TestCase):
    def test_sample_metadata_validation(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        validate_script = repo_root / "scripts" / "validate_metadata.py"
        config_path = repo_root / "configs" / "samples" / "sample_experiment_config.json"
        manifest_path = repo_root / "configs" / "samples" / "sample_result_manifest.json"

        commands = [
            [sys.executable, str(validate_script), "--config", str(config_path)],
            [sys.executable, str(validate_script), "--manifest", str(manifest_path)],
            [
                sys.executable,
                str(validate_script),
                "--config",
                str(config_path),
                "--manifest",
                str(manifest_path),
                "--check-config-hash",
            ],
        ]

        for cmd in commands:
            proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"command failed: {' '.join(cmd)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
