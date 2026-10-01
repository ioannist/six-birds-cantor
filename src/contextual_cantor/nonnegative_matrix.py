"""Floating Perron estimates for finite nonnegative matrices.

These estimates are numerical, not interval certificates. Decomposing into
strongly connected components handles reducible matrices; shifting by the
identity handles periodic components. A failed convergence check raises rather
than returning the last (possibly oscillating) power-iteration scale.
"""

from __future__ import annotations

import math


def spectral_radius(matrix: list[list[float]], max_iter: int = 4096, tol: float = 1e-14) -> float:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square")
    if any(not math.isfinite(x) or x < 0 for row in matrix for x in row):
        raise ValueError("matrix must have finite nonnegative entries")
    if max_iter < 1 or not math.isfinite(tol) or tol <= 0:
        raise ValueError("max_iter and tol must be positive")
    if not n:
        return 0.0

    # Reachability suffices for the small matrices used by these experiments.
    reach = []
    for start in range(n):
        seen = {start}
        pending = [start]
        while pending:
            i = pending.pop()
            for j, value in enumerate(matrix[i]):
                if value > 0 and j not in seen:
                    seen.add(j)
                    pending.append(j)
        reach.append(seen)
    remaining = set(range(n))
    radii = []
    while remaining:
        i = min(remaining)
        component = sorted(j for j in remaining if j in reach[i] and i in reach[j])
        remaining.difference_update(component)
        if len(component) == 1:
            radii.append(float(matrix[i][i]))
            continue
        block = [[matrix[i][j] for j in component] for i in component]
        v = [1.0] * len(component)
        # Scale the shift to the block, preserving accuracy for small matrices.
        shift = max(sum(row) for row in block)
        for _ in range(max_iter):
            w = [sum(a * b for a, b in zip(row, v)) for row in block]
            ratios = [x / y for x, y in zip(w, v)]
            lower, upper = min(ratios), max(ratios)
            if upper - lower <= tol * max(upper, 1e-300):
                radii.append((lower + upper) / 2)
                break
            shifted = [x + shift * y for x, y in zip(w, v)]
            scale = max(shifted)
            v = [x / scale for x in shifted]
        else:
            raise RuntimeError("Perron iteration did not converge within max_iter")
    return max(radii)
