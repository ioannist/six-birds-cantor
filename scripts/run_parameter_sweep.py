#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
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


def _depths_for_point(depth: int) -> str:
    a = max(2, depth - 4)
    b = max(2, depth - 2)
    return f"{a},{b},{depth}"


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local-pressure parameter sweep atlas.")
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.result_layout import atlas_run_dir, atlas_sweep_root, slugify_family_id, write_artifact_index

    plan_path = args.plan if args.plan.is_absolute() else (Path.cwd() / args.plan)
    plan_path = plan_path.resolve()
    plan = _load_json(plan_path)
    if not isinstance(plan, dict):
        raise ValueError("plan must be a JSON object")

    sweep_id = str(plan["sweep_id"])
    sweep_root = atlas_sweep_root(repo_root, sweep_id)
    sweep_root.mkdir(parents=True, exist_ok=True)

    run_local_pressure = repo_root / "scripts" / "run_local_pressure.py"

    rows: list[dict[str, Any]] = []
    run_counter = 0
    families = plan.get("families", [])
    if not isinstance(families, list):
        raise ValueError("plan.families must be an array")

    for family in families:
        if not isinstance(family, dict):
            raise ValueError("family entries must be objects")
        family_id = str(family["family_id"])
        config_rel = str(family["config_path"])
        config_path = repo_root / config_rel
        config = _load_json(config_path)
        if not isinstance(config, dict):
            raise ValueError(f"config must be object: {config_rel}")
        experiment_id = str(config["experiment_id"])
        source_dir = repo_root / "results" / "local_pressure" / experiment_id

        points = family.get("parameter_points", [])
        if not isinstance(points, list):
            raise ValueError(f"parameter_points must be array for {family_id}")

        for point in points:
            if not isinstance(point, dict):
                raise ValueError("parameter point entries must be objects")
            run_counter += 1
            parameter_point_id = str(point["parameter_point_id"])
            depth = int(point["depth"])
            depths_arg = _depths_for_point(depth)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(run_local_pressure),
                    "--config",
                    config_rel,
                    "--depths",
                    depths_arg,
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"run_local_pressure failed for {family_id}/{parameter_point_id}:\n{proc.stdout}\n{proc.stderr}"
                )

            source_manifest = source_dir / "result_manifest.json"
            source_csv = source_dir / f"{experiment_id}-local-pressure-run-0001_summary.csv"
            source_png = source_dir / f"{experiment_id}-local-pressure-run-0001_root_convergence.png"
            if not source_manifest.exists() or not source_csv.exists() or not source_png.exists():
                raise FileNotFoundError(f"expected local-pressure artifacts missing in {source_dir}")

            family_slug = slugify_family_id(family_id)
            run_id = f"{sweep_id}-{family_slug}-{parameter_point_id}-{run_counter:03d}"
            run_dir = atlas_run_dir(repo_root, sweep_id, family_id, run_id)
            run_dir.mkdir(parents=True, exist_ok=True)

            manifest_path = run_dir / "result_manifest.json"
            csv_path = run_dir / f"{run_id}_summary.csv"
            png_path = run_dir / f"{run_id}_root_convergence.png"
            shutil.copy2(source_csv, csv_path)
            shutil.copy2(source_png, png_path)

            manifest = _load_json(source_manifest)
            if not isinstance(manifest, dict):
                raise ValueError("source manifest must be object")
            manifest["run_id"] = run_id
            manifest["artifacts"] = [
                {
                    "path": csv_path.relative_to(repo_root).as_posix(),
                    "kind": "local_pressure_csv",
                },
                {
                    "path": png_path.relative_to(repo_root).as_posix(),
                    "kind": "local_pressure_plot",
                },
            ]
            manifest["command"] = (
                f"python scripts/run_parameter_sweep.py --plan {plan_path.relative_to(repo_root).as_posix()}"
            )
            manifest["notes"] = f"sweep_id={sweep_id}; parameter_point_id={parameter_point_id}; depth={depth}"
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

            final_row = _parse_final_row(csv_path)
            summary_metrics = manifest.get("summary_metrics", {})
            last_drift = summary_metrics.get("last_step_upper_root_drift")
            reference_root = summary_metrics.get("reference_root")
            abs_error = summary_metrics.get("abs_error")

            artifact_index_path = write_artifact_index(
                run_dir,
                run_id=run_id,
                family_id=family_id,
                config_path=config_rel,
                manifest_path=manifest_path.relative_to(repo_root).as_posix(),
                artifact_paths=[
                    csv_path.relative_to(repo_root).as_posix(),
                    png_path.relative_to(repo_root).as_posix(),
                ],
                parameter_point_id=parameter_point_id,
                parameter_overrides={"depth": depth, "depths_arg": depths_arg},
            )

            rows.append(
                {
                    "sweep_id": sweep_id,
                    "run_id": run_id,
                    "family_id": family_id,
                    "config_path": config_rel,
                    "manifest_path": manifest_path.relative_to(repo_root).as_posix(),
                    "parameter_point_id": parameter_point_id,
                    "parameter_overrides": json.dumps({"depth": depth, "depths": depths_arg}, sort_keys=True),
                    "final_depth": final_row["final_depth"],
                    "final_upper_root": final_row["final_upper_root"],
                    "final_lower_root": final_row["final_lower_root"],
                    "interval_root_width": final_row["interval_root_width"],
                    "last_step_drift": last_drift,
                    "reference_root": reference_root,
                    "abs_error": abs_error,
                    "artifact_index_path": artifact_index_path.relative_to(repo_root).as_posix(),
                }
            )

    summary_csv = sweep_root / "sweep_summary.csv"
    summary_json = sweep_root / "sweep_summary.json"
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
                "plan_path": plan_path.relative_to(repo_root).as_posix(),
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
