#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def canonical_json_sha256(data: Any) -> str:
    if not isinstance(data, dict):
        raise ValueError("config must be a top-level JSON object")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("config JSON must be an object")
    return data


def plot_cylinders(cylinders: list[tuple[float, float]], path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 1.8))
    y = 0.5
    for start, end in sorted(cylinders):
        ax.plot([start, end], [y, y], color="#1f77b4", linewidth=3, solid_capstyle="butt")
    ax.set_ylim(0.0, 1.0)
    ax.set_xlim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("x")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run classical similarity baseline from config.")
    parser.add_argument("--config", required=True, type=Path, help="Path to a classical experiment config JSON.")
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    config_path = args.config if args.config.is_absolute() else (Path.cwd() / args.config)
    config_path = config_path.resolve()

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.classical_similarity import (
        generate_cylinders,
        maps_from_restricted_digits,
        solve_similarity_dimension,
    )

    config = load_config(config_path)
    parameters = config.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("config 'parameters' must be an object")

    base = int(parameters["base"])
    allowed_digits = parameters["allowed_digits"]
    depth = int(parameters.get("max_depth", 8))

    maps = maps_from_restricted_digits(base=base, allowed_digits=allowed_digits)
    cylinders = generate_cylinders(maps, depth=depth)
    exact_dimension = solve_similarity_dimension([m.ratio for m in maps], tol=1e-14)

    lengths = [end - start for start, end in cylinders]
    cylinder_stats = {
        "depth": depth,
        "cylinder_count": len(cylinders),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "total_length": sum(lengths),
    }

    output_root = repo_root / str(config["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = f"{config['experiment_id']}-run-0001"

    png_path = output_root / f"{run_id}_stage_{depth}.png"
    plot_cylinders(cylinders, png_path, f"{config['family_id']} (depth={depth})")

    config_rel = config_path.relative_to(repo_root).as_posix()
    png_rel = png_path.relative_to(repo_root).as_posix()
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "success",
        "code_version": "UNSET",
        "config_path": config_rel,
        "config_hash_method": "sha256-json-canonical-v1",
        "config_hash_sha256": canonical_json_sha256(config),
        "family_id": config["family_id"],
        "engine": config["engine"],
        "parameters": parameters,
        "artifacts": [
            {
                "path": png_rel,
                "kind": "attractor_plot"
            }
        ],
        "summary_metrics": {
            "exact_dimension": exact_dimension,
            "max_depth": depth,
            "interval_count": len(cylinders),
        },
        "command": f"python {script_path.relative_to(repo_root).as_posix()} --config {config_rel}",
        "exit_status": 0,
        "warnings": [],
        "notes": None,
        "environment": {
            "python": sys.version.split()[0]
        }
    }
    manifest_path = output_root / "result_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(
        f"run_id={run_id} family={config['family_id']} "
        f"exact_dimension={exact_dimension:.15f} cylinders={len(cylinders)} "
        f"manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
