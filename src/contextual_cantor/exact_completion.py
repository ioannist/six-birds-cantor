"""Exact rational certificates for a fixed evolve/forget/reinstate package.

This is the rational mathematical counterpart of the simulator's lazy
completion blend, not a certificate of floating execution or shell membership.
It retains the supplied partition. Distinct stationary outputs belong to
different completion operators, never to multiple attractors of one positive
operator. Inputs must be rational; floats are deliberately rejected.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

Q = Fraction
Matrix = tuple[tuple[Fraction, ...], ...]


def _rational(x: Fraction | int) -> Fraction:
    if not isinstance(x, (Fraction, int)) or isinstance(x, bool):
        raise ValueError("exact certificates require Fraction or integer inputs")
    return Fraction(x)


def _kernel(rows: list[list[Fraction]] | Matrix) -> Matrix:
    matrix = tuple(tuple(_rational(x) for x in row) for row in rows)
    d = len(matrix)
    if not d or any(len(row) != d for row in matrix):
        raise ValueError("kernel must be nonempty square")
    if any(x <= 0 for row in matrix for x in row) or any(sum(row) != 1 for row in matrix):
        raise ValueError("kernel must be strictly positive and exactly row-stochastic")
    return matrix


def _linear_solve(a: list[list[Fraction]], b: list[Fraction]) -> tuple[Fraction, ...]:
    d = len(b)
    aug = [list(row) + [rhs] for row, rhs in zip(a, b)]
    for j in range(d):
        pivot = next((i for i in range(j, d) if aug[i][j]), None)
        if pivot is None:
            raise ValueError("singular rational system")
        aug[j], aug[pivot] = aug[pivot], aug[j]
        scale = aug[j][j]
        aug[j] = [x / scale for x in aug[j]]
        for i in range(d):
            if i != j:
                scale = aug[i][j]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[j])]
    return tuple(row[-1] for row in aug)


def stationary_distribution_exact(rows: list[list[Fraction]] | Matrix) -> tuple[Fraction, ...]:
    matrix = _kernel(rows)
    d = len(matrix)
    equations = [[matrix[i][j] - int(i == j) for i in range(d)] for j in range(d - 1)]
    equations.append([Q(1)] * d)
    p = _linear_solve(equations, [Q(0)] * (d - 1) + [Q(1)])
    if any(x <= 0 for x in p) or sum(p) != 1 or any(sum(p[i] * matrix[i][j] for i in range(d)) != p[j] for j in range(d)):
        raise ArithmeticError("stationary certificate failed its exact identities")
    return p


def stationary_estimate_exact(rows: list[list[Fraction]] | Matrix, steps: int = 80) -> tuple[Fraction, ...]:
    """Rational counterpart of the simulator's finite stationary informant.

    This is NOT a stationary certificate. It retains the 80-step cutoff and
    10^(-12) consecutive-iterate test of the current algorithm, interpreted
    in rational arithmetic rather than replacing it with the exact limit.
    """
    kernel = _kernel(rows)
    if steps < 1:
        raise ValueError("steps must be positive")
    d = len(kernel)
    vector = (Q(1, d),) * d
    for _ in range(steps):
        nxt = tuple(sum(vector[i] * kernel[i][j] for i in range(d)) for j in range(d))
        if max(abs(a - b) for a, b in zip(nxt, vector)) <= Q(1, 10**12):
            return nxt
        vector = nxt
    return vector


@dataclass(frozen=True)
class ExactCompletionCertificate:
    transport: Matrix
    reinstatement: Matrix
    operator: Matrix
    stationary: tuple[Fraction, ...]
    limit_closure: Matrix
    minorization: Fraction
    contraction: Fraction
    groups: tuple[tuple[int, ...], ...]
    lumpability_defect: Fraction


def certify_completion(rows: list[list[Fraction]] | Matrix, tau: Fraction,
                       groups: list[list[int]], *, support: list[Fraction] | None = None) -> ExactCompletionCertificate:
    """Build E=B_tau Q U and verify its unique limit closure exactly.

    A positive stochastic E minorizes the uniform kernel by d*min(E_ij).
    Hence its action contracts zero-mass row vectors in l1 by at most
    1-d*min(E_ij)<1. Every probability initial state converges to stationary;
    the matrix with that row repeated is the idempotent limiting closure.
    This does not assert that E itself is idempotent.
    """
    kernel = _kernel(rows)
    tau = _rational(tau)
    if tau <= 0:
        raise ValueError("tau must be positive")
    d = len(kernel)
    if not groups or any(not group for group in groups) or sorted(i for group in groups for i in group) != list(range(d)):
        raise ValueError("groups must form a nonempty partition")
    if any(type(i) is not int for group in groups for i in group):
        raise ValueError("group indices must be integers")
    alpha = max(Q(18, 100), min(Q(78, 100), Q(22, 100) + Q(18, 100) * min(Q(1), tau / 3)))
    transport = tuple(tuple((1 - alpha) * int(i == j) + alpha * kernel[i][j] for j in range(d)) for i in range(d))
    # Preserve the finite informant algorithm used by completion, not an
    # unadvertised replacement by K's exact stationary limit.
    p = stationary_estimate_exact(kernel)
    sup = tuple(_rational(x) for x in support) if support is not None else (Q(1, d),) * d
    if len(sup) != d or any(x < 0 for x in sup):
        raise ValueError("support must be nonnegative with matching dimension")
    weights = [Q(55, 100) * p[i] + Q(25, 100) * sup[i] + Q(20, 100) * kernel[i][i] for i in range(d)]
    membership = {i: tuple(group) for group in groups for i in group}
    reinstate = tuple(tuple(weights[j] / sum(weights[h] for h in membership[i]) if j in membership[i] else Q(0)
                            for j in range(d)) for i in range(d))
    operator = tuple(tuple(sum(transport[i][h] * reinstate[h][j] for h in range(d)) for j in range(d)) for i in range(d))
    stationary = stationary_distribution_exact(operator)
    closure = tuple(stationary for _ in range(d))
    # Idempotence and absorption on both sides are verified, not inferred
    # from repeated samples or rounded signatures.
    for left, right, expected in [(closure, closure, closure), (operator, closure, closure), (closure, operator, closure)]:
        actual = tuple(tuple(sum(left[i][h] * right[h][j] for h in range(d)) for j in range(d)) for i in range(d))
        if actual != expected:
            raise ArithmeticError("limit closure identities failed")
    epsilon = min(x for row in operator for x in row)
    contraction = 1 - d * epsilon
    if not 0 <= contraction < 1:
        raise ArithmeticError("positive stochastic minorization failed")
    defect = max(max(sum(transport[i][j] for j in target) for i in source)
                 - min(sum(transport[i][j] for j in target) for i in source)
                 for source in groups for target in groups)
    return ExactCompletionCertificate(transport, reinstate, operator, stationary, closure, epsilon, contraction,
                                      tuple(tuple(group) for group in groups), defect)
