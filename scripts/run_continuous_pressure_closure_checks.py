#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any


PRIMITIVES = ("P1", "P2", "P3", "P4", "P5", "P6")
ALLOWED_DECISION = {"closed_on_working_class", "working_class_narrowed_and_closed"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_prereqs(repo_root: Path) -> None:
    import subprocess

    pressure_report = repo_root / "results" / "continuous_pressure_existence" / "report.json"
    forward_report = repo_root / "results" / "continuous_forward_invariance" / "report.json"
    if not pressure_report.exists():
        subprocess.run(["python", "scripts/run_continuous_pressure_checks.py"], cwd=repo_root, check=True)
    if not forward_report.exists():
        subprocess.run(["python", "scripts/run_forward_invariant_regime_checks.py"], cwd=repo_root, check=True)


def _observable(step: dict[str, Any]) -> float:
    action_weights = list(step["action_weights"].values())
    total = sum(action_weights)
    entropy = 0.0
    if total > 0.0:
        for w in action_weights:
            if w > 0.0:
                p = w / total
                entropy -= p * math.log(p)
    return math.log1p(
        float(step["variation"])
        + 0.25 * float(step["lens"]["score"])
        + 0.3 * float(step["packaging"]["score"])
        + 0.05 * float(step["p6"]["budget"]) / 12.0
        + 0.05 * float(step["p3"]["tau"])
        + 0.05 * entropy
    )


def _fekete_proxy(values: list[float], s: float) -> dict[str, float]:
    from contextual_cantor.time_partition import time_partition_pressure_proxy
    if not values:
        return {"pressure_proxy": 0.0, "gap_proxy": 0.0, "sign": 0.0}
    logs = [time_partition_pressure_proxy(values[:i], s) for i in range(1, len(values) + 1)]
    pressure = logs[-1]
    gap = max((abs(b - a) for a, b in zip(logs, logs[1:])), default=0.0)
    sign = 1.0 if pressure > 0 else (-1.0 if pressure < 0 else 0.0)
    return {"pressure_proxy": pressure, "gap_proxy": gap, "sign": sign}


def _run_config(repo_root: Path, cfg_path: Path) -> dict[str, Any]:
    from contextual_cantor.continuous_kernel_substrate import PilotParameters, simulate_substrate

    cfg = _load_json(cfg_path)
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
    values = [_observable(step) for step in trajectory]
    s_grid = [0.5, 1.0, 1.5]
    profiles = {f"{s:.1f}": _fekete_proxy(values, s) for s in s_grid}
    return {
        "family_id": cfg["family_id"],
        "config_path": str(cfg_path.relative_to(repo_root)),
        "kernel_dim": len(state.kernel),
        "seed": int(params["seed"]),
        "steps": len(trajectory),
        "all_six_primitives_active": all(state.primitive_activity.get(p, False) for p in PRIMITIVES),
        "shell_exit_count": sum(
            not (2.1 <= step["p6"]["budget"] <= 12.1
                 and 0.55 <= step["p3"]["tau"] <= 1.05
                 and step["selector_diagnostics"]["lens_margin"] >= 0.01
                 and step["selector_diagnostics"]["packaging_margin"] >= 0.01)
            for step in trajectory
        ),
        "min_lens_margin": min(step["selector_diagnostics"]["lens_margin"] for step in trajectory) if trajectory else 0.0,
        "min_packaging_margin": min(step["selector_diagnostics"]["packaging_margin"] for step in trajectory) if trajectory else 0.0,
        "budget_range": [min(state.budget_history), max(state.budget_history)] if state.budget_history else [state.budget, state.budget],
        "tau_range": [min(state.tau_history), max(state.tau_history)] if state.tau_history else [state.tau, state.tau],
        "growth_bound_proxy": max(values) - min(values) if values else 0.0,
        "fekete_gap_proxy": profiles["1.0"]["gap_proxy"],
        "pressure_profiles": profiles,
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    import sys

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    _ensure_prereqs(repo_root)

    config_paths = [
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json",
        repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json",
    ]
    runs = [_run_config(repo_root, path) for path in config_paths]

    pressure_report = _load_json(repo_root / "results" / "continuous_pressure_existence" / "report.json")
    forward_report = _load_json(repo_root / "results" / "continuous_forward_invariance" / "report.json")

    monotonicity_support = []
    for run in runs:
        profile = run["pressure_profiles"]
        monotonicity_support.append(profile["0.5"]["pressure_proxy"] >= profile["1.0"]["pressure_proxy"] >= profile["1.5"]["pressure_proxy"])

    decision = "closed_on_working_class"
    if not all(run["all_six_primitives_active"] for run in runs):
        decision = "working_class_narrowed_and_closed"
    if not all(monotonicity_support):
        decision = "working_class_narrowed_and_closed"

    report = {
        "schema_version": "v1",
        "report_id": "continuous_pressure_closure_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "decision": decision,
        "closed_class_id": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "selected_pressure_route": "fekete_sup_cocycle_route",
        "selected_observable_family": "selector_weighted_operator_growth_observable",
        "support_sources": {
            "pressure_existence_report": "results/continuous_pressure_existence/report.json",
            "forward_invariance_report": "results/continuous_forward_invariance/report.json",
        },
        "support_summary": {
            "all_six_primitives_active": all(run["all_six_primitives_active"] for run in runs),
            "shell_exit_count": sum(run["shell_exit_count"] for run in runs),
            "mean_fekete_gap_proxy": statistics.fmean(run["fekete_gap_proxy"] for run in runs),
            "monotonicity_support_fraction": sum(1 for flag in monotonicity_support if flag) / max(1, len(monotonicity_support)),
            "pressure_proxy_mean": statistics.fmean(
                [pressure_report["support_summary"]["pressure_proxy_mean"], statistics.fmean(run["pressure_profiles"]["1.0"]["pressure_proxy"] for run in runs)]
            ),
            "sampled_bounds": {
                "lens_margin_min": min(run["min_lens_margin"] for run in runs),
                "packaging_margin_min": min(run["min_packaging_margin"] for run in runs),
                "budget_range": [min(run["budget_range"][0] for run in runs), max(run["budget_range"][1] for run in runs)],
                "tau_range": [min(run["tau_range"][0] for run in runs), max(run["tau_range"][1] for run in runs)],
            },
            "forward_invariance_decision": forward_report.get("decision"),
        },
        "runs": runs,
        "notes": [
            "Support evidence only; the closure lives in the theorem note.",
            "The working class remains the shell-stable continuous full-loop class, not a finite proxy.",
        ],
    }

    out_dir = repo_root / "results" / "continuous_pressure_closure"
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
                "fekete_gap_proxy": run["fekete_gap_proxy"],
                "shell_exit_count": run["shell_exit_count"],
                "min_lens_margin": run["min_lens_margin"],
                "min_packaging_margin": run["min_packaging_margin"],
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
