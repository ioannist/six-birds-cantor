#!/usr/bin/env python3
"""Reproduce the original-target shell and conditional-pressure obstructions."""
from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys


def run() -> int:
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "src"))
    from contextual_cantor.continuous_kernel_substrate import (
        KernelSubstrateState, PilotParameters, step_substrate,
    )
    from contextual_cantor.original_claim_obstructions import (
        initial_conditioned_partition, uniform_shell_certificate,
    )
    from contextual_cantor.pressure_extension import construct_pressure_extension, construct_forced_completion

    config_path = root / "configs/experiments/generated/continuous_full_loop_kernel_shell.json"
    cfg = json.loads(config_path.read_text())
    params = PilotParameters(**cfg["parameters"]["pilot_parameters"])
    kernel = [[0.05]*20 for _ in range(20)]
    state = KernelSubstrateState(kernel, 1.05, 3.0, 0.0, 0, "boot",
        "spectral_lens", "partition_cluster_packaging", [1.0]*3,
        previous_kernel=[row[:] for row in kernel], pilot_parameters=params)
    step = step_substrate(state, random.Random(cfg["parameters"]["seed"]))
    exact = uniform_shell_certificate()
    witness = construct_pressure_extension()
    forced = construct_forced_completion(witness)
    if (not step["selector_diagnostics"]["lens_margin"] > 0.01
            or not step["selector_diagnostics"]["packaging_margin"] > 0.01
            or not state.tau >= float(exact["tau_next_lower"]) > 1.05):
        raise ArithmeticError("source replay no longer matches the shell certificate")
    readouts = []
    for name, physical, initial in (("forward", witness.kernel, witness.forward.stationary),
                                    ("transpose", witness.reversed_kernel, witness.backward.stationary)):
        for n in (0, 1, 2, 5, 15):
            audit = initial_conditioned_partition(physical, initial, n)
            spectral = initial_conditioned_partition(physical, forced.stationary, n)
            if audit != spectral or audit != Q(1,2)**n:
                raise ArithmeticError("equal-original-partition control failed")
            readouts.append({"kernel": name, "horizon": n, "audit": str(audit), "spectral": str(spectral)})
    tracked_inputs = [
        "src/contextual_cantor/continuous_kernel_substrate.py",
        "src/contextual_cantor/original_claim_obstructions.py",
        "src/contextual_cantor/pressure_extension.py",
        "src/contextual_cantor/exact_completion.py",
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        "lean/OriginalShell.lean", "lean/ConditionalPressure.lean",
        "lean/CompletionForcing.lean", "scripts/run_original_claim_obstructions.py",
    ]
    report = {
        "schema_version": "v1", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "main_theorem_package_complete": False,
        "original_update_law_modified": False,
        "input_sha256": {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in tracked_inputs},
        "shell": {
            "scope": "twenty_state_operational_rectangle_not_arbitrary_invariant_subclass",
            "seed_reachability": "not_established", "original_shell_membership": "not_established",
            "initial": {"kernel": "all entries 1/20", "tau": "21/20", "budget": 3,
                        "phase": 0, "lens": "spectral_lens", "packaging": "partition_cluster_packaging",
                        "switch_history": "empty", "primitive_activity": "all six enabled"},
            "exact_bounds": {name: str(value) for name, value in exact.items()},
            "floating_source_replay": {"tau_next": state.tau,
                "lens_score": step["lens"]["score"], "packaging_score": step["packaging"]["score"],
                "eta": step["p1"]["eta"], "selector_margins": step["selector_diagnostics"]},
            "noise_scope": "tau updated before noise; exact escape independent of legal noise input",
            "formalization_scope": "selector isolation, variance cap and clamped tau escape; source bridge analytic",
        },
        "pressure": {
            "scope": "genuine_fixed_initial_law_disintegration_of_same_frozen_positive_potential",
            "kernel_dimension": 4, "original_shell_membership": "not_established",
            "nonfactorizing_fixed_object_family": True,
            "actual_completion_forcing_creates_distinct_object": True,
            "conditional_gap": "identically zero for all real s; Lean limit theorem, not finite sampling",
            "changed_path_potential": False, "likelihood_ratio_price": False,
            "frozen_observable": "q=log(2), same potential as existing exact transpose witness",
            "full_loop_selector_observable_bridge": "not_established",
            "exact_s_one_readouts": readouts,
        },
        "review": "docs/internal/original_claim_obstructions_2026_10_02.md",
    }
    out = root / "results/original_claim_obstructions/report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
