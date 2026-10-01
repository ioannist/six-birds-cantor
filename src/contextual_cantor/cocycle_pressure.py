"""Finite-horizon diagnostics for a genuine kernel-history cocycle.

For a row-stochastic K and positive selector observable q, the one-step
branch weights are r_ij = exp(-q) K_ij. A_s has entries r_ij**s, and
the cocycle is A_s(x) A_s(Fx) ... . The row-sum operator norm counts
weighted length-n histories from the maximizing initial microstate.

Every returned number is a floating finite-horizon diagnostic. A pressure
limit over a shell needs forward invariance and uniform bounds, as stated
in the restoration theorem notes; it is not certified by this module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class KernelHistoryStep:
    kernel: list[list[float]]
    observable: float

    def __post_init__(self) -> None:
        d = len(self.kernel)
        if not d or any(len(row) != d for row in self.kernel):
            raise ValueError("kernel must be nonempty square")
        if any(not math.isfinite(k) or k < 0 for row in self.kernel for k in row):
            raise ValueError("kernel entries must be finite and nonnegative")
        if any(not math.isclose(math.fsum(row), 1.0, rel_tol=0.0, abs_tol=1e-10) for row in self.kernel):
            raise ValueError("kernel must be row-stochastic")
        if not math.isfinite(self.observable) or self.observable <= 0:
            raise ValueError("selector observable must be finite and positive")


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    d = len(a)
    return [[math.fsum(a[i][k] * b[k][j] for k in range(d)) for j in range(d)] for i in range(d)]


def history_log_norm(
    steps: list[KernelHistoryStep],
    s: float,
    *,
    fibers: list[set[int]] | None = None,
) -> float:
    """Log row-sum norm of the history product.

    Optional fibers specify allowed microstates at *each* of n+1 times.
    This is path-survival conditioning, not conditioning just the initial
    point or an assertion about persistent completion fixed-point strata.
    At s=0 a zero kernel entry is an absent edge, with weight zero.
    """
    if not steps or not math.isfinite(s) or s < 0:
        raise ValueError("history must be nonempty and s finite and nonnegative")
    d = len(steps[0].kernel)
    if any(len(step.kernel) != d for step in steps):
        raise ValueError("all kernels must have the same dimension")
    if fibers is not None:
        if len(fibers) != len(steps) + 1 or any(not group or not group <= set(range(d)) for group in fibers):
            raise ValueError("fibers must specify nonempty legal sets at n+1 times")
    product = [[float(i == j) for j in range(d)] for i in range(d)]
    log_scale = 0.0
    for t, step in enumerate(steps):
        terms = [[s * (math.log(k) - step.observable) if k > 0 else -math.inf for k in row]
                 for row in step.kernel]
        if fibers is not None:
            terms = [[value if i in fibers[t] and j in fibers[t + 1] else -math.inf
                      for j, value in enumerate(row)] for i, row in enumerate(terms)]
        largest = max(value for row in terms for value in row)
        if largest == -math.inf:
            return -math.inf
        weighted = [[math.exp(value - largest) for value in row] for row in terms]
        product = _matmul(product, weighted)
        norm = max(math.fsum(row) for row in product)
        if norm == 0:
            return -math.inf
        log_scale += largest + math.log(norm)
        product = [[value / norm for value in row] for row in product]
    return log_scale


def history_pressure_proxy(steps: list[KernelHistoryStep], s: float, *, fibers: list[set[int]] | None = None) -> float:
    return history_log_norm(steps, s, fibers=fibers) / len(steps)


def two_step_escape_factor(lower_entry: float, upper_entry: float, dimension: int) -> float:
    """Conservative gain from at least one missing intermediate fiber state.

    Positive entry bounds a<=A_ij<=b imply a two-step full product restricted
    to the same endpoints dominates (1+a²/(d b²)) times the fiber product.
    This algebraic bound requires positivity; it is not inferred from samples.
    """
    if not (0 < lower_entry <= upper_entry) or not math.isfinite(upper_entry) or dimension < 2:
        raise ValueError("positive ordered entry bounds and dimension >= 2 are required")
    return 1.0 + (lower_entry / upper_entry) ** 2 / dimension


def conditioned_history_log_mass(steps: list[KernelHistoryStep], s: float, initial: list[float]) -> float:
    """Log partition with a probability law on the INITIAL microstate only.

    This propagates every subsequent legal path. It must not be confused
    with the every-step fiber-survival partition of history_log_norm.
    """
    if not steps or not math.isfinite(s) or s < 0:
        raise ValueError("history must be nonempty and s finite and nonnegative")
    d = len(steps[0].kernel)
    if len(initial) != d or any(not math.isfinite(p) or p < 0 for p in initial):
        raise ValueError("initial must be a finite nonnegative probability vector of matching dimension")
    if not math.isclose(math.fsum(initial), 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("initial must have mass one")
    vector = list(initial)
    log_scale = 0.0
    for step in steps:
        if len(step.kernel) != d:
            raise ValueError("all kernels must have the same dimension")
        logs = [[s * (math.log(k) - step.observable) if k > 0 else -math.inf for k in row]
                for row in step.kernel]
        largest = max(x for row in logs for x in row)
        if largest == -math.inf:
            return -math.inf
        weighted = [[math.exp(x - largest) for x in row] for row in logs]
        vector = [math.fsum(vector[i] * weighted[i][j] for i in range(d)) for j in range(d)]
        mass = math.fsum(vector)
        if mass == 0:
            return -math.inf
        log_scale += largest + math.log(mass)
        vector = [x / mass for x in vector]
    return log_scale
