import json
from fractions import Fraction as Q
from pathlib import Path
import random

import pytest

from contextual_cantor.continuous_kernel_substrate import (
    KernelSubstrateState, PilotParameters, step_substrate,
)
from contextual_cantor.original_claim_obstructions import (
    initial_conditioned_partition, uniform_shell_certificate,
)
from contextual_cantor.pressure_extension import (
    construct_pressure_extension, construct_forced_completion,
)


@pytest.mark.parametrize("noise_seed", [0, 5, 17])
def test_original_twenty_state_box_exits_before_noise(noise_seed):
    cfg = json.loads((Path(__file__).resolve().parents[1] /
        "configs/experiments/generated/continuous_full_loop_kernel_shell.json").read_text())
    params = PilotParameters(**cfg["parameters"]["pilot_parameters"])
    kernel = [[0.05]*20 for _ in range(20)]
    state = KernelSubstrateState(kernel, 1.05, 3.0, 0.0, 0, "boot",
        "spectral_lens", "partition_cluster_packaging", [1.0]*3,
        previous_kernel=[row[:] for row in kernel], pilot_parameters=params)
    out = step_substrate(state, random.Random(noise_seed))
    certificate = uniform_shell_certificate()
    assert params.kernel_minorization == 0  # original update law
    assert all(state.primitive_activity.values())
    assert out["lens"]["name"] == "spectral_lens"
    assert out["packaging"]["name"] == "partition_cluster_packaging"
    assert out["packaging"]["groups"] == [list(range(10)), list(range(10,20))]
    assert out["selector_diagnostics"]["lens_margin"] > 0.01
    assert out["selector_diagnostics"]["packaging_margin"] > 0.01
    assert out["p1"]["eta"] < float(certificate["eta_cap"])
    assert state.tau >= float(certificate["tau_next_lower"]) > 1.05
    assert state.tau == pytest.approx(1.0512825927393918, abs=1e-14)


def test_actual_distinct_completion_objects_have_equal_original_partitions():
    witness = construct_pressure_extension()
    forced = construct_forced_completion(witness)
    assert forced.stationary != witness.forward.stationary
    for kernel, initial in ((witness.kernel, witness.forward.stationary),
                            (witness.reversed_kernel, witness.backward.stationary)):
        for horizon in (0, 1, 2, 5, 15):
            a = initial_conditioned_partition(kernel, initial, horizon)
            b = initial_conditioned_partition(kernel, forced.stationary, horizon)
            assert a == b == Q(1, 2)**horizon


def test_true_finite_disintegration_at_same_potential_and_zero_initial_cells():
    witness = construct_pressure_extension()
    a = witness.forward.stationary
    b = (Q(1), Q(0), Q(0), Q(0))
    weight = Q(2, 7)
    mixture = tuple(weight*x+(1-weight)*y for x, y in zip(a,b))
    # Away from s=1 the conditional finite sums can DIFFER. They still
    # have the SAME limiting pressure by the positive-matrix Lean theorem.
    assert initial_conditioned_partition(witness.kernel, a, 1, 2) != \
        initial_conditioned_partition(witness.kernel, b, 1, 2)
    for parameter in (0, 1, 2, 3):
        for horizon in (0, 1, 3, 7):
            joint = initial_conditioned_partition(witness.kernel, mixture, horizon, parameter)
            conditional = weight*initial_conditioned_partition(witness.kernel, a, horizon, parameter) \
                +(1-weight)*initial_conditioned_partition(witness.kernel, b, horizon, parameter)
            assert joint == conditional


@pytest.mark.parametrize("initial,horizon,parameter", [
    ((0.25,)*4, 1, 1), ((Q(1),)*4, 1, 1), ((Q(1),Q(0),Q(0),Q(-1)), 1, 1),
    ((Q(1),Q(0),Q(0),Q(0)), 1.5, 1), ((Q(1),Q(0),Q(0),Q(0)), 1, -1),
])
def test_exact_partition_rejects_inexact_or_invalid_laws(initial,horizon,parameter):
    with pytest.raises(ValueError):
        initial_conditioned_partition(construct_pressure_extension().kernel, initial, horizon, parameter)
