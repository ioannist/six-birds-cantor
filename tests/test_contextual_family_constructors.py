import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.contextual_family_constructors import (
    build_domain_gated_two_map_local_ifs,
    build_prefix_memory_last_digit_rule,
    build_prefix_memory_no_22_base3,
    build_stage_dependent_alternating_removal,
)


class ContextualFamilyConstructorsTest(unittest.TestCase):
    def test_constructor_dicts_validate(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        validate_script = repo_root / "scripts" / "validate_metadata.py"
        constructors = [
            build_prefix_memory_last_digit_rule,
            build_prefix_memory_no_22_base3,
            build_domain_gated_two_map_local_ifs,
            build_stage_dependent_alternating_removal,
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for i, ctor in enumerate(constructors):
                config = ctor()
                config_path = tmp_path / f"contextual_{i}.json"
                config_path.write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, str(validate_script), "--config", str(config_path)],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    proc.returncode,
                    0,
                    msg=f"validation failed for {ctor.__name__}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
                )

    def test_generator_outputs_all_files_and_snapshots(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        generator = repo_root / "scripts" / "generate_contextual_family_samples.py"
        configs_dir = repo_root / "configs" / "experiments" / "contextual"
        out_dir = repo_root / "results" / "contextual_family_samples"
        expected_configs = [
            configs_dir / "prefix_memory_last_digit_rule.json",
            configs_dir / "prefix_memory_no_22_base3.json",
            configs_dir / "domain_gated_two_map_local_ifs.json",
            configs_dir / "stage_dependent_alternating_removal.json",
        ]
        expected_pngs = [
            out_dir / "prefix-memory-last-digit-rule_snapshot.png",
            out_dir / "prefix-memory-no-22-base3_snapshot.png",
            out_dir / "domain-gated-two-map-local-ifs_snapshot.png",
            out_dir / "stage-dependent-alternating-removal_snapshot.png",
        ]

        first = subprocess.run(
            [sys.executable, str(generator)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + "\n" + first.stderr)

        second = subprocess.run(
            [sys.executable, str(generator)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(second.returncode, 0, msg=second.stdout + "\n" + second.stderr)

        for path in expected_configs + expected_pngs:
            self.assertTrue(path.exists(), msg=f"missing generated file: {path}")


if __name__ == "__main__":
    unittest.main()
