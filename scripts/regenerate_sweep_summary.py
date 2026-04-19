#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_final_row(csv_path: Path) -> dict[str, Any]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"empty summary csv: {csv_path}")
    row = rows[-1]

    def _to_float(name: str) -> float | None:
        raw = row.get(name, "")
        if raw in {"", "None", "null", None}:
            return None
        return float(raw)

    return {
        "final_depth": int(row["depth"]),
        "final_upper_root": _to_float("upper_root"),
        "final_lower_root": _to_float("lower_root"),
        "interval_root_width": _to_float("interval_root_width"),
    }


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate sweep summary from atlas manifests and artifact indexes.")
    parser.add_argument("--plan", type=Path, default=None)
    parser.add_argument("--sweep-root", type=Path, default=None)
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent

    if args.sweep_root is not None:
        sweep_root = args.sweep_root if args.sweep_root.is_absolute() else (Path.cwd() / args.sweep_root)
        sweep_root = sweep_root.resolve()
        sweep_id = sweep_root.name
    elif args.plan is not None:
        plan_path = args.plan if args.plan.is_absolute() else (Path.cwd() / args.plan)
        plan_path = plan_path.resolve()
        plan = _load_json(plan_path)
        if not isinstance(plan, dict):
            raise ValueError("plan must be object")
        sweep_id = str(plan["sweep_id"])
        sweep_root = repo_root / "results" / "atlas" / sweep_id
    else:
        raise ValueError("provide --plan or --sweep-root")

    if not sweep_root.exists():
        raise FileNotFoundError(f"missing sweep root: {sweep_root}")

    rows: list[dict[str, Any]] = []
    for artifact_index in sorted(sweep_root.glob("*/*/artifact_index.json")):
        run_dir = artifact_index.parent
        idx = _load_json(artifact_index)
        if not isinstance(idx, dict):
            raise ValueError(f"artifact index must be object: {artifact_index}")

        manifest_path = repo_root / str(idx["manifest_path"])
        manifest = _load_json(manifest_path)
        if not isinstance(manifest, dict):
            raise ValueError(f"manifest must be object: {manifest_path}")

        csv_candidates = sorted(run_dir.glob("*_summary.csv"))
        if not csv_candidates:
            raise FileNotFoundError(f"missing per-run summary CSV in {run_dir}")
        final_row = _parse_final_row(csv_candidates[0])

        summary_metrics = manifest.get("summary_metrics", {})
        rows.append(
            {
                "sweep_id": sweep_id,
                "run_id": str(idx["run_id"]),
                "family_id": str(idx["family_id"]),
                "config_path": str(idx["config_path"]),
                "manifest_path": str(idx["manifest_path"]),
                "parameter_point_id": str(idx.get("parameter_point_id", "")),
                "parameter_overrides": json.dumps(idx.get("parameter_overrides", {}), sort_keys=True),
                "final_depth": final_row["final_depth"],
                "final_upper_root": final_row["final_upper_root"],
                "final_lower_root": final_row["final_lower_root"],
                "interval_root_width": final_row["interval_root_width"],
                "last_step_drift": summary_metrics.get("last_step_upper_root_drift"),
                "reference_root": summary_metrics.get("reference_root"),
                "abs_error": summary_metrics.get("abs_error"),
                "artifact_index_path": artifact_index.relative_to(repo_root).as_posix(),
            }
        )

    rows.sort(key=lambda r: r["run_id"])
    summary_csv = sweep_root / "sweep_summary_regenerated.csv"
    summary_json = sweep_root / "sweep_summary_regenerated.json"

    fieldnames = [
        "sweep_id",
        "run_id",
        "family_id",
        "config_path",
        "manifest_path",
        "parameter_point_id",
        "parameter_overrides",
        "final_depth",
        "final_upper_root",
        "final_lower_root",
        "interval_root_width",
        "last_step_drift",
        "reference_root",
        "abs_error",
        "artifact_index_path",
    ]
    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary_json.write_text(
        json.dumps(
            {
                "sweep_id": sweep_id,
                "run_count": len(rows),
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print(
        f"sweep_id={sweep_id} run_count={len(rows)} "
        f"summary_csv={summary_csv.relative_to(repo_root).as_posix()} "
        f"summary_json={summary_json.relative_to(repo_root).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
