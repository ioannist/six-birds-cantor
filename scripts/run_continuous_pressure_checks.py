#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any


PRIMITIVES = ("P1", "P2", "P3", "P4", "P5", "P6")
WORKING_ROUTE = "switched_operator_cocycle_pressure"
OBSERVABLE_FAMILY = "selector_weighted_operator_growth_observable"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_support_artifacts(repo_root: Path) -> None:
    needed = [
        repo_root / "results" / "continuous_kernel_pilot" / "report.json",
        repo_root / "results" / "continuous_kernel_pilot" / "knockout_report.json",
        repo_root / "results" / "continuous_forward_invariance" / "report.json",
    ]
    if all(path.exists() for path in needed):
        return

    import subprocess

    if not needed[0].exists() or not needed[1].exists():
        subprocess.run(["python", "scripts/run_continuous_kernel_pilot.py"], cwd=repo_root, check=True)
    if not needed[2].exists():
        subprocess.run(["python", "scripts/run_forward_invariant_regime_checks.py"], cwd=repo_root, check=True)


def _series_for_step(step: dict[str, Any]) -> dict[str, float]:
    action_weights = list(step["action_weights"].values())
    selector_entropy = 0.0
    total = sum(action_weights)
    if total > 0:
        for weight in action_weights:
            if weight > 0:
                p = weight / total
                selector_entropy -= p * math.log(p)
    return {
        "variation": float(step["variation"]),
        "lens_score": float(step["lens"]["score"]),
        "packaging_score": float(step["packaging"]["score"]),
        "budget": float(step["p6"]["budget"]),
        "tau": float(step["p3"]["tau"]),
        "selector_entropy": selector_entropy,
    }


def _observable_value(step_values: dict[str, float]) -> float:
    return math.log1p(
        max(0.0, step_values["variation"])
        + 0.28 * step_values["lens_score"]
        + 0.32 * step_values["packaging_score"]
        + 0.10 * (step_values["budget"] / 12.0)
        + 0.08 * step_values["tau"]
        + 0.05 * step_values["selector_entropy"]
    )


def _pressure_proxy(series: list[float], s: float) -> float:
    from contextual_cantor.time_partition import time_partition_pressure_proxy
    n = len(series)
    if n == 0:
        return 0.0
    return time_partition_pressure_proxy(series, s)


def _subadditivity_defect(series: list[float], s: float) -> float:
    from contextual_cantor.time_partition import time_partition_log
    if len(series) < 4:
        return 0.0
    whole = time_partition_log(series, s)
    splits = []
    for k in range(1, len(series)):
        left = time_partition_log(series[:k], s)
        right = time_partition_log(series[k:], s)
        defect = abs(whole - (left + right))
        splits.append(defect)
    return statistics.fmean(splits) if splits else 0.0


