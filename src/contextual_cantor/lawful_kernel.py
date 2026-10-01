"""Exact constants for the real-arithmetic, ideal fresh-noise counterpart.

These do not turn a finite pseudorandom run into an infinite iid-noise proof.
See the all-core restoration note for the conditional probability argument.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


@dataclass(frozen=True)
class NoncollapseConstants:
    coordinate_jump: Q
    conditional_probability: Q
    noise_min: Q = Q(1, 400)
    noise_max: Q = Q(9, 2000)


def noise_noncollapse_constants(dimension: int, minorization: Q = Q(0)) -> NoncollapseConstants:
    """For enabled P6 and iid uniform fresh entry noise, infinitely many
    kernel jumps exceed coordinate_jump almost surely. This holds for the
    original update (epsilon=0) as well as the minorized variant.

    The estimate is independent of the pre-noise stochastic row and of the
    adapted selectors and budget. It is intentionally conservative.
    """
    if type(dimension) is not int or dimension < 2:
        raise ValueError("dimension must be an integer >=2")
    if not isinstance(minorization, (Q, int)) or isinstance(minorization, bool) or not 0 <= minorization < 1:
        raise ValueError("minorization must be exact and lie in [0,1)")
    lower, upper = Q(1, 400), Q(9, 2000)
    jump = (1 - minorization) * lower / (4 * dimension * (1 + dimension * upper)**2)
    return NoncollapseConstants(jump, Q(1, 2**(dimension + 1)))
