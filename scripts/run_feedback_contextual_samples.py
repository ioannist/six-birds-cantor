#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def canonical_json_sha256(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def run_one(config_path: Path, repo_root: Path) -> Path:
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.feedback_contextual import (
        render_stage_snapshot,
        render_stage_snapshot_raw,
        run_feedback_family,
    )

    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError("config must be JSON object")
    params = cfg.get("parameters", {})
    if not isinstance(params, dict):
        raise ValueError("parameters must be object")
    steps = int(params.get("steps", 8))

    result = run_feedback_family(cfg, steps=steps)
    trace_rows = result["trace_rows"]
    final_union = result["final_union"]
    final_raw_intervals = result["final_raw_intervals"]
    switches = result["switch_counts"]
    visited = result["visited"]

    experiment_id = str(cfg["experiment_id"])
    family_id = str(cfg["family_id"])
    run_id = f"{experiment_id}-run-0001"
    out_dir = repo_root / "results" / "feedback_contextual" / experiment_id
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / f"{run_id}_trace.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "stage",
                "protocol_state_before",
                "protocol_state_after",
                "lens_mode_before",
                "lens_mode_after",
                "packaging_mode_before",
                "packaging_mode_after",
                "observed_metric_name",
                "observed_metric_value",
                "decision_rule",
                "triggered_cells",
                "gating_state_before",
                "gating_state_after",
                "gating_rule",
                "lens_metric_threshold",
                "p2_from_p4_fired",
                "p2_from_p6_fired",
                "p5_from_p4_fired",
                "p5_from_p6_fired",
                "raw_interval_count",
                "packaged_interval_count",
                "total_length_before_packaging",
                "total_length_after_packaging",
            ],
        )
        writer.writeheader()
        for row in trace_rows:
            writer.writerow(
                {
                    "stage": row.stage,
                    "protocol_state_before": row.protocol_state_before,
                    "protocol_state_after": row.protocol_state_after,
                    "lens_mode_before": row.lens_mode_before,
                    "lens_mode_after": row.lens_mode_after,
                    "packaging_mode_before": row.packaging_mode_before,
                    "packaging_mode_after": row.packaging_mode_after,
                    "observed_metric_name": row.observed_metric_name,
                    "observed_metric_value": row.observed_metric_value,
                    "decision_rule": row.decision_rule,
                    "triggered_cells": row.triggered_cells,
                    "gating_state_before": row.gating_state_before,
                    "gating_state_after": row.gating_state_after,
                    "gating_rule": row.gating_rule,
                    "lens_metric_threshold": row.lens_metric_threshold,
                    "p2_from_p4_fired": row.p2_from_p4_fired,
                    "p2_from_p6_fired": row.p2_from_p6_fired,
                    "p5_from_p4_fired": row.p5_from_p4_fired,
                    "p5_from_p6_fired": row.p5_from_p6_fired,
                    "raw_interval_count": row.raw_interval_count,
                    "packaged_interval_count": row.packaged_interval_count,
                    "total_length_before_packaging": row.total_length_before_packaging,
                    "total_length_after_packaging": row.total_length_after_packaging,
                }
            )

    final_packaging_applied = trace_rows[-1].packaging_mode_before if trace_rows else cfg.get("packaging_mode", "")
    if final_packaging_applied == "identity":
        png_path = out_dir / f"{run_id}_final_snapshot_raw.png"
        render_stage_snapshot_raw(final_raw_intervals, png_path, f"{family_id} (steps={steps})")
    else:
        png_path = out_dir / f"{run_id}_final_snapshot.png"
        render_stage_snapshot(final_union, png_path, f"{family_id} (steps={steps})")

    summary_path = out_dir / f"{run_id}_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "family_id": family_id,
                "run_id": run_id,
                "stage_count": steps,
                "switch_counts": switches,
                "distinct_lens_modes_visited": visited["lens_modes"],
                "distinct_packaging_modes_visited": visited["packaging_modes"],
                "distinct_protocol_states_visited": visited["protocol_states"],
                "cells_fired_at_least_once": visited["cells_fired"],
                "final_packaging_applied": final_packaging_applied,
                "identity_visualization": final_packaging_applied == "identity",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    config_rel = config_path.relative_to(repo_root).as_posix()
    manifest_path = out_dir / "result_manifest.json"
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "success",
        "code_version": "UNSET",
        "config_path": config_rel,
        "config_hash_method": "sha256-json-canonical-v1",
        "config_hash_sha256": canonical_json_sha256(cfg),
        "family_id": family_id,
        "engine": cfg["engine"],
        "parameters": params,
        "artifacts": [
            {"path": csv_path.relative_to(repo_root).as_posix(), "kind": "stage_trace_csv"},
            {"path": png_path.relative_to(repo_root).as_posix(), "kind": "final_snapshot_png"},
            {"path": summary_path.relative_to(repo_root).as_posix(), "kind": "run_summary_json"},
        ],
        "summary_metrics": {
            "steps": steps,
            "final_interval_count": len(final_union.intervals),
            "final_total_length": final_union.total_length,
            "protocol_switches": switches["protocol_switches"],
            "lens_switches": switches["lens_switches"],
            "packaging_switches": switches["packaging_switches"],
        },
        "command": f"python scripts/run_feedback_contextual_samples.py",
        "exit_status": 0,
        "warnings": [],
        "notes": None,
        "environment": {"python": sys.version.split()[0]},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"family={family_id} run_id={run_id} "
        f"protocol_switches={switches['protocol_switches']} "
        f"lens_switches={switches['lens_switches']} "
        f"packaging_switches={switches['packaging_switches']} "
        f"manifest={manifest_path}"
    )
    return manifest_path


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    (repo_root / "results" / "feedback_contextual").mkdir(parents=True, exist_ok=True)
    config_paths = [
        repo_root / "configs" / "experiments" / "contextual" / "feedback_lens_protocol_coupled.json",
        repo_root / "configs" / "experiments" / "contextual" / "feedback_budget_gate_and_packaging.json",
    ]
    for path in config_paths:
        run_one(path, repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
