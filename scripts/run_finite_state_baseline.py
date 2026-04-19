#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run finite-state symbolic baseline from config.")
    parser.add_argument("--config", required=True, type=Path, help="Path to finite-state config JSON.")
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    config_path = args.config if args.config.is_absolute() else (Path.cwd() / args.config)
    config_path = config_path.resolve()

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.finite_state_symbolic import (
        admissible_word_count,
        normalize_edges,
        pressure_estimate,
        solve_partition_root_for_depth,
        solve_spectral_root_dimension,
    )

    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")

    parameters = config.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")
    edges = normalize_edges(parameters.get("edges", []))
    start_states = parameters.get("start_states")
    depth_list = parameters.get("depth_list", [2, 4, 6, 8, 10])
    if not isinstance(depth_list, list) or any(int(d) <= 0 for d in depth_list):
        raise ValueError("depth_list must be a list of positive integers")
    depths = [int(d) for d in depth_list]

    spectral_root = solve_spectral_root_dimension(edges, tol=1e-13)

    rows: list[dict[str, float | int]] = []
    for depth in depths:
        root_n = solve_partition_root_for_depth(
            edges=edges,
            depth=depth,
            start_states=start_states,
            tol=1e-13,
        )
        pressure_at_spectral = pressure_estimate(
            edges=edges,
            depth=depth,
            s=spectral_root,
            start_states=start_states,
        )
        count_n = admissible_word_count(edges=edges, depth=depth, start_states=start_states)
        rows.append(
            {
                "depth": depth,
                "root_estimate": root_n,
                "pressure_at_spectral_root": pressure_at_spectral,
                "word_count": count_n,
            }
        )

    last_drift = abs(rows[-1]["root_estimate"] - rows[-2]["root_estimate"]) if len(rows) >= 2 else 0.0

    output_root = repo_root / str(config["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = f"{config['experiment_id']}-run-0001"

    csv_path = output_root / f"{run_id}_root_convergence.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["depth", "root_estimate", "pressure_at_spectral_root", "word_count"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    png_path = output_root / f"{run_id}_root_convergence.png"
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot([r["depth"] for r in rows], [r["root_estimate"] for r in rows], marker="o", color="#1f77b4")
    ax.axhline(spectral_root, linestyle="--", color="#d62728", label="spectral root")
    ax.set_xlabel("depth n")
    ax.set_ylabel("root estimate s_n")
    ax.set_title(config["family_id"])
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(png_path, dpi=150)
    plt.close(fig)

    config_rel = config_path.relative_to(repo_root).as_posix()
    csv_rel = csv_path.relative_to(repo_root).as_posix()
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
            {"path": csv_rel, "kind": "root_convergence_csv"},
            {"path": png_rel, "kind": "root_convergence_plot"},
        ],
        "summary_metrics": {
            "spectral_root_dimension": spectral_root,
            "final_depth_root_estimate": rows[-1]["root_estimate"],
            "last_step_drift": last_drift,
            "depths": depths,
        },
        "command": f"python {script_path.relative_to(repo_root).as_posix()} --config {config_rel}",
        "exit_status": 0,
        "warnings": [],
        "notes": None,
        "environment": {"python": sys.version.split()[0]},
    }

    manifest_path = output_root / "result_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(
        f"run_id={run_id} family={config['family_id']} "
        f"spectral_root={spectral_root:.15f} final_depth_root={rows[-1]['root_estimate']:.15f} "
        f"drift={last_drift:.6e} manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
