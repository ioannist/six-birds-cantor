#!/usr/bin/env python3
"""Receipts for scoped constructive repairs; never closes the old ledger."""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from contextual_cantor.pressure_extension import (
    construct_pressure_extension, predictive_price_lower_bound, construct_forced_completion,
    completion_predictive_price_lower_bound, completion_affinity_loss_bound, affinity_pressure_proxy,
)
from contextual_cantor.retained_memory import construct_retained_memory
from contextual_cantor.lawful_kernel import noise_noncollapse_constants
from contextual_cantor.continuous_kernel_substrate import PilotParameters, build_initial_state, step_substrate
from contextual_cantor.cocycle_pressure import KernelHistoryStep, history_log_norm, conditioned_history_log_mass
from run_continuous_pressure_checks import _observable_value, _series_for_step


def build_report(count: int) -> dict:
    if count < 2:
        raise ValueError("at least two steps required")
    witness = construct_pressure_extension()
    forced = construct_forced_completion(witness)
    memory = construct_retained_memory()
    memory_price = completion_predictive_price_lower_bound(*memory.completions)
    # Keep a short exact lower bound instead of printing enormous fractions
    # produced by the finite 80-step informant in this second instance.
    short_memory_price = Q(1, 10**20)
    if memory_price < short_memory_price:
        raise ArithmeticError("short retained-memory price bound failed")
    affinity_loss = completion_affinity_loss_bound(witness.forward, witness.backward)
    memory_affinity_loss = completion_affinity_loss_bound(*memory.completions)
    if memory_affinity_loss < short_memory_price:
        raise ArithmeticError("short retained-memory affinity bound failed")
    d, epsilon = 8, Q(1, 25)
    state = build_initial_state(n=d, seed=17, pilot_parameters=PilotParameters(kernel_minorization=float(epsilon)))
    rng = random.Random(17)
    history = []
    for _ in range(count):
        kernel = [list(row) for row in state.kernel]
        snap = step_substrate(state, rng)
        observable = max(0.05, min(10.0, _observable_value(_series_for_step(snap))))
        history.append(KernelHistoryStep(kernel, observable))
    constants = noise_noncollapse_constants(d, epsilon)
    fixed = [KernelHistoryStep([[float(x) for x in row] for row in witness.kernel], math.log(2))] * count
    full = history_log_norm(fixed, 0.5)
    conditioned = [conditioned_history_log_mass(fixed, 0.5, [float(x) for x in cert.stationary])
                   for cert in (witness.forward, witness.backward)]
    restricted = [history_log_norm(fixed, 0.5, fibers=[set(group)] * (count + 1))
                  for group in witness.groups]
    price = predictive_price_lower_bound(witness)
    return {
        "schema_version": "v1",
        "all_four_original_theorems_restored": False,
        "paper_changed": False,
        "lawfulness": {
            "variant": "explicit_uniform_minorization_after_noise_and_at_initialization",
            "epsilon": str(epsilon), "uniform_entry_floor_real_arithmetic": str(epsilon / d),
            "sample_steps": count,
            "sample_min_entry": min(x for step in history for row in step.kernel for x in row),
            "noncollapse": {
                "scope": "almost_sure_under_ideal_independent_uniform_noise_in_real_arithmetic",
                "coordinate_jump": str(constants.coordinate_jump),
                "conditional_probability": str(constants.conditional_probability),
                "strong_original_shell_certified": False,
                "original_stronger_shell_sixfold_activity_certified": False,
                "all_six_functions_nonredundant_on_new_carrier": "analytic_counterfactual_construction",
            },
        },
        "pressure": {
            "scope": "full_repaired_loop_on_global_positive_box_with_clamped_selector_potential",
            "observable_range": [0.05, 10],
            "sample_at_one_identity_error": abs(history_log_norm(history, 1) + sum(step.observable for step in history)),
            "existence_and_unique_root": "analytic_theorem_applies_to_real_arithmetic_variant",
            "fully_mechanized_matrix_instance": False,
        },
        "extension": {
            "scope": "all_frozen_kernel_total_history_partitions_same_lens_tau_and_package",
            "kernel": [[str(x) for x in row] for row in witness.kernel],
            "groups": witness.groups,
            "fixed_forward": [str(x) for x in witness.forward.stationary],
            "fixed_reverse": [str(x) for x in witness.backward.stationary],
            "partition_identity_scope": "every_real_entrywise_weight_function_and_every_horizon",
            "exact_split_pair": True,
            "forced_lens": "spectral_lens",
            "post_forcing_fixed": [str(x) for x in forced.stationary],
            "forcing_changes_fixed_object": forced.stationary != witness.forward.stationary,
            "full_evolving_cocycle_collision_certified": False,
        },
        "retained_memory_extension": {
            "scope": "real_arithmetic_full_future_kernel_and_selector_cocycle_on_declared_positive_warm_start_carrier",
            "actual_P5_retained": True,
            "warm_start_carrier_is_original_stronger_shell": False,
            "source_lens_score_interval": ["37/50", "21/25"],
            "rational_algebra_instance_lens_score": str(memory.lens_score),
            "exact_rational_recoupling": True,
            "readout_changes_exactly": memory.completions[0].stationary != memory.completions[1].stationary,
            "maximum_exact_noise_below": "1/1000000",
            "shared_future_cocycle": "analytic_source_readset_and_recoupling_proof",
            "fully_mechanized_simulator_bridge": False,
            "same_kernel_completion_predictive_KL_rate_lower_bound": str(short_memory_price),
            "initial_conditioned_history_pressure_gap_in_this_positive_instance": 0,
            "relative_affinity_pressure_gap_lower_bound_at_half": str(short_memory_price),
        },
        "consequence": {
            "predictive_KL_rate_lower_bound": str(price),
            "predictive_scope": "stationary_completion_processes_vs_best_current_state_only_autonomous_predictor",
            "initial_conditioned_history_pressure_gap_in_this_positive_instance": 0,
            "relative_affinity_pressure": {
                "explicit_changed_path_potential": "minus_t_log_completed_transition_over_common_lower_predictor",
                "parameter": 0.5,
                "exact_rational_gap_lower_bound": str(affinity_loss),
                "finite_weighted_gap": -sum(affinity_pressure_proxy(witness.forward, witness.backward, z, 0.5, count)
                                            for z in (0, 1)) / 2,
                "hybrid_gap_formula": "P0(s)-sum_w(P0(s)+Q_z(t))=-sum_w Q_z(t)",
                "completion_channel_frozen_in_augmented_carrier": True,
                "original_measure_disintegration_identified": False,
            },
            "initial_conditioning_finite_horizon_differences": [(full - value) / count for value in conditioned],
            "two_actual_package_survival_finite_pressure_gaps": [(full - value) / count for value in restricted],
            "survival_is_persistent_fixed_point_disintegration": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=96)
    args = parser.parse_args()
    if args.steps < 2:
        parser.error("steps must be at least two")
    report = build_report(args.steps)
    out = ROOT / "results/core_restoration/report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
