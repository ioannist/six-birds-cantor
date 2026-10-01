import copy
from fractions import Fraction as Q
import random

import pytest

from contextual_cantor.retained_memory import construct_retained_memory
from contextual_cantor.continuous_kernel_substrate import (
    PilotParameters, build_initial_state, step_substrate, complete_retained_packaging,
)


@pytest.mark.parametrize("score", [Q(74, 100), Q(4, 5), Q(84, 100)])
def test_exact_recoupling_and_persistent_split(score):
    w = construct_retained_memory(score)
    for kernel, noise in zip(w.pre_noise_kernels, w.compensating_noise):
        coupled = tuple(tuple((1 - w.epsilon) * (kernel[i][j] + noise[i][j]) + w.epsilon / 8
                              for j in range(8)) for i in range(8))
        assert coupled == w.shared_kernel
        assert max(abs(x) for row in noise for x in row) < Q(1, 10**6)
    a, b = w.completions
    assert a.stationary != b.stationary
    # Same current K, tau, active lens and package groups. The different
    # actual retained SUPPORT weights alone supply the completion distinction.
    assert a.transport == b.transport
    assert a.groups == b.groups
    assert a.stationary[0] / a.stationary[2] != b.stationary[0] / b.stationary[2]
    from contextual_cantor.pressure_extension import completion_predictive_price_lower_bound, completion_affinity_loss_bound
    assert completion_predictive_price_lower_bound(a, b) > Q(1, 10**20)
    assert completion_affinity_loss_bound(a, b) > Q(1, 10**20)
    # Recoupling breaks the old symmetry: coordinates 0,1 have distinct
    # diagonal tags in the shared kernel, so swapping them is not a base
    # automorphism. The first completion mass also changes exactly.
    assert w.shared_kernel[0][0] != w.shared_kernel[1][1]
    assert a.stationary[0] != b.stationary[0]


class FixedNoise(random.Random):
    def __init__(self, values=None):
        super().__init__(0)
        self.values = iter(values) if values is not None else None

    def random(self):
        return 0.5

    def uniform(self, a, b):
        value = next(self.values) if self.values is not None else 0.0
        assert a <= value <= b
        return value


def warm_state(support):
    params = PilotParameters(lens_hysteresis=1, packaging_hysteresis=1, budget_income_scale=10,
                             tau_initial=0.6, kernel_minorization=0.04)
    state = build_initial_state(n=8, pilot_parameters=params)
    state.kernel = [list(support) for _ in range(8)]
    state.tau, state.budget, state.phase = 0.6, 12.0, 4
    state.protocol_state = "packaging"
    state.active_lens = "row_similarity_cluster_lens"
    state.active_packaging = "partition_cluster_packaging"
    state.previous_signature = None
    return state


def test_real_source_update_matches_recoupling_algebra_and_keeps_actual_memory():
    # Float replay corroborates the source bridge; it is not the exact
    # equality certificate. Exact equality is the real-arithmetic proof.
    p = [0.01] * 4 + [0.24] * 4
    changed = [p[0] + 1e-6, p[1] - 1e-6, *p[2:]]
    states = [warm_state(s) for s in (p, changed)]
    outputs = []
    for state in states:
        preview = copy.deepcopy(state)
        preview.pilot_parameters.kernel_minorization = 0
        snap = step_substrate(preview, FixedNoise())
        assert snap["lens"]["name"] == "row_similarity_cluster_lens"
        assert snap["packaging"]["groups"] == [list(range(4)), list(range(4, 8))]
        assert snap["variation"] > 0.12
        assert preview.tau == 0.6 and preview.budget == 12
        outputs.append(preview.kernel)
    common = [[(outputs[0][i][j] + outputs[1][i][j]) / 2 for j in range(8)] for i in range(8)]
    for state, output in zip(states, outputs):
        noises = [common[i][j] - output[i][j] for i in range(8) for j in range(8)]
        step_substrate(state, FixedNoise(noises))
    assert states[0].retained_packaging["support"] != states[1].retained_packaging["support"]
    assert [x for row in states[0].kernel for x in row] == pytest.approx(
        [x for row in states[1].kernel for x in row], abs=1e-15)
    completions = [complete_retained_packaging(state, [1 / 8] * 8, max_iter=500, tol=1e-13) for state in states]
    assert all(c["numerically_converged"] for c in completions)
    assert abs(completions[0]["final_mu"][0] - completions[1]["final_mu"][0]) > 1e-8
    for _ in range(12):
        snaps = [step_substrate(state, FixedNoise()) for state in states]
        assert [x for row in states[0].kernel for x in row] == pytest.approx(
            [x for row in states[1].kernel for x in row], abs=1e-14)
        assert snaps[0]["lens"]["name"] == snaps[1]["lens"]["name"]
        assert snaps[0]["packaging"]["name"] == snaps[1]["packaging"]["name"]


def test_each_of_the_six_operations_changes_the_actual_update_on_the_warm_carrier():
    initial = warm_state([0.01] * 4 + [0.24] * 4)
    full = copy.deepcopy(initial)
    step_substrate(full, FixedNoise([0.00225] * 64))
    for primitive in ("P1", "P2", "P3", "P4", "P5", "P6"):
        ablated = copy.deepcopy(initial)
        step_substrate(ablated, FixedNoise([0.00225] * 64), {primitive: False})
        if primitive == "P3":
            assert full.phase == 5 and ablated.phase == 4
        else:
            assert max(abs(a - b) for row_a, row_b in zip(full.kernel, ablated.kernel)
                       for a, b in zip(row_a, row_b)) > 1e-5
