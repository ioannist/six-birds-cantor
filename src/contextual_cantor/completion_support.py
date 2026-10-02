"""Exact finite support witnesses for original nonnegative completion data.

Only adjacency/path assertions are certified here. The mathematical return
uses stochastic real rows with this support and the actual B Q U formulas.
Floating evolution, original seeded-real reachability and shell membership
are not certified. No positive-kernel blend or edge is added to the source.
"""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
import math


def verify_power_support(certificate: dict) -> bool:
    """Verify paths relative to the supplied adjacency, not its data binding."""
    if not isinstance(certificate, dict):
        return False
    adjacency = certificate.get("adjacency")
    paths = certificate.get("paths")
    power = certificate.get("power")
    if not isinstance(adjacency,(list,tuple)) or not isinstance(paths,(list,tuple)):
        return False
    d = len(adjacency)
    if (not d or type(power) is not int or power < 1
            or any(not isinstance(row,(list,tuple)) or len(row) != d
                   or any(type(x) is not bool for x in row) for row in adjacency)
            or len(paths) != d or any(not isinstance(row,(list,tuple)) or len(row) != d for row in paths)):
        return False
    for i in range(d):
        for j in range(d):
            path = paths[i][j]
            if (not isinstance(path,(list,tuple)) or len(path) != power+1 or path[0] != i or path[-1] != j
                    or any(type(k) is not int or not 0 <= k < d for k in path)
                    or not all(adjacency[a][b] for a,b in zip(path,path[1:]))):
                return False
    return True


def _positive_power_paths(adjacency: list[list[bool]]) -> dict | None:
    d = len(adjacency)
    paths = [[([i,j] if adjacency[i][j] else None) for j in range(d)] for i in range(d)]
    # Both the lazy transport and the positive-diagonal lift have loops.
    # If irreducible, their longest shortest path is at most d-1.
    for power in range(1,max(1,d-1)+1):
        if all(path is not None for row in paths for path in row):
            certificate = {"adjacency": adjacency, "power": power, "paths": paths}
            if not verify_power_support(certificate):
                raise ArithmeticError("positive-power support witness failed")
            return certificate
        paths = [[next((paths[i][h]+[j] for h in range(d)
                        if paths[i][h] is not None and adjacency[h][j]), None)
                  for j in range(d)] for i in range(d)]
    return None


def completion_support_certificate(kernel: list[list[float]], groups: list[list[int]]) -> dict:
    d = len(kernel)
    if (not d or any(len(row) != d for row in kernel)
            or any(type(x) not in (float,int) or isinstance(x,bool) or not math.isfinite(x) or x < 0
                   for row in kernel for x in row)
            or any(sum(row) <= 0 for row in kernel)):
        raise ValueError("support input must be a finite nonnegative square table with positive row masses")
    groups = [list(group) for group in groups if group]
    if (not groups or any(type(j) is not int for group in groups for j in group)
            or sorted(j for group in groups for j in group) != list(range(d))):
        raise ValueError("groups must partition the kernel indices")
    kernel_edges = [[x > 0 for x in row] for row in kernel]
    positive_columns = all(any(kernel_edges[i][j] for i in range(d)) for j in range(d))
    transport_edges = [[i == j or kernel_edges[i][j] for j in range(d)] for i in range(d)]
    group_of = {j:group for group in groups for j in group}
    completion_edges = [[any(transport_edges[i][h] for h in group_of[j]) for j in range(d)]
                        for i in range(d)]
    transport = _positive_power_paths(transport_edges)
    # With a positive column in each column, EVERY finite informant iterate
    # from uniform is positive. All prototypes are then positive, independent
    # of the early-stop decision. Without that fact, U can have absent edges.
    completion = _positive_power_paths(completion_edges) if positive_columns else None
    raw = json.dumps([[float(x).hex() for x in row] for row in kernel], separators=(",",":"))
    discrepancy = max(abs(sum(Q(x) for x in row)-1) for row in kernel)
    return {
        "scope": "exact_support_of_recorded_input_and_its_row_normalized_real_interpretation",
        "kernel_data_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "kernel_dimension": d, "kernel_support": kernel_edges, "groups": groups,
        "raw_row_mass_deviation_exact": str(discrepancy),
        "real_input_interpretation": "K_ij=v_ij/sum_j(v_ij); no edges change",
        "every_kernel_column_has_positive_entry": positive_columns,
        "transport_power": transport, "completion_power": completion,
        "positive_completion_power_verified": completion is not None,
        "prototype_positivity_bridge": "finite informant remains positive; all support and diagonal terms nonnegative",
        "return": ("unique positive stationary law and all-start saturation for mathematical B Q U"
                   if completion is not None else "no saturation conclusion from this support test"),
        "floating_iteration_certified": False, "original_audited_shell_membership": "not_established",
    }
