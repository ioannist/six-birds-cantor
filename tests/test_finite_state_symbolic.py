import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contextual_cantor.finite_state_symbolic import (
    admissible_word_count,
    solve_partition_root_for_depth,
    solve_spectral_root_dimension,
)


class FiniteStateSymbolicTest(unittest.TestCase):
    def test_control_middle_thirds_root(self) -> None:
        edges = [
            {"src": "q0", "dst": "q0", "ratio": 1.0 / 3.0},
            {"src": "q0", "dst": "q0", "ratio": 1.0 / 3.0},
        ]
        root = solve_spectral_root_dimension(edges, tol=1e-13)
        expected = math.log(2.0) / math.log(3.0)
        self.assertLessEqual(abs(root - expected), 1e-10)

    def test_control_base5_024_root(self) -> None:
        edges = [
            {"src": "q0", "dst": "q0", "ratio": 1.0 / 5.0},
            {"src": "q0", "dst": "q0", "ratio": 1.0 / 5.0},
            {"src": "q0", "dst": "q0", "ratio": 1.0 / 5.0},
        ]
        root = solve_spectral_root_dimension(edges, tol=1e-13)
        expected = math.log(3.0) / math.log(5.0)
        self.assertLessEqual(abs(root - expected), 1e-10)

    def test_adjacency_fibonacci_base3_root(self) -> None:
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        edges = [
            {"src": "a", "dst": "a", "ratio": 1.0 / 3.0},
            {"src": "a", "dst": "b", "ratio": 1.0 / 3.0},
            {"src": "b", "dst": "a", "ratio": 1.0 / 3.0},
        ]
        root = solve_spectral_root_dimension(edges, tol=1e-13)
        expected = math.log(phi) / math.log(3.0)
        self.assertLessEqual(abs(root - expected), 1e-10)

    def test_toy_word_counts(self) -> None:
        edges = [
            {"src": "x", "dst": "x", "ratio": 0.5},
            {"src": "x", "dst": "y", "ratio": 0.5},
            {"src": "y", "dst": "x", "ratio": 0.5},
        ]
        c1 = admissible_word_count(edges, depth=1, start_states=["x"])
        c2 = admissible_word_count(edges, depth=2, start_states=["x"])
        c3 = admissible_word_count(edges, depth=3, start_states=["x"])
        self.assertEqual((c1, c2, c3), (2, 3, 5))
        r4 = solve_partition_root_for_depth(edges, depth=4, start_states=["x"], tol=1e-13)
        self.assertGreaterEqual(r4, 0.0)

    def test_runner_manifest_valid_for_control(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        run_script = repo_root / "scripts" / "run_finite_state_baseline.py"
        validate_script = repo_root / "scripts" / "validate_metadata.py"
        config_path = repo_root / "configs" / "experiments" / "finite_state" / "control_middle_thirds_symbolic.json"

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

        manifest_path = repo_root / "results" / "finite_state_baselines" / "control_middle_thirds_symbolic" / "result_manifest.json"
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

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("summary_metrics", data)
        self.assertIn("spectral_root_dimension", data["summary_metrics"])


if __name__ == "__main__":
    unittest.main()
