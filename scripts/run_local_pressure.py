#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def canonical_json_sha256(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _parse_depths(raw: str) -> list[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _reference_root_for_family(family_id: str) -> float | None:
    if family_id == "classical.middle_thirds":
        return math.log(2.0) / math.log(3.0)
    if family_id == "classical.restricted_digits_base5_024":
        return math.log(3.0) / math.log(5.0)
    if family_id == "finite_state.adjacency_no_consecutive_2_base3":
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        return math.log(phi) / math.log(3.0)
    return None


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run truncated local-pressure analysis.")
    parser.add_argument("--config", required=True, type=Path, help="Path to experiment config JSON.")
    parser.add_argument("--depths", type=str, default=None, help="Comma-separated depth list, e.g. 2,4,6,8.")
    parser.add_argument("--s-max", type=float, default=2.0, help="Upper search bound for s.")
    parser.add_argument("--s-min", type=float, default=0.0, help="Lower search bound for s.")
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.local_pressure import analyze_config, default_depths_from_config

    config_path = args.config if args.config.is_absolute() else (Path.cwd() / args.config)
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config JSON must be an object")

    if args.depths:
        depths = _parse_depths(args.depths)
    else:
        depths = default_depths_from_config(config)

    analysis = analyze_config(
        config=config,
        depths=depths,
        s_min=args.s_min,
        s_max=args.s_max,
        tol=1e-10,
    )
    rows = analysis["rows"]
    family_id = str(config["family_id"])
    experiment_id = str(config["experiment_id"])

    output_root = repo_root / "results" / "local_pressure" / experiment_id
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = f"{experiment_id}-local-pressure-run-0001"

    csv_path = output_root / f"{run_id}_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "depth",
                "upper_root",
                "lower_root",
                "interval_root_width",
                "upper_pressure_at_upper_root",
                "lower_pressure_at_lower_root",
                "branch_count_raw",
                "interval_count_packaged",
                "protocol_state",
                "gating_state",
                "lens_mode",
                "packaging_mode",
                "triggered_cells",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "depth": row["depth"],
                    "upper_root": row["upper_root"],
                    "lower_root": row["lower_root"],
                    "interval_root_width": row["interval_root_width"],
                    "upper_pressure_at_upper_root": row["upper_pressure_at_upper_root"],
                    "lower_pressure_at_lower_root": row["lower_pressure_at_lower_root"],
                    "branch_count_raw": row["branch_count_raw"],
                    "interval_count_packaged": row["interval_count_packaged"],
                    "protocol_state": row.get("protocol_state") or "",
                    "gating_state": row.get("gating_state") or "",
                    "lens_mode": row.get("lens_mode") or "",
                    "packaging_mode": row.get("packaging_mode") or "",
                    "triggered_cells": row.get("triggered_cells") or "",
                }
            )

    png_path = output_root / f"{run_id}_root_convergence.png"
    x = [row["depth"] for row in rows]
    upper = [row["upper_root"] for row in rows]
    lower = [row["lower_root"] for row in rows]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(x, upper, marker="o", label="upper root", color="#1f77b4")
    if any(v is not None for v in lower):
        ax.plot(x, lower, marker="s", label="lower root", color="#ff7f0e")
    ax.set_xlabel("depth n")
    ax.set_ylabel("root estimate s_n")
    ax.set_title(family_id)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(png_path, dpi=150)
    plt.close(fig)

    last_drift = 0.0
    if len(rows) >= 2 and rows[-1]["upper_root"] is not None and rows[-2]["upper_root"] is not None:
        last_drift = abs(rows[-1]["upper_root"] - rows[-2]["upper_root"])

    reference_root = _reference_root_for_family(family_id)
    abs_error = None
    if reference_root is not None and rows[-1]["upper_root"] is not None:
        abs_error = abs(rows[-1]["upper_root"] - reference_root)

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
        "family_id": family_id,
        "engine": config["engine"],
        "parameters": config["parameters"],
        "artifacts": [
            {"path": csv_rel, "kind": "local_pressure_csv"},
            {"path": png_rel, "kind": "local_pressure_plot"},
        ],
        "summary_metrics": {
            "final_depth": rows[-1]["depth"],
            "final_upper_root": rows[-1]["upper_root"],
            "final_lower_root": rows[-1]["lower_root"],
            "last_step_upper_root_drift": last_drift,
            "depth_count": len(rows),
            "reference_root": reference_root,
            "abs_error": abs_error,
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
        f"run_id={run_id} family={family_id} "
        f"final_depth={rows[-1]['depth']} upper_root={rows[-1]['upper_root']} "
        f"lower_root={rows[-1]['lower_root']} drift={last_drift:.6e} "
        f"manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