def _slope(series: list[float], s: float) -> float:
    if len(series) < 20:
        return 0.0
    window = max(5, len(series) // 5)
    first = _pressure_proxy(series[:window], s)
    last = _pressure_proxy(series[-window:], s)
    return last - first


def _run_config(repo_root: Path, config_path: Path) -> dict[str, Any]:
    from contextual_cantor.continuous_kernel_substrate import PilotParameters, simulate_substrate

    cfg = _load_json(config_path)
    params = cfg["parameters"]
    pilot = params["pilot_parameters"]
    sim = simulate_substrate(
        steps=int(params["steps_run"]),
        n=int(params["kernel_dim"]),
        seed=int(params["seed"]),
        pilot_parameters=PilotParameters(
            lens_hysteresis=float(pilot["lens_hysteresis"]),
            packaging_hysteresis=float(pilot["packaging_hysteresis"]),
            budget_income_scale=float(pilot["budget_income_scale"]),
            budget_cost_scale=float(pilot["budget_cost_scale"]),
            tau_initial=float(pilot["tau_initial"]),
            action_temperature_bias=float(pilot["action_temperature_bias"]),
            lens_temperature_shift=float(pilot["lens_temperature_shift"]),
        ),
    )
    trajectory = sim["trajectory"]
    state = sim["state"]
    values = [_observable_value(_series_for_step(step)) for step in trajectory]
    s_grid = [0.75, 1.0, 1.25]
    pressure_grid = {f"{s:.2f}": _pressure_proxy(values, s) for s in s_grid}
    monotonicity = {
        "decreasing_pairs": sum(
            1
            for a, b in zip(
                [pressure_grid["0.75"], pressure_grid["1.00"]],
                [pressure_grid["1.00"], pressure_grid["1.25"]],
            )
            if a >= b
        ),
        "grid_values": pressure_grid,
        "proxy": pressure_grid["0.75"] >= pressure_grid["1.00"] >= pressure_grid["1.25"],
    }
    return {
        "family_id": cfg["family_id"],
        "config_path": str(config_path.relative_to(repo_root)),
        "steps": len(trajectory),
        "kernel_dim": len(state.kernel),
        "seed": int(params["seed"]),
        "route": WORKING_ROUTE,
        "observable_family": OBSERVABLE_FAMILY,
        "observable_mean": statistics.fmean(values) if values else 0.0,
        "observable_stdev": statistics.pstdev(values) if len(values) > 1 else 0.0,
        "pressure_proxy": pressure_grid["1.00"],
        "growth_rate_proxy": _slope(values, 1.0),
        "subadditivity_defect_proxy": _subadditivity_defect(values, 1.0),
        "monotonicity_proxy": monotonicity,
        "seed_variation": statistics.pstdev(values) if len(values) > 1 else 0.0,
        "primitive_activity": dict(state.primitive_activity),
        "selector_entropy_mean": statistics.fmean(_series_for_step(step)["selector_entropy"] for step in trajectory) if trajectory else 0.0,
        "budget_weighted_activity_mean": statistics.fmean(
            (_series_for_step(step)["budget"] / 12.0) * (_series_for_step(step)["lens_score"] + _series_for_step(step)["packaging_score"])
            for step in trajectory
        ) if trajectory else 0.0,
        "all_six_primitives_active": all(state.primitive_activity.get(p, False) for p in PRIMITIVES),
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    import sys

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    _ensure_support_artifacts(repo_root)

    config_paths = [
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json",
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json",
    ]
    runs = [_run_config(repo_root, path) for path in config_paths]

    pressures = [run["pressure_proxy"] for run in runs]
    subdefects = [run["subadditivity_defect_proxy"] for run in runs]
    monotonicity_flags = [run["monotonicity_proxy"]["proxy"] for run in runs]
    all_six = [run["all_six_primitives_active"] for run in runs]

    report = {
        "schema_version": "v1",
        "report_id": "continuous_pressure_existence_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "working_class_id": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "selected_pressure_route": WORKING_ROUTE,
        "selected_observable_family": OBSERVABLE_FAMILY,
        "witness_configs": [run["config_path"] for run in runs],
        "support_summary": {
            "pressure_proxy_mean": statistics.fmean(pressures) if pressures else 0.0,
            "pressure_proxy_stdev": statistics.pstdev(pressures) if len(pressures) > 1 else 0.0,
            "subadditivity_defect_proxy_mean": statistics.fmean(subdefects) if subdefects else 0.0,
            "monotonicity_proxy_support_fraction": sum(1 for flag in monotonicity_flags if flag) / max(1, len(monotonicity_flags)),
            "all_six_primitives_active": all(all_six),
            "support_runs": runs,
        },
        "decision": "pressure_existence_scaffolded",
        "notes": [
            "Support evidence only; the pressure theorem remains a scaffold.",
            "The pressure candidate remains six-birds-native on the closed shell-stable class."
        ],
    }

    out_dir = repo_root / "results" / "continuous_pressure_existence"
    out_dir.mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0, str(repo_root / "src"))
    from contextual_cantor.audit_status import mark_diagnostic_report
    mark_diagnostic_report(report, "bounded_observable_time_sum_diagnostic")

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    rows = []
    for run in runs:
        rows.append(
            {
                "family_id": run["family_id"],
                "seed": run["seed"],
                "kernel_dim": run["kernel_dim"],
                "pressure_proxy": run["pressure_proxy"],
                "growth_rate_proxy": run["growth_rate_proxy"],
                "subadditivity_defect_proxy": run["subadditivity_defect_proxy"],
                "monotonicity_proxy": run["monotonicity_proxy"]["proxy"],
            }
        )
    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
