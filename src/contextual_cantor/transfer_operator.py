from __future__ import annotations

import math
from typing import Any


def _matvec(matrix: list[list[float]], vec: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, vec)) for row in matrix]


def spectral_radius(matrix: list[list[float]], max_iter: int = 500, tol: float = 1e-14) -> float:
    n = len(matrix)
    if n == 0:
        return 0.0
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square")
    v = [1.0 / n] * n
    prev = 0.0
    for _ in range(max_iter):
        w = _matvec(matrix, v)
        m = max(abs(x) for x in w)
        if m == 0.0:
            return 0.0
        v = [x / m for x in w]
        if abs(m - prev) <= tol * max(1.0, abs(m)):
            return m
        prev = m
    return prev


def build_transfer_matrix(config: dict[str, Any], s: float) -> list[list[float]]:
    engine = str(config["engine"])
    params = config.get("parameters", {})
    if not isinstance(params, dict):
        raise ValueError("config.parameters must be object")

    if engine == "classical_similarity":
        base = int(params["base"])
        digits = params["allowed_digits"]
        if not isinstance(digits, list):
            raise ValueError("allowed_digits must be list")
        weight = sum((1.0 / float(base)) ** s for _ in digits)
        return [[weight]]

    if engine == "finite_state_symbolic":
        edges = params.get("edges")
        if not isinstance(edges, list):
            raise ValueError("finite_state_symbolic requires parameters.edges list")
        state_set: set[str] = set()
        states_raw = params.get("states")
        if isinstance(states_raw, list) and states_raw:
            for st in states_raw:
                state_set.add(str(st))
        for e in edges:
            if isinstance(e, dict):
                state_set.add(str(e["src"]))
                state_set.add(str(e["dst"]))
        states = sorted(state_set)
        index = {st: i for i, st in enumerate(states)}
        n = len(states)
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        for e in edges:
            if not isinstance(e, dict):
                continue
            i = index[str(e["src"])]
            j = index[str(e["dst"])]
            ratio = float(e["ratio"])
            mat[i][j] += ratio**s
        return mat

    raise ValueError(f"unsupported engine for transfer matrix: {engine}")


def solve_transfer_root(
    config: dict[str, Any],
    s_min: float = 0.0,
    s_max: float = 2.0,
    tol: float = 1e-12,
    max_iter: int = 200,
) -> float:
    def f(s: float) -> float:
        return spectral_radius(build_transfer_matrix(config, s)) - 1.0

    flo = f(s_min)
    fhi = f(s_max)
    if abs(flo) <= tol:
        return s_min
    if abs(fhi) <= tol:
        return s_max
    if flo * fhi > 0:
        raise ValueError("root not bracketed on [s_min, s_max]")

    lo, hi = s_min, s_max
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fmid = f(mid)
        if abs(fmid) <= tol or (hi - lo) <= tol:
            return mid
        if flo * fmid <= 0:
            hi = mid
            fhi = fmid
        else:
            lo = mid
            flo = fmid
    return 0.5 * (lo + hi)


def reference_root_for_family(family_id: str) -> float | None:
    if family_id == "classical.middle_thirds":
        return math.log(2.0) / math.log(3.0)
    if family_id == "classical.restricted_digits_base5_024":
        return math.log(3.0) / math.log(5.0)
    if family_id == "finite_state.adjacency_no_consecutive_2_base3":
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        return math.log(phi) / math.log(3.0)
    return None
