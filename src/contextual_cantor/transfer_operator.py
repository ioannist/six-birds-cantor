from __future__ import annotations

import math
from typing import Any

from .classical_similarity import maps_from_restricted_digits, integer_parameter
from .finite_state_symbolic import normalize_edges
from .nonnegative_matrix import spectral_radius


def _matvec(matrix: list[list[float]], vec: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, vec)) for row in matrix]


def build_transfer_matrix(config: dict[str, Any], s: float) -> list[list[float]]:
    engine = str(config["engine"])
    params = config.get("parameters", {})
    if not isinstance(params, dict):
        raise ValueError("config.parameters must be object")

    if engine == "classical_similarity":
        base = integer_parameter(params["base"], "base")
        digits = params["allowed_digits"]
        if not isinstance(digits, list):
            raise ValueError("allowed_digits must be list")
        weight = sum(smap.ratio ** s for smap in maps_from_restricted_digits(base, digits))
        return [[weight]]

    if engine == "finite_state_symbolic":
        edges = params.get("edges")
        if not isinstance(edges, list):
            raise ValueError("finite_state_symbolic requires parameters.edges list")
        edge_list = normalize_edges(edges)
        state_set: set[str] = set()
        states_raw = params.get("states")
        if isinstance(states_raw, list) and states_raw:
            for st in states_raw:
                state_set.add(str(st))
        for e in edge_list:
            state_set.update((e.src, e.dst))
        if "start_states" in params:
            reachable = {str(st) for st in params["start_states"]}
            if not reachable or not reachable <= state_set:
                raise ValueError("start_states must be nonempty known states")
            while True:
                expanded = reachable | {e.dst for e in edge_list if e.src in reachable}
                if expanded == reachable:
                    break
                reachable = expanded
            state_set = reachable
        states = sorted(state_set)
        index = {st: i for i, st in enumerate(states)}
        n = len(states)
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        for e in edge_list:
            if e.src not in index:
                continue
            i = index[e.src]
            j = index[e.dst]
            ratio = e.ratio
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
