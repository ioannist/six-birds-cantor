from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    ratio: float
    label: str | None = None


def normalize_edges(edges: Iterable[dict[str, object] | Edge]) -> list[Edge]:
    out: list[Edge] = []
    for item in edges:
        if isinstance(item, Edge):
            edge = item
        else:
            src = str(item["src"])
            dst = str(item["dst"])
            ratio = float(item["ratio"])
            label_raw = item.get("label")
            label = None if label_raw is None else str(label_raw)
            edge = Edge(src=src, dst=dst, ratio=ratio, label=label)
        if not (0.0 < edge.ratio < 1.0):
            raise ValueError(f"edge ratio must lie in (0,1): {edge}")
        out.append(edge)
    if not out:
        raise ValueError("edges must be non-empty")
    return out


def states_from_edges(edges: Iterable[Edge]) -> list[str]:
    states = {e.src for e in edges}
    states.update(e.dst for e in edges)
    return sorted(states)


def _normalize_start_states(states: list[str], start_states: Iterable[str] | None) -> list[str]:
    if start_states is None:
        return states
    start = sorted(set(str(s) for s in start_states))
    missing = [s for s in start if s not in set(states)]
    if missing:
        raise ValueError(f"unknown start states: {missing}")
    if not start:
        raise ValueError("start_states must be non-empty")
    return start


def outgoing_edges(edges: Iterable[Edge]) -> dict[str, list[Edge]]:
    out: dict[str, list[Edge]] = {}
    for edge in edges:
        out.setdefault(edge.src, []).append(edge)
    return out


def admissible_words(
    edges: Iterable[dict[str, object] | Edge],
    depth: int,
    start_states: Iterable[str] | None = None,
) -> list[list[Edge]]:
    if depth < 0:
        raise ValueError("depth must be non-negative")
    edge_list = normalize_edges(edges)
    states = states_from_edges(edge_list)
    start = _normalize_start_states(states, start_states)
    by_src = outgoing_edges(edge_list)

    if depth == 0:
        return [[] for _ in start]

    current: list[tuple[str, list[Edge]]] = [(s, []) for s in start]
    for _ in range(depth):
        nxt: list[tuple[str, list[Edge]]] = []
        for state, prefix in current:
            for edge in by_src.get(state, []):
                nxt.append((edge.dst, prefix + [edge]))
        current = nxt
    return [w for _, w in current]


def admissible_word_count(
    edges: Iterable[dict[str, object] | Edge],
    depth: int,
    start_states: Iterable[str] | None = None,
) -> int:
    edge_list = normalize_edges(edges)
    if depth < 0:
        raise ValueError("depth must be non-negative")
    states = states_from_edges(edge_list)
    start = _normalize_start_states(states, start_states)
    by_src = outgoing_edges(edge_list)

    counts: dict[str, int] = {s: 1 for s in start}
    for _ in range(depth):
        nxt: dict[str, int] = {}
        for state, c in counts.items():
            for edge in by_src.get(state, []):
                nxt[edge.dst] = nxt.get(edge.dst, 0) + c
        counts = nxt
    return sum(counts.values())


def partition_sum(
    edges: Iterable[dict[str, object] | Edge],
    depth: int,
    s: float,
    start_states: Iterable[str] | None = None,
) -> float:
    if depth < 0:
        raise ValueError("depth must be non-negative")
    edge_list = normalize_edges(edges)
    states = states_from_edges(edge_list)
    start = _normalize_start_states(states, start_states)
    by_src = outgoing_edges(edge_list)

    weights: dict[str, float] = {st: 1.0 for st in start}
    for _ in range(depth):
        nxt: dict[str, float] = {}
        for state, w in weights.items():
            for edge in by_src.get(state, []):
                nxt[edge.dst] = nxt.get(edge.dst, 0.0) + w * (edge.ratio**s)
        weights = nxt
    return float(sum(weights.values()))


def pressure_estimate(
    edges: Iterable[dict[str, object] | Edge],
    depth: int,
    s: float,
    start_states: Iterable[str] | None = None,
) -> float:
    if depth <= 0:
        raise ValueError("depth must be positive")
    z = partition_sum(edges=edges, depth=depth, s=s, start_states=start_states)
    if z <= 0.0:
        raise ValueError("partition sum must be positive")
    return math.log(z) / float(depth)


def weighted_matrix(
    edges: Iterable[dict[str, object] | Edge],
    s: float,
) -> tuple[list[str], list[list[float]]]:
    edge_list = normalize_edges(edges)
    states = states_from_edges(edge_list)
    idx = {state: i for i, state in enumerate(states)}
    n = len(states)
    mat = [[0.0 for _ in range(n)] for _ in range(n)]
    for edge in edge_list:
        i = idx[edge.src]
        j = idx[edge.dst]
        mat[i][j] += edge.ratio**s
    return states, mat


def spectral_radius_power_iteration(
    matrix: list[list[float]],
    tol: float = 1e-14,
    max_iter: int = 4096,
) -> float:
    n = len(matrix)
    if n == 0:
        return 0.0
    for row in matrix:
        if len(row) != n:
            raise ValueError("matrix must be square")

    v = [1.0 / n for _ in range(n)]
    lam_old = 0.0
    for _ in range(max_iter):
        w = [sum(matrix[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = max(abs(x) for x in w)
        if norm == 0.0:
            return 0.0
        v = [x / norm for x in w]
        if abs(norm - lam_old) <= tol * max(1.0, norm):
            return norm
        lam_old = norm
    return lam_old


def spectral_radius_for_s(
    edges: Iterable[dict[str, object] | Edge],
    s: float,
) -> float:
    _, mat = weighted_matrix(edges=edges, s=s)
    return spectral_radius_power_iteration(mat)


def solve_spectral_root_dimension(
    edges: Iterable[dict[str, object] | Edge],
    tol: float = 1e-12,
    max_iter: int = 512,
) -> float:
    edge_list = normalize_edges(edges)

    def f(x: float) -> float:
        return spectral_radius_for_s(edge_list, x) - 1.0

    lo = 0.0
    flo = f(lo)
    if flo < 0.0:
        raise ValueError("rho(M_0) < 1: no positive spectral root")
    if abs(flo) <= tol:
        return 0.0

    hi = 1.0
    fhi = f(hi)
    while fhi > 0.0:
        hi *= 2.0
        if hi > 1e6:
            raise RuntimeError("failed to bracket spectral root")
        fhi = f(hi)

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) <= tol or (hi - lo) <= tol:
            return mid
        if fm > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def solve_partition_root_for_depth(
    edges: Iterable[dict[str, object] | Edge],
    depth: int,
    start_states: Iterable[str] | None = None,
    tol: float = 1e-12,
    max_iter: int = 512,
) -> float:
    edge_list = normalize_edges(edges)

    def g(x: float) -> float:
        return partition_sum(edge_list, depth=depth, s=x, start_states=start_states) - 1.0

    lo = 0.0
    glo = g(lo)
    if glo < 0.0:
        raise ValueError("Z_n(0) < 1: no nonnegative depth root")
    if abs(glo) <= tol:
        return 0.0

    hi = 1.0
    ghi = g(hi)
    while ghi > 0.0:
        hi *= 2.0
        if hi > 1e6:
            raise RuntimeError("failed to bracket depth root")
        ghi = g(hi)

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        gm = g(mid)
        if abs(gm) <= tol or (hi - lo) <= tol:
            return mid
        if gm > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
