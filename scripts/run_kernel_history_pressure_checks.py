#!/usr/bin/env python3
"""Finite history-product checks on unrounded kernels from the full update.

This constructs the repaired observable on actual sampled updates. It does
not certify shell supremum limits or a uniform entry lower bound.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from contextual_cantor.cocycle_pressure import KernelHistoryStep, history_log_norm
from contextual_cantor.continuous_kernel_substrate import PilotParameters, build_initial_state, step_substrate
from run_continuous_pressure_checks import _observable_value, _series_for_step


def run_config(path: Path, count: int) -> dict:
    config = json.loads(path.read_text())
    params = config["parameters"]
    pilot = PilotParameters(**params["pilot_parameters"])
    state = build_initial_state(n=params["kernel_dim"], seed=params["seed"], pilot_parameters=pilot)
    rng = random.Random(params["seed"])
    steps, fibers = [], []
    # The extra state supplies the endpoint fiber; it contributes no branch weight.
    for t in range(count + 1):
        kernel = [list(row) for row in state.kernel]
        snapshot = step_substrate(state, rng, params["primitive_activity"])
        group = next(group for group in snapshot["packaging"]["groups"] if group)
        fibers.append(set(group))
        if t < count:
            # Explicit positive bounded selector potential for the new family.
            # This is a declared change from the old time-sum observable.
            q = max(0.05, min(10.0, _observable_value(_series_for_step(snapshot))))
            steps.append(KernelHistoryStep(kernel, q))
    profiles = {}
    for s in [0.0, 0.5, 1.0, 1.5]:
        full = history_log_norm(steps, s)
        restricted = history_log_norm(steps, s, fibers=fibers)
        cut = count // 2
        comparison = history_log_norm(steps[:cut], s) + history_log_norm(steps[cut:], s) - full
        profiles[str(s)] = {"full_log_norm": full, "finite_pressure": full / count,
                            "fiber_log_norm": restricted if math.isfinite(restricted) else None,
                            "fiber_has_positive_path": math.isfinite(restricted),
                            "concatenation_slack": comparison}
    return {"family_id": config["family_id"], "steps": count, "profiles": profiles,
            "sample_min_kernel_entry": min(k for step in steps for row in step.kernel for k in row),
            "all_sampled_fibers_proper": all(len(fiber) < len(state.kernel) for fiber in fibers),
            "observable_range": [min(step.observable for step in steps), max(step.observable for step in steps)],
            "at_one_identity_error": abs(profiles["1.0"]["full_log_norm"] + sum(step.observable for step in steps))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=64)
    args = parser.parse_args()
    if args.steps < 2:
        parser.error("steps must be at least two")
    configs = [ROOT / "configs/experiments/generated" / name
               for name in ["continuous_full_loop_kernel.json", "continuous_full_loop_kernel_shell.json"]]
    report = {"schema_version": "v2", "decision": "diagnostic_only_not_certified",
              "observable": "kernel_history_product_with_clamped_positive_selector_potential",
              "conditioning": "microstate_survival_in_first_selected_packaging_cell_at_every_step",
              "main_theorems_certified": False, "uniform_shell_entry_bound_certified": False,
              "fixed_point_stratum_disintegration_certified": False,
              "runs": [run_config(path, args.steps) for path in configs]}
    out = ROOT / "results/kernel_history_pressure"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(f"wrote {out / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
