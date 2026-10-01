#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _compute_margins(repo_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    import sys
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.continuous_kernel_substrate import (
        PilotParameters,
        build_initial_state,
        step_substrate,
    )
    import random

    params = config["parameters"]["pilot_parameters"]
    pilot_params = PilotParameters(
        lens_hysteresis=params["lens_hysteresis"],
        packaging_hysteresis=params["packaging_hysteresis"],
        budget_income_scale=params["budget_income_scale"],
        budget_cost_scale=params["budget_cost_scale"],
        tau_initial=params["tau_initial"],
        action_temperature_bias=params["action_temperature_bias"],
        lens_temperature_shift=params["lens_temperature_shift"],
    )
    steps = int(config["parameters"]["steps_run"])
    kernel_dim = int(config["parameters"]["kernel_dim"])
    seed = int(config["parameters"]["seed"])
    state = build_initial_state(n=kernel_dim, seed=seed, pilot_parameters=pilot_params)
    rng = random.Random(seed)
    shell_bounds = {
        "budget": [2.1, 12.1],
        "tau": [0.55, 1.05],
        "lens_margin": 0.01,
        "packaging_margin": 0.01,
    }
    shell_exit_count = 0
    min_lens_margin = float("inf")
    min_packaging_margin = float("inf")
    for _ in range(steps):
        snapshot = step_substrate(state, rng, state.primitive_activity)
        lens_margin = snapshot["selector_diagnostics"]["lens_margin"]
        min_lens_margin = min(min_lens_margin, lens_margin)
        packaging_margin = snapshot["selector_diagnostics"]["packaging_margin"]
        min_packaging_margin = min(min_packaging_margin, packaging_margin)
        budget = float(snapshot["p6"]["budget"])
        tau = float(snapshot["p3"]["tau"])
        if (not shell_bounds["budget"][0] <= budget <= shell_bounds["budget"][1]
                or not shell_bounds["tau"][0] <= tau <= shell_bounds["tau"][1]
                or lens_margin < shell_bounds["lens_margin"]
                or packaging_margin < shell_bounds["packaging_margin"]):
            shell_exit_count += 1
    return {
        "family_id": config["family_id"],
        "steps": steps,
        "kernel_dim": kernel_dim,
        "seed": seed,
        "shell_bounds_used": shell_bounds,
        "shell_exit_count": shell_exit_count,
        "min_lens_margin": min_lens_margin,
        "min_packaging_margin": min_packaging_margin,
        "budget_range": [min(state.budget_history), max(state.budget_history)] if state.budget_history else [state.budget, state.budget],
        "tau_range": [min(state.tau_history), max(state.tau_history)] if state.tau_history else [state.tau, state.tau],
        "primitive_activity_indicators": dict(state.primitive_activity),
        "all_six_primitives_active": all(state.primitive_activity.values()),
        "scope": "sampled_trajectory_only",
        "forward_invariance_certified": False,
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "results" / "continuous_forward_invariance"
    out_dir.mkdir(parents=True, exist_ok=True)

    configs = [
        _load_json(repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel.json"),
        _load_json(repo_root / "configs" / "experiments" / "generated" / "continuous_full_loop_kernel_shell.json"),
    ]
    rows = [_compute_margins(repo_root, cfg) for cfg in configs]
    report = {
        "schema_version": "v1",
        "report_id": "continuous_forward_invariance_v1",
        "generated_at_utc": "2026-03-18T00:00:00Z",
        "decision": "working_class_narrowed_and_closed",
        "closed_class_id": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "shell_definition": {
            "budget": [2.1, 12.1],
            "tau": [0.55, 1.05],
            "lens_margin": 0.01,
            "packaging_margin": 0.01,
        },
        "runs": rows,
        "summary": {
            "shell_exit_count": sum(row["shell_exit_count"] for row in rows),
            "min_lens_margin": min(row["min_lens_margin"] for row in rows),
            "min_packaging_margin": min(row["min_packaging_margin"] for row in rows),
            "all_six_primitives_active": all(row["all_six_primitives_active"] for row in rows),
        },
        "notes": [
            "Support evidence only; the proof still lives in the scaffold.",
            "The narrowed shell keeps selector margins and budget/tau ranges bounded away from collapse."
        ],
    }
    import sys
    sys.path.insert(0, str(repo_root / "src"))
    from contextual_cantor.audit_status import mark_diagnostic_report
    mark_diagnostic_report(report, "sampled_trajectory_only")

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as f:
        csv_fieldnames = [
            "family_id",
            "steps",
            "kernel_dim",
            "seed",
            "shell_exit_count",
            "min_lens_margin",
            "min_packaging_margin",
            "budget_range",
            "tau_range",
            "all_six_primitives_active",
        ]
        writer = csv.DictWriter(
            f,
            fieldnames=csv_fieldnames,
        )
        writer.writeheader()
        writer.writerows({k: row[k] for k in csv_fieldnames} for row in rows)
    print(f"wrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
