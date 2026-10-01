"""Counterexamples to the mathematical defects found in the October audit."""

from __future__ import annotations

import math

import pytest

from contextual_cantor import certified_bracketing, interval_utils
from contextual_cantor.contextual_certification import (
    certify_markov_equal_ratio_dimension,
    perron_bounds_collatz_wielandt,
)
from contextual_cantor.continuous_kernel_substrate import (
    apply_p3_timescale_update,
    apply_p6_budget_update,
    build_initial_state,
    compute_packaging_fixed_points,
    detect_packaging_saturation,
    evolve_forget_reinstate,
    iterate_completion_endomap,
    packaging_macro_admissibility,
)
from contextual_cantor.finite_state_symbolic import spectral_radius_power_iteration
from contextual_cantor.local_ifs import Interval
from contextual_cantor.transfer_operator import build_transfer_matrix, spectral_radius
from contextual_cantor.time_partition import time_partition_pressure_proxy


@pytest.mark.parametrize("radius", [spectral_radius, spectral_radius_power_iteration])
@pytest.mark.parametrize("matrix,expected", [
    ([[0.0, 4.0], [1.0, 0.0]], 2.0),
    ([[0.0, 8.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 2.0),
    ([[1.0, 20.0], [0.0, 1.0]], 1.0),
    ([[0.0, 1.0], [0.0, 0.0]], 0.0),
    ([[0.0, 0.0], [0.0, 3.0]], 3.0),
])
def test_periodic_and_reducible_perron_matrices(radius, matrix, expected):
    assert radius(matrix) == pytest.approx(expected, abs=1e-12)


def test_perron_failure_is_not_silently_returned():
    with pytest.raises(RuntimeError):
        spectral_radius([[0.0, 4.0], [1.0, 0.0]], max_iter=1)
    with pytest.raises(ValueError):
        spectral_radius([[math.nan]])
    with pytest.raises(ValueError):
        perron_bounds_collatz_wielandt([[-1]], 1)


def test_transfer_ignores_unreachable_branching_component():
    config = {"engine": "finite_state_symbolic", "parameters": {
        "start_states": ["a"], "edges": [
            {"src": "a", "dst": "a", "ratio": 0.5},
            {"src": "b", "dst": "b", "ratio": 0.5},
            {"src": "b", "dst": "b", "ratio": 0.5},
        ],
    }}
    assert build_transfer_matrix(config, 0.0) == [[1.0]]


def test_float_margin_cannot_be_called_certified(monkeypatch):
    monkeypatch.setattr(certified_bracketing, "HAS_MPMATH_IV", False)
    with pytest.raises(ValueError, match="interval evaluator"):
        certified_bracketing.certify_monotone_decreasing_root(
            func_interval=None, func_point=lambda x: 1 - x,
            s_min=0, s_max=2, precision_dps=80, max_steps=20,
        )


def test_interval_precision_and_export_are_outward():
    mp = pytest.importorskip("mpmath")
    old = mp.iv.dps
    result = interval_utils.evaluate_function_interval_at_point(
        0.0, 90, lambda x: mp.iv.mpf(1) / 3, lambda x: 1 / 3,
    )
    assert mp.iv.dps == old
    with mp.workdps(100):
        assert mp.mpf(result.lower) <= mp.mpf(1) / 3 <= mp.mpf(result.upper)
    assert result.certified


def test_general_markov_config_has_no_fibonacci_reference():
    pytest.importorskip("mpmath")
    config = {"family_id": "other", "parameters": {
        "base": 4, "start_digits": [0, 2], "transition_digits": {"0": [0, 2], "2": [0, 2]},
    }}
    result = certify_markov_equal_ratio_dimension(config)
    assert result["reference_root"] is None
    assert result["certified_lower"] <= 0.5 <= result["certified_upper"]


def test_nearly_disjoint_intervals_do_not_construct_reversed_intersection():
    left = Interval(0.0, 0.5)
    right = Interval(math.nextafter(0.5, math.inf), 1.0)
    assert left.intersection(right) is None


def test_completion_metadata_and_actual_macro_test_are_separate():
    kernel = [[0.9, 0.1], [0.2, 0.8]]
    packaging = {"groups": [[0], [1]], "support": [0.5, 0.5]}
    summary = iterate_completion_endomap(
        [1.0, 0.0], kernel, 1.0, "spectral_lens", packaging_state=packaging, max_iter=1,
    )
    assert summary["status"] == "nonconvergent"
    assert summary["package_count"] == 2
    assert summary["certified_fixed_point"] is False
    assert packaging_macro_admissibility(summary)["admissible"] is None
    macro = packaging_macro_admissibility(summary, kernel=kernel, groups=[[0], [1]])
    assert macro["admissible"] is True  # identity partition is always lumpable


def test_completion_requires_a_partition():
    kernel = [[0.9, 0.1], [0.2, 0.8]]
    with pytest.raises(ValueError, match="partition"):
        evolve_forget_reinstate([0.5, 0.5], kernel, 1.0, "spectral_lens",
                               {"groups": [[0], [0, 1]]})


def test_nonconverged_runs_are_not_counted_as_fixed_points():
    kernel = [[0.9, 0.1], [0.2, 0.8]]
    result = compute_packaging_fixed_points(
        kernel, [1.0], ["row_similarity_cluster_lens"], [[1.0, 0.0]], max_iter=1,
    )
    assert result["distinct_fixed_point_count"] == 0


def test_rounded_repeat_is_not_a_cycle():
    kernel = [[1 - 1e-8, 1e-8], [1e-8, 1 - 1e-8]]
    summary = iterate_completion_endomap(
        [0.6, 0.4], kernel, 1.0, "spectral_lens", max_iter=4, tol=1e-12,
        packaging_state={"groups": [[0], [1]], "support": [0.5, 0.5]},
    )
    assert summary["status"] == "nonconvergent"
    assert summary["cycle_length"] == 0


def test_switch_penalties_use_previous_selection():
    state = build_initial_state(n=4)
    state.active_lens = "new_lens"
    state.active_packaging = "new_package"
    state.lens_history = ["old_lens", "new_lens"]
    state.packaging_history = ["old_package", "new_package"]
    lens = {"score": 0.5}
    packaging = {"score": 0.5}
    tau = apply_p3_timescale_update(state, 0.0, lens, packaging)["tau"]
    assert tau == pytest.approx(1.0 + 0.11 * 0.12 - 0.07 - 0.05)
    cost = apply_p6_budget_update(state, packaging, lens, 0.0)["cost"]
    assert cost == pytest.approx(0.06 + 0.018 * state.phase + 0.03 + 0.03)


def test_time_sum_is_stable_but_has_zero_asymptotic_pressure():
    for n in [1, 10, 10000]:
        value = time_partition_pressure_proxy([2.0] * n, 1000.0)
        assert value == pytest.approx((math.log(n) - 2000.0) / n)


def test_subadditivity_diagnostic_is_not_a_log_identity():
    from scripts.run_continuous_pressure_checks import _subadditivity_defect

    assert _subadditivity_defect([1.0] * 4, 1.0) > 0.1


def test_saturation_diagnostic_rejects_unfinished_iterates():
    runs = [{"tau": 1.0, "lens_state": "l", "completion_summary": {
        "final_signature": (0.5, 0.5), "numerically_converged": False,
    }}] * 3
    result = detect_packaging_saturation(runs, tau_values=[1.0], lens_states=["l"], initial_count=3)
    assert result["saturated_panel_count"] == 0
    assert result["saturation_verified"] is False


def test_lumpability_obstruction_uses_transport_rows():
    kernel = [[0.8, 0.1, 0.1], [0.1, 0.1, 0.8], [0.1, 0.1, 0.8]]
    result = packaging_macro_admissibility({}, kernel=kernel, groups=[[0, 1], [2]])
    assert result["admissible"] is False
    assert result["max_lumpability_defect"] == pytest.approx(0.7)


def test_kl_support_mismatch_is_infinite_and_invalid_vectors_rejected():
    from scripts.run_conditional_disintegration_checks import _kl_divergence, _normalize

    assert _kl_divergence([1.0, 0.0], [0.0, 1.0]) == math.inf
    with pytest.raises(ValueError):
        _normalize([0.0, 0.0])
    with pytest.raises(ValueError):
        _kl_divergence([1.0], [0.5, 0.5])


def test_synthetic_moment_gap_exists_even_without_fiber_information():
    from scripts.run_conditional_disintegration_checks import _stratum_pressure_profile, _kl_divergence

    # A single, identical future has zero information deficit, yet the v1
    # correction produces a positive "pressure gap". It cannot witness strict extension.
    future = [0.5, 0.5]
    assert _kl_divergence(future, future) == 0.0
    profile = _stratum_pressure_profile(tuple(future), {"1.0": {"pressure_proxy": 0.2}})
    assert 0.2 - profile["1.0"] == pytest.approx(math.log(2) / 2)


def test_integer_digit_data_cannot_be_silently_truncated_into_a_certificate():
    from contextual_cantor.classical_similarity import maps_from_restricted_digits
    from contextual_cantor.contextual_certification import parse_digit_transition_config
    with pytest.raises(ValueError, match="integer"):
        maps_from_restricted_digits(3, [0, 1.7])
    with pytest.raises(ValueError, match="integer"):
        maps_from_restricted_digits(3.5, [0, 2])
    with pytest.raises(ValueError, match="duplicate normalized"):
        parse_digit_transition_config({"parameters": {"base": 3, "start_digits": [0],
                                                      "transition_digits": {"0": [0], "00": [2]}}})
