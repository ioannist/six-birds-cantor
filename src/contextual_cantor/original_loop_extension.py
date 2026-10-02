"""Original-parameter warm-state construction for the extension obligation.

The exact rational constructor covers kernels, actual completion objects,
and P1/P2/noise algebra uniformly over the real package-score interval.
Original infinite-time audited-shell membership and seeded reachability remain
unproved. This is not a replacement for that applicability obligation.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q

from .exact_completion import Matrix, ExactCompletionCertificate, _kernel, certify_completion


@dataclass(frozen=True)
class OriginalLoopExtension:
    kernels: tuple[Matrix, Matrix]
    support: tuple[Q, ...]
    audit_groups: tuple[tuple[int, ...], ...]
    audit: tuple[ExactCompletionCertificate, ExactCompletionCertificate]
    spectral: ExactCompletionCertificate
    cluster: ExactCompletionCertificate
    shared_next_kernel: Matrix
    tau: Q = Q(3, 5)
    lens_score: Q = Q(37, 80)


def construct_original_loop_extension() -> OriginalLoopExtension:
    """Exact 20-state pair; no added minorization or altered pilot parameter."""
    d = 20
    rows = [[Q(1, d) for _ in range(d)] for _ in range(d)]
    # Symmetric, zero-row/column-sum tags determine distinct diagonal supports.
    for i, j, a in ((0, 3, Q(1, 10000)), (1, 3, -Q(1, 20000)),
                    (2, 3, -Q(1, 40000)), (4, 7, Q(1, 12500)),
                    (5, 7, Q(3, 50000)), (6, 7, Q(1, 25000))):
        rows[i][i] += a
        rows[j][j] += a
        rows[i][j] -= a
        rows[j][i] -= a
    for i, j in ((0, 1), (1, 2), (2, 0)):
        rows[i][j] += Q(1, 10**6)
        rows[j][i] -= Q(1, 10**6)
    forward = _kernel(rows)
    backward = _kernel(tuple(tuple(row) for row in zip(*forward)))
    for i in range(d):
        # The two cycle neighbours swap their entries in each affected row.
        # Sorted rational equality certifies equality for EVERY entry weight.
        if sorted(forward[i]) != sorted(backward[i]):
            raise ArithmeticError("pointwise row-moment identity failed")
        if sum(forward[i][:10]) != Q(1, 2):
            raise ArithmeticError("physical half-block normalization changed")
    support = tuple((Q(1, d)+forward[i][i])/2 for i in range(d))
    core = sorted(range(d), key=lambda i: (support[i], forward[i][i]), reverse=True)[:5]
    groups = [sorted(core), [i for i in range(d) if i not in core]]
    audit = tuple(certify_completion(k, Q(3, 5), groups, support=list(support))
                  for k in (forward, backward))
    spectral = certify_completion(forward, Q(3, 5), [list(range(d))], support=list(support))
    cluster = certify_completion(forward, Q(3, 5), [[i] for i in range(d)], support=list(support))
    if cluster.stationary != (Q(1,d),)*d:
        raise ArithmeticError("singleton completion lost its common uniform object")
    if audit[0].stationary == audit[1].stationary:
        raise ArithmeticError("actual audit completion did not split")
    if any(a.stationary == spectral.stationary for a in audit):
        raise ArithmeticError("audit-to-spectral forcing lost materiality")
    # All-cell reinstatement is independent of its incoming transport.
    if spectral.stationary != certify_completion(backward, Q(3, 5), [list(range(d))],
                                                 support=list(support)).stationary:
        raise ArithmeticError("common forced object failed")
    return OriginalLoopExtension((forward, backward), support, audit[0].groups,
                                 audit, spectral, cluster, tuple((Q(1, d),)*d for _ in range(d)))


def exact_pre_noise(witness: OriginalLoopExtension, package_score: Q) -> tuple[Matrix, Matrix]:
    """Actual P1/P2 formula on the isolated spectral/cluster branch.

    The real source score is .736+.035 sqrt(3), inside [.79,.80]. Rational
    arguments are exact checks of an affine family, not a rationalization of
    sqrt(3). The accompanying derivation returns the endpoint bounds to it.
    """
    if (not isinstance(package_score, (Q, int)) or isinstance(package_score, bool)
            or not Q(79, 100) <= package_score <= Q(4, 5)):
        raise ValueError("exact package score must be in [.79,.80]")
    eta = Q(92, 1000) + Q(1, 20)*package_score
    shift = Q(1, 50)*witness.lens_score
    denominator = Q(17, 10)+shift
    outputs = []
    for k in witness.kernels:
        rows = []
        for i in range(20):
            viability = (Q(1, 5)+Q(4, 5)*witness.support[i])*Q(21, 40)
            if not Q(8, 100) <= viability < Q(18, 100):
                raise ArithmeticError("all-core fallback branch changed")
            target = tuple(((k[i][j]+Q(1, 10) if (i<10)==(j<10) else Q(2, 5)*k[i][j])
                            +shift*int(i==j))/denominator for j in range(20))
            if sum(target) != 1:
                raise ArithmeticError("common target denominator failed")
            rows.append(tuple(Q(65, 100)*((1-eta)*k[i][j]+eta*target[j])+Q(35, 2000)
                              for j in range(20)))
        outputs.append(_kernel(rows))
    if outputs[1] != tuple(tuple(row) for row in zip(*outputs[0])):
        raise ArithmeticError("full pre-noise transpose relation failed")
    if max(abs(x-Q(1, 20)) for m in outputs for row in m for x in row) >= Q(9, 2000):
        raise ArithmeticError("noise recoupling is outside original legal support")
    # Frobenius delta <= d * max coordinate delta, on a d-by-d matrix.
    if max(abs(outputs[z][i][j]-witness.kernels[z][i][j])
           for z in (0,1) for i in range(20) for j in range(20))*20 >= Q(8, 100):
        raise ArithmeticError("variation bound for original budget saturation failed")
    return tuple(outputs)


def integer_moving_history_rows(kernels: tuple[Matrix, ...], parameter: int,
                                scales: tuple[Q, ...]) -> tuple[Q, ...]:
    """Exact finite-history examples; the all-real-parameter proof is analytic.

    Each scale represents the shared positive exp(-q_t) branch scalar. This
    does not substitute rational numbers for the actual selector observable.
    """
    if type(parameter) is not int or parameter < 0 or len(kernels) != len(scales):
        raise ValueError("nonnegative integer parameter and one scale per step required")
    if not kernels:
        raise ValueError("a nonempty history is required")
    d = len(kernels[0])
    vector = (Q(1),)*d
    for k, scale in reversed(tuple(zip(kernels,scales))):
        _kernel(k)
        if len(k) != d or not isinstance(scale,(Q,int)) or isinstance(scale,bool) or not 0 < scale < 1:
            raise ValueError("common dimension and exact scale in (0,1) required")
        vector = tuple(sum((scale*k[i][j])**parameter*vector[j] for j in range(d))
                       for i in range(d))
    return vector
