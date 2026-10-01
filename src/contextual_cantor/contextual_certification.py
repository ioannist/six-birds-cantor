from __future__ import annotations

import math
from fractions import Fraction
from typing import Any

from .interval_utils import HAS_MPMATH_IV
from .classical_similarity import integer_parameter

try:
    import mpmath as mp  # type: ignore
except Exception:  # pragma: no cover
    mp = None


def parse_digit_transition_config(config: dict[str, Any]) -> dict[str, Any]:
    """Parse the equal-ratio digit-transition form used by the contextual prefix-memory witness.

    Prototype scope: only digit-transition Markov, equal ratio (1/base), affine families.
    """
    params = config.get("parameters", {})
    if not isinstance(params, dict):
        raise ValueError("config.parameters must be an object")
    base = integer_parameter(params["base"], "base")
    if base < 2 or base != params["base"]:
        raise ValueError("base must be an integer greater than 1")
    start_digits = [integer_parameter(d, "digit") for d in params["start_digits"]]
    raw_transitions = params["transition_digits"]
    if not isinstance(raw_transitions, dict):
        raise ValueError("parameters.transition_digits must be an object")
    transitions = {integer_parameter(src, "source digit"): [integer_parameter(dst, "target digit") for dst in dsts]
                   for src, dsts in raw_transitions.items()}
    if len(transitions) != len(raw_transitions):
        raise ValueError("duplicate normalized transition source digits")
    if not start_digits or len(set(start_digits)) != len(start_digits):
        raise ValueError("start_digits must be nonempty and distinct")
    for digit in start_digits + list(transitions) + [d for ds in transitions.values() for d in ds]:
        if not 0 <= digit < base:
            raise ValueError("digits must lie in range(base)")
    if any(len(set(dsts)) != len(dsts) for dsts in transitions.values()):
        raise ValueError("duplicate digit transitions do not define distinct geometric cylinders")
    return {"base": base, "start_digits": start_digits, "transitions": transitions}


def _reachable_states(start_digits: list[int], transitions: dict[int, list[int]]) -> list[int]:
    seen = set(start_digits)
    stack = list(start_digits)
    while stack:
        state = stack.pop()
        for nxt in transitions.get(state, []):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return sorted(seen)


def build_reachable_adjacency_matrix(config: dict[str, Any]) -> tuple[list[int], list[list[int]]]:
    parsed = parse_digit_transition_config(config)
    transitions = parsed["transitions"]
    states = _reachable_states(parsed["start_digits"], transitions)
    if not states:
        raise ValueError("no reachable states from start_digits")
    index = {state: i for i, state in enumerate(states)}
    n = len(states)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for src in states:
        outgoing = transitions.get(src, [])
        if not outgoing:
            raise ValueError(f"reachable state {src} has no outgoing transitions")
        for dst in outgoing:
            if dst in index:
                matrix[index[src]][index[dst]] += 1
    return states, matrix


def _matvec_int(matrix: list[list[int]], vec: list[int]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vec)) for row in matrix]


def perron_bounds_collatz_wielandt(matrix: list[list[int]], steps: int) -> tuple[Fraction, Fraction]:
    if steps < 1:
        raise ValueError("steps must be >= 1")
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be non-empty square")
    if any(not isinstance(v, int) or v < 0 for row in matrix for v in row):
        raise ValueError("Collatz-Wielandt requires nonnegative integer entries")

    vec = [1 for _ in range(n)]
    for _ in range(steps):
        vec = _matvec_int(matrix, vec)
        if any(v <= 0 for v in vec):
            raise ValueError("Collatz-Wielandt prototype requires a positive iterate vector")

    next_vec = _matvec_int(matrix, vec)
    ratios = [Fraction(next_vec[i], vec[i]) for i in range(n)]
    return min(ratios), max(ratios)


def _fraction_point_iv(value: Fraction) -> Any:
    assert mp is not None
    return mp.iv.mpf([int(value.numerator), int(value.numerator)]) / int(value.denominator)


def certify_markov_equal_ratio_dimension(
    config: dict[str, Any],
    *,
    perron_steps: int = 40,
    precision_dps: int = 90,
) -> dict[str, Any]:
    family_id = str(config.get("family_id"))
    parsed = parse_digit_transition_config(config)
    base = int(parsed["base"])
    states, matrix = build_reachable_adjacency_matrix(config)
    rho_lower, rho_upper = perron_bounds_collatz_wielandt(matrix, steps=perron_steps)

    backend = "collatz-wielandt+mpmath-iv"
    if not HAS_MPMATH_IV or mp is None:
        raise ValueError("dimension certification requires mpmath.iv; floating margins are not certificates")
    if precision_dps < 1:
        raise ValueError("precision_dps must be positive")
    previous = mp.iv.dps
    try:
        mp.iv.dps = max(30, precision_dps)
        log_base_iv = mp.iv.log(mp.iv.mpf([base, base]))
        lower_iv = mp.iv.log(_fraction_point_iv(rho_lower)) / log_base_iv
        upper_iv = mp.iv.log(_fraction_point_iv(rho_upper)) / log_base_iv
        certified_lower = math.nextafter(float(lower_iv.a), -math.inf)
        certified_upper = math.nextafter(float(upper_iv.b), math.inf)
    finally:
        mp.iv.dps = previous

    # This reference applies only to the Fibonacci witness, not every Markov config.
    is_fibonacci = base == 3 and parsed["transitions"] == {0: [0, 2], 2: [0]} and set(parsed["start_digits"]) <= {0, 2}
    reference_root = math.log((1.0 + math.sqrt(5.0)) / 2.0) / math.log(3.0) if is_fibonacci else None
    return {
        "family_id": family_id,
        "states": states,
        "adjacency_matrix": matrix,
        "base": base,
        "rho_lower": str(rho_lower),
        "rho_upper": str(rho_upper),
        "perron_steps": perron_steps,
        "precision_dps": precision_dps,
        "certified_lower": certified_lower,
        "certified_upper": certified_upper,
        "certified_width": certified_upper - certified_lower,
        "reference_root": reference_root,
        "contains_reference_root": None if reference_root is None else certified_lower <= reference_root <= certified_upper,
        "certified": True,
        "method_backend": backend,
        "prototype_scope": "digit-transition Markov, equal ratio (1/base), affine maps",
    }
