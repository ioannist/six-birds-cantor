from fractions import Fraction as Q

import pytest

from contextual_cantor.continuous_kernel_substrate import (
    apply_completion_feedback, compute_packaging_fixed_points,
    iterate_completion_endomap, update_lens_from_packaging,
)
from contextual_cantor.pressure_extension import construct_pressure_extension, construct_forced_completion


@pytest.mark.parametrize("summary", [
    {},
    {"status": "nonconvergent", "package_count": 20, "package_entropy": 10, "residual": 0},
    {"status": "cycle", "numerically_converged": True, "residual": 0},
    {"status": "fixed_point", "residual": 0},
    {"status": "fixed_point", "numerically_converged": True, "residual": 1},
])
def test_feedback_does_not_treat_missing_data_or_package_count_as_saturation(summary):
    lens, feedback = update_lens_from_packaging("audit_flow_quantile_lens", summary)
    assert lens == "audit_flow_quantile_lens" and not feedback["applied"]


def test_panel_executes_post_saturation_feedback_and_matches_exact_bqu_output():
    witness = construct_pressure_extension()
    kernel = [[float(x) for x in row] for row in witness.kernel]
    panel = compute_packaging_fixed_points(
        kernel, [1.0], [witness.lens], [[0.25]*4], max_iter=500, tol=1e-12,
    )
    run = panel["runs"][0]
    assert run["feedback"]["applied"]
    assert run["feedback"]["post_completion_evaluated"]
    assert run["feedback"]["numerical_object_change"]
    assert not run["feedback"]["materiality_certified"]
    before = run["completion_summary"]
    after = run["post_feedback_completion_summary"]
    # A 1e-12 consecutive-iterate residual is not a 1e-12 stationary error.
    # The proved contraction gives the additional geometric-tail factor.
    assert before["final_mu"] == pytest.approx([float(x) for x in witness.forward.stationary], abs=1e-11)
    assert before["minorization_mass_estimate"] > 0
    assert not before["error_bound_certified"]
    actual_error = sum(abs(x-float(p)) for x, p in zip(before["final_mu"], witness.forward.stationary))
    assert actual_error <= before["stationary_l1_error_estimate"] + 1e-13
    exact_after = construct_forced_completion(witness)
    assert exact_after.stationary == (Q(239,891), Q(226,891), Q(71,297), Q(71,297))
    assert after["numerically_converged"]
    assert after["final_mu"] == pytest.approx([float(x) for x in exact_after.stationary], abs=1e-12)
    assert run["post_feedback_packaging_state"]["groups"] == [list(range(4)), []]


def test_real_lens_change_need_not_change_the_fixed_object():
    # Uniform K produces the uniform fixed object for both audit and spectral
    # packages. This exercises the actual mechanism against a false target.
    kernel = [[0.25]*4 for _ in range(4)]
    before = iterate_completion_endomap([0.25]*4, kernel, 1, "audit_flow_quantile_lens")
    result = apply_completion_feedback(kernel, 1, "audit_flow_quantile_lens", before)
    assert result["feedback"]["applied"]
    assert result["feedback"]["post_completion_evaluated"]
    assert not result["feedback"]["numerical_object_change"]
    assert result["feedback"]["pre_post_l1_distance"] == pytest.approx(0)


def test_failed_post_completion_is_not_counted_as_material():
    witness = construct_pressure_extension()
    kernel = [[float(x) for x in row] for row in witness.kernel]
    # Spectral -> singleton completion can converge slowly from the completed
    # spectral vector; an intentionally short horizon is inconclusive.
    before = iterate_completion_endomap([0.25]*4, kernel, 1, "spectral_lens", max_iter=20, tol=1e-12)
    result = apply_completion_feedback(kernel, 1, "spectral_lens", before, max_iter=1, tol=1e-12)
    assert result["feedback"]["post_completion_evaluated"]
    assert not result["post_feedback_completion_summary"]["numerically_converged"]
    assert not result["feedback"]["numerical_object_change"]


def test_error_diagnostic_preserves_the_existing_all_cell_fallback():
    summary = iterate_completion_endomap(
        [0.25]*4, [[0.25]*4 for _ in range(4)], 1, "spectral_lens",
        packaging_state={"support": [0.25]*4},
    )
    assert summary["numerically_converged"]
    assert summary["minorization_mass_estimate"] == pytest.approx(1)
    assert summary["stationary_l1_error_estimate"] == pytest.approx(0)
