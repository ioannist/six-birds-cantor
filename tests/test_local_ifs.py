import subprocess
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.local_ifs import (
    Interval,
    IntervalUnion,
    LocalAffineMap,
    LocalIFS,
    is_word_admissible,
    iterate_set,
)


class LocalIFSTest(unittest.TestCase):
    def test_interval_union_merge(self) -> None:
        union = IntervalUnion(
            [
                Interval(0.0, 0.2),
                Interval(0.2, 0.4),
                Interval(0.6, 0.7),
                Interval(0.65, 0.8),
            ]
        )
        self.assertEqual(len(union.intervals), 2)
        self.assertAlmostEqual(union.intervals[0].left, 0.0)
        self.assertAlmostEqual(union.intervals[0].right, 0.4)
        self.assertAlmostEqual(union.intervals[1].left, 0.6)
        self.assertAlmostEqual(union.intervals[1].right, 0.8)

    def test_admissible_and_inadmissible_words(self) -> None:
        local_ifs = LocalIFS(
            maps=(
                LocalAffineMap(a=0.5, b=0.0, domain=Interval(0.0, 0.5)),
                LocalAffineMap(a=0.5, b=0.5, domain=Interval(0.5, 1.0)),
            )
        )
        self.assertTrue(is_word_admissible(local_ifs, [0, 0]))
        self.assertFalse(is_word_admissible(local_ifs, [0, 1]))

    def test_toy_systems_iterate(self) -> None:
        system_a = LocalIFS(
            maps=(
                LocalAffineMap(a=0.5, b=0.0, domain=Interval(0.0, 0.5)),
                LocalAffineMap(a=0.5, b=0.5, domain=Interval(0.5, 1.0)),
            )
        )
        seq_a = iterate_set(system_a, steps=4)
        self.assertEqual(len(seq_a), 5)

        system_b = LocalIFS(
            maps=(
                LocalAffineMap(a=0.4, b=0.0, domain=Interval(0.0, 1.0)),
                LocalAffineMap(a=0.3, b=0.35, domain=Interval(0.2, 0.8)),
                LocalAffineMap(a=0.25, b=0.7, domain=Interval(0.6, 1.0)),
            )
        )
        seq_b = iterate_set(system_b, steps=4)
        self.assertEqual(len(seq_b), 5)
        self.assertGreaterEqual(len(seq_b[-1].intervals), 1)

    def test_runner_manifest_valid_for_toy(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        run_script = repo_root / "scripts" / "run_local_ifs_toy.py"
        validate_script = repo_root / "scripts" / "validate_metadata.py"
        config_path = repo_root / "configs" / "experiments" / "local_ifs" / "domain_gated_two_map_local_ifs.json"
        manifest_path = (
            repo_root
            / "results"
            / "local_ifs_toys"
            / "domain_gated_two_map_local_ifs"
            / "result_manifest.json"
        )

        run_proc = subprocess.run(
            [sys.executable, str(run_script), "--config", str(config_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            run_proc.returncode,
            0,
            msg=f"runner failed\nstdout:\n{run_proc.stdout}\nstderr:\n{run_proc.stderr}",
        )

        validate_proc = subprocess.run(
            [sys.executable, str(validate_script), "--manifest", str(manifest_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            validate_proc.returncode,
            0,
            msg=f"manifest validation failed\nstdout:\n{validate_proc.stdout}\nstderr:\n{validate_proc.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
