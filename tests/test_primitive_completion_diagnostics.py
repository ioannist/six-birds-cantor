import pytest

from contextual_cantor.continuous_kernel_substrate import iterate_completion_endomap


def test_sparse_cycle_uses_positive_power_and_actual_block_residual():
    # Source B_tau has self-loops, so the four-cycle's completion becomes
    # strictly positive in THREE steps, although K and E have zero entries.
    kernel = [[float(j == (i+1)%4) for j in range(4)] for i in range(4)]
    package = {"groups": [[0],[1],[2],[3]], "support": [0.25]*4}
    result = iterate_completion_endomap([1,0,0,0], kernel, 1,
        "row_similarity_cluster_lens", packaging_state=package, max_iter=500, tol=1e-10)
    assert result["numerically_converged"]
    assert result["minorization_mass_estimate"] == 0
    assert result["minorization_power_estimate"] == 3
    assert result["block_minorization_mass_estimate"] == pytest.approx(4*0.28**3)
    actual_error = sum(abs(x-0.25) for x in result["final_mu"])
    assert actual_error <= result["stationary_l1_error_estimate"]+1e-14
    assert result["stationary_l1_error_estimate"] == pytest.approx(
        result["block_l1_residual"]/result["block_minorization_mass_estimate"])
    assert not result["error_bound_certified"]
    assert not result["certified_fixed_point"]


def test_reducible_identity_does_not_get_a_mixing_or_stationary_error_claim():
    kernel = [[float(i == j) for j in range(4)] for i in range(4)]
    package = {"groups": [[0],[1],[2],[3]], "support": [0.25]*4}
    one = iterate_completion_endomap([1,0,0,0], kernel, 1, "row_similarity_cluster_lens",
                                    packaging_state=package)
    another = iterate_completion_endomap([0,1,0,0], kernel, 1, "row_similarity_cluster_lens",
                                        packaging_state=package)
    assert one["numerically_converged"] and another["numerically_converged"]
    assert one["final_mu"] != another["final_mu"]
    assert one["minorization_power_estimate"] is None
    assert one["block_minorization_mass_estimate"] == 0
    assert one["stationary_l1_error_estimate"] is None


def test_failure_of_positive_power_is_inconclusive_even_for_a_unique_limit():
    # A reducible absorbing channel has a unique attracting law with zeros.
    # The new full-support mixing criterion is sufficient, not necessary.
    kernel = [[1.0,0,0,0] for _ in range(4)]
    package = {"groups": [[0],[1],[2],[3]], "support": [1.0,0,0,0]}
    result = iterate_completion_endomap([0,1,0,0], kernel, 1,
        "row_similarity_cluster_lens", packaging_state=package, max_iter=300, tol=1e-10)
    assert result["numerically_converged"]
    assert result["final_mu"] == pytest.approx([1,0,0,0], abs=1e-8)
    assert result["minorization_power_estimate"] is None
    assert result["stationary_l1_error_estimate"] is None
