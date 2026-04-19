from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from contextual_cantor.contextual_certification import certify_markov_equal_ratio_dimension
from contextual_cantor.interval_utils import HAS_MPMATH_IV


def _load_config(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_contextual_certification_contains_reference() -> None:
    if not HAS_MPMATH_IV:
        pytest.skip("mpmath.iv unavailable; interval backend required for guaranteed prototype test")

    config = _load_config("configs/experiments/contextual/prefix_memory_no_22_base3.json")
    payload = certify_markov_equal_ratio_dimension(config, perron_steps=40, precision_dps=90)
    assert payload["contains_reference_root"] is True
    assert payload["certified_width"] < 1e-8


def test_contextual_certification_runner_and_manifest() -> None:
    if not HAS_MPMATH_IV:
        pytest.skip("mpmath.iv unavailable; interval backend required for guaranteed prototype test")

    subprocess.run(
        [
            sys.executable,
            "scripts/run_contextual_certification.py",
            "--config",
            "configs/experiments/contextual/prefix_memory_no_22_base3.json",
            "--precision-dps",
            "90",
            "--perron-steps",
            "40",
        ],
        check=True,
    )
    manifest_path = Path("results/certified_contextual/prefix-memory-no-22-base3/result_manifest.json")
    interval_path = Path("results/certified_contextual/prefix-memory-no-22-base3/certified_interval.json")
    assert manifest_path.exists()
    assert interval_path.exists()
    subprocess.run(
        [sys.executable, "scripts/validate_metadata.py", "--manifest", str(manifest_path)],
        check=True,
    )
