from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


Interval = tuple[float, float]


@dataclass(frozen=True)
class SimilarityMap1D:
    ratio: float
    offset: float

    def apply(self, interval: Interval) -> Interval:
        start, end = interval
        return (self.offset + self.ratio * start, self.offset + self.ratio * end)


def maps_from_restricted_digits(base: int, allowed_digits: Iterable[int]) -> list[SimilarityMap1D]:
    if base <= 1:
        raise ValueError("base must be greater than 1")
    digits = sorted(set(int(d) for d in allowed_digits))
    if not digits:
        raise ValueError("allowed_digits must be non-empty")
    for digit in digits:
        if digit < 0 or digit >= base:
            raise ValueError(f"digit out of range for base {base}: {digit}")
    ratio = 1.0 / float(base)
    return [SimilarityMap1D(ratio=ratio, offset=float(digit) / float(base)) for digit in digits]


def generate_cylinders(maps: Iterable[SimilarityMap1D], depth: int) -> list[Interval]:
    if depth < 0:
        raise ValueError("depth must be non-negative")
    maps_list = list(maps)
    if not maps_list:
        raise ValueError("maps must be non-empty")
    cylinders: list[Interval] = [(0.0, 1.0)]
    for _ in range(depth):
        next_cylinders: list[Interval] = []
        for interval in cylinders:
            for smap in maps_list:
                next_cylinders.append(smap.apply(interval))
        cylinders = next_cylinders
    return cylinders


def solve_similarity_dimension(
    ratios: Iterable[float],
    tol: float = 1e-12,
    max_iter: int = 512,
) -> float:
    ratio_list = [float(r) for r in ratios]
    if not ratio_list:
        raise ValueError("ratios must be non-empty")
    for ratio in ratio_list:
        if not (0.0 < ratio < 1.0):
            raise ValueError(f"ratio must be in (0,1): {ratio}")

    if len(ratio_list) == 1:
        return 0.0

    def f(s: float) -> float:
        return sum(r ** s for r in ratio_list) - 1.0

    lo = 0.0
    hi = 1.0
    while f(hi) > 0.0:
        hi *= 2.0
        if hi > 1e6:
            raise RuntimeError("failed to bracket similarity-dimension root")

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        value = f(mid)
        if abs(value) <= tol or (hi - lo) <= tol:
            return mid
        if value > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
