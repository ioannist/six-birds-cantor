from fractions import Fraction as Q

import pytest

from contextual_cantor.exact_completion import certify_completion, stationary_distribution_exact
from contextual_cantor.continuous_kernel_substrate import evolve_forget_reinstate

K = [[Q(6, 10), Q(2, 10), Q(1, 10), Q(1, 10)],
     [Q(2, 10), Q(4, 10), Q(2, 10), Q(2, 10)],
     [Q(1, 10), Q(2, 10), Q(4, 10), Q(3, 10)],
     [Q(1, 10), Q(2, 10), Q(3, 10), Q(4, 10)]]
SUPPORT = [(Q(1, 4) + K[i][i]) / 2 for i in range(4)]


def test_stationarity_and_idempotent_limit_are_exact():
    assert stationary_distribution_exact(K) == (Q(1, 4),) * 4
    full = certify_completion(K, Q(1), [[0, 1, 2, 3]], support=SUPPORT)
    singleton = certify_completion(K, Q(1), [[0], [1], [2], [3]], support=SUPPORT)
    assert full.stationary == (Q(97, 336), Q(239, 1008), Q(239, 1008), Q(239, 1008))
    assert singleton.stationary == (Q(1, 4),) * 4
    assert full.operator == full.limit_closure  # one-step saturation
    assert singleton.operator != singleton.limit_closure  # limiting saturation only
    assert full.stationary != singleton.stationary
    assert 0 <= singleton.contraction < 1


def test_exact_macro_obstruction_and_actual_completion_action_agree():
    groups = [[0, 1], [2, 3]]
    cert = certify_completion(K, Q(1), groups, support=SUPPORT)
    assert cert.lumpability_defect == Q(7, 125)
    mu = [0.1, 0.2, 0.3, 0.4]
    actual = evolve_forget_reinstate(mu, [[float(x) for x in row] for row in K], 1.0, "audit_flow_quantile_lens",
                                    {"groups": groups, "support": [float(x) for x in SUPPORT]})
    expected = [sum(mu[i] * float(cert.operator[i][j]) for i in range(4)) for j in range(4)]
    assert actual == pytest.approx(expected)
    assert sum(cert.stationary) == 1


def test_exact_certificates_reject_approximate_or_invalid_inputs():
    with pytest.raises(ValueError, match="Fraction"):
        certify_completion([[0.5, 0.5], [0.5, 0.5]], Q(1), [[0], [1]])
    with pytest.raises(ValueError, match="partition"):
        certify_completion(K, Q(1), [[0, 1], [1, 2, 3]])


def test_completion_prototypes_retain_the_finite_informant_not_an_exact_limit():
    from contextual_cantor.exact_completion import stationary_estimate_exact
    kernel = [[Q(99, 100), Q(1, 100)], [Q(2, 100), Q(98, 100)]]
    estimate = stationary_estimate_exact(kernel)
    assert estimate != stationary_distribution_exact(kernel)
    cert = certify_completion(kernel, Q(1), [[0, 1]])
    actual = evolve_forget_reinstate([0.3, 0.7], [[float(x) for x in row] for row in kernel], 1,
                                    "spectral_lens", {"groups": [[0, 1]], "support": [0.5, 0.5]})
    assert actual == pytest.approx([float(x) for x in cert.stationary], abs=1e-14)
