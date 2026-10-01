import copy
import random

import pytest

from contextual_cantor.continuous_kernel_substrate import (
    PilotParameters, build_initial_state, step_substrate, complete_retained_packaging,
    iterate_completion_endomap,
)


def test_retained_p5_object_is_used_without_lens_reconstruction_or_aliasing():
    state = build_initial_state(n=8, seed=17)
    with pytest.raises(ValueError, match="no retained"):
        complete_retained_packaging(state, [1 / 8] * 8)
    snap = step_substrate(state, random.Random(17))
    package = copy.deepcopy(snap["packaging"])
    assert state.retained_packaging == package
    actual = complete_retained_packaging(state, [1 / 8] * 8)
    expected = iterate_completion_endomap([1 / 8] * 8, state.kernel, state.tau, state.active_lens,
                                         packaging_state=package)
    assert actual == expected
    snap["packaging"]["groups"][0].append(100)
    saved = state.snapshot()
    saved["retained_packaging"]["support"][0] = 100
    assert state.retained_packaging == package


def test_positive_repaired_variant_preserves_a_uniform_entry_floor_after_noise():
    n, epsilon = 8, 0.04
    state = build_initial_state(n=n, seed=7, pilot_parameters=PilotParameters(kernel_minorization=epsilon))
    rng = random.Random(7)
    # A legal boundary input exercises the repair; its one-step image lies in
    # the positive shell, regardless of zeros introduced by clipping noise.
    state.kernel = [[float(i == j) for j in range(n)] for i in range(n)]
    for _ in range(50):
        snap = step_substrate(state, rng)
        assert snap["kernel_minorization"] == epsilon
        assert min(x for row in state.kernel for x in row) >= epsilon / n - 1e-15
        assert all(sum(row) == pytest.approx(1) for row in state.kernel)
        assert 0 <= state.budget <= 12
        assert 0.6 <= state.tau <= 4


def test_historical_variant_is_explicitly_unminorized_and_bad_floors_rejected():
    assert PilotParameters().kernel_minorization == 0
    for epsilon in (-0.1, 1, float("nan")):
        with pytest.raises(ValueError):
            PilotParameters(kernel_minorization=epsilon)
