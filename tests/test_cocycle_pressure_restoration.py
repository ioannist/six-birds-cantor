from __future__ import annotations

import itertools
import math

import pytest

from contextual_cantor.cocycle_pressure import KernelHistoryStep, history_log_norm, history_pressure_proxy


def test_actual_path_enumeration_matches_cocycle():
    steps = [KernelHistoryStep([[0.8, 0.2], [0.3, 0.7]], 0.4),
             KernelHistoryStep([[0.5, 0.5], [0.1, 0.9]], 0.7)]
    s = 0.6
    by_start = []
    for start in range(2):
        total = 0.0
        for tail in itertools.product(range(2), repeat=2):
            path = (start,) + tail
            total += math.prod((math.exp(-step.observable) * step.kernel[path[t]][path[t + 1]]) ** s
                               for t, step in enumerate(steps))
        by_start.append(total)
    assert history_log_norm(steps, s) == pytest.approx(math.log(max(by_start)))


def test_uniform_kernel_has_nontrivial_pressure_and_unique_positive_root():
    d, q, n = 4, 0.5, 30
    steps = [KernelHistoryStep([[1 / d] * d for _ in range(d)], q)] * n
    root = math.log(d) / (math.log(d) + q)
    for s in [0.0, root, 1.0]:
        assert history_pressure_proxy(steps, s) == pytest.approx(math.log(d) - s * (math.log(d) + q), abs=1e-12)
    assert 0 < root < 1


def test_at_one_stochastic_products_retain_selector_decay():
    steps = [KernelHistoryStep([[0.8, 0.2], [0.3, 0.7]], 0.4),
             KernelHistoryStep([[0.5, 0.5], [0.1, 0.9]], 0.7)]
    assert history_log_norm(steps, 1.0) == pytest.approx(-1.1)


def test_cross_fiber_gap_comes_from_excluded_histories():
    n, d = 20, 4
    steps = [KernelHistoryStep([[0.25] * d for _ in range(d)], 0.5)] * n
    global_pressure = history_pressure_proxy(steps, 0.5)
    conditioned = history_pressure_proxy(steps, 0.5, fibers=[{0, 1}] * (n + 1))
    assert global_pressure - conditioned == pytest.approx(math.log(2))


def test_cocycle_concatenation_is_submultiplicative():
    left = [KernelHistoryStep([[0.8, 0.2], [0.3, 0.7]], 0.4)]
    right = [KernelHistoryStep([[0.5, 0.5], [0.1, 0.9]], 0.7)]
    assert history_log_norm(left + right, 0.5) <= history_log_norm(left, 0.5) + history_log_norm(right, 0.5) + 1e-14


def test_distinct_completion_fixed_priors_do_not_force_a_pressure_gap():
    from fractions import Fraction as Q
    from contextual_cantor.exact_completion import certify_completion
    from contextual_cantor.cocycle_pressure import conditioned_history_log_mass
    kernel = [[Q(3, 5), Q(1, 5), Q(1, 10), Q(1, 10)],
              [Q(1, 5), Q(2, 5), Q(1, 5), Q(1, 5)],
              [Q(1, 10), Q(1, 5), Q(2, 5), Q(3, 10)],
              [Q(1, 10), Q(1, 5), Q(3, 10), Q(2, 5)]]
    support = [(Q(1, 4) + kernel[i][i]) / 2 for i in range(4)]
    full = certify_completion(kernel, Q(1), [[0, 1, 2, 3]], support=support)
    singleton = certify_completion(kernel, Q(1), [[0], [1], [2], [3]], support=support)
    assert full.stationary != singleton.stationary
    floating = [[float(x) for x in row] for row in kernel]
    steps = [KernelHistoryStep(floating, 0.5)] * 80
    global_log = history_log_norm(steps, 0.5)
    for certificate in [full, singleton]:
        initial = [float(x) for x in certificate.stationary]
        conditional_log = conditioned_history_log_mass(steps, 0.5, initial)
        # The discrepancy is O(1), not a per-step inserted entropy offset.
        assert 0 <= global_log - conditional_log <= -math.log(min(initial)) + 1e-12
    # At s=1 stochasticity makes both initial-conditioned partitions exactly
    # the same as the global one, even at finite horizons.
    for certificate in [full, singleton]:
        assert conditioned_history_log_mass(steps, 1, [float(x) for x in certificate.stationary]) == pytest.approx(-40)
