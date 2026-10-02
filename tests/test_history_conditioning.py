import math

import pytest

from contextual_cantor.cocycle_pressure import (
    KernelHistoryStep, conditioned_history_log_mass, history_log_norm,
)


def _moving_history(length):
    kernels = [
        [[float(j == (i+1)%4) for j in range(4)] for i in range(4)],
        [[1.0,0.0,0.0,0.0] for _ in range(4)],
        [[0.1,0.2,0.3,0.4] for _ in range(4)],
    ]
    return [KernelHistoryStep(kernels[t%3], 0.07+0.002*t) for t in range(length)]


def test_original_s_one_partition_is_initial_law_independent_for_moving_kernels():
    for n in (1,2,7,80):
        history = _moving_history(n)
        expected = -math.fsum(step.observable for step in history)
        assert history_log_norm(history,1) == pytest.approx(expected, abs=2e-12)
        for initial in ([1,0,0,0], [0,0,0,1], [0.25]*4):
            assert conditioned_history_log_mass(history,1,initial) == pytest.approx(expected, abs=2e-12)


def test_full_support_history_comparison_needs_no_positive_or_frozen_kernel():
    initial = [0.01,0.09,0.3,0.6]
    for n in (2,7,80):
        history = _moving_history(n)
        for parameter in (0,0.5,1,2.5):
            base = history_log_norm(history,parameter)
            conditional = conditioned_history_log_mass(history,parameter,initial)
            assert math.log(min(initial))+base-2e-12 <= conditional <= base+2e-12
            assert abs(conditional/n-base/n) <= -math.log(min(initial))/n+2e-12
