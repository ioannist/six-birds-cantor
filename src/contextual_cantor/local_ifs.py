from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable, Sequence


EPS = 1e-15


@dataclass(frozen=True, order=True)
class Interval:
    left: float
    right: float

    def __post_init__(self) -> None:
        l = float(self.left)
        r = float(self.right)
        if not math.isfinite(l) or not math.isfinite(r):
            raise ValueError("interval endpoints must be finite")
        if r < l:
            raise ValueError(f"invalid interval [{l}, {r}]")
        object.__setattr__(self, "left", l)
        object.__setattr__(self, "right", r)

    @property
    def length(self) -> float:
        return self.right - self.left

    def is_empty(self) -> bool:
        return self.right < self.left - EPS

    def intersects(self, other: "Interval") -> bool:
        return not (self.right < other.left - EPS or other.right < self.left - EPS)

    def intersection(self, other: "Interval") -> "Interval | None":
        l = max(self.left, other.left)
        r = min(self.right, other.right)
        if r < l:
            return None
        return Interval(l, r)

    def contains(self, x: float) -> bool:
        return self.left - EPS <= x <= self.right + EPS


class IntervalUnion:
    def __init__(self, intervals: Iterable[Interval] = ()) -> None:
        self.intervals: list[Interval] = self._coalesce(list(intervals))

    @staticmethod
    def _coalesce(intervals: list[Interval]) -> list[Interval]:
        if not intervals:
            return []
        sorted_intervals = sorted(intervals, key=lambda iv: (iv.left, iv.right))
        out = [sorted_intervals[0]]
        for current in sorted_intervals[1:]:
            prev = out[-1]
            if current.left <= prev.right + EPS:
                out[-1] = Interval(prev.left, max(prev.right, current.right))
            else:
                out.append(current)
        return out

    @classmethod
    def from_interval(cls, interval: Interval) -> "IntervalUnion":
        return cls([interval])

    @property
    def total_length(self) -> float:
        return sum(iv.length for iv in self.intervals)

    def is_empty(self) -> bool:
        return len(self.intervals) == 0

    def intersection_interval(self, domain: Interval) -> "IntervalUnion":
        parts: list[Interval] = []
        for iv in self.intervals:
            inter = iv.intersection(domain)
            if inter is not None:
                parts.append(inter)
        return IntervalUnion(parts)

    def union(self, other: "IntervalUnion") -> "IntervalUnion":
        return IntervalUnion(self.intervals + other.intervals)


@dataclass(frozen=True)
class LocalAffineMap:
    a: float
    b: float
    domain: Interval
    label: str | None = None

    def __post_init__(self) -> None:
        a = float(self.a)
        b = float(self.b)
        object.__setattr__(self, "a", a)
        object.__setattr__(self, "b", b)
        if not math.isfinite(a) or not math.isfinite(b) or abs(a) >= 1.0:
            raise ValueError("local affine map must be contractive: |a| < 1")
        if self.domain.left < -EPS or self.domain.right > 1.0 + EPS:
            raise ValueError("map domain must lie in [0,1]")
        image_left = a * self.domain.left + b
        image_right = a * self.domain.right + b
        low = min(image_left, image_right)
        high = max(image_left, image_right)
        if low < -EPS or high > 1.0 + EPS:
            raise ValueError("map image over domain must lie in [0,1]")

    def apply_point(self, x: float) -> float:
        return self.a * float(x) + self.b

    def apply_interval(self, iv: Interval) -> Interval:
        y1 = self.apply_point(iv.left)
        y2 = self.apply_point(iv.right)
        return Interval(min(y1, y2), max(y1, y2))

    def apply_union(self, union: IntervalUnion) -> IntervalUnion:
        return IntervalUnion([self.apply_interval(iv) for iv in union.intervals])

    def is_admissible_for_point(self, x: float) -> bool:
        return self.domain.contains(x)


@dataclass(frozen=True)
class LocalIFS:
    maps: tuple[LocalAffineMap, ...]

    def __post_init__(self) -> None:
        if len(self.maps) == 0:
            raise ValueError("LocalIFS requires at least one map")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LocalIFS":
        maps_raw = data.get("maps")
        if not isinstance(maps_raw, list) or not maps_raw:
            raise ValueError("parameters.maps must be a non-empty list")
        maps: list[LocalAffineMap] = []
        for item in maps_raw:
            if not isinstance(item, dict):
                raise ValueError("each map entry must be an object")
            domain_raw = item.get("domain")
            if not isinstance(domain_raw, list) or len(domain_raw) != 2:
                raise ValueError("map.domain must be [left, right]")
            domain = Interval(float(domain_raw[0]), float(domain_raw[1]))
            maps.append(
                LocalAffineMap(
                    a=float(item["a"]),
                    b=float(item["b"]),
                    domain=domain,
                    label=None if item.get("label") is None else str(item["label"]),
                )
            )
        return cls(maps=tuple(maps))


def iterate_once(local_ifs: LocalIFS, seed: IntervalUnion) -> IntervalUnion:
    total = IntervalUnion()
    for local_map in local_ifs.maps:
        restricted = seed.intersection_interval(local_map.domain)
        if restricted.is_empty():
            continue
        total = total.union(local_map.apply_union(restricted))
    return total


def iterate_set(
    local_ifs: LocalIFS,
    steps: int,
    seed: IntervalUnion | Interval | None = None,
) -> list[IntervalUnion]:
    if steps < 0:
        raise ValueError("steps must be non-negative")
    if seed is None:
        current = IntervalUnion.from_interval(Interval(0.0, 1.0))
    elif isinstance(seed, Interval):
        current = IntervalUnion.from_interval(seed)
    else:
        current = seed

    seq = [current]
    for _ in range(steps):
        current = iterate_once(local_ifs, current)
        seq.append(current)
    return seq


def is_word_admissible(
    local_ifs: LocalIFS,
    word: Sequence[int],
    seed: IntervalUnion | Interval | None = None,
) -> bool:
    if seed is None:
        current = IntervalUnion.from_interval(Interval(0.0, 1.0))
    elif isinstance(seed, Interval):
        current = IntervalUnion.from_interval(seed)
    else:
        current = seed

    for index in word:
        if index < 0 or index >= len(local_ifs.maps):
            raise IndexError(f"word index out of range: {index}")
        local_map = local_ifs.maps[index]
        restricted = current.intersection_interval(local_map.domain)
        if restricted.is_empty():
            return False
        current = local_map.apply_union(restricted)
        if current.is_empty():
            return False
    return True


def sample_orbit(
    local_ifs: LocalIFS,
    x0: float,
    steps: int,
    seed: int | None = None,
) -> dict[str, object]:
    if steps < 0:
        raise ValueError("steps must be non-negative")
    rng = random.Random(seed)
    x = float(x0)
    points = [x]
    indices: list[int] = []
    terminated = False

    for _ in range(steps):
        admissible = [i for i, m in enumerate(local_ifs.maps) if m.is_admissible_for_point(x)]
        if not admissible:
            terminated = True
            break
        idx = rng.choice(admissible)
        x = local_ifs.maps[idx].apply_point(x)
        indices.append(idx)
        points.append(x)

    return {
        "points": points,
        "map_indices": indices,
        "terminated_early": terminated,
    }
