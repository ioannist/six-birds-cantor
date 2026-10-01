"""Stable finite time-sum diagnostics; these are not cocycle pressure.

For bounded q_t, log(sum_{t<=n} exp(-s q_t))/n tends to zero. The
time-sum must not be silently identified with a sum over length-n histories.
"""

from __future__ import annotations

import math


def time_partition_log(values: list[float], s: float) -> float:
    if not values or not math.isfinite(s) or any(not math.isfinite(v) for v in values):
        raise ValueError("a time partition requires nonempty finite values and a finite parameter")
    terms = [-s * v for v in values]
    if any(not math.isfinite(term) for term in terms):
        raise ValueError("weighted observables must be finite")
    largest = max(terms)
    return largest + math.log(math.fsum(math.exp(term - largest) for term in terms))


def time_partition_pressure_proxy(values: list[float], s: float) -> float:
    return time_partition_log(values, s) / len(values)
