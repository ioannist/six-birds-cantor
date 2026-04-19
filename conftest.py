from __future__ import annotations

from pathlib import Path


VENDOR_ROOT = (Path(__file__).resolve().parent / "vendors" / "six-birds-pica").resolve()


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # type: ignore[override]
    path = Path(str(collection_path)).resolve()
    if VENDOR_ROOT not in path.parents:
        return False
    return path.suffix == ".py" and path.name.startswith("test_")
