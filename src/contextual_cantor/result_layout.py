from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_SLUG_SAFE = re.compile(r"[^a-z0-9]+")


def slugify_family_id(family_id: str) -> str:
    s = family_id.strip().lower().replace(".", "-").replace("_", "-")
    s = _SLUG_SAFE.sub("-", s)
    return s.strip("-") or "family"


def atlas_sweep_root(repo_root: Path, sweep_id: str) -> Path:
    return repo_root / "results" / "atlas" / sweep_id


def atlas_family_dir(repo_root: Path, sweep_id: str, family_id: str) -> Path:
    return atlas_sweep_root(repo_root, sweep_id) / slugify_family_id(family_id)


def atlas_run_dir(repo_root: Path, sweep_id: str, family_id: str, run_id: str) -> Path:
    return atlas_family_dir(repo_root, sweep_id, family_id) / run_id


def write_artifact_index(
    run_dir: Path,
    *,
    run_id: str,
    family_id: str,
    config_path: str,
    manifest_path: str,
    artifact_paths: list[str],
    parameter_point_id: str,
    parameter_overrides: dict[str, Any],
) -> Path:
    data = {
        "run_id": run_id,
        "family_id": family_id,
        "config_path": config_path,
        "manifest_path": manifest_path,
        "artifact_paths": artifact_paths,
        "parameter_point_id": parameter_point_id,
        "parameter_overrides": parameter_overrides,
    }
    out = run_dir / "artifact_index.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return out
