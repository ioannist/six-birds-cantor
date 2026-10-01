"""Exact algebraic instance of actual-P5 memory and noise recoupling.

The source phase-4 cluster score L lies in [74/100,84/100]; the construction
works uniformly on that interval. A rational L is an exact algebraic instance
of these source formulae, not a claim that the simulator's sine is rational.
The analytic note establishes the real-parameter construction and readout.
"""
from dataclasses import dataclass
from fractions import Fraction as Q

from .exact_completion import Matrix, ExactCompletionCertificate, certify_completion


@dataclass(frozen=True)
class RetainedMemoryWitness:
    pre_supports: tuple[tuple[Q, ...], tuple[Q, ...]]
    pre_noise_kernels: tuple[Matrix, Matrix]
    compensating_noise: tuple[Matrix, Matrix]
    shared_kernel: Matrix
    completions: tuple[ExactCompletionCertificate, ExactCompletionCertificate]
    lens_score: Q
    epsilon: Q


def construct_retained_memory(lens_score: Q = Q(4, 5), epsilon: Q = Q(1, 25)) -> RetainedMemoryWitness:
    if not isinstance(lens_score, (Q, int)) or isinstance(lens_score, bool) or not Q(74, 100) <= lens_score <= Q(84, 100):
        raise ValueError("exact lens score must lie in [74/100,84/100]")
    if not isinstance(epsilon, (Q, int)) or isinstance(epsilon, bool) or not 0 <= epsilon < 1:
        raise ValueError("exact minorization must lie in [0,1)")
    delta = Q(1, 10**6)
    p = (Q(1, 100),) * 4 + (Q(24, 100),) * 4
    changed = (p[0] + delta, p[1] - delta, *p[2:])
    package_score = Q(395, 1000) + Q(32, 100) * lens_score
    eta = Q(92, 1000) + Q(5, 100) * package_score
    diagonal_shift = Q(3, 100) * package_score
    outputs = []
    for support in (p, changed):
        # Rank-one K has exactly this stationary informant after one step;
        # diagonal = support. The actual n=8 cluster P5 compresses its
        # singleton list to these two contiguous groups and core=all states.
        rows = []
        for i in range(8):
            target = [support[j] + Q(1, 10) if (i < 4) == (j < 4) else Q(2, 5) * support[j]
                      for j in range(8)]
            target[i] += diagonal_shift
            total = sum(target)
            mixed = [(1 - eta) * support[j] + eta * target[j] / total for j in range(8)]
            viability = (Q(1, 5) + Q(4, 5) * support[i]) * (Q(1, 2) + Q(1, 2) * support[i])
            # With core=all, row-constant sqrt(viability) cancels exactly.
            if viability < Q(18, 100):
                mixed = [Q(65, 100) * x + Q(35, 100) / 8 for x in mixed]
            rows.append(tuple(mixed))
        outputs.append(tuple(rows))
    common = tuple(tuple((outputs[0][i][j] + outputs[1][i][j]) / 2 for j in range(8)) for i in range(8))
    noise = tuple(tuple(tuple(common[i][j] - output[i][j] for j in range(8)) for i in range(8))
                  for output in outputs)
    if max(abs(x) for matrix in noise for row in matrix for x in row) > Q(9, 2000):
        raise ArithmeticError("coupling is outside legal P6 noise")
    kernel = tuple(tuple((1 - epsilon) * common[i][j] + epsilon / 8 for j in range(8)) for i in range(8))
    certificates = tuple(certify_completion(kernel, Q(3, 5), [list(range(4)), list(range(4, 8))],
                                          support=list(support)) for support in (p, changed))
    if certificates[0].stationary == certificates[1].stationary:
        raise ArithmeticError("retained completion did not split")
    return RetainedMemoryWitness((p, changed), tuple(outputs), noise, kernel, certificates, Q(lens_score), Q(epsilon))
