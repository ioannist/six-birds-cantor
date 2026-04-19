from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

try:
    import mpmath as mp  # type: ignore
except Exception:  # pragma: no cover
    mp = None


@dataclass(frozen=True)
class ScalarInterval:
    lower: float
    upper: float
    backend: str

    @property
    def width(self) -> float:
        return self.upper - self.lower

    def is_positive(self) -> bool:
        return self.lower > 0.0

    def is_negative(self) -> bool:
        return self.upper < 0.0


HAS_MPMATH = mp is not None
HAS_MPMATH_IV = HAS_MPMATH and hasattr(mp, "iv")


def _fallback_margin(dps: int) -> float:
    # Explicit outward margin for non-interval backends.
    return 10.0 ** (-max(6, min(24, dps // 2)))


def evaluate_function_interval_at_point(
    x: float,
    dps: int,
    func_interval: Callable[[Any], Any] | None,
    func_point: Callable[[Any], Any],
) -> ScalarInterval:
    if HAS_MPMATH_IV and func_interval is not None:
        assert mp is not None
        mp.mp.dps = max(20, dps)
        y_iv = func_interval(mp.iv.mpf([x, x]))
        return ScalarInterval(float(y_iv.a), float(y_iv.b), "mpmath.iv")

    if HAS_MPMATH:
        assert mp is not None
        mp.mp.dps = max(20, dps)
        y = mp.mpf(func_point(mp.mpf(str(x))))
        margin = _fallback_margin(dps)
        return ScalarInterval(float(y) - margin, float(y) + margin, "mpmath-mpf-margin")

    y = float(func_point(float(x)))
    margin = max(1e-12, _fallback_margin(dps))
    return ScalarInterval(y - margin, y + margin, "float-margin")
