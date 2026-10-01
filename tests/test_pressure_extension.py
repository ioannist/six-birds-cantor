from fractions import Fraction as Q

import pytest

from contextual_cantor.pressure_extension import (
    construct_pressure_extension, integer_history_partition, predictive_price_lower_bound,
    construct_forced_completion,
    completion_affinity_loss_bound, affinity_pressure_proxy,
)
from contextual_cantor.continuous_kernel_substrate import (
    _completion_packaging_from_lens, evolve_forget_reinstate,
)


def test_split_pair_uses_the_same_actual_lens_package_and_finite_informant():
    w = construct_pressure_extension()
    assert w.groups == ((0, 1), (2, 3))
    assert w.forward.stationary == (Q(4063, 15745), Q(3842, 15745), Q(784, 3149), Q(784, 3149))
    assert w.backward.stationary == (Q(4063, 15849), Q(3842, 15849), Q(1324, 5283), Q(1324, 5283))
    for kernel, cert in ((w.kernel, w.forward), (w.reversed_kernel, w.backward)):
        floating = [[float(x) for x in row] for row in kernel]
        package = _completion_packaging_from_lens(floating, float(w.tau), w.lens)
        assert package["groups"] == [list(group) for group in w.groups]
        assert package["support"] == pytest.approx([float(x) for x in w.support])
        actual = evolve_forget_reinstate([float(x) for x in cert.stationary], floating, float(w.tau), w.lens)
        assert actual == pytest.approx([float(x) for x in cert.stationary], abs=1e-14)
    # Distinct diagonal entries fix states 0,1 under any relabelling, but the
    # edge 0->1 changes. Thus this is not a mere coordinate-permutation example.
    assert w.kernel[0][0] != w.kernel[1][1]
    assert w.kernel[0][1] != w.reversed_kernel[0][1]


@pytest.mark.parametrize("n,s", [(0, 0), (1, 0), (3, 1), (12, 2), (7, 5)])
def test_exact_whole_history_partitions_match(n, s):
    w = construct_pressure_extension()
    assert integer_history_partition(w.kernel, n, s) == integer_history_partition(w.reversed_kernel, n, s)


def test_predictive_price_is_positive_and_not_an_injected_entropy_offset():
    w = construct_pressure_extension()
    assert predictive_price_lower_bound(w) > Q(1, 10000)
    assert w.forward.lumpability_defect == Q(7, 100)
    assert w.backward.lumpability_defect == Q(21, 500)
    # Singleton completion makes both operators' stationary limits uniform;
    # equality of pressure does not, on its own, force a split completion.
    from contextual_cantor.exact_completion import certify_completion
    groups = [[i] for i in range(4)]
    a = certify_completion(w.kernel, Q(1), groups, support=list(w.support))
    b = certify_completion(w.reversed_kernel, Q(1), groups, support=list(w.support))
    assert a.stationary == b.stationary == (Q(1, 4),) * 4


def test_integer_readouts_reject_approximate_parameters():
    w = construct_pressure_extension()
    with pytest.raises(ValueError, match="integers"):
        integer_history_partition(w.kernel, 2, 0.5)
    with pytest.raises(ValueError, match="exact rational"):
        integer_history_partition(w.kernel, 2, 1, branch_scale=0.5)


def test_actual_feedback_changes_the_post_completion_limit_at_fixed_kernel():
    from contextual_cantor.continuous_kernel_substrate import iterate_completion_endomap, update_lens_from_packaging
    w = construct_pressure_extension()
    kernel = [[float(x) for x in row] for row in w.kernel]
    before = iterate_completion_endomap([0.25] * 4, kernel, 1, w.lens, max_iter=500, tol=1e-12)
    assert before["numerically_converged"]
    lens, feedback = update_lens_from_packaging(w.lens, before)
    assert feedback["applied"] and lens == "spectral_lens"
    after = iterate_completion_endomap(before["final_mu"], kernel, 1, lens, max_iter=500, tol=1e-12)
    cert = construct_forced_completion(w)
    assert cert.stationary == (Q(239, 891), Q(226, 891), Q(71, 297), Q(71, 297))
    assert after["final_mu"] == pytest.approx([float(x) for x in cert.stationary], abs=1e-12)
    assert after["final_mu"] != pytest.approx(before["final_mu"])
    assert cert.operator == cert.limit_closure  # all-state package saturates in one step


def test_true_relative_pressure_loss_and_false_target_endpoints():
    w = construct_pressure_extension()
    loss = completion_affinity_loss_bound(w.forward, w.backward)
    assert loss > 0
    for choice in (0, 1):
        assert affinity_pressure_proxy(w.forward, w.backward, choice, 0.5, 256) <= -float(loss)
        for endpoint in (0.0, 1.0):
            assert affinity_pressure_proxy(w.forward, w.backward, choice, endpoint, 32) == pytest.approx(0, abs=1e-14)
    assert completion_affinity_loss_bound(w.forward, w.forward) == 0
    assert affinity_pressure_proxy(w.forward, w.forward, 0, 0.5, 64) == pytest.approx(0, abs=1e-14)
