from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

from .interval_utils import HAS_MPMATH_IV, ScalarInterval, evaluate_function_interval_at_point

try:
    import mpmath as mp  # type: ignore
except Exception:  # pragma: no cover
    mp = None


@dataclass(frozen=True)
class CertifiedBracket:
    lower: float
    upper: float
    width: float
    steps_used: int
    function_backend: str
    certification_method: str


def _refine_sign(
    x: float,
    dps: int,
    func_interval: Callable[[Any], Any] | None,
    func_point: Callable[[Any], Any],
) -> ScalarInterval:
    return evaluate_function_interval_at_point(
        x=x,
        dps=dps,
        func_interval=func_interval,
        func_point=func_point,
    )


def certify_monotone_decreasing_root(
    *,
    func_interval: Callable[[Any], Any] | None,
    func_point: Callable[[Any], Any],
    s_min: float,
    s_max: float,
    precision_dps: int,
    max_steps: int,
) -> CertifiedBracket:
    lo = float(s_min)
    hi = float(s_max)

    f_lo = _refine_sign(lo, precision_dps, func_interval, func_point)
    f_hi = _refine_sign(hi, precision_dps, func_interval, func_point)
    if not f_lo.is_positive():
        raise ValueError("left endpoint is not certified positive for monotone-decreasing root")
    if not f_hi.is_negative():
        raise ValueError("right endpoint is not certified negative for monotone-decreasing root")

    steps_used = 0
    backend = f_lo.backend
    for step in range(1, max_steps + 1):
        mid = 0.5 * (lo + hi)
        f_mid = _refine_sign(mid, precision_dps, func_interval, func_point)
        backend = f_mid.backend

        if f_mid.is_positive():
            lo = mid
            steps_used = step
            continue
        if f_mid.is_negative():
            hi = mid
            steps_used = step
            continue

        resolved = False
        for bump in (10, 20, 40):
            f_mid_more = _refine_sign(mid, precision_dps + bump, func_interval, func_point)
            backend = f_mid_more.backend
            if f_mid_more.is_positive():
                lo = mid
                steps_used = step
                resolved = True
                break
            if f_mid_more.is_negative():
                hi = mid
                steps_used = step
                resolved = True
                break
        if not resolved:
            steps_used = step
            break

    method = "interval-bisection-mpmath-iv" if HAS_MPMATH_IV and func_interval is not None else "margin-bisection"
    return CertifiedBracket(
        lower=lo,
        upper=hi,
        width=hi - lo,
        steps_used=steps_used,
        function_backend=backend,
        certification_method=method,
    )


def _classical_funcs(ratios: list[float]) -> tuple[Callable[[Any], Any] | None, Callable[[Any], Any]]:
    def func_interval(s: Any) -> Any:
        total = 0
        for r in ratios:
            total += r**s
        return total - 1

    def func_point(s: Any) -> Any:
        total = 0
        for r in ratios:
            total += r**s
        return total - 1

    return func_interval, func_point


def _adjacency_no_consecutive_2_funcs() -> tuple[Callable[[Any], Any] | None, Callable[[Any], Any]]:
    # Baseline-specific certified route for T08:
    # rho(A)=phi for Fibonacci adjacency matrix A=[[1,1],[1,0]], all edge ratios are 1/3,
    # so solve phi * 3^{-s} - 1 = 0.
    if mp is not None and HAS_MPMATH_IV:

        def func_interval(s: Any) -> Any:
            phi_iv = (1 + mp.iv.sqrt(mp.iv.mpf([5, 5]))) / 2
            return phi_iv * ((mp.iv.mpf([1, 1]) / 3) ** s) - 1

    else:
        func_interval = None

    def func_point(s: Any) -> Any:
        phi = (1 + math.sqrt(5.0)) / 2.0
        return phi * ((1.0 / 3.0) ** s) - 1

    return func_interval, func_point


def reference_root_for_family(family_id: str) -> float | None:
    if family_id == "classical.middle_thirds":
        return math.log(2.0) / math.log(3.0)
    if family_id == "classical.restricted_digits_base5_024":
        return math.log(3.0) / math.log(5.0)
    if family_id == "finite_state.adjacency_no_consecutive_2_base3":
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        return math.log(phi) / math.log(3.0)
    return None


def certify_config_root(
    config: dict[str, Any],
    *,
    precision_dps: int = 80,
    max_steps: int = 80,
    s_min: float = 0.0,
    s_max: float = 2.0,
) -> dict[str, Any]:
    family_id = str(config["family_id"])
    engine = str(config["engine"])
    params = config.get("parameters", {})

    if engine == "classical_similarity":
        base = int(params["base"])
        digits = params["allowed_digits"]
        ratios = [1.0 / float(base) for _ in digits]
        func_interval, func_point = _classical_funcs(ratios)
        bracket = certify_monotone_decreasing_root(
            func_interval=func_interval,
            func_point=func_point,
            s_min=s_min,
            s_max=s_max,
            precision_dps=precision_dps,
            max_steps=max_steps,
        )
        route = "classical-sum-r_i^s"

    elif family_id == "finite_state.adjacency_no_consecutive_2_base3":
        func_interval, func_point = _adjacency_no_consecutive_2_funcs()
        bracket = certify_monotone_decreasing_root(
            func_interval=func_interval,
            func_point=func_point,
            s_min=s_min,
            s_max=s_max,
            precision_dps=precision_dps,
            max_steps=max_steps,
        )
        route = "adjacency-fibonacci-phi-reduction"

    else:
        raise ValueError(f"unsupported family for certified bracketing prototype: {family_id}")

    ref = reference_root_for_family(family_id)
    contains_ref = None
    if ref is not None:
        contains_ref = bracket.lower <= ref <= bracket.upper

    return {
        "family_id": family_id,
        "certified_lower": bracket.lower,
        "certified_upper": bracket.upper,
        "certified_width": bracket.width,
        "steps_used": bracket.steps_used,
        "precision_dps": precision_dps,
        "max_steps": max_steps,
        "reference_root": ref,
        "contains_reference_root": contains_ref,
        "certification_method": bracket.certification_method,
        "function_backend": bracket.function_backend,
        "route": route,
    }
