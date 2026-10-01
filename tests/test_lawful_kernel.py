from fractions import Fraction as Q

import pytest

from contextual_cantor.lawful_kernel import noise_noncollapse_constants


def test_noise_jump_constants_bound_normalized_coordinate_sensitivity():
    d, epsilon = 4, Q(1, 25)
    c = noise_noncollapse_constants(d, epsilon)
    assert c.conditional_probability == Q(1, 32)
    # On the event that all entry noises are nonnegative, S is the sum of
    # the coordinates other than j. A maximizing a != j gives S >=1/d.
    # This verifies the exact finite-difference identity underlying the
    # all-row analytic lower derivative estimate.
    for s in (Q(1, d), Q(1, 2), Q(1)):
        for v in (Q(0), Q(1, 4), Q(1, 2)):
            if s + v > 1:
                continue
            u0, u1 = Q(0), c.noise_min
            image = lambda u: (1 - epsilon) * (v + u) / (s + v + u) + epsilon / d
            assert image(u1) - image(u0) == (1 - epsilon) * s * (u1 - u0) / ((s + v + u1) * (s + v + u0))
            assert image(u1) - image(u0) >= 4 * c.coordinate_jump


def test_original_noise_rule_and_minorized_rule_both_have_nonzero_constants():
    a = noise_noncollapse_constants(16)
    b = noise_noncollapse_constants(16, Q(1, 25))
    assert a.coordinate_jump > b.coordinate_jump > 0
    assert a.conditional_probability == b.conditional_probability > 0
    for d, epsilon in ((1, Q(0)), (4, 0.04), (4, Q(1))):
        with pytest.raises(ValueError):
            noise_noncollapse_constants(d, epsilon)
