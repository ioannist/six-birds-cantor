"""Exact completion split pair over an entire scalar history-partition family.

The lower carrier retains tau, the active audit lens, its actual partition,
support, and ALL frozen-kernel total history partitions (every n and real s).
It does not retain the labelled kernel or its full evolving cocycle. Equality
of the entire family follows analytically from transposition, not sampling s.
The rational checks here verify the displayed instance and integer readouts.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
import math

from .exact_completion import Matrix, ExactCompletionCertificate, _kernel, certify_completion


@dataclass(frozen=True)
class PressureExtensionWitness:
    kernel: Matrix
    reversed_kernel: Matrix
    support: tuple[Q, ...]
    groups: tuple[tuple[int, ...], ...]
    forward: ExactCompletionCertificate
    backward: ExactCompletionCertificate
    # Every integer-parameter branch weight is (K_ij/2)^s; q=log(2).
    branch_scale: Q = Q(1, 2)
    tau: Q = Q(1)
    lens: str = "audit_flow_quantile_lens"


def construct_pressure_extension() -> PressureExtensionWitness:
    kernel = _kernel([[Q(x, 100) for x in row] for row in
                      [[40, 30, 20, 10], [10, 35, 25, 30],
                       [25, 15, 30, 30], [25, 20, 25, 30]]])
    reverse = tuple(tuple(row) for row in zip(*kernel))
    _kernel(reverse)  # verifies both column sums and positivity exactly
    support = tuple((Q(1, 4) + kernel[i][i]) / 2 for i in range(4))
    # The actual completion audit lens selects the two largest support/diag
    # entries. Doubly stochasticity makes its finite informant exactly uniform.
    core = sorted(range(4), key=lambda i: (support[i], kernel[i][i]), reverse=True)[:2]
    groups = [sorted(core), [i for i in range(4) if i not in core]]
    forward = certify_completion(kernel, Q(1), groups, support=list(support))
    backward = certify_completion(reverse, Q(1), groups, support=list(support))
    if forward.stationary == backward.stationary:
        raise ArithmeticError("completion split pair failed")
    return PressureExtensionWitness(kernel, reverse, support, forward.groups, forward, backward)


def integer_history_partition(rows: Matrix, horizon: int, parameter: int,
                              *, branch_scale: Q = Q(1, 2)) -> Q:
    """Exact sum over all initial/end states and all length-n histories.

    Integer readouts are verification examples, not the proof of equality
    for every real parameter. Only nonnegative integer n,s are admitted.
    """
    kernel = _kernel(rows)
    if type(horizon) is not int or type(parameter) is not int or horizon < 0 or parameter < 0:
        raise ValueError("horizon and parameter must be nonnegative integers")
    if not isinstance(branch_scale, (Q, int)) or isinstance(branch_scale, bool) or not 0 < branch_scale < 1:
        raise ValueError("branch scale must be an exact rational in (0,1)")
    d = len(kernel)
    matrix = tuple(tuple((branch_scale * k) ** parameter for k in row) for row in kernel)
    vector = (Q(1),) * d
    for _ in range(horizon):
        vector = tuple(sum(matrix[i][j] * vector[j] for j in range(d)) for i in range(d))
    return sum(vector)


def predictive_price_lower_bound(witness: PressureExtensionWitness) -> Q:
    """A strictly positive rational lower bound on an extensive KL price.

    Give each completion operator prior probability 1/2 and initialize it
    at its own stationary law p_z. The best predictor using only the shared
    lower object and current microstate i has row
    R_ij=(p_+i E_+ij+p_-i E_-ij)/(p_+i+p_-i).
    Its per-step excess log loss is sum_z,i (p_zi/2) KL(E_zi || R_i).
    Pinsker in natural logs gives at least (1/2)||E_zi-R_i||_1^2 per KL.
    Stationarity makes the expected length-n log-likelihood penalty n times
    this rate. This is not a difference of initial-conditioned pressures.
    """
    return completion_predictive_price_lower_bound(witness.forward, witness.backward)


def completion_predictive_price_lower_bound(a: ExactCompletionCertificate,
                                           b: ExactCompletionCertificate) -> Q:
    """Pinsker lower bound for the two stationary completion processes.

    See predictive_price_lower_bound for the precise comparator and prior.
    """
    if len(a.operator) != len(b.operator):
        raise ValueError("completion operators must have the same dimension")
    price = Q(0)
    for i, (pa, pb) in enumerate(zip(a.stationary, b.stationary)):
        row = [(pa * a.operator[i][j] + pb * b.operator[i][j]) / (pa + pb)
               for j in range(len(a.operator))]
        for p, operator in ((pa, a.operator), (pb, b.operator)):
            distance = sum(abs(operator[i][j] - row[j]) for j in range(len(row)))
            price += p * distance**2 / 4
    if price <= 0:
        raise ArithmeticError("no strictly positive predictive price")
    return price


def construct_forced_completion(witness: PressureExtensionWitness) -> ExactCompletionCertificate:
    """Actual audit-to-spectral feedback at a saturated fixed package.

    The current completion feedback sends a converged audit lens to the
    spectral lens. Both kernels have uniform informants, so the spectral
    core includes all states. Its unique output differs from the prior audit
    output. This is an extension of the available one-lens operator panel,
    not creation of another fixed point of the same positive operator.
    """
    forced = certify_completion(witness.kernel, witness.tau, [list(range(4))], support=list(witness.support))
    if forced.stationary == witness.forward.stationary:
        raise ArithmeticError("forcing did not change the persistent completion object")
    return forced


def completion_lower_predictor(a: ExactCompletionCertificate, b: ExactCompletionCertificate) -> Matrix:
    """Best autonomous predictor under the stationary, equally weighted pair."""
    if len(a.operator) != len(b.operator):
        raise ValueError("completion operators must have the same dimension")
    return tuple(tuple((a.stationary[i] * a.operator[i][j] + b.stationary[i] * b.operator[i][j])
                       / (a.stationary[i] + b.stationary[i]) for j in range(len(a.operator)))
                 for i in range(len(a.operator)))


def completion_affinity_loss_bound(a: ExactCompletionCertificate, b: ExactCompletionCertificate) -> Q:
    """Exact lower bound for the reference-minus-package affinity pressures.

    T_z(1/2)_ij=sqrt(E_zij R_ij) has row sum at most
    1-||E_zi-R_i||_1^2/8. Let lambda be the minimum of these rational losses.
    Then every length-n affinity partition is <=(1-lambda)^n, so each
    pressure <=log(1-lambda) and the weighted gap >=-log(1-lambda)>=lambda.
    lambda=0 is a legitimate inconclusive bound, including identical kernels.
    This changes the PATH potential explicitly; it is not initial conditioning.
    """
    reference = completion_lower_predictor(a, b)
    return min(sum(abs(operator[i][j] - reference[i][j]) for j in range(len(reference)))**2 / 8
               for operator in (a.operator, b.operator) for i in range(len(reference)))


def affinity_pressure_proxy(a: ExactCompletionCertificate, b: ExactCompletionCertificate,
                            choice: int, parameter: float, horizon: int) -> float:
    """Floating finite-horizon log affinity per step, NOT a limit certificate.

    The exact pressure/loss theorem is in the all-core construction note.
    At t=0,1 the matrix is stochastic and the affinity pressure is zero.
    """
    if choice not in (0, 1) or not math.isfinite(parameter) or not 0 <= parameter <= 1:
        raise ValueError("choice must be 0 or 1 and parameter in [0,1]")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("horizon must be a positive integer")
    reference = completion_lower_predictor(a, b)
    certificate = (a, b)[choice]
    d = len(reference)
    matrix = [[math.exp((1 - parameter) * math.log(float(certificate.operator[i][j]))
                        + parameter * math.log(float(reference[i][j]))) for j in range(d)] for i in range(d)]
    vector = [float(x) for x in certificate.stationary]
    logarithm = 0.0
    for _ in range(horizon):
        vector = [math.fsum(vector[i] * matrix[i][j] for i in range(d)) for j in range(d)]
        mass = math.fsum(vector)
        logarithm += math.log(mass)
        vector = [x / mass for x in vector]
    return logarithm / horizon
