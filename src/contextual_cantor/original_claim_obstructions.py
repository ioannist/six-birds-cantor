"""Exact children of the missing ORIGINAL shell/disintegration obligations.

These are obstruction checks, not certificates of the original four theorems.
The uniform warm state has not been proved reachable from a published seed.
The pressure check uses genuine fixed initial-law conditioning of the SAME
path potential; other interpretations require an explicit conditional law.
"""
from __future__ import annotations

from fractions import Fraction as Q

from .exact_completion import Matrix, _kernel


def uniform_shell_certificate() -> dict[str, Q]:
    """Rational variance and timescale bounds for the source 20-state step.

    Uniform K; tau=21/20, budget=3, phase=0; spectral/cluster incumbents,
    no switch history. sqrt(2)<3/2 and sqrt(3)<7/4 prove the selectors are
    isolated and the cluster score <4/5. Consequently eta <141/1000.
    The uniform informant, two ten-cell groups, P1 and P2 fallback reduce
    the Frobenius variation to the three entry multiplicities below.
    """
    lens = Q(731, 1600)
    shift = lens / 50
    denominator = Q(17, 10) + shift
    eta_cap = Q(141, 1000)
    variance_cap = 20 * (Q(13, 20) * eta_cap)**2 * (
        ((Q(3, 20)+shift)/denominator-Q(1, 20))**2
        + 9*(Q(3, 20)/denominator-Q(1, 20))**2
        + 10*(Q(1, 50)/denominator-Q(1, 20))**2
    )
    variation_cap = Q(3, 40)
    tau_lower = Q(21, 20)+Q(33, 2500)-Q(17, 100)*variation_cap
    if not variance_cap < variation_cap**2 or not tau_lower > Q(21, 20):
        raise ArithmeticError("shell escape bound failed")
    return {"lens_score": lens, "eta_cap": eta_cap,
            "variance_cap": variance_cap, "variation_cap": variation_cap,
            "tau_initial": Q(21, 20), "tau_next_lower": tau_lower}


def initial_conditioned_partition(kernel: Matrix, initial: tuple[Q, ...],
                                  horizon: int, parameter: int = 1,
                                  branch_scale: Q = Q(1, 2)) -> Q:
    """Actual SAME-potential finite history sum, with an exact initial law.

    Integer s permits rational verification; the all-real positive-matrix
    pressure result is mechanized in ConditionalPressure.lean.
    """
    kernel = _kernel(kernel)
    if (type(horizon) is not int or horizon < 0
            or type(parameter) is not int or parameter < 0):
        raise ValueError("horizon and parameter must be nonnegative integers")
    if (not isinstance(branch_scale, (Q, int)) or isinstance(branch_scale, bool)
            or not 0 < branch_scale < 1):
        raise ValueError("branch scale must be an exact rational in (0,1)")
    if (len(initial) != len(kernel)
            or any(not isinstance(p, (Q, int)) or isinstance(p, bool) or p < 0 for p in initial)
            or sum(initial) != 1):
        raise ValueError("initial law must be an exact probability distribution")
    vector = (Q(1),)*len(kernel)
    matrix = tuple(tuple((branch_scale*k)**parameter for k in row) for row in kernel)
    for _ in range(horizon):
        vector = tuple(sum(k*v for k, v in zip(row, vector)) for row in matrix)
    return sum(p*v for p, v in zip(initial, vector))
