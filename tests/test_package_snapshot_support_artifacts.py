from __future__ import annotations

import re
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATTERN = re.compile(r"^six-birds-cantor_snapshot_v(\d+)\.zip$")
EXPECTED_PATHS = {
    "results/continuous_pressure_existence/report.json",
    "results/continuous_pressure_existence/report.csv",
    "results/continuous_pressure_closure/report.json",
    "results/continuous_pressure_closure/report.csv",
}


def test_snapshot_contains_support_reports() -> None:
    snapshots = []
    for path in REPO_ROOT.iterdir():
        match = SNAPSHOT_PATTERN.match(path.name)
        if match:
            snapshots.append((int(match.group(1)), path))
    assert snapshots, "no snapshot zip found"
    _, zip_path = max(snapshots)

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert EXPECTED_PATHS <= names

