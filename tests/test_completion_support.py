import copy

import pytest

from contextual_cantor.completion_support import completion_support_certificate, verify_power_support


def test_exact_support_certificate_for_sparse_periodic_kernel():
    kernel = [[int(j == (i+1)%4) for j in range(4)] for i in range(4)]
    cert = completion_support_certificate(kernel, [[0],[1],[2],[3]])
    assert cert["raw_row_mass_deviation_exact"] == "0"
    assert cert["completion_power"]["power"] == 3
    assert cert["transport_power"]["power"] == 3
    assert verify_power_support(cert["completion_power"])
    assert cert["positive_completion_power_verified"]
    assert not cert["floating_iteration_certified"]
    broken = copy.deepcopy(cert["completion_power"])
    broken["paths"][0][3] = [0,0,0,3]  # last edge absent
    assert not verify_power_support(broken)


def test_lift_can_mix_identity_transport_without_transport_primitivity():
    kernel = [[int(i == j) for j in range(4)] for i in range(4)]
    singletons = completion_support_certificate(kernel, [[0],[1],[2],[3]])
    assert singletons["completion_power"] is None
    full = completion_support_certificate(kernel, [[0,1,2,3]])
    assert full["transport_power"] is None
    assert full["completion_power"]["power"] == 1


def test_missing_informant_positivity_does_not_get_a_false_full_support_proof():
    # A zero column permits zero prototypes. Merging the cells does not
    # establish a positive lift without a separate positivity certificate.
    kernel = [[1,0,0,0] for _ in range(4)]
    cert = completion_support_certificate(kernel, [[0,1,2,3]])
    assert not cert["every_kernel_column_has_positive_entry"]
    assert cert["completion_power"] is None


@pytest.mark.parametrize("groups", [[[0,1],[1,2,3]], [[0,1,2]], [[True],[1,2,3]]])
def test_support_certificate_requires_a_partition(groups):
    with pytest.raises(ValueError, match="partition"):
        completion_support_certificate([[0.25]*4 for _ in range(4)],groups)
